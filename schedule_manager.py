#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
排期管理工具
管理时间段、任务和完成情况
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ScheduleManager:
    """排期管理器"""
    
    def __init__(self, schedule_file: str):
        """
        初始化排期管理器
        
        Args:
            schedule_file: 排期文件路径（JSON 格式）
        """
        self.schedule_file = schedule_file
        self.schedules = []  # 排期列表数据
        
        # 加载已有的排期列表
        self._load_schedules()
    
    def _load_schedules(self):
        """从文件加载排期列表"""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.schedules = data.get('schedules', [])
            except Exception as e:
                print(f"加载排期列表失败：{str(e)}")
                self.schedules = []
        else:
            self.schedules = []
    
    def _save_schedules(self):
        """保存排期列表到文件"""
        try:
            data = {
                'schedules': self.schedules
            }
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存排期列表失败：{str(e)}")
            return False
    
    def add_schedule(self, start_time: str, end_time: str, task: str, 
                     status: str = "未完成", description: str = "", value: str = "") -> Dict:
        """
        添加排期
        
        Args:
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM 或 YYYY-MM-DD）
            end_time: 结束时间（格式：YYYY-MM-DD HH:MM 或 YYYY-MM-DD）
            task: 任务描述
            status: 完成情况（默认：未完成，可选：已完成、进行中、未完成）
            description: 详细描述（可选）
            value: 意义/价值（可选，用于激励自己）
        
        Returns:
            Dict: 添加结果 {'success': bool, 'message': str, 'schedule': Dict}
        """
        try:
            # 验证时间格式
            try:
                if len(start_time) == 10:  # YYYY-MM-DD
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d")
                else:  # YYYY-MM-DD HH:MM
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                
                if len(end_time) == 10:  # YYYY-MM-DD
                    end_dt = datetime.strptime(end_time, "%Y-%m-%d")
                else:  # YYYY-MM-DD HH:MM
                    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                
                if end_dt < start_dt:
                    return {
                        'success': False,
                        'message': "结束时间不能早于开始时间",
                        'schedule': None
                    }
            except ValueError as e:
                return {
                    'success': False,
                    'message': f"时间格式错误：{str(e)}（支持格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）",
                    'schedule': None
                }
            
            # 验证状态
            valid_statuses = ["已完成", "进行中", "未完成", "搁置", "延期"]
            if status not in valid_statuses:
                return {
                    'success': False,
                    'message': f"状态无效：{status}（有效值：{', '.join(valid_statuses)}）",
                    'schedule': None
                }
            
            # 生成ID（如果没有ID，则使用当前最大ID+1）
            max_id = -1
            for s in self.schedules:
                if s.get('id') is not None and s.get('id') > max_id:
                    max_id = s.get('id')
            new_id = max_id + 1
            
            # 创建排期对象
            schedule = {
                'id': new_id,
                '开始时间': start_time,
                '结束时间': end_time,
                '任务': task,
                '完成情况': status,
                '描述': description,
                '意义': value,
                '创建时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.schedules.append(schedule)
            
            if self._save_schedules():
                return {
                    'success': True,
                    'message': "添加排期成功",
                    'schedule': schedule
                }
            else:
                return {
                    'success': False,
                    'message': "添加排期成功但保存失败",
                    'schedule': schedule
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"添加排期失败：{str(e)}",
                'schedule': None
            }
    
    def list_schedules(self, limit: int = None, status: str = None, 
                      start_date: str = None, end_date: str = None, 
                      include_deleted: bool = False) -> List[Dict]:
        """
        获取排期列表
        
        Args:
            limit: 限制返回的数量
            status: 按状态筛选（已完成、进行中、未完成、搁置、延期）
            start_date: 筛选开始日期之后（YYYY-MM-DD）
            end_date: 筛选结束日期之前（YYYY-MM-DD）
            include_deleted: 是否包含已软删除的排期（默认：False）
        
        Returns:
            List[Dict]: 排期列表
        """
        filtered = self.schedules.copy()
        
        # 过滤已删除的排期（除非明确要求包含）
        if not include_deleted:
            filtered = [s for s in filtered if not s.get('已删除', False)]
        
        # 按状态筛选
        if status:
            filtered = [s for s in filtered if s.get('完成情况') == status]
        
        # 按日期范围筛选
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                filtered = [s for s in filtered if 
                           datetime.strptime(s.get('开始时间', '')[:10], "%Y-%m-%d") >= start_dt]
            except:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                filtered = [s for s in filtered if 
                           datetime.strptime(s.get('结束时间', '')[:10], "%Y-%m-%d") <= end_dt]
            except:
                pass
        
        # 按开始时间排序
        try:
            filtered.sort(key=lambda s: datetime.strptime(s.get('开始时间', ''), 
                         "%Y-%m-%d" if len(s.get('开始时间', '')) == 10 else "%Y-%m-%d %H:%M"))
        except:
            pass
        
        if limit:
            return filtered[:limit]
        return filtered
    
    def find_schedule_by_id(self, schedule_id: int) -> Optional[Dict]:
        """
        根据ID查找排期
        
        Args:
            schedule_id: 排期ID
        
        Returns:
            Dict: 找到的排期字典，如果未找到返回 None
        """
        for schedule in self.schedules:
            if schedule.get('id') == schedule_id:
                return schedule
        return None
    
    def find_schedule_by_index(self, index: int) -> Optional[Dict]:
        """
        根据索引查找排期（在列表中的位置）
        
        Args:
            index: 索引（从0开始）
        
        Returns:
            Dict: 找到的排期字典，如果未找到返回 None
        """
        active_schedules = self.list_schedules()
        if 0 <= index < len(active_schedules):
            return active_schedules[index]
        return None
    
    def update_schedule(self, schedule_id: int = None, index: int = None,
                       start_time: str = None, end_time: str = None,
                       task: str = None, status: str = None, 
                       description: str = None, value: str = None) -> Dict:
        """
        更新排期信息
        
        Args:
            schedule_id: 排期ID（与 index 二选一）
            index: 排期索引（与 schedule_id 二选一）
            start_time: 新的开始时间
            end_time: 新的结束时间
            task: 新的任务描述
            status: 新的完成情况
            description: 新的描述
            value: 新的意义/价值
        
        Returns:
            Dict: 更新结果 {'success': bool, 'message': str, 'schedule': Dict}
        """
        # 查找排期
        schedule = None
        if schedule_id is not None:
            schedule = self.find_schedule_by_id(schedule_id)
        elif index is not None:
            schedule = self.find_schedule_by_index(index)
        
        if not schedule:
            return {
                'success': False,
                'message': "未找到指定的排期",
                'schedule': None
            }
        
        # 更新字段
        updated = False
        
        if start_time is not None:
            try:
                if len(start_time) == 10:
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d")
                else:
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                
                # 验证结束时间是否仍然有效
                end_time_check = schedule.get('结束时间')
                if end_time_check:
                    if len(end_time_check) == 10:
                        end_dt = datetime.strptime(end_time_check, "%Y-%m-%d")
                    else:
                        end_dt = datetime.strptime(end_time_check, "%Y-%m-%d %H:%M")
                    if end_dt < start_dt:
                        return {
                            'success': False,
                            'message': "结束时间不能早于开始时间",
                            'schedule': None
                        }
                
                schedule['开始时间'] = start_time
                updated = True
            except ValueError as e:
                return {
                    'success': False,
                    'message': f"开始时间格式错误：{str(e)}",
                    'schedule': None
                }
        
        if end_time is not None:
            try:
                if len(end_time) == 10:
                    end_dt = datetime.strptime(end_time, "%Y-%m-%d")
                else:
                    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                
                # 验证开始时间是否仍然有效
                start_time_check = schedule.get('开始时间')
                if start_time_check:
                    if len(start_time_check) == 10:
                        start_dt = datetime.strptime(start_time_check, "%Y-%m-%d")
                    else:
                        start_dt = datetime.strptime(start_time_check, "%Y-%m-%d %H:%M")
                    if end_dt < start_dt:
                        return {
                            'success': False,
                            'message': "结束时间不能早于开始时间",
                            'schedule': None
                        }
                
                schedule['结束时间'] = end_time
                updated = True
            except ValueError as e:
                return {
                    'success': False,
                    'message': f"结束时间格式错误：{str(e)}",
                    'schedule': None
                }
        
        if task is not None:
            schedule['任务'] = task
            updated = True
        
        if status is not None:
            valid_statuses = ["已完成", "进行中", "未完成", "搁置", "延期"]
            if status not in valid_statuses:
                return {
                    'success': False,
                    'message': f"状态无效：{status}（有效值：{', '.join(valid_statuses)}）",
                    'schedule': None
                }
            schedule['完成情况'] = status
            updated = True
        
        if description is not None:
            schedule['描述'] = description
            updated = True
        
        if value is not None:
            schedule['意义'] = value
            updated = True
        
        if updated:
            if self._save_schedules():
                return {
                    'success': True,
                    'message': "更新排期成功",
                    'schedule': schedule
                }
            else:
                return {
                    'success': False,
                    'message': "更新排期成功但保存失败",
                    'schedule': schedule
                }
        else:
            return {
                'success': False,
                'message': "没有提供要更新的字段",
                'schedule': schedule
            }
    
    def delete_schedule(self, schedule_id: int = None, index: int = None) -> Dict:
        """
        删除排期（硬删除）
        
        Args:
            schedule_id: 排期ID（与 index 二选一）
            index: 排期索引（与 schedule_id 二选一）
        
        Returns:
            Dict: 删除结果 {'success': bool, 'message': str}
        """
        # 查找排期
        schedule = None
        if schedule_id is not None:
            schedule = self.find_schedule_by_id(schedule_id)
        elif index is not None:
            schedule = self.find_schedule_by_index(index)
        
        if not schedule:
            return {
                'success': False,
                'message': "未找到指定的排期"
            }
        
        try:
            self.schedules.remove(schedule)
            if self._save_schedules():
                return {
                    'success': True,
                    'message': "删除排期成功"
                }
            else:
                return {
                    'success': False,
                    'message': "删除排期成功但保存失败"
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"删除排期失败：{str(e)}"
            }
    
    def soft_delete_schedule(self, schedule_id: int = None, index: int = None) -> Dict:
        """
        软删除排期（标记为已删除）
        
        Args:
            schedule_id: 排期ID（与 index 二选一）
            index: 排期索引（与 schedule_id 二选一）
        
        Returns:
            Dict: 删除结果 {'success': bool, 'message': str}
        """
        # 查找排期
        schedule = None
        if schedule_id is not None:
            schedule = self.find_schedule_by_id(schedule_id)
        elif index is not None:
            schedule = self.find_schedule_by_index(index)
        
        if not schedule:
            return {
                'success': False,
                'message': "未找到指定的排期"
            }
        
        try:
            schedule['已删除'] = True
            if self._save_schedules():
                return {
                    'success': True,
                    'message': "软删除排期成功"
                }
            else:
                return {
                    'success': False,
                    'message': "软删除排期成功但保存失败"
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"软删除排期失败：{str(e)}"
            }
    
    def soft_delete_future_schedules(self) -> Dict:
        """
        软删除所有未来的排期（未软删除的）
        
        Returns:
            Dict: 删除结果 {'success': bool, 'message': str, 'count': int}
        """
        now = datetime.now()
        deleted_count = 0
        
        try:
            for schedule in self.schedules:
                if schedule.get('已删除', False):
                    continue
                
                # 解析结束时间
                end_time_str = schedule.get('结束时间', '')
                try:
                    if len(end_time_str) == 10:
                        end_dt = datetime.strptime(end_time_str, "%Y-%m-%d")
                    else:
                        end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                    
                    # 如果结束时间在未来，软删除
                    if end_dt > now:
                        schedule['已删除'] = True
                        deleted_count += 1
                except:
                    pass
            
            if self._save_schedules():
                return {
                    'success': True,
                    'message': f"成功软删除 {deleted_count} 个未来排期",
                    'count': deleted_count
                }
            else:
                return {
                    'success': False,
                    'message': "软删除成功但保存失败",
                    'count': deleted_count
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"软删除失败：{str(e)}",
                'count': 0
            }
    
    def get_future_schedules(self) -> List[Dict]:
        """
        获取所有未来的排期（未软删除的）
        
        Returns:
            List[Dict]: 未来排期列表
        """
        now = datetime.now()
        future_schedules = []
        
        for schedule in self.schedules:
            if schedule.get('已删除', False):
                continue
            
            # 解析开始时间
            start_time_str = schedule.get('开始时间', '')
            try:
                if len(start_time_str) == 10:
                    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d")
                else:
                    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                
                # 如果开始时间在未来，加入列表
                if start_dt > now:
                    future_schedules.append(schedule)
            except:
                pass
        
        # 按开始时间排序
        try:
            future_schedules.sort(key=lambda s: datetime.strptime(s.get('开始时间', ''), 
                         "%Y-%m-%d" if len(s.get('开始时间', '')) == 10 else "%Y-%m-%d %H:%M"))
        except:
            pass
        
        return future_schedules
    
    def get_in_progress_schedules(self) -> List[Dict]:
        """
        获取正在进行的排期（当前时间在开始时间和结束时间之间）
        
        Returns:
            List[Dict]: 正在进行的排期列表
        """
        now = datetime.now()
        in_progress = []
        
        for schedule in self.schedules:
            if schedule.get('已删除', False):
                continue
            
            # 解析时间
            start_time_str = schedule.get('开始时间', '')
            end_time_str = schedule.get('结束时间', '')
            try:
                if len(start_time_str) == 10:
                    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d")
                else:
                    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                
                if len(end_time_str) == 10:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d")
                else:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                
                # 如果当前时间在开始时间和结束时间之间
                if start_dt <= now <= end_dt:
                    in_progress.append(schedule)
            except:
                pass
        
        # 按开始时间排序
        try:
            in_progress.sort(key=lambda s: datetime.strptime(s.get('开始时间', ''), 
                         "%Y-%m-%d" if len(s.get('开始时间', '')) == 10 else "%Y-%m-%d %H:%M"))
        except:
            pass
        
        return in_progress
    
    def get_expired_schedules(self) -> List[Dict]:
        """
        获取已过期的排期（结束时间 < 当前时间，且状态不是"已完成"）
        
        Returns:
            List[Dict]: 已过期的排期列表
        """
        now = datetime.now()
        expired = []
        
        for schedule in self.schedules:
            if schedule.get('已删除', False):
                continue
            
            # 只检查未完成的任务
            status = schedule.get('完成情况', '未完成')
            if status == '已完成':
                continue
            
            # 解析结束时间
            end_time_str = schedule.get('结束时间', '')
            try:
                if len(end_time_str) == 10:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d")
                else:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                
                # 如果结束时间 < 当前时间
                if end_dt < now:
                    expired.append(schedule)
            except:
                pass
        
        # 按结束时间排序（最近的在前）
        try:
            expired.sort(key=lambda s: datetime.strptime(s.get('结束时间', ''), 
                         "%Y-%m-%d" if len(s.get('结束时间', '')) == 10 else "%Y-%m-%d %H:%M"), reverse=True)
        except:
            pass
        
        return expired
    
    def get_history_schedules(self, days: int = 7) -> List[Dict]:
        """
        获取历史排期（结束时间在当前时间之前，且在指定天数内）
        
        Args:
            days: 查询过去多少天内的历史排期（默认：7天）
        
        Returns:
            List[Dict]: 历史排期列表
        """
        now = datetime.now()
        history = []
        
        # 计算起始时间（当前时间往前推 days 天）
        start_time = now - timedelta(days=days)
        
        for schedule in self.schedules:
            if schedule.get('已删除', False):
                continue
            
            # 解析结束时间
            end_time_str = schedule.get('结束时间', '')
            try:
                if len(end_time_str) == 10:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d")
                else:
                    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                
                # 如果结束时间在当前时间之前，且在指定天数内
                if end_dt < now and end_dt >= start_time:
                    history.append(schedule)
            except:
                pass
        
        # 按结束时间排序（最近的在前）
        try:
            history.sort(key=lambda s: datetime.strptime(s.get('结束时间', ''), 
                         "%Y-%m-%d" if len(s.get('结束时间', '')) == 10 else "%Y-%m-%d %H:%M"), reverse=True)
        except:
            pass
        
        return history
    
    def extend_schedule(self, schedule_id: int = None, index: int = None, 
                       extension_minutes: float = None) -> Dict:
        """
        延期排期（延长结束时间，不插队）
        
        Args:
            schedule_id: 排期ID（与 index 二选一）
            index: 排期索引（与 schedule_id 二选一）
            extension_minutes: 延长的分钟数
        
        Returns:
            Dict: 延期结果 {'success': bool, 'message': str, 'schedule': Dict}
        """
        # 查找排期
        schedule = None
        if schedule_id is not None:
            schedule = self.find_schedule_by_id(schedule_id)
        elif index is not None:
            schedule = self.find_schedule_by_index(index)
        
        if not schedule:
            return {
                'success': False,
                'message': "未找到指定的排期",
                'schedule': None
            }
        
        if extension_minutes is None or extension_minutes <= 0:
            return {
                'success': False,
                'message': "延长时间必须大于0",
                'schedule': None
            }
        
        try:
            # 解析当前结束时间
            end_time_str = schedule.get('结束时间', '')
            if len(end_time_str) == 10:
                end_dt = datetime.strptime(end_time_str, "%Y-%m-%d")
            else:
                end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
            
            # 计算新的结束时间
            new_end_dt = end_dt + timedelta(minutes=extension_minutes)
            
            # 格式化新的结束时间
            if len(end_time_str) == 10:
                new_end_time_str = new_end_dt.strftime("%Y-%m-%d")
            else:
                new_end_time_str = new_end_dt.strftime("%Y-%m-%d %H:%M")
            
            # 更新排期
            schedule['结束时间'] = new_end_time_str
            schedule['完成情况'] = '延期'
            
            if self._save_schedules():
                return {
                    'success': True,
                    'message': f"延期成功，新的结束时间：{new_end_time_str}",
                    'schedule': schedule
                }
            else:
                return {
                    'success': False,
                    'message': "延期成功但保存失败",
                    'schedule': schedule
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"延期失败：{str(e)}",
                'schedule': None
            }
    
    def search(self, keyword: str = None, task: str = None, 
               description: str = None, value: str = None, case_sensitive: bool = False) -> List[Dict]:
        """
        搜索排期
        
        Args:
            keyword: 关键词（在任务、描述和意义/价值中搜索）
            task: 任务关键词
            description: 描述关键词
            value: 意义/价值关键词
            case_sensitive: 是否区分大小写（默认：False）
        
        Returns:
            List[Dict]: 匹配的排期列表
        """
        results = []
        
        for schedule in self.schedules:
            matched = False
            
            if keyword:
                # 在任务、描述和意义/价值中搜索
                task_text = schedule.get('任务', '')
                desc_text = schedule.get('描述', '')
                value_text = schedule.get('意义', '')
                
                if not case_sensitive:
                    keyword_lower = keyword.lower()
                    task_text = task_text.lower()
                    desc_text = desc_text.lower()
                    value_text = value_text.lower()
                
                if keyword in task_text or keyword in desc_text or keyword in value_text:
                    matched = True
            
            if task:
                task_text = schedule.get('任务', '')
                if not case_sensitive:
                    task_lower = task.lower()
                    task_text = task_text.lower()
                    if task_lower in task_text:
                        matched = True
                else:
                    if task in task_text:
                        matched = True
            
            if description:
                desc_text = schedule.get('描述', '')
                if not case_sensitive:
                    description_lower = description.lower()
                    desc_text = desc_text.lower()
                    if description_lower in desc_text:
                        matched = True
                else:
                    if description in desc_text:
                        matched = True
            
            if value:
                value_text = schedule.get('意义', '')
                if not case_sensitive:
                    value_lower = value.lower()
                    value_text = value_text.lower()
                    if value_lower in value_text:
                        matched = True
                else:
                    if value in value_text:
                        matched = True
            
            if matched:
                results.append(schedule)
        
        # 按开始时间排序
        try:
            results.sort(key=lambda s: datetime.strptime(s.get('开始时间', ''), 
                         "%Y-%m-%d" if len(s.get('开始时间', '')) == 10 else "%Y-%m-%d %H:%M"))
        except:
            pass
        
        return results
    
    def get_stats(self) -> Dict:
        """
        获取排期统计信息
        
        Returns:
            Dict: 统计信息
        """
        total = len(self.schedules)
        completed = len([s for s in self.schedules if s.get('完成情况') == '已完成'])
        in_progress = len([s for s in self.schedules if s.get('完成情况') == '进行中'])
        not_started = len([s for s in self.schedules if s.get('完成情况') == '未完成'])
        
        return {
            'total_schedules': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started
        }


# ============================================================================
# CLI 命令函数
# ============================================================================

def cmd_schedule_add(schedule_file: str, start_time: str, end_time: str, 
                     task: str, status: str = "未完成", description: str = "", value: str = "") -> bool:
    """添加排期（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    result = manager.add_schedule(start_time, end_time, task, status, description, value)
    
    print("=" * 60)
    print("添加排期")
    print("=" * 60)
    
    if result['success']:
        print(f"[OK] {result['message']}")
        schedule = result['schedule']
        print(f"\n排期信息：")
        print(f"  ID：{schedule.get('id')}")
        print(f"  时间段：{schedule.get('开始时间')} ~ {schedule.get('结束时间')}")
        print(f"  任务：{schedule.get('任务')}")
        print(f"  完成情况：{schedule.get('完成情况')}")
        if schedule.get('描述'):
            desc = schedule.get('描述')
            if '\n' in desc:
                print(f"  描述：")
                for line in desc.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  描述：{desc}")
        if schedule.get('意义'):
            val = schedule.get('意义')
            if '\n' in val:
                print(f"  意义/价值：")
                for line in val.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  意义/价值：{val}")
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_schedule_list(schedule_file: str, limit: int = None, status: str = None,
                     start_date: str = None, end_date: str = None) -> bool:
    """显示排期列表（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    schedules = manager.list_schedules(limit, status, start_date, end_date)
    stats = manager.get_stats()
    
    print("=" * 60)
    print("排期列表")
    print("=" * 60)
    print(f"总排期数：{stats['total_schedules']}")
    print(f"已完成：{stats['completed']}")
    print(f"进行中：{stats['in_progress']}")
    print(f"未完成：{stats['not_started']}")
    
    if len(schedules) == 0:
        print("\n排期列表为空")
        return True
    
    display_schedules = schedules if limit is None else schedules[:limit]
    print(f"\n排期列表（显示 {len(display_schedules)} 条）：")
    print("-" * 60)
    
    for schedule in display_schedules:
        schedule_id = schedule.get('id')
        print(f"\n[{schedule_id}] {schedule.get('任务', '无任务')}")
        print(f"    时间段：{schedule.get('开始时间')} ~ {schedule.get('结束时间')}")
        print(f"    完成情况：{schedule.get('完成情况')}")
        if schedule.get('描述'):
            desc = schedule.get('描述')
            if '\n' in desc:
                print(f"    描述：")
                for line in desc.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    描述：{desc}")
        if schedule.get('意义'):
            value = schedule.get('意义')
            if '\n' in value:
                print(f"    意义/价值：")
                for line in value.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    意义/价值：{value}")
        print(f"    创建时间：{schedule.get('创建时间', '未知')}")
    
    return True


def cmd_schedule_edit(schedule_file: str, schedule_id: int = None, index: int = None,
                     start_time: str = None, end_time: str = None,
                     task: str = None, status: str = None, 
                     description: str = None, value: str = None) -> bool:
    """编辑排期（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    
    # 先查找排期以显示当前信息
    schedule = None
    if schedule_id is not None:
        schedule = manager.find_schedule_by_id(schedule_id)
    elif index is not None:
        schedule = manager.find_schedule_by_index(index)
    
    if schedule:
        print("=" * 60)
        print("编辑排期")
        print("=" * 60)
        print("当前信息：")
        print(f"  时间段：{schedule.get('开始时间')} ~ {schedule.get('结束时间')}")
        print(f"  任务：{schedule.get('任务')}")
        print(f"  完成情况：{schedule.get('完成情况')}")
        if schedule.get('描述'):
            desc = schedule.get('描述')
            if '\n' in desc:
                print(f"  描述：")
                for line in desc.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  描述：{desc}")
        if schedule.get('意义'):
            val = schedule.get('意义')
            if '\n' in val:
                print(f"  意义/价值：")
                for line in val.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  意义/价值：{val}")
        print("-" * 60)
    
    result = manager.update_schedule(schedule_id, index, start_time, end_time, 
                                    task, status, description, value)
    
    if result['success']:
        print(f"[OK] {result['message']}")
        schedule = result['schedule']
        print(f"\n更新后的信息：")
        print(f"  时间段：{schedule.get('开始时间')} ~ {schedule.get('结束时间')}")
        print(f"  任务：{schedule.get('任务')}")
        print(f"  完成情况：{schedule.get('完成情况')}")
        if schedule.get('描述'):
            desc = schedule.get('描述')
            if '\n' in desc:
                print(f"  描述：")
                for line in desc.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  描述：{desc}")
        if schedule.get('意义'):
            val = schedule.get('意义')
            if '\n' in val:
                print(f"  意义/价值：")
                for line in val.split('\n'):
                    print(f"      {line}")
            else:
                print(f"  意义/价值：{val}")
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_schedule_delete(schedule_file: str, schedule_id: int = None, index: int = None) -> bool:
    """删除排期（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    result = manager.delete_schedule(schedule_id, index)
    
    print("=" * 60)
    print("删除排期")
    print("=" * 60)
    
    if result['success']:
        print(f"[OK] {result['message']}")
        return True
    else:
        print(f"[ERROR] {result['message']}")
        return False


def cmd_schedule_gen(schedule_file: str) -> bool:
    """对话式生成排期（CLI命令）- 增强版，包含检查和处理现有排期"""
    import re
    
    manager = ScheduleManager(schedule_file)
    now = datetime.now()
    
    print("=" * 60)
    print("排期管理")
    print("=" * 60)
    print()
    
    # ========================================================================
    # 第一步：检查未来排期，询问是否重新制定
    # ========================================================================
    future_schedules = manager.get_future_schedules()
    if future_schedules:
        print("检测到已有未来排期：")
        print("-" * 60)
        for schedule in future_schedules:
            schedule_id = schedule.get('id')
            task = schedule.get('任务', '无任务')
            start_time = schedule.get('开始时间', '')
            end_time = schedule.get('结束时间', '')
            status = schedule.get('完成情况', '未完成')
            description = schedule.get('描述', '')
            value = schedule.get('意义', '')
            print(f"[{schedule_id}] {task}")
            print(f"    时间段：{start_time} ~ {end_time}")
            print(f"    状态：{status}")
            if description:
                # 如果描述包含换行符，格式化显示
                if '\n' in description:
                    print(f"    描述：")
                    for line in description.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    描述：{description}")
            if value:
                # 如果意义/价值包含换行符，格式化显示
                if '\n' in value:
                    print(f"    意义/价值：")
                    for line in value.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    意义/价值：{value}")
        print("-" * 60)
        print()
        
        # 询问是否重新制定（默认：n）
        while True:
            try:
                confirm = input("是否要重新制定计划？(y/n，默认：n)：").strip().lower()
                if not confirm:
                    confirm = 'n'
                if confirm in ['y', 'yes', '是', 'n', 'no', '否']:
                    break
                print("请输入 y 或 n")
            except KeyboardInterrupt:
                print("\n\n已取消")
                return False
        
        if confirm in ['y', 'yes', '是']:
            # 三次确认
            confirm_count = 0
            confirm_messages = [
                "确认重新制定计划？这将软删除所有未来排期（y/n，默认：n）：",
                "再次确认？请慎重考虑（y/n，默认：n）：",
                "最后确认？确定要重新制定计划吗？（y/n，默认：n）："
            ]
            
            for i, msg in enumerate(confirm_messages):
                try:
                    confirm_input = input(msg).strip().lower()
                    if not confirm_input:
                        confirm_input = 'n'
                    if confirm_input not in ['y', 'yes', '是']:
                        print("已取消重新制定计划")
                        break
                    confirm_count += 1
                except KeyboardInterrupt:
                    print("\n\n已取消")
                    return False
            
            if confirm_count == 3:
                # 软删除所有未来排期
                result = manager.soft_delete_future_schedules()
                if result['success']:
                    print(f"[OK] {result['message']}")
                else:
                    print(f"[ERROR] {result['message']}")
                    return False
            else:
                print("未完成三次确认，取消重新制定计划")
    
    # ========================================================================
    # 第二步：检查正在进行的任务
    # ========================================================================
    in_progress = manager.get_in_progress_schedules()
    if in_progress:
        print("\n" + "=" * 60)
        print("正在进行的任务")
        print("=" * 60)
        
        for schedule in in_progress:
            schedule_id = schedule.get('id')
            task = schedule.get('任务', '无任务')
            start_time = schedule.get('开始时间', '')
            end_time = schedule.get('结束时间', '')
            status = schedule.get('完成情况', '未完成')
            description = schedule.get('描述', '')
            value = schedule.get('意义', '')
            
            print(f"\n[{schedule_id}] {task}")
            print(f"    时间段：{start_time} ~ {end_time}")
            print(f"    当前状态：{status}")
            if description:
                if '\n' in description:
                    print(f"    描述：")
                    for line in description.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    描述：{description}")
            if value:
                if '\n' in value:
                    print(f"    意义/价值：")
                    for line in value.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    意义/价值：{value}")
            
            # 询问执行情况
            print("\n请选择操作：")
            print("  [1] 正常进行中（保持状态）")
            print("  [2] 已完成（更新为已完成）")
            print("  [3] 需要延期（延长结束时间）")
            print("  [4] 需要搁置（更新为搁置）")
            print("  [5] 更新描述")
            print("  [6] 补充意义/价值")
            print("  [0] 跳过")
            
            while True:
                try:
                    choice = input("\n请选择（0-6，默认：0）：").strip()
                    if not choice:
                        choice = '0'
                    
                    if choice == '0':
                        break
                    elif choice == '1':
                        # 保持状态，但确保是"进行中"
                        manager.update_schedule(schedule_id=schedule_id, status='进行中')
                        print("[OK] 已更新状态为：进行中")
                        break
                    elif choice == '2':
                        manager.update_schedule(schedule_id=schedule_id, status='已完成')
                        print("[OK] 已更新状态为：已完成")
                        break
                    elif choice == '3':
                        # 延期
                        while True:
                            try:
                                extension_input = input("请输入延长时间（例如：1小时、30分钟、1.5小时）：").strip()
                                if not extension_input:
                                    print("输入不能为空")
                                    continue
                                
                                # 解析延长时间
                                extension_minutes = None
                                hour_match = re.match(r'^(\d+(?:\.\d+)?)\s*小时$', extension_input)
                                if hour_match:
                                    extension_minutes = float(hour_match.group(1)) * 60
                                else:
                                    minute_match = re.match(r'^(\d+(?:\.\d+)?)\s*分钟$', extension_input)
                                    if minute_match:
                                        extension_minutes = float(minute_match.group(1))
                                    else:
                                        try:
                                            extension_minutes = float(extension_input) * 60
                                        except ValueError:
                                            print("无法解析时间，请使用格式：1小时、30分钟 等")
                                            continue
                                
                                if extension_minutes <= 0:
                                    print("延长时间必须大于0")
                                    continue
                                
                                result = manager.extend_schedule(schedule_id=schedule_id, extension_minutes=extension_minutes)
                                if result['success']:
                                    print(f"[OK] {result['message']}")
                                else:
                                    print(f"[ERROR] {result['message']}")
                                break
                            except KeyboardInterrupt:
                                print("\n已取消延期")
                                break
                        break
                    elif choice == '4':
                        manager.update_schedule(schedule_id=schedule_id, status='搁置')
                        print("[OK] 已更新状态为：搁置")
                        break
                    elif choice == '5':
                        new_desc = input("请输入新的描述（支持\\n换行，留空则清空）：").strip()
                        if new_desc:
                            new_desc = new_desc.replace('\\n', '\n')
                        manager.update_schedule(schedule_id=schedule_id, description=new_desc)
                        print("[OK] 已更新描述")
                        break
                    elif choice == '6':
                        new_value = input("请输入意义/价值（支持\\n换行，留空则清空）：").strip()
                        if new_value:
                            new_value = new_value.replace('\\n', '\n')
                        manager.update_schedule(schedule_id=schedule_id, value=new_value)
                        print("[OK] 已更新意义/价值")
                        break
                    else:
                        print("无效的选择，请输入 0-6")
                except KeyboardInterrupt:
                    print("\n已取消")
                    break
    
    # ========================================================================
    # 第三步：检查已过期的任务
    # ========================================================================
    expired = manager.get_expired_schedules()
    if expired:
        print("\n" + "=" * 60)
        print("已过期的任务")
        print("=" * 60)
        
        for schedule in expired:
            schedule_id = schedule.get('id')
            task = schedule.get('任务', '无任务')
            start_time = schedule.get('开始时间', '')
            end_time = schedule.get('结束时间', '')
            status = schedule.get('完成情况', '未完成')
            description = schedule.get('描述', '')
            value = schedule.get('意义', '')
            
            print(f"\n[{schedule_id}] {task}")
            print(f"    时间段：{start_time} ~ {end_time}（已过期）")
            print(f"    当前状态：{status}")
            if description:
                if '\n' in description:
                    print(f"    描述：")
                    for line in description.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    描述：{description}")
            if value:
                if '\n' in value:
                    print(f"    意义/价值：")
                    for line in value.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    意义/价值：{value}")
            
            # 询问是否需要更新状态
            print("\n请选择操作：")
            print("  [1] 已完成（更新为已完成）")
            print("  [2] 未完成（更新为未完成，记录原因）")
            print("  [3] 需要延期（延长结束时间）")
            print("  [4] 需要搁置（更新为搁置）")
            print("  [5] 更新描述")
            print("  [6] 补充意义/价值")
            print("  [0] 跳过")
            
            while True:
                try:
                    choice = input("\n请选择（0-6，默认：0）：").strip()
                    if not choice:
                        choice = '0'
                    
                    if choice == '0':
                        break
                    elif choice == '1':
                        manager.update_schedule(schedule_id=schedule_id, status='已完成')
                        print("[OK] 已更新状态为：已完成")
                        break
                    elif choice == '2':
                        reason = input("请输入未完成的原因（可选）：").strip()
                        manager.update_schedule(schedule_id=schedule_id, status='未完成')
                        if reason:
                            current_desc = schedule.get('描述', '')
                            new_desc = f"{current_desc}\n未完成原因：{reason}" if current_desc else f"未完成原因：{reason}"
                            manager.update_schedule(schedule_id=schedule_id, description=new_desc)
                        print("[OK] 已更新状态为：未完成")
                        break
                    elif choice == '3':
                        # 延期
                        while True:
                            try:
                                extension_input = input("请输入延长时间（例如：1小时、30分钟、1.5小时）：").strip()
                                if not extension_input:
                                    print("输入不能为空")
                                    continue
                                
                                # 解析延长时间
                                extension_minutes = None
                                hour_match = re.match(r'^(\d+(?:\.\d+)?)\s*小时$', extension_input)
                                if hour_match:
                                    extension_minutes = float(hour_match.group(1)) * 60
                                else:
                                    minute_match = re.match(r'^(\d+(?:\.\d+)?)\s*分钟$', extension_input)
                                    if minute_match:
                                        extension_minutes = float(minute_match.group(1))
                                    else:
                                        try:
                                            extension_minutes = float(extension_input) * 60
                                        except ValueError:
                                            print("无法解析时间，请使用格式：1小时、30分钟 等")
                                            continue
                                
                                if extension_minutes <= 0:
                                    print("延长时间必须大于0")
                                    continue
                                
                                result = manager.extend_schedule(schedule_id=schedule_id, extension_minutes=extension_minutes)
                                if result['success']:
                                    print(f"[OK] {result['message']}")
                                else:
                                    print(f"[ERROR] {result['message']}")
                                break
                            except KeyboardInterrupt:
                                print("\n已取消延期")
                                break
                        break
                    elif choice == '4':
                        manager.update_schedule(schedule_id=schedule_id, status='搁置')
                        print("[OK] 已更新状态为：搁置")
                        break
                    elif choice == '5':
                        new_desc = input("请输入新的描述（支持\\n换行，留空则清空）：").strip()
                        if new_desc:
                            new_desc = new_desc.replace('\\n', '\n')
                        manager.update_schedule(schedule_id=schedule_id, description=new_desc)
                        print("[OK] 已更新描述")
                        break
                    elif choice == '6':
                        new_value = input("请输入意义/价值（支持\\n换行，留空则清空）：").strip()
                        if new_value:
                            new_value = new_value.replace('\\n', '\n')
                        manager.update_schedule(schedule_id=schedule_id, value=new_value)
                        print("[OK] 已更新意义/价值")
                        break
                    else:
                        print("无效的选择，请输入 0-6")
                except KeyboardInterrupt:
                    print("\n已取消")
                    break
    
    # ========================================================================
    # 第四步：询问是否要制定新的排期
    # ========================================================================
    print("\n" + "=" * 60)
    print("制定新排期")
    print("=" * 60)
    
    while True:
        try:
            create_new = input("是否要制定新的排期？(y/n，默认：n)：").strip().lower()
            if not create_new:
                create_new = 'n'
            if create_new in ['y', 'yes', '是', 'n', 'no', '否']:
                break
            print("请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return False
    
    if create_new not in ['y', 'yes', '是']:
        print("已退出")
        return True
    
    # ========================================================================
    # 第五步：原有的生成排期流程
    # ========================================================================
    print("\n" + "=" * 60)
    print("自动生成排期")
    print("=" * 60)
    print()
    
    # 1. 询问总时长
    while True:
        try:
            total_hours_input = input("请输入接下来安排的总时长（小时，例如：8 表示8小时）：").strip()
            if not total_hours_input:
                print("输入不能为空，请重新输入")
                continue
            total_hours = float(total_hours_input)
            if total_hours <= 0:
                print("总时长必须大于0，请重新输入")
                continue
            break
        except ValueError:
            print("输入格式错误，请输入数字（例如：8 或 8.5）")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return False
    
    # 2. 询问时间单位
    while True:
        unit_input = input("请输入每个排期的时间单位（例如：1小时、40分钟、1.5小时）：").strip()
        if not unit_input:
            print("输入不能为空，请重新输入")
            continue
        
        # 解析时间单位
        unit_minutes = None
        
        # 匹配 "X小时" 或 "X.5小时" 格式
        hour_match = re.match(r'^(\d+(?:\.\d+)?)\s*小时$', unit_input)
        if hour_match:
            unit_minutes = float(hour_match.group(1)) * 60
        else:
            # 匹配 "X分钟" 格式
            minute_match = re.match(r'^(\d+(?:\.\d+)?)\s*分钟$', unit_input)
            if minute_match:
                unit_minutes = float(minute_match.group(1))
            else:
                # 尝试直接解析为数字（假设是小时）
                try:
                    unit_minutes = float(unit_input) * 60
                except ValueError:
                    print("无法解析时间单位，请使用格式：1小时、40分钟、1.5小时 等")
                    continue
        
        if unit_minutes <= 0:
            print("时间单位必须大于0，请重新输入")
            continue
        
        if unit_minutes > total_hours * 60:
            print(f"时间单位（{unit_minutes/60:.2f}小时）不能大于总时长（{total_hours}小时），请重新输入")
            continue
        
        break
    
    # 3. 询问开始时间（可选）
    start_time_input = input("请输入开始时间（格式：YYYY-MM-DD HH:MM，留空则从当前时间开始）：").strip()
    if start_time_input:
        try:
            # 替换中文冒号为英文冒号（处理用户输入中文冒号的情况）
            start_time_input = start_time_input.replace('：', ':')
            # 移除可能的换行符和多余空格
            start_time_input = ' '.join(start_time_input.split())
            
            if len(start_time_input) == 10:
                start_dt = datetime.strptime(start_time_input, "%Y-%m-%d")
            else:
                start_dt = datetime.strptime(start_time_input, "%Y-%m-%d %H:%M")
        except ValueError as e:
            print(f"时间格式错误：{str(e)}，将使用当前时间")
            start_dt = datetime.now()
            # 将分钟数向下取整到最近的5分钟
            start_dt = start_dt.replace(minute=(start_dt.minute // 5) * 5, second=0, microsecond=0)
    else:
        start_dt = datetime.now()
        # 将分钟数向下取整到最近的5分钟
        start_dt = start_dt.replace(minute=(start_dt.minute // 5) * 5, second=0, microsecond=0)
    
    # 4. 询问任务名称模板（可选）
    print("\n任务名称模板说明：")
    print("  - 留空：使用默认模板 \"任务{n}\"，将生成：任务1、任务2、任务3...")
    print("  - 使用 {n} 占位符：例如 \"工作{n}\" 将生成：工作1、工作2、工作3...")
    print("  - 不使用 {n}：例如 \"学习\" 将生成：学习、学习、学习...")
    print("  - 示例：\"第{n}个任务\" → 第1个任务、第2个任务、第3个任务...")
    task_template = input("\n请输入任务名称模板（留空则使用默认）：").strip()
    if not task_template:
        task_template = "任务{n}"
    
    # 5. 询问默认状态
    while True:
        default_status = input("请输入默认完成情况（已完成/进行中/未完成/搁置/延期，默认：未完成）：").strip()
        if not default_status:
            default_status = "未完成"
            break
        if default_status in ["已完成", "进行中", "未完成", "搁置", "延期"]:
            break
        print("无效的状态，请输入：已完成、进行中、未完成、搁置 或 延期")
    
    # 计算排期数量
    total_minutes = total_hours * 60
    num_schedules = int(total_minutes / unit_minutes)
    remaining_minutes = total_minutes % unit_minutes
    
    if num_schedules == 0:
        print(f"\n[ERROR] 时间单位（{unit_minutes/60:.2f}小时）大于总时长（{total_hours}小时），无法生成排期")
        return False
    
    # 显示生成预览
    print(f"\n生成预览：")
    print(f"  总时长：{total_hours} 小时")
    print(f"  时间单位：{unit_minutes/60:.2f} 小时（{unit_minutes} 分钟）")
    print(f"  开始时间：{start_dt.strftime('%Y-%m-%d %H:%M')}")
    print(f"  排期数量：{num_schedules} 个")
    if remaining_minutes > 0:
        print(f"  剩余时间：{remaining_minutes} 分钟（将不生成排期）")
    print(f"  任务模板：{task_template}")
    print(f"  默认状态：{default_status}")
    print()
    
    # 为每个任务询问详细描述
    task_descriptions = []
    print("=" * 60)
    print("为每个任务设置详细描述")
    print("=" * 60)
    print("提示：")
    print("  - 可以直接回车跳过，留空则不设置描述")
    print("  - 支持多行输入，使用 \\n 表示换行（例如：第一行\\n第二行）")
    print()
    
    for i in range(num_schedules):
        # 计算开始和结束时间（用于显示）
        temp_start = start_dt + timedelta(minutes=unit_minutes * i)
        temp_end = temp_start + timedelta(minutes=unit_minutes)
        temp_start_str = temp_start.strftime("%Y-%m-%d %H:%M")
        temp_end_str = temp_end.strftime("%Y-%m-%d %H:%M")
        
        # 生成任务名称（用于显示）
        task_name = task_template.replace("{n}", str(i + 1))
        
        # 询问描述
        try:
            desc_prompt = f"[{i+1}/{num_schedules}] {task_name} ({temp_start_str} ~ {temp_end_str})\n  请输入详细描述："
            description = input(desc_prompt).strip()
            # 将 \n 转换为实际的换行符
            if description:
                description = description.replace('\\n', '\n')
            task_descriptions.append(description)
        except KeyboardInterrupt:
            print("\n\n已取消")
            return False
    
    print()
    print("=" * 60)
    print("为每个任务设置意义/价值")
    print("=" * 60)
    print("提示：")
    print("  - 可以直接回车跳过，留空则不设置意义/价值")
    print("  - 支持多行输入，使用 \\n 表示换行（例如：第一行\\n第二行）")
    print("  - 意义/价值用于激励自己，例如：'完成这个任务可以提升我的技能'")
    print()
    
    # 为每个任务询问意义/价值
    task_values = []
    for i in range(num_schedules):
        # 计算开始和结束时间（用于显示）
        temp_start = start_dt + timedelta(minutes=unit_minutes * i)
        temp_end = temp_start + timedelta(minutes=unit_minutes)
        temp_start_str = temp_start.strftime("%Y-%m-%d %H:%M")
        temp_end_str = temp_end.strftime("%Y-%m-%d %H:%M")
        
        # 生成任务名称（用于显示）
        task_name = task_template.replace("{n}", str(i + 1))
        
        # 询问意义/价值
        try:
            value_prompt = f"[{i+1}/{num_schedules}] {task_name} ({temp_start_str} ~ {temp_end_str})\n  请输入意义/价值："
            value = input(value_prompt).strip()
            # 将 \n 转换为实际的换行符
            if value:
                value = value.replace('\\n', '\n')
            task_values.append(value)
        except KeyboardInterrupt:
            print("\n\n已取消")
            return False
    
    print()
    print("=" * 60)
    print("设置完成")
    print("=" * 60)
    print()
    
    # 确认生成
    confirm = input("确认生成？(y/n，默认：y)：").strip().lower()
    if confirm and confirm not in ['y', 'yes', '是']:
        print("已取消")
        return False
    
    # 生成排期
    manager = ScheduleManager(schedule_file)
    current_dt = start_dt
    generated_count = 0
    
    print("\n正在生成排期...")
    print("-" * 60)
    
    for i in range(num_schedules):
        # 计算开始和结束时间
        schedule_start = current_dt
        schedule_end = current_dt + timedelta(minutes=unit_minutes)
        
        # 格式化时间字符串
        start_time_str = schedule_start.strftime("%Y-%m-%d %H:%M")
        end_time_str = schedule_end.strftime("%Y-%m-%d %H:%M")
        
        # 生成任务名称
        task_name = task_template.replace("{n}", str(i + 1))
        
        # 获取对应的描述和意义/价值
        description = task_descriptions[i] if i < len(task_descriptions) else ""
        value = task_values[i] if i < len(task_values) else ""
        
        # 添加排期
        result = manager.add_schedule(
            start_time=start_time_str,
            end_time=end_time_str,
            task=task_name,
            status=default_status,
            description=description,
            value=value
        )
        
        if result['success']:
            generated_count += 1
            schedule = result['schedule']
            print(f"[{schedule.get('id')}] {task_name}")
            print(f"    {start_time_str} ~ {end_time_str}")
            if description:
                # 如果描述包含换行符，格式化显示
                if '\n' in description:
                    print(f"    描述：")
                    for line in description.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    描述：{description}")
            if value:
                # 如果意义/价值包含换行符，格式化显示
                if '\n' in value:
                    print(f"    意义/价值：")
                    for line in value.split('\n'):
                        print(f"        {line}")
                else:
                    print(f"    意义/价值：{value}")
        else:
            print(f"[ERROR] 生成排期 {i+1} 失败：{result['message']}")
        
        # 更新当前时间
        current_dt = schedule_end
    
    print("-" * 60)
    print(f"\n[OK] 成功生成 {generated_count}/{num_schedules} 个排期")
    
    if remaining_minutes > 0:
        print(f"提示：剩余 {remaining_minutes} 分钟未生成排期")
    
    return True


def cmd_schedule_search(schedule_file: str, keyword: str = None, task: str = None,
                       description: str = None, value: str = None, case_sensitive: bool = False) -> bool:
    """搜索排期（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    
    if not keyword and not task and not description and not value:
        print("错误：请提供搜索关键词")
        print("用法示例：")
        print("  python texteditor_cli.py schedule search \"项目\"")
        print("  python texteditor_cli.py schedule search --task \"开发\"")
        print("  python texteditor_cli.py schedule search --description \"重要\"")
        print("  python texteditor_cli.py schedule search --value \"提升技能\"")
        return False
    
    results = manager.search(keyword, task, description, value, case_sensitive)
    
    print("=" * 60)
    print("搜索结果")
    print("=" * 60)
    
    if keyword:
        print(f"搜索关键词：{keyword}（在任务、描述和意义/价值中搜索）")
    if task:
        print(f"任务关键词：{task}")
    if description:
        print(f"描述关键词：{description}")
    if value:
        print(f"意义/价值关键词：{value}")
    print(f"匹配数量：{len(results)}")
    print("-" * 60)
    
    if len(results) == 0:
        print("未找到匹配的排期")
        return True
    
    for schedule in results:
        schedule_id = schedule.get('id')
        print(f"\n[{schedule_id}] {schedule.get('任务', '无任务')}")
        print(f"    时间段：{schedule.get('开始时间')} ~ {schedule.get('结束时间')}")
        print(f"    完成情况：{schedule.get('完成情况')}")
        if schedule.get('描述'):
            desc = schedule.get('描述')
            if '\n' in desc:
                print(f"    描述：")
                for line in desc.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    描述：{desc}")
        if schedule.get('意义'):
            value = schedule.get('意义')
            if '\n' in value:
                print(f"    意义/价值：")
                for line in value.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    意义/价值：{value}")
    
    return True


def cmd_schedule_history(schedule_file: str, days: int = 7) -> bool:
    """查询历史排期（CLI命令）"""
    manager = ScheduleManager(schedule_file)
    history = manager.get_history_schedules(days)
    
    now = datetime.now()
    start_time = now - timedelta(days=days)
    
    print("=" * 60)
    print("历史排期")
    print("=" * 60)
    print(f"查询范围：过去 {days} 天内（{start_time.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}）")
    print(f"历史排期数量：{len(history)}")
    print("-" * 60)
    
    if len(history) == 0:
        print("未找到历史排期")
        return True
    
    # 统计信息
    status_count = {}
    for schedule in history:
        status = schedule.get('完成情况', '未知')
        status_count[status] = status_count.get(status, 0) + 1
    
    print("\n完成情况统计：")
    for status, count in sorted(status_count.items()):
        print(f"  {status}：{count} 个")
    
    print("\n历史排期列表：")
    print("-" * 60)
    
    for schedule in history:
        schedule_id = schedule.get('id')
        task = schedule.get('任务', '无任务')
        start_time_str = schedule.get('开始时间', '')
        end_time_str = schedule.get('结束时间', '')
        status = schedule.get('完成情况', '未知')
        description = schedule.get('描述', '')
        value = schedule.get('意义', '')
        create_time = schedule.get('创建时间', '未知')
        
        print(f"\n[{schedule_id}] {task}")
        print(f"    时间段：{start_time_str} ~ {end_time_str}")
        print(f"    完成情况：{status}")
        print(f"    创建时间：{create_time}")
        
        if description:
            if '\n' in description:
                print(f"    描述：")
                for line in description.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    描述：{description}")
        
        if value:
            if '\n' in value:
                print(f"    意义/价值：")
                for line in value.split('\n'):
                    print(f"        {line}")
            else:
                print(f"    意义/价值：{value}")
    
    return True

