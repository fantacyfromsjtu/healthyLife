from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt

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
        self.resize(400, 300)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        
        # 设置登录页
        self.setup_login_tab()
        
        # 设置注册页
        self.setup_register_tab()
        
        # 添加标签页
        self.tab_widget.addTab(self.login_tab, "登录")
        self.tab_widget.addTab(self.register_tab, "注册")
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        
    def setup_login_tab(self):
        """设置登录标签页"""
        layout = QVBoxLayout()
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        self.login_username = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.login_username)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.login_password)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.login)
        
        # 添加到布局
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.login_button)
        layout.addStretch()
        
        self.login_tab.setLayout(layout)
        
    def setup_register_tab(self):
        """设置注册标签页"""
        layout = QVBoxLayout()
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        self.register_username = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.register_username)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.register_password)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("确认密码:")
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.register_confirm)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.clicked.connect(self.register)
        
        # 添加到布局
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(confirm_layout)
        layout.addWidget(self.register_button)
        layout.addStretch()
        
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