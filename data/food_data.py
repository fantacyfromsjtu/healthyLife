# 食物数据模块 - 提供食物数据访问辅助功能
import json
import os

# 食物数据缓存
_food_data_cache = None

def load_food_data():
    """从JSON文件加载食物数据"""
    global _food_data_cache
    
    # 如果已经加载过数据，直接返回缓存
    if _food_data_cache is not None:
        return _food_data_cache
    
    # 获取食物数据文件路径
    json_path = os.path.join(os.path.dirname(__file__), 'foods.json')
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            _food_data_cache = json.load(f)
        return _food_data_cache
    else:
        print("食物数据文件不存在：", json_path)
        return []

def get_food_categories():
    """获取所有食物分类"""
    foods = load_food_data()
    categories = set()
    for food in foods:
        categories.add(food['category'])
    return sorted(list(categories))

def get_foods_by_category(category):
    """获取特定分类的食物"""
    foods = load_food_data()
    return [food for food in foods if food['category'] == category]

def search_foods(keyword):
    """搜索食物"""
    foods = load_food_data()
    return [food for food in foods if keyword.lower() in food['name'].lower()] 