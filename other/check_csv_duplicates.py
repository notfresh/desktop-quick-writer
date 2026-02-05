#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查 CSV 文件中的重复数据"""

from csv_parser import parse_csv

csv_file = "data/分享的链接_20251219_readshare.csv"
headers, data = parse_csv(csv_file)

print("=" * 60)
print("CSV 文件重复检查")
print("=" * 60)
print(f"总行数: {len(data)}")

# 检查链接重复
links = [row.get('链接', '') for row in data if row.get('链接')]
unique_links = set(links)
print(f"\n有链接的行数: {len(links)}")
print(f"唯一链接数: {len(unique_links)}")

# 找出重复的链接
link_counts = {}
for link in links:
    link_counts[link] = link_counts.get(link, 0) + 1

duplicate_links = {link: count for link, count in link_counts.items() if count > 1}

if duplicate_links:
    print(f"\n发现 {len(duplicate_links)} 个重复链接:")
    for link, count in duplicate_links.items():
        print(f"\n  重复 {count} 次:")
        # 找出所有包含这个链接的行
        for i, row in enumerate(data, 1):
            if row.get('链接') == link:
                print(f"    第{i}行: {row.get('标题', '无标题')} | {row.get('时间', '无时间')}")
else:
    print("\n[OK] 没有发现重复链接")

# 检查标题+时间重复（用于没有链接的情况）
no_link_rows = [row for row in data if not row.get('链接')]
if no_link_rows:
    print(f"\n没有链接的行数: {len(no_link_rows)}")
    title_time_keys = [f"{row.get('标题', '')}|{row.get('时间', '')}" for row in no_link_rows]
    unique_title_time = set(title_time_keys)
    print(f"唯一标题+时间组合数: {len(unique_title_time)}")
    
    title_time_counts = {}
    for key in title_time_keys:
        title_time_counts[key] = title_time_counts.get(key, 0) + 1
    
    duplicate_title_time = {key: count for key, count in title_time_counts.items() if count > 1}
    
    if duplicate_title_time:
        print(f"\n发现 {len(duplicate_title_time)} 个重复的标题+时间组合:")
        for key, count in duplicate_title_time.items():
            print(f"  重复 {count} 次: {key}")
    else:
        print("[OK] 没有发现重复的标题+时间组合")

# 显示所有行的链接（用于人工检查）
print("\n" + "=" * 60)
print("所有行的链接列表（用于检查）:")
print("=" * 60)
for i, row in enumerate(data, 1):
    link = row.get('链接', '')
    title = row.get('标题', '无标题')
    if link:
        # 截断长链接
        link_display = link[:80] + "..." if len(link) > 80 else link
        print(f"{i:2d}. {title:30s} | {link_display}")
    else:
        print(f"{i:2d}. {title:30s} | [无链接]")

