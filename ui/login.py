from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QTabWidget,
                            QFrame, QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow
from ui.profile import ProfileWindow
from utils.verification import validate_password_strength, generate_captcha_text, generate_captcha_image
import time

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('健康生活 - 登录/注册')
        self.resize(1000, 800)  # 增大窗口尺寸
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)  # 增加边距
        
        # 添加应用标题
        title_label = QLabel("健康生活管理")
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加应用描述
        description = QLabel("记录健康数据，培养良好习惯")
        description.setObjectName("appDescription")
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)
        
        # 创建内容框
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("authTabs")
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        
        # 设置登录页
        self.setup_login_tab()
        
        # 设置注册页
        self.setup_register_tab()
        
        # 添加标签页
        self.tab_widget.addTab(self.login_tab, "登录")
        self.tab_widget.addTab(self.register_tab, "注册")
        
        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(content_frame)
        
        # 添加版权信息
        copyright_label = QLabel("© 2025 大学生健康生活")
        copyright_label.setObjectName("copyright")
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)
        
        self.setLayout(main_layout)
        
        # 初始选择登录标签页
        self.tab_widget.setCurrentIndex(0)
    
    def setup_login_tab(self):
        """设置登录标签页"""
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 增加间距
        
        # 用户名
        username_layout = QVBoxLayout()  # 改为垂直布局
        username_label = QLabel("用户名")
        username_label.setObjectName("fieldLabel")
        self.login_username = QLineEdit()
        self.login_username.setObjectName("inputField")
        self.login_username.setPlaceholderText("请输入用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.login_username)
        
        # 密码
        password_layout = QVBoxLayout()  # 改为垂直布局
        password_label = QLabel("密码")
        password_label.setObjectName("fieldLabel")
        self.login_password = QLineEdit()
        self.login_password.setObjectName("inputField")
        self.login_password.setPlaceholderText("请输入密码")
        self.login_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.login_password)
        
        # 图形验证码 (新增)
        captcha_layout = QVBoxLayout()
        captcha_label = QLabel("验证码")
        captcha_label.setObjectName("fieldLabel")
        
        captcha_input_layout = QHBoxLayout()
        self.login_captcha = QLineEdit()
        self.login_captcha.setObjectName("inputField")
        self.login_captcha.setPlaceholderText("请输入验证码")
        self.login_captcha.setMaxLength(4)
        self.login_captcha.setMinimumWidth(180)  # 适合验证码的宽度
        
        # 验证码图片标签
        self.login_captcha_image = QLabel()
        self.login_captcha_image.setFixedSize(160, 60)  # 增加尺寸
        self.login_captcha_image.setCursor(Qt.PointingHandCursor)
        self.login_captcha_image.mousePressEvent = self.refresh_login_captcha
        
        # 刷新验证码按钮
        self.login_refresh_button = QPushButton("刷新")
        self.login_refresh_button.setObjectName("secondaryButton")
        self.login_refresh_button.clicked.connect(lambda: self.refresh_login_captcha(None))
        
        captcha_input_layout.addWidget(self.login_captcha, 3)
        captcha_input_layout.addWidget(self.login_captcha_image, 1)
        captcha_input_layout.addWidget(self.login_refresh_button, 1)
        
        captcha_layout.addWidget(captcha_label)
        captcha_layout.addLayout(captcha_input_layout)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setObjectName("actionButton")
        self.login_button.clicked.connect(self.login)
        
        # 添加到布局
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(captcha_layout)  # 添加验证码布局
        layout.addStretch()
        layout.addWidget(self.login_button)
        
        self.login_tab.setLayout(layout)
        
        # 初始生成验证码
        self.login_captcha_text = ""  # 存储当前登录验证码文本
        self.refresh_login_captcha(None)
    
    def setup_register_tab(self):
        """设置注册标签页"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 用户名
        username_layout = QVBoxLayout()
        username_label = QLabel("用户名")
        username_label.setObjectName("fieldLabel")
        self.register_username = QLineEdit()
        self.register_username.setObjectName("inputField")
        self.register_username.setPlaceholderText("请创建用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.register_username)
        
        # 图形验证码
        captcha_layout = QVBoxLayout()
        captcha_label = QLabel("验证码")
        captcha_label.setObjectName("fieldLabel")
        
        captcha_input_layout = QHBoxLayout()
        self.register_captcha = QLineEdit()
        self.register_captcha.setObjectName("inputField")
        self.register_captcha.setPlaceholderText("请输入验证码")
        self.register_captcha.setMaxLength(4)
        self.register_captcha.setMinimumWidth(180)  # 适合验证码的宽度
        
        # 验证码图片标签
        self.captcha_image = QLabel()
        self.captcha_image.setFixedSize(160, 60)  # 增加尺寸
        self.captcha_image.setCursor(Qt.PointingHandCursor)
        self.captcha_image.mousePressEvent = self.refresh_captcha
        
        # 刷新验证码按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(lambda: self.refresh_captcha(None))
        
        captcha_input_layout.addWidget(self.register_captcha, 3)  # 3:1:1 的比例
        captcha_input_layout.addWidget(self.captcha_image, 1)
        captcha_input_layout.addWidget(self.refresh_button, 1)
        
        captcha_layout.addWidget(captcha_label)
        captcha_layout.addLayout(captcha_input_layout)
        
        # 密码
        password_layout = QVBoxLayout()
        password_label = QLabel("密码")
        password_label.setObjectName("fieldLabel")
        self.register_password = QLineEdit()
        self.register_password.setObjectName("inputField")
        self.register_password.setPlaceholderText("请创建密码(至少8位，包含字母和数字)")
        self.register_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.register_password)
        
        # 确认密码
        confirm_layout = QVBoxLayout()
        confirm_label = QLabel("确认密码")
        confirm_label.setObjectName("fieldLabel")
        self.register_confirm = QLineEdit()
        self.register_confirm.setObjectName("inputField")
        self.register_confirm.setPlaceholderText("请再次输入密码")
        self.register_confirm.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.register_confirm)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.setObjectName("actionButton")
        self.register_button.clicked.connect(self.register)
        
        # 添加到布局
        layout.addLayout(username_layout)
        layout.addLayout(captcha_layout)
        layout.addLayout(password_layout)
        layout.addLayout(confirm_layout)
        layout.addStretch()
        layout.addWidget(self.register_button)
        
        self.register_tab.setLayout(layout)
        
        # 初始生成验证码
        self.refresh_captcha(None)
        self.captcha_text = ""  # 存储当前验证码文本
    
    def refresh_captcha(self, event):
        """刷新验证码"""
        pixmap, self.captcha_text = generate_captcha_image(generate_captcha_text())
        self.captcha_image.setPixmap(pixmap)
    
    def register(self):
        """处理注册逻辑"""
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        captcha = self.register_captcha.text().strip().upper()  # 转为大写比较
        
        # 基本验证
        if not username or not password or not captcha:
            QMessageBox.warning(self, "警告", "所有字段都是必填的!")
            return
        
        # 验证密码强度
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            QMessageBox.warning(self, "警告", message)
            return
        
        # 验证两次密码是否一致
        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致!")
            return
        
        # 验证图形验证码
        if captcha != self.captcha_text:
            QMessageBox.warning(self, "警告", "验证码错误!")
            self.refresh_captcha(None)  # 刷新验证码
            return
        
        # 添加用户
        user_id = self.db_manager.add_user(username, password)
        if user_id:
            QMessageBox.information(self, "注册成功", "注册成功，请登录!")
            self.tab_widget.setCurrentIndex(0)  # 切换到登录页
            self.register_username.clear()
            self.register_password.clear()
            self.register_confirm.clear()
            self.register_captcha.clear()
            self.refresh_captcha(None)  # 刷新验证码
        else:
            QMessageBox.warning(self, "注册失败", "用户名已存在!")
            
    def refresh_login_captcha(self, event):
        """刷新登录验证码"""
        pixmap, self.login_captcha_text = generate_captcha_image(generate_captcha_text())
        self.login_captcha_image.setPixmap(pixmap)
    
    def login(self):
        """用户登录"""
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        captcha = self.login_captcha.text().strip()
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名!")
            return
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码!")
            return
        if not captcha:
            QMessageBox.warning(self, "警告", "请输入验证码!")
            return
        if captcha.lower() != self.login_captcha_text.lower():
            QMessageBox.warning(self, "警告", "验证码错误!")
            self.login_captcha.clear()
            self.refresh_login_captcha(None)
            return
        
        # 验证用户登录
        try:
            # 创建数据库连接
            if not hasattr(self, 'db_manager'):
                try:
                    from database.db_manager import DatabaseManager
                    self.db_manager = DatabaseManager('database/health_life.db')
                    print("已创建数据库连接")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法连接数据库: {str(e)}")
                    return
            
            user_id = self.db_manager.verify_user(username, password)
            if user_id:
                print(f"用户登录成功: {username}, ID: {user_id}")
                
                # 检查用户资料是否完整
                try:
                    user_data = self.db_manager.get_user_profile(user_id)
                    print(f"获取到用户资料: {user_data}")
                    
                    # 防止None值导致的错误
                    if user_data is None:
                        print("用户资料为None，创建空字典")
                        user_data = {}
                    
                    # 使用get方法安全地获取可能不存在的键的值
                    is_first_login = not user_data.get("gender") and not user_data.get("age")
                    print(f"是否首次登录: {is_first_login}")
                    
                    if is_first_login:
                        from ui.profile import ProfileWindow
                        profile_window = ProfileWindow(user_id, username, self.db_manager, True)
                        # 直接连接信号到我们自己的方法而不是open_main_window
                        profile_window.profile_updated.connect(lambda uid, uname: self.handle_profile_updated(uid, uname))
                        profile_window.exec_()
                    else:
                        self.open_main_window(user_id, username)
                except Exception as e:
                    print(f"处理用户资料时出错: {str(e)}")
                    QMessageBox.warning(self, "警告", f"登录过程中发生错误: {str(e)}")
                    # 尽管发生错误，仍尝试打开主窗口
                    self.open_main_window(user_id, username)
            else:
                QMessageBox.warning(self, "警告", "用户名或密码错误!")
                self.login_password.clear()
                self.login_captcha.clear()
                self.refresh_login_captcha(None)
        except Exception as e:
            print(f"登录过程发生异常: {str(e)}")
            QMessageBox.critical(self, "错误", f"登录过程中发生错误: {str(e)}")
            self.refresh_login_captcha(None)
    
    def handle_profile_updated(self, user_id, username):
        """处理用户资料更新后的操作"""
        print(f"用户资料已更新，准备打开主窗口: {username} (ID: {user_id})")
        # 确保信号处理完成后打开主窗口
        QTimer.singleShot(100, lambda: self.open_main_window(user_id, username))
    
    def open_main_window(self, user_id, username):
        """打开主窗口"""
        print(f"正在打开主窗口: {username} (ID: {user_id})")
        # 直接导入MainWindow，避免循环导入
        from ui.main_window import MainWindow
        
        # 检查用户资料是否完整
        profile_complete = self.db_manager.is_profile_complete(user_id)
        print(f"用户资料是否完整: {profile_complete}")
        
        if not profile_complete:
            # 如果资料不完整，先打开资料编辑窗口
            from ui.profile import ProfileWindow
            profile_window = ProfileWindow(user_id, username, self.db_manager, is_first_login=True)
            profile_window.profile_updated.connect(lambda uid, uname: self.handle_profile_updated(uid, uname))
            profile_window.exec_()
        else:
            # 资料已完整，直接打开主窗口
            try:
                print("正在创建主窗口实例...")
                self.main_window = MainWindow(user_id, username, self.db_manager)
                print("正在显示主窗口...")
                self.main_window.show()
                print("关闭登录窗口...")
                self.close()
            except Exception as e:
                print(f"打开主窗口失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"打开主窗口时发生错误: {str(e)}") 