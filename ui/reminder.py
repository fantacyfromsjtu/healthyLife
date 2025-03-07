#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提醒设置界面
用于添加、编辑和管理健康相关提醒
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QComboBox, QDateEdit, QTimeEdit, QLineEdit, QTableWidget,
                           QTableWidgetItem, QMessageBox, QHeaderView, QGridLayout,
                           QDialog, QFrame, QTextEdit, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon, QFont

import datetime

class ReminderDialog(QDialog):
    """创建或编辑提醒的对话框"""
    
    # 信号
    reminder_updated = pyqtSignal()
    
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        
        self.setWindowTitle("添加提醒")
        self.resize(500, 400)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        
        # 提醒信息组
        reminder_group = QGroupBox("提醒信息")
        reminder_layout = QFormLayout()
        reminder_group.setLayout(reminder_layout)
        
        # 日期选择
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        reminder_layout.addRow(QLabel("日期:"), self.date_edit)
        
        # 时间选择
        self.time_edit = QTimeEdit(QTime.currentTime().addSecs(3600))  # 默认一小时后
        self.time_edit.setDisplayFormat("HH:mm")
        reminder_layout.addRow(QLabel("时间:"), self.time_edit)
        
        # 提醒类型
        self.reminder_type = QComboBox()
        self.reminder_type.addItems(["饮食", "运动", "睡眠", "学习", "其他"])
        reminder_layout.addRow(QLabel("类型:"), self.reminder_type)
        
        # 提醒内容
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("请输入提醒内容...")
        reminder_layout.addRow(QLabel("内容:"), self.content_edit)
        
        main_layout.addWidget(reminder_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_reminder)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def save_reminder(self):
        """保存提醒"""
        try:
            # 获取用户输入
            date = self.date_edit.date().toString("yyyy-MM-dd")
            time = self.time_edit.time().toString("HH:mm")  # 不需要秒
            reminder_type = self.reminder_type.currentText()
            content = self.content_edit.toPlainText()
            
            # 基本验证
            if not content.strip():
                QMessageBox.warning(self, "警告", "请输入提醒内容")
                return
            
            # 将数据保存到数据库
            print(f"保存提醒: 日期={date}, 时间={time}, 类型={reminder_type}, 内容={content}")
            reminder_id = self.db_manager.add_reminder(self.user_id, date, time, reminder_type, content)
            
            if reminder_id:
                print(f"提醒已保存，ID={reminder_id}")
                QMessageBox.information(self, "成功", "提醒已成功添加！")
                self.reminder_updated.emit()  # 发出信号
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "保存提醒失败，请重试")
                
        except Exception as e:
            print(f"保存提醒时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
            
    def closeEvent(self, event):
        """处理关闭事件"""
        super().closeEvent(event)


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
        
        dialog = ReminderDialog(self.db_manager, self.user_id, self)
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