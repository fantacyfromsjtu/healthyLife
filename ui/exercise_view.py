from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView, QFrame,
                             QComboBox, QDateEdit, QTimeEdit, QMenu, QAction)
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

from ui.exercise_record import ExerciseRecordDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

class ExerciseView(QWidget):
    """运动记录视图"""
    
    def __init__(self, user_id, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        self.current_date = QDate.currentDate()
        self.exercise_records = []
        
        self.init_ui()
        self.load_exercise_records()
    
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # 顶部控制面板
        control_panel = QHBoxLayout()
        
        # 上一天
        self.prev_day_btn = QPushButton()
        self.prev_day_btn.setObjectName("iconButton")
        self.prev_day_btn.setText("◀ 前一天")
        self.prev_day_btn.clicked.connect(self.prev_day)
        control_panel.addWidget(self.prev_day_btn)
        
        # 日期选择器
        self.date_edit = QDateEdit(self.current_date)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.dateChanged.connect(self.date_changed)
        control_panel.addWidget(self.date_edit)
        
        # 下一天
        self.next_day_btn = QPushButton()
        self.next_day_btn.setObjectName("iconButton")
        self.next_day_btn.setText("后一天 ▶")
        self.next_day_btn.clicked.connect(self.next_day)
        control_panel.addWidget(self.next_day_btn)
        
        # 添加按钮
        self.add_btn = QPushButton("添加运动记录")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_exercise_record)
        control_panel.addStretch()
        control_panel.addWidget(self.add_btn)
        
        main_layout.addLayout(control_panel)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # 卡路里消耗统计
        calories_frame = QFrame()
        calories_frame.setObjectName("statsFrame")
        calories_layout = QVBoxLayout(calories_frame)
        
        self.calories_title = QLabel("今日消耗卡路里")
        self.calories_title.setAlignment(Qt.AlignCenter)
        calories_layout.addWidget(self.calories_title)
        
        self.calories_value = QLabel("0")
        self.calories_value.setAlignment(Qt.AlignCenter)
        self.calories_value.setObjectName("statsValue")
        calories_layout.addWidget(self.calories_value)
        
        stats_layout.addWidget(calories_frame)
        
        # 运动时长统计
        duration_frame = QFrame()
        duration_frame.setObjectName("statsFrame")
        duration_layout = QVBoxLayout(duration_frame)
        
        self.duration_title = QLabel("今日运动时长")
        self.duration_title.setAlignment(Qt.AlignCenter)
        duration_layout.addWidget(self.duration_title)
        
        self.duration_value = QLabel("0 分钟")
        self.duration_value.setAlignment(Qt.AlignCenter)
        self.duration_value.setObjectName("statsValue")
        duration_layout.addWidget(self.duration_value)
        
        stats_layout.addWidget(duration_frame)
        
        # 运动次数统计
        count_frame = QFrame()
        count_frame.setObjectName("statsFrame")
        count_layout = QVBoxLayout(count_frame)
        
        self.count_title = QLabel("今日运动次数")
        self.count_title.setAlignment(Qt.AlignCenter)
        count_layout.addWidget(self.count_title)
        
        self.count_value = QLabel("0")
        self.count_value.setAlignment(Qt.AlignCenter)
        self.count_value.setObjectName("statsValue")
        count_layout.addWidget(self.count_value)
        
        stats_layout.addWidget(count_frame)
        
        main_layout.addLayout(stats_layout)
        
        # 图表展示
        self.chart_widget = QWidget()
        chart_layout = QVBoxLayout(self.chart_widget)
        
        # 创建图表
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        main_layout.addWidget(self.chart_widget)
        
        # 运动记录表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["时间", "运动", "分类", "持续时间", "强度", "卡路里消耗"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.records_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.records_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.records_table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.records_table)
        
        self.setLayout(main_layout)
    
    def load_exercise_records(self):
        """加载指定日期的运动记录"""
        date_str = self.current_date.toString("yyyy-MM-dd")
        try:
            self.exercise_records = self.db_manager.get_exercise_records_by_date(self.user_id, date_str)
            self.update_records_table()
            self.update_stats()
            self.update_chart()
        except Exception as e:
            logging.error(f"加载运动记录时出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"加载运动记录时出错: {str(e)}")
    
    def update_records_table(self):
        """更新运动记录表格"""
        self.records_table.setRowCount(0)
        
        if not self.exercise_records:
            return
            
        # 填充表格
        for row, record in enumerate(self.exercise_records):
            self.records_table.insertRow(row)
            
            # 时间
            time_item = QTableWidgetItem(record[8].split()[1][:5] if ' ' in record[8] else record[8][:5])
            self.records_table.setItem(row, 0, time_item)
            
            # 运动名称
            name_item = QTableWidgetItem(record[2])
            self.records_table.setItem(row, 1, name_item)
            
            # 分类
            category_item = QTableWidgetItem(record[3])
            self.records_table.setItem(row, 2, category_item)
            
            # 持续时间
            duration_item = QTableWidgetItem(f"{record[4]} 分钟")
            self.records_table.setItem(row, 3, duration_item)
            
            # 强度
            intensity_item = QTableWidgetItem(record[5])
            self.records_table.setItem(row, 4, intensity_item)
            
            # 卡路里消耗
            calories_item = QTableWidgetItem(f"{record[6]} kcal")
            self.records_table.setItem(row, 5, calories_item)
            
            # 保存记录ID到第一列
            time_item.setData(Qt.UserRole, record[0])
    
    def update_stats(self):
        """更新统计信息"""
        if not self.exercise_records:
            self.calories_value.setText("0")
            self.duration_value.setText("0 分钟")
            self.count_value.setText("0")
            return
            
        # 计算总卡路里消耗
        total_calories = sum(record[6] for record in self.exercise_records)
        self.calories_value.setText(f"{total_calories}")
        
        # 计算总运动时长
        total_duration = sum(record[4] for record in self.exercise_records)
        self.duration_value.setText(f"{total_duration} 分钟")
        
        # 计算运动次数
        self.count_value.setText(f"{len(self.exercise_records)}")
    
    def update_chart(self):
        """更新图表"""
        self.figure.clear()
        
        # 如果没有记录，显示提示
        if not self.exercise_records:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "没有运动记录", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return
            
        # 准备数据
        times = []
        calories = []
        exercise_names = []
        
        for record in self.exercise_records:
            time_str = record[8].split()[1] if ' ' in record[8] else record[8]
            times.append(datetime.strptime(time_str[:5], "%H:%M"))
            calories.append(record[6])
            exercise_names.append(record[2])
        
        # 绘制卡路里消耗图表
        ax = self.figure.add_subplot(111)
        bars = ax.bar(times, calories, width=0.02, alpha=0.7)
        
        # 设置样式
        ax.set_title("今日运动消耗卡路里分布")
        ax.set_xlabel("时间")
        ax.set_ylabel("卡路里 (kcal)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        
        # 添加标签
        for i, (bar, name) in enumerate(zip(bars, exercise_names)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                    name, ha='center', va='bottom', rotation=45, fontsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def add_exercise_record(self):
        """添加运动记录"""
        dialog = ExerciseRecordDialog(self.user_id, self.db_manager, self)
        dialog.record_added.connect(self.load_exercise_records)
        dialog.exec_()
    
    def edit_exercise_record(self, record_id):
        """编辑运动记录"""
        dialog = ExerciseRecordDialog(self.user_id, self.db_manager, self, record_id)
        dialog.record_added.connect(self.load_exercise_records)
        dialog.exec_()
    
    def delete_exercise_record(self, record_id):
        """删除运动记录"""
        confirm = QMessageBox.question(self, "确认删除", "确定要删除这条运动记录吗？",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                success = self.db_manager.delete_exercise_record(record_id)
                if success:
                    QMessageBox.information(self, "成功", "运动记录已删除!")
                    self.load_exercise_records()
                else:
                    QMessageBox.warning(self, "错误", "删除运动记录失败，请重试!")
            except Exception as e:
                logging.error(f"删除运动记录时出错: {str(e)}")
                QMessageBox.warning(self, "错误", f"删除运动记录时出错: {str(e)}")
    
    def show_context_menu(self, position):
        """显示上下文菜单"""
        # 获取选中的行
        indexes = self.records_table.selectedIndexes()
        if not indexes:
            return
            
        # 获取记录ID
        record_id = self.records_table.item(indexes[0].row(), 0).data(Qt.UserRole)
        
        # 创建菜单
        menu = QMenu(self)
        edit_action = QAction("编辑", self)
        delete_action = QAction("删除", self)
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        
        # 连接信号
        edit_action.triggered.connect(lambda: self.edit_exercise_record(record_id))
        delete_action.triggered.connect(lambda: self.delete_exercise_record(record_id))
        
        # 显示菜单
        menu.exec_(self.records_table.mapToGlobal(position))
    
    def prev_day(self):
        """前一天"""
        self.current_date = self.current_date.addDays(-1)
        self.date_edit.setDate(self.current_date)
    
    def next_day(self):
        """后一天"""
        self.current_date = self.current_date.addDays(1)
        self.date_edit.setDate(self.current_date)
    
    def date_changed(self, date):
        """日期改变"""
        self.current_date = date
        self.load_exercise_records()
    
    def update_date(self, date):
        """更新当前显示的日期，并重新加载数据
        
        参数:
        - date: 可以是字符串(yyyy-MM-dd)或QDate对象
        """
        try:
            if isinstance(date, str):
                # 如果是字符串格式，转换为QDate对象
                q_date = QDate.fromString(date, "yyyy-MM-dd")
                if q_date.isValid():
                    self.date_edit.setDate(q_date)
                else:
                    print(f"无效的日期字符串格式: {date}")
            else:
                # 假设已经是QDate对象
                self.date_edit.setDate(date)
                
            # 在设置日期后加载运动记录
            self.load_exercise_records()
        except Exception as e:
            print(f"更新运动视图日期时出错: {str(e)}")
    
    def generate_summary(self, start_date, end_date):
        """生成指定日期范围的运动总结"""
        try:
            # 获取日期范围内的运动记录摘要
            summary = self.db_manager.get_weekly_exercise_summary(
                self.user_id, 
                start_date.toString("yyyy-MM-dd"), 
                end_date.toString("yyyy-MM-dd")
            )
            
            # 如果没有记录，返回空结果
            if not summary:
                return {
                    "total_exercises": 0,
                    "total_duration": 0,
                    "total_calories": 0,
                    "exercise_categories": []
                }
            
            # 处理结果
            categories = {}
            total_exercises = 0
            total_duration = 0
            total_calories = 0
            
            for record in summary:
                total_exercises += 1
                total_duration += record[4]  # duration字段
                total_calories += record[6]  # calories_burned字段
                
                category = record[3]  # category字段
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
            
            # 格式化分类数据
            category_data = [{"name": name, "count": count} for name, count in categories.items()]
            
            return {
                "total_exercises": total_exercises,
                "total_duration": total_duration,
                "total_calories": total_calories,
                "exercise_categories": category_data
            }
        except Exception as e:
            logging.error(f"生成运动总结时出错: {str(e)}")
            return None 