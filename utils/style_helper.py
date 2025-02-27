import os
from PyQt5.QtCore import QFile, QTextStream

def load_stylesheet(file_path):
    """加载样式表文件"""
    qss_file = QFile(file_path)
    if qss_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(qss_file)
        stylesheet = stream.readAll()
        qss_file.close()
        return stylesheet
    return ""

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