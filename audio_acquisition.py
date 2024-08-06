import pyaudio
import numpy as np
import librosa
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import wave
from pydub import AudioSegment

# 定义函数以从音频数据中提取 MFCC 特征
def extract_features_from_audio(data, sample_rate):
    # 将整型数据转换为浮点型数据
    data = data.astype(np.float32) / 32767.0

    mfccs = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=40, n_fft=1024)
    mfccs_processed = np.mean(mfccs.T, axis=0)
    return mfccs_processed.reshape(1, 40, 1, 1)  # 调整形状以匹配模型输入

# 定义预测函数
def predict_sound_type(model, features):
    prediction = model.predict(features)
    predicted_class = np.argmax(prediction, axis=1)
    return predicted_class[0]  # 返回预测的类别索引

# 加载模型
model = load_model('my_model.keras')

# 加载标签编码器
encoder = LabelEncoder()
encoder.classes_ = np.load('classes.npy', allow_pickle=True)

# 实时音频采集参数
CHUNK = 1024  # 每次读取的帧数
FORMAT = pyaudio.paInt16  # 采样格式
CHANNELS = 1  # 单声道
RATE = 44100  # 采样率
RECORD_SECONDS = 0.03  # 每次采集的秒数

# 设置声音活动检测的阈值
THRESHOLD = 0.01  # 根据实际情况调整

# 初始化 PyAudio
p = pyaudio.PyAudio()

# 打开音频流
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening...")

try:
    save_index = 1
    frames_list = []
    while True:
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # 将音频数据转换为 numpy 数组
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

        # 计算音频片段的平均能量
        energy = np.mean(np.abs(audio_data)) / 32767.0

        if energy > THRESHOLD:
            frames_list.extend(frames)
        elif len(frames_list) > 0:
            # 将音频数据转换为 numpy 数组
            audio_data = np.frombuffer(b''.join(frames_list), dtype=np.int16)

            # 提取 MFCC 特征
            mfccs = extract_features_from_audio(audio_data, RATE)

            # 预测声音类型
            predicted_class = predict_sound_type(model, mfccs)

            # 将整数类别转换回原始类别标签
            predicted_label = encoder.inverse_transform([predicted_class])
            print(f"Predicted sound type: {predicted_label[0]}")


            #保存音频文件
            # print(f"Saving audio...{save_index}")
            # save_path = f"audio_files/{save_index}.wav"
            # # 保存为 .wav 文件
            # with wave.open(save_path, "wb") as wf:
            #     wf.setnchannels(CHANNELS)
            #     wf.setsampwidth(p.get_sample_size(FORMAT))
            #     wf.setframerate(RATE)
            #     wf.writeframes(b''.join(frames_list))
            # save_index+=1

            
            frames_list = []

except KeyboardInterrupt:
    pass

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Stopped listening.")