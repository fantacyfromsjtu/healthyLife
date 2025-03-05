#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提醒管理器模块
负责后台检查并发送提醒通知
"""

import threading
import time
import datetime
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("plyer库未安装，将使用替代通知方式")

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='app.log')
logger = logging.getLogger('ReminderManager')

class ReminderManager(QObject):
    """
    提醒管理器类，负责检查即将到来的提醒并发送通知
    """
    # 定义信号，当新提醒被触发时发送
    reminder_triggered = pyqtSignal(int, str, str)
    
    def __init__(self, db_manager):
        """
        初始化提醒管理器
        
        参数:
            db_manager: 数据库管理器实例
        """
        super().__init__()
        self.db_manager = db_manager
        self.is_running = False
        self.check_interval = 30  # 检查间隔(秒)
        self.reminder_thread = None
        self.notification_titles = {
            "锻炼": "健康生活提醒 - 该锻炼了",
            "吃饭": "健康生活提醒 - 该吃饭了",
            "睡觉": "健康生活提醒 - 该休息了"
        }
        logger.info("提醒管理器初始化完成")
    
    def start(self):
        """启动提醒检查线程"""
        if self.is_running:
            logger.info("提醒管理器已在运行")
            return
            
        self.is_running = True
        self.reminder_thread = threading.Thread(target=self._check_reminders_loop)
        self.reminder_thread.daemon = True  # 设置为守护线程，主线程结束时自动结束
        self.reminder_thread.start()
        logger.info("提醒管理器已启动")
    
    def stop(self):
        """停止提醒检查线程"""
        self.is_running = False
        if self.reminder_thread:
            try:
                self.reminder_thread.join(timeout=1.0)
            except RuntimeError:
                pass
        logger.info("提醒管理器已停止")
    
    def _check_reminders_loop(self):
        """检查提醒的主循环"""
        logger.info("提醒检查循环已启动")
        while self.is_running:
            try:
                self._check_upcoming_reminders()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"检查提醒时发生错误: {e}")
                time.sleep(self.check_interval)
    
    def _check_upcoming_reminders(self):
        """检查即将到来的提醒"""
        now = datetime.datetime.now()
        # 设置检查范围为前后5分钟
        start_time = now - datetime.timedelta(minutes=1)
        end_time = now + datetime.timedelta(minutes=1)
        
        # 获取当前用户ID
        user_id = self._get_current_user_id()
        if not user_id:
            return
        
        # 创建新的数据库连接，避免线程问题
        import sqlite3
        try:
            # 创建临时数据库连接
            temp_conn = sqlite3.connect(self.db_manager.db_path)
            temp_conn.row_factory = sqlite3.Row  # 让结果以字典形式返回
            temp_cursor = temp_conn.cursor()
            
            # 手动实现get_reminders_for_time_range，而不是调用self.db_manager的方法
            start_date = start_time.strftime("%Y-%m-%d")
            end_date = end_time.strftime("%Y-%m-%d")
            start_time_str = start_time.strftime("%H:%M")
            end_time_str = end_time.strftime("%H:%M")
            
            # 处理同一天的情况
            if start_date == end_date:
                temp_cursor.execute('''
                SELECT id, user_id, date, time, reminder_type, content, is_completed
                FROM reminders
                WHERE user_id = ? AND date = ? AND time BETWEEN ? AND ?
                AND is_completed = 0
                ORDER BY time
                ''', (user_id, start_date, start_time_str, end_time_str))
            else:
                # 处理跨天的情况
                temp_cursor.execute('''
                SELECT id, user_id, date, time, reminder_type, content, is_completed
                FROM reminders
                WHERE user_id = ? AND 
                      ((date = ? AND time >= ?) OR (date = ? AND time <= ?))
                AND is_completed = 0
                ORDER BY date, time
                ''', (user_id, start_date, start_time_str, end_date, end_time_str))
            
            # 将查询结果转为字典列表
            reminders = []
            for row in temp_cursor.fetchall():
                reminder = dict(row)
                reminders.append(reminder)
            
            # 处理提醒
            for reminder in reminders:
                # 检查提醒是否在当前时间点触发
                if self._should_trigger_now(reminder, now):
                    self._send_notification(reminder)
                    
                    # 使用临时连接标记提醒为已完成
                    temp_cursor.execute(
                        "UPDATE reminders SET is_completed = 1 WHERE id = ?", 
                        (reminder['id'],)
                    )
                    temp_conn.commit()
                    
                    # 发出信号
                    self.reminder_triggered.emit(
                        reminder['id'], 
                        reminder['reminder_type'], 
                        reminder['content']
                    )
                
        except Exception as e:
            logger.error(f"获取时间范围内的提醒失败: {e}")
        finally:
            # 确保关闭临时连接
            if 'temp_conn' in locals():
                temp_conn.close()
    
    def _should_trigger_now(self, reminder, current_time):
        """
        判断是否应该触发提醒
        
        参数:
            reminder (dict): 提醒信息
            current_time (datetime): 当前时间
            
        返回:
            bool: 是否应该触发
        """
        # 解析提醒时间
        reminder_date = reminder['date']
        reminder_time = reminder['time']
        
        if not reminder_date or not reminder_time:
            return False
        
        try:
            reminder_datetime = datetime.datetime.strptime(
                f"{reminder_date} {reminder_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # 计算时间差（分钟）
            time_diff = abs((current_time - reminder_datetime).total_seconds() / 60)
            
            # 如果时间差在1分钟内，且未完成，则触发
            return time_diff <= 1 and not reminder['is_completed']
        except ValueError:
            logger.error(f"解析提醒时间失败: {reminder_date} {reminder_time}")
            return False
    
    def _send_notification(self, reminder):
        """
        发送桌面通知
        
        参数:
            reminder (dict): 提醒信息
        """
        title = self.notification_titles.get(
            reminder['reminder_type'], 
            "健康生活提醒"
        )
        message = reminder['content'] or f"您设置的{reminder['reminder_type']}提醒时间到了"
        
        logger.info(f"发送提醒: {title} - {message}")
        
        # 使用plyer发送通知
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="健康生活助手",
                    timeout=10
                )
            except Exception as e:
                logger.error(f"发送通知失败: {e}")
                self._fallback_notification(title, message)
        else:
            self._fallback_notification(title, message)
    
    def _fallback_notification(self, title, message):
        """
        备用通知方式
        
        参数:
            title (str): 通知标题
            message (str): 通知内容
        """
        # 使用Qt自带的方式显示通知
        print(f"提醒: {title} - {message}")
        # 这里可以添加其他通知方式
        
    def _get_current_user_id(self):
        """
        获取当前登录用户ID
        
        返回:
            int: 用户ID，如果没有登录用户则返回None
        """
        # 在实际应用中，应当从当前应用状态获取
        # 这里暂时使用一个固定值或从主应用获取
        # 这个方法需要根据实际情况修改
        return 1  # 测试时默认使用用户ID 1


# 单例模式
_reminder_manager_instance = None

def get_reminder_manager(db_manager=None):
    """
    获取提醒管理器单例
    
    参数:
        db_manager: 数据库管理器实例，首次调用时必须提供
        
    返回:
        ReminderManager: 提醒管理器实例
    """
    global _reminder_manager_instance
    if _reminder_manager_instance is None:
        if db_manager is None:
            raise ValueError("首次获取提醒管理器时必须提供数据库管理器")
        _reminder_manager_instance = ReminderManager(db_manager)
    return _reminder_manager_instance 