import tkinter as tk
from tkinter import ttk
import json
import os
from tkinter import messagebox
import shutil

def center_window(window, width, height):
    # 获取屏幕宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算窗口左上角的位置坐标
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口的位置
    window.geometry(f"{width}x{height}+{x}+{y}")

# 配置json修改
def change_configuration_json(key,value):
    configuration_json[key] = value
    with open("configuration.json", 'w', encoding='utf-8') as file:
        json.dump(configuration_json, file, ensure_ascii=False, indent=4)

# 语言选择
def on_language_combobox_change(*args):
    selected_value = language_combo_var.get()
    change_configuration_json("language",selected_value)
    with open(f"language/{configuration_json["language"]}.json", 'r', encoding='utf-8') as file:
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

# 配置选择
def on_configuration_combobox_change(*args):
    selected_value = configuration_combo_var.get()
    change_configuration_json("now_configuration",selected_value)
    configuration_name_entry.delete(0, tk.END)
    configuration_name_entry.insert(0, configuration_json["now_configuration"])

# 更新配置选择
def update_configuration_combobox(configuration_name):
    configuration_combo_values = []
    for key in configuration_json["configuration"].keys():
        configuration_combo_values.append(key)
    configuration_combo["values"] = configuration_combo_values
    configuration_combo_var.set(configuration_name)

# 添加配置
def on_configuration_add_button_click():
    configuration_name = configuration_name_entry.get()
    if configuration_name not in configuration_json["configuration"].keys() and configuration_name != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.mkdir(f"configuration/{configuration_name}")
            os.mkdir(f"configuration/{configuration_name}/audio")
            configuration_json["configuration"][configuration_name] = {"audio":{}}
            change_configuration_json("configuration",configuration_json["configuration"])

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
        print()
    # 配置名称改变
    elif configuration_name not in configuration_json["configuration"].keys() and configuration_name != "" and configuration_combo["values"] != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.rename(f"configuration/{configuration_combo_var.get()}", f"configuration/{configuration_name}")
            configuration_json["configuration"][configuration_name] = {"audio":{}}
            configuration_json["configuration"].pop(configuration_combo_var.get())
            change_configuration_json("configuration",configuration_json["configuration"])

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
            configuration_json["configuration"].pop(configuration_combo_var.get())
            change_configuration_json("configuration",configuration_json["configuration"])
            configuration_combo_var.set("")

            # 更新配置选择
            update_configuration_combobox("")

            messagebox.showinfo(text_json["tips"], text_json["success"])

# 声音选择
def on_audio_combobox_change(*args):
    selected_value = audio_combo_var.get()
    audio_name_entry.delete(0, tk.END)
    audio_name_entry.insert(0, selected_value)

# 更新声音选择
def update_audio_combobox(audio_name):
    audio_combo_values = []
    for key in configuration_json["configuration"][configuration_combo_var.get()]["audio"].keys():
        audio_combo_values.append(key)
    audio_combo["values"] = audio_combo_values
    audio_combo_var.set(audio_name)

# 添加声音
def on_audio_add_button_click():
    audio_name = audio_name_entry.get()
    if audio_name not in configuration_json["configuration"][configuration_combo_var.get()].keys() and audio_name != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.mkdir(f"configuration/{configuration_combo_var.get()}/audio/{audio_name}")
            configuration_json["configuration"][configuration_combo_var.get()]["audio"][audio_name] = {}
            change_configuration_json("configuration",configuration_json["configuration"])

            # 更新声音选择
            update_audio_combobox(audio_name)

            messagebox.showinfo(text_json["tips"], text_json["success"])
    elif audio_name == "":
        messagebox.showinfo(text_json["tips"], text_json["audio_name_cannot_be_empty"])
    else:
        messagebox.showinfo(text_json["tips"], text_json["audio_name_already_exists"])

# 修改声音
def on_audio_update_button_click():
    audio_name = audio_name_entry.get()
    # 声音名称没改变
    if audio_combo_var.get() == audio_name and audio_name != "" and audio_combo["values"] != "":
        print()
    # 声音名称改变
    elif audio_name not in configuration_json["configuration"][configuration_combo_var.get()].keys() and audio_name != "" and audio_combo["values"] != "":
        answer = messagebox.askquestion(text_json["verify"], text_json["want_to_continue"])
        if answer == 'yes':
            os.rename(f"configuration/{configuration_combo_var.get()}/audio/{audio_combo_var.get()}", f"configuration/{configuration_combo_var.get()}/audio/{audio_name}")
            configuration_json["configuration"][configuration_combo_var.get()]["audio"][audio_name] = {}
            configuration_json["configuration"][configuration_combo_var.get()]["audio"].pop(audio_combo_var.get())
            change_configuration_json("configuration",configuration_json["configuration"])

            # 更新声音选择
            update_audio_combobox(audio_name)
            
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
            configuration_json["configuration"][configuration_combo_var.get()]["audio"].pop(audio_combo_var.get())
            change_configuration_json("configuration",configuration_json["configuration"])
            audio_combo_var.set("")

            # 更新声音选择
            update_audio_combobox("")

            messagebox.showinfo(text_json["tips"], text_json["success"])




with open("configuration.json", 'r', encoding='utf-8') as file:
    configuration_json = json.load(file)

with open(f"language/{configuration_json["language"]}.json", 'r', encoding='utf-8') as file:
    text_json = json.load(file)

window = tk.Tk()
# 设置窗口的初始大小
window_width = 500
window_height = 200
# 调用center_window函数使窗口居中
center_window(window, window_width, window_height)

# 语言选择
language_combo_values = []
language_dirs = os.listdir("language")
for item in language_dirs:
    language_combo_values.append(item.split('.')[0])
language_combo_var = tk.StringVar()
language_combo_var.trace_add('write', on_language_combobox_change)
language_combo = ttk.Combobox(window, textvariable=language_combo_var, values=language_combo_values, state='readonly')
language_combo.pack(pady=1)

# 配置选择
configuration_combo_values = []
for key in configuration_json["configuration"].keys():
    configuration_combo_values.append(key)
configuration_combo_var = tk.StringVar()
configuration_combo_var.trace_add('write', on_configuration_combobox_change)
configuration_combo = ttk.Combobox(window, textvariable=configuration_combo_var, values=configuration_combo_values, state='readonly')
configuration_combo.pack(pady=1)

# 配置名称
configuration_name_entry = tk.Entry(window)
configuration_name_entry.pack(pady=1)

# 配置容器
configuration_frame = tk.Frame(window)

# 添加配置
configuration_add_button = tk.Button(configuration_frame, command=on_configuration_add_button_click)
configuration_add_button.pack(side=tk.LEFT, padx=5, pady=1)

# 修改配置
configuration_update_button = tk.Button(configuration_frame, command=on_configuration_update_button_click)
configuration_update_button.pack(side=tk.LEFT, padx=5, pady=1)

# 删除配置
configuration_delete_button = tk.Button(configuration_frame, command=on_configuration_delete_button_click)
configuration_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

configuration_frame.pack()

# 声音选择
audio_combo_values = []
if configuration_json["now_configuration"] in configuration_json["configuration"]:
    for key in configuration_json["configuration"][configuration_json["now_configuration"]]["audio"].keys():
        audio_combo_values.append(key)
audio_combo_var = tk.StringVar()
audio_combo_var.trace_add('write', on_audio_combobox_change)
audio_combo = ttk.Combobox(window, textvariable=audio_combo_var, values=audio_combo_values, state='readonly')
audio_combo.pack(pady=1)

# 声音名称
audio_name_entry = tk.Entry(window)
audio_name_entry.pack(pady=1)

# 声音容器
audio_frame = tk.Frame(window)

# 添加声音
audio_add_button = tk.Button(audio_frame, command=on_audio_add_button_click)
audio_add_button.pack(side=tk.LEFT, padx=5, pady=1)

# 修改声音
audio_update_button = tk.Button(audio_frame, command=on_audio_update_button_click)
audio_update_button.pack(side=tk.LEFT, padx=5, pady=1)

# 删除声音
audio_delete_button = tk.Button(audio_frame, command=on_audio_delete_button_click)
audio_delete_button.pack(side=tk.LEFT, padx=5, pady=1)

audio_frame.pack()




# button = tk.Button(window, text="声音信息", command=on_button_click)
# button.pack()

# button = tk.Button(window, text="创建模型", command=on_button_click)
# button.pack()

# button = tk.Button(window, text="测试模型", command=on_button_click)
# button.pack()

# button = tk.Button(window, text="绑定按键", command=on_button_click)
# button.pack()

# button = tk.Button(window, text="运行启动", command=on_button_click)
# button.pack()

language_combo.set(configuration_json["language"])
configuration_combo.set(configuration_json["now_configuration"])
window.mainloop()