from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QApplication, QStyle
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPalette, QColor, QPainter, QFont, QPolygon

class HealthyLifeComboBox(QComboBox):
    """自定义下拉框，确保悬停和选中项的文字颜色可见"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 应用自定义委托
        self.setItemDelegate(HealthyLifeItemDelegate(self))
        
        # 设置样式
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                padding-right: 20px; /* 为下拉箭头留出空间 */
                background-color: white;
                min-height: 30px;
                font-size: 12pt;
            }
            
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                border-radius: 0;
                background-color: white;
                selection-background-color: #3498db;
                color: #2c3e50;
                outline: 0px;
            }
        """)
        
    def showPopup(self):
        """显示下拉菜单前应用样式"""
        super().showPopup()
    
    def paintEvent(self, event):
        """重写绘制事件，手动绘制下拉箭头"""
        super().paintEvent(event)
        
        # 绘制下拉箭头
        painter = QPainter(self)
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建箭头多边形
        arrow_size = 8
        x = self.width() - arrow_size - 10  # 距离右边缘10像素
        y = self.height() // 2
        
        arrow = QPolygon()
        arrow.append(QPoint(x, y - arrow_size // 2))
        arrow.append(QPoint(x + arrow_size, y - arrow_size // 2))
        arrow.append(QPoint(x + arrow_size // 2, y + arrow_size // 2))
        
        # 设置画笔颜色
        painter.setPen(Qt.NoPen)
        
        # 设置画刷颜色
        if self.isEnabled():
            painter.setBrush(QColor(44, 62, 80))  # 深色
        else:
            painter.setBrush(QColor(189, 195, 199))  # 浅灰色
        
        # 绘制箭头
        painter.drawPolygon(arrow)
        
        # 结束绘制
        painter.end()
        
class HealthyLifeItemDelegate(QStyledItemDelegate):
    """自定义项目委托，用于控制QComboBox下拉菜单项的绘制"""
    
    def paint(self, painter, option, index):
        """重写绘制方法，确保文字始终可见"""
        # 获取项目文本和字体
        text = index.data(Qt.DisplayRole)
        font = QFont(option.font)
        
        # 清除原有背景
        painter.save()
        painter.fillRect(option.rect, QColor(255, 255, 255))
        
        # 如果悬停在项目上 - 使用正确的QStyle枚举值
        if option.state & QStyle.State_MouseOver:
            # 设置浅蓝色背景
            painter.fillRect(option.rect, QColor(232, 244, 252))  # 浅蓝色
            painter.setPen(QColor(44, 62, 80))  # 深色文字
        
        # 如果项目被选中
        elif option.state & QStyle.State_Selected:
            # 设置蓝色背景
            painter.fillRect(option.rect, QColor(52, 152, 219))  # 蓝色
            painter.setPen(QColor(255, 255, 255))  # 白色文字
        
        # 正常状态
        else:
            painter.setPen(QColor(44, 62, 80))  # 正常文字色
        
        # 设置字体
        painter.setFont(font)
        
        # 绘制文本，添加适当的边距
        text_rect = QRect(option.rect)
        text_rect.setLeft(text_rect.left() + 5)  # 左边距
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)
        
        painter.restore() 