import threading
import tkinter as tk
from tkinter import font as tkFont
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER, windll
from comtypes import CLSCTX_ALL
import pythoncom
import keyboard
from tkinter import Scrollbar, Canvas
from tkinter import Tk
from screeninfo import get_monitors
import time
from datetime import datetime

# 初始化音量控制接口
pythoncom.CoInitialize()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 更新音量显示的函数
def update_label():
    while True:
        currentDateAndTime = datetime.now()
        time_label.config(text=f"現在時間: {currentDateAndTime.strftime('%Y/%m/%d %H:%M:%S')}")

        if volume.GetMute():
            current_volume = "靜音"
        else:
            current_volume = f"{volume.GetMasterVolumeLevelScalar() * 100:.0f}%"
        volume_label.config(text=f"音量: {current_volume}")
    
# 定义按钮功能
def volume_up():
    volume.SetMasterVolumeLevelScalar(min(volume.GetMasterVolumeLevelScalar() + 0.05, 1), None)
    #update_volume_label()

def volume_down():
    volume.SetMasterVolumeLevelScalar(max(volume.GetMasterVolumeLevelScalar() - 0.05, 0), None)
    #update_volume_label()

def lock_screen():
    windll.user32.LockWorkStation()

def mute_volume():
    """切换静音状态"""
    current_mute = volume.GetMute()
    volume.SetMute(not current_mute, None)

def toggle_play_pause():
    pyautogui.press('playpause')

def previous_track():
    keyboard.send('previous track')

def next_track():
    keyboard.send('next track')

def open_action_center():
    pyautogui.hotkey('win', 'a')

def open_task_manager():
    pyautogui.hotkey('ctrl', 'shift', 'esc')

# 创建Tkinter窗口
window = tk.Tk()
window.title("Touch Panel")

# 设置字体大小
btn_font = tkFont.Font(family='Helvetica', size=24, weight='bold')
btn_bg_color = 'light grey'

# 音量显示
volume_label = tk.Label(window, text="音量: 0%", font=btn_font, bg='light blue')
time_label = tk.Label(window, text="現在時間", font=btn_font, bg='light blue')
volume_label.pack(fill=tk.X)
time_label.pack(fill=tk.X)
label_thread = threading.Thread(target=update_label)
label_thread.daemon
label_thread.start()

# 创建滚动条和Canvas
scrollbar = Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas = Canvas(window, yscrollcommand=scrollbar.set, bg='sky blue')
canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
scrollbar.config(command=canvas.yview)

frame_inside_canvas = tk.Frame(canvas, bg='sky blue')
canvas.create_window((0,0), window=frame_inside_canvas, anchor='nw')

# 动态添加按钮并处理换行
buttons_info = [
    ("上一首", previous_track),
    ("播放/暫停", toggle_play_pause),
    ("下一首", next_track),
    ("音量+", volume_up),
    ("音量-", volume_down),
    ("鎖定螢幕", lock_screen),
    ("打開 Action Center", open_action_center),
    ("靜音/解除靜音", mute_volume),
    ("工作管理員", open_task_manager),
]

current_width_px = 0
max_width_px = 970
row_frame = tk.Frame(frame_inside_canvas, bg='sky blue')
row_frame.pack(fill=tk.X)

for text, command in buttons_info:
    button = tk.Button(row_frame, text=text, command=command, font=btn_font, bg='light grey')
    button.pack(side=tk.LEFT, padx=5, pady=10, ipadx=5, ipady=5)


    window.update_idletasks()  # 更新窗口以获取正确的宽度
    button_width = button.winfo_width()
    current_width_px += button_width + 20  # 加上间距的宽度

    if current_width_px >= max_width_px:
        current_width_px = button_width + 10
        row_frame = tk.Frame(frame_inside_canvas, bg='sky blue')
        row_frame.pack(fill=tk.X)
        button.pack_forget()  # 从旧的行中移除
        button.pack(side=tk.LEFT, padx=5, pady=10, ipadx=5, ipady=5)  # 在新行中重新打包

def onFrameConfigure(canvas):
    '''重置滚动区域以包含内部框架'''
    canvas.configure(scrollregion=canvas.bbox("all"))

frame_inside_canvas.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

def get_second_monitor():
    # 获取所有连接的显示器
    monitors = get_monitors()
    # 如果有多于一个显示器，则返回第二个显示器的信息
    if len(monitors) > 1:
        return monitors[1]
    # 如果只有一个显示器，返回None
    return None

def create_window_on_second_monitor():
    second_monitor = get_second_monitor()
    if second_monitor:
        # 创建Tkinter窗口
        # 设置窗口在第二个显示器上打开
        # 使用第二个显示器的位置和分辨率信息来定位窗口
        window.geometry(f'{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}')
        # 尝试最大化窗口，注意：这在所有系统和Tkinter版本上的表现可能不一致

        pyautogui.hotkey('win', 'up')
        
        window.mainloop()
    else:
        print("只有一个显示器连接，无法在第二个显示器上打开窗口。")

create_window_on_second_monitor()
# window.mainloop()
