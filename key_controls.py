from pynput.keyboard import Key, Listener as KeyboardListener,Controller as KeyboardController
from pynput.mouse import Button, Listener as MouseListener,Controller as MouseController
import queue
import threading
import time

bind_key_thread_stop_flag = threading.Event()
key_queue = queue.Queue()

# 键盘监听器
def on_keyboard_press(key):
    if not bind_key_thread_stop_flag.is_set():
        key_queue.put(key)

# 鼠标监听器
def on_mouse_click(x, y, button, pressed):
    if not bind_key_thread_stop_flag.is_set() and pressed:
        key_queue.put(button)
def on_scroll(x, y, dx, dy):
    if not bind_key_thread_stop_flag.is_set():
        key_queue.put(f"Scroll.{dy}")

def key_listener():
    # 创建键盘监听器
    keyboard_listener = KeyboardListener(on_press=on_keyboard_press)
    keyboard_listener.start()

    # 创建鼠标监听器
    mouse_listener = MouseListener(on_click=on_mouse_click, on_scroll=on_scroll)
    mouse_listener.start()

    while True:
        if bind_key_thread_stop_flag.is_set():
            keyboard_listener.stop()
            mouse_listener.stop()
            break
        time.sleep(0.001)

    # 等待所有监听器结束
    # keyboard_listener.join()
    # mouse_listener.join()

# 创建键盘控制器
keyboard = KeyboardController()
# 创建鼠标控制器
mouse = MouseController()

def key_controller(keys):
    for key in keys:
        if key.startswith("Scroll."):
            mouse.scroll(0, int(key.split(".")[1]))
        elif key.startswith("Button."):
            exec(f"mouse.click({key}, 1)")
        else:
            exec(f"keyboard.press({key})")
            exec(f"keyboard.release({key})")