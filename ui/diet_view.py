from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QHeaderView, QPushButton, QDateEdit,
                           QComboBox, QMessageBox, QTabWidget, QGroupBox, QDialog,
                           QFormLayout, QFrame, QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.diet_record import DietRecordDialog
from ui.meal_batch_edit import MealBatchEditDialog

class DietView(QWidget):
    """饮食记录查看界面"""
    
    def __init__(self, user_id, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        
        # 顶部控制区域
        controls_layout = QHBoxLayout()
        
        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("日期:")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.dateChanged.connect(self.load_diet_records)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        
        # 餐食类型选择
        meal_layout = QHBoxLayout()
        meal_label = QLabel("餐食类型:")
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(["全部", "早餐", "午餐", "晚餐", "加餐"])
        self.meal_combo.currentIndexChanged.connect(self.load_diet_records)
        
        meal_layout.addWidget(meal_label)
        meal_layout.addWidget(self.meal_combo)
        
        # 添加记录按钮
        self.add_button = QPushButton("添加记录")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_diet_record)
        
        controls_layout.addLayout(date_layout)
        controls_layout.addLayout(meal_layout)
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_button)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("separator")
        
        # 记录表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(7)
        self.records_table.setHorizontalHeaderLabels([
            "时间", "餐食类型", "食物", "数量", "热量(kcal)", "蛋白质(g)", "碳水(g)"
        ])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 记录操作按钮
        record_buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self.edit_diet_record)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_diet_record)
        
        record_buttons_layout.addStretch()
        record_buttons_layout.addWidget(self.edit_button)
        record_buttons_layout.addWidget(self.delete_button)
        
        # 营养摄入总结
        summary_group = QGroupBox("今日营养摄入总结")
        summary_layout = QFormLayout()
        
        self.total_calories_label = QLabel("0 kcal")
        self.total_protein_label = QLabel("0 g")
        self.total_fat_label = QLabel("0 g")
        self.total_carbs_label = QLabel("0 g")
        self.total_fiber_label = QLabel("0 g")
        
        summary_layout.addRow(QLabel("总热量:"), self.total_calories_label)
        summary_layout.addRow(QLabel("蛋白质:"), self.total_protein_label)
        summary_layout.addRow(QLabel("脂肪:"), self.total_fat_label)
        summary_layout.addRow(QLabel("碳水化合物:"), self.total_carbs_label)
        summary_layout.addRow(QLabel("膳食纤维:"), self.total_fiber_label)
        
        summary_group.setLayout(summary_layout)
        
        # 将所有组件添加到主布局
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.records_table)
        main_layout.addLayout(record_buttons_layout)
        main_layout.addWidget(summary_group)
        
        self.setLayout(main_layout)
        
        # 加载初始数据
        self.load_diet_records()
        
    def load_diet_records(self):
        """加载饮食记录"""
        try:
            date = self.date_edit.date().toString("yyyy-MM-dd")
            meal_type = self.meal_combo.currentText()
            
            print(f"加载饮食记录: 日期={date}, 餐食类型={meal_type}")
            
            # 获取记录
            if meal_type == "全部":
                records = self.db_manager.get_diet_records_by_date(self.user_id, date)
            else:
                records = self.db_manager.get_diet_records_by_date_and_meal(self.user_id, date, meal_type)
            
            print(f"获取到 {len(records)} 条记录")
            if records and len(records) > 0:
                print(f"第一条记录结构: {records[0]}")
            
            # 更新表格
            self.records_table.setRowCount(len(records))
            
            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0
            total_fiber = 0
            
            for row, record in enumerate(records):
                # 添加调试信息
                print(f"处理第{row+1}条记录: 长度={len(record)}")
                
                # 安全获取食物营养数据，使用默认值防止索引错误
                try:
                    # 尝试获取基本记录数据
                    record_id = record[0]
                    food_name = record[3] if len(record) > 3 else "未知食物"
                    amount = record[4] if len(record) > 4 else 0
                    unit = record[5] if len(record) > 5 else "份"
                    meal_type = record[6] if len(record) > 6 else "未知"
                    
                    # 安全地获取时间字符串
                    record_time_str = "00:00"
                    if len(record) > 8 and record[8]:
                        try:
                            # 如果时间格式是 "HH:MM:SS"
                            if ":" in record[8]:
                                record_time_str = record[8].split(":")[0:2]
                                record_time_str = ":".join(record_time_str)
                            # 如果时间格式是 "YYYY-MM-DD HH:MM:SS"
                            elif " " in record[8]:
                                record_time_str = record[8].split()[1].split(":")[0:2]
                                record_time_str = ":".join(record_time_str)
                        except Exception as e:
                            print(f"处理时间字符串出错: {str(e)}, 使用默认时间")
                            record_time_str = "00:00"
                    
                    print(f"  基本信息: id={record_id}, 食物={food_name}, 数量={amount}{unit}, 类型={meal_type}, 时间={record_time_str}")
                    
                    # 尝试获取食物营养数据
                    # 检查记录长度，防止索引错误
                    if len(record) > 11:  # 确保能访问record[11]及以后的元素
                        print(f"  尝试获取营养信息: 记录从索引11开始的值: {record[11:] if len(record) > 11 else '无'}")
                        
                    if len(record) > 11:  # 确保能访问record[11]
                        food_calories = record[11] if record[11] is not None else 0  # 每100g的热量
                    else:
                        food_calories = 0
                        
                    if len(record) > 12:
                        food_protein = record[12] if record[12] is not None else 0  # 每100g的蛋白质
                    else:
                        food_protein = 0
                        
                    if len(record) > 13:
                        food_fat = record[13] if record[13] is not None else 0  # 每100g的脂肪
                    else:
                        food_fat = 0
                        
                    if len(record) > 14:
                        food_carbs = record[14] if record[14] is not None else 0  # 每100g的碳水
                    else:
                        food_carbs = 0
                        
                    if len(record) > 15:
                        food_fiber = record[15] if record[15] is not None else 0  # 每100g的膳食纤维
                    else:
                        food_fiber = 0
                        
                    if len(record) > 16:
                        food_standard_weight = record[16] if record[16] is not None else 100  # 标准重量
                    else:
                        food_standard_weight = 100  # 默认100克
                    
                    print(f"  营养信息: 热量={food_calories}, 蛋白质={food_protein}, 脂肪={food_fat}, 碳水={food_carbs}, 纤维={food_fiber}, 标准重量={food_standard_weight}")
                    
                    # 根据单位转换为克重
                    weight_in_grams = amount
                    if unit != "克" and unit != "g" and unit != "ml":
                        weight_in_grams = amount * food_standard_weight
                    
                    # 计算实际营养摄入
                    actual_calories = food_calories * (weight_in_grams / 100)
                    actual_protein = food_protein * (weight_in_grams / 100)
                    actual_fat = food_fat * (weight_in_grams / 100)
                    actual_carbs = food_carbs * (weight_in_grams / 100)
                    actual_fiber = food_fiber * (weight_in_grams / 100)
                    
                    # 累加总营养摄入
                    total_calories += actual_calories
                    total_protein += actual_protein
                    total_fat += actual_fat
                    total_carbs += actual_carbs
                    total_fiber += actual_fiber
                    
                    print(f"  计算结果: 实际热量={actual_calories:.1f}, 实际蛋白质={actual_protein:.1f}, 实际脂肪={actual_fat:.1f}, 实际碳水={actual_carbs:.1f}, 实际纤维={actual_fiber:.1f}")
                    
                    # 设置表格项
                    time_item = QTableWidgetItem(record_time_str)
                    self.records_table.setItem(row, 0, time_item)
                    
                    meal_item = QTableWidgetItem(meal_type)
                    self.records_table.setItem(row, 1, meal_item)
                    
                    food_item = QTableWidgetItem(food_name)
                    self.records_table.setItem(row, 2, food_item)
                    
                    amount_item = QTableWidgetItem(f"{amount} {unit}")
                    self.records_table.setItem(row, 3, amount_item)
                    
                    calories_item = QTableWidgetItem(f"{actual_calories:.1f}")
                    self.records_table.setItem(row, 4, calories_item)
                    
                    protein_item = QTableWidgetItem(f"{actual_protein:.1f}")
                    self.records_table.setItem(row, 5, protein_item)
                    
                    carbs_item = QTableWidgetItem(f"{actual_carbs:.1f}")
                    self.records_table.setItem(row, 6, carbs_item)
                    
                    # 存储记录ID为隐藏数据
                    time_item.setData(Qt.UserRole, record_id)
                    
                    # 为不同餐食类型设置不同颜色
                    row_color = QColor(255, 255, 255)  # 默认白色
                    if meal_type == "早餐":
                        row_color = QColor(255, 240, 220)  # 浅橙色
                    elif meal_type == "午餐":
                        row_color = QColor(220, 255, 220)  # 浅绿色
                    elif meal_type == "晚餐":
                        row_color = QColor(220, 240, 255)  # 浅蓝色
                    elif meal_type == "加餐":
                        row_color = QColor(255, 220, 255)  # 浅紫色
                    
                    print(f"  设置表格行颜色: {row_color.name()}")
                    
                    # 设置行背景色
                    for col in range(self.records_table.columnCount()):
                        # 确保每个单元格都已创建
                        if self.records_table.item(row, col) is None:
                            self.records_table.setItem(row, col, QTableWidgetItem(""))
                        # 然后设置背景色
                        self.records_table.item(row, col).setBackground(row_color)
                        
                    print(f"  行{row}处理完成")
                    
                except Exception as e:
                    print(f"处理记录时出错 (行 {row}): {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # 如果出错，尝试至少显示基本信息
                    for col in range(self.records_table.columnCount()):
                        if self.records_table.item(row, col) is None:
                            self.records_table.setItem(row, col, QTableWidgetItem("错误"))
            
            # 更新营养摄入总结
            self.total_calories_label.setText(f"{total_calories:.1f} kcal")
            self.total_protein_label.setText(f"{total_protein:.1f} g")
            self.total_fat_label.setText(f"{total_fat:.1f} g")
            self.total_carbs_label.setText(f"{total_carbs:.1f} g")
            self.total_fiber_label.setText(f"{total_fiber:.1f} g")
            
        except Exception as e:
            print(f"加载饮食记录出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def add_diet_record(self):
        """添加饮食记录"""
        # 先让用户选择餐食类型
        meal_type = self.meal_combo.currentText()
        if meal_type == "全部":
            # 如果没有选择具体餐食类型，弹出选择对话框
            meal_types = ["早餐", "午餐", "晚餐", "加餐"]
            selected_meal, ok = QInputDialog.getItem(
                self, "选择餐食类型", "请选择要添加记录的餐食类型:", 
                meal_types, 0, False
            )
            if not ok:
                return
            meal_type = selected_meal
        
        # 获取当前日期的已有记录
        current_date = self.date_edit.date().toString("yyyy-MM-dd")
        existing_records = self.db_manager.get_diet_records_by_date_and_meal(
            self.user_id, current_date, meal_type
        )
        
        # 打开批量编辑对话框
        dialog = MealBatchEditDialog(
            self.user_id, 
            self.db_manager, 
            current_date, 
            meal_type, 
            existing_records,
            self
        )
        dialog.records_updated.connect(self.load_diet_records)
        dialog.exec_()
    
    def edit_diet_record(self):
        """编辑饮食记录"""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一条记录!")
            return
        
        # 获取选中行的第一个单元格，以便获取记录ID
        row = selected_items[0].row()
        record_id = self.records_table.item(row, 0).data(Qt.UserRole)
        
        # 这里你可以实现编辑记录的逻辑，如打开一个编辑对话框
        # 暂时简单地提示一下
        QMessageBox.information(self, "提示", f"编辑记录功能待实现，记录ID: {record_id}")
    
    def delete_diet_record(self):
        """删除饮食记录"""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一条记录!")
            return
        
        # 获取选中行的第一个单元格，以便获取记录ID
        row = selected_items[0].row()
        record_id = self.records_table.item(row, 0).data(Qt.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除这条记录吗？此操作不可恢复!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.db_manager.delete_diet_record(record_id)
            if success:
                self.load_diet_records()  # 重新加载记录
                QMessageBox.information(self, "成功", "记录已删除!")
            else:
                QMessageBox.warning(self, "错误", "删除记录失败，请重试!")

    def update_date(self, selected_date):
        """更新当前显示的日期，并重新加载数据"""
        try:
            if isinstance(selected_date, str):
                # 如果是字符串格式，转换为QDate
                q_date = QDate.fromString(selected_date, "yyyy-MM-dd")
            else:
                # 假设已经是QDate对象
                q_date = selected_date
                
            if q_date and q_date.isValid():
                self.date_edit.setDate(q_date)
                # load_diet_records会在date_edit的dateChanged信号触发时自动调用
            else:
                print(f"无效的日期格式: {selected_date}")
        except Exception as e:
            print(f"更新饮食视图日期出错: {str(e)}") 