import pyaudio
import numpy as np
from keras.api.models import load_model
from sklearn.preprocessing import LabelEncoder
import wave
import os
import queue


from model_training import extract_features

acquisition_audio_name_queue = queue.Queue()

def audio_acquisition(use_model,save_path,stop_flag,save_flag):
    if use_model:
        # 加载模型
        model = load_model(save_path+'/model.keras')

        # 加载标签编码器
        encoder = LabelEncoder()
        encoder.classes_ = np.load(save_path+'/classes.npy', allow_pickle=True)

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
        while not stop_flag.is_set():
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
                if use_model:
                    # 保存为 .wav 文件
                    with wave.open("temp.wav", "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames_list))
                    mfccs = extract_features("temp.wav")

                    # 准备输入数据
                    input_data = mfccs.reshape(1, 40, 1, 1)  # 重塑为模型输入的形状

                    # 使用模型进行预测
                    predictions = model.predict(input_data)

                    # 获取预测结果
                    predicted_class = np.argmax(predictions[0])

                    # 将整数类别转换回原始类别标签
                    predicted_label = encoder.inverse_transform([predicted_class])
                    print(f"Predicted sound type: {predicted_label[0]}")
                    acquisition_audio_name_queue.put(predicted_label[0])
                else:
                    audio_dirs = os.listdir(save_path)
                    for item in audio_dirs:
                        if save_index <= int(item.split('.')[0]):
                            save_index = int(item.split('.')[0])+1
                    #保存音频文件
                    print(f"Saving audio...{save_index}")
                    file_save_path = f"{save_path}/{save_index}.wav"
                    # 保存为 .wav 文件
                    with wave.open(file_save_path, "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames_list))
                    save_flag.set()
                
                frames_list = []

    except KeyboardInterrupt as e:
        print(e)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Stopped listening.")