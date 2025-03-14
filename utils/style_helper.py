import os
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QStyle, QProxyStyle, QCommonStyle, QStyleFactory, QApplication

class HealthyLifeProxyStyle(QProxyStyle):
    """自定义代理样式类，解决QComboBox下拉列表在悬停时文字被覆盖的问题"""
    
    def __init__(self, style=None):
        """初始化代理样式"""
        if style is None:
            style = QStyleFactory.create("Fusion")
        super().__init__(style)
    
    def drawControl(self, element, option, painter, widget=None):
        """重写绘制控件方法，特别处理QComboBox的下拉项"""
        from PyQt5.QtWidgets import QComboBox, QStyle
        
        # 如果是QComboBox下拉菜单项并且处于悬停状态，使用自定义绘制样式
        if element == QStyle.CE_ItemViewItem and isinstance(widget, QComboBox):
            # 使用修改后的选项进行绘制，确保文字颜色可见
            if option.state & QStyle.State_MouseOver:
                from PyQt5.QtGui import QColor
                from PyQt5.QtCore import Qt
                
                # 创建选项的副本
                option_copy = option
                # 设置项目的文本颜色为可见色
                option_copy.palette.setColor(option.palette.Text, QColor(44, 62, 80))  # 深蓝灰色文字
                option_copy.palette.setColor(option.palette.HighlightedText, QColor(44, 62, 80))
                
                # 用修改后的选项绘制
                super().drawControl(element, option_copy, painter, widget)
                return
        
        # 其他情况正常绘制
        super().drawControl(element, option, painter, widget)

def load_stylesheet(file_path):
    """加载样式表文件"""
    qss_file = QFile(file_path)
    if qss_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(qss_file)
        stylesheet = stream.readAll()
        qss_file.close()
        return stylesheet
    return ""

def refresh_style(app, style_path="resources/styles/style.qss"):
    """刷新应用样式"""
    try:
        style_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), style_path)
        print(f"正在重新加载样式: {style_file}")
        with open(style_file, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
        
        # 应用自定义代理样式
        custom_style = HealthyLifeProxyStyle()
        app.setStyle(custom_style)
        
        # 直接应用关键的QComboBox样式修复
        apply_combo_box_fix(app)
        return True
    except Exception as e:
        print(f"刷新样式失败: {e}")
        return False

def apply_combo_box_fix(app):
    """直接应用下拉框样式修复"""
    combo_style = """
    QComboBox QAbstractItemView {
        border: 1px solid #bdc3c7;
        border-radius: 0;
        background-color: white;
        selection-background-color: #ecf0f1;
        font-size: 12pt;
        color: #2c3e50;
        outline: 0px;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox QAbstractItemView::item {
        min-height: 25px;
        padding: 5px;
        border: none;
    }
    
    QComboBox QAbstractItemView::item:hover {
        background-color: #e8f4fc;
        color: #2c3e50;
        font-weight: normal;
    }
    
    QComboBox QAbstractItemView::item:selected {
        background-color: #3498db;
        color: white;
    }
    """
    
    # 附加样式到现有样式表
    current_style = app.styleSheet()
    app.setStyleSheet(current_style + combo_style)
    print("已应用下拉框样式修复")

def set_dark_mode(app):
    """设置应用为深色模式"""
    app.setStyleSheet("""
    QWidget {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    
    QPushButton {
        background-color: #34495e;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #4a6984;
    }
    
    QLineEdit {
        background-color: #34495e;
        color: white;
        border: 1px solid #7f8c8d;
        border-radius: 4px;
        padding: 8px;
    }
    
    QComboBox {
        background-color: #34495e;
        color: white;
        border: 1px solid #7f8c8d;
        border-radius: 4px;
        padding: 6px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2c3e50;
        border: 1px solid #7f8c8d;
        color: white;
        outline: 0px;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox QAbstractItemView::item {
        min-height: 25px;
        padding: 5px;
        border: none;
    }
    
    QComboBox QAbstractItemView::item:selected, 
    QComboBox QAbstractItemView::item:hover {
        background-color: #3e5871;
        color: white;
        font-weight: normal;
    }
    
    QComboBox QAbstractItemView::item:selected {
        background-color: #3498db;
        color: white;
    }
    
    QTabWidget::pane {
        border: 1px solid #7f8c8d;
    }
    
    QTabBar::tab {
        background-color: #34495e;
        color: #bdc3c7;
        padding: 8px 12px;
    }
    
    QTabBar::tab:selected {
        background-color: #3498db;
        color: white;
    }
    
    QCalendarWidget {
        background-color: #34495e;
    }
    
    QCalendarWidget QTableView {
        alternate-background-color: #40556e;
    }
    """) 