from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QScrollArea, QWidget, QFrame,
                           QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from ui.diet_record import DietRecordDialog

class MealBatchEditDialog(QDialog):
    """餐食批量编辑对话框，允许编辑一餐中的多个食物"""
    
    records_updated = pyqtSignal()
    
    def __init__(self, user_id, db_manager, date, meal_type, existing_records=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        self.date = date
        self.meal_type = meal_type
        self.existing_records = existing_records or []
        
        self.setWindowTitle(f"编辑{meal_type} - {date}")
        self.resize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f"编辑 {self.meal_type} ({self.date})")
        title_label.setObjectName("sectionTitle")
        main_layout.addWidget(title_label)
        
        # 现有记录区域
        if self.existing_records:
            existing_label = QLabel("已添加的食物:")
            existing_label.setObjectName("groupTitle")
            main_layout.addWidget(existing_label)
            
            # 使用滚动区域显示已有记录
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            
            for record in self.existing_records:
                record_frame = QFrame()
                record_frame.setFrameShape(QFrame.StyledPanel)
                record_layout = QHBoxLayout(record_frame)
                
                # 食物名称和数量
                food_name = record[3]  # food_name在索引3
                amount = record[4]     # amount在索引4
                unit = record[5]       # unit在索引5
                
                record_label = QLabel(f"{food_name} - {amount} {unit}")
                record_layout.addWidget(record_label)
                
                # 在这里可以添加编辑按钮，但按照需求只允许新增不允许删除
                # edit_btn = QPushButton("编辑")
                # record_layout.addWidget(edit_btn)
                
                scroll_layout.addWidget(record_frame)
            
            scroll_layout.addStretch()
            scroll_area.setWidget(scroll_content)
            main_layout.addWidget(scroll_area)
        
        # 添加新食物按钮
        add_button = QPushButton("添加新食物")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self.add_new_food)
        main_layout.addWidget(add_button)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def add_new_food(self):
        """添加新食物"""
        dialog = DietRecordDialog(self.user_id, self.db_manager, self)
        # 预设日期和餐食类型
        dialog.date_edit.setDate(QDate.fromString(self.date, "yyyy-MM-dd"))
        index = dialog.meal_type.findText(self.meal_type)
        if index >= 0:
            dialog.meal_type.setCurrentIndex(index)
        
        if dialog.exec_() == QDialog.Accepted:
            self.records_updated.emit()
            # 刷新当前对话框中显示的记录
            self.existing_records = self.db_manager.get_diet_records_by_date_and_meal(
                self.user_id, self.date, self.meal_type
            )
            # 重新初始化UI以显示新添加的记录
            # 清除旧的布局
            QWidget().setLayout(self.layout())
            self.init_ui() 