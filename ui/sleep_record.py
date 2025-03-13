from PyQt5.QtWidgets import (QDialog, QLabel, QComboBox, QLineEdit, QTextEdit,
                           QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QDateEdit, QTimeEdit, QSpinBox, QMessageBox, QSlider,
                           QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QDateTime
from PyQt5.QtGui import QFont

import datetime

class SleepRecordDialog(QDialog):
    """睡眠记录对话框"""
    
    # 定义信号
    record_added = pyqtSignal()
    
    def __init__(self, user_id, db_manager, parent=None, record_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db_manager = db_manager
        self.record_id = record_id  # 如果有记录ID，表示是编辑模式
        
        self.setWindowTitle("添加睡眠记录" if not record_id else "编辑睡眠记录")
        self.resize(800, 600)
        
        self.init_ui()
        
        # 如果是编辑模式，加载现有记录
        if self.record_id:
            self.load_record()
    
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # 创建表单布局
        form_group = QGroupBox("睡眠记录详情")
        form_layout = QFormLayout()
        
        # 睡眠日期和时间
        sleep_date_layout = QHBoxLayout()
        sleep_date_label = QLabel("入睡日期:")
        self.sleep_date_edit = QDateEdit(QDate.currentDate())
        self.sleep_date_edit.setCalendarPopup(True)
        self.sleep_date_edit.setDisplayFormat("yyyy-MM-dd")
        sleep_date_layout.addWidget(sleep_date_label)
        sleep_date_layout.addWidget(self.sleep_date_edit)
        
        sleep_time_label = QLabel("入睡时间:")
        self.sleep_time_edit = QTimeEdit(QTime(22, 30))  # 默认晚上10:30
        self.sleep_time_edit.setDisplayFormat("HH:mm")
        sleep_date_layout.addWidget(sleep_time_label)
        sleep_date_layout.addWidget(self.sleep_time_edit)
        sleep_date_layout.addStretch()
        
        # 起床日期和时间
        wake_date_layout = QHBoxLayout()
        wake_date_label = QLabel("起床日期:")
        self.wake_date_edit = QDateEdit(QDate.currentDate().addDays(1))  # 默认第二天
        self.wake_date_edit.setCalendarPopup(True)
        self.wake_date_edit.setDisplayFormat("yyyy-MM-dd")
        wake_date_layout.addWidget(wake_date_label)
        wake_date_layout.addWidget(self.wake_date_edit)
        
        wake_time_label = QLabel("起床时间:")
        self.wake_time_edit = QTimeEdit(QTime(7, 0))  # 默认早上7:00
        self.wake_time_edit.setDisplayFormat("HH:mm")
        wake_date_layout.addWidget(wake_time_label)
        wake_date_layout.addWidget(self.wake_time_edit)
        wake_date_layout.addStretch()
        
        # 计算睡眠时长按钮
        calculate_layout = QHBoxLayout()
        calculate_button = QPushButton("计算睡眠时长")
        calculate_button.clicked.connect(self.calculate_duration)
        calculate_layout.addWidget(calculate_button)
        calculate_layout.addStretch()
        
        # 睡眠时长显示
        duration_layout = QHBoxLayout()
        duration_label = QLabel("睡眠时长:")
        self.duration_hours = QSpinBox()
        self.duration_hours.setRange(0, 24)
        self.duration_hours.setValue(8)  # 默认8小时
        self.duration_hours.setSuffix(" 小时")
        
        self.duration_minutes = QSpinBox()
        self.duration_minutes.setRange(0, 59)
        self.duration_minutes.setValue(30)  # 默认30分钟
        self.duration_minutes.setSuffix(" 分钟")
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_hours)
        duration_layout.addWidget(self.duration_minutes)
        duration_layout.addStretch()
        
        # 睡眠质量评分
        quality_layout = QVBoxLayout()
        quality_label = QLabel("睡眠质量:")
        quality_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        rating_layout = QHBoxLayout()
        self.quality_group = QButtonGroup(self)
        
        quality_options = ["很差", "较差", "一般", "良好", "优秀"]
        self.quality_radios = []
        
        for i, option in enumerate(quality_options):
            radio = QRadioButton(option)
            if i == 2:  # 默认选择"一般"
                radio.setChecked(True)
            self.quality_radios.append(radio)
            self.quality_group.addButton(radio, i + 1)  # 使用1-5作为ID
            rating_layout.addWidget(radio)
        
        quality_layout.addWidget(quality_label)
        quality_layout.addLayout(rating_layout)
        
        # 备注
        notes_label = QLabel("备注:")
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("请输入睡眠相关备注，如：是否做梦、是否容易醒来等...")
        
        # 将所有组件添加到表单布局
        form_layout.addRow(sleep_date_layout)
        form_layout.addRow(wake_date_layout)
        form_layout.addRow(calculate_layout)
        form_layout.addRow(duration_layout)
        form_layout.addRow("睡眠质量:", rating_layout)
        form_layout.addRow(notes_label, self.notes_text)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_record)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        # 初始计算一次时长
        self.calculate_duration()
        
    def calculate_duration(self):
        """计算睡眠时长"""
        try:
            sleep_date = self.sleep_date_edit.date()
            sleep_time = self.sleep_time_edit.time()
            wake_date = self.wake_date_edit.date()
            wake_time = self.wake_time_edit.time()
            
            # 创建完整的日期时间对象
            sleep_datetime = QDateTime(sleep_date, sleep_time)
            wake_datetime = QDateTime(wake_date, wake_time)
            
            # 计算时间差（秒）
            duration_secs = sleep_datetime.secsTo(wake_datetime)
            
            # 如果结果为负，说明醒来时间在睡觉前面，可能是跨天睡眠
            if duration_secs < 0:
                QMessageBox.warning(self, "时间错误", "醒来时间必须在睡眠时间之后!")
                # 自动修正：假设第二天醒来
                self.wake_date_edit.setDate(sleep_date.addDays(1))
                return self.calculate_duration()  # 重新计算
                
            # 转换为小时和分钟
            duration_minutes = duration_secs // 60
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            
            # 更新显示
            self.duration_hours.setValue(hours)
            self.duration_minutes.setValue(minutes)
            
            return duration_minutes  # 返回总分钟数
            
        except Exception as e:
            print(f"计算睡眠时长出错: {str(e)}")
            QMessageBox.warning(self, "计算错误", f"计算睡眠时长时出错: {str(e)}")
            return 0
    
    def get_quality_value(self):
        """获取当前选择的睡眠质量值（1-5）"""
        return self.quality_group.checkedId()
    
    def load_record(self):
        """加载现有记录数据（编辑模式）"""
        try:
            # 从数据库获取记录
            record = None
            
            # 检查数据库是否有该方法
            if hasattr(self.db_manager, 'get_sleep_record_by_id'):
                record = self.db_manager.get_sleep_record_by_id(self.record_id)
            else:
                # 尝试使用通用方法
                try:
                    record = self.db_manager.get_record_by_id('sleep_records', self.record_id)
                except Exception as e:
                    print(f"尝试使用通用方法获取睡眠记录失败: {str(e)}")
                    # 最后尝试使用sleep_records表直接查询
                    try:
                        with self.db_manager as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM sleep_records WHERE id = ?", (self.record_id,))
                            record = cursor.fetchone()
                    except Exception as inner_e:
                        print(f"直接查询数据库失败: {str(inner_e)}")
            
            if not record:
                QMessageBox.warning(self, "错误", "无法加载睡眠记录，请重试!")
                self.reject()
                return
            
            # 解析记录数据
            record_id, user_id, create_time, sleep_date, sleep_time, wake_date, wake_time, duration, quality, notes = record
            
            # 设置界面值
            self.sleep_date_edit.setDate(QDate.fromString(sleep_date, "yyyy-MM-dd"))
            self.sleep_time_edit.setTime(QTime.fromString(sleep_time, "HH:mm:ss"))
            self.wake_date_edit.setDate(QDate.fromString(wake_date, "yyyy-MM-dd"))
            self.wake_time_edit.setTime(QTime.fromString(wake_time, "HH:mm:ss"))
            
            # 设置时长
            hours = duration // 60
            minutes = duration % 60
            self.duration_hours.setValue(hours)
            self.duration_minutes.setValue(minutes)
            
            # 设置质量
            if 0 <= quality <= 5:
                button = self.quality_group.button(quality)
                if button:
                    button.setChecked(True)
            
            # 设置备注
            if notes:
                self.notes_text.setText(notes)
                
        except Exception as e:
            print(f"加载睡眠记录出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"加载睡眠记录时出错: {str(e)}")
            self.reject()
    
    def save_record(self):
        """保存睡眠记录"""
        try:
            # 获取界面数据
            sleep_date = self.sleep_date_edit.date().toString("yyyy-MM-dd")
            sleep_time = self.sleep_time_edit.time().toString("HH:mm:ss")
            wake_date = self.wake_date_edit.date().toString("yyyy-MM-dd")
            wake_time = self.wake_time_edit.time().toString("HH:mm:ss")
            
            # 计算时长（分钟）
            duration = self.calculate_duration()
            if duration <= 0:
                QMessageBox.warning(self, "错误", "睡眠时长必须大于0!")
                return
            
            # 获取质量评分
            quality = self.get_quality_value()
            
            # 获取备注
            notes = self.notes_text.toPlainText()
            
            # 根据模式保存记录
            success = False
            if self.record_id:  # 编辑模式
                success = self.db_manager.update_sleep_record(
                    self.record_id,
                    sleep_date=sleep_date,
                    sleep_time=sleep_time,
                    wake_date=wake_date,
                    wake_time=wake_time,
                    duration=duration,
                    quality=quality,
                    notes=notes
                )
                message = "睡眠记录已更新!"
            else:  # 添加模式
                success = self.db_manager.add_sleep_record(
                    self.user_id,
                    sleep_date,
                    sleep_time,
                    wake_date,
                    wake_time,
                    duration,
                    quality,
                    notes
                )
                message = "睡眠记录已添加!"
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.record_added.emit()  # 发出记录添加信号
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "保存睡眠记录失败，请重试!")
                
        except Exception as e:
            print(f"保存睡眠记录出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"保存睡眠记录时出错: {str(e)}") 