import tkinter as tk
from tkinter import ttk
import json
import os
from tkinter import messagebox
import shutil
import threading
from natsort import natsorted
from playsound import playsound
import time


from audio_acquisition import audio_acquisition
from audio_acquisition import acquisition_audio_name_queue
from model_training import model_training

# 窗口大小改变
def window_on_resize(event):
    configuration_json["window_width"] = event.width
    configuration_json["window_height"] = event.height

# 窗口居中
def center_window(window, width, height):
    # 获取屏幕宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算窗口左上角的位置坐标
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口的位置
    window.geometry(f"{width}x{height}+{x}+{y}")

# 退出窗口
def delete_window():
    answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
    if answer == 'yes':
        audio_acquisition_thread_stop_flag.set()
        with open("configuration.json", 'w', encoding='utf-8') as file:
            json.dump(configuration_json, file, ensure_ascii=False, indent=4)
        window.destroy()

# 语言选择
def on_language_combobox_change(*args):
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

    audio_file_pack()

# 配置选择
def on_configuration_combobox_change(*args):
    # 停止声音采集
    on_audio_acquisition_stop_button_click()

    selected_value = configuration_combo_var.get()
    configuration_json["now_configuration"] = selected_value
    configuration_name_entry.delete(0, tk.END)
    configuration_name_entry.insert(0, configuration_json["now_configuration"])

    # 更新声音选择
    audio_name_entry.delete(0, tk.END)
    update_audio_combobox()

# 更新配置选择
def update_configuration_combobox(configuration_name):
    configuration_combo_values = os.listdir(f"configuration")
    configuration_combo["values"] = configuration_combo_values
    configuration_combo_var.set(configuration_name)

# 添加配置
def on_configuration_add_button_click():
    configuration_name = configuration_name_entry.get()
    if not os.path.exists("configuration/"+configuration_name) and configuration_name != "":
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

# 修改配置
def on_configuration_update_button_click():
    configuration_name = configuration_name_entry.get()
    # 配置名称没改变
    if configuration_combo_var.get() == configuration_name and configuration_name != "" and configuration_combo["values"] != "":
        messagebox.showinfo(text_json["tips"], text_json["success"])
    # 配置名称改变
    elif not os.path.exists("configuration/"+configuration_name) and configuration_name != "" and configuration_combo["values"] != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.rename(f"configuration/{configuration_combo_var.get()}", f"configuration/{configuration_name}")

            # 更新配置选择
            update_configuration_combobox(configuration_name)

            messagebox.showinfo(text_json["tips"], text_json["success"])
    elif configuration_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
    elif configuration_name == "":
        messagebox.showinfo(text_json["tips"], text_json["configuration_name_cannot_be_empty"])
    else:
        messagebox.showinfo(text_json["tips"], text_json["configuration_name_already_exists"])

# 删除配置
def on_configuration_delete_button_click():
    if configuration_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
    else:
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            shutil.rmtree(f"configuration/{configuration_combo_var.get()}")
            configuration_combo_var.set("")

            # 更新配置选择
            update_configuration_combobox("")

            messagebox.showinfo(text_json["tips"], text_json["success"])

# 声音选择
def on_audio_combobox_change(*args):
    # 停止声音采集
    on_audio_acquisition_stop_button_click()

    selected_value = audio_combo_var.get()
    audio_name_entry.delete(0, tk.END)
    audio_name_entry.insert(0, selected_value)
    audio_file_pack()
    

# 声音文件
def audio_file_pack(update = False):
    if not update:
        for widget in audio_file_frame.winfo_children():
            widget.destroy()
    if audio_combo_var.get() != "":
        audio_dirs = natsorted(os.listdir(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}"))
        if update:
            audio_dirs = [audio_dirs[len(audio_dirs)-1]]
        for item in audio_dirs:
            audio_file_row_frame = tk.Frame(audio_file_frame)
            audio_file_row_frame.pack(side=tk.BOTTOM)
            label = tk.Label(audio_file_row_frame, text=item)
            label.pack(side=tk.LEFT, padx=5, pady=1)
            file_path=f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}/{item}"
            # 播放声音文件
            button = tk.Button(audio_file_row_frame, text=text_json["play"], command=lambda file_path=file_path: playsound(file_path))
            button.pack(side=tk.LEFT, padx=5, pady=1)
            # 删除声音文件
            button = tk.Button(audio_file_row_frame, text=text_json["delete"], command=lambda file_path=file_path: on_audio_file_delete_button_click(file_path))
            button.pack(side=tk.LEFT, padx=5, pady=1)
            
    # 更新滚动区域
    if audio_file_frame.winfo_children():
        audio_file_frame.update_idletasks()
        audio_file_canvas.config(scrollregion=audio_file_canvas.bbox('all'),width=audio_file_frame.winfo_reqwidth())
        audio_file_canvas.yview_moveto(0.0)

# 删除声音文件
def on_audio_file_delete_button_click(file_path):
    answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
    if answer == 'yes':
        os.remove(file_path)
        audio_file_pack()

# 更新声音选择
def update_audio_combobox():
    audio_combo_values = []
    if configuration_combo_var.get() != "":
        audio_combo_values = os.listdir(f"configuration/{configuration_combo_var.get()}/audio")
    audio_combo["values"] = audio_combo_values
    audio_combo_var.set(audio_name_entry.get())

# 添加声音
def on_audio_add_button_click():
    audio_name = audio_name_entry.get()
    if configuration_combo_var.get() == "":
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

# 修改声音
def on_audio_update_button_click():
    audio_name = audio_name_entry.get()
    if configuration_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["configuration_now_cannot_be_empty"])
    # 声音名称没改变
    elif audio_combo_var.get() == audio_name and audio_name != "" and audio_combo["values"] != "":
        messagebox.showinfo(text_json["tips"], text_json["success"])
    # 声音名称改变
    elif not os.path.exists(f"configuration/{configuration_combo_var.get()}/audio/{audio_name}") and audio_name != "" and audio_combo["values"] != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.rename(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}", f"configuration/{configuration_combo_var.get()}/audio/{audio_name}")

            # 更新声音选择
            update_audio_combobox()
            
            messagebox.showinfo(text_json["tips"], text_json["success"])
    elif audio_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
    elif audio_name == "":
        messagebox.showinfo(text_json["tips"], text_json["audio_name_cannot_be_empty"])
    else:
        messagebox.showinfo(text_json["tips"], text_json["audio_name_already_exists"])

# 删除声音
def on_audio_delete_button_click():
    if audio_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
    else:
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            shutil.rmtree(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}")
            audio_combo_var.set("")

            # 更新声音选择
            update_audio_combobox()

            messagebox.showinfo(text_json["tips"], text_json["success"])

# 声音采集
audio_acquisition_thread_stop_flag = threading.Event()
audio_acquisition_thread_stop_flag.set()
audio_acquisition_thread_save_flag = threading.Event()
def on_audio_acquisition_button_click():
    if audio_combo_var.get() == "":
        messagebox.showinfo(text_json["tips"], text_json["audio_now_cannot_be_empty"])
    elif audio_acquisition_thread_stop_flag.is_set():
        audio_acquisition_thread_stop_flag.clear()
        audio_acquisition_thread_save_flag.clear()
        audio_acquisition_thread = threading.Thread(target=audio_acquisition, args=(False,f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}",audio_acquisition_thread_stop_flag,audio_acquisition_thread_save_flag))
        audio_acquisition_thread.start()
        audio_acquisition_button.config(bg='red')

        def save_flag():
            while not audio_acquisition_thread_stop_flag.is_set():
                if audio_acquisition_thread_save_flag.is_set():
                    audio_acquisition_thread_save_flag.clear()
                    audio_file_pack(update = True)
        save_flag_thread = threading.Thread(target=save_flag)
        save_flag_thread.start()
    else:
        messagebox.showinfo(text_json["tips"], text_json["audio_acquisition_listening"])

# 声音采集停止
def on_audio_acquisition_stop_button_click():
    audio_acquisition_thread_stop_flag.set()
    audio_acquisition_button.config(bg='SystemButtonFace')
    model_test_button.config(bg='SystemButtonFace')

# 模型训练
def on_model_training_button_click():
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
        model_training(audio_json,f"configuration/{configuration_combo_var.get()}")

# 模型测试
def on_model_test_button_click():
    audio_acquisition_thread_stop_flag.clear()
    audio_acquisition_thread_save_flag.clear()
    audio_acquisition_thread = threading.Thread(target=audio_acquisition, args=(True,f"configuration/{configuration_combo_var.get()}",audio_acquisition_thread_stop_flag,audio_acquisition_thread_save_flag))
    audio_acquisition_thread.start()
    model_test_button.config(bg='red')

    def save_flag():
        while not audio_acquisition_thread_stop_flag.is_set():
            if audio_acquisition_thread_save_flag.is_set():
                audio_acquisition_thread_save_flag.clear()
                print(acquisition_audio_name_queue.get(timeout=1))
            time.sleep(0.001)
    save_flag_thread = threading.Thread(target=save_flag)
    save_flag_thread.start()

with open("configuration.json", 'r', encoding='utf-8') as file:
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

audio_file_canvas = tk.Canvas(audio_file_scrollbar_frame, yscrollcommand=audio_file_scrollbar.set,height=200)
audio_file_canvas.pack()
audio_file_scrollbar.config(command=audio_file_canvas.yview)

audio_file_frame = tk.Frame(audio_file_canvas)
audio_file_canvas.create_window((0, 0), window=audio_file_frame, anchor='nw')

audio_file_canvas.config(scrollregion=audio_file_canvas.bbox('all'),width=audio_file_frame.winfo_reqwidth())

def audio_file_canvas_on_mousewheel(event):
    audio_file_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
audio_file_canvas.bind_all("<MouseWheel>", audio_file_canvas_on_mousewheel)

# 模型训练
model_training_button = tk.Button(left_frame, command=on_model_training_button_click)
model_training_button.pack()

# 模型测试
model_test_button = tk.Button(left_frame, text="测试模型", command=on_model_test_button_click)
model_test_button.pack()

# button = tk.Button(window, text="绑定按键", command=on_button_click)
# button.pack()

# button = tk.Button(window, text="运行启动", command=on_button_click)
# button.pack()

language_combo.set(configuration_json["language"])
if configuration_json['now_configuration'] != "" and os.path.exists(f"configuration/{configuration_json['now_configuration']}"):
    configuration_combo.set(configuration_json["now_configuration"])
elif configuration_json['now_configuration'] != "":
    configuration_json["now_configuration"] = ""


# 绑定关闭事件
window.protocol("WM_DELETE_WINDOW", delete_window)
window.bind("<Configure>", window_on_resize)

window.mainloop()