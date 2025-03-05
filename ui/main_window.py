from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QStackedWidget,
                            QAction, QToolBar, QMessageBox, QFrame, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from ui.diet_view import DietView

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
        
        # 在选项卡布局中添加饮食记录视图
        self.tab_widget = QTabWidget()
        
        # 饮食记录标签页
        self.diet_view = DietView(self.user_id, self.db_manager)
        self.tab_widget.addTab(self.diet_view, "饮食记录")
        
        # 创建不同的内容视图
        self.all_view = QLabel("全部内容视图")
        self.all_view.setAlignment(Qt.AlignCenter)
        self.all_view.setObjectName("contentView")
        
        self.exercise_view = QLabel("运动内容视图")
        self.exercise_view.setAlignment(Qt.AlignCenter)
        self.exercise_view.setObjectName("contentView")
        
        self.sleep_view = QLabel("睡眠内容视图")
        self.sleep_view.setAlignment(Qt.AlignCenter)
        self.sleep_view.setObjectName("contentView")
        
        self.plan_view = QLabel("计划内容视图")
        self.plan_view.setAlignment(Qt.AlignCenter)
        self.plan_view.setObjectName("contentView")
        
        self.content_stack.addWidget(self.all_view)
        self.content_stack.addWidget(self.diet_view)
        self.content_stack.addWidget(self.exercise_view)
        self.content_stack.addWidget(self.sleep_view)
        self.content_stack.addWidget(self.plan_view)
        
        right_layout.addWidget(self.tab_widget)
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
        
    def load_date_data(self):
        """加载所选日期的数据"""
        # 这里需要实现从数据库加载当天的数据
        # 暂时使用占位文本
        selected_date = self.calendar.selectedDate().toString('yyyy-MM-dd')
        
        self.all_view.setText(f"全部内容 - {selected_date}\n暂无数据")
        self.diet_view.setText(f"饮食记录 - {selected_date}\n暂无数据")
        self.exercise_view.setText(f"运动记录 - {selected_date}\n暂无数据")
        self.sleep_view.setText(f"睡眠记录 - {selected_date}\n暂无数据")
        self.plan_view.setText(f"计划安排 - {selected_date}\n暂无数据")
        
    def add_record(self):
        """添加记录"""
        QMessageBox.information(self, "提示", "添加记录功能正在开发中...")
        
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