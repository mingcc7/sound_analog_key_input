import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from keras.models import Sequential
from keras.layers import InputLayer, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.utils import to_categorical
import queue
from keras.callbacks import Callback
from tkinter import messagebox
import time
import traceback

from audio_acquisition import CHUNK
from audio_acquisition import RATE

zeros_data = np.zeros(CHUNK, dtype=np.int16)

model_training_queue = queue.Queue()

# 预运行
librosa.feature.mfcc(
    y=zeros_data.astype(np.float32) / 32768.0, sr=RATE, n_fft=len(zeros_data)
)


# 音色特征提取函数
def extract_features(file_path, one_volume_count, y=None, sr=None):
    if file_path != None:
        y, sr = librosa.load(file_path, sr=RATE)  # 加载音频文件

    count = int(len(y) / CHUNK)
    if count < one_volume_count:
        for _ in range(one_volume_count - count):
            y = np.concatenate((y, zeros_data))
    elif count > one_volume_count:
        y = y[: one_volume_count * CHUNK]

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_fft=len(y))  # 提取MFCC特征
    # mfccs_processed = np.mean(mfccs.T, axis=0)  # 平均化处理
    return mfccs.flatten()


# 加载数据
def load_data(audio_dirs, audio_path, one_volume_count):
    features = []
    labels = []

    for label in audio_dirs.keys():
        for filename in audio_dirs[label].keys():
            file_name = f"{audio_path}/{label}/{filename}"
            class_label = label
            feature = extract_features(file_name, one_volume_count)
            features.append(feature)
            labels.append(class_label)

    features = np.array(features)
    labels = np.array(labels)
    return features, labels


def model_training(audio_dirs, configuration_path, stop_flag, one_volume_count):
    try:
        X, y = load_data(audio_dirs, configuration_path + "/audio", one_volume_count)

        # 编码标签
        encoder = LabelEncoder()
        y = encoder.fit_transform(y)
        y = to_categorical(y)

        # 数据集划分
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # 创建Sequential模型
        model = Sequential()
        model.add(
            Dense(256, input_shape=(X_train.shape[1],), activation="relu")
        )  # 输入层
        model.add(Dropout(0.5))
        model.add(Dense(128, activation="relu"))  # 隐藏层
        model.add(Dropout(0.5))
        model.add(Dense(len(encoder.classes_), activation="softmax"))  # 输出层

        # 编译模型
        model.compile(
            loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
        )

        class CustomCallback(Callback):
            def on_epoch_end(self, epoch, logs=None):
                model_training_queue.put({"epoch": f"{epoch+1}/100"})

        custom_callback = CustomCallback()
        model_training_queue.put({"type": "fit"})
        model_training_queue.put({"epoch": "0/100"})

        model.fit(
            X_train,
            y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[custom_callback],
        )

        # 评估模型
        model_training_queue.put({"type": "evaluate"})
        loss, accuracy = model.evaluate(X_test, y_test)
        model_training_queue.put({"accuracy": f"{accuracy:.4f}"})

        # 保存整个模型
        model.save(configuration_path + "/model.keras")
        np.save(configuration_path + "/classes.npy", encoder.classes_)

        stop_flag.set()
    except Exception as e:
        error_info = traceback.format_exc()
        print(error_info)
        messagebox.showinfo("error", error_info)
        model_training_queue.put({"type": "fail"})
        time.sleep(0.001)
        stop_flag.set()
