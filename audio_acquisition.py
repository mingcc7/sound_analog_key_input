import pyaudio
import numpy as np
import wave
import os
import queue
from tkinter import messagebox
import traceback

acquisition_audio_name_queue = queue.Queue()
acquisition_audio_energy_queue = queue.Queue()
acquisition_audio_probability_queue = queue.Queue()
volume_threshold_queue = queue.Queue()
one_volume_count_queue = queue.Queue()

# 实时音频采集参数
CHUNK = 1024  # 每次读取的帧数
FORMAT = pyaudio.paInt16  # 采样格式
CHANNELS = 1  # 单声道
RATE = 44100  # 采样率


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
        frames = []
        data_np_list = np.empty((0,), dtype=np.int16)
        min_energy = float("inf")
        max_energy = float("-inf")
        audio_index = 0
        zeros_data = np.zeros(CHUNK, dtype=np.int16).tobytes()
        one_volume_count = 10  # 单个音频取样次数
        while not stop_flag.is_set():
            data = stream.read(CHUNK)

            # 将数据转换为NumPy数组
            data_np = np.frombuffer(data, dtype=np.int16)
            data_np_list = np.concatenate((data_np_list, data_np))

            # 计算音频片段的平均能量
            energy = round((np.mean(np.abs(data_np)) / 32767.0) * 100, 2)

            if not volume_threshold_queue.empty():
                THRESHOLD = volume_threshold_queue.get()

            if not one_volume_count_queue.empty():
                one_volume_count = one_volume_count_queue.get()

            if energy > THRESHOLD:
                audio_index += 1
                frames.append(data)
                min_energy = min(min_energy, energy)
                max_energy = max(max_energy, energy)
            elif audio_index > 0:
                for _ in range(1, one_volume_count - audio_index + 1):
                    frames.append(zeros_data)
                audio_index = one_volume_count

            if len(frames) > 0 and audio_index == one_volume_count:
                audio_index = 0
                if use_model:
                    data_np_list = data_np_list.astype(np.float32) / 32768.0
                    features = extract_features(
                        None, one_volume_count, data_np_list, RATE
                    )

                    # 使用模型进行预测
                    predictions = model.predict(np.array([features]))

                    # 获取预测结果
                    predicted_class = np.argmax(predictions[0])

                    # 概率
                    probability = predictions[0][predicted_class]
                    print(probability)

                    # 将整数类别转换回原始类别标签
                    predicted_label = encoder.inverse_transform([predicted_class])
                    print(f"Predicted sound type: {predicted_label[0]}")

                    acquisition_audio_energy_queue.put((min_energy, max_energy))
                    acquisition_audio_probability_queue.put(probability)
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
                        wf.writeframes(b"".join(frames))
                    save_flag.set()

                frames = []
                data_np_list = np.empty((0,), dtype=np.int16)
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
