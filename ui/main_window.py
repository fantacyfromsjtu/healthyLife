import datetime
from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QStackedWidget,
                            QAction, QToolBar, QMessageBox, QFrame, QTabWidget, QInputDialog, QMenu)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor
from ui.diet_view import DietView
from ui.exercise_view import ExerciseView
from utils.health_analyzer import HealthAnalyzer
from utils.report_generator import WeeklyReportGenerator
import os

# 导入其他需要的视图类
# 为缺少的视图创建基本视图类
class BaseView(QWidget):
    """基本视图类，用于统一视图接口"""
    
    def __init__(self, user_id, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 默认标题
        self.title_label = QLabel("数据视图")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # 默认内容标签
        self.content_label = QLabel("暂无数据")
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setObjectName("contentView")
        layout.addWidget(self.content_label)
        
        # 使用 stretch 填充
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_date(self, selected_date):
        """更新视图显示的日期"""
        try:
            # 检查日期类型，如果是字符串则转换为QDate
            if isinstance(selected_date, str):
                q_date = QDate.fromString(selected_date, "yyyy-MM-dd")
                date_str = selected_date
            else:
                q_date = selected_date
                date_str = selected_date.toString("yyyy-MM-dd")
                
            # 更新内容
            self.content_label.setText(f"日期: {date_str}\n暂无数据")
        except Exception as e:
            print(f"更新日期出错: {str(e)}")
            self.content_label.setText("日期显示出错")
    
    def load_data(self):
        """加载数据，子类应重写此方法"""
        pass


class SleepView(BaseView):
    """睡眠记录视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        # 调用父类初始化
        super().init_ui()
        
        # 设置标题
        self.title_label.setText("睡眠记录")
        
        # 自定义内容
        self.content_layout = QVBoxLayout()
        
        # 创建表格展示
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        self.sleep_table = QTableWidget()
        self.sleep_table.setColumnCount(5)
        self.sleep_table.setHorizontalHeaderLabels(["入睡时间", "起床时间", "睡眠时长", "质量", "备注"])
        self.sleep_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sleep_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sleep_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为不可编辑
        
        # 允许右键菜单
        self.sleep_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sleep_table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.content_layout.addWidget(self.sleep_table)
        
        # 添加一个添加按钮
        self.add_button = QPushButton("添加睡眠记录")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_sleep_record)
        
        self.content_layout.addWidget(self.add_button)
        
        # 替换原始布局中的内容标签
        layout = self.layout()
        layout.removeWidget(self.content_label)
        self.content_label.deleteLater()
        layout.addLayout(self.content_layout)
        
    def update_date(self, selected_date):
        """更新视图显示的日期"""
        try:
            # 保存当前日期
            self.current_date = selected_date
            
            # 加载睡眠记录
            self.load_sleep_records()
        except Exception as e:
            print(f"更新睡眠视图日期时出错: {str(e)}")
            
    def load_sleep_records(self):
        """加载睡眠记录"""
        try:
            # 确保导入QDate和QTableWidgetItem
            from PyQt5.QtCore import QDate
            from PyQt5.QtWidgets import QTableWidgetItem
            
            # 确保有日期
            if not hasattr(self, 'current_date'):
                self.current_date = QDate.currentDate().toString("yyyy-MM-dd")
                
            # 从当前日期获取记录
            if isinstance(self.current_date, QDate):
                date_str = self.current_date.toString("yyyy-MM-dd")
            else:
                date_str = self.current_date
                
            # 加载睡眠记录
            records = self.db_manager.get_sleep_records_by_date(self.user_id, date_str)
            
            # 清空表格
            self.sleep_table.setRowCount(0)
            
            # 如果没有记录
            if not records or len(records) == 0:
                self.title_label.setText(f"睡眠记录 ({date_str}) - 暂无数据")
                return
                
            # 设置表格行数
            self.sleep_table.setRowCount(len(records))
            
            # 填充表格
            for row, record in enumerate(records):
                # 提取记录详情
                record_id = record[0]
                sleep_date = record[3]
                sleep_time = record[4]
                wake_date = record[5]
                wake_time = record[6]
                duration = record[7]  # 单位为分钟
                quality = record[8]
                notes = record[9]
                
                # 计算可读的睡眠时长
                hours = duration // 60
                minutes = duration % 60
                duration_text = f"{hours}小时{minutes}分钟"
                
                # 将睡眠质量转换为文本
                quality_map = {0: "未评价", 1: "很差", 2: "较差", 3: "一般", 4: "良好", 5: "优秀"}
                quality_text = quality_map.get(quality, "未知")
                
                # 设置单元格内容
                self.sleep_table.setItem(row, 0, QTableWidgetItem(f"{sleep_date} {sleep_time}"))
                self.sleep_table.setItem(row, 1, QTableWidgetItem(f"{wake_date} {wake_time}"))
                self.sleep_table.setItem(row, 2, QTableWidgetItem(duration_text))
                self.sleep_table.setItem(row, 3, QTableWidgetItem(quality_text))
                self.sleep_table.setItem(row, 4, QTableWidgetItem(notes))
                
                # 存储记录ID供后续操作使用
                for col in range(5):
                    self.sleep_table.item(row, col).setData(Qt.UserRole, record_id)
                    
            # 更新标题
            self.title_label.setText(f"睡眠记录 ({date_str}) - {len(records)}条")
                
        except Exception as e:
            print(f"加载睡眠记录时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def add_sleep_record(self):
        """添加睡眠记录"""
        from ui.sleep_record import SleepRecordDialog
        dialog = SleepRecordDialog(self.user_id, self.db_manager, self)
        
        # 在记录添加后刷新视图
        def on_record_added():
            self.load_sleep_records()
            
        dialog.record_added.connect(on_record_added)
        dialog.exec_()
        
    def edit_sleep_record(self, record_id):
        """编辑睡眠记录"""
        from ui.sleep_record import SleepRecordDialog
        dialog = SleepRecordDialog(self.user_id, self.db_manager, self, record_id)
        
        # 在记录更新后刷新视图
        def on_record_added():
            self.load_sleep_records()
            
        dialog.record_added.connect(on_record_added)
        dialog.exec_()
        
    def delete_sleep_record(self, record_id):
        """删除睡眠记录"""
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除这条睡眠记录吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_sleep_record(record_id):
                    QMessageBox.information(self, "成功", "睡眠记录已删除。")
                    # 重新加载记录
                    self.load_sleep_records()
                else:
                    QMessageBox.warning(self, "失败", "删除睡眠记录失败，请重试。")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除睡眠记录时出错: {str(e)}")
                
    def show_context_menu(self, position):
        """显示右键菜单"""
        # 获取当前选中行
        indexes = self.sleep_table.selectedIndexes()
        if indexes:
            # 创建菜单
            menu = QMenu()
            
            # 获取记录ID
            record_id = indexes[0].data(Qt.UserRole)
            
            # 添加编辑选项
            edit_action = menu.addAction("编辑")
            edit_action.triggered.connect(lambda: self.edit_sleep_record(record_id))
            
            # 添加删除选项
            delete_action = menu.addAction("删除")
            delete_action.triggered.connect(lambda: self.delete_sleep_record(record_id))
            
            # 显示菜单
            menu.exec_(self.sleep_table.viewport().mapToGlobal(position))
            
    def load_data(self):
        """加载数据"""
        self.load_sleep_records()


class PlanView(BaseView):
    """计划安排视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("计划安排")
        
        # 创建一个布局来显示提醒列表
        layout = self.layout()
        
        # 添加一个标签用于显示提醒列表
        self.reminder_label = QLabel("暂无提醒计划")
        self.reminder_label.setWordWrap(True)
        self.reminder_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.reminder_label.setObjectName("reminderLabel")
        layout.addWidget(self.reminder_label)
        
        # 替换原有的默认内容标签
        layout.removeWidget(self.content_label)
        self.content_label.hide()
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        
        # 检查日期类型，如果是字符串则使用原样显示
        if isinstance(selected_date, str):
            date_str = selected_date
            self.current_date = date_str
        else:
            date_str = selected_date.toString('yyyy-MM-dd')
            self.current_date = date_str
        
        self.title_label.setText(f"计划安排 - {date_str}")
        
        # 加载该日期的提醒数据
        self.load_reminders()
    
    def load_reminders(self):
        """加载提醒数据"""
        try:
            # 检查是否已设置当前日期
            if not hasattr(self, 'current_date'):
                self.current_date = QDate.currentDate().toString('yyyy-MM-dd')
            
            # 从数据库加载提醒
            reminders = self.db_manager.get_reminders_by_user_date(self.user_id, self.current_date)
            
            if not reminders or len(reminders) == 0:
                self.reminder_label.setText(f"日期: {self.current_date}\n\n暂无提醒计划")
                return
            
            # 构建提醒文本
            reminder_text = f"<h3>日期: {self.current_date}</h3>"
            reminder_text += "<ul>"
            
            for reminder in reminders:
                # 获取提醒数据
                reminder_id = reminder[0]
                reminder_time = reminder[3]  # 时间
                reminder_type = reminder[4]  # 类型
                reminder_content = reminder[5]  # 内容
                is_completed = reminder[6]  # 是否完成
                
                # 根据完成状态设置样式
                status = "✓" if is_completed else "○"
                style = "text-decoration: line-through; color: gray;" if is_completed else ""
                
                reminder_text += f'<li style="{style}"><b>{reminder_time}</b> - {reminder_type}: {reminder_content} {status}</li>'
            
            reminder_text += "</ul>"
            self.reminder_label.setText(reminder_text)
            
        except Exception as e:
            print(f"加载提醒数据出错: {str(e)}")
            self.reminder_label.setText(f"日期: {self.current_date}\n\n加载提醒数据出错")
    
    def load_data(self):
        """加载数据"""
        self.load_reminders()


class MainWindow(QMainWindow):
    def __init__(self, user_id, username, db_manager):
        """初始化主窗口"""
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.db_manager = db_manager
        print(f"正在创建主窗口实例...")
        
        # 初始化提醒管理器
        from utils.reminder import ReminderManager, show_reminder
        self.reminder_manager = ReminderManager(db_manager, user_id, self)
        self.reminder_manager.reminder_triggered.connect(self.on_reminder_triggered)
        print("提醒管理器已连接到主窗口")
        
        self.init_ui()
        
        # 加载初始数据
        self.load_date_data()
        self.update_weekly_summary()
        
        print("主窗口实例化完成")
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(f'健康生活 - {self.username}')
        self.resize(1280, 900)  # 增大窗口尺寸
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)  # 增加组件间距
        central_widget.setLayout(main_layout)
        
        # 左侧日历和功能区
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 添加用户欢迎标签
        welcome_label = QLabel(f"欢迎, {self.username}!")
        welcome_label.setObjectName("welcomeLabel")
        left_layout.addWidget(welcome_label)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        self.calendar.setObjectName("mainCalendar")
        self.calendar.selectionChanged.connect(self.date_selected)
        left_layout.addWidget(self.calendar)
        
        # 功能区 - 添加记录和计划
        function_layout = QHBoxLayout()
        function_layout.setSpacing(10)
        
        # 添加记录按钮
        self.add_record_button = QPushButton("添加记录")
        self.add_record_button.setObjectName("primaryButton")
        self.add_record_button.setMinimumHeight(40)
        self.add_record_button.clicked.connect(self.add_record)
        function_layout.addWidget(self.add_record_button)
        
        # 添加计划按钮
        self.add_plan_button = QPushButton("添加计划")
        self.add_plan_button.setObjectName("secondaryButton")
        self.add_plan_button.setMinimumHeight(40)
        self.add_plan_button.clicked.connect(self.add_plan)
        function_layout.addWidget(self.add_plan_button)
        
        left_layout.addLayout(function_layout)
        
        # 右侧显示区域
        right_widget = QFrame()
        right_widget.setObjectName("rightPanel")
        right_widget.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 当前日期显示
        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        self.update_date_label()
        right_layout.addWidget(self.date_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("separator")
        right_layout.addWidget(separator)
        
        # 显示模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel("显示模式:")
        mode_label.setObjectName("modeLabel")
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("modeCombo")
        self.mode_combo.addItems(["饮食", "运动", "睡眠", "计划"])
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)
        self.mode_combo.setMinimumHeight(30)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        right_layout.addLayout(mode_layout)
        
        # 内容区域 - 使用堆叠部件切换不同视图
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # 创建各种视图
        self.diet_view = DietView(self.user_id, self.db_manager)
        self.exercise_view = ExerciseView(self.user_id, self.db_manager)
        self.sleep_view = SleepView(self.user_id, self.db_manager)
        self.plan_view = PlanView(self.user_id, self.db_manager)
        
        # 添加视图到堆叠部件
        self.content_stack.addWidget(self.diet_view)
        self.content_stack.addWidget(self.exercise_view)
        self.content_stack.addWidget(self.sleep_view)
        self.content_stack.addWidget(self.plan_view)
        
        right_layout.addWidget(self.content_stack)
        
        # 将左右区域添加到主布局
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 2)
        
        # 创建工具栏
        self.create_toolbar()
        
    def create_toolbar(self):
        """创建工具栏"""
        # 创建简化版的工具栏，只包含必要功能
        toolbar = QToolBar("快速工具栏")
        self.addToolBar(toolbar)
        
        # 添加个人信息按钮到工具栏
        profile_action = QAction("个人信息", self)
        profile_action.triggered.connect(self.edit_profile)
        toolbar.addAction(profile_action)
        
        # 添加周报按钮到工具栏
        weekly_report_action = QAction("周报摘要", self)
        weekly_report_action.triggered.connect(self.show_weekly_report)
        toolbar.addAction(weekly_report_action)
        
        # 添加查看提醒按钮到工具栏
        view_reminders_action = QAction("查看提醒", self)
        view_reminders_action.triggered.connect(self.view_reminders)
        toolbar.addAction(view_reminders_action)
        
        # 添加退出按钮到工具栏
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        toolbar.addAction(exit_action)
        
    def update_date_label(self):
        """更新日期标签"""
        selected_date = self.calendar.selectedDate()
        self.date_label.setText(f"当前日期: {selected_date.toString('yyyy-MM-dd')}")
        
    def date_selected(self):
        """日期选择改变事件"""
        self.update_date_label()
        # 加载所选日期的数据
        self.load_date_data()
        
    def mode_changed(self, index):
        """显示模式改变事件"""
        self.content_stack.setCurrentIndex(index)
        
        # 确保当前视图的日期是最新的
        self.update_current_view()
        
    def update_current_view(self):
        """更新当前显示的视图"""
        current_index = self.content_stack.currentIndex()
        
        # 获取当前QDate对象和它的字符串表示
        selected_qdate = self.calendar.selectedDate()
        selected_date = selected_qdate.toString("yyyy-MM-dd")
        
        # 获取当前视图
        current_view = self.content_stack.currentWidget()
        
        print(f"更新视图: current_index={current_index}, 视图类型={type(current_view).__name__}")
        
        # 检查当前视图类型并调用适当的方法
        from ui.diet_view import DietView
        
        if hasattr(current_view, 'update_date'):
            # 通用视图更新方法 - 传递字符串格式的日期
            current_view.update_date(selected_date)
        elif isinstance(current_view, DietView):
            # DietView特殊处理
            print("检测到DietView，使用特殊更新方法")
            try:
                if hasattr(current_view, 'date_edit'):
                    # 使用QDate对象设置date_edit
                    current_view.date_edit.setDate(selected_qdate)
                    # 加载相应的饮食记录
                    current_view.load_diet_records()
            except Exception as e:
                print(f"更新DietView时出错: {str(e)}")
        else:
            print(f"警告: 未知的视图类型 {type(current_view).__name__}，无法更新")
            
    def load_date_data(self):
        """加载当前选择日期的数据"""
        self.update_current_view()
        
        # 获取当前日期
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        # 根据当前显示的视图类型，加载相应数据
        current_index = self.content_stack.currentIndex()
        current_view = self.content_stack.currentWidget()
        
        print(f"加载日期数据: 日期={selected_date}, 视图索引={current_index}")
        
        # 尝试调用视图的load_data方法（如果存在）
        if hasattr(current_view, 'load_data'):
            try:
                current_view.load_data()
                print(f"已调用 {type(current_view).__name__}.load_data()")
            except Exception as e:
                print(f"调用load_data出错: {str(e)}")
                
        # 特殊处理各种视图类型
        if current_index == 0 and hasattr(self.diet_view, 'load_diet_records'):  # 饮食视图
            self.diet_view.load_diet_records()
        elif current_index == 1 and hasattr(self.exercise_view, 'load_exercise_records'):  # 运动视图
            self.exercise_view.load_exercise_records()
        elif current_index == 2 and hasattr(self.sleep_view, 'load_sleep_records'):  # 睡眠视图
            self.sleep_view.load_sleep_records()
        elif current_index == 3 and hasattr(self.plan_view, 'load_reminders'):  # 计划视图
            self.plan_view.load_reminders()
        
    def add_record(self):
        """添加记录"""
        # 显示一个选项菜单让用户选择要添加的记录类型
        menu = QMenu(self)
        diet_action = menu.addAction("添加饮食记录")
        exercise_action = menu.addAction("添加运动记录")
        sleep_action = menu.addAction("添加睡眠记录")
        
        diet_action.triggered.connect(self.add_diet_record)
        exercise_action.triggered.connect(self.add_exercise_record)
        sleep_action.triggered.connect(self.add_sleep_record)
        
        # 在按钮位置显示菜单
        button = self.sender()
        if button:
            menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
        else:
            menu.exec_(QCursor.pos())
        
    def add_diet_record(self):
        """添加饮食记录"""
        if hasattr(self.diet_view, 'add_diet_record'):
            self.diet_view.add_diet_record()
            # 在添加完成后自动刷新视图
            def refresh_views():
                self.diet_view.load_diet_records()
                self.load_date_data()
            
            # 尝试连接信号
            if hasattr(self.diet_view, 'records_updated'):
                self.diet_view.records_updated.connect(refresh_views)
        else:
            from ui.diet_record import DietRecordDialog
            dialog = DietRecordDialog(self.user_id, self.db_manager, self)
            
            # 在记录添加后刷新视图
            def on_record_added():
                self.diet_view.load_diet_records()
                self.load_date_data()
                
            dialog.record_added.connect(on_record_added)
            dialog.exec_()
        
    def add_exercise_record(self):
        """添加运动记录"""
        from ui.exercise_record import ExerciseRecordDialog
        dialog = ExerciseRecordDialog(self.user_id, self.db_manager, self)
        
        # 在记录添加后刷新视图
        def on_record_added():
            self.exercise_view.load_exercise_records()
            self.load_date_data()
            # 更新每周摘要
            self.update_weekly_summary()
            
        dialog.record_added.connect(on_record_added)
        dialog.exec_()
        
    def add_sleep_record(self):
        """添加睡眠记录"""
        from ui.sleep_record import SleepRecordDialog
        dialog = SleepRecordDialog(self.user_id, self.db_manager, self)
        
        # 在记录添加后刷新视图
        def on_record_added():
            self.sleep_view.load_sleep_records()
            self.load_date_data()
            
        dialog.record_added.connect(on_record_added)
        dialog.exec_()
        
    def add_plan(self):
        """添加提醒计划"""
        from ui.reminder import ReminderDialog
        dialog = ReminderDialog(self.db_manager, self.user_id, self)
        
        # 当提醒更新时，更新计划视图和当前视图
        def on_reminder_updated():
            # 更新计划视图
            if hasattr(self.plan_view, 'load_reminders'):
                self.plan_view.load_reminders()
            
            # 更新当前视图
            self.load_date_data()
            
            # 如果当前是计划视图，还需要额外刷新
            if self.content_stack.currentIndex() == 3:  # 计划视图索引
                self.mode_changed(3)
                
        dialog.reminder_updated.connect(on_reminder_updated)
        dialog.exec_()
        
    def edit_profile(self):
        """编辑个人信息"""
        from ui.profile import ProfileWindow
        profile_window = ProfileWindow(self.user_id, self.username, self.db_manager)
        profile_window.profile_updated.connect(self.update_user_info)
        profile_window.exec_()
        
    def update_user_info(self, user_id, username):
        """更新用户信息后的回调"""
        # 可以在这里更新主窗口中显示的用户信息
        # 例如更新欢迎消息等
        pass
        
    def show_weekly_report(self):
        """显示周报告，包含运动、饮食、睡眠分析及健康建议，并支持导出为PDF"""
        # 获取当前周的起止日期
        today = datetime.datetime.now()
        # 计算本周的第一天（周一）
        week_start = today - datetime.timedelta(days=today.weekday())
        week_start = datetime.datetime(week_start.year, week_start.month, week_start.day)
        # 计算本周的最后一天（周日）
        week_end = week_start + datetime.timedelta(days=6)
        
        # 获取用户信息
        try:
            user_info = self.db_manager.get_user_profile_for_analysis()
        except Exception as e:
            user_info = {}
            print(f"获取用户信息失败: {e}")
        
        # 获取本周的运动、饮食、睡眠数据
        try:
            # 运动数据
            exercise_summary = self.db_manager.get_weekly_exercise_summary(
                week_start.strftime('%Y-%m-%d'), 
                week_end.strftime('%Y-%m-%d')
            )
            
            # 饮食数据
            diet_summary = self.db_manager.get_weekly_diet_summary(
                week_start.strftime('%Y-%m-%d'), 
                week_end.strftime('%Y-%m-%d')
            )
            
            # 睡眠数据
            sleep_summary = self.db_manager.get_weekly_sleep_summary(
                week_start.strftime('%Y-%m-%d'), 
                week_end.strftime('%Y-%m-%d')
            )
        except Exception as e:
            QMessageBox.warning(self, "数据获取错误", f"获取周数据失败: {e}")
            return
        
        # 分析健康数据并生成建议
        analyzer = HealthAnalyzer()
        analysis_results = analyzer.analyze_weekly_data(
            exercise_summary, 
            diet_summary, 
            sleep_summary, 
            user_info
        )
        
        # 创建周报摘要文本
        summary_text = self._generate_weekly_summary_text(analysis_results, week_start, week_end)
        
        # 显示周报摘要对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("本周健康报告")
        msg_box.setText(summary_text)
        msg_box.setDetailedText(self._generate_detailed_report_text(analysis_results))
        
        # 添加导出PDF按钮
        export_btn = msg_box.addButton("导出PDF报告", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Ok)
        
        msg_box.exec_()
        
        # 处理导出PDF请求
        if msg_box.clickedButton() == export_btn:
            self._export_weekly_report_pdf(analysis_results, user_info, week_start, week_end)

    def _generate_weekly_summary_text(self, analysis_results, week_start, week_end):
        """生成周报摘要文本"""
        exercise_stats = analysis_results.get("exercise_stats", {})
        diet_stats = analysis_results.get("diet_stats", {})
        sleep_stats = analysis_results.get("sleep_stats", {})
        
        summary = f"健康周报 ({week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')})\n\n"
        
        # 运动摘要
        summary += "【运动情况】\n"
        summary += f"- 运动天数: {exercise_stats.get('exercise_days', 0)}/7天\n"
        summary += f"- 总运动时间: {exercise_stats.get('total_duration', 0)}分钟\n"
        summary += f"- 总消耗卡路里: {exercise_stats.get('total_calories', 0)}卡路里\n"
        
        # 饮食摘要
        summary += "\n【饮食情况】\n"
        summary += f"- 平均每日摄入热量: {diet_stats.get('avg_calories_per_day', 0):.1f}卡路里\n"
        summary += f"- 蛋白质摄入比例: {diet_stats.get('protein_ratio', 0):.1f}%\n"
        summary += f"- 脂肪摄入比例: {diet_stats.get('fat_ratio', 0):.1f}%\n"
        summary += f"- 碳水摄入比例: {diet_stats.get('carbs_ratio', 0):.1f}%\n"
        
        # 睡眠摘要
        summary += "\n【睡眠情况】\n"
        summary += f"- 睡眠记录天数: {sleep_stats.get('sleep_days', 0)}/7天\n"
        summary += f"- 平均睡眠时长: {sleep_stats.get('avg_duration_per_day', 0) / 60:.1f}小时\n"
        summary += f"- 平均睡眠质量: {sleep_stats.get('avg_quality', 0):.1f}/5分\n"
        
        # 主要健康建议
        summary += "\n【主要健康建议】\n"
        if analysis_results.get("overall_advice"):
            for i, advice in enumerate(analysis_results.get("overall_advice")[:3], 1):
                summary += f"{i}. {advice}\n"
        else:
            summary += "暂无建议\n"
        
        summary += "\n点击\"显示详情\"查看完整分析，或导出PDF报告获取更详细的内容。"
        return summary

    def _generate_detailed_report_text(self, analysis_results):
        """生成详细报告文本"""
        detailed_text = "详细健康分析报告\n\n"
        
        # 运动建议
        detailed_text += "【运动建议】\n"
        if analysis_results.get("exercise_advice"):
            for advice in analysis_results.get("exercise_advice"):
                detailed_text += f"- {advice}\n"
        else:
            detailed_text += "暂无运动建议\n"
        
        # 饮食建议
        detailed_text += "\n【饮食建议】\n"
        if analysis_results.get("diet_advice"):
            for advice in analysis_results.get("diet_advice"):
                detailed_text += f"- {advice}\n"
        else:
            detailed_text += "暂无饮食建议\n"
        
        # 睡眠建议
        detailed_text += "\n【睡眠建议】\n"
        if analysis_results.get("sleep_advice"):
            for advice in analysis_results.get("sleep_advice"):
                detailed_text += f"- {advice}\n"
        else:
            detailed_text += "暂无睡眠建议\n"
        
        # 整体健康建议
        detailed_text += "\n【整体健康建议】\n"
        if analysis_results.get("overall_advice"):
            for advice in analysis_results.get("overall_advice"):
                detailed_text += f"- {advice}\n"
        else:
            detailed_text += "暂无整体健康建议\n"
        
        return detailed_text

    def _export_weekly_report_pdf(self, analysis_results, user_info, week_start, week_end):
        """导出周报告为PDF文件"""
        try:
            # 创建报告生成器
            report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
            report_generator = WeeklyReportGenerator(analysis_results, user_info, output_dir=report_dir)
            
            # 生成PDF文件
            filename = f"健康周报_{week_start.strftime('%Y%m%d')}-{week_end.strftime('%Y%m%d')}.pdf"
            pdf_path = report_generator.generate_pdf(filename)
            
            # 显示成功消息
            QMessageBox.information(
                self, 
                "导出成功", 
                f"健康周报已成功导出到:\n{pdf_path}\n\n是否打开文件?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            # 如果用户选择打开文件
            if QMessageBox.Yes:
                # 使用系统默认程序打开PDF文件
                import platform
                import subprocess
                
                if platform.system() == 'Windows':
                    os.startfile(pdf_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', pdf_path))
                else:  # Linux
                    subprocess.call(('xdg-open', pdf_path))
                
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出PDF报告失败: {e}")

    def view_reminders(self):
        """查看所有提醒"""
        from ui.reminder import ReminderView
        self.reminder_view = ReminderView(self.user_id, self.db_manager, self)
        self.reminder_view.show()

    def update_weekly_summary(self):
        """更新周摘要信息"""
        try:
            import datetime
            
            print("更新每周运动摘要...")
            
            # 获取当前周的起止日期
            today = datetime.date.today()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            
            # 格式化日期为字符串
            start_date = start_of_week.strftime('%Y-%m-%d')
            end_date = end_of_week.strftime('%Y-%m-%d')
            
            # 从数据库获取本周的运动数据
            try:
                weekly_exercise = self.db_manager.get_weekly_exercise_summary(
                    self.user_id, start_date, end_date
                )
                print(f"获取到周运动数据: {len(weekly_exercise) if weekly_exercise else 0}条记录")
            except Exception as e:
                print(f"获取周运动数据时出错: {str(e)}")
                weekly_exercise = []  # 确保不会因空值报错
            
            # 生成摘要文本
            summary_text = self.generate_summary_text(weekly_exercise)
            
            # 更新UI显示
            # 注意：不再使用all_view显示摘要，可以考虑在状态栏或其他地方显示
            status_bar = self.statusBar()
            status_bar.showMessage(f"本周摘要: {summary_text}")
        except Exception as e:
            print(f"更新周摘要时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def generate_summary_text(self, weekly_exercise):
        """生成摘要文本"""
        try:
            if not weekly_exercise or len(weekly_exercise) == 0:
                return "本周暂无运动记录"
            
            # 安全地尝试生成总结
            total_days = len(set([ex[0] for ex in weekly_exercise if ex and len(ex) > 0]))
            total_duration = sum([ex[1] for ex in weekly_exercise if ex and len(ex) > 1])
            total_calories = sum([ex[2] for ex in weekly_exercise if ex and len(ex) > 2])
            
            return f"本周运动: {total_days}天, 总时长: {total_duration}分钟, 消耗: {total_calories}卡路里"
        except Exception as e:
            print(f"生成总结文本时出错: {str(e)}")
            return "无法生成运动总结"

    def on_reminder_triggered(self, title, content, reminder_id):
        """处理提醒触发事件"""
        try:
            from utils.reminder import show_reminder
            print(f"MainWindow接收到提醒触发事件: {title}")
            
            # 调用弹出提醒对话框的函数
            result = show_reminder(self, self.db_manager, title, content, reminder_id)
            print(f"提醒对话框结果: {result}")
            
            # 刷新计划视图，显示更新后的提醒状态
            if hasattr(self, 'plan_view') and hasattr(self.plan_view, 'load_reminders'):
                self.plan_view.load_reminders()
                print("已刷新计划视图")
            
        except Exception as e:
            print(f"处理提醒触发时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 出错时尝试直接显示一个基本的消息框
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, title, content)
                print("使用基本消息框显示提醒")
            except Exception as e2:
                print(f"显示基本消息框也失败: {str(e2)}") 