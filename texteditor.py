import tkinter as tk
from tkinter import messagebox, filedialog
import keyboard
import threading
import time
import os
import json
import win32gui
import win32con
import win32com

# 创建主窗口
root = tk.Tk()
root.title("快捷记事本")
root.geometry("400x300")

# 在创建主窗口后添加配置管理
CONFIG_FILE = "texteditor_config.json"

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"file_path": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

# 在Text组件之前添加文件路径框
path_frame = tk.Frame(root)
path_frame.pack(pady=5, fill=tk.X, padx=10)

path_label = tk.Label(path_frame, text="文件路径：")
path_label.pack(side=tk.LEFT)

path_entry = tk.Entry(path_frame)
path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

def browse_file():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
    )
    if file_path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, file_path)
        save_config({"file_path": file_path})
        load_file_content()

browse_button = tk.Button(path_frame, text="浏览", command=browse_file)
browse_button.pack(side=tk.LEFT, padx=5)

# 添加最小化到系统托盘的功能
def hide_window():
    root.withdraw()

def show_window():
    # 获取窗口句柄
    hwnd = win32gui.GetParent(root.winfo_id())
    
    # 如果窗口最小化，恢复它
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    
    try:
        # 将窗口移到前台
        win32gui.BringWindowToTop(hwnd)
        # 激活窗口
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"激活窗口出错：{str(e)}")
    
    # 确保窗口可见和正常状态
    root.deiconify()
    root.state('normal')
    root.lift()
    root.focus_force()
    root.update()

# 创建一个标志来控制快捷键监听线程
running = True

# 快捷键监听函数
def hotkey_listener():
    while running:
        if keyboard.is_pressed('shift+alt+e'):
            root.after(0, show_window)  # 使用after方法在主线程中执行
            time.sleep(0.3)  # 防止重复触发
        time.sleep(0.1)  # 减少CPU使用率

# 启动快捷键监听线程
listener_thread = threading.Thread(target=hotkey_listener, daemon=True)
listener_thread.start()

# 创建标签
label = tk.Label(root, text="现在发生了什么？")
label.pack(pady=10)

# Text组件
text_box = tk.Text(root, width=40, height=10)
text_box.pack(pady=5)

# 文件内容同步功能
def save_to_file(*args):
    file_path = path_entry.get()
    if file_path:
        try:
            content = text_box.get("1.0", tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("保存错误", f"保存文件时出错：{str(e)}")

def load_file_content():
    file_path = path_entry.get()
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_box.delete("1.0", tk.END)
                text_box.insert("1.0", content)
                text_box.edit_modified(False)  # 重置修改标志
        except Exception as e:
            messagebox.showerror("读取错误", f"读取文件时出错：{str(e)}")

# 刷新功能：从硬盘重新载入文件
def refresh_file():
    file_path = path_entry.get()
    if not file_path:
        messagebox.showwarning("刷新", "请先选择文件路径")
        return
    
    if not os.path.exists(file_path):
        messagebox.showerror("刷新错误", f"文件不存在：{file_path}")
        return
    
    # 检查是否有未保存的更改
    if text_box.edit_modified():
        result = messagebox.askyesnocancel(
            "未保存的更改",
            "当前内容有未保存的更改，刷新将丢失这些更改。\n是否先保存？"
        )
        if result is None:  # 取消
            return
        elif result:  # 是，先保存
            save_to_file()
    
    # 从硬盘重新载入文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            text_box.delete("1.0", tk.END)
            text_box.insert("1.0", content)
            text_box.edit_modified(False)  # 重置修改标志
            # 不显示成功提示，静默刷新
    except Exception as e:
        messagebox.showerror("刷新错误", f"读取文件时出错：{str(e)}")

# 加载配置
config = load_config()
if config["file_path"]:
    path_entry.insert(0, config["file_path"])
    load_file_content()

# 绑定文本变化事件
def on_text_change(event=None):
    if text_box.edit_modified():
        save_to_file()
        text_box.edit_modified(False)
    return "break"

text_box.bind("<<Modified>>", on_text_change)
path_entry.bind('<Return>', lambda e: load_file_content())

# 按钮点击事件
def show_message():
    user_input = text_box.get("1.0", tk.END)
    
    # 创建自定义对话框
    dialog = tk.Toplevel(root)
    dialog.title("您输入的内容")
    
    # 获取屏幕尺寸
    screen_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()
    # 使用完整屏幕尺寸
    max_height = screen_height
    max_width = screen_width
    
    # 创建Frame容器
    frame = tk.Frame(dialog)
    frame.pack(expand=True, fill='both', padx=10, pady=10)
    
    # 创建文本框和滚动条
    display_text = tk.Text(frame, wrap=tk.WORD, width=60, height=20)
    scrollbar = tk.Scrollbar(frame, command=display_text.yview)
    display_text.configure(yscrollcommand=scrollbar.set)
    
    # 放置文本框和滚动条
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    display_text.pack(side=tk.LEFT, expand=True, fill='both')
    
    # 插入内容
    display_text.insert("1.0", user_input)
    # 设置为只读
    display_text.configure(state='disabled')
    
    # 添加确定按钮
    ok_button = tk.Button(dialog, text="确定", command=dialog.destroy)
    ok_button.pack(pady=5)
    
    # 设置为全屏大小
    dialog_width = max_width
    dialog_height = max_height
    
    # 位置设置为屏幕左上角
    x = 0
    y = 0
    
    # 设置窗口大小和位置
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # 设置模态
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

# 退出函数
def quit_app():
    if messagebox.askokcancel("退出", "确定要完全退出程序吗？"):
        save_to_file()  # 退出前保存
        global running
        running = False
        root.destroy()

# 创建按钮框来容纳两个按钮
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# 修改原有按钮的父容器为button_frame
button = tk.Button(button_frame, text="显示内容", command=show_message)
button.pack(side=tk.LEFT, padx=5)

# 添加退出按钮
quit_button = tk.Button(button_frame, text="退出程序", command=quit_app, fg='red')
quit_button.pack(side=tk.LEFT, padx=5)

# 绑定窗口关闭事件为最小化
root.protocol('WM_DELETE_WINDOW', hide_window)

# 初始隐藏窗口
# root.withdraw()

# 在show_window函数后添加
def bind_shortcuts():
    # 绑定ESC键到hide_window函数
    root.bind('<Escape>', lambda e: hide_window())
    # 添加Ctrl+S保存快捷键
    root.bind('<Control-s>', lambda e: save_to_file())
    # 同时也为文本框绑定，确保在输入时也能响应快捷键
    text_box.bind('<Control-s>', lambda e: save_to_file())
    # 添加Ctrl+R刷新快捷键（只在文本框绑定，避免重复触发）
    def refresh_handler(e):
        refresh_file()
        return "break"  # 阻止事件继续传播
    text_box.bind('<Control-r>', refresh_handler)
    root.bind('<Control-r>', refresh_handler)

# 在创建主窗口后调用绑定函数
root.title("简单桌面记事本")
root.geometry("400x300")
bind_shortcuts()  # 添加这一行

# 在path_frame中添加保存和刷新按钮
update_button = tk.Button(path_frame, text="保存", command=save_to_file)  # 直接使用函数名
update_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(path_frame, text="刷新", command=refresh_file)
refresh_button.pack(side=tk.LEFT, padx=5)

# 启动主事件循环
root.mainloop()
