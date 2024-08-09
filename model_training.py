import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,StandardScaler
from keras.api.models import Sequential
from keras.api.layers import InputLayer, Conv2D, MaxPooling2D, Flatten, Dense
from keras.api.utils import to_categorical
import queue
from keras.api.callbacks import Callback, ProgbarLogger

model_training_queue = queue.Queue()

# 第一次加载慢
librosa.load("temp.wav")

# 数据预处理
def extract_features(file_path):
    # 加载音频文件
    y, sr = librosa.load(file_path)
    
    # 计算 MFCCs
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfccs_processed = np.mean(mfccs.T, axis=0)
    
    # 计算其他特征
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr).T, axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr).T, axis=0)
    
    # 组合所有特征
    features = np.hstack([mfccs_processed, chroma, mel, contrast, tonnetz])
    
    return features

# 加载数据
def load_data(audio_dirs,audio_path):
    features = []
    labels = []

    for label in audio_dirs.keys():
        for filename in audio_dirs[label].keys():
            file_name = f"{audio_path}/{label}/{filename}"
            class_label = label
            feature = extract_features(file_name)
            features.append(feature)
            labels.append(class_label)

    features = np.array(features)
    labels = np.array(labels)
    return features, labels

def model_training(audio_dirs,configuration_path,stop_flag):
    X, y = load_data(audio_dirs,configuration_path + "/audio")

    # 编码标签
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)
    y = to_categorical(y)

    # 特征标准化
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # 数据集划分
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 构建模型
    model = Sequential([
        InputLayer(shape=(40, 1, 1)),  # 明确指定输入维度为 40x1x1
        Conv2D(32, (3, 1), activation='relu'),
        MaxPooling2D(pool_size=(2, 1)),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(len(encoder.classes_), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # 训练模型
    class CustomCallback(Callback):
        def on_epoch_end(self, epoch, logs=None):
            model_training_queue.put({"epoch":f"{epoch+1}/10"})
            # model_training_queue.put({"loss":f"{logs['loss']:.4f}"})
            # model_training_queue.put({"accuracy":f"{logs['accuracy']:.4f}"})
    custom_callback = CustomCallback()
    model_training_queue.put({"type":"fit"})
    model_training_queue.put({"epoch":"0/10"})
    model.fit(X_train.reshape(-1, 40, 1, 1), y_train, epochs=10, batch_size=32, callbacks=[custom_callback, ProgbarLogger()])

    # 评估模型
    model_training_queue.put({"type":"evaluate"})
    loss, accuracy = model.evaluate(X_test.reshape(-1, 40, 1, 1), y_test)
    # model_training_queue.put({"loss":f"{loss:.4f}"})
    model_training_queue.put({"accuracy":f"{accuracy:.4f}"})
    print(f"Test accuracy: {accuracy}")

    # 保存整个模型
    model.save(configuration_path+'/model.keras')
    np.save(configuration_path+'/classes.npy', encoder.classes_)

    stop_flag.set()