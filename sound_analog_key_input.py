try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import json
    import os
    import shutil
    import threading
    from natsort import natsorted
    import time
    import queue
    import sys
    import pygame
    import traceback

    from audio_acquisition import audio_acquisition
    from audio_acquisition import acquisition_audio_name_queue
    from audio_acquisition import acquisition_audio_energy_queue
    from audio_acquisition import volume_threshold_queue

    from key_controls import key_listener
    from key_controls import bind_key_thread_stop_flag
    from key_controls import key_queue
    from key_controls import key_press
    from key_controls import key_release

    # 无控制台运行时模型训练无此行代码会报错
    sys.stdout = open("log.log", "w")

    configuration_json_path = "configuration.json"

    with open(configuration_json_path, "r", encoding="utf-8") as file:
        configuration_json = json.load(file)

    with open(
        f"language/{configuration_json['language']}.json", "r", encoding="utf-8"
    ) as file:
        text_json = json.load(file)

    # 线程导入需要keras的模块，keras加载慢
    model_training = None
    model_training_queue = None
    import_model_success = False

    def import_model_training():
        try:
            print("import model training loading")
            model_training_Lable["text"] = text_json["loading"]
            model_test_Lable["text"] = text_json["loading"]
            global model_training
            from model_training import model_training

            global model_training_queue
            from model_training import model_training_queue

            global import_model_success
            import_model_success = True
            print("import model training success")

            try:
                model_training_Lable["text"] = ""
                model_test_Lable["text"] = ""
            except Exception as e:
                print(e)
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 窗口居中
    def center_window(window, width, height):
        try:
            # 获取屏幕宽度和高度
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()

            # 计算窗口左上角的位置坐标
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

            # 设置窗口的位置
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 退出窗口
    def delete_window():
        try:
            answer = messagebox.askquestion(
                text_json["verify"], text_json["want_to_continue"]
            )
            if answer == "yes":
                audio_acquisition_thread_stop_flag.set()
                model_test_thread_stop_flag.set()
                configuration_json["window_width"] = window.winfo_width()
                configuration_json["window_height"] = window.winfo_height()
                with open(configuration_json_path, "w", encoding="utf-8") as file:
                    json.dump(configuration_json, file, ensure_ascii=False, indent=4)
                window.destroy()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 语言选择
    def on_language_combobox_change(*args):
        try:
            selected_value = language_combo_var.get()
            configuration_json["language"] = selected_value
            with open(
                f"language/{configuration_json['language']}.json", "r", encoding="utf-8"
            ) as file:
                global text_json
                text_json = json.load(file)

            # 初始化组件名称
            window.title(text_json["title"])
            configuration_add_button["text"] = text_json["configuration_add"]
            configuration_update_button["text"] = text_json["configuration_update"]
            configuration_delete_button["text"] = text_json["configuration_delete"]
            audio_add_button["text"] = text_json["audio_add"]
            audio_update_button["text"] = text_json["audio_update"]
            audio_delete_button["text"] = text_json["audio_delete"]
            audio_acquisition_button["text"] = text_json["audio_acquisition"]
            audio_acquisition_stop_button["text"] = text_json["audio_acquisition_stop"]
            model_training_button["text"] = text_json["model_training"]
            model_test_button["text"] = text_json["model_test"]
            bind_key_add_button["text"] = text_json["bind_key_add"]

            start_running_button["text"] = text_json["start_running"]
            volume_threshold_set_button["text"] = text_json["volume_threshold_set"]

            if audio_combo_var.get() != "":
                bind_key_modules_load()

            audio_file_pack()
            model_training_Lable["text"] = ""
            volume_energy_Lable["text"] = ""
            model_test_Lable["text"] = ""
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 配置选择
    def on_configuration_combobox_change(*args):
        try:
            if not start_running_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            else:
                # 停止声音采集
                on_audio_acquisition_stop_button_click()

                selected_value = configuration_combo_var.get()
                configuration_json["now_configuration"] = selected_value
                configuration_name_entry.delete(0, tk.END)
                configuration_name_entry.insert(
                    0, configuration_json["now_configuration"]
                )
                volume_threshold_entry.delete(0, tk.END)

                if selected_value != "":
                    volume_threshold_entry.insert(
                        0,
                        configuration_json["configuration"][selected_value][
                            "volume_threshold"
                        ],
                    )

                # 更新声音选择
                audio_name_entry.delete(0, tk.END)
                update_audio_combobox()

                bind_key_modules_load()

                model_training_Lable["text"] = ""
                volume_energy_Lable["text"] = ""
                model_test_Lable["text"] = ""
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 更新配置选择
    def update_configuration_combobox(configuration_name):
        try:
            configuration_combo_values = os.listdir(f"configuration")
            configuration_combo["values"] = configuration_combo_values
            configuration_combo_var.set(configuration_name)
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 添加配置
    def on_configuration_add_button_click():
        try:
            configuration_name = configuration_name_entry.get()
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif (
                not os.path.exists("configuration/" + configuration_name)
                and configuration_name != ""
            ):
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    if not os.path.exists("configuration"):
                        os.mkdir(f"configuration")
                    try:
                        os.mkdir(f"configuration/{configuration_name}")
                    except FileExistsError:
                        print(f"configuration/{configuration_name} already exists")
                    try:
                        os.mkdir(f"configuration/{configuration_name}/audio")
                    except FileExistsError:
                        print(
                            f"configuration/{configuration_name}/audio already exists"
                        )

                    configuration_json["configuration"][configuration_name] = {
                        "volume_threshold": 1.0,
                        "audio": {},
                    }
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json, file, ensure_ascii=False, indent=4
                        )

                    # 更新配置选择
                    update_configuration_combobox(configuration_name)

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif configuration_name == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_name_cannot_be_empty"]
                )
            else:
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_name_already_exists"]
                )
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 修改配置
    def on_configuration_update_button_click():
        try:
            configuration_name = configuration_name_entry.get()
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            # 配置名称没改变
            elif (
                configuration_combo_var.get() == configuration_name
                and configuration_name != ""
                and configuration_combo["values"] != ""
            ):
                messagebox.showinfo(text_json["tips"], text_json["success"])
            # 配置名称改变
            elif (
                not os.path.exists("configuration/" + configuration_name)
                and configuration_name != ""
                and configuration_combo["values"] != ""
            ):
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    os.rename(
                        f"configuration/{configuration_combo_var.get()}",
                        f"configuration/{configuration_name}",
                    )

                    if (
                        configuration_combo_var.get()
                        in configuration_json["configuration"]
                    ):
                        configuration_json["configuration"][configuration_name] = (
                            configuration_json["configuration"][
                                configuration_combo_var.get()
                            ]
                        )
                        configuration_json["configuration"].pop(
                            configuration_combo_var.get()
                        )
                        with open(
                            configuration_json_path, "w", encoding="utf-8"
                        ) as file:
                            json.dump(
                                configuration_json, file, ensure_ascii=False, indent=4
                            )

                    # 更新配置选择
                    update_configuration_combobox(configuration_name)

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            elif configuration_name == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_name_cannot_be_empty"]
                )
            else:
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_name_already_exists"]
                )
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 删除配置
    def on_configuration_delete_button_click():
        try:
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            else:
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    shutil.rmtree(f"configuration/{configuration_combo_var.get()}")

                    configuration_json["configuration"].pop(
                        configuration_combo_var.get()
                    )
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json, file, ensure_ascii=False, indent=4
                        )

                    configuration_combo_var.set("")

                    # 更新配置选择
                    update_configuration_combobox("")

                    messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 声音选择
    def on_audio_combobox_change(*args):
        try:
            # 停止声音采集
            on_audio_acquisition_stop_button_click()

            selected_value = audio_combo_var.get()
            audio_name_entry.delete(0, tk.END)
            audio_name_entry.insert(0, selected_value)
            audio_file_pack()

            if audio_combo_var.get() != "":
                bind_key_modules_load()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 播放声音文件
    def play_audio_file(file_path):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.quit()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 声音文件
    def audio_file_pack(update=False):
        try:
            if not update:
                for widget in audio_file_frame.winfo_children():
                    widget.destroy()
            if audio_combo_var.get() != "":
                audio_dirs = natsorted(
                    os.listdir(
                        f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}"
                    )
                )
                if update:
                    audio_dirs = [audio_dirs[len(audio_dirs) - 1]]
                for item in audio_dirs:
                    audio_file_row_frame = tk.Frame(audio_file_frame)
                    audio_file_row_frame.pack(side=tk.BOTTOM, fill=tk.X)
                    label = tk.Label(audio_file_row_frame, text=item)
                    label.pack(side=tk.LEFT, padx=5, pady=1)
                    file_path = f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}/{item}"
                    # 删除声音文件
                    button = tk.Button(
                        audio_file_row_frame,
                        text=text_json["delete"],
                        command=lambda file_path=file_path: on_audio_file_delete_button_click(
                            file_path
                        ),
                    )
                    button.pack(side=tk.RIGHT, padx=5, pady=1)
                    # 播放声音文件
                    button = tk.Button(
                        audio_file_row_frame,
                        text=text_json["play"],
                        command=lambda file_path=file_path: play_audio_file(file_path),
                    )
                    button.pack(side=tk.RIGHT, padx=5, pady=1)

            # 更新滚动区域
            if audio_file_frame.winfo_children():
                audio_file_frame.update_idletasks()
                audio_file_canvas.config(
                    scrollregion=audio_file_canvas.bbox("all"),
                    width=audio_file_frame.winfo_reqwidth(),
                )
                audio_file_canvas.yview_moveto(0.0)
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 删除声音文件
    def on_audio_file_delete_button_click(file_path):
        try:
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            else:
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    os.remove(file_path)
                    audio_file_pack()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 更新声音选择
    def update_audio_combobox():
        try:
            audio_combo_values = []
            if configuration_combo_var.get() != "":
                audio_combo_values = os.listdir(
                    f"configuration/{configuration_combo_var.get()}/audio"
                )
            audio_combo["values"] = audio_combo_values
            audio_combo_var.set(audio_name_entry.get())
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 添加声音
    def on_audio_add_button_click():
        try:
            audio_name = audio_name_entry.get()
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            elif (
                not os.path.exists(
                    f"configuration/{configuration_combo_var.get()}/audio/{audio_name}"
                )
                and audio_name != ""
            ):
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    try:
                        os.mkdir(
                            f"configuration/{configuration_combo_var.get()}/audio/{audio_name}"
                        )
                    except FileExistsError:
                        print(
                            f"configuration/{configuration_combo_var.get()}/audio/{audio_name} already exists"
                        )

                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["audio"][audio_name] = {
                        "1": {
                            "key": [],
                            "type1": "click",
                            "type2": "simultaneously",
                            "volume_threshold": [1.0, 99.0],
                        }
                    }
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json, file, ensure_ascii=False, indent=4
                        )

                    # 更新声音选择
                    update_audio_combobox()

                    bind_key_modules_load()

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif audio_name == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_name_cannot_be_empty"]
                )
            else:
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_name_already_exists"]
                )
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 修改声音
    def on_audio_update_button_click():
        try:
            audio_name = audio_name_entry.get()
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            # 声音名称没改变
            elif (
                audio_combo_var.get() == audio_name
                and audio_name != ""
                and audio_combo["values"] != ""
            ):
                messagebox.showinfo(text_json["tips"], text_json["success"])
            # 声音名称改变
            elif (
                not os.path.exists(
                    f"configuration/{configuration_combo_var.get()}/audio/{audio_name}"
                )
                and audio_name != ""
                and audio_combo["values"] != ""
            ):
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    os.rename(
                        f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}",
                        f"configuration/{configuration_combo_var.get()}/audio/{audio_name}",
                    )

                    configuration_json["configuration"][configuration_combo_var.get()][
                        "audio"
                    ][audio_name] = configuration_json["configuration"][
                        configuration_combo_var.get()
                    ][
                        "audio"
                    ][
                        audio_combo_var.get()
                    ]
                    configuration_json["configuration"][configuration_combo_var.get()][
                        "audio"
                    ].pop(audio_combo_var.get())
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json, file, ensure_ascii=False, indent=4
                        )

                    # 更新声音选择
                    update_audio_combobox()

                    bind_key_modules_load()

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            elif audio_name == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_name_cannot_be_empty"]
                )
            else:
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_name_already_exists"]
                )
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 删除声音
    def on_audio_delete_button_click():
        try:
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            else:
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    shutil.rmtree(
                        f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}"
                    )

                    configuration_json["configuration"][configuration_combo_var.get()][
                        "audio"
                    ].pop(audio_combo_var.get())
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json, file, ensure_ascii=False, indent=4
                        )

                    audio_combo_var.set("")

                    # 更新声音选择
                    update_audio_combobox()

                    bind_key_modules_load()

                    messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 声音采集
    audio_acquisition_thread_stop_flag = threading.Event()
    audio_acquisition_thread_stop_flag.set()
    audio_acquisition_thread_save_flag = threading.Event()

    def on_audio_acquisition_button_click():
        try:
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            elif audio_acquisition_thread_stop_flag.is_set():
                audio_acquisition_thread_stop_flag.clear()
                audio_acquisition_thread_save_flag.clear()
                volume_threshold = 0.01
                volume_threshold = (
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["volume_threshold"]
                    / 100
                )
                volume_threshold_queue.put(volume_threshold)
                audio_acquisition_thread = threading.Thread(
                    target=audio_acquisition,
                    args=(
                        False,
                        f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}",
                        audio_acquisition_thread_stop_flag,
                        audio_acquisition_thread_save_flag,
                    ),
                )
                audio_acquisition_thread.start()
                audio_acquisition_button.config(bg="red")

                def save_flag():
                    try:
                        while not audio_acquisition_thread_stop_flag.is_set():
                            if audio_acquisition_thread_save_flag.is_set():
                                audio_acquisition_thread_save_flag.clear()
                                audio_file_pack(update=True)
                            time.sleep(0.001)
                    except Exception as e:
                        error_info = traceback.format_exc()
                        print(error_info)
                        messagebox.showinfo("error", error_info)

                save_flag_thread = threading.Thread(target=save_flag)
                save_flag_thread.start()
            else:
                on_audio_acquisition_stop_button_click()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 声音采集停止
    def on_audio_acquisition_stop_button_click():
        try:
            audio_acquisition_thread_stop_flag.set()
            audio_acquisition_button.config(bg="SystemButtonFace")
            model_test_thread_stop_flag.set()
            model_test_button.config(bg="SystemButtonFace")
            start_running_thread_stop_flag.set()
            start_running_button.config(bg="SystemButtonFace")
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 模型训练
    model_training_thread_stop_flag = threading.Event()
    model_training_thread_stop_flag.set()

    def on_model_training_button_click():
        try:
            if not import_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            else:
                audio_dirs = os.listdir(
                    f"configuration/{configuration_combo_var.get()}/audio"
                )
                audio_json = {}
                count = 0
                for item in audio_dirs:
                    audio_json[item] = {}
                    audio_file_dirs = os.listdir(
                        f"configuration/{configuration_combo_var.get()}/audio/{item}"
                    )
                    for file_item in audio_file_dirs:
                        audio_json[item][file_item] = {}
                        count += 1
                if count == 0:
                    messagebox.showinfo(
                        text_json["tips"], text_json["audio_file_cannot_be_empty"]
                    )
                elif count == 1:
                    messagebox.showinfo(
                        text_json["tips"], text_json["audio_file_cannot_be_1"]
                    )
                else:
                    model_training_thread_stop_flag.clear()
                    model_training_thread = threading.Thread(
                        target=model_training,
                        args=(
                            audio_json,
                            f"configuration/{configuration_combo_var.get()}",
                            model_training_thread_stop_flag,
                        ),
                    )
                    model_training_thread.start()
                    model_training_Lable["text"] = text_json["fit"]
                    model_training_button.config(bg="skyblue")

                    def queue_get():
                        try:
                            while not model_training_thread_stop_flag.is_set():
                                if not model_training_queue.empty():
                                    queue_get = model_training_queue.get(timeout=1)
                                    key = list(queue_get.keys())[0]
                                    values = list(queue_get.values())[0]
                                    if key == "type":
                                        model_training_Lable["text"] = (
                                            f"{text_json['status']}:{text_json[values]}"
                                        )
                                    elif key == "epoch":
                                        model_training_Lable["text"] = (
                                            f"{text_json['schedule']}:{values}"
                                        )
                                    elif key == "accuracy":
                                        model_training_Lable["text"] = (
                                            f"{text_json['accuracy']}:{values}"
                                        )
                                time.sleep(0.001)

                            model_training_button.config(bg="SystemButtonFace")
                        except Exception as e:
                            error_info = traceback.format_exc()
                            print(error_info)
                            messagebox.showinfo("error", error_info)

                    save_flag_thread = threading.Thread(target=queue_get)
                    save_flag_thread.start()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 音量阈值设置
    def on_volume_threshold_set_button_click():
        try:
            if configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            else:
                try:
                    volume_threshold = float(volume_threshold_entry.get())
                    if volume_threshold < 1:
                        messagebox.showinfo(
                            text_json["tips"],
                            text_json["volume_threshold_cannot_less_1"],
                        )
                    else:
                        configuration_json["configuration"][
                            configuration_json["now_configuration"]
                        ]["volume_threshold"] = volume_threshold
                        with open(
                            configuration_json_path, "w", encoding="utf-8"
                        ) as file:
                            json.dump(
                                configuration_json, file, ensure_ascii=False, indent=4
                            )
                        volume_threshold_queue.put(volume_threshold / 100)
                        messagebox.showinfo(text_json["tips"], text_json["success"])
                except Exception as e:
                    messagebox.showinfo(
                        text_json["tips"], text_json["volume_threshold_only_be_number"]
                    )

        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 模型测试
    model_test_thread_stop_flag = threading.Event()
    model_test_thread_stop_flag.set()

    def on_model_test_button_click():
        try:
            if not import_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                on_audio_acquisition_stop_button_click()
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif not audio_acquisition_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_acquisition_listening"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            elif not os.path.exists(
                f"configuration/{configuration_combo_var.get()}/model.keras"
            ):
                messagebox.showinfo(text_json["tips"], text_json["model_not_exist"])
            else:
                model_test_thread_stop_flag.clear()
                volume_threshold = 0.01
                volume_threshold = (
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["volume_threshold"]
                    / 100
                )
                volume_threshold_queue.put(volume_threshold)
                audio_acquisition_thread = threading.Thread(
                    target=audio_acquisition,
                    args=(
                        True,
                        f"configuration/{configuration_combo_var.get()}",
                        model_test_thread_stop_flag,
                        None,
                    ),
                )
                audio_acquisition_thread.start()
                model_test_button.config(bg="red")

                def get_name_queue():
                    try:
                        index = 1
                        while not model_test_thread_stop_flag.is_set():
                            energy = (0.0123, 0.01234)
                            if not acquisition_audio_energy_queue.empty():
                                energy = acquisition_audio_energy_queue.get(timeout=1)
                                energy = tuple(
                                    f"{element * 100:.2f}" for element in energy
                                )
                                volume_energy_Lable["text"] = f"{energy[0]}-{energy[1]}"
                            if not acquisition_audio_name_queue.empty():
                                model_test_Lable["text"] = (
                                    f"{index}:{acquisition_audio_name_queue.get(timeout=1)}"
                                )
                                index += 1
                            time.sleep(0.001)
                    except Exception as e:
                        error_info = traceback.format_exc()
                        print(error_info)
                        messagebox.showinfo("error", error_info)

                get_name_queue_thread = threading.Thread(target=get_name_queue)
                get_name_queue_thread.start()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 绑定按键模块加载
    bind_key_button_map = {}
    bind_key_Lable_map = {}
    bind_key_type1_combo_var_map = {}
    bind_key_type1_combo_map = {}
    bind_key_type2_combo_var_map = {}
    bind_key_type2_combo_map = {}
    bind_key_volume_min_threshold_entry_map = {}
    bind_key_volume_max_threshold_entry_map = {}

    def bind_key_modules_load():
        for widget in bind_key_modules_frame.winfo_children():
            widget.destroy()

        if (
            audio_combo_var.get()
            not in configuration_json["configuration"][
                configuration_json["now_configuration"]
            ]["audio"]
        ):
            return
        bind_key_json = configuration_json["configuration"][
            configuration_json["now_configuration"]
        ]["audio"][audio_combo_var.get()]

        for key, value in bind_key_json.items():
            # 按键绑定模块容器
            bind_key_module_frame = tk.Frame(bind_key_modules_frame)
            bind_key_module_frame.pack(fill=tk.BOTH, side=tk.TOP)

            # 按键绑定容器
            bind_key_frame = tk.Frame(bind_key_module_frame)
            bind_key_frame.pack(fill=tk.BOTH)

            # 按键绑定
            bind_key_button_map[key] = tk.Button(
                bind_key_frame, command=lambda key=key: on_bind_key_button_click(key)
            )
            bind_key_button_map[key].pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_button_map[key]["text"] = text_json["bind_key"]

            # 按键绑定结果
            bind_key_Lable_map[key] = tk.Label(bind_key_frame)
            bind_key_Lable_map[key].pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_Lable_map[key]["text"] = value["key"]

            # 按键绑定设置容器
            bind_key_set_frame = tk.Frame(bind_key_module_frame)
            bind_key_set_frame.pack(fill=tk.BOTH)

            # 按键类型1选择
            bind_key_type1_combo_var_map[key] = tk.StringVar()
            bind_key_type1_combo_var_map[key].trace_add(
                "write",
                lambda *args, key=key: on_bind_key_type_combobox_change(
                    *args, key=key, type_index=1
                ),
            )
            bind_key_type1_combo_map[key] = ttk.Combobox(
                bind_key_set_frame,
                textvariable=bind_key_type1_combo_var_map[key],
                state="readonly",
                width=4,
            )
            bind_key_type1_combo_map[key].pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_type1_combo_map[key]["values"] = [
                text_json["click"],
                text_json["short_press"],
                text_json["hold"],
                text_json["release"],
            ]
            bind_key_type1_combo_map[key].set(text_json[value["type1"]])

            # 按键类型2选择
            bind_key_type2_combo_var_map[key] = tk.StringVar()
            bind_key_type2_combo_var_map[key].trace_add(
                "write",
                lambda *args, key=key: on_bind_key_type_combobox_change(
                    *args, key=key, type_index=2
                ),
            )
            bind_key_type2_combo_map[key] = ttk.Combobox(
                bind_key_set_frame,
                textvariable=bind_key_type2_combo_var_map[key],
                state="readonly",
                width=4,
            )
            bind_key_type2_combo_map[key].pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_type2_combo_map[key]["values"] = [
                text_json["simultaneously"],
                text_json["sequentially"],
            ]
            bind_key_type2_combo_map[key].set(text_json[value["type2"]])

            # 绑定按键音量最低阈值
            bind_key_volume_min_threshold_entry_map[key] = tk.Entry(
                bind_key_set_frame, width=4
            )
            bind_key_volume_min_threshold_entry_map[key].pack(
                side=tk.LEFT, padx=5, pady=1
            )
            bind_key_volume_min_threshold_entry_map[key].insert(
                0, value["volume_threshold"][0]
            )

            # 绑定按键音量阈值中间符号
            bind_key_volume_threshold_middle_Lable = tk.Label(
                bind_key_set_frame, text="-"
            )
            bind_key_volume_threshold_middle_Lable.pack(side=tk.LEFT, pady=1)

            # 绑定按键音量最高阈值
            bind_key_volume_max_threshold_entry_map[key] = tk.Entry(
                bind_key_set_frame, width=4
            )
            bind_key_volume_max_threshold_entry_map[key].pack(
                side=tk.LEFT, padx=5, pady=1
            )
            bind_key_volume_max_threshold_entry_map[key].insert(
                0, value["volume_threshold"][1]
            )

            # 绑定按键音量阈值设置
            bind_key_volume_threshold_set_button = tk.Button(
                bind_key_set_frame,
                command=lambda key=key: on_bind_key_volume_threshold_set_button_click(
                    key
                ),
            )
            bind_key_volume_threshold_set_button.pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_volume_threshold_set_button["text"] = text_json[
                "bind_key_volume_threshold_set"
            ]

            # 删除绑定按键
            bind_key_del_button = tk.Button(
                bind_key_set_frame,
                command=lambda key=key: on_bind_key_del_button_click(key),
            )
            bind_key_del_button.pack(side=tk.LEFT, padx=5, pady=1)
            bind_key_del_button["text"] = text_json["bind_key_del"]

        # 更新滚动区域
        if bind_key_modules_frame.winfo_children():
            bind_key_modules_frame.update_idletasks()
            bind_key_modules_canvas.config(
                scrollregion=bind_key_modules_canvas.bbox("all")
            )
            bind_key_modules_canvas.yview_moveto(0.0)

    # 绑定按键删除
    def on_bind_key_del_button_click(key):
        try:
            answer = messagebox.askquestion(
                text_json["verify"], text_json["want_to_continue"]
            )
            if answer == "yes":
                configuration_json["configuration"][
                    configuration_json["now_configuration"]
                ]["audio"][audio_combo_var.get()].pop(key)
                with open(configuration_json_path, "w", encoding="utf-8") as file:
                    json.dump(configuration_json, file, ensure_ascii=False, indent=4)

                bind_key_modules_load()

                messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 绑定按键音量阈值设置
    def on_bind_key_volume_threshold_set_button_click(key):
        try:
            min = bind_key_volume_min_threshold_entry_map[key].get()
            max = bind_key_volume_max_threshold_entry_map[key].get()
            try:
                min = float(min)
                max = float(max)
            except Exception as e:
                messagebox.showinfo(
                    text_json["tips"], text_json["volume_threshold_only_be_number"]
                )
                return
            if min < 1 or max < 1:
                messagebox.showinfo(
                    text_json["tips"],
                    text_json["volume_threshold_cannot_less_1"],
                )
                return

            configuration_json["configuration"][
                configuration_json["now_configuration"]
            ]["audio"][audio_combo_var.get()][key]["volume_threshold"] = [min, max]

            with open(configuration_json_path, "w", encoding="utf-8") as file:
                json.dump(configuration_json, file, ensure_ascii=False, indent=4)
            messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 绑定按键添加
    def on_bind_key_add_button_click():
        try:
            if not bind_key_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["bind_key_in_progress"]
                )
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            else:
                answer = messagebox.askquestion(
                    text_json["verify"], text_json["want_to_continue"]
                )
                if answer == "yes":
                    bind_key_json = configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["audio"][audio_combo_var.get()]
                    if len(bind_key_json) > 0:
                        max_key = max(map(int, bind_key_json.keys()))
                    else:
                        max_key = 0
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["audio"][audio_combo_var.get()][f"{max_key+1}"] = {
                        "key": [],
                        "type1": "click",
                        "type2": "simultaneously",
                        "volume_threshold": [1.0, 99.0],
                    }
                    with open(configuration_json_path, "w", encoding="utf-8") as file:
                        json.dump(
                            configuration_json,
                            file,
                            ensure_ascii=False,
                            indent=4,
                        )
                    bind_key_modules_load()

        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 绑定按键
    bind_key_thread_stop_flag.set()

    def on_bind_key_button_click(key_name):
        try:
            if not bind_key_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["bind_key_in_progress"]
                )
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            else:
                bind_key_thread_stop_flag.clear()
                while not key_queue.empty():
                    try:
                        key_queue.get_nowait()
                    except queue.Empty:
                        break
                key_listener_thread = threading.Thread(target=key_listener)
                key_listener_thread.start()
                bind_key_button_map[key_name].config(bg="red")

                def queue_get():
                    try:
                        keys = []
                        stop = False
                        while not bind_key_thread_stop_flag.is_set():
                            while not key_queue.empty():
                                key = key_queue.get(timeout=1)
                                keys.append(f"{key}")
                                bind_key_Lable_map[key_name]["text"] = keys

                                configuration_json["configuration"][
                                    configuration_json["now_configuration"]
                                ]["audio"][audio_combo_var.get()][key_name][
                                    "key"
                                ] = keys
                                with open(
                                    configuration_json_path, "w", encoding="utf-8"
                                ) as file:
                                    json.dump(
                                        configuration_json,
                                        file,
                                        ensure_ascii=False,
                                        indent=4,
                                    )
                                time.sleep(0.5)
                                stop = True
                            if stop:
                                bind_key_thread_stop_flag.set()

                            time.sleep(0.001)
                        bind_key_button_map[key_name].config(bg="SystemButtonFace")
                    except Exception as e:
                        error_info = traceback.format_exc()
                        print(error_info)
                        messagebox.showinfo("error", error_info)

                queue_get_thread = threading.Thread(target=queue_get)
                queue_get_thread.start()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 绑定按键类型
    def on_bind_key_type_combobox_change(name, index, mode, key, type_index):
        try:
            if not bind_key_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["bind_key_in_progress"]
                )
            elif audio_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_now_cannot_be_empty"]
                )
            else:
                if type_index == 1:
                    index = bind_key_type1_combo_map[key].current()
                    type1 = ["click", "short_press", "hold", "release"]
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["audio"][audio_combo_var.get()][key]["type1"] = type1[index]
                elif type_index == 2:
                    index = bind_key_type2_combo_map[key].current()
                    type2 = ["simultaneously", "sequentially"]
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["audio"][audio_combo_var.get()][key]["type2"] = type2[index]

                with open(configuration_json_path, "w", encoding="utf-8") as file:
                    json.dump(configuration_json, file, ensure_ascii=False, indent=4)
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    # 开始运行
    start_running_thread_stop_flag = threading.Event()
    start_running_thread_stop_flag.set()

    def on_start_running_button_click():
        try:
            if not import_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                on_audio_acquisition_stop_button_click()
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_test_in_progress"]
                )
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["model_training_in_progress"]
                )
            elif not audio_acquisition_thread_stop_flag.is_set():
                messagebox.showinfo(
                    text_json["tips"], text_json["audio_acquisition_listening"]
                )
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(
                    text_json["tips"], text_json["configuration_now_cannot_be_empty"]
                )
            elif not os.path.exists(
                f"configuration/{configuration_combo_var.get()}/model.keras"
            ):
                messagebox.showinfo(text_json["tips"], text_json["model_not_exist"])
            else:
                start_running_thread_stop_flag.clear()
                volume_threshold = 0.01
                volume_threshold = (
                    configuration_json["configuration"][
                        configuration_json["now_configuration"]
                    ]["volume_threshold"]
                    / 100
                )
                volume_threshold_queue.put(volume_threshold)
                start_running_thread = threading.Thread(
                    target=audio_acquisition,
                    args=(
                        True,
                        f"configuration/{configuration_combo_var.get()}",
                        start_running_thread_stop_flag,
                        None,
                    ),
                )
                start_running_thread.start()
                start_running_button.config(bg="red")

                def get_name_queue():
                    try:
                        wait_key_release_audio = {}
                        key_index = {}
                        while not start_running_thread_stop_flag.is_set():
                            if not acquisition_audio_name_queue.empty():
                                audio = acquisition_audio_name_queue.get(timeout=1)
                                energy = acquisition_audio_energy_queue.get(timeout=1)

                                for id, value in configuration_json["configuration"][
                                    configuration_json["now_configuration"]
                                ]["audio"][audio].items():
                                    if not (
                                        value["volume_threshold"][0] / 100 <= energy[1]
                                        and energy[1]
                                        <= value["volume_threshold"][1] / 100
                                    ):
                                        continue

                                    if value["type2"] == "simultaneously":
                                        if value["type1"] == "click":
                                            key_press(value["key"])
                                            key_release(value["key"])
                                        elif value["type1"] == "short_press":
                                            if audio not in wait_key_release_audio:
                                                wait_key_release_audio[audio] = 0
                                                key_press(value["key"])
                                            elif wait_key_release_audio[audio] == 0:
                                                key_press(value["key"])
                                        elif value["type1"] == "hold":
                                            key_release(value["key"])
                                            key_press(value["key"])
                                        elif value["type1"] == "release":
                                            key_release(value["key"])
                                    elif value["type2"] == "sequentially":
                                        if audio not in key_index:
                                            key_index[audio] = 0
                                        else:
                                            key_index[audio] += 1
                                        key = [
                                            value["key"][
                                                key_index[audio] % len(value["key"])
                                            ]
                                        ]
                                        if value["type1"] == "click":
                                            key_press(key)
                                            key_release(key)
                                        elif value["type1"] == "short_press":
                                            key_press(key)
                                        elif value["type1"] == "hold":
                                            key_press(key)
                                        elif value["type1"] == "release":
                                            key_release(key)

                                    def wait_key_release(audio, key, type2):
                                        if type2 == "simultaneously":
                                            wait_key_release_audio[audio] += 1
                                            time.sleep(0.5)
                                            wait_key_release_audio[audio] -= 1
                                            if wait_key_release_audio[audio] == 0:
                                                key_release(key)
                                        elif type2 == "sequentially":
                                            time.sleep(0.5)
                                            key_release(key)

                                    if value["type1"] == "short_press":
                                        if value["type2"] == "simultaneously":
                                            wait_key_release_thread = threading.Thread(
                                                target=wait_key_release,
                                                args=(
                                                    audio,
                                                    value["key"],
                                                    value["type2"],
                                                ),
                                            )
                                        elif value["type2"] == "sequentially":
                                            wait_key_release_thread = threading.Thread(
                                                target=wait_key_release,
                                                args=(
                                                    audio,
                                                    key,
                                                    value["type2"],
                                                ),
                                            )
                                        wait_key_release_thread.start()
                            time.sleep(0.001)
                    except Exception as e:
                        error_info = traceback.format_exc()
                        print(error_info)
                        messagebox.showinfo("error", error_info)

                get_name_queue_thread = threading.Thread(target=get_name_queue)
                get_name_queue_thread.start()
        except Exception as e:
            error_info = traceback.format_exc()
            print(error_info)
            messagebox.showinfo("error", error_info)

    if __name__ == "__main__":
        window = tk.Tk()
        # 调用center_window函数使窗口居中
        center_window(
            window,
            configuration_json["window_width"],
            configuration_json["window_height"],
        )

        # 居中容器
        center_frame = tk.Frame(window)
        center_frame.pack(expand=True)

        # 左侧容器
        top_frame = tk.Frame(center_frame)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH)

        # 左侧容器
        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # 语言选择
        language_combo_values = []
        language_dirs = os.listdir("language")
        for item in language_dirs:
            language_combo_values.append(item.split(".")[0])
        language_combo_var = tk.StringVar()
        language_combo_var.trace_add("write", on_language_combobox_change)
        language_combo = ttk.Combobox(
            left_frame,
            textvariable=language_combo_var,
            values=language_combo_values,
            state="readonly",
        )
        language_combo.pack(pady=1, fill=tk.BOTH)

        # 配置选择
        if not os.path.exists("configuration"):
            os.mkdir("configuration")
        configuration_combo_values = os.listdir(f"configuration")
        configuration_combo_var = tk.StringVar()
        configuration_combo_var.trace_add("write", on_configuration_combobox_change)
        configuration_combo = ttk.Combobox(
            left_frame,
            textvariable=configuration_combo_var,
            values=configuration_combo_values,
            state="readonly",
        )
        configuration_combo.pack(pady=1, fill=tk.BOTH)

        # 配置名称
        configuration_name_entry = tk.Entry(left_frame)
        configuration_name_entry.pack(pady=1, fill=tk.BOTH)

        # 配置容器
        configuration_frame = tk.Frame(left_frame)
        configuration_frame.pack(fill=tk.BOTH)

        # 添加配置
        configuration_add_button = tk.Button(
            configuration_frame, command=on_configuration_add_button_click
        )
        configuration_add_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 修改配置
        configuration_update_button = tk.Button(
            configuration_frame, command=on_configuration_update_button_click
        )
        configuration_update_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 删除配置
        configuration_delete_button = tk.Button(
            configuration_frame, command=on_configuration_delete_button_click
        )
        configuration_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音选择
        audio_combo_var = tk.StringVar()
        audio_combo_var.trace_add("write", on_audio_combobox_change)
        audio_combo = ttk.Combobox(
            left_frame, textvariable=audio_combo_var, state="readonly"
        )
        audio_combo.pack(pady=1, fill=tk.BOTH)

        # 声音名称
        audio_name_entry = tk.Entry(left_frame)
        audio_name_entry.pack(pady=1, fill=tk.BOTH)

        # 声音容器
        audio_frame = tk.Frame(left_frame)
        audio_frame.pack(fill=tk.BOTH)

        # 添加声音
        audio_add_button = tk.Button(audio_frame, command=on_audio_add_button_click)
        audio_add_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 修改声音
        audio_update_button = tk.Button(
            audio_frame, command=on_audio_update_button_click
        )
        audio_update_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 删除声音
        audio_delete_button = tk.Button(
            audio_frame, command=on_audio_delete_button_click
        )
        audio_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 右侧容器
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # 声音采集容器
        audio_acquisition_frame = tk.Frame(right_frame)
        audio_acquisition_frame.pack()

        # 声音采集
        audio_acquisition_button = tk.Button(
            audio_acquisition_frame, command=on_audio_acquisition_button_click
        )
        audio_acquisition_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音采集停止
        audio_acquisition_stop_button = tk.Button(
            audio_acquisition_frame, command=on_audio_acquisition_stop_button_click
        )
        audio_acquisition_stop_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音文件容器
        audio_file_scrollbar_frame = tk.Frame(right_frame)
        audio_file_scrollbar_frame.pack(fill=tk.BOTH)

        audio_file_scrollbar = tk.Scrollbar(audio_file_scrollbar_frame)
        audio_file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        audio_file_canvas = tk.Canvas(
            audio_file_scrollbar_frame,
            yscrollcommand=audio_file_scrollbar.set,
            height=240,
        )
        audio_file_canvas.pack()
        audio_file_scrollbar.config(command=audio_file_canvas.yview)

        audio_file_frame = tk.Frame(audio_file_canvas)
        audio_file_canvas.create_window((0, 0), window=audio_file_frame, anchor="nw")

        audio_file_canvas.config(
            scrollregion=audio_file_canvas.bbox("all"),
            width=audio_file_frame.winfo_reqwidth(),
        )

        def audio_file_canvas_on_mousewheel(event):
            try:
                audio_file_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception as e:
                error_info = traceback.format_exc()
                print(error_info)
                messagebox.showinfo("error", error_info)

        audio_file_canvas.bind_all("<MouseWheel>", audio_file_canvas_on_mousewheel)

        # 模型训练容器
        model_training_frame = tk.Frame(left_frame)
        model_training_frame.pack(fill=tk.BOTH)

        # 模型训练
        model_training_button = tk.Button(
            model_training_frame, command=on_model_training_button_click
        )
        model_training_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型训练结果
        model_training_Lable = tk.Label(model_training_frame)
        model_training_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 音量阈值容器
        volume_threshold_frame = tk.Frame(left_frame)
        volume_threshold_frame.pack(fill=tk.BOTH)

        # 音量阈值
        volume_threshold_entry = tk.Entry(volume_threshold_frame, width=5)
        volume_threshold_entry.pack(side=tk.LEFT, padx=5, pady=1)

        # 音量阈值设置
        volume_threshold_set_button = tk.Button(
            volume_threshold_frame, command=on_volume_threshold_set_button_click
        )
        volume_threshold_set_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 监听声音音量
        volume_energy_Lable = tk.Label(volume_threshold_frame)
        volume_energy_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型测试容器
        model_test_frame = tk.Frame(left_frame)
        model_test_frame.pack(fill=tk.BOTH)

        # 模型测试
        model_test_button = tk.Button(
            model_test_frame, command=on_model_test_button_click
        )
        model_test_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型测试结果
        model_test_Lable = tk.Label(model_test_frame)
        model_test_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 按键绑定添加
        bind_key_add_button = tk.Button(
            center_frame, command=on_bind_key_add_button_click
        )
        bind_key_add_button.pack(fill=tk.BOTH, side=tk.TOP)

        # 按键绑定多个模块容器
        bind_key_modules_scrollbar_frame = tk.Frame(center_frame)
        bind_key_modules_scrollbar_frame.pack(fill=tk.BOTH)

        bind_key_modules_scrollbar = tk.Scrollbar(bind_key_modules_scrollbar_frame)
        bind_key_modules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bind_key_modules_canvas = tk.Canvas(
            bind_key_modules_scrollbar_frame,
            yscrollcommand=bind_key_modules_scrollbar.set,
            height=100,
        )
        bind_key_modules_canvas.pack(fill=tk.BOTH)
        bind_key_modules_scrollbar.config(command=bind_key_modules_canvas.yview)

        bind_key_modules_frame = tk.Frame(bind_key_modules_canvas)
        bind_key_modules_canvas.create_window(
            (0, 0), window=bind_key_modules_frame, anchor="nw"
        )

        bind_key_modules_canvas.config(scrollregion=bind_key_modules_canvas.bbox("all"))

        def bind_key_modules_canvas_on_mousewheel(event):
            try:
                bind_key_modules_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )
            except Exception as e:
                error_info = traceback.format_exc()
                print(error_info)
                messagebox.showinfo("error", error_info)

        bind_key_modules_canvas.bind_all(
            "<MouseWheel>", bind_key_modules_canvas_on_mousewheel
        )

        # 开始运行
        start_running_button = tk.Button(
            center_frame, command=on_start_running_button_click
        )
        start_running_button.pack(fill=tk.BOTH, side=tk.TOP)

        language_combo.set(configuration_json["language"])
        if configuration_json["now_configuration"] != "" and os.path.exists(
            f"configuration/{configuration_json['now_configuration']}"
        ):
            configuration_combo.set(configuration_json["now_configuration"])
        elif configuration_json["now_configuration"] != "":
            configuration_json["now_configuration"] = ""

        # 绑定关闭事件
        window.protocol("WM_DELETE_WINDOW", delete_window)

        # 导入model_training
        import_model_training_thread = threading.Thread(target=import_model_training)
        import_model_training_thread.start()

        window.mainloop()

except Exception as e:
    error_info = traceback.format_exc()
    print(error_info)
    messagebox.showinfo("error", error_info)
