import numpy as np
import pandas as pd
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import InputLayer, Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

# 数据预处理
def extract_features(file_path):
    y, sr = librosa.load(file_path, duration=3, offset=0.5)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfccs_processed = np.mean(mfccs.T,axis=0)
    return mfccs_processed

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

def model_training(audio_dirs,configuration_path):
    X, y = load_data(audio_dirs,configuration_path + "/audio")

    # 编码标签
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)
    y = to_categorical(y)

    # 数据集划分
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
    model.fit(X_train.reshape(-1, 40, 1, 1), y_train, epochs=10, batch_size=32)

    # 评估模型
    loss, accuracy = model.evaluate(X_test.reshape(-1, 40, 1, 1), y_test)
    print(f"Test accuracy: {accuracy}")

    # 保存整个模型
    model.save(configuration_path+'/model.keras')
    np.save(configuration_path+'/classes.npy', encoder.classes_)