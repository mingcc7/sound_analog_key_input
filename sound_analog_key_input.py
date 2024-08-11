try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import json
    import os
    import shutil
    import threading
    from natsort import natsorted
    from playsound import playsound
    import time
    import queue

   
    # 线程导入需要keras的模块，keras加载慢
    audio_acquisition = None
    acquisition_audio_name_queue = None
    model_training = None
    model_training_queue = None
    import_audio_model_success = False
    def import_audio_model():
        try:
            print("import audio model loading")
            global audio_acquisition
            from audio_acquisition import audio_acquisition
            global acquisition_audio_name_queue
            from audio_acquisition import acquisition_audio_name_queue
            global model_training
            from model_training import model_training
            global model_training_queue
            from model_training import model_training_queue
            global import_audio_model_success
            import_audio_model_success = True
            print("import audio model success")
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)
    import_audio_model_thread = threading.Thread(target=import_audio_model)
    import_audio_model_thread.start()


    from key_controls import key_listener
    from key_controls import bind_key_thread_stop_flag
    from key_controls import key_queue
    from key_controls import key_controller

    configuration_json_path = 'configuration.json'

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
            print(e)
            messagebox.showinfo("error", e)

    # 退出窗口
    def delete_window():
        try:
            answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
            if answer == 'yes':
                audio_acquisition_thread_stop_flag.set()
                model_test_thread_stop_flag.set()
                configuration_json["window_width"] = window.winfo_width()
                configuration_json["window_height"] = window.winfo_height()
                with open(configuration_json_path, 'w', encoding='utf-8') as file:
                    json.dump(configuration_json, file, ensure_ascii=False, indent=4)
                window.destroy()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 语言选择
    def on_language_combobox_change(*args):
        try:
            selected_value = language_combo_var.get()
            configuration_json["language"] = selected_value
            with open(f"language/{configuration_json['language']}.json", 'r', encoding='utf-8') as file:
                global text_json
                text_json = json.load(file)

            #初始化组件名称
            window.title(text_json["title"])
            configuration_add_button['text'] = text_json["configuration_add"]
            configuration_update_button['text'] = text_json["configuration_update"]
            configuration_delete_button['text'] = text_json["configuration_delete"]
            audio_add_button['text'] = text_json["audio_add"]
            audio_update_button['text'] = text_json["audio_update"]
            audio_delete_button['text'] = text_json["audio_delete"]
            audio_acquisition_button['text'] = text_json["audio_acquisition"]
            audio_acquisition_stop_button['text'] = text_json["audio_acquisition_stop"]
            model_training_button['text'] = text_json["model_training"]
            model_test_button['text'] = text_json["model_test"]
            bind_key_button['text'] = text_json["bind_key"]
            start_running_button['text'] = text_json["start_running"]

            audio_file_pack()
            model_training_Lable["text"] = ""
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 配置选择
    def on_configuration_combobox_change(*args):
        try:
            if not start_running_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                configuration_combo.set(configuration_json["now_configuration"])
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            else:
                # 停止声音采集
                on_audio_acquisition_stop_button_click()

                selected_value = configuration_combo_var.get()
                configuration_json["now_configuration"] = selected_value
                configuration_name_entry.delete(0, tk.END)
                configuration_name_entry.insert(0, configuration_json["now_configuration"])

                # 更新声音选择
                audio_name_entry.delete(0, tk.END)
                update_audio_combobox()

                model_training_Lable["text"] = ""
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 更新配置选择
    def update_configuration_combobox(configuration_name):
        try:
            configuration_combo_values = os.listdir(f"configuration")
            configuration_combo["values"] = configuration_combo_values
            configuration_combo_var.set(configuration_name)
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 添加配置
    def on_configuration_add_button_click():
        try:
            configuration_name = configuration_name_entry.get()
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif not os.path.exists("configuration/"+configuration_name) and configuration_name != "":
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    if not os.path.exists("configuration"):
                        os.mkdir(f"configuration")
                    try:
                        os.mkdir(f"configuration/{configuration_name}")
                    except FileExistsError:
                        print(f"configuration/{configuration_name} already exists")
                    try:
                        os.mkdir(f"configuration/{configuration_name}/audio")
                    except FileExistsError:
                        print(f"configuration/{configuration_name}/audio already exists")

                    # 更新配置选择
                    update_configuration_combobox(configuration_name)

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif configuration_name == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_name_cannot_be_empty"])
            else:
                messagebox.showinfo(text_json["tips"], text_json["configuration_name_already_exists"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)
    # 修改配置
    def on_configuration_update_button_click():
        try:
            configuration_name = configuration_name_entry.get()
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            # 配置名称没改变
            elif configuration_combo_var.get() == configuration_name and configuration_name != "" and configuration_combo["values"] != "":
                messagebox.showinfo(text_json["tips"], text_json["success"])
            # 配置名称改变
            elif not os.path.exists("configuration/"+configuration_name) and configuration_name != "" and configuration_combo["values"] != "":
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    os.rename(f"configuration/{configuration_combo_var.get()}", f"configuration/{configuration_name}")

                    if configuration_combo_var.get() in configuration_json["configuration_audio_key"]:
                        configuration_json["configuration_audio_key"][configuration_name] = configuration_json["configuration_audio_key"][configuration_combo_var.get()]
                        configuration_json["configuration_audio_key"].pop(configuration_combo_var.get())
                        with open(configuration_json_path, 'w', encoding='utf-8') as file:
                            json.dump(configuration_json, file, ensure_ascii=False, indent=4)

                    # 更新配置选择
                    update_configuration_combobox(configuration_name)

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            elif configuration_name == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_name_cannot_be_empty"])
            else:
                messagebox.showinfo(text_json["tips"], text_json["configuration_name_already_exists"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 删除配置
    def on_configuration_delete_button_click():
        try:
            if not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            else:
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    shutil.rmtree(f"configuration/{configuration_combo_var.get()}")

                    if configuration_combo_var.get() in configuration_json["configuration_audio_key"]:
                        configuration_json["configuration_audio_key"].pop(configuration_combo_var.get())
                        with open(configuration_json_path, 'w', encoding='utf-8') as file:
                            json.dump(configuration_json, file, ensure_ascii=False, indent=4)

                    configuration_combo_var.set("")

                    # 更新配置选择
                    update_configuration_combobox("")

                    messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 声音选择
    def on_audio_combobox_change(*args):
        try:
            # 停止声音采集
            on_audio_acquisition_stop_button_click()

            selected_value = audio_combo_var.get()
            audio_name_entry.delete(0, tk.END)
            audio_name_entry.insert(0, selected_value)
            audio_file_pack()

            if configuration_json["now_configuration"] in configuration_json["configuration_audio_key"] and audio_combo_var.get() in configuration_json["configuration_audio_key"][configuration_json["now_configuration"]]:
                bind_key_Lable["text"] = configuration_json["configuration_audio_key"][configuration_json["now_configuration"]][audio_combo_var.get()]
            else:
                bind_key_Lable["text"] = ""
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)
        

    # 声音文件
    def audio_file_pack(update = False):
        try:
            if not update:
                for widget in audio_file_frame.winfo_children():
                    widget.destroy()
            if audio_combo_var.get() != "":
                audio_dirs = natsorted(os.listdir(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}"))
                if update:
                    audio_dirs = [audio_dirs[len(audio_dirs)-1]]
                for item in audio_dirs:
                    audio_file_row_frame = tk.Frame(audio_file_frame)
                    audio_file_row_frame.pack(side=tk.BOTTOM,fill=tk.X)
                    label = tk.Label(audio_file_row_frame, text=item)
                    label.pack(side=tk.LEFT, padx=5, pady=1)
                    file_path=f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}/{item}"
                    # 删除声音文件
                    button = tk.Button(audio_file_row_frame, text=text_json["delete"], command=lambda file_path=file_path: on_audio_file_delete_button_click(file_path))
                    button.pack(side=tk.RIGHT, padx=5, pady=1)
                    # 播放声音文件
                    button = tk.Button(audio_file_row_frame, text=text_json["play"], command=lambda file_path=file_path: playsound(file_path))
                    button.pack(side=tk.RIGHT, padx=5, pady=1)
                    
            # 更新滚动区域
            if audio_file_frame.winfo_children():
                audio_file_frame.update_idletasks()
                audio_file_canvas.config(scrollregion=audio_file_canvas.bbox('all'),width=audio_file_frame.winfo_reqwidth())
                audio_file_canvas.yview_moveto(0.0)
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 删除声音文件
    def on_audio_file_delete_button_click(file_path):
        try:
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            else:
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    os.remove(file_path)
                    audio_file_pack()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 更新声音选择
    def update_audio_combobox():
        try:
            audio_combo_values = []
            if configuration_combo_var.get() != "":
                audio_combo_values = os.listdir(f"configuration/{configuration_combo_var.get()}/audio")
            audio_combo["values"] = audio_combo_values
            audio_combo_var.set(audio_name_entry.get())
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 添加声音
    def on_audio_add_button_click():
        try:
            audio_name = audio_name_entry.get()
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            elif not os.path.exists(f"configuration/{configuration_combo_var.get()}/audio/{audio_name}") and audio_name != "":
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    try:
                        os.mkdir(f"configuration/{configuration_combo_var.get()}/audio/{audio_name}")
                    except FileExistsError:
                        print(f"configuration/{configuration_combo_var.get()}/audio/{audio_name} already exists")

                    # 更新声音选择
                    update_audio_combobox()

                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif audio_name == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_name_cannot_be_empty"])
            else:
                messagebox.showinfo(text_json["tips"], text_json["audio_name_already_exists"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 修改声音
    def on_audio_update_button_click():
        try:
            audio_name = audio_name_entry.get()
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            # 声音名称没改变
            elif audio_combo_var.get() == audio_name and audio_name != "" and audio_combo["values"] != "":
                messagebox.showinfo(text_json["tips"], text_json["success"])
            # 声音名称改变
            elif not os.path.exists(f"configuration/{configuration_combo_var.get()}/audio/{audio_name}") and audio_name != "" and audio_combo["values"] != "":
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    os.rename(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}", f"configuration/{configuration_combo_var.get()}/audio/{audio_name}")
                    
                    if configuration_combo_var.get() in configuration_json["configuration_audio_key"] and audio_combo_var.get() in configuration_json["configuration_audio_key"][configuration_combo_var.get()]:
                        configuration_json["configuration_audio_key"][configuration_combo_var.get()][audio_name] = configuration_json["configuration_audio_key"][configuration_combo_var.get()][audio_combo_var.get()]
                        configuration_json["configuration_audio_key"][configuration_combo_var.get()].pop(audio_combo_var.get())
                        with open(configuration_json_path, 'w', encoding='utf-8') as file:
                            json.dump(configuration_json, file, ensure_ascii=False, indent=4)

                    # 更新声音选择
                    update_audio_combobox()
                    
                    messagebox.showinfo(text_json["tips"], text_json["success"])
            elif audio_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
            elif audio_name == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_name_cannot_be_empty"])
            else:
                messagebox.showinfo(text_json["tips"], text_json["audio_name_already_exists"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 删除声音
    def on_audio_delete_button_click():
        try:
            if not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif audio_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
            else:
                answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
                if answer == 'yes':
                    shutil.rmtree(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}")

                    if configuration_combo_var.get() in configuration_json["configuration_audio_key"] and audio_combo_var.get() in configuration_json["configuration_audio_key"][configuration_combo_var.get()]:
                        configuration_json["configuration_audio_key"][configuration_combo_var.get()].pop(audio_combo_var.get())
                        with open(configuration_json_path, 'w', encoding='utf-8') as file:
                            json.dump(configuration_json, file, ensure_ascii=False, indent=4)

                    audio_combo_var.set("")

                    # 更新声音选择
                    update_audio_combobox()

                    messagebox.showinfo(text_json["tips"], text_json["success"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 声音采集
    audio_acquisition_thread_stop_flag = threading.Event()
    audio_acquisition_thread_stop_flag.set()
    audio_acquisition_thread_save_flag = threading.Event()
    def on_audio_acquisition_button_click():
        try:
            if not import_audio_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif audio_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
            elif audio_acquisition_thread_stop_flag.is_set():
                audio_acquisition_thread_stop_flag.clear()
                audio_acquisition_thread_save_flag.clear()
                audio_acquisition_thread = threading.Thread(target=audio_acquisition, args=(False,f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}",audio_acquisition_thread_stop_flag,audio_acquisition_thread_save_flag))
                audio_acquisition_thread.start()
                audio_acquisition_button.config(bg='red')

                def save_flag():
                    try:
                        while not audio_acquisition_thread_stop_flag.is_set():
                            if audio_acquisition_thread_save_flag.is_set():
                                audio_acquisition_thread_save_flag.clear()
                                audio_file_pack(update = True)
                            time.sleep(0.001)
                    except Exception as e:
                        print(e)
                        messagebox.showinfo("error", e)
                save_flag_thread = threading.Thread(target=save_flag)
                save_flag_thread.start()
            else:
                messagebox.showinfo(text_json["tips"], text_json["audio_acquisition_listening"])
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 声音采集停止
    def on_audio_acquisition_stop_button_click():
        try:
            audio_acquisition_thread_stop_flag.set()
            audio_acquisition_button.config(bg='SystemButtonFace')
            model_test_thread_stop_flag.set()
            model_test_button.config(bg='SystemButtonFace')
            start_running_thread_stop_flag.set()
            start_running_button.config(bg='SystemButtonFace')
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 模型训练
    model_training_thread_stop_flag = threading.Event()
    model_training_thread_stop_flag.set()
    def on_model_training_button_click():
        try:
            if not import_audio_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            else:
                audio_dirs = os.listdir(f"configuration/{configuration_combo_var.get()}/audio")
                audio_json = {}
                count = 0
                for item in audio_dirs:
                    audio_json[item] = {}
                    audio_file_dirs = os.listdir(f"configuration/{configuration_combo_var.get()}/audio/{item}")
                    for file_item in audio_file_dirs:
                        audio_json[item][file_item] = {}
                        count += 1
                if count == 0:
                    messagebox.showinfo(text_json["tips"], text_json["audio_file_cannot_be_empty"])
                else:
                    model_training_thread_stop_flag.clear()
                    model_training_thread = threading.Thread(target=model_training, args=(audio_json,f"configuration/{configuration_combo_var.get()}",model_training_thread_stop_flag))
                    model_training_thread.start()
                    model_training_Lable["text"] = text_json["fit"]
                    model_training_button.config(bg='skyblue')

                    def queue_get():
                        try:
                            while not model_training_thread_stop_flag.is_set():
                                if not model_training_queue.empty():
                                    queue_get = model_training_queue.get(timeout=1)
                                    key = list(queue_get.keys())[0]
                                    values = list(queue_get.values())[0]
                                    if key == "type":
                                        model_training_Lable["text"] = f"{text_json['status']}:{text_json[values]}"
                                    elif key == "epoch":
                                        model_training_Lable["text"] = f"{text_json['schedule']}:{values}"
                                    elif key == "accuracy":
                                        model_training_Lable["text"] = f"{text_json['accuracy']}:{values}"
                                    # elif key == "loss":
                                        # model_training_Lable["text"] = f"{key}:{values}"
                                time.sleep(0.001)
                        
                            model_training_button.config(bg='SystemButtonFace')
                        except Exception as e:
                            print(e)
                            messagebox.showinfo("error", e)
                    save_flag_thread = threading.Thread(target=queue_get)
                    save_flag_thread.start()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 模型测试
    model_test_thread_stop_flag = threading.Event()
    model_test_thread_stop_flag.set()
    def on_model_test_button_click():
        try:
            if not import_audio_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            elif not os.path.exists(f"configuration/{configuration_combo_var.get()}/model.keras"):
                messagebox.showinfo(text_json["tips"], text_json["model_not_exist"])
            else:
                model_test_thread_stop_flag.clear()
                audio_acquisition_thread = threading.Thread(target=audio_acquisition, args=(True,f"configuration/{configuration_combo_var.get()}",model_test_thread_stop_flag,None))
                audio_acquisition_thread.start()
                model_test_button.config(bg='red')

                def get_name_queue():
                    try:
                        index = 1
                        while not model_test_thread_stop_flag.is_set():
                            if not acquisition_audio_name_queue.empty():
                                model_test_Lable["text"] = f"{index}:{acquisition_audio_name_queue.get(timeout=1)}"
                                index += 1
                            time.sleep(0.001)
                    except Exception as e:
                        print(e)
                        messagebox.showinfo("error", e)
                get_name_queue_thread = threading.Thread(target=get_name_queue)
                get_name_queue_thread.start()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 绑定按键
    bind_key_thread_stop_flag.set()
    def on_bind_key_button_click():
        try:
            if not bind_key_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["bind_key_in_progress"])
            elif audio_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
            else:
                bind_key_thread_stop_flag.clear()
                while not key_queue.empty():
                    try:
                        key_queue.get_nowait()
                    except queue.Empty:
                        break
                key_listener_thread = threading.Thread(target=key_listener)
                key_listener_thread.start()
                bind_key_button.config(bg='red')

                def queue_get():
                    try:
                        keys = []
                        stop = False
                        while not bind_key_thread_stop_flag.is_set():
                            while not key_queue.empty():
                                key = key_queue.get(timeout=1)
                                keys.append(f"{key}")
                                bind_key_Lable["text"] =keys
                                if configuration_json["now_configuration"] not in configuration_json["configuration_audio_key"]:
                                    configuration_json["configuration_audio_key"][configuration_json["now_configuration"]] = {}
                                configuration_json["configuration_audio_key"][configuration_json["now_configuration"]][audio_combo_var.get()] = keys
                                with open(configuration_json_path, 'w', encoding='utf-8') as file:
                                    json.dump(configuration_json, file, ensure_ascii=False, indent=4)
                                time.sleep(0.1)
                                stop = True
                            if stop:
                                bind_key_thread_stop_flag.set()

                            time.sleep(0.001)
                        bind_key_button.config(bg='SystemButtonFace')
                    except Exception as e:
                        print(e)
                        messagebox.showinfo("error", e)
                queue_get_thread = threading.Thread(target=queue_get)
                queue_get_thread.start()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)

    # 开始运行
    start_running_thread_stop_flag = threading.Event()
    start_running_thread_stop_flag.set()
    def on_start_running_button_click():
        try:
            if not import_audio_model_success:
                messagebox.showinfo(text_json["tips"], text_json["loading"])
            elif not start_running_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["is_running"])
            elif not model_test_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_test_in_progress"])
            elif not model_training_thread_stop_flag.is_set():
                messagebox.showinfo(text_json["tips"], text_json["model_training_in_progress"])
            elif configuration_combo_var.get() == "":
                messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
            elif not os.path.exists(f"configuration/{configuration_combo_var.get()}/model.keras"):
                messagebox.showinfo(text_json["tips"], text_json["model_not_exist"])
            else:
                start_running_thread_stop_flag.clear()
                start_running_thread = threading.Thread(target=audio_acquisition, args=(True,f"configuration/{configuration_combo_var.get()}",start_running_thread_stop_flag,None))
                start_running_thread.start()
                start_running_button.config(bg='red')

                def get_name_queue():
                    try:
                        while not start_running_thread_stop_flag.is_set():
                            if not acquisition_audio_name_queue.empty():
                                audio = acquisition_audio_name_queue.get(timeout=1)
                                key_controller(configuration_json["configuration_audio_key"][configuration_json["now_configuration"]][audio])
                            time.sleep(0.001)
                    except Exception as e:
                        print(e)
                        messagebox.showinfo("error", e)
                get_name_queue_thread = threading.Thread(target=get_name_queue)
                get_name_queue_thread.start()
        except Exception as e:
            print(e)
            messagebox.showinfo("error", e)
        
    if __name__ == '__main__':
        with open(configuration_json_path, 'r', encoding='utf-8') as file:
            configuration_json = json.load(file)

        with open(f"language/{configuration_json['language']}.json", 'r', encoding='utf-8') as file:
            text_json = json.load(file)

        window = tk.Tk()
        # 调用center_window函数使窗口居中
        center_window(window, configuration_json["window_width"], configuration_json["window_height"])

        # 居中容器
        center_frame = tk.Frame(window)
        center_frame.pack(expand=True)

        # 左侧容器
        left_frame = tk.Frame(center_frame)
        left_frame.pack(side=tk.LEFT,fill=tk.BOTH)

        # 语言选择
        language_combo_values = []
        language_dirs = os.listdir("language")
        for item in language_dirs:
            language_combo_values.append(item.split('.')[0])
        language_combo_var = tk.StringVar()
        language_combo_var.trace_add('write', on_language_combobox_change)
        language_combo = ttk.Combobox(left_frame, textvariable=language_combo_var, values=language_combo_values, state='readonly')
        language_combo.pack(pady=1,fill=tk.BOTH)

        # 配置选择
        if not os.path.exists("configuration"):
            os.mkdir("configuration")
        configuration_combo_values = os.listdir(f"configuration")
        configuration_combo_var = tk.StringVar()
        configuration_combo_var.trace_add('write', on_configuration_combobox_change)
        configuration_combo = ttk.Combobox(left_frame, textvariable=configuration_combo_var, values=configuration_combo_values, state='readonly')
        configuration_combo.pack(pady=1,fill=tk.BOTH)

        # 配置名称
        configuration_name_entry = tk.Entry(left_frame)
        configuration_name_entry.pack(pady=1,fill=tk.BOTH)

        # 配置容器
        configuration_frame = tk.Frame(left_frame)
        configuration_frame.pack(fill=tk.BOTH)

        # 添加配置
        configuration_add_button = tk.Button(configuration_frame, command=on_configuration_add_button_click)
        configuration_add_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 修改配置
        configuration_update_button = tk.Button(configuration_frame, command=on_configuration_update_button_click)
        configuration_update_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 删除配置
        configuration_delete_button = tk.Button(configuration_frame, command=on_configuration_delete_button_click)
        configuration_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音选择
        audio_combo_var = tk.StringVar()
        audio_combo_var.trace_add('write', on_audio_combobox_change)
        audio_combo = ttk.Combobox(left_frame, textvariable=audio_combo_var, state='readonly')
        audio_combo.pack(pady=1,fill=tk.BOTH)

        # 声音名称
        audio_name_entry = tk.Entry(left_frame)
        audio_name_entry.pack(pady=1,fill=tk.BOTH)

        # 声音容器
        audio_frame = tk.Frame(left_frame)
        audio_frame.pack(fill=tk.BOTH)

        # 添加声音
        audio_add_button = tk.Button(audio_frame, command=on_audio_add_button_click)
        audio_add_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 修改声音
        audio_update_button = tk.Button(audio_frame, command=on_audio_update_button_click)
        audio_update_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 删除声音
        audio_delete_button = tk.Button(audio_frame, command=on_audio_delete_button_click)
        audio_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 右侧容器
        right_frame = tk.Frame(center_frame)
        right_frame.pack(side=tk.LEFT,fill=tk.BOTH)

        # 声音采集容器
        audio_acquisition_frame = tk.Frame(right_frame)
        audio_acquisition_frame.pack()

        # 声音采集
        audio_acquisition_button = tk.Button(audio_acquisition_frame, command=on_audio_acquisition_button_click)
        audio_acquisition_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音采集停止
        audio_acquisition_stop_button = tk.Button(audio_acquisition_frame, command=on_audio_acquisition_stop_button_click)
        audio_acquisition_stop_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 声音文件容器
        audio_file_scrollbar_frame = tk.Frame(right_frame)
        audio_file_scrollbar_frame.pack(fill=tk.BOTH)

        audio_file_scrollbar = tk.Scrollbar(audio_file_scrollbar_frame)
        audio_file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        audio_file_canvas = tk.Canvas(audio_file_scrollbar_frame, yscrollcommand=audio_file_scrollbar.set,height=270)
        audio_file_canvas.pack()
        audio_file_scrollbar.config(command=audio_file_canvas.yview)

        audio_file_frame = tk.Frame(audio_file_canvas)
        audio_file_canvas.create_window((0, 0), window=audio_file_frame, anchor='nw')

        audio_file_canvas.config(scrollregion=audio_file_canvas.bbox('all'),width=audio_file_frame.winfo_reqwidth())

        def audio_file_canvas_on_mousewheel(event):
            try:
                audio_file_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                print(e)
                messagebox.showinfo("error", e)
        audio_file_canvas.bind_all("<MouseWheel>", audio_file_canvas_on_mousewheel)

        # 模型训练容器
        model_training_frame = tk.Frame(left_frame)
        model_training_frame.pack(fill=tk.BOTH)

        # 模型训练
        model_training_button = tk.Button(model_training_frame, command=on_model_training_button_click)
        model_training_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型训练结果
        model_training_Lable = tk.Label(model_training_frame)
        model_training_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型测试容器
        model_test_frame = tk.Frame(left_frame)
        model_test_frame.pack(fill=tk.BOTH)

        # 模型测试
        model_test_button = tk.Button(model_test_frame, command=on_model_test_button_click)
        model_test_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 模型测试结果
        model_test_Lable = tk.Label(model_test_frame)
        model_test_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 按键绑定容器
        bind_key_frame = tk.Frame(left_frame)
        bind_key_frame.pack(fill=tk.BOTH)

        # 按键绑定
        bind_key_button = tk.Button(bind_key_frame, command=on_bind_key_button_click)
        bind_key_button.pack(side=tk.LEFT, padx=5, pady=1)

        # 按键绑定结果
        bind_key_Lable = tk.Label(bind_key_frame)
        bind_key_Lable.pack(side=tk.LEFT, padx=5, pady=1)

        # 开始运行
        start_running_button = tk.Button(left_frame, command=on_start_running_button_click)
        start_running_button.pack(fill=tk.BOTH)


        language_combo.set(configuration_json["language"])
        if configuration_json['now_configuration'] != "" and os.path.exists(f"configuration/{configuration_json['now_configuration']}"):
            configuration_combo.set(configuration_json["now_configuration"])
        elif configuration_json['now_configuration'] != "":
            configuration_json["now_configuration"] = ""


        # 绑定关闭事件
        window.protocol("WM_DELETE_WINDOW", delete_window)

        window.mainloop()

except Exception as e:
    print(e)
    messagebox.showinfo("error", e)