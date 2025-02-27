from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QTabWidget,
                            QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow

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
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setObjectName("actionButton")
        self.login_button.clicked.connect(self.login)
        
        # 添加到布局
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addStretch()
        layout.addWidget(self.login_button)
        
        self.login_tab.setLayout(layout)
        
    def setup_register_tab(self):
        """设置注册标签页"""
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 增加间距
        
        # 用户名
        username_layout = QVBoxLayout()  # 改为垂直布局
        username_label = QLabel("用户名")
        username_label.setObjectName("fieldLabel")
        self.register_username = QLineEdit()
        self.register_username.setObjectName("inputField")
        self.register_username.setPlaceholderText("请创建用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.register_username)
        
        # 密码
        password_layout = QVBoxLayout()  # 改为垂直布局
        password_label = QLabel("密码")
        password_label.setObjectName("fieldLabel")
        self.register_password = QLineEdit()
        self.register_password.setObjectName("inputField")
        self.register_password.setPlaceholderText("请创建密码")
        self.register_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.register_password)
        
        # 确认密码
        confirm_layout = QVBoxLayout()  # 改为垂直布局
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
        layout.addLayout(password_layout)
        layout.addLayout(confirm_layout)
        layout.addStretch()
        layout.addWidget(self.register_button)
        
        self.register_tab.setLayout(layout)
    
    def login(self):
        """处理登录逻辑"""
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空!")
            return
        
        user_id = self.db_manager.verify_user(username, password)
        if user_id:
            self.open_main_window(user_id, username)
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误!")
            
    def register(self):
        """处理注册逻辑"""
        username = self.register_username.text()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空!")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致!")
            return
            
        user_id = self.db_manager.add_user(username, password)
        if user_id:
            QMessageBox.information(self, "注册成功", "注册成功，请登录!")
            self.tab_widget.setCurrentIndex(0)  # 切换到登录页
            self.register_username.clear()
            self.register_password.clear()
            self.register_confirm.clear()
        else:
            QMessageBox.warning(self, "注册失败", "用户名已存在!")
            
    def open_main_window(self, user_id, username):
        """打开主窗口"""
        self.main_window = MainWindow(user_id, username)
        self.main_window.show()
        self.close() 