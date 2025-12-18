#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文本编辑器命令行工具
用于快速添加带时间戳的随笔到配置文件中指定的文件
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径（与 texteditor.py 共享），使用脚本所在目录
CONFIG_FILE = os.path.join(SCRIPT_DIR, "texteditor_config.json")


def load_config():
    """加载配置文件"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取配置文件出错：{str(e)}")
    return {"file_path": ""}


def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置文件出错：{str(e)}")
        return False


def get_file_path():
    """获取配置文件中记录的文件路径"""
    config = load_config()
    file_path = config.get("file_path", "")
    if not file_path:
        print("错误：配置文件中没有设置文件路径")
        return None
    return file_path


def add_note(content_parts):
    """添加带时间戳的随笔到文件，支持标签（以#开头）
    
    Args:
        content_parts: 内容列表，可以是字符串（用空格分割）或列表
    """
    file_path = get_file_path()
    if not file_path:
        return False
    
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f"创建目录失败：{str(e)}")
            return False
    
    # 如果传入的是字符串，转换为列表
    if isinstance(content_parts, str):
        parts = content_parts.split()
    else:
        parts = content_parts
    
    # 解析内容，提取标签和正文
    tags = []
    note_text_parts = []
    
    for part in parts:
        if part.startswith('#'):
            # 这是一个标签
            tags.append(part)
        else:
            # 这是正文内容
            note_text_parts.append(part)
    
    # 组合正文内容
    note_text = ' '.join(note_text_parts)
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 格式化标签
    tags_str = ' '.join(tags) if tags else ''
    
    # 准备要追加的内容
    if tags_str:
        note_content = f"\n\n[{timestamp}] {tags_str}\n{note_text}\n"
    else:
        note_content = f"\n\n[{timestamp}]\n{note_text}\n"
    
    try:
        # 追加内容到文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(note_content)
        print(f"随笔已添加到：{file_path}")
        print(f"  时间戳：{timestamp}")
        if tags_str:
            print(f"  标签：{tags_str}")
        return True
    except Exception as e:
        print(f"写入文件失败：{str(e)}")
        return False


def show_file_path():
    """显示当前配置的文件路径"""
    file_path = get_file_path()
    if file_path:
        print(f"当前文件路径：{file_path}")
        if os.path.exists(file_path):
            print(f"文件存在：是")
            # 显示文件大小
            size = os.path.getsize(file_path)
            print(f"文件大小：{size} 字节")
        else:
            print(f"文件存在：否（将在首次写入时创建）")
    return file_path


def set_file_path(new_path):
    """设置新的文件路径"""
    if not new_path:
        print("错误：请提供文件路径")
        return False
    
    # 规范化路径（将反斜杠转换为正斜杠，或保持原样）
    new_path = os.path.normpath(new_path)
    
    config = load_config()
    old_path = config.get("file_path", "")
    config["file_path"] = new_path
    
    if save_config(config):
        print("文件路径已更新")
        if old_path:
            print(f"  旧路径：{old_path}")
        print(f"  新路径：{new_path}")
        return True
    else:
        return False


def show_head(n_lines=10):
    """显示文件的前N行（类似head命令）"""
    file_path = get_file_path()
    if not file_path:
        return False
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在：{file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            # 显示前N行
            display_lines = lines[:n_lines]
            for line in display_lines:
                # 不添加额外的换行，因为readlines已经保留了换行符
                print(line, end='')
            
            # 如果文件行数超过显示的行数，显示提示
            if total_lines > n_lines:
                print(f"\n... (共 {total_lines} 行，显示前 {n_lines} 行)")
            
        return True
    except Exception as e:
        print(f"读取文件失败：{str(e)}")
        return False


def show_tail(n_lines=10):
    """显示文件的最后N行（类似tail命令）"""
    file_path = get_file_path()
    if not file_path:
        return False
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在：{file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            # 显示最后N行
            display_lines = lines[-n_lines:] if total_lines >= n_lines else lines
            for line in display_lines:
                # 不添加额外的换行，因为readlines已经保留了换行符
                print(line, end='')
            
            # 如果文件行数超过显示的行数，显示提示
            if total_lines > n_lines:
                print(f"... (共 {total_lines} 行，显示最后 {n_lines} 行)")
            
        return True
    except Exception as e:
        print(f"读取文件失败：{str(e)}")
        return False


def is_process_running(process_name, script_path=None):
    """检测进程是否正在运行
    
    Args:
        process_name: 进程名称（如 'texteditor.exe' 或 'python.exe'）
        script_path: 如果是 Python 脚本，需要检查脚本路径
    
    Returns:
        bool: 如果进程正在运行返回 True
    """
    if sys.platform == 'win32':
        try:
            # 使用 tasklist 命令查找进程
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            # 检查输出中是否包含进程名
            if process_name.lower() in result.stdout.lower():
                # 如果是 Python 脚本，还需要检查命令行参数
                if script_path and process_name.lower() == 'python.exe':
                    # 使用 wmic 获取更详细的进程信息
                    wmic_result = subprocess.run(
                        ['wmic', 'process', 'where', f'name="{process_name}"', 'get', 'commandline'],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    # 检查命令行中是否包含脚本路径
                    if script_path.lower() in wmic_result.stdout.lower():
                        return True
                else:
                    return True
            return False
        except Exception:
            return False
    else:
        # 其他平台使用 ps 命令
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            if process_name in result.stdout:
                if script_path:
                    return script_path in result.stdout
                return True
            return False
        except Exception:
            return False


def launch_gui():
    """启动 GUI 版本的文本编辑器"""
    # 使用编译好的 exe 文件
    gui_exe = os.path.join(SCRIPT_DIR, "dist", "texteditor", "texteditor.exe")
    
    if not os.path.exists(gui_exe):
        print(f"错误：找不到 GUI 程序：{gui_exe}")
        return False
    
    # 检查进程是否已经运行
    if is_process_running("texteditor.exe"):
        print("GUI 程序已经在运行中")
        return True
    
    try:
        # 启动 exe 文件
        subprocess.Popen(
            gui_exe,
            cwd=SCRIPT_DIR,
            shell=True
        )
        print("GUI 窗口已启动")
        return True
    except Exception as e:
        print(f"启动 GUI 失败：{str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="文本编辑器命令行工具 - 快速添加带时间戳的随笔",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 添加一条随笔
  python texteditor_cli.py add "今天天气真好"
  
  # 添加带标签的随笔（在 PowerShell 中需要用引号包裹标签）
  python texteditor_cli.py add "#TODO" "我勒个去"
  python texteditor_cli.py add "#工作" "#重要" "完成项目报告"
  
  # 或者使用单个引号包裹所有内容
  python texteditor_cli.py add "#TODO 我勒个去"
  
  # 添加多行随笔（使用引号包裹）
  python texteditor_cli.py add "今天学习了Python
  感觉很有收获"
  
  # 查看当前配置的文件路径
  python texteditor_cli.py path
  
  # 设置新的文件路径
  python texteditor_cli.py path "C:/path/to/new/file.txt"
  
  # 显示文件的前10行（默认）
  python texteditor_cli.py head
  
  # 显示文件的前20行
  python texteditor_cli.py head -n 20
  
  # 显示文件的最后10行（默认）
  python texteditor_cli.py tail
  
  # 显示文件的最后20行
  python texteditor_cli.py tail -n 20
  
  # 启动 GUI 版本
  python texteditor_cli.py gui
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # add 命令：添加随笔
    add_parser = subparsers.add_parser('add', help='添加带时间戳的随笔')
    add_parser.add_argument('content', nargs='+', help='随笔内容（多个单词将用空格连接）')
    
    # path 命令：显示或设置文件路径
    path_parser = subparsers.add_parser('path', help='显示或设置配置文件中记录的文件路径')
    path_parser.add_argument('new_path', nargs='?', help='新的文件路径（可选，不提供则显示当前路径）')
    
    # head 命令：显示文件的前N行
    head_parser = subparsers.add_parser('head', help='显示配置文件指定文件的前N行')
    head_parser.add_argument('-n', '--lines', type=int, default=10, 
                            help='要显示的行数（默认：10）')
    
    # tail 命令：显示文件的最后N行
    tail_parser = subparsers.add_parser('tail', help='显示配置文件指定文件的最后N行')
    tail_parser.add_argument('-n', '--lines', type=int, default=10, 
                            help='要显示的行数（默认：10）')
    
    # gui 命令：启动 GUI 版本
    gui_parser = subparsers.add_parser('gui', help='启动 GUI 版本的文本编辑器')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        # 直接传递参数列表，支持标签识别
        add_note(args.content)
    elif args.command == 'path':
        if args.new_path:
            # 设置新路径
            set_file_path(args.new_path)
        else:
            # 显示当前路径
            show_file_path()
    elif args.command == 'head':
        # 显示文件的前N行
        show_head(args.lines)
    elif args.command == 'tail':
        # 显示文件的最后N行
        show_tail(args.lines)
    elif args.command == 'gui':
        # 启动 GUI 版本
        launch_gui()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

