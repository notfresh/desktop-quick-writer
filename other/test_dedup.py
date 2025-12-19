#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试去重功能"""

import json

# 读取 job_list.json
with open('job_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

jobs = data['jobs']
print(f"总工作数: {len(jobs)}")

# 检查链接重复
links = [j.get('链接', '') for j in jobs if j.get('链接')]
unique_links = set(links)
print(f"有链接的工作数: {len(links)}")
print(f"唯一链接数: {len(unique_links)}")

# 检查重复
duplicate_links = []
for link in unique_links:
    count = links.count(link)
    if count > 1:
        duplicate_links.append((link, count))

if duplicate_links:
    print(f"\n发现 {len(duplicate_links)} 个重复链接:")
    for link, count in duplicate_links[:5]:
        print(f"  重复 {count} 次: {link[:80]}...")
else:
    print("\n✓ 没有发现重复链接")

# 检查标题+时间重复（用于没有链接的情况）
no_link_jobs = [j for j in jobs if not j.get('链接')]
if no_link_jobs:
    print(f"\n没有链接的工作数: {len(no_link_jobs)}")
    title_time_keys = [f"{j.get('标题', '')}|{j.get('时间', '')}" for j in no_link_jobs]
    unique_title_time = set(title_time_keys)
    print(f"唯一标题+时间组合数: {len(unique_title_time)}")
    
    duplicate_title_time = []
    for key in unique_title_time:
        count = title_time_keys.count(key)
        if count > 1:
            duplicate_title_time.append((key, count))
    
    if duplicate_title_time:
        print(f"发现 {len(duplicate_title_time)} 个重复的标题+时间组合")
    else:
        print("[OK] 没有发现重复的标题+时间组合")

