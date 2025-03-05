from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont


class ProfileWindow(QDialog):
    # 定义信号用于通知主窗口用户信息已更新
    profile_updated = pyqtSignal(int, str)

    def __init__(self, user_id, username, db_manager, is_first_login=False):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.db_manager = db_manager
        self.is_first_login = is_first_login
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        """初始化用户界面"""
        if self.is_first_login:
            self.setWindowTitle("完善个人信息")
        else:
            self.setWindowTitle("编辑个人信息")
        self.resize(800, 700)
        self.setModal(True)  # 设置为模态对话框

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # 标题
        title_label = QLabel("个人健康信息")
        title_label.setObjectName("heading")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        basic_group.setLayout(basic_layout)

        # 性别选择
        gender_layout = QHBoxLayout()
        self.male_radio = QRadioButton("男")
        self.female_radio = QRadioButton("女")
        self.gender_group = QButtonGroup()
        self.gender_group.addButton(self.male_radio, 1)
        self.gender_group.addButton(self.female_radio, 2)
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        gender_layout.addStretch()
        basic_layout.addRow(QLabel("性别:"), gender_layout)

        # 年龄
        self.age_spin = QSpinBox()
        self.age_spin.setRange(14, 100)
        self.age_spin.setValue(20)
        self.age_spin.setSuffix(" 岁")
        basic_layout.addRow(QLabel("年龄:"), self.age_spin)

        # 身高
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(100, 250)
        self.height_spin.setValue(170)
        self.height_spin.setSuffix(" 厘米")
        self.height_spin.setDecimals(1)
        self.height_spin.setSingleStep(0.5)
        basic_layout.addRow(QLabel("身高:"), self.height_spin)

        # 体重
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(30, 200)
        self.weight_spin.setValue(60)
        self.weight_spin.setSuffix(" 公斤")
        self.weight_spin.setDecimals(1)
        self.weight_spin.setSingleStep(0.5)
        basic_layout.addRow(QLabel("体重:"), self.weight_spin)

        main_layout.addWidget(basic_group)

        # 饮食习惯组
        diet_group = QGroupBox("饮食习惯")
        diet_layout = QFormLayout()
        diet_group.setLayout(diet_layout)

        # 饮食类型
        self.diet_type = QComboBox()
        self.diet_type.addItems(
            ["无特殊饮食习惯", "长期素食", "低碳水化合物", "低脂肪", "高蛋白", "其他"]
        )
        diet_layout.addRow(QLabel("饮食类型:"), self.diet_type)

        # 饮食习惯详情
        self.diet_habits = QTextEdit()
        self.diet_habits.setPlaceholderText(
            "请描述您的饮食习惯，例如：早餐通常吃什么，是否有食物过敏等..."
        )
        diet_layout.addRow(QLabel("详细描述:"), self.diet_habits)

        main_layout.addWidget(diet_group)

        # 运动习惯组
        exercise_group = QGroupBox("运动习惯")
        exercise_layout = QFormLayout()
        exercise_group.setLayout(exercise_layout)

        # 运动频率
        self.exercise_frequency = QComboBox()
        self.exercise_frequency.addItems(
            ["几乎不运动", "每周1-2次", "每周3-4次", "每周5次以上", "每天都运动"]
        )
        exercise_layout.addRow(QLabel("运动频率:"), self.exercise_frequency)

        # 运动类型
        self.exercise_types = QComboBox()
        self.exercise_types.addItems(
            [
                "步行/跑步",
                "游泳",
                "骑行",
                "球类运动",
                "健身房锻炼",
                "瑜伽/普拉提",
                "其他",
            ]
        )
        exercise_layout.addRow(QLabel("常见运动:"), self.exercise_types)

        # 运动习惯详情
        self.exercise_habits = QTextEdit()
        self.exercise_habits.setPlaceholderText(
            "请描述您的运动习惯，例如：喜欢什么运动，运动强度等..."
        )
        exercise_layout.addRow(QLabel("详细描述:"), self.exercise_habits)

        main_layout.addWidget(exercise_group)

        # 睡眠习惯组
        sleep_group = QGroupBox("睡眠习惯")
        sleep_layout = QFormLayout()
        sleep_group.setLayout(sleep_layout)

        # 睡眠时间
        sleep_layout_h = QHBoxLayout()
        self.sleep_hours = QSpinBox()
        self.sleep_hours.setRange(3, 12)
        self.sleep_hours.setValue(7)
        self.sleep_hours.setSuffix(" 小时")
        sleep_layout_h.addWidget(self.sleep_hours)
        self.sleep_minutes = QSpinBox()
        self.sleep_minutes.setRange(0, 59)
        self.sleep_minutes.setValue(0)
        self.sleep_minutes.setSuffix(" 分钟")
        sleep_layout_h.addWidget(self.sleep_minutes)
        sleep_layout_h.addStretch()
        sleep_layout.addRow(QLabel("平均睡眠时长:"), sleep_layout_h)

        # 睡眠质量
        self.sleep_quality = QComboBox()
        self.sleep_quality.addItems(["很差", "较差", "一般", "良好", "优秀"])
        self.sleep_quality.setCurrentIndex(2)  # 默认"一般"
        sleep_layout.addRow(QLabel("睡眠质量:"), self.sleep_quality)

        # 睡眠习惯详情
        self.sleep_habits = QTextEdit()
        self.sleep_habits.setPlaceholderText(
            "请描述您的睡眠习惯，例如：常规入睡和起床时间，是否有睡眠问题等..."
        )
        sleep_layout.addRow(QLabel("详细描述:"), self.sleep_habits)

        main_layout.addWidget(sleep_group)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_profile)
        button_layout.addWidget(self.save_button)

        if not self.is_first_login:
            self.cancel_button = QPushButton("取消")
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_user_data(self):
        """加载用户数据"""
        if not self.is_first_login:
            user_data = self.db_manager.get_user_profile(self.user_id)
            if user_data:
                # 设置性别
                if user_data.get("gender") == "男":
                    self.male_radio.setChecked(True)
                elif user_data.get("gender") == "女":
                    self.female_radio.setChecked(True)

                # 设置其他基本信息
                if user_data.get("age"):
                    self.age_spin.setValue(int(user_data.get("age")))
                if user_data.get("height"):
                    self.height_spin.setValue(float(user_data.get("height")))
                if user_data.get("weight"):
                    self.weight_spin.setValue(float(user_data.get("weight")))

                # 设置饮食习惯
                if user_data.get("diet_habit"):
                    habit_parts = user_data.get("diet_habit", "").split("|", 1)
                    if len(habit_parts) > 0 and habit_parts[0] in [
                        self.diet_type.itemText(i)
                        for i in range(self.diet_type.count())
                    ]:
                        self.diet_type.setCurrentText(habit_parts[0])
                    if len(habit_parts) > 1:
                        self.diet_habits.setText(habit_parts[1])

                # 设置运动习惯
                if user_data.get("exercise_habit"):
                    habit_parts = user_data.get("exercise_habit", "").split("|", 2)
                    if len(habit_parts) > 0 and habit_parts[0] in [
                        self.exercise_frequency.itemText(i)
                        for i in range(self.exercise_frequency.count())
                    ]:
                        self.exercise_frequency.setCurrentText(habit_parts[0])
                    if len(habit_parts) > 1 and habit_parts[1] in [
                        self.exercise_types.itemText(i)
                        for i in range(self.exercise_types.count())
                    ]:
                        self.exercise_types.setCurrentText(habit_parts[1])
                    if len(habit_parts) > 2:
                        self.exercise_habits.setText(habit_parts[2])

                # 设置睡眠习惯
                if user_data.get("sleep_habit"):
                    habit_parts = user_data.get("sleep_habit", "").split("|", 3)
                    if len(habit_parts) > 0:
                        try:
                            sleep_time = habit_parts[0].split(":")
                            if len(sleep_time) == 2:
                                self.sleep_hours.setValue(int(sleep_time[0]))
                                self.sleep_minutes.setValue(int(sleep_time[1]))
                        except ValueError:
                            pass
                    if len(habit_parts) > 1 and habit_parts[1] in [
                        self.sleep_quality.itemText(i)
                        for i in range(self.sleep_quality.count())
                    ]:
                        self.sleep_quality.setCurrentText(habit_parts[1])
                    if len(habit_parts) > 2:
                        self.sleep_habits.setText(habit_parts[2])

    def save_profile(self):
        """保存个人资料"""
        try:
            # 获取性别
            gender = (
                "男"
                if self.male_radio.isChecked()
                else "女" if self.female_radio.isChecked() else None
            )

            # 获取基本信息
            age = self.age_spin.value()
            height = self.height_spin.value()
            weight = self.weight_spin.value()

            # 获取饮食习惯
            diet_type = self.diet_type.currentText()
            diet_details = self.diet_habits.toPlainText()
            diet_habit = f"{diet_type}|{diet_details}"

            # 获取运动习惯
            exercise_frequency = self.exercise_frequency.currentText()
            exercise_type = self.exercise_types.currentText()
            exercise_details = self.exercise_habits.toPlainText()
            exercise_habit = f"{exercise_frequency}|{exercise_type}|{exercise_details}"

            # 获取睡眠习惯
            sleep_time = f"{self.sleep_hours.value()}:{self.sleep_minutes.value()}"
            sleep_quality_text = self.sleep_quality.currentText()
            sleep_details = self.sleep_habits.toPlainText()
            sleep_habit = f"{sleep_time}|{sleep_quality_text}|{sleep_details}"

            # 更新用户资料
            if self.db_manager.update_user_profile(
                self.user_id,
                gender,
                age,
                height,
                weight,
                diet_habit,
                exercise_habit,
                sleep_habit,
            ):
                QMessageBox.information(self, "成功", "个人资料保存成功！")
                # 发出信号通知资料已更新
                print(f"发出profile_updated信号: user_id={self.user_id}, username={self.username}")
                self.profile_updated.emit(self.user_id, self.username)
                # 延迟关闭窗口，确保信号有时间处理
                QTimer.singleShot(200, self.accept)
            else:
                QMessageBox.warning(self, "错误", "保存个人资料时出现错误！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生异常：{str(e)}")
