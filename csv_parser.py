#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 文件解析工具
解析 CSV 文件并返回表头字段名和数据表
"""

import csv
import os
import sys
from typing import List, Dict, Union, Tuple


def parse_csv(file_path: str, encoding: str = 'utf-8', delimiter: str = ',') -> Tuple[List[str], List[Dict[str, str]]]:
    """
    解析 CSV 文件
    
    Args:
        file_path: CSV 文件路径
        encoding: 文件编码（默认：utf-8）
        delimiter: 分隔符（默认：逗号）
    
    Returns:
        Tuple[List[str], List[Dict[str, str]]]: (表头字段名列表, 数据行列表（每行是字典）)
    
    Raises:
        FileNotFoundError: 文件不存在
        Exception: 解析错误
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    headers = []
    data_rows = []
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            # 使用 csv.DictReader 自动处理表头
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # 获取表头
            headers = reader.fieldnames if reader.fieldnames else []
            
            # 读取所有数据行
            for row in reader:
                # 过滤空行（所有字段都为空）
                if any(row.values()):
                    data_rows.append(dict(row))
    
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，尝试其他编码
        encodings = ['gbk', 'gb2312', 'latin-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    headers = reader.fieldnames if reader.fieldnames else []
                    for row in reader:
                        if any(row.values()):
                            data_rows.append(dict(row))
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception(f"无法使用常见编码解析文件：{file_path}")
    
    return headers, data_rows


def parse_csv_as_list(file_path: str, encoding: str = 'utf-8', delimiter: str = ',') -> Tuple[List[str], List[List[str]]]:
    """
    解析 CSV 文件，返回列表格式（而不是字典格式）
    
    Args:
        file_path: CSV 文件路径
        encoding: 文件编码（默认：utf-8）
        delimiter: 分隔符（默认：逗号）
    
    Returns:
        Tuple[List[str], List[List[str]]]: (表头字段名列表, 数据行列表（每行是字段值列表）)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    headers = []
    data_rows = []
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            
            # 第一行是表头
            headers = next(reader, [])
            
            # 读取所有数据行
            for row in reader:
                # 过滤空行
                if any(cell.strip() for cell in row):
                    data_rows.append(row)
    
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，尝试其他编码
        encodings = ['gbk', 'gb2312', 'latin-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    headers = next(reader, [])
                    for row in reader:
                        if any(cell.strip() for cell in row):
                            data_rows.append(row)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception(f"无法使用常见编码解析文件：{file_path}")
    
    return headers, data_rows


def get_csv_info(file_path: str) -> Dict:
    """
    获取 CSV 文件的基本信息
    
    Returns:
        Dict: 包含表头、行数、列数等信息
    """
    headers, data_rows = parse_csv(file_path)
    
    return {
        'file_path': file_path,
        'headers': headers,
        'column_count': len(headers),
        'row_count': len(data_rows),
        'data': data_rows
    }


def main():
    """命令行工具入口"""
    if len(sys.argv) < 2:
        print("用法: python csv_parser.py <csv_file_path> [format]")
        print("  format: 'dict' (默认，返回字典格式) 或 'list' (返回列表格式)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    # 处理路径编码问题
    if not os.path.exists(file_path):
        # 尝试使用 glob 查找
        import glob
        dir_name = os.path.dirname(file_path) if os.path.dirname(file_path) else '.'
        pattern = os.path.join(dir_name, '*.csv')
        matches = glob.glob(pattern)
        if matches:
            file_path = matches[0]
            print(f"使用找到的文件：{file_path}")
    
    format_type = sys.argv[2] if len(sys.argv) > 2 else 'dict'
    
    try:
        if format_type == 'list':
            headers, data = parse_csv_as_list(file_path)
            print("表头字段名：")
            print(headers)
            print(f"\n数据行数：{len(data)}")
            print("\n前5行数据：")
            for i, row in enumerate(data[:5], 1):
                print(f"第{i}行: {row}")
        else:
            headers, data = parse_csv(file_path)
            print("表头字段名：")
            print(headers)
            print(f"\n数据行数：{len(data)}")
            print("\n前5行数据：")
            for i, row in enumerate(data[:5], 1):
                print(f"第{i}行: {row}")
        
        # 返回信息
        info = get_csv_info(file_path)
        print(f"\n文件信息：")
        print(f"  文件路径：{info['file_path']}")
        print(f"  列数：{info['column_count']}")
        print(f"  行数：{info['row_count']}")
        
    except Exception as e:
        print(f"错误：{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

