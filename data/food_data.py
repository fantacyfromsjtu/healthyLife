# 食物数据模块 - 提供食物数据访问辅助功能
import json
import os
import sys

# 食物数据缓存
_food_data_cache = None

def load_food_data():
    """从JSON文件加载食物数据"""
    global _food_data_cache
    
    # 如果已经加载过数据，直接返回缓存
    if _food_data_cache is not None:
        return _food_data_cache
    
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'foods.json'),  # 相对于当前文件
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'foods.json'),  # 相对于项目根目录
        os.path.join(os.getcwd(), 'data', 'foods.json'),  # 相对于当前工作目录
    ]
    
    # 打印工作目录和模块路径，帮助调试
    print(f"当前工作目录: {os.getcwd()}")
    print(f"当前模块路径: {__file__}")
    print(f"Python路径: {sys.path}")
    
    # 尝试所有可能的路径
    json_path = None
    for path in possible_paths:
        print(f"尝试加载食物数据: {path}")
        if os.path.exists(path):
            json_path = path
            print(f"找到食物数据文件: {path}")
            break
    
    if json_path:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                _food_data_cache = json.load(f)
                print(f"成功加载食物数据: {len(_food_data_cache)} 条记录")
                # 打印前5条记录作为示例
                if _food_data_cache and len(_food_data_cache) > 0:
                    print("示例食物数据:")
                    for i, food in enumerate(_food_data_cache[:5]):
                        print(f"  {i+1}. {food}")
                return _food_data_cache
        except Exception as e:
            print(f"加载食物数据出错: {str(e)}")
            return []
    else:
        print("未找到食物数据文件，创建示例数据...")
        # 如果找不到文件，创建一些示例数据并保存
        example_foods = [
            {"name": "米饭", "category": "主食", "calories": 116, "protein": 2.6, "fat": 0.3, "carbs": 25.6, "fiber": 0.3, "unit": "碗", "standard_weight": 100},
            {"name": "面条", "category": "主食", "calories": 110, "protein": 3.3, "fat": 0.5, "carbs": 22.8, "fiber": 0.9, "unit": "碗", "standard_weight": 100},
            {"name": "馒头", "category": "主食", "calories": 223, "protein": 6.6, "fat": 1.0, "carbs": 47.7, "fiber": 1.3, "unit": "个", "standard_weight": 100},
            {"name": "鸡蛋", "category": "蛋类", "calories": 144, "protein": 12.8, "fat": 10.3, "carbs": 0.7, "fiber": 0, "unit": "个", "standard_weight": 50},
            {"name": "猪肉（瘦）", "category": "肉类", "calories": 143, "protein": 21.2, "fat": 6.3, "carbs": 0, "fiber": 0, "unit": "份", "standard_weight": 100},
            {"name": "牛肉", "category": "肉类", "calories": 126, "protein": 20.7, "fat": 4.6, "carbs": 0, "fiber": 0, "unit": "份", "standard_weight": 100},
            {"name": "鸡胸肉", "category": "肉类", "calories": 120, "protein": 22.8, "fat": 2.8, "carbs": 0, "fiber": 0, "unit": "份", "standard_weight": 100},
            {"name": "豆腐", "category": "豆制品", "calories": 81, "protein": 8.1, "fat": 4.6, "carbs": 1.9, "fiber": 0.3, "unit": "块", "standard_weight": 100},
            {"name": "西红柿", "category": "蔬菜", "calories": 15, "protein": 0.9, "fat": 0.2, "carbs": 3.3, "fiber": 1.2, "unit": "个", "standard_weight": 100},
            {"name": "黄瓜", "category": "蔬菜", "calories": 16, "protein": 0.7, "fat": 0.1, "carbs": 3.6, "fiber": 0.5, "unit": "根", "standard_weight": 100},
            {"name": "胡萝卜", "category": "蔬菜", "calories": 33, "protein": 0.9, "fat": 0.2, "carbs": 7.6, "fiber": 2.8, "unit": "根", "standard_weight": 100},
            {"name": "白菜", "category": "蔬菜", "calories": 12, "protein": 1.2, "fat": 0.2, "carbs": 2.2, "fiber": 1.3, "unit": "份", "standard_weight": 100},
            {"name": "苹果", "category": "水果", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 13.7, "fiber": 2.4, "unit": "个", "standard_weight": 150},
            {"name": "香蕉", "category": "水果", "calories": 93, "protein": 1.1, "fat": 0.3, "carbs": 23.2, "fiber": 2.4, "unit": "根", "standard_weight": 120},
            {"name": "橙子", "category": "水果", "calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 11.8, "fiber": 2.4, "unit": "个", "standard_weight": 150},
            {"name": "牛奶", "category": "乳制品", "calories": 42, "protein": 3.3, "fat": 1.6, "carbs": 4.9, "fiber": 0, "unit": "杯", "standard_weight": 100},
            {"name": "酸奶", "category": "乳制品", "calories": 72, "protein": 3.3, "fat": 3.1, "carbs": 5.4, "fiber": 0, "unit": "杯", "standard_weight": 100},
            {"name": "奶酪", "category": "乳制品", "calories": 348, "protein": 21.4, "fat": 28.7, "carbs": 2.1, "fiber": 0, "unit": "份", "standard_weight": 30},
            {"name": "坚果", "category": "零食", "calories": 607, "protein": 18.2, "fat": 53.7, "carbs": 19.2, "fiber": 8.6, "unit": "份", "standard_weight": 30}
        ]
        
        # 保存示例数据
        try:
            new_file_path = os.path.join(os.path.dirname(__file__), 'foods.json')
            with open(new_file_path, 'w', encoding='utf-8') as f:
                json.dump(example_foods, f, ensure_ascii=False, indent=4)
                print(f"已创建示例食物数据并保存至: {new_file_path}")
                _food_data_cache = example_foods
                return example_foods
        except Exception as e:
            print(f"创建示例食物数据失败: {str(e)}")
            # 如果无法保存到文件，至少返回内存中的示例数据
            _food_data_cache = example_foods
            return example_foods

def get_food_categories():
    """获取所有食物分类"""
    foods = load_food_data()
    categories = set()
    for food in foods:
        if 'category' in food:
            categories.add(food['category'])
    return sorted(list(categories))

def get_foods_by_category(category=None):
    """获取特定分类的食物，如果未指定分类则返回所有食物"""
    foods = load_food_data()
    if category:
        return [food for food in foods if food.get('category') == category]
    return foods

def search_foods(keyword):
    """搜索食物"""
    foods = load_food_data()
    return [food for food in foods if keyword.lower() in food.get('name', '').lower()] 