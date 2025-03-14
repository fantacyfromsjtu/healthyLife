#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QColor
from PyQt5.QtCore import QLocale, QTranslator, QLibraryInfo
import matplotlib
matplotlib.use('Qt5Agg')  # 设置matplotlib后端为Qt5Agg

from database.db_manager import DatabaseManager
from ui.login import LoginWindow
from utils.style_helper import refresh_style

def setup_exception_handling():
    """设置全局异常处理"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        # 准备错误信息
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"未捕获的异常:\n{error_msg}")
        
        # 如果GUI已经初始化，显示错误对话框
        if QApplication.instance():
            QMessageBox.critical(None, "错误", 
                f"发生未处理的错误:\n{str(exc_value)}\n\n请联系开发人员并提供以下信息:\n{error_msg[:500]}...")
        
        # 调用原始的异常处理器
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception

def setup_chinese_fonts(app):
    """设置中文字体支持"""
    # 创建字体族列表，包含通用字体族名称
    fontlist = "Microsoft YaHei UI, Microsoft YaHei, SimSun, SimHei, WenQuanYi Micro Hei, Source Han Sans CN, Noto Sans CJK SC, Arial, sans-serif"
    
    # 直接应用字体设置到全局样式表
    app.setStyleSheet(app.styleSheet() + f"""
    * {{
        font-family: {fontlist};
    }}
    
    QWidget {{
        font-family: {fontlist};
    }}
    """)
    
    # 设置Matplotlib字体，如果matplotlib被导入
    try:
        import matplotlib.font_manager as fm
        import matplotlib
        
        # 尝试查找系统中的中文字体
        chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'WenQuanYi Micro Hei']
        font_found = False
        
        for font_name in chinese_fonts:
            try:
                font_path = fm.findfont(font_name, fallback_to_default=False)
                if font_path:
                    matplotlib.rcParams['font.family'] = ['sans-serif']
                    matplotlib.rcParams['font.sans-serif'] = [font_name] + matplotlib.rcParams['font.sans-serif']
                    print(f"Matplotlib将使用字体: {font_name}")
                    font_found = True
                    break
            except:
                continue
                
        if not font_found:
            print("警告: 未找到适合Matplotlib的中文字体")
            
    except ImportError:
        pass
    
    return True

if __name__ == '__main__':
    # 设置异常处理
    setup_exception_handling()
    
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用样式
        app.setStyle('Fusion')
        
        # 加载样式表（使用新的刷新样式函数）
        refresh_style(app)
        
        # 应用自定义QComboBox样式
        def patch_combo_boxes():
            """为所有QComboBox应用自定义样式"""
            try:
                from PyQt5.QtWidgets import QComboBox
                from ui.custom_widgets import HealthyLifeComboBox
                
                # 为所有未来创建的QComboBox应用自定义的Item委托
                from PyQt5.QtWidgets import QProxyStyle
                
                class ComboBoxProxyStyle(QProxyStyle):
                    def drawControl(self, element, option, painter, widget=None):
                        from PyQt5.QtWidgets import QStyle
                        if element == QStyle.CE_ItemViewItem and isinstance(widget, QComboBox):
                            # 修改选项颜色
                            if option.state & QStyle.State_MouseOver:
                                option.palette.setBrush(option.palette.Text, QColor(44, 62, 80))
                            
                        super().drawControl(element, option, painter, widget)
                
                # 应用代理样式
                app.setStyle(ComboBoxProxyStyle(app.style()))
                print("应用了ComboBoxProxyStyle")
                
            except Exception as e:
                print(f"应用QComboBox自定义样式失败: {e}")
        
        # 调用补丁函数
        patch_combo_boxes()
        
        # 设置中文字体支持
        setup_chinese_fonts(app)
        
        # 设置应用图标
        try:
            app.setWindowIcon(QIcon(':/icons/app_icon.png'))
        except Exception as e:
            print(f"设置应用图标失败: {e}")
        
        # 创建数据库连接
        print("正在初始化数据库...")
        db_path = os.path.join(os.path.dirname(__file__), 'database/health_life.db')
        db_manager = DatabaseManager(db_path)
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库结构
        db_manager.initialize()
        print(f"数据库初始化完成: {db_path}")
        
        # 显示登录窗口
        login_window = LoginWindow()
        login_window.db_manager = db_manager  # 注入数据库管理器
        login_window.show()
        
        # 运行应用
        sys.exit(app.exec_())
    except Exception as e:
        print(f"启动应用程序时出错: {str(e)}")
        if QApplication.instance():
            QMessageBox.critical(None, "启动错误", f"启动应用程序时出错:\n{str(e)}")
        sys.exit(1) 