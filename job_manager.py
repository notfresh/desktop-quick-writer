#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作列表管理工具
维护从 CSV 文件加载的工作信息，支持去重和持久化存储
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Set
from csv_parser import parse_csv


class JobManager:
    """工作列表管理器"""
    
    def __init__(self, job_list_file: str):
        """
        初始化工作列表管理器
        
        Args:
            job_list_file: 工作列表文件路径（JSON 格式）
        """
        self.job_list_file = job_list_file
        self.csv_files = []  # 已加载的 CSV 文件列表
        self.jobs = []  # 工作列表数据
        
        # 加载已有的工作列表
        self._load_job_list()
    
    def _load_job_list(self):
        """从文件加载工作列表"""
        if os.path.exists(self.job_list_file):
            try:
                with open(self.job_list_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.csv_files = data.get('csv_files', [])
                    self.jobs = data.get('jobs', [])
            except Exception as e:
                print(f"加载工作列表失败：{str(e)}")
                self.csv_files = []
                self.jobs = []
        else:
            self.csv_files = []
            self.jobs = []
    
    def _save_job_list(self):
        """保存工作列表到文件"""
        try:
            data = {
                'csv_files': self.csv_files,
                'jobs': self.jobs
            }
            with open(self.job_list_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存工作列表失败：{str(e)}")
            return False
    
    def _get_job_key(self, job: Dict) -> str:
        """
        生成工作的唯一标识符（用于去重）
        使用链接作为唯一标识，如果没有链接则使用标题+时间
        
        Args:
            job: 工作数据字典
        
        Returns:
            str: 唯一标识符
        """
        # 优先使用链接作为唯一标识
        if job.get('链接'):
            return job['链接']
        # 如果没有链接，使用标题+时间
        title = job.get('标题', '')
        time_str = job.get('时间', '')
        return f"{title}|{time_str}"
    
    def load_from_csv(self, csv_file_path: str) -> Dict:
        """
        从 CSV 文件加载数据到工作列表（去重，只增不删）
        
        Args:
            csv_file_path: CSV 文件路径
        
        Returns:
            Dict: 加载结果统计信息
        """
        if not os.path.exists(csv_file_path):
            return {
                'success': False,
                'message': f"文件不存在：{csv_file_path}",
                'added': 0,
                'skipped': 0,
                'total': 0
            }
        
        # 规范化路径
        csv_file_path = os.path.normpath(os.path.abspath(csv_file_path))
        
        # 检查是否已经加载过这个文件
        if csv_file_path in self.csv_files:
            return {
                'success': False,
                'message': f"文件已加载过：{csv_file_path}",
                'added': 0,
                'skipped': 0,
                'total': 0
            }
        
        try:
            # 解析 CSV 文件
            headers, data_rows = parse_csv(csv_file_path)
            
            # 检查必要的字段
            if '链接' not in headers and '标题' not in headers:
                return {
                    'success': False,
                    'message': "CSV 文件缺少必要的字段（链接或标题）",
                    'added': 0,
                    'skipped': 0,
                    'total': len(data_rows)
                }
            
            # 获取已有工作的唯一标识集合
            existing_keys: Set[str] = set()
            for job in self.jobs:
                key = self._get_job_key(job)
                existing_keys.add(key)
            
            # 添加新工作（去重）
            added_count = 0
            skipped_count = 0
            
            for row in data_rows:
                key = self._get_job_key(row)
                if key not in existing_keys:
                    self.jobs.append(row)
                    existing_keys.add(key)
                    added_count += 1
                else:
                    skipped_count += 1
            
            # 记录已加载的 CSV 文件
            self.csv_files.append(csv_file_path)
            
            # 保存工作列表
            if self._save_job_list():
                return {
                    'success': True,
                    'message': f"成功加载 {csv_file_path}",
                    'added': added_count,
                    'skipped': skipped_count,
                    'total': len(data_rows)
                }
            else:
                return {
                    'success': False,
                    'message': "加载完成但保存失败",
                    'added': added_count,
                    'skipped': skipped_count,
                    'total': len(data_rows)
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"加载失败：{str(e)}",
                'added': 0,
                'skipped': 0,
                'total': 0
            }
    
    def list_jobs(self, limit: int = None, include_deleted: bool = False) -> List[Dict]:
        """
        获取工作列表
        
        Args:
            limit: 限制返回的数量（None 表示返回全部）
            include_deleted: 是否包含已删除的工作（默认：False）
        
        Returns:
            List[Dict]: 工作列表
        """
        # 过滤已删除的工作
        if include_deleted:
            jobs = self.jobs
        else:
            jobs = [job for job in self.jobs if not job.get('已删除', False)]
        
        if limit is None:
            return jobs
        return jobs[:limit]
    
    def get_stats(self) -> Dict:
        """
        获取工作列表统计信息
        
        Returns:
            Dict: 统计信息
        """
        active_jobs = [job for job in self.jobs if not job.get('已删除', False)]
        deleted_jobs = [job for job in self.jobs if job.get('已删除', False)]
        return {
            'total_jobs': len(self.jobs),
            'active_jobs': len(active_jobs),
            'deleted_jobs': len(deleted_jobs),
            'csv_files_count': len(self.csv_files),
            'csv_files': self.csv_files
        }
    
    def clear_all(self) -> bool:
        """
        清空所有工作列表（危险操作）
        
        Returns:
            bool: 是否成功
        """
        self.jobs = []
        self.csv_files = []
        return self._save_job_list()
    
    def find_job(self, job_key: str, include_deleted: bool = True) -> Dict:
        """
        根据唯一标识查找工作
        
        Args:
            job_key: 工作的唯一标识（链接或标题+时间）
            include_deleted: 是否包含已删除的工作（默认：True，因为编辑时需要找到已删除的）
        
        Returns:
            Dict: 找到的工作字典，如果未找到返回 None
        """
        for job in self.jobs:
            if self._get_job_key(job) == job_key:
                if include_deleted or not job.get('已删除', False):
                    return job
        return None
    
    def find_job_by_index(self, index: int, include_deleted: bool = False) -> Dict:
        """
        根据索引查找工作（基于未删除的列表）
        
        Args:
            index: 工作索引（从0开始，基于未删除的列表）
            include_deleted: 是否包含已删除的工作（默认：False）
        
        Returns:
            Dict: 找到的工作字典，如果索引无效返回 None
        """
        jobs = self.list_jobs(include_deleted=include_deleted)
        if 0 <= index < len(jobs):
            return jobs[index]
        return None
    
    def update_job(self, job_key: str, updates: Dict) -> Dict:
        """
        更新工作信息
        
        Args:
            job_key: 工作的唯一标识（链接或标题+时间）
            updates: 要更新的字段字典，例如 {'标题': '新标题', '标签': '新标签'}
        
        Returns:
            Dict: 更新结果 {'success': bool, 'message': str, 'job': Dict}
        """
        job = self.find_job(job_key)
        if not job:
            return {
                'success': False,
                'message': f"未找到工作（key: {job_key[:50]}...）",
                'job': None
            }
        
        # 更新字段（如果字段不存在则添加）
        for key, value in updates.items():
            job[key] = value
        
        # 保存
        if self._save_job_list():
            return {
                'success': True,
                'message': "更新成功",
                'job': job
            }
        else:
            return {
                'success': False,
                'message': "更新完成但保存失败",
                'job': job
            }
    
    def update_job_by_index(self, index: int, updates: Dict) -> Dict:
        """
        根据索引更新工作信息
        
        Args:
            index: 工作索引（从0开始）
            updates: 要更新的字段字典
        
        Returns:
            Dict: 更新结果
        """
        job = self.find_job_by_index(index)
        if not job:
            return {
                'success': False,
                'message': f"索引无效：{index}",
                'job': None
            }
        
        job_key = self._get_job_key(job)
        return self.update_job(job_key, updates)
    
    def add_tag(self, job_key: str, new_tag: str) -> Dict:
        """
        给工作添加标签（如果标签已存在则不重复添加）
        
        Args:
            job_key: 工作的唯一标识
            new_tag: 要添加的新标签
        
        Returns:
            Dict: 更新结果
        """
        job = self.find_job(job_key)
        if not job:
            return {
                'success': False,
                'message': f"未找到工作（key: {job_key[:50]}...）",
                'job': None
            }
        
        # 获取现有标签
        current_tags = job.get('标签', '').strip()
        
        # 如果标签为空，直接设置
        if not current_tags:
            job['标签'] = new_tag
        else:
            # 解析现有标签（支持逗号分隔）
            tag_list = [tag.strip() for tag in current_tags.split(',')]
            # 如果新标签不存在，则添加
            if new_tag not in tag_list:
                tag_list.append(new_tag)
                job['标签'] = ', '.join(tag_list)
        
        # 保存
        if self._save_job_list():
            return {
                'success': True,
                'message': f"标签已添加：{new_tag}",
                'job': job
            }
        else:
            return {
                'success': False,
                'message': "添加标签完成但保存失败",
                'job': job
            }
    
    def add_tag_by_index(self, index: int, new_tag: str) -> Dict:
        """
        根据索引给工作添加标签
        
        Args:
            index: 工作索引
            new_tag: 要添加的新标签
        
        Returns:
            Dict: 更新结果
        """
        job = self.find_job_by_index(index)
        if not job:
            return {
                'success': False,
                'message': f"索引无效：{index}",
                'job': None
            }
        
        job_key = self._get_job_key(job)
        return self.add_tag(job_key, new_tag)
    
    def remove_tag(self, job_key: str, tag_to_remove: str) -> Dict:
        """
        从工作中移除标签
        
        Args:
            job_key: 工作的唯一标识
            tag_to_remove: 要移除的标签
        
        Returns:
            Dict: 更新结果
        """
        job = self.find_job(job_key)
        if not job:
            return {
                'success': False,
                'message': f"未找到工作（key: {job_key[:50]}...）",
                'job': None
            }
        
        # 获取现有标签
        current_tags = job.get('标签', '').strip()
        if not current_tags:
            return {
                'success': False,
                'message': "工作没有标签",
                'job': job
            }
        
        # 解析现有标签
        tag_list = [tag.strip() for tag in current_tags.split(',')]
        
        # 移除标签
        if tag_to_remove in tag_list:
            tag_list.remove(tag_to_remove)
            job['标签'] = ', '.join(tag_list) if tag_list else ''
            
            # 保存
            if self._save_job_list():
                return {
                    'success': True,
                    'message': f"标签已移除：{tag_to_remove}",
                    'job': job
                }
            else:
                return {
                    'success': False,
                    'message': "移除标签完成但保存失败",
                    'job': job
                }
        else:
            return {
                'success': False,
                'message': f"标签不存在：{tag_to_remove}",
                'job': job
            }
    
    def update_title(self, job_key: str, new_title: str) -> Dict:
        """
        更新工作标题
        
        Args:
            job_key: 工作的唯一标识
            new_title: 新标题
        
        Returns:
            Dict: 更新结果
        """
        return self.update_job(job_key, {'标题': new_title})
    
    def update_title_by_index(self, index: int, new_title: str) -> Dict:
        """
        根据索引更新工作标题
        
        Args:
            index: 工作索引
            new_title: 新标题
        
        Returns:
            Dict: 更新结果
        """
        return self.update_job_by_index(index, {'标题': new_title})
    
    def search(self, keyword: str = None, title: str = None, tag: str = None, case_sensitive: bool = False, include_deleted: bool = False) -> List[Dict]:
        """
        搜索工作
        
        Args:
            keyword: 通用关键词（默认同时搜索标题和标签）
            title: 标题关键词（部分匹配，如果提供 keyword 则忽略）
            tag: 标签关键词（部分匹配，如果提供 keyword 则忽略）
            case_sensitive: 是否区分大小写（默认：False）
        
        Returns:
            List[Dict]: 匹配的工作列表
        """
        results = []
        
        # 如果提供了 keyword，默认同时搜索标题和标签
        if keyword:
            title = keyword
            tag = keyword
        
        # 如果既没有 keyword 也没有 title 和 tag，返回空列表
        if not title and not tag:
            return results
        
        for job in self.jobs:
            match = False
            
            # 判断是否使用 keyword（即 title 和 tag 相同，表示是 keyword 模式）
            is_keyword_mode = (keyword and title == keyword and tag == keyword)
            
            if is_keyword_mode:
                # keyword 模式：OR 逻辑（标题或标签包含即可）
                job_title = job.get('标题', '')
                job_tags = job.get('标签', '')
                if not case_sensitive:
                    job_title = job_title.lower()
                    job_tags = job_tags.lower()
                    keyword_lower = keyword.lower()
                else:
                    keyword_lower = keyword
                match = (keyword_lower in job_title) or (keyword_lower in job_tags)
            else:
                # 精确模式：根据提供的参数决定逻辑
                if title and tag:
                    # 同时指定 title 和 tag：AND 逻辑（都需要匹配）
                    job_title = job.get('标题', '')
                    job_tags = job.get('标签', '')
                    if not case_sensitive:
                        job_title = job_title.lower()
                        job_tags = job_tags.lower()
                        title_lower = title.lower()
                        tag_lower = tag.lower()
                    else:
                        title_lower = title
                        tag_lower = tag
                    match = (title_lower in job_title) and (tag_lower in job_tags)
                else:
                    # 只指定 title 或 tag：分别匹配
                    if title:
                        job_title = job.get('标题', '')
                        if not case_sensitive:
                            job_title = job_title.lower()
                            title_lower = title.lower()
                        else:
                            title_lower = title
                        if title_lower in job_title:
                            match = True
                    
                    if tag:
                        job_tags = job.get('标签', '')
                        if not case_sensitive:
                            job_tags = job_tags.lower()
                            tag_lower = tag.lower()
                        else:
                            tag_lower = tag
                        if tag_lower in job_tags:
                            match = True
            
            if match:
                # 根据include_deleted参数决定是否包含已删除的工作
                if include_deleted or not job.get('已删除', False):
                    results.append(job)
        
        return results
    
    def search_by_title(self, title: str, case_sensitive: bool = False) -> List[Dict]:
        """
        根据标题搜索工作
        
        Args:
            title: 标题关键词
            case_sensitive: 是否区分大小写
        
        Returns:
            List[Dict]: 匹配的工作列表
        """
        return self.search(title=title, case_sensitive=case_sensitive)
    
    def search_by_tag(self, tag: str, case_sensitive: bool = False) -> List[Dict]:
        """
        根据标签搜索工作
        
        Args:
            tag: 标签关键词
            case_sensitive: 是否区分大小写
        
        Returns:
            List[Dict]: 匹配的工作列表
        """
        return self.search(tag=tag, case_sensitive=case_sensitive)
    
    def soft_delete(self, job_key: str) -> Dict:
        """
        软删除工作（标记为已删除，不真正删除）
        
        Args:
            job_key: 工作的唯一标识（链接或标题+时间）
        
        Returns:
            Dict: 删除结果 {'success': bool, 'message': str, 'job': Dict}
        """
        job = self.find_job(job_key, include_deleted=True)
        if not job:
            return {
                'success': False,
                'message': f"未找到工作（key: {job_key[:50]}...）",
                'job': None
            }
        
        # 检查是否已经删除
        if job.get('已删除', False):
            return {
                'success': False,
                'message': "工作已经被删除",
                'job': job
            }
        
        # 标记为已删除，并记录删除时间
        job['已删除'] = True
        job['删除时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存
        if self._save_job_list():
            return {
                'success': True,
                'message': "工作已删除（软删除）",
                'job': job
            }
        else:
            return {
                'success': False,
                'message': "删除完成但保存失败",
                'job': job
            }
    
    def soft_delete_by_index(self, index: int) -> Dict:
        """
        根据索引软删除工作
        
        Args:
            index: 工作索引（基于未删除的列表）
        
        Returns:
            Dict: 删除结果
        """
        job = self.find_job_by_index(index, include_deleted=False)
        if not job:
            return {
                'success': False,
                'message': f"索引无效：{index}",
                'job': None
            }
        
        job_key = self._get_job_key(job)
        return self.soft_delete(job_key)
    
    def restore_deleted(self, job_key: str) -> Dict:
        """
        恢复已删除的工作
        
        Args:
            job_key: 工作的唯一标识（链接或标题+时间）
        
        Returns:
            Dict: 恢复结果 {'success': bool, 'message': str, 'job': Dict}
        """
        job = self.find_job(job_key, include_deleted=True)
        if not job:
            return {
                'success': False,
                'message': f"未找到工作（key: {job_key[:50]}...）",
                'job': None
            }
        
        # 检查是否已删除
        if not job.get('已删除', False):
            return {
                'success': False,
                'message': "工作未被删除，无需恢复",
                'job': job
            }
        
        # 恢复工作
        job['已删除'] = False
        if '删除时间' in job:
            del job['删除时间']
        
        # 保存
        if self._save_job_list():
            return {
                'success': True,
                'message': "工作已恢复",
                'job': job
            }
        else:
            return {
                'success': False,
                'message': "恢复完成但保存失败",
                'job': job
            }
    
    def restore_deleted_by_index(self, index: int) -> Dict:
        """
        根据索引恢复已删除的工作（基于已删除的列表）
        
        Args:
            index: 工作索引（基于已删除的列表）
        
        Returns:
            Dict: 恢复结果
        """
        deleted_jobs = [job for job in self.jobs if job.get('已删除', False)]
        if 0 <= index < len(deleted_jobs):
            job = deleted_jobs[index]
            job_key = self._get_job_key(job)
            return self.restore_deleted(job_key)
        else:
            return {
                'success': False,
                'message': f"索引无效：{index}（有效范围：0-{len(deleted_jobs)-1}）",
                'job': None
            }
    
    def backup(self, backup_dir: str = None) -> Dict:
        """
        备份工作列表文件
        
        Args:
            backup_dir: 备份目录路径（默认：job-manager-data）
        
        Returns:
            Dict: 备份结果 {'success': bool, 'message': str, 'backup_path': str}
        """
        if backup_dir is None:
            # 默认备份目录：与 job_list_file 同目录下的 job-manager-data
            base_dir = os.path.dirname(self.job_list_file)
            backup_dir = os.path.join(base_dir, 'job-manager-data')
        
        # 创建备份目录（如果不存在）
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            return {
                'success': False,
                'message': f"创建备份目录失败：{str(e)}",
                'backup_path': None
            }
        
        # 生成备份文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"job_list_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制文件
        try:
            if os.path.exists(self.job_list_file):
                shutil.copy2(self.job_list_file, backup_path)
                return {
                    'success': True,
                    'message': f"备份成功",
                    'backup_path': backup_path
                }
            else:
                return {
                    'success': False,
                    'message': f"源文件不存在：{self.job_list_file}",
                    'backup_path': None
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"备份失败：{str(e)}",
                'backup_path': None
            }


def load_job_from_csv(job_list_file: str, csv_file_path: str) -> Dict:
    """
    从 CSV 文件加载数据到工作列表（便捷函数）
    
    Args:
        job_list_file: 工作列表文件路径
        csv_file_path: CSV 文件路径
    
    Returns:
        Dict: 加载结果
    """
    manager = JobManager(job_list_file)
    return manager.load_from_csv(csv_file_path)


def list_jobs(job_list_file: str, limit: int = None) -> List[Dict]:
    """
    获取工作列表（便捷函数）
    
    Args:
        job_list_file: 工作列表文件路径
        limit: 限制返回的数量
    
    Returns:
        List[Dict]: 工作列表
    """
    manager = JobManager(job_list_file)
    return manager.list_jobs(limit)


def get_job_stats(job_list_file: str) -> Dict:
    """
    获取工作列表统计信息（便捷函数）
    
    Args:
        job_list_file: 工作列表文件路径
    
    Returns:
        Dict: 统计信息
    """
    manager = JobManager(job_list_file)
    return manager.get_stats()


# ============================================================================
# CLI 命令函数（从 texteditor_cli.py 移动过来）
# ============================================================================

def cmd_job_load(job_list_file: str, csv_file_path: str) -> bool:
    """从 CSV 文件加载数据到工作列表（CLI命令）"""
    manager = JobManager(job_list_file)
    result = manager.load_from_csv(csv_file_path)
    
    if result['success']:
        print("=" * 60)
        print("加载结果")
        print("=" * 60)
        print(f"状态：成功")
        print(f"文件：{csv_file_path}")
        print(f"新增：{result['added']} 条")
        print(f"跳过（重复）：{result['skipped']} 条")
        print(f"总计：{result['total']} 条")
        
        # 显示统计信息
        stats = manager.get_stats()
        print(f"\n工作列表统计：")
        print(f"  总工作数：{stats['total_jobs']}")
        print(f"  已加载 CSV 文件数：{stats['csv_files_count']}")
        return True
    else:
        print(f"错误：{result['message']}")
        return False


def cmd_job_list(job_list_file: str, limit: int = None, include_deleted: bool = False) -> bool:
    """显示工作列表（CLI命令）"""
    manager = JobManager(job_list_file)
    jobs = manager.list_jobs(limit, include_deleted=include_deleted)
    stats = manager.get_stats()
    
    print("=" * 60)
    print("工作列表")
    print("=" * 60)
    print(f"总工作数：{stats['total_jobs']}")
    print(f"活跃工作数：{stats['active_jobs']}")
    if stats['deleted_jobs'] > 0:
        print(f"已删除工作数：{stats['deleted_jobs']}（使用 --include-deleted 查看）")
    print(f"已加载 CSV 文件数：{stats['csv_files_count']}")
    
    if stats['csv_files_count'] > 0:
        print(f"\n已加载的 CSV 文件：")
        for i, csv_file in enumerate(stats['csv_files'], 1):
            print(f"  {i}. {csv_file}")
    
    if len(jobs) == 0:
        print("\n工作列表为空")
        return True
    
    display_jobs = jobs if limit is None else jobs[:limit]
    print(f"\n工作列表（显示 {len(display_jobs)} 条）：")
    print("-" * 60)
    
    for i, job in enumerate(display_jobs, 0):
        print(f"\n[{i}] {job.get('标题', '无标题')}")
        if job.get('链接'):
            link = job['链接']
            print(f"    链接：{link}")
        if job.get('时间'):
            print(f"    时间：{job['时间']}")
        if job.get('标签'):
            print(f"    标签：{job['标签']}")
        if job.get('摘要'):
            summary = job['摘要']
            # 如果摘要包含换行符，格式化显示
            if '\n' in summary:
                print(f"    摘要：")
                for line in summary.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    摘要：{summary}")
        if job.get('阅读次数'):
            print(f"    阅读次数：{job['阅读次数']}")
    
    if limit and len(jobs) > limit:
        print(f"\n... (还有 {len(jobs) - limit} 条未显示)")
    
    return True


def cmd_job_backup(job_list_file: str, backup_dir: str = None) -> bool:
    """备份工作列表文件（CLI命令）"""
    import os
    manager = JobManager(job_list_file)
    result = manager.backup(backup_dir)
    
    print("=" * 60)
    print("备份工作列表")
    print("=" * 60)
    
    if result['success']:
        print(f"[OK] {result['message']}")
        print(f"备份路径：{result['backup_path']}")
        
        # 显示备份文件信息
        if os.path.exists(result['backup_path']):
            file_size = os.path.getsize(result['backup_path'])
            print(f"备份文件大小：{file_size} 字节")
        
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_job_search(job_list_file: str, keyword: str = None, title: str = None, tag: str = None, case_sensitive: bool = False) -> bool:
    """搜索工作（CLI命令）"""
    manager = JobManager(job_list_file)
    
    # 优先使用位置参数 keyword，如果没有则使用 --keyword
    search_keyword = keyword if keyword else None
    
    # 如果提供了 keyword（位置参数或 --keyword），默认同时搜索标题和标签
    if search_keyword:
        results = manager.search(keyword=search_keyword, case_sensitive=case_sensitive)
        search_type = "标题和标签"
    elif title and tag:
        results = manager.search(title=title, tag=tag, case_sensitive=case_sensitive)
        search_type = "标题和标签（AND）"
    elif title:
        results = manager.search(title=title, case_sensitive=case_sensitive)
        search_type = "标题"
    elif tag:
        results = manager.search(tag=tag, case_sensitive=case_sensitive)
        search_type = "标签"
    else:
        print("错误：请提供搜索关键词或指定搜索条件（--title 或 --tag）")
        print("用法示例：")
        print("  python texteditor_cli.py job search \"量化\"")
        print("  python texteditor_cli.py job search --title \"量化\"")
        print("  python texteditor_cli.py job search --tag \"工作\"")
        return False
    
    print("=" * 60)
    print("搜索结果")
    print("=" * 60)
    
    if keyword:
        print(f"搜索关键词：{keyword}（在标题和标签中搜索）")
    else:
        if title:
            print(f"标题关键词：{title}")
        if tag:
            print(f"标签关键词：{tag}")
    print(f"搜索范围：{search_type}")
    print(f"匹配数量：{len(results)}")
    print("-" * 60)
    
    if len(results) == 0:
        print("未找到匹配的工作")
        return True
    
    # 显示搜索结果
    for i, job in enumerate(results, 1):
        print(f"\n[{i}] {job.get('标题', '无标题')}")
        if job.get('链接'):
            link = job['链接']
            print(f"    链接：{link}")
        if job.get('时间'):
            print(f"    时间：{job['时间']}")
        if job.get('标签'):
            print(f"    标签：{job['标签']}")
        if job.get('摘要'):
            summary = job['摘要']
            # 如果摘要包含换行符，格式化显示
            if '\n' in summary:
                print(f"    摘要：")
                for line in summary.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    摘要：{summary}")
        if job.get('阅读次数'):
            print(f"    阅读次数：{job['阅读次数']}")
    
    return True


def cmd_job_edit(job_list_file: str, index: int = None, job_key: str = None, field: str = None, value: str = None, 
                 add_tag: str = None, remove_tag: str = None, summary: str = None, summary_from_file: str = None) -> bool:
    """编辑工作信息（CLI命令）"""
    import os
    manager = JobManager(job_list_file)
    
    # 确定要编辑的工作
    if index is not None:
        job = manager.find_job_by_index(index)
        if not job:
            print(f"错误：索引 {index} 无效（有效范围：0-{len(manager.jobs)-1}）")
            return False
        job_key = manager._get_job_key(job)
    elif not job_key:
        print("错误：请提供索引（--index）或工作标识（--key）")
        return False
    
    # 显示当前工作信息
    job = manager.find_job(job_key)
    if not job:
        print(f"错误：未找到工作")
        return False
    
    # 先验证参数，再显示信息（避免显示旧值造成混淆）
    # 如果是设置摘要操作，先检查参数
    if summary is not None or summary_from_file:
        # 先验证参数
        if summary_from_file:
            if not os.path.exists(summary_from_file):
                print(f"[ERROR] 文件不存在：{summary_from_file}")
                return False
        elif summary is None:
            print("[ERROR] 请提供摘要内容（--summary 或 --summary-from-file）")
            return False
        elif summary == "$value":
            print(f"[ERROR] 检测到未展开的变量 '$value'")
            print(f"  可能的原因：")
            print(f"  1. PowerShell变量未定义或不在作用域内")
            print(f"  2. 变量展开失败")
            print(f"  解决方案：")
            print(f"  - 确保变量已定义：`$value = \"你的摘要内容\"")
            print(f"  - 或者直接使用值：--summary \"你的摘要内容\"")
            return False
    
    print("=" * 60)
    print("编辑工作")
    print("=" * 60)
    print(f"当前信息：")
    print(f"  标题：{job.get('标题', '无')}")
    print(f"  标签：{job.get('标签', '无')}")
    print(f"  时间：{job.get('时间', '无')}")
    if job.get('摘要'):
        old_summary = job['摘要']
        if '\n' in old_summary:
            print(f"  摘要：")
            for line in old_summary.split('\n'):
                print(f"    {line}")
        else:
            print(f"  摘要：{old_summary}")
    print("-" * 60)
    
    # 执行编辑操作
    if add_tag:
        result = manager.add_tag(job_key, add_tag)
        if result['success']:
            print(f"[OK] {result['message']}")
            print(f"  新标签：{result['job'].get('标签', '无')}")
        else:
            print(f"[ERROR] {result['message']}")
        return result['success']
    
    elif remove_tag:
        result = manager.remove_tag(job_key, remove_tag)
        if result['success']:
            print(f"[OK] {result['message']}")
            print(f"  新标签：{result['job'].get('标签', '无')}")
        else:
            print(f"[ERROR] {result['message']}")
        return result['success']
    
    elif summary is not None or summary_from_file:
        # 处理摘要：支持多行输入
        if summary_from_file:
            # 如果指定了从文件读取，则从文件读取
            try:
                with open(summary_from_file, 'r', encoding='utf-8') as f:
                    summary_value = f.read()
            except Exception as e:
                print(f"[ERROR] 读取摘要文件失败：{str(e)}")
                return False
        elif summary is not None:
            summary_value = summary
        else:
            print("[ERROR] 请提供摘要内容（--summary 或 --summary-from-file）")
            return False
        
        # 检查接收到的值是否有效
        if summary_value is None:
            print(f"[ERROR] 摘要值为None，参数可能未正确传递")
            print(f"  请确保使用引号包裹包含空格的值：--summary \"你的摘要内容\"")
            return False
        
        if summary_value == "$value":
            print(f"[ERROR] 摘要值异常：'{summary_value}'，这可能是之前的错误值")
            print(f"  请使用引号包裹参数值：--summary \"你的摘要内容\"")
            return False
        
        # 将\n转换为实际的换行符（如果用户输入的是\n字符串）
        summary_value = summary_value.replace('\\n', '\n')
        
        result = manager.update_job(job_key, {'摘要': summary_value})
        if result['success']:
            print(f"[OK] {result['message']}")
            updated_summary = result['job'].get('摘要', '无')
            if '\n' in updated_summary:
                print(f"  更新后的摘要：")
                for line in updated_summary.split('\n'):
                    print(f"    {line}")
            else:
                print(f"  更新后的摘要：{updated_summary}")
        else:
            print(f"[ERROR] {result['message']}")
        return result['success']
    
    elif field and value:
        result = manager.update_job(job_key, {field: value})
        if result['success']:
            print(f"[OK] {result['message']}")
            print(f"  更新后的 {field}：{result['job'].get(field, '无')}")
        else:
            print(f"[ERROR] {result['message']}")
        return result['success']
    
    else:
        print("错误：请指定编辑操作（--field 和 --value，或 --summary，或 --add-tag，或 --remove-tag）")
        return False


def cmd_job_delete(job_list_file: str, index: int = None, job_key: str = None) -> bool:
    """软删除工作（CLI命令）"""
    manager = JobManager(job_list_file)
    
    # 确定要删除的工作
    if index is not None:
        result = manager.soft_delete_by_index(index)
    elif job_key:
        result = manager.soft_delete(job_key)
    else:
        print("错误：请提供索引（--index）或工作标识（--key）")
        return False
    
    if result['success']:
        print("=" * 60)
        print("删除工作")
        print("=" * 60)
        print(f"[OK] {result['message']}")
        job = result['job']
        print(f"  已删除的工作：{job.get('标题', '无标题')}")
        if job.get('删除时间'):
            print(f"  删除时间：{job['删除时间']}")
        print(f"\n提示：使用 'job restore --index <索引>' 可以恢复已删除的工作")
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_job_restore(job_list_file: str, index: int = None, job_key: str = None) -> bool:
    """恢复已删除的工作（CLI命令）"""
    manager = JobManager(job_list_file)
    
    # 确定要恢复的工作
    if index is not None:
        result = manager.restore_deleted_by_index(index)
    elif job_key:
        result = manager.restore_deleted(job_key)
    else:
        print("错误：请提供索引（--index）或工作标识（--key）")
        print("提示：使用 'job list-deleted' 查看已删除的工作列表")
        return False
    
    if result['success']:
        print("=" * 60)
        print("恢复工作")
        print("=" * 60)
        print(f"[OK] {result['message']}")
        job = result['job']
        print(f"  已恢复的工作：{job.get('标题', '无标题')}")
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_job_list_deleted(job_list_file: str, limit: int = None) -> bool:
    """显示已删除的工作列表（CLI命令）"""
    manager = JobManager(job_list_file)
    deleted_jobs = [job for job in manager.jobs if job.get('已删除', False)]
    stats = manager.get_stats()
    
    print("=" * 60)
    print("已删除的工作列表")
    print("=" * 60)
    print(f"已删除工作数：{stats['deleted_jobs']}")
    
    if len(deleted_jobs) == 0:
        print("\n没有已删除的工作")
        return True
    
    display_jobs = deleted_jobs if limit is None else deleted_jobs[:limit]
    print(f"\n已删除的工作列表（显示 {len(display_jobs)} 条）：")
    print("-" * 60)
    
    for i, job in enumerate(display_jobs, 1):
        print(f"\n[{i}] {job.get('标题', '无标题')} [已删除]")
        if job.get('链接'):
            link = job['链接']
            print(f"    链接：{link}")
        if job.get('时间'):
            print(f"    时间：{job['时间']}")
        if job.get('删除时间'):
            print(f"    删除时间：{job['删除时间']}")
        if job.get('标签'):
            print(f"    标签：{job['标签']}")
        if job.get('摘要'):
            summary = job['摘要']
            if '\n' in summary:
                print(f"    摘要：")
                for line in summary.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    摘要：{summary}")
    
    if limit and len(deleted_jobs) > limit:
        print(f"\n... (还有 {len(deleted_jobs) - limit} 条未显示)")
    
    print(f"\n提示：使用 'job restore --index <索引>' 可以恢复工作")
    return True

