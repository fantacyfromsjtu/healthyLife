from PyQt5.QtWidgets import (QDialog, QLabel, QComboBox, QLineEdit, QTextEdit, 
                           QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QDateEdit, QTimeEdit, QDoubleSpinBox, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QFrame, QTabWidget,
                           QWidget, QMessageBox, QCompleter, QGroupBox, QCheckBox,
                           QInputDialog)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt5.QtGui import QFont

class DietRecordDialog(QDialog):
    """饮食记录对话框"""
    
    # 定义信号
    record_added = pyqtSignal()
    
    def __init__(self, user_id, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        
        self.setWindowTitle("添加饮食记录")
        self.resize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        
        # 记录信息区域
        record_group = QGroupBox("记录信息")
        record_layout = QFormLayout()
        
        # 日期和时间
        date_time_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        
        date_time_layout.addWidget(QLabel("日期:"))
        date_time_layout.addWidget(self.date_edit)
        date_time_layout.addWidget(QLabel("时间:"))
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addStretch()
        
        # 餐食类型
        meal_layout = QHBoxLayout()
        meal_label = QLabel("餐食类型:")
        self.meal_type = QComboBox()
        self.meal_type.addItems(["早餐", "午餐", "晚餐", "加餐"])
        
        meal_layout.addWidget(meal_label)
        meal_layout.addWidget(self.meal_type)
        meal_layout.addStretch()
        
        # 添加到记录布局
        record_layout.addRow(date_time_layout)
        record_layout.addRow(meal_layout)
        record_group.setLayout(record_layout)
        
        # 食物选择区域
        food_group = QGroupBox("食物选择")
        food_layout = QVBoxLayout()
        
        # 食物搜索
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索食物:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入食物名称...")
        self.search_input.textChanged.connect(self.search_foods)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        # 食物分类选择
        category_layout = QHBoxLayout()
        category_label = QLabel("分类:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        
        # 获取所有食物分类
        try:
            # 确保数据库中有食物数据
            self.db_manager.initialize_food_database()
            
            # 获取分类
            categories = set()
            foods = self.db_manager.get_foods_by_category()
            print(f"从数据库获取食物数据: {len(foods)}条记录")
            
            if not foods or len(foods) == 0:
                # 如果数据库中没有数据，显示错误消息
                QMessageBox.warning(self, "警告", "无法加载食物数据，请确保数据库已正确初始化。")
                print("警告: 无法从数据库加载食物数据")
            else:
                for food in foods:
                    if food[2]:  # 分类在索引2
                        categories.add(food[2])
                
                print(f"找到的食物分类: {categories}")
                
                # 如果没有分类，添加一些默认分类
                if not categories:
                    default_categories = ["主食", "肉类", "蔬菜", "水果", "乳制品", "豆制品", "零食"]
                    for cat in default_categories:
                        self.category_combo.addItem(cat)
                    print(f"使用默认分类: {default_categories}")
                else:
                    for category in sorted(categories):
                        self.category_combo.addItem(category)
        except Exception as e:
            print(f"加载食物分类时出错: {str(e)}")
            # 添加一些默认分类
            default_categories = ["主食", "肉类", "蔬菜", "水果", "乳制品", "豆制品", "零食"]
            for cat in default_categories:
                self.category_combo.addItem(cat)
            print(f"使用默认分类: {default_categories}")
        
        self.category_combo.currentIndexChanged.connect(self.filter_by_category)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        
        # 食物表格
        self.food_table = QTableWidget()
        self.food_table.setColumnCount(5)
        self.food_table.setHorizontalHeaderLabels(["名称", "分类", "热量(kcal/100g)", "蛋白质(g)", "碳水(g)"])
        self.food_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.food_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.food_table.setSelectionMode(QTableWidget.SingleSelection)
        self.food_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.food_table.cellClicked.connect(self.food_selected)
        
        # 填充食物表格
        self.populate_food_table(foods if 'foods' in locals() else [])
        
        # 数量和单位
        amount_layout = QHBoxLayout()
        amount_label = QLabel("数量:")
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMinimum(0.1)
        self.amount_spin.setMaximum(1000)
        self.amount_spin.setValue(1)
        self.amount_spin.setSingleStep(0.5)
        
        unit_label = QLabel("单位:")
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["份", "克", "ml", "个", "碗", "杯"])
        
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_spin)
        amount_layout.addWidget(unit_label)
        amount_layout.addWidget(self.unit_combo)
        amount_layout.addStretch()
        
        # 添加食物按钮
        add_food_button = QPushButton("添加食物")
        add_food_button.setObjectName("secondaryButton")
        add_food_button.clicked.connect(self.add_new_food)
        
        # 备注
        notes_layout = QVBoxLayout()
        notes_label = QLabel("备注:")
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_text)
        
        # 添加到食物布局
        food_layout.addLayout(search_layout)
        food_layout.addLayout(category_layout)
        food_layout.addWidget(self.food_table)
        food_layout.addLayout(amount_layout)
        food_layout.addWidget(add_food_button)
        food_layout.addLayout(notes_layout)
        food_group.setLayout(food_layout)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("保存记录")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_record)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # 将所有组件添加到主布局
        main_layout.addWidget(record_group)
        main_layout.addWidget(food_group)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        # 保存当前选中的食物ID
        self.selected_food_id = None
        self.selected_food_name = None
        
    def populate_food_table(self, foods):
        """填充食物表格"""
        self.food_table.setRowCount(len(foods))
        
        for row, food in enumerate(foods):
            # ID在索引0，名称在索引1，分类在索引2，热量在索引3，蛋白质在索引4，脂肪在索引5，碳水在索引6
            self.food_table.setItem(row, 0, QTableWidgetItem(food[1]))  # 名称
            self.food_table.setItem(row, 1, QTableWidgetItem(food[2] if food[2] else ""))  # 分类
            self.food_table.setItem(row, 2, QTableWidgetItem(str(food[3])))  # 热量
            self.food_table.setItem(row, 3, QTableWidgetItem(str(food[4])))  # 蛋白质
            self.food_table.setItem(row, 4, QTableWidgetItem(str(food[6])))  # 碳水
            
            # 存储食物ID为隐藏数据
            self.food_table.item(row, 0).setData(Qt.UserRole, food[0])
    
    def search_foods(self):
        """搜索食物"""
        keyword = self.search_input.text().strip()
        if keyword:
            foods = self.db_manager.search_foods(keyword)
        else:
            # 如果搜索框为空，显示所有食物或按当前选中的分类过滤
            category = self.category_combo.currentText()
            if category == "全部":
                foods = self.db_manager.get_foods_by_category()
            else:
                foods = self.db_manager.get_foods_by_category(category)
        
        self.populate_food_table(foods)
    
    def filter_by_category(self):
        """按分类过滤食物"""
        category = self.category_combo.currentText()
        if category == "全部":
            foods = self.db_manager.get_foods_by_category()
        else:
            foods = self.db_manager.get_foods_by_category(category)
        
        self.populate_food_table(foods)
    
    def food_selected(self, row, column):
        """食物被选中时的回调"""
        self.selected_food_id = self.food_table.item(row, 0).data(Qt.UserRole)
        self.selected_food_name = self.food_table.item(row, 0).text()
        
        # 更新单位选择框
        foods = self.db_manager.search_foods(self.selected_food_name)
        if foods and len(foods) > 0:
            unit = foods[0][8]  # 单位在索引8
            if unit:
                # 查找该单位在组合框中的索引
                index = self.unit_combo.findText(unit)
                if index >= 0:
                    self.unit_combo.setCurrentIndex(index)
    
    def save_record(self):
        """保存饮食记录"""
        if not self.selected_food_id:
            QMessageBox.warning(self, "警告", "请先选择一种食物！")
            return
        
        # 获取各字段值
        record_date = self.date_edit.date().toString("yyyy-MM-dd")
        record_time = self.time_edit.time().toString("HH:mm:ss")
        meal_type = self.meal_type.currentText()
        amount = self.amount_spin.value()
        unit = self.unit_combo.currentText()
        notes = self.notes_text.toPlainText()
        
        # 保存记录
        success = self.db_manager.add_diet_record(
            self.user_id,
            self.selected_food_id,
            self.selected_food_name,
            amount,
            unit,
            meal_type,
            record_date,
            record_time,
            notes
        )
        
        if success:
            QMessageBox.information(self, "成功", "饮食记录已保存！")
            self.record_added.emit()  # 发射记录添加信号
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "保存记录失败，请重试！")
    
    def add_new_food(self):
        """添加新的食物到数据库"""
        try:
            # 获取食物名称
            food_name, ok = QInputDialog.getText(self, "添加新食物", "食物名称:")
            if not ok or not food_name.strip():
                return
                
            # 获取食物分类
            categories = [self.category_combo.itemText(i) for i in range(1, self.category_combo.count())]
            if not categories:
                categories = ["主食", "肉类", "蔬菜", "水果", "乳制品", "豆制品", "零食"]
                
            category, ok = QInputDialog.getItem(self, "选择分类", "食物分类:", categories, 0, False)
            if not ok:
                return
                
            # 获取食物热量
            calories, ok = QInputDialog.getDouble(self, "食物热量", "每100克热量(kcal):", 100, 0, 1000, 1)
            if not ok:
                return
                
            # 获取蛋白质含量
            protein, ok = QInputDialog.getDouble(self, "蛋白质含量", "每100克蛋白质(g):", 5, 0, 100, 1)
            if not ok:
                return
                
            # 获取脂肪含量
            fat, ok = QInputDialog.getDouble(self, "脂肪含量", "每100克脂肪(g):", 5, 0, 100, 1)
            if not ok:
                return
                
            # 获取碳水含量
            carbs, ok = QInputDialog.getDouble(self, "碳水化合物含量", "每100克碳水(g):", 10, 0, 100, 1)
            if not ok:
                return
                
            # 获取膳食纤维含量
            fiber, ok = QInputDialog.getDouble(self, "膳食纤维含量", "每100克膳食纤维(g):", 2, 0, 50, 1)
            if not ok:
                return
                
            # 获取标准单位
            units = ["份", "克", "ml", "个", "碗", "杯"]
            unit, ok = QInputDialog.getItem(self, "标准单位", "选择标准单位:", units, 0, False)
            if not ok:
                return
                
            # 获取标准重量
            standard_weight, ok = QInputDialog.getDouble(self, "标准重量", f"一{unit}的重量(克):", 100, 1, 1000, 1)
            if not ok:
                return
                
            # 添加到数据库
            success = self.db_manager.add_food(food_name, category, calories, protein, fat, carbs, fiber, unit, standard_weight)
            
            if success:
                QMessageBox.information(self, "成功", f"已添加食物: {food_name}")
                
                # 刷新食物列表
                self.filter_by_category()
                
                # 如果当前分类是新添加食物的分类，选择该食物
                if self.category_combo.currentText() == category or self.category_combo.currentText() == "全部":
                    self.search_input.setText(food_name)
            else:
                QMessageBox.warning(self, "失败", "添加食物失败，请重试。")
                
        except Exception as e:
            print(f"添加食物时出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"添加食物时出错: {str(e)}") 