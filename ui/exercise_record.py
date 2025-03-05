from PyQt5.QtWidgets import (QDialog, QLabel, QComboBox, QLineEdit, QTextEdit,
                           QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QDateEdit, QTimeEdit, QSpinBox, QMessageBox, QSlider,
                           QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                           QTabWidget, QWidget, QCompleter, QGroupBox, QRadioButton,
                           QButtonGroup)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator

from data.exercise_data import (load_exercise_data, get_exercise_categories,
                              get_exercises_by_category, search_exercises,
                              calculate_calories)
import datetime

class ExerciseRecordDialog(QDialog):
    """运动记录对话框"""
    
    # 定义信号
    record_added = pyqtSignal()
    
    def __init__(self, user_id, db_manager, parent=None, record_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        self.record_id = record_id  # 如果有记录ID，表示是编辑模式
        self.exercise_data = None   # 当前选择的运动数据
        
        self.setWindowTitle("添加运动记录" if not record_id else "编辑运动记录")
        self.resize(800, 600)
        
        # 获取用户体重
        self.user_weight = self.get_user_weight()  # 已经在方法中设置了默认值
        print(f"初始化运动记录对话框，用户体重: {self.user_weight}kg")
        
        self.init_ui()
        
        # 如果是编辑模式，加载现有记录
        if self.record_id:
            self.load_record()
    
    def get_user_weight(self):
        """获取用户体重，用于卡路里计算"""
        try:
            # 获取用户资料
            user_profile = self.db_manager.get_user_profile(self.user_id)
            print(f"获取用户体重: user_profile = {user_profile}")
            
            # 安全地获取体重值
            if user_profile and isinstance(user_profile, dict) and "weight" in user_profile:
                weight = user_profile.get("weight")
                if weight and isinstance(weight, (int, float)):
                    print(f"用户体重: {weight} kg")
                    return weight
            
            # 如果无法获取体重，使用默认值
            print("未能获取用户体重，使用默认值: 60 kg")
            return 60  # 默认体重60kg
        except Exception as e:
            print(f"获取用户体重时出错: {str(e)}")
            return 60  # 发生异常时返回默认值
    
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 创建"选择运动"选项卡
        self.select_exercise_tab = QWidget()
        self.setup_select_exercise_tab()
        self.tab_widget.addTab(self.select_exercise_tab, "选择运动")
        
        # 创建"运动详情"选项卡
        self.exercise_details_tab = QWidget()
        self.setup_exercise_details_tab()
        self.tab_widget.addTab(self.exercise_details_tab, "运动详情")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_record)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
    
    def setup_select_exercise_tab(self):
        """设置选择运动选项卡"""
        layout = QVBoxLayout()
        
        # 搜索和筛选区域
        search_layout = QHBoxLayout()
        
        # 搜索框
        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入运动名称或关键词")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_exercises)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.search_button, 1)
        
        # 分类筛选
        category_layout = QHBoxLayout()
        category_label = QLabel("分类:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        
        # 获取所有运动分类
        categories = get_exercise_categories()
        for category in categories:
            self.category_combo.addItem(category)
        
        self.category_combo.currentIndexChanged.connect(self.filter_by_category)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        
        # 运动表格
        self.exercise_table = QTableWidget()
        self.exercise_table.setColumnCount(4)
        self.exercise_table.setHorizontalHeaderLabels(["运动", "分类", "卡路里/小时", "描述"])
        self.exercise_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.exercise_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exercise_table.setSelectionMode(QTableWidget.SingleSelection)
        self.exercise_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exercise_table.cellClicked.connect(self.exercise_selected)
        
        # 填充运动表格
        self.populate_exercise_table(load_exercise_data())
        
        # 将组件添加到布局
        layout.addLayout(search_layout)
        layout.addLayout(category_layout)
        layout.addWidget(self.exercise_table)
        
        self.select_exercise_tab.setLayout(layout)
    
    def setup_exercise_details_tab(self):
        """设置运动详情选项卡"""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 运动名称
        self.exercise_name_label = QLabel("(未选择)")
        self.exercise_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        form_layout.addRow(QLabel("运动名称:"), self.exercise_name_label)
        
        # 分类
        self.category_label = QLabel("-")
        form_layout.addRow(QLabel("分类:"), self.category_label)
        
        # 日期
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("日期:"), self.date_edit)
        
        # 时间
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow(QLabel("时间:"), self.time_edit)
        
        # 持续时间
        time_layout = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)  # 1分钟到24小时
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" 分钟")
        self.duration_spin.valueChanged.connect(self.update_calories)
        time_layout.addWidget(self.duration_spin)
        form_layout.addRow(QLabel("持续时间:"), time_layout)
        
        # 强度选择
        intensity_layout = QHBoxLayout()
        self.intensity_group = QButtonGroup()
        
        self.low_intensity = QRadioButton("低")
        self.medium_intensity = QRadioButton("中")
        self.high_intensity = QRadioButton("高")
        
        self.intensity_group.addButton(self.low_intensity, 1)
        self.intensity_group.addButton(self.medium_intensity, 2)
        self.intensity_group.addButton(self.high_intensity, 3)
        
        self.medium_intensity.setChecked(True)  # 默认选中中等强度
        
        intensity_layout.addWidget(self.low_intensity)
        intensity_layout.addWidget(self.medium_intensity)
        intensity_layout.addWidget(self.high_intensity)
        intensity_layout.addStretch()
        
        form_layout.addRow(QLabel("强度:"), intensity_layout)
        
        # 卡路里消耗
        self.calories_layout = QHBoxLayout()
        self.calories_label = QLabel("0")
        self.calories_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.calories_layout.addWidget(self.calories_label)
        self.calories_layout.addWidget(QLabel("kcal"))
        self.calories_layout.addStretch()
        
        form_layout.addRow(QLabel("消耗卡路里:"), self.calories_layout)
        
        # 备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("添加备注...")
        form_layout.addRow(QLabel("备注:"), self.notes_edit)
        
        layout.addLayout(form_layout)
        
        self.exercise_details_tab.setLayout(layout)
    
    def populate_exercise_table(self, exercises):
        """填充运动表格"""
        self.exercise_table.setRowCount(len(exercises))
        
        for row, exercise in enumerate(exercises):
            name_item = QTableWidgetItem(exercise['name'])
            self.exercise_table.setItem(row, 0, name_item)
            
            category_item = QTableWidgetItem(exercise['category'])
            self.exercise_table.setItem(row, 1, category_item)
            
            calories_item = QTableWidgetItem(str(exercise['calories_per_hour']))
            self.exercise_table.setItem(row, 2, calories_item)
            
            description_item = QTableWidgetItem(exercise['description'])
            self.exercise_table.setItem(row, 3, description_item)
    
    def search_exercises(self):
        """搜索运动"""
        keyword = self.search_input.text().strip()
        exercises = search_exercises(keyword)
        self.populate_exercise_table(exercises)
    
    def filter_by_category(self):
        """按分类筛选运动"""
        category = self.category_combo.currentText()
        exercises = get_exercises_by_category(category)
        self.populate_exercise_table(exercises)
    
    def exercise_selected(self, row, column):
        """选择运动时的处理"""
        # 获取选择的运动数据
        exercise_name = self.exercise_table.item(row, 0).text()
        category = self.exercise_table.item(row, 1).text()
        
        # 在运动数据中查找
        exercises = load_exercise_data()
        for exercise in exercises:
            if exercise['name'] == exercise_name:
                self.exercise_data = exercise
                break
        
        if self.exercise_data:
            # 更新详情页的信息
            self.exercise_name_label.setText(self.exercise_data['name'])
            self.category_label.setText(self.exercise_data['category'])
            
            # 更新卡路里计算
            self.update_calories()
            
            # 切换到详情选项卡
            self.tab_widget.setCurrentIndex(1)
    
    def update_calories(self):
        """更新卡路里消耗计算"""
        if not self.exercise_data:
            return
        
        duration = self.duration_spin.value()
        
        # 根据强度调整消耗
        intensity_factor = 1.0
        if self.low_intensity.isChecked():
            intensity_factor = 0.8
        elif self.high_intensity.isChecked():
            intensity_factor = 1.2
        
        # 确保用户体重有效
        weight = self.user_weight if isinstance(self.user_weight, (int, float)) else 60
        
        # 计算卡路里消耗
        try:
            calories = calculate_calories(self.exercise_data['name'], duration, weight)
            adjusted_calories = round(calories * intensity_factor)
            
            self.calories_label.setText(str(adjusted_calories))
        except Exception as e:
            print(f"计算卡路里消耗时出错: {str(e)}")
            self.calories_label.setText("0")  # 出错时显示0
    
    def load_record(self):
        """加载已有记录进行编辑"""
        if not self.record_id:
            return
            
        try:
            # 从数据库获取记录
            cursor = self.db_manager.conn.cursor()
            cursor.execute("SELECT * FROM exercise_records WHERE id = ?", (self.record_id,))
            record = cursor.fetchone()
            
            if not record:
                QMessageBox.warning(self, "错误", "找不到指定的记录!")
                self.reject()
                return
                
            # 填充表单
            exercise_name = record[2]  # exercise_name字段
            category = record[3]       # category字段
            duration = record[4]       # duration字段
            intensity = record[5]      # intensity字段
            record_date = record[7]    # record_date字段
            record_time = record[8]    # record_time字段
            notes = record[9]          # notes字段
            
            # 设置运动名称和分类
            self.exercise_name_label.setText(exercise_name)
            self.category_label.setText(category)
            
            # 查找并设置运动数据
            exercises = load_exercise_data()
            for exercise in exercises:
                if exercise['name'] == exercise_name:
                    self.exercise_data = exercise
                    break
            
            # 设置日期和时间
            if record_date:
                self.date_edit.setDate(QDate.fromString(record_date, "yyyy-MM-dd"))
            
            if record_time:
                time_str = record_time.split()[1] if ' ' in record_time else record_time
                self.time_edit.setTime(QTime.fromString(time_str.split('.')[0], "HH:mm:ss"))
            
            # 设置持续时间
            self.duration_spin.setValue(duration)
            
            # 设置强度
            if intensity == "低":
                self.low_intensity.setChecked(True)
            elif intensity == "中":
                self.medium_intensity.setChecked(True)
            elif intensity == "高":
                self.high_intensity.setChecked(True)
            
            # 设置备注
            if notes:
                self.notes_edit.setText(notes)
            
            # 更新卡路里计算
            self.update_calories()
            
            # 设置为详情选项卡
            self.tab_widget.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载记录时出错: {str(e)}")
    
    def save_record(self):
        """保存运动记录"""
        if not self.exercise_data:
            QMessageBox.warning(self, "警告", "请选择一项运动!")
            return
        
        # 获取表单数据
        exercise_name = self.exercise_name_label.text()
        category = self.category_label.text()
        duration = self.duration_spin.value()
        
        # 获取强度
        intensity = "中"
        if self.low_intensity.isChecked():
            intensity = "低"
        elif self.high_intensity.isChecked():
            intensity = "高"
        
        # 获取卡路里消耗
        calories_burned = int(self.calories_label.text())
        
        # 获取日期和时间
        record_date = self.date_edit.date().toString("yyyy-MM-dd")
        record_time = self.time_edit.time().toString("HH:mm:ss")
        
        # 获取备注
        notes = self.notes_edit.toPlainText()
        
        try:
            if self.record_id:  # 编辑模式
                success = self.db_manager.update_exercise_record(
                    self.record_id,
                    exercise_name=exercise_name,
                    category=category,
                    duration=duration,
                    intensity=intensity,
                    calories_burned=calories_burned,
                    record_date=record_date,
                    record_time=record_time,
                    notes=notes
                )
                
                if success:
                    QMessageBox.information(self, "成功", "运动记录已更新!")
                    self.record_added.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "错误", "更新运动记录失败，请重试!")
            else:  # 添加模式
                record_id = self.db_manager.add_exercise_record(
                    self.user_id,
                    exercise_name,
                    category,
                    duration,
                    intensity,
                    calories_burned,
                    record_date,
                    record_time,
                    notes
                )
                
                if record_id:
                    QMessageBox.information(self, "成功", "运动记录已添加!")
                    self.record_added.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "错误", "添加运动记录失败，请重试!")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存记录时出错: {str(e)}") 