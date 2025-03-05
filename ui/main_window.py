from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QStackedWidget,
                            QAction, QToolBar, QMessageBox, QFrame, QTabWidget, QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from ui.diet_view import DietView

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
        """更新日期"""
        self.selected_date = selected_date
        self.content_label.setText(f"日期: {selected_date.toString('yyyy-MM-dd')}\n暂无数据")
    
    def load_data(self):
        """加载数据，子类应重写此方法"""
        pass


class AllView(BaseView):
    """所有内容综合视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("全部内容")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        self.content_label.setText(f"全部内容 - {selected_date.toString('yyyy-MM-dd')}\n暂无数据")


class ExerciseView(BaseView):
    """运动记录视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("运动记录")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        self.content_label.setText(f"运动记录 - {selected_date.toString('yyyy-MM-dd')}\n暂无数据")


class SleepView(BaseView):
    """睡眠记录视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("睡眠记录")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        self.content_label.setText(f"睡眠记录 - {selected_date.toString('yyyy-MM-dd')}\n暂无数据")


class PlanView(BaseView):
    """计划安排视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("计划安排")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        self.content_label.setText(f"计划安排 - {selected_date.toString('yyyy-MM-dd')}\n暂无数据")


class MainWindow(QMainWindow):
    def __init__(self, user_id, username, db_manager):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.db_manager = db_manager  # 添加数据库管理器
        self.init_ui()
        
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
        self.mode_combo.addItems(["全部", "饮食", "运动", "睡眠", "计划"])
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
        self.all_view = AllView(self.user_id, self.db_manager)
        self.diet_view = DietView(self.user_id, self.db_manager)
        self.exercise_view = ExerciseView(self.user_id, self.db_manager)
        self.sleep_view = SleepView(self.user_id, self.db_manager)
        self.plan_view = PlanView(self.user_id, self.db_manager)
        
        # 添加视图到堆叠部件
        self.content_stack.addWidget(self.all_view)
        self.content_stack.addWidget(self.diet_view)
        self.content_stack.addWidget(self.exercise_view)
        self.content_stack.addWidget(self.sleep_view)
        self.content_stack.addWidget(self.plan_view)
        
        right_layout.addWidget(self.content_stack)
        
        # 将左右区域添加到主布局
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 2)
        
        # 创建菜单和工具栏
        self.create_menus()
        
    def create_menus(self):
        """创建菜单和工具栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        export_action = QAction("导出报告", self)
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 用户菜单
        user_menu = self.menuBar().addMenu("用户")
        
        profile_action = QAction("个人信息", self)
        profile_action.triggered.connect(self.edit_profile)
        user_menu.addAction(profile_action)
        
        # 报告菜单
        report_menu = self.menuBar().addMenu("报告")
        
        daily_report_action = QAction("每日报告", self)
        daily_report_action.triggered.connect(self.show_daily_report)
        report_menu.addAction(daily_report_action)
        
        weekly_report_action = QAction("每周报告", self)
        weekly_report_action.triggered.connect(self.show_weekly_report)
        report_menu.addAction(weekly_report_action)
        
        # 添加"查看提醒"菜单项
        tools_menu = self.menuBar().addMenu("工具")
        
        view_reminders_action = QAction("查看提醒", self)
        view_reminders_action.triggered.connect(self.view_reminders)
        tools_menu.addAction(view_reminders_action)
        
        # 工具栏
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        toolbar.addAction(profile_action)
        toolbar.addAction(daily_report_action)
        toolbar.addAction(weekly_report_action)
        
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
        current_view = self.content_stack.widget(current_index)
        
        # 如果是DietView，特殊处理
        if isinstance(current_view, DietView):
            if hasattr(current_view, 'date_edit'):
                current_view.date_edit.setDate(self.calendar.selectedDate())
                current_view.load_diet_records()
        # 其他视图使用标准的update_date方法
        elif hasattr(current_view, 'update_date'):
            current_view.update_date(self.calendar.selectedDate())
            
    def load_date_data(self):
        """加载所选日期的数据"""
        selected_date = self.calendar.selectedDate()
        
        # 更新所有视图的日期
        self.all_view.update_date(selected_date)
        
        # DietView 需要特殊处理，因为它有自己的日期控件
        if hasattr(self.diet_view, 'date_edit'):
            self.diet_view.date_edit.setDate(selected_date)
            self.diet_view.load_diet_records()
        
        # 更新其他视图
        self.exercise_view.update_date(selected_date)
        self.sleep_view.update_date(selected_date)
        self.plan_view.update_date(selected_date)
        
    def add_record(self):
        """添加记录"""
        current_index = self.mode_combo.currentIndex()
        
        if current_index == 0:  # 全部模式
            # 弹出选择对话框让用户选择要添加的记录类型
            record_types = ["饮食记录", "运动记录", "睡眠记录"]
            selected_type, ok = QInputDialog.getItem(
                self, "选择记录类型", "请选择要添加的记录类型:", 
                record_types, 0, False
            )
            if not ok:
                return
                
            if selected_type == "饮食记录":
                self.add_diet_record()
            elif selected_type == "运动记录":
                QMessageBox.information(self, "提示", "添加运动记录功能正在开发中...")
            elif selected_type == "睡眠记录":
                QMessageBox.information(self, "提示", "添加睡眠记录功能正在开发中...")
        
        elif current_index == 1:  # 饮食模式
            self.add_diet_record()
        elif current_index == 2:  # 运动模式
            QMessageBox.information(self, "提示", "添加运动记录功能正在开发中...")
        elif current_index == 3:  # 睡眠模式
            QMessageBox.information(self, "提示", "添加睡眠记录功能正在开发中...")
        elif current_index == 4:  # 计划模式
            self.add_plan()
    
    def add_diet_record(self):
        """添加饮食记录"""
        if hasattr(self.diet_view, 'add_diet_record'):
            self.diet_view.add_diet_record()
        else:
            from ui.diet_record import DietRecordDialog
            dialog = DietRecordDialog(self.user_id, self.db_manager)
            dialog.record_added.connect(lambda: self.diet_view.load_diet_records())
            dialog.exec_()
        
    def add_plan(self):
        """添加提醒计划"""
        from ui.reminder import ReminderDialog
        dialog = ReminderDialog(self.db_manager, self.user_id, self)
        dialog.reminder_updated.connect(self.load_date_data)
        dialog.exec_()
        
    def export_report(self):
        """导出报告"""
        QMessageBox.information(self, "提示", "导出报告功能正在开发中...")
        
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
        
    def show_daily_report(self):
        """显示每日报告"""
        QMessageBox.information(self, "提示", "每日报告功能正在开发中...")
        
    def show_weekly_report(self):
        """显示每周报告"""
        QMessageBox.information(self, "提示", "每周报告功能正在开发中...")
        
    def view_reminders(self):
        """查看所有提醒"""
        from ui.reminder import ReminderView
        self.reminder_view = ReminderView(self.user_id, self.db_manager, self)
        self.reminder_view.show() 