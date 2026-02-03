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
from csv_parser import parse_csv, get_csv_info
from job_manager import (
    cmd_job_load, cmd_job_list, cmd_job_backup, 
    cmd_job_search, cmd_job_edit, cmd_job_delete,
    cmd_job_restore, cmd_job_list_deleted, cmd_job_reset_id
)
from schedule_manager import (
    cmd_schedule_add, cmd_schedule_list, cmd_schedule_edit,
    cmd_schedule_delete, cmd_schedule_search, cmd_schedule_gen,
    cmd_schedule_history
)

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径（与 texteditor.py 共享），使用脚本所在目录
CONFIG_FILE = os.path.join(SCRIPT_DIR, "texteditor_config.json")

# 工作列表文件路径
JOB_LIST_FILE = os.path.join(SCRIPT_DIR, "job_list.json")

# 排期列表文件路径
SCHEDULE_LIST_FILE = os.path.join(SCRIPT_DIR, "schedule_list.json")


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


def set_config_value(key_path: str, value):
    """
    设置配置项的值（支持嵌套键名，如 'tail.n'）
    
    Args:
        key_path: 配置项的键路径，支持点号分隔的嵌套键（如 'tail.n'）
        value: 要设置的值
    
    Returns:
        bool: 是否成功
    """
    config = load_config()
    
    # 解析嵌套键名
    keys = key_path.split('.')
    
    # 创建嵌套字典结构
    current = config
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            # 如果中间键已经存在但不是字典，需要先转换为字典
            current[key] = {}
        current = current[key]
    
    # 设置最终值
    # 尝试将值转换为合适的类型
    final_key = keys[-1]
    if isinstance(value, str):
        # 尝试转换为数字
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            # 保持字符串
            pass
    
    current[final_key] = value
    
    # 保存配置
    if save_config(config):
        print(f"配置项 '{key_path}' 已设置为：{value}")
        return True
    else:
        print(f"保存配置失败")
        return False


def get_config_value(key_path: str, default=None):
    """
    获取配置项的值（支持嵌套键名，如 'tail.n'）
    
    Args:
        key_path: 配置项的键路径，支持点号分隔的嵌套键（如 'tail.n'）
        default: 如果键不存在时返回的默认值
    
    Returns:
        配置项的值，如果不存在则返回 default
    """
    config = load_config()
    
    # 解析嵌套键名
    keys = key_path.split('.')
    
    # 遍历嵌套字典
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


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


def show_tail(n_lines=None):
    """显示文件的最后N行（类似tail命令）"""
    # 如果未指定行数，从配置文件读取
    if n_lines is None:
        n_lines = get_config_value('tail.n', 10)
        # 确保是整数
        try:
            n_lines = int(n_lines)
        except (ValueError, TypeError):
            n_lines = 10
    
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


def show_csv_info(csv_file_path):
    """显示 CSV 文件的基本信息"""
    if not csv_file_path:
        print("错误：请提供 CSV 文件路径")
        return False
    
    if not os.path.exists(csv_file_path):
        print(f"错误：文件不存在：{csv_file_path}")
        return False
    
    try:
        info = get_csv_info(csv_file_path)
        
        print("=" * 60)
        print("CSV 文件信息")
        print("=" * 60)
        print(f"文件路径：{info['file_path']}")
        print(f"列数：{info['column_count']}")
        print(f"行数：{info['row_count']}")
        print(f"\n表头字段名：")
        for i, header in enumerate(info['headers'], 1):
            print(f"  {i}. {header}")
        
        if info['row_count'] > 0:
            print(f"\n前3行数据预览：")
            for i, row in enumerate(info['data'][:3], 1):
                print(f"\n第{i}行：")
                for header in info['headers']:
                    value = row.get(header, '')
                    # 如果值太长，截断显示
                    if len(value) > 80:
                        value = value[:77] + "..."
                    print(f"  {header}: {value}")
        
        return True
    except Exception as e:
        print(f"解析 CSV 文件失败：{str(e)}")
        return False


# ============================================================================
# Job 命令包装函数（实际实现在 job_manager.py 中）
# ============================================================================

def job_load(csv_file_path: str):
    """从 CSV 文件加载数据到工作列表"""
    return cmd_job_load(JOB_LIST_FILE, csv_file_path)


def job_list(limit: int = None, include_deleted: bool = False):
    """显示工作列表"""
    return cmd_job_list(JOB_LIST_FILE, limit, include_deleted)


def job_backup(backup_dir: str = None):
    """备份工作列表文件"""
    return cmd_job_backup(JOB_LIST_FILE, backup_dir)


def job_search(keyword: str = None, title: str = None, tag: str = None, case_sensitive: bool = False, include_deleted: bool = False):
    """搜索工作"""
    return cmd_job_search(JOB_LIST_FILE, keyword, title, tag, case_sensitive, include_deleted)


def job_delete(index: int = None, job_key: str = None):
    """软删除工作"""
    return cmd_job_delete(JOB_LIST_FILE, index, job_key)


def job_restore(index: int = None, job_key: str = None):
    """恢复已删除的工作"""
    return cmd_job_restore(JOB_LIST_FILE, index, job_key)


def job_list_deleted(limit: int = None):
    """显示已删除的工作列表"""
    return cmd_job_list_deleted(JOB_LIST_FILE, limit)


def job_reset_id():
    """重置所有工作的ID字段"""
    return cmd_job_reset_id(JOB_LIST_FILE)


def job_edit(index: int = None, job_key: str = None, field: str = None, value: str = None, 
             add_tag: str = None, remove_tag: str = None, summary: str = None, summary_from_file: str = None):
    """编辑工作信息"""
    return cmd_job_edit(JOB_LIST_FILE, index, job_key, field, value, add_tag, remove_tag, summary, summary_from_file)


# ============================================================================
# Schedule 命令包装函数（实际实现在 schedule_manager.py 中）
# ============================================================================

def schedule_add(start_time: str, end_time: str, task: str, status: str = "未完成", description: str = "", value: str = ""):
    """添加排期"""
    return cmd_schedule_add(SCHEDULE_LIST_FILE, start_time, end_time, task, status, description, value)


def schedule_list(limit: int = None, status: str = None, start_date: str = None, end_date: str = None):
    """显示排期列表"""
    return cmd_schedule_list(SCHEDULE_LIST_FILE, limit, status, start_date, end_date)


def schedule_edit(schedule_id: int = None, index: int = None, start_time: str = None, end_time: str = None,
                  task: str = None, status: str = None, description: str = None, value: str = None):
    """编辑排期"""
    return cmd_schedule_edit(SCHEDULE_LIST_FILE, schedule_id, index, start_time, end_time, task, status, description, value)


def schedule_delete(schedule_id: int = None, index: int = None):
    """删除排期"""
    return cmd_schedule_delete(SCHEDULE_LIST_FILE, schedule_id, index)


def schedule_search(keyword: str = None, task: str = None, description: str = None, value: str = None, case_sensitive: bool = False):
    """搜索排期"""
    return cmd_schedule_search(SCHEDULE_LIST_FILE, keyword, task, description, value, case_sensitive)


def schedule_gen():
    """对话式生成排期"""
    return cmd_schedule_gen(SCHEDULE_LIST_FILE)


def schedule_history(days: int = 7):
    """查询历史排期"""
    return cmd_schedule_history(SCHEDULE_LIST_FILE, days)


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
  
  # 查看 CSV 文件基本信息
  python texteditor_cli.py csv "data/分享的链接_20251219_readshare.csv"
  
  # 从 CSV 文件加载数据到工作列表
  python texteditor_cli.py job load "data/分享的链接_20251219_readshare.csv"
  
  # 显示工作列表
  python texteditor_cli.py job list
  
  # 显示工作列表（限制显示数量）
  python texteditor_cli.py job list --limit 10
  
  # 编辑工作（通过索引）
  python texteditor_cli.py job edit --index 0 --field "标题" --value "新标题"
  python texteditor_cli.py job edit --index 0 --add-tag "重要"
  python texteditor_cli.py job edit --index 0 --remove-tag "重要"
  
  # 编辑工作（通过链接）
  python texteditor_cli.py job edit --key "https://..." --add-tag "目标工作"
  
  # 备份工作列表
  python texteditor_cli.py job backup
  python texteditor_cli.py job backup --dir "custom/backup/path"
  
  # 搜索工作（默认同时搜索标题和标签）
  python texteditor_cli.py job search "量化"
  python texteditor_cli.py job search --title "量化"
  python texteditor_cli.py job search --tag "工作"
  python texteditor_cli.py job search --title "开发" --tag "重要"
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
    tail_parser.add_argument('-n', '--lines', type=int, default=None, 
                            help='要显示的行数（默认：从配置文件 tail.n 读取，如果未配置则使用 10）')
    
    # config 命令：设置配置项
    config_parser = subparsers.add_parser('config', help='设置配置项（支持嵌套键名，如 tail.n）')
    config_parser.add_argument('key', help='配置项的键路径（支持点号分隔，如 tail.n）')
    config_parser.add_argument('value', help='要设置的值')
    
    # gui 命令：启动 GUI 版本
    gui_parser = subparsers.add_parser('gui', help='启动 GUI 版本的文本编辑器')
    
    # csv 命令：查看 CSV 文件基本信息
    csv_parser = subparsers.add_parser('csv', help='查看 CSV 文件的基本信息（表头、行数、列数等）')
    csv_parser.add_argument('csv_file', help='CSV 文件路径')
    
    # job 命令：工作列表管理
    job_parser = subparsers.add_parser('job', help='工作列表管理（从 CSV 文件加载数据，维护工作列表）')
    job_subparsers = job_parser.add_subparsers(dest='job_command', help='job 子命令')
    
    # job load 命令：从 CSV 文件加载数据
    job_load_parser = job_subparsers.add_parser('load', help='从 CSV 文件加载数据到工作列表（去重，只增不删）')
    job_load_parser.add_argument('csv_file', help='CSV 文件路径')
    
    # job list 命令：显示工作列表
    job_list_parser = job_subparsers.add_parser('list', help='显示工作列表')
    job_list_parser.add_argument('--limit', type=int, default=None, help='限制显示的数量（默认：显示全部）')
    job_list_parser.add_argument('--include-deleted', action='store_true', help='包含已删除的工作（默认：不包含）')
    
    # job edit 命令：编辑工作信息
    job_edit_parser = job_subparsers.add_parser('edit', help='编辑工作信息（修改标题、添加/移除标签、设置摘要等）')
    job_edit_parser.add_argument('--index', type=int, default=None, help='工作索引（从0开始，与 --key 二选一）')
    job_edit_parser.add_argument('--key', type=str, default=None, help='工作唯一标识（链接，与 --index 二选一）')
    job_edit_parser.add_argument('--field', type=str, default=None, help='要修改的字段名（如：标题、时间等）')
    job_edit_parser.add_argument('--value', type=str, default=None, help='新值（与 --field 配合使用）')
    job_edit_parser.add_argument('--add-tag', type=str, default=None, help='添加标签')
    job_edit_parser.add_argument('--remove-tag', type=str, default=None, help='移除标签')
    job_edit_parser.add_argument('--summary', type=str, default=None, help='设置摘要内容（支持多行，使用\\n表示换行，或使用--summary-from-file从文件读取。注意：包含空格的值需要用引号包裹）')
    job_edit_parser.add_argument('--summary-from-file', type=str, default=None, help='从文件读取摘要内容（支持多行）')
    
    # job backup 命令：备份工作列表
    job_backup_parser = job_subparsers.add_parser('backup', help='备份工作列表文件到 job-manager-data 目录')
    job_backup_parser.add_argument('--dir', type=str, default=None, help='备份目录路径（默认：job-manager-data）')
    
    # job search 命令：搜索工作
    job_search_parser = job_subparsers.add_parser('search', help='搜索工作（默认同时搜索标题和标签）')
    # 位置参数：直接提供关键词
    job_search_parser.add_argument('keyword', type=str, nargs='?', default=None, help='搜索关键词（位置参数，默认同时搜索标题和标签）')
    # 选项参数：用于精确控制
    job_search_parser.add_argument('--title', type=str, default=None, help='标题关键词（部分匹配）')
    job_search_parser.add_argument('--tag', type=str, default=None, help='标签关键词（部分匹配）')
    job_search_parser.add_argument('--case-sensitive', action='store_true', help='区分大小写（默认：不区分）')
    job_search_parser.add_argument('--include-deleted', action='store_true', help='包含已删除的工作（默认：不包含）')
    
    # job delete 命令：软删除工作
    job_delete_parser = job_subparsers.add_parser('delete', help='软删除工作（标记为已删除，可恢复）')
    job_delete_parser.add_argument('--index', type=int, default=None, help='工作索引（从0开始，与 --key 二选一）')
    job_delete_parser.add_argument('--key', type=str, default=None, help='工作唯一标识（链接，与 --index 二选一）')
    
    # job restore 命令：恢复已删除的工作
    job_restore_parser = job_subparsers.add_parser('restore', help='恢复已删除的工作')
    job_restore_parser.add_argument('--index', type=int, default=None, help='工作索引（基于已删除列表，与 --key 二选一）')
    job_restore_parser.add_argument('--key', type=str, default=None, help='工作唯一标识（链接，与 --index 二选一）')
    
    # job list-deleted 命令：显示已删除的工作列表
    job_list_deleted_parser = job_subparsers.add_parser('list-deleted', help='显示已删除的工作列表')
    job_list_deleted_parser.add_argument('--limit', type=int, default=None, help='限制显示的数量（默认：显示全部）')
    
    # job reset-id 命令：重置所有工作的ID字段
    job_reset_id_parser = job_subparsers.add_parser('reset-id', help='重置所有工作的ID字段，从0开始重新编号')
    
    # schedule 命令：排期管理
    schedule_parser = subparsers.add_parser('schedule', help='排期管理（管理时间段、任务和完成情况）')
    schedule_subparsers = schedule_parser.add_subparsers(dest='schedule_command', help='schedule 子命令')
    
    # schedule add 命令：添加排期
    schedule_add_parser = schedule_subparsers.add_parser('add', help='添加排期')
    schedule_add_parser.add_argument('start_time', help='开始时间（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）')
    schedule_add_parser.add_argument('end_time', help='结束时间（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）')
    schedule_add_parser.add_argument('task', help='任务描述')
    schedule_add_parser.add_argument('--status', type=str, default='未完成', 
                                     choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                                     help='完成情况（默认：未完成）')
    schedule_add_parser.add_argument('--description', type=str, default='', help='详细描述（可选）')
    schedule_add_parser.add_argument('--value', type=str, default='', help='意义/价值（可选，用于激励自己）')
    
    # schedule list 命令：显示排期列表
    schedule_list_parser = schedule_subparsers.add_parser('list', help='显示排期列表')
    schedule_list_parser.add_argument('--limit', type=int, default=None, help='限制显示的数量（默认：显示全部）')
    schedule_list_parser.add_argument('--status', type=str, choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                                     help='按状态筛选')
    schedule_list_parser.add_argument('--start-date', type=str, help='筛选开始日期之后（YYYY-MM-DD）')
    schedule_list_parser.add_argument('--end-date', type=str, help='筛选结束日期之前（YYYY-MM-DD）')
    
    # schedule edit 命令：编辑排期
    schedule_edit_parser = schedule_subparsers.add_parser('edit', help='编辑排期信息')
    schedule_edit_parser.add_argument('--id', type=int, default=None, dest='schedule_id',
                                     help='排期ID（与 --index 二选一）')
    schedule_edit_parser.add_argument('--index', type=int, default=None,
                                     help='排期索引（从0开始，与 --id 二选一）')
    schedule_edit_parser.add_argument('--start-time', type=str, help='新的开始时间')
    schedule_edit_parser.add_argument('--end-time', type=str, help='新的结束时间')
    schedule_edit_parser.add_argument('--task', type=str, help='新的任务描述')
    schedule_edit_parser.add_argument('--status', type=str, choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                                     help='新的完成情况')
    schedule_edit_parser.add_argument('--description', type=str, help='新的描述')
    schedule_edit_parser.add_argument('--value', type=str, help='新的意义/价值')
    
    # schedule delete 命令：删除排期
    schedule_delete_parser = schedule_subparsers.add_parser('delete', help='删除排期')
    schedule_delete_parser.add_argument('--id', type=int, default=None, dest='schedule_id',
                                       help='排期ID（与 --index 二选一）')
    schedule_delete_parser.add_argument('--index', type=int, default=None,
                                       help='排期索引（从0开始，与 --id 二选一）')
    
    # schedule search 命令：搜索排期
    schedule_search_parser = schedule_subparsers.add_parser('search', help='搜索排期')
    schedule_search_parser.add_argument('keyword', type=str, nargs='?', default=None,
                                       help='搜索关键词（位置参数，在任务、描述和意义/价值中搜索）')
    schedule_search_parser.add_argument('--task', type=str, default=None, help='任务关键词')
    schedule_search_parser.add_argument('--description', type=str, default=None, help='描述关键词')
    schedule_search_parser.add_argument('--value', type=str, default=None, help='意义/价值关键词')
    schedule_search_parser.add_argument('--case-sensitive', action='store_true',
                                       help='区分大小写（默认：不区分）')
    
    # schedule gen 命令：对话式生成排期
    schedule_gen_parser = schedule_subparsers.add_parser('gen', help='对话式自动生成排期任务')
    
    # schedule history 命令：查询历史排期
    schedule_history_parser = schedule_subparsers.add_parser('history', help='查询历史排期（查看过去N天内的排期）')
    schedule_history_parser.add_argument('--days', type=int, default=7, 
                                        help='查询过去多少天内的历史排期（默认：7天）')
    
    # ss 命令：schedule 的快捷方式
    ss_parser = subparsers.add_parser('ss', help='排期管理快捷方式（等同于 schedule）')
    ss_subparsers = ss_parser.add_subparsers(dest='ss_command', help='ss 子命令')
    
    # ss add 命令：添加排期
    ss_add_parser = ss_subparsers.add_parser('add', help='添加排期')
    ss_add_parser.add_argument('start_time', help='开始时间（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）')
    ss_add_parser.add_argument('end_time', help='结束时间（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）')
    ss_add_parser.add_argument('task', help='任务描述')
    ss_add_parser.add_argument('--status', type=str, default='未完成', 
                               choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                               help='完成情况（默认：未完成）')
    ss_add_parser.add_argument('--description', type=str, default='', help='详细描述（可选）')
    ss_add_parser.add_argument('--value', type=str, default='', help='意义/价值（可选，用于激励自己）')
    
    # ss list 命令：显示排期列表
    ss_list_parser = ss_subparsers.add_parser('list', help='显示排期列表')
    ss_list_parser.add_argument('--limit', type=int, default=None, help='限制显示的数量（默认：显示全部）')
    ss_list_parser.add_argument('--status', type=str, choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                               help='按状态筛选')
    ss_list_parser.add_argument('--start-date', type=str, help='筛选开始日期之后（YYYY-MM-DD）')
    ss_list_parser.add_argument('--end-date', type=str, help='筛选结束日期之前（YYYY-MM-DD）')
    
    # ss edit 命令：编辑排期
    ss_edit_parser = ss_subparsers.add_parser('edit', help='编辑排期信息')
    ss_edit_parser.add_argument('--id', type=int, default=None, dest='schedule_id',
                               help='排期ID（与 --index 二选一）')
    ss_edit_parser.add_argument('--index', type=int, default=None,
                               help='排期索引（从0开始，与 --id 二选一）')
    ss_edit_parser.add_argument('--start-time', type=str, help='新的开始时间')
    ss_edit_parser.add_argument('--end-time', type=str, help='新的结束时间')
    ss_edit_parser.add_argument('--task', type=str, help='新的任务描述')
    ss_edit_parser.add_argument('--status', type=str, choices=['已完成', '进行中', '未完成', '搁置', '延期'],
                               help='新的完成情况')
    ss_edit_parser.add_argument('--description', type=str, help='新的描述')
    ss_edit_parser.add_argument('--value', type=str, help='新的意义/价值')
    
    # ss delete 命令：删除排期
    ss_delete_parser = ss_subparsers.add_parser('delete', help='删除排期')
    ss_delete_parser.add_argument('--id', type=int, default=None, dest='schedule_id',
                                 help='排期ID（与 --index 二选一）')
    ss_delete_parser.add_argument('--index', type=int, default=None,
                                 help='排期索引（从0开始，与 --id 二选一）')
    
    # ss search 命令：搜索排期
    ss_search_parser = ss_subparsers.add_parser('search', help='搜索排期')
    ss_search_parser.add_argument('keyword', type=str, nargs='?', default=None,
                                 help='搜索关键词（位置参数，在任务、描述和意义/价值中搜索）')
    ss_search_parser.add_argument('--task', type=str, default=None, help='任务关键词')
    ss_search_parser.add_argument('--description', type=str, default=None, help='描述关键词')
    ss_search_parser.add_argument('--value', type=str, default=None, help='意义/价值关键词')
    ss_search_parser.add_argument('--case-sensitive', action='store_true',
                                 help='区分大小写（默认：不区分）')
    
    # ss gen 命令：对话式生成排期
    ss_gen_parser = ss_subparsers.add_parser('gen', help='对话式自动生成排期任务')
    
    # ss history 命令：查询历史排期
    ss_history_parser = ss_subparsers.add_parser('history', help='查询历史排期（查看过去N天内的排期）')
    ss_history_parser.add_argument('--days', type=int, default=7, 
                                   help='查询过去多少天内的历史排期（默认：7天）')
    
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
    elif args.command == 'config':
        # 设置配置项
        set_config_value(args.key, args.value)
    elif args.command == 'gui':
        # 启动 GUI 版本
        launch_gui()
    elif args.command == 'csv':
        # 查看 CSV 文件信息
        show_csv_info(args.csv_file)
    elif args.command == 'job':
        # 工作列表管理
        if args.job_command == 'load':
            job_load(args.csv_file)
        elif args.job_command == 'list':
            job_list(args.limit, getattr(args, 'include_deleted', False))
        elif args.job_command == 'edit':
            job_edit(
                index=args.index,
                job_key=args.key,
                field=args.field,
                value=args.value,
                add_tag=args.add_tag,
                remove_tag=args.remove_tag,
                summary=args.summary,
                summary_from_file=args.summary_from_file
            )
        elif args.job_command == 'backup':
            job_backup(args.dir)
        elif args.job_command == 'search':
            # 位置参数 keyword 优先，如果没有位置参数则使用选项参数
            search_keyword = args.keyword if args.keyword else None
            job_search(
                keyword=search_keyword,
                title=args.title,
                tag=args.tag,
                case_sensitive=args.case_sensitive,
                include_deleted=getattr(args, 'include_deleted', False)
            )
        elif args.job_command == 'delete':
            job_delete(index=args.index, job_key=args.key)
        elif args.job_command == 'restore':
            job_restore(index=args.index, job_key=args.key)
        elif args.job_command == 'list-deleted':
            job_list_deleted(args.limit)
        elif args.job_command == 'reset-id':
            job_reset_id()
        else:
            job_parser.print_help()
    elif args.command == 'schedule':
        # 排期管理
        # 如果没有子命令，默认调用 gen
        if not args.schedule_command:
            schedule_gen()
        elif args.schedule_command == 'add':
            schedule_add(args.start_time, args.end_time, args.task, args.status, 
                        getattr(args, 'description', ''), getattr(args, 'value', ''))
        elif args.schedule_command == 'list':
            schedule_list(args.limit, getattr(args, 'status', None),
                         getattr(args, 'start_date', None), getattr(args, 'end_date', None))
        elif args.schedule_command == 'edit':
            schedule_edit(
                schedule_id=getattr(args, 'schedule_id', None),
                index=args.index,
                start_time=getattr(args, 'start_time', None),
                end_time=getattr(args, 'end_time', None),
                task=getattr(args, 'task', None),
                status=getattr(args, 'status', None),
                description=getattr(args, 'description', None),
                value=getattr(args, 'value', None)
            )
        elif args.schedule_command == 'delete':
            schedule_delete(schedule_id=getattr(args, 'schedule_id', None), index=args.index)
        elif args.schedule_command == 'search':
            search_keyword = args.keyword if args.keyword else None
            schedule_search(
                keyword=search_keyword,
                task=getattr(args, 'task', None),
                description=getattr(args, 'description', None),
                value=getattr(args, 'value', None),
                case_sensitive=getattr(args, 'case_sensitive', False)
            )
        elif args.schedule_command == 'gen':
            schedule_gen()
        elif args.schedule_command == 'history':
            schedule_history(getattr(args, 'days', 7))
        else:
            schedule_parser.print_help()
    elif args.command == 'ss':
        # ss 命令：schedule 的快捷方式，转发给 schedule 的处理逻辑
        # 如果没有子命令，默认调用 gen
        if not args.ss_command:
            schedule_gen()
        elif args.ss_command == 'add':
            schedule_add(args.start_time, args.end_time, args.task, args.status, 
                        getattr(args, 'description', ''), getattr(args, 'value', ''))
        elif args.ss_command == 'list':
            schedule_list(args.limit, getattr(args, 'status', None),
                         getattr(args, 'start_date', None), getattr(args, 'end_date', None))
        elif args.ss_command == 'edit':
            schedule_edit(
                schedule_id=getattr(args, 'schedule_id', None),
                index=args.index,
                start_time=getattr(args, 'start_time', None),
                end_time=getattr(args, 'end_time', None),
                task=getattr(args, 'task', None),
                status=getattr(args, 'status', None),
                description=getattr(args, 'description', None),
                value=getattr(args, 'value', None)
            )
        elif args.ss_command == 'delete':
            schedule_delete(schedule_id=getattr(args, 'schedule_id', None), index=args.index)
        elif args.ss_command == 'search':
            search_keyword = args.keyword if args.keyword else None
            schedule_search(
                keyword=search_keyword,
                task=getattr(args, 'task', None),
                description=getattr(args, 'description', None),
                value=getattr(args, 'value', None),
                case_sensitive=getattr(args, 'case_sensitive', False)
            )
        elif args.ss_command == 'gen':
            schedule_gen()
        elif args.ss_command == 'history':
            schedule_history(getattr(args, 'days', 7))
        else:
            ss_parser.print_help()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

