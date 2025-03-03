import sys
from PyQt5.QtWidgets import QApplication
from ui.login import LoginWindow
import logging
import os
from utils.style_helper import load_stylesheet
from database.db_manager import DatabaseManager

# 在main.py顶部添加
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

def main():
    app = QApplication(sys.argv)
    
    # 加载全局样式表
    style_path = "resources/styles/style.qss"
    if os.path.exists(style_path):
        app.setStyleSheet(load_stylesheet(style_path))
    
    # 初始化数据库管理器
    db_manager = DatabaseManager()
    
    # 初始化食物数据库
    db_manager.initialize_food_database()
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# 然后在代码中使用
logging.debug("调试信息")
logging.info("一般信息")
logging.error("错误信息") 