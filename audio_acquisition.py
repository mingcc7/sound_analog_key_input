import pyaudio
import numpy as np
import wave
import os
import queue
from tkinter import messagebox
import traceback

acquisition_audio_name_queue = queue.Queue()
acquisition_audio_energy_queue = queue.Queue()
volume_threshold_queue = queue.Queue()


def audio_acquisition(use_model, save_path, stop_flag, save_flag):
    try:
        acquisition_audio_energy_queue.queue.clear()

        if use_model:
            from keras.models import load_model
            from sklearn.preprocessing import LabelEncoder
            from model_training import extract_features

            # 加载模型
            model = load_model(save_path + "/model.keras")

            # 加载标签编码器
            encoder = LabelEncoder()
            encoder.classes_ = np.load(save_path + "/classes.npy", allow_pickle=True)

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
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print("Listening...")

        save_index = 1
        frames_list = []
        min_energy = float("inf")
        max_energy = float("-inf")
        audio_index = 0
        while not stop_flag.is_set():
            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            # 将音频数据转换为 numpy 数组
            audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)

            # 计算音频片段的平均能量
            energy = np.mean(np.abs(audio_data)) / 32767.0

            if not volume_threshold_queue.empty():
                THRESHOLD = volume_threshold_queue.get()

            if energy > THRESHOLD and audio_index < 3:
                audio_index += 1
                frames_list.extend(frames)
                min_energy = min(min_energy, energy)
                max_energy = max(max_energy, energy)
            elif len(frames_list) > 0:
                audio_index = 0
                if use_model:
                    # 保存为 .wav 文件
                    with wave.open("temp.wav", "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b"".join(frames_list))
                    features = extract_features("temp.wav")

                    # 使用模型进行预测
                    predictions = model.predict(np.array([features]))

                    # 获取预测结果
                    predicted_class = np.argmax(predictions[0])

                    # 将整数类别转换回原始类别标签
                    predicted_label = encoder.inverse_transform([predicted_class])
                    print(f"Predicted sound type: {predicted_label[0]}")
                    acquisition_audio_energy_queue.put((min_energy, max_energy))
                    acquisition_audio_name_queue.put(predicted_label[0])
                else:
                    audio_dirs = os.listdir(save_path)
                    for item in audio_dirs:
                        if save_index <= int(item.split(".")[0]):
                            save_index = int(item.split(".")[0]) + 1
                    # 保存音频文件
                    print(f"Saving audio...{save_index}")
                    file_save_path = f"{save_path}/{save_index}.wav"
                    # 保存为 .wav 文件
                    with wave.open(file_save_path, "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b"".join(frames_list))
                    save_flag.set()

                frames_list = []
                min_energy = float("inf")
                max_energy = float("-inf")

    except Exception as e:
        error_info = traceback.format_exc()
        print(error_info)
        messagebox.showinfo("error", error_info)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Stopped listening.")
