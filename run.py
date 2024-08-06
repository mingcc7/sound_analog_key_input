import tkinter as tk
from tkinter import ttk
import json
import os
from tkinter import messagebox

class Sound_analog_key_input_window:
    def clear_window(window):
        for widget in window.winfo_children():
            widget.pack_forget()

    def create_window():
        def on_button_click():
            print("Button clicked!")

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

            window.title(text_json["title"])
            configuration_add_button['text'] = text_json["configuration_add"]

        # 配置选择
        def on_configuration_combobox_change(*args):
            selected_value = configuration_combo_var.get()
            change_configuration_json("now_configuration",selected_value)
            configuration_name_entry.delete(0, tk.END)
            configuration_name_entry.insert(0, configuration_json["now_configuration"])

        # 添加配置
        def on_configuration_add_button_click():
            configuration_name = configuration_name_entry.get()
            if configuration_name not in configuration_json["configuration"].keys():
                configuration_json["configuration"][configuration_name] = {}
                change_configuration_json("configuration",configuration_json["configuration"])
            else:
                messagebox.showinfo(text_json["tips"], text_json["configuration_name_already_exists"])

        with open("configuration.json", 'r', encoding='utf-8') as file:
            configuration_json = json.load(file)

        with open(f"language/{configuration_json["language"]}.json", 'r', encoding='utf-8') as file:
            text_json = json.load(file)

        window = tk.Tk()
        window.geometry("300x200")

        # 语言选择
        language_combo_values = []
        language_dirs = os.listdir("language")
        for item in language_dirs:
            language_combo_values.append(item.split('.')[0])
        language_combo_var = tk.StringVar()
        language_combo_var.trace_add('write', on_language_combobox_change)
        language_combo = ttk.Combobox(window, textvariable=language_combo_var, values=language_combo_values, state='readonly')
        
        language_combo.pack()

        # 配置选择
        configuration_combo_values = []
        for key in configuration_json["configuration"].keys():
            configuration_combo_values.append(key)
        configuration_combo_var = tk.StringVar()
        configuration_combo_var.trace_add('write', on_configuration_combobox_change)
        configuration_combo = ttk.Combobox(window, textvariable=configuration_combo_var, values=configuration_combo_values, state='readonly')
        configuration_combo.pack()

        # 配置名称
        configuration_name_entry = tk.Entry(window)
        configuration_name_entry.pack()

        # 添加配置
        configuration_add_button = tk.Button(window, command=on_configuration_add_button_click)
        configuration_add_button.pack()

        button = tk.Button(window, text="修改配置", command=on_button_click)
        button.pack()

        button = tk.Button(window, text="声音信息", command=on_button_click)
        button.pack()

        button = tk.Button(window, text="创建模型", command=on_button_click)
        button.pack()

        button = tk.Button(window, text="测试模型", command=on_button_click)
        button.pack()

        button = tk.Button(window, text="绑定按键", command=on_button_click)
        button.pack()

        button = tk.Button(window, text="运行启动", command=on_button_click)
        button.pack()

        language_combo.set(configuration_json["language"])
        configuration_combo.set(configuration_json["now_configuration"])
        window.mainloop()

Sound_analog_key_input_window.create_window()