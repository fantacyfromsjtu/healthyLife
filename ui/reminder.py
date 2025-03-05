#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提醒设置界面
用于添加、编辑和管理健康相关提醒
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QComboBox, QDateEdit, QTimeEdit, QLineEdit, QTableWidget,
                           QTableWidgetItem, QMessageBox, QHeaderView, QGridLayout,
                           QDialog, QFrame)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

import datetime

class ReminderDialog(QDialog):
    """提醒创建/编辑对话框"""
    
    # 定义信号，提醒添加或更新后发出
    reminder_updated = pyqtSignal()
    
    def __init__(self, db_manager, user_id, parent=None, reminder_id=None):
        """
        初始化提醒对话框
        
        参数:
            db_manager: 数据库管理器
            user_id (int): 用户ID
            parent: 父窗口
            reminder_id (int, optional): 提醒ID，如果提供则为编辑模式
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.reminder_id = reminder_id
        self.reminder_data = None
        
        # 如果有提醒ID，则加载该提醒数据
        if reminder_id:
            self.load_reminder_data()
            self.setWindowTitle("编辑提醒")
        else:
            self.setWindowTitle("添加提醒")
        
        self.init_ui()
        
    def load_reminder_data(self):
        """加载提醒数据"""
        reminders = self.db_manager.get_reminders_by_user_date(self.user_id)
        for r in reminders:
            if r['id'] == self.reminder_id:
                self.reminder_data = r
                break
    
    def init_ui(self):
        """初始化用户界面"""
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 提醒类型
        type_layout = QHBoxLayout()
        type_label = QLabel("提醒类型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["锻炼", "吃饭", "睡觉"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 日期
        date_layout = QHBoxLayout()
        date_label = QLabel("日期:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        # 时间
        time_layout = QHBoxLayout()
        time_label = QLabel("时间:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        layout.addLayout(time_layout)
        
        # 内容
        content_layout = QHBoxLayout()
        content_label = QLabel("提醒内容:")
        self.content_edit = QLineEdit()
        content_layout.addWidget(content_label)
        content_layout.addWidget(self.content_edit)
        layout.addLayout(content_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_reminder)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 如果是编辑模式，填充已有数据
        if self.reminder_data:
            self.fill_form_with_data()
    
    def fill_form_with_data(self):
        """用已有数据填充表单"""
        if not self.reminder_data:
            return
            
        # 设置提醒类型
        reminder_type = self.reminder_data['reminder_type']
        index = self.type_combo.findText(reminder_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # 设置日期
        try:
            date = QDate.fromString(self.reminder_data['date'], "yyyy-MM-dd")
            self.date_edit.setDate(date)
        except:
            pass
        
        # 设置时间
        try:
            time = QTime.fromString(self.reminder_data['time'], "HH:mm")
            self.time_edit.setTime(time)
        except:
            pass
        
        # 设置内容
        self.content_edit.setText(self.reminder_data['content'] or "")
    
    def save_reminder(self):
        """保存提醒数据"""
        reminder_type = self.type_combo.currentText()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("HH:mm")
        content = self.content_edit.text()
        
        # 简单验证
        if not content:
            QMessageBox.warning(self, "提示", "请输入提醒内容")
            return
        
        # 检查日期是否已过
        current_date = datetime.datetime.now().date()
        selected_date = self.date_edit.date().toPyDate()
        current_time = datetime.datetime.now().time()
        selected_time = self.time_edit.time().toPyTime()
        
        if selected_date < current_date or (selected_date == current_date and selected_time < current_time):
            response = QMessageBox.question(
                self, 
                "确认", 
                "您选择的时间已经过去，确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if response == QMessageBox.No:
                return
        
        try:
            # 如果是编辑模式
            if self.reminder_id:
                success = self.db_manager.update_reminder(
                    self.reminder_id, 
                    date=date, 
                    time=time, 
                    content=content
                )
                if success:
                    QMessageBox.information(self, "成功", "提醒已更新")
                    self.reminder_updated.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", "更新提醒失败")
            else:
                # 添加新提醒
                reminder_id = self.db_manager.add_reminder(
                    self.user_id, 
                    date, 
                    time, 
                    reminder_type, 
                    content
                )
                if reminder_id:
                    QMessageBox.information(self, "成功", "提醒已添加")
                    self.reminder_updated.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", "添加提醒失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存提醒时发生错误: {str(e)}")


class ReminderView(QWidget):
    """提醒管理视图"""
    
    def __init__(self, user_id, db_manager, parent=None):
        """
        初始化提醒视图
        
        参数:
            user_id (int): 用户ID
            db_manager: 数据库管理器
            parent: 父窗口
        """
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        
        self.init_ui()
        self.load_reminders()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("我的健康提醒")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加提醒")
        self.add_btn.clicked.connect(self.add_reminder)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑提醒")
        self.edit_btn.clicked.connect(self.edit_reminder)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除提醒")
        self.delete_btn.clicked.connect(self.delete_reminder)
        btn_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_reminders)
        btn_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 提醒列表
        self.reminder_table = QTableWidget()
        self.reminder_table.setColumnCount(5)
        self.reminder_table.setHorizontalHeaderLabels(["ID", "类型", "日期", "时间", "内容"])
        self.reminder_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.reminder_table.verticalHeader().setVisible(False)
        self.reminder_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.reminder_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reminder_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.reminder_table)
        
        self.setLayout(layout)
    
    def load_reminders(self):
        """加载用户的提醒列表"""
        # 清空表格
        self.reminder_table.setRowCount(0)
        
        # 获取提醒数据
        reminders = self.db_manager.get_reminders_by_user_date(self.user_id)
        
        # 填充表格
        for row, reminder in enumerate(reminders):
            self.reminder_table.insertRow(row)
            
            # 隐藏ID列，但保留数据
            id_item = QTableWidgetItem(str(reminder['id']))
            self.reminder_table.setItem(row, 0, id_item)
            
            # 类型
            type_item = QTableWidgetItem(reminder['reminder_type'])
            self.reminder_table.setItem(row, 1, type_item)
            
            # 日期
            date_item = QTableWidgetItem(reminder['date'])
            self.reminder_table.setItem(row, 2, date_item)
            
            # 时间
            time_item = QTableWidgetItem(reminder['time'])
            self.reminder_table.setItem(row, 3, time_item)
            
            # 内容
            content_item = QTableWidgetItem(reminder['content'])
            self.reminder_table.setItem(row, 4, content_item)
            
            # 如果已完成，设置灰色
            if reminder['is_completed']:
                for col in range(5):
                    self.reminder_table.item(row, col).setBackground(Qt.lightGray)
        
        # 隐藏ID列
        self.reminder_table.hideColumn(0)
        
        # 调整列宽
        self.reminder_table.resizeColumnsToContents()
    
    def add_reminder(self):
        """添加新提醒"""
        dialog = ReminderDialog(self.db_manager, self.user_id, self)
        dialog.reminder_updated.connect(self.load_reminders)
        dialog.exec_()
    
    def edit_reminder(self):
        """编辑选中的提醒"""
        selected_rows = self.reminder_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一个提醒")
            return
        
        row = selected_rows[0].row()
        reminder_id = int(self.reminder_table.item(row, 0).text())
        
        dialog = ReminderDialog(self.db_manager, self.user_id, self, reminder_id)
        dialog.reminder_updated.connect(self.load_reminders)
        dialog.exec_()
    
    def delete_reminder(self):
        """删除选中的提醒"""
        selected_rows = self.reminder_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一个提醒")
            return
        
        row = selected_rows[0].row()
        reminder_id = int(self.reminder_table.item(row, 0).text())
        
        response = QMessageBox.question(
            self, 
            "确认删除", 
            "您确定要删除这个提醒吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if response == QMessageBox.Yes:
            success = self.db_manager.delete_reminder(reminder_id)
            if success:
                QMessageBox.information(self, "成功", "提醒已删除")
                self.load_reminders()
            else:
                QMessageBox.critical(self, "错误", "删除提醒失败") 