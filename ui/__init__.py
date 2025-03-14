# UI包初始化 

# 添加自定义组件导入
from ui.custom_widgets import HealthyLifeComboBox

# 使用monkey patching替换标准QComboBox为我们的自定义版本
try:
    import PyQt5.QtWidgets
    original_combobox = PyQt5.QtWidgets.QComboBox
    
    # 保存原始类以便可以恢复
    if not hasattr(PyQt5.QtWidgets, '_original_QComboBox'):
        PyQt5.QtWidgets._original_QComboBox = original_combobox
        PyQt5.QtWidgets.QComboBox = HealthyLifeComboBox
        print("成功替换QComboBox为HealthyLifeComboBox")
except Exception as e:
    print(f"替换QComboBox时出错: {e}") 