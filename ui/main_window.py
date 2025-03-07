from PyQt5.QtWidgets import (QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QStackedWidget,
                            QAction, QToolBar, QMessageBox, QFrame, QTabWidget, QInputDialog, QMenu)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor
from ui.diet_view import DietView
from ui.exercise_view import ExerciseView

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


class AllView(BaseView):
    """所有内容综合视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("全部内容")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        
        # 检查日期类型，如果是字符串则使用原样显示
        if isinstance(selected_date, str):
            date_str = selected_date
        else:
            date_str = selected_date.toString('yyyy-MM-dd')
            
        self.content_label.setText(f"全部内容 - {date_str}\n暂无数据")

    def update_summary(self, summary_text):
        """更新摘要内容"""
        self.content_label.setText(summary_text)


class SleepView(BaseView):
    """睡眠记录视图"""
    
    def init_ui(self):
        """初始化用户界面"""
        super().init_ui()
        self.title_label.setText("睡眠记录")
    
    def update_date(self, selected_date):
        """更新日期"""
        super().update_date(selected_date)
        
        # 检查日期类型，如果是字符串则使用原样显示
        if isinstance(selected_date, str):
            date_str = selected_date
        else:
            date_str = selected_date.toString('yyyy-MM-dd')
            
        self.content_label.setText(f"睡眠记录 - {date_str}\n暂无数据")


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
        if current_index == 1 and hasattr(self.diet_view, 'load_diet_records'):  # 饮食视图
            self.diet_view.load_diet_records()
        elif current_index == 2 and hasattr(self.exercise_view, 'load_exercise_records'):  # 运动视图
            self.exercise_view.load_exercise_records()
        elif current_index == 4 and hasattr(self.plan_view, 'load_reminders'):  # 计划视图
            self.plan_view.load_reminders()
        
    def add_record(self):
        """添加记录"""
        current_index = self.content_stack.currentIndex()
        print(f"添加记录: 当前视图索引 = {current_index}")
        
        # 根据当前视图索引决定添加什么类型的记录
        if current_index == 0:  # 全部视图
            # 显示一个选项菜单让用户选择要添加的记录类型
            menu = QMenu(self)
            diet_action = menu.addAction("添加饮食记录")
            exercise_action = menu.addAction("添加运动记录")
            plan_action = menu.addAction("添加计划提醒")
            
            diet_action.triggered.connect(self.add_diet_record)
            exercise_action.triggered.connect(self.add_exercise_record)
            plan_action.triggered.connect(self.add_plan)
            
            # 在按钮位置显示菜单
            button = self.sender()
            if button:
                menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
            else:
                menu.exec_(QCursor.pos())
                
        elif current_index == 1:  # 饮食视图
            self.add_diet_record()
        elif current_index == 2:  # 运动视图
            self.add_exercise_record()
        elif current_index == 3:  # 睡眠视图
            # 这里可以添加睡眠记录功能
            QMessageBox.information(self, "提示", "睡眠记录功能暂未实现")
        elif current_index == 4:  # 计划视图
            self.add_plan()
        else:
            print(f"未知的视图索引: {current_index}")
            QMessageBox.warning(self, "错误", "无法确定要添加的记录类型")
    
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
            if self.content_stack.currentIndex() == 4:  # 计划视图索引
                self.mode_changed(4)
                
        dialog.reminder_updated.connect(on_reminder_updated)
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
        try:
            # 更新周报摘要
            self.update_weekly_summary()
            
            # 切换到全部模式显示周报
            self.mode_combo.setCurrentIndex(0)  # 全部模式
            
            QMessageBox.information(self, "周报", "周报已生成并在全部模式中显示！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成周报时出错: {str(e)}")
        
    def view_reminders(self):
        """查看所有提醒"""
        from ui.reminder import ReminderView
        self.reminder_view = ReminderView(self.user_id, self.db_manager, self)
        self.reminder_view.show()

    def update_weekly_summary(self):
        """更新每周运动和饮食总结"""
        try:
            print("更新每周总结...")
            # 获取当前周的开始和结束日期
            today = QDate.currentDate()
            days_to_sunday = today.dayOfWeek() % 7  # 周日为0，周一为1，...，周六为6
            start_date = today.addDays(-days_to_sunday).toString("yyyy-MM-dd")
            end_date = today.addDays(6 - days_to_sunday).toString("yyyy-MM-dd")
            
            print(f"周期: {start_date} 到 {end_date}")
            
            # 获取每周运动总结
            try:
                weekly_exercise = self.db_manager.get_weekly_exercise_summary(
                    self.user_id, start_date, end_date)
                print(f"获取到每周运动总结: {weekly_exercise}")
                
                # 防止空值错误
                if weekly_exercise is None:
                    print("警告: 运动总结为None，使用空列表")
                    weekly_exercise = []
                
                # 更新所有视图的总结
                if hasattr(self, 'all_view') and self.all_view:
                    summary_text = self.generate_summary_text(weekly_exercise)
                    self.all_view.update_summary(summary_text)
            except Exception as e:
                print(f"更新运动总结时出错: {str(e)}")
                # 提供默认值避免后续错误
                weekly_exercise = []
                if hasattr(self, 'all_view') and self.all_view:
                    self.all_view.update_summary("本周暂无运动数据")
        except Exception as e:
            print(f"更新每周总结出错: {str(e)}")
            # 避免错误传播
    
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