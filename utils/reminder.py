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
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox
from PyQt5.QtCore import QObject, QTimer, QTime, QDateTime, pyqtSignal
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
    reminder_triggered = pyqtSignal(str, str, int)  # 标题，内容，提醒ID
    
    def __init__(self, db_manager, user_id, parent=None):
        """
        初始化提醒管理器
        
        参数:
            db_manager: 数据库管理器实例
            user_id: 用户ID
            parent: 父对象
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.timer = QTimer(self)
        self.active_reminders = {}  # 记录活跃的提醒，防止重复提示
        self.check_interval = 30000  # 默认30秒检查一次
        
        # 连接定时器到检查函数
        self.timer.timeout.connect(self.check_reminders)
        
        # 初始化时启动定时器
        self.start()
        
        print("提醒管理器已初始化，检查间隔：30秒")
    
    def start(self):
        """启动提醒检查"""
        self.timer.start(self.check_interval)
        print("提醒检查已启动")
    
    def stop(self):
        """停止提醒检查"""
        self.timer.stop()
        print("提醒检查已停止")
    
    def set_check_interval(self, milliseconds):
        """设置检查间隔"""
        self.check_interval = milliseconds
        # 如果定时器在运行，重新设置间隔
        if self.timer.isActive():
            self.timer.start(self.check_interval)
        print(f"提醒检查间隔已更新为：{milliseconds/1000}秒")
    
    def check_reminders(self):
        """检查是否有到期的提醒"""
        try:
            # 获取当前时间
            now = QDateTime.currentDateTime()
            now_time = now.time()
            now_date = now.date().toString("yyyy-MM-dd")
            
            # 检查前后15分钟内的提醒
            start_time = now.addSecs(-900).toString("HH:mm:ss")  # 15分钟前
            end_time = now.addSecs(900).toString("HH:mm:ss")    # 15分钟后
            
            print(f"当前检查提醒: 当前时间={now.toString('yyyy-MM-dd HH:mm:ss')}")
            
            # 查询数据库
            reminders = self.db_manager.get_reminders_for_time_range(
                self.user_id, 
                (now_date, start_time), 
                (now_date, end_time)
            )
            
            if reminders:
                print(f"检查到{len(reminders)}个在时间范围内的提醒")
            
            for reminder in reminders:
                reminder_id = reminder[0]
                reminder_date = reminder[2]
                reminder_time = reminder[3]
                reminder_type = reminder[4]
                reminder_content = reminder[5]
                is_completed = reminder[6]
                
                print(f"处理提醒: ID={reminder_id}, 日期={reminder_date}, 时间={reminder_time}, 类型={reminder_type}, 内容={reminder_content}, 完成={is_completed}")
                
                # 检查是否已完成或已提醒
                if is_completed or reminder_id in self.active_reminders:
                    print(f"  跳过提醒: 已完成={is_completed}, 在活跃列表中={(reminder_id in self.active_reminders)}")
                    continue
                
                # 解析提醒时间 - 支持多种格式
                reminder_datetime = QDateTime()
                reminder_datetime.setDate(QDateTime.fromString(reminder_date, "yyyy-MM-dd").date())
                
                # 处理不同格式的时间字符串
                time_obj = None
                if ":" in reminder_time:
                    # 尝试不同的时间格式
                    formats = ["HH:mm:ss", "HH:mm", "h:mm:ss", "h:mm"]
                    for fmt in formats:
                        time_obj = QTime.fromString(reminder_time, fmt)
                        if time_obj.isValid():
                            print(f"  成功解析时间: {reminder_time} 使用格式 {fmt}")
                            break
                
                if not time_obj or not time_obj.isValid():
                    print(f"  无法解析时间: {reminder_time}")
                    continue
                    
                reminder_datetime.setTime(time_obj)
                
                # 确保日期时间有效
                if not reminder_datetime.isValid():
                    print(f"  无效的日期时间: {reminder_date} {reminder_time}")
                    continue
                
                # 计算时间差（秒）
                seconds_diff = reminder_datetime.secsTo(now)
                print(f"  时间差: {seconds_diff}秒")
                
                # 如果时间差在±10分钟内且未完成，触发提醒
                if -600 <= seconds_diff <= 600:
                    print(f"  准备触发提醒: 时间差在±10分钟内")
                    # 将提醒添加到活跃列表，防止重复提醒
                    self.active_reminders[reminder_id] = time.time()
                    
                    # 计算时间状态说明
                    time_status = ""
                    if seconds_diff < 0:
                        time_status = f"还有{abs(seconds_diff)//60}分钟"
                    elif seconds_diff > 0:
                        time_status = f"已过{seconds_diff//60}分钟"
                    else:
                        time_status = "现在"
                    
                    # 触发提醒信号
                    title = f"{reminder_type}提醒 ({time_status})"
                    content = f"{reminder_content}\n时间：{reminder_time}"
                    
                    print(f"  发送提醒触发信号: {title}")
                    self.reminder_triggered.emit(title, content, reminder_id)
                    
                    # 调用直接显示的方法，以防信号/槽机制出问题
                    try:
                        from PyQt5.QtWidgets import QApplication
                        if parent := self.parent():
                            self._direct_show_reminder(parent, title, content, reminder_id)
                        else:
                            # 尝试直接弹出消息框
                            QMessageBox = QApplication.instance().findChild("QMessageBox")
                            if QMessageBox:
                                msgbox = QMessageBox()
                                msgbox.setWindowTitle(title)
                                msgbox.setText(content)
                                msgbox.exec_()
                                print(f"  直接弹出提醒对话框")
                    except Exception as e:
                        print(f"  直接显示提醒失败: {str(e)}")
                    
                    print(f"  提醒触发完成: {title} - {content}")
            
            # 清理过期的活跃提醒（超过30分钟）
            current_time = time.time()
            expired_reminders = []
            for rid, timestamp in self.active_reminders.items():
                if current_time - timestamp > 1800:  # 30分钟
                    expired_reminders.append(rid)
            
            for rid in expired_reminders:
                del self.active_reminders[rid]
                
        except Exception as e:
            print(f"检查提醒时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _direct_show_reminder(self, parent, title, content, reminder_id):
        """直接显示提醒窗口，不依赖信号槽"""
        try:
            dialog = ReminderDialog(title, content, reminder_id, self.db_manager, parent)
            dialog.show()  # 使用show而不是exec_
            print(f"  直接显示提醒窗口")
        except Exception as e:
            print(f"  直接显示提醒窗口失败: {str(e)}")

class ReminderDialog(QDialog):
    """提醒对话框"""
    
    def __init__(self, title, content, reminder_id, db_manager, parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.reminder_id = reminder_id
        self.db_manager = db_manager
        
        self.setWindowTitle(title)
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 提醒内容
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        # 标记为已完成选项
        self.complete_checkbox = QCheckBox("标记为已完成")
        self.complete_checkbox.setChecked(True)
        layout.addWidget(self.complete_checkbox)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        
        snooze_button = QPushButton("稍后提醒")
        snooze_button.clicked.connect(self.snooze)
        
        button_layout.addWidget(snooze_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def accept(self):
        """处理确定按钮"""
        # 如果选中了标记为已完成，更新数据库
        if self.complete_checkbox.isChecked():
            self.db_manager.mark_reminder_completed(self.reminder_id)
            print(f"提醒 #{self.reminder_id} 已标记为完成")
        
        super().accept()
    
    def snooze(self):
        """延迟提醒"""
        # 延迟15分钟
        now = QDateTime.currentDateTime()
        new_time = now.addSecs(15 * 60).time().toString("HH:mm:ss")
        
        # 更新提醒时间
        self.db_manager.update_reminder(
            self.reminder_id, 
            time=new_time
        )
        
        print(f"提醒 #{self.reminder_id} 已延迟到 {new_time}")
        QMessageBox.information(self, "延迟提醒", f"提醒已延迟到 {new_time}")
        self.reject()

def show_reminder(parent, db_manager, title, content, reminder_id):
    """显示提醒对话框"""
    dialog = ReminderDialog(title, content, reminder_id, db_manager, parent)
    return dialog.exec_()

# 单例模式
_reminder_manager_instance = None

def get_reminder_manager(db_manager=None, user_id=None):
    """
    获取提醒管理器单例
    
    参数:
        db_manager: 数据库管理器实例，首次调用时必须提供
        user_id: 用户ID，首次调用时必须提供
        
    返回:
        ReminderManager: 提醒管理器实例
    """
    global _reminder_manager_instance
    if _reminder_manager_instance is None:
        if db_manager is None or user_id is None:
            raise ValueError("首次获取提醒管理器时必须提供数据库管理器和用户ID")
        _reminder_manager_instance = ReminderManager(db_manager, user_id)
    return _reminder_manager_instance 