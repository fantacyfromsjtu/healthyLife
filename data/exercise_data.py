import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_exercise_data():
    """加载运动数据"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'exercises.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"成功加载{len(data)}种运动数据")
        return data
    except Exception as e:
        logger.error(f"加载运动数据时出错: {str(e)}")
        return []

def get_exercise_categories():
    """获取所有运动分类"""
    exercises = load_exercise_data()
    categories = set()
    for exercise in exercises:
        categories.add(exercise.get('category', '未分类'))
    return sorted(list(categories))

def get_exercises_by_category(category=None):
    """按类别获取运动列表"""
    exercises = load_exercise_data()
    if category and category != '全部':
        return [e for e in exercises if e.get('category') == category]
    return exercises

def search_exercises(keyword):
    """搜索运动"""
    if not keyword:
        return load_exercise_data()
    
    exercises = load_exercise_data()
    keyword = keyword.lower()
    return [e for e in exercises if keyword in e.get('name', '').lower() or 
                                 keyword in e.get('description', '').lower() or
                                 keyword in e.get('category', '').lower()]

def calculate_calories(exercise_name, duration_minutes, weight_kg=60):
    """
    计算特定运动消耗的卡路里
    
    参数:
    - exercise_name: 运动名称
    - duration_minutes: 运动持续时间(分钟)
    - weight_kg: 用户体重(kg)，默认60kg
    
    返回:
    - 消耗的卡路里数量
    """
    try:
        # 确保参数类型正确
        if not isinstance(duration_minutes, (int, float)) or duration_minutes <= 0:
            print(f"警告: 无效的运动时长 {duration_minutes}，使用默认值30分钟")
            duration_minutes = 30
            
        if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
            print(f"警告: 无效的体重 {weight_kg}，使用默认值60kg")
            weight_kg = 60
            
        # 加载运动数据
        exercise_data = load_exercise_data()
        
        # 查找指定运动
        exercise = None
        for ex in exercise_data:
            if ex['name'] == exercise_name:
                exercise = ex
                break
        
        # 如果找不到运动，使用平均值
        if not exercise:
            print(f"警告: 找不到运动 '{exercise_name}'，使用默认MET值")
            return int(3.0 * weight_kg * duration_minutes / 60)
        
        # MET值转换为卡路里
        # 卡路里 = MET值 * 体重(kg) * 时间(小时)
        hours = duration_minutes / 60
        calories = exercise.get('met', 3.0) * weight_kg * hours
        
        return int(calories)
    except Exception as e:
        print(f"计算卡路里时出错: {str(e)}")
        # 返回一个合理的默认值
        return int(3.0 * 60 * duration_minutes / 60)  # 使用MET=3作为默认值 