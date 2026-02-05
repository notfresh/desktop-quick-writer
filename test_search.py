#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试搜索功能"""

from job_manager import JobManager

manager = JobManager('job_list.json')

# 测试搜索"阿里"
print("测试搜索'阿里':")
results = manager.search(keyword='阿里')
print(f"搜索结果数: {len(results)}")
for r in results:
    print(f"  - {r.get('标题')} (标签: {r.get('标签')})")

print("\n测试搜索'量化':")
results = manager.search(keyword='量化')
print(f"搜索结果数: {len(results)}")
for r in results[:3]:
    print(f"  - {r.get('标题')}")



