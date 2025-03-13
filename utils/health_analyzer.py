import datetime
import math

class HealthAnalyzer:
    """健康数据分析器，用于生成健康报告和建议"""
    
    def __init__(self, user_profile=None):
        """初始化健康分析器
        
        参数:
            user_profile: 用户资料，包含性别、年龄、身高、体重等信息
        """
        self.user_profile = user_profile or {}
        
    def analyze_weekly_data(self, exercise_data, diet_data, sleep_data):
        """分析每周健康数据，生成报告和建议
        
        参数:
            exercise_data: 运动数据列表 [(日期, 总时长, 消耗卡路里), ...]
            diet_data: 饮食数据列表 [(日期, 总卡路里, 蛋白质, 脂肪, 碳水), ...]
            sleep_data: 睡眠数据列表 [(日期, 平均时长, 平均质量), ...]
            
        返回:
            包含分析结果和建议的字典
        """
        # 对数据进行预处理，确保日期可比较
        exercise_dict = {record[0]: (record[1], record[2]) for record in exercise_data} if exercise_data else {}
        diet_dict = {record[0]: (record[1], record[2], record[3], record[4]) for record in diet_data} if diet_data else {}
        sleep_dict = {record[0]: (record[1], record[2]) for record in sleep_data} if sleep_data else {}
        
        # 获取所有不同的日期
        all_dates = set(exercise_dict.keys()).union(set(diet_dict.keys())).union(set(sleep_dict.keys()))
        all_dates = sorted(all_dates)
        
        # 计算每个方面的统计数据
        exercise_stats = self._analyze_exercise(exercise_dict, all_dates)
        diet_stats = self._analyze_diet(diet_dict, all_dates)
        sleep_stats = self._analyze_sleep(sleep_dict, all_dates)
        
        # 生成健康建议
        exercise_advice = self._generate_exercise_advice(exercise_stats)
        diet_advice = self._generate_diet_advice(diet_stats)
        sleep_advice = self._generate_sleep_advice(sleep_stats)
        
        # 生成综合建议
        overall_advice = self._generate_overall_advice(exercise_stats, diet_stats, sleep_stats)
        
        return {
            "exercise_stats": exercise_stats,
            "diet_stats": diet_stats,
            "sleep_stats": sleep_stats,
            "exercise_advice": exercise_advice,
            "diet_advice": diet_advice,
            "sleep_advice": sleep_advice,
            "overall_advice": overall_advice,
            "dates": list(all_dates)
        }
        
    def _analyze_exercise(self, exercise_dict, all_dates):
        """分析运动数据"""
        total_days = len(all_dates)
        exercise_days = len(exercise_dict)
        total_duration = sum(record[0] for record in exercise_dict.values()) if exercise_dict else 0
        total_calories = sum(record[1] for record in exercise_dict.values()) if exercise_dict else 0
        
        # 计算平均值
        avg_duration_per_day = total_duration / total_days if total_days > 0 else 0
        avg_duration_per_exercise_day = total_duration / exercise_days if exercise_days > 0 else 0
        avg_calories_per_day = total_calories / total_days if total_days > 0 else 0
        
        # 计算达标情况（每周至少150分钟中等强度运动）
        weekly_recommendation = 150  # 分钟
        target_percentage = (total_duration / weekly_recommendation) * 100 if weekly_recommendation > 0 else 0
        
        return {
            "total_days": total_days,
            "exercise_days": exercise_days,
            "exercise_percentage": (exercise_days / total_days * 100) if total_days > 0 else 0,
            "total_duration": total_duration,
            "total_calories": total_calories,
            "avg_duration_per_day": avg_duration_per_day,
            "avg_duration_per_exercise_day": avg_duration_per_exercise_day,
            "avg_calories_per_day": avg_calories_per_day,
            "target_percentage": target_percentage,
            "meets_recommendation": target_percentage >= 100
        }
        
    def _analyze_diet(self, diet_dict, all_dates):
        """分析饮食数据"""
        # 计算总摄入量
        total_calories = sum(record[0] for record in diet_dict.values()) if diet_dict else 0
        total_protein = sum(record[1] for record in diet_dict.values()) if diet_dict else 0
        total_fat = sum(record[2] for record in diet_dict.values()) if diet_dict else 0
        total_carbs = sum(record[3] for record in diet_dict.values()) if diet_dict else 0
        
        # 计算平均摄入量
        total_days = len(all_dates)
        avg_calories_per_day = total_calories / total_days if total_days > 0 else 0
        avg_protein_per_day = total_protein / total_days if total_days > 0 else 0
        avg_fat_per_day = total_fat / total_days if total_days > 0 else 0
        avg_carbs_per_day = total_carbs / total_days if total_days > 0 else 0
        
        # 计算推荐摄入量（根据用户资料）
        recommended_calories = self._calculate_recommended_calories()
        recommended_protein = self._calculate_recommended_protein()
        recommended_fat = self._calculate_recommended_fat(recommended_calories)
        recommended_carbs = self._calculate_recommended_carbs(recommended_calories)
        
        # 计算营养素比例
        total_macros = total_protein * 4 + total_fat * 9 + total_carbs * 4  # 卡路里
        protein_ratio = (total_protein * 4 / total_macros * 100) if total_macros > 0 else 0
        fat_ratio = (total_fat * 9 / total_macros * 100) if total_macros > 0 else 0
        carbs_ratio = (total_carbs * 4 / total_macros * 100) if total_macros > 0 else 0
        
        return {
            "total_days": total_days,
            "diet_days": len(diet_dict),
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_fat": total_fat,
            "total_carbs": total_carbs,
            "avg_calories_per_day": avg_calories_per_day,
            "avg_protein_per_day": avg_protein_per_day,
            "avg_fat_per_day": avg_fat_per_day,
            "avg_carbs_per_day": avg_carbs_per_day,
            "recommended_calories": recommended_calories,
            "recommended_protein": recommended_protein,
            "recommended_fat": recommended_fat,
            "recommended_carbs": recommended_carbs,
            "protein_ratio": protein_ratio,
            "fat_ratio": fat_ratio,
            "carbs_ratio": carbs_ratio,
            "calories_percentage": (avg_calories_per_day / recommended_calories * 100) if recommended_calories > 0 else 0,
            "protein_percentage": (avg_protein_per_day / recommended_protein * 100) if recommended_protein > 0 else 0,
            "fat_percentage": (avg_fat_per_day / recommended_fat * 100) if recommended_fat > 0 else 0,
            "carbs_percentage": (avg_carbs_per_day / recommended_carbs * 100) if recommended_carbs > 0 else 0
        }
        
    def _analyze_sleep(self, sleep_dict, all_dates):
        """分析睡眠数据"""
        # 计算总睡眠时间和质量
        total_duration = sum(record[0] for record in sleep_dict.values()) if sleep_dict else 0
        
        # 计算平均值
        total_days = len(all_dates)
        sleep_days = len(sleep_dict)
        avg_duration_per_day = total_duration / total_days if total_days > 0 else 0
        avg_duration_per_sleep_day = total_duration / sleep_days if sleep_days > 0 else 0
        
        # 计算平均质量
        if sleep_dict:
            quality_values = [record[1] for record in sleep_dict.values() if record[1] is not None]
            avg_quality = sum(quality_values) / len(quality_values) if quality_values else 0
        else:
            avg_quality = 0
            
        # 计算推荐睡眠时间
        recommended_sleep = self._calculate_recommended_sleep()
        
        return {
            "total_days": total_days,
            "sleep_days": sleep_days,
            "sleep_percentage": (sleep_days / total_days * 100) if total_days > 0 else 0,
            "total_duration": total_duration,
            "avg_duration_per_day": avg_duration_per_day,
            "avg_duration_per_sleep_day": avg_duration_per_sleep_day,
            "avg_quality": avg_quality,
            "recommended_sleep": recommended_sleep,
            "sleep_percentage_of_recommended": (avg_duration_per_day / (recommended_sleep * 60) * 100) if recommended_sleep > 0 else 0,
            "meets_recommendation": avg_duration_per_day >= (recommended_sleep * 60) if recommended_sleep > 0 else False
        }
        
    def _generate_exercise_advice(self, stats):
        """生成运动建议"""
        advice = []
        
        # 检查是否达到每周150分钟中等强度运动的推荐
        if stats["meets_recommendation"]:
            advice.append("您本周的运动时间达到了世界卫生组织推荐的每周至少150分钟中等强度运动的标准，请继续保持。")
        else:
            target_percentage = stats["target_percentage"]
            if target_percentage < 30:
                advice.append("您本周的运动时间远低于推荐标准。建议逐步增加运动时间，可以从每天散步15-30分钟开始。")
            elif target_percentage < 60:
                advice.append("您本周的运动时间不足推荐标准的60%。建议增加运动频率，尝试每天安排一些中等强度的活动，如快走、骑车等。")
            else:
                advice.append(f"您本周的运动时间已达到推荐标准的{target_percentage:.1f}%。再稍加努力，即可达到每周150分钟的推荐运动时间。")
        
        # 检查运动频率
        exercise_days = stats["exercise_days"]
        if exercise_days == 0:
            advice.append("本周没有记录任何运动。建议每周至少进行3天的中等强度有氧运动，对心肺功能和整体健康有益。")
        elif exercise_days < 3:
            advice.append(f"本周仅有{exercise_days}天进行了运动。建议将运动分散到每周至少3-5天，有助于保持运动习惯和提高身体素质。")
        
        # 根据平均每天运动时间提供建议
        avg_duration_per_day = stats["avg_duration_per_day"]
        if avg_duration_per_day < 10:
            advice.append("您每天的平均运动时间过短。即使是短时间的运动也比不运动好，但建议每次运动时间至少持续10分钟以上，才能获得明显的健康益处。")
        elif avg_duration_per_day < 30:
            advice.append("您每天的平均运动时间不到30分钟。建议在您的日常生活中融入更多的身体活动，比如步行上下班、爬楼梯等。")
        
        return advice
        
    def _generate_diet_advice(self, stats):
        """生成饮食建议"""
        advice = []
        
        # 检查总热量摄入
        calories_percentage = stats["calories_percentage"]
        if calories_percentage == 0:
            advice.append("本周没有记录任何饮食数据。建议记录您的日常饮食，以便更好地分析和调整饮食结构。")
            return advice
            
        if calories_percentage > 110:
            advice.append(f"您的平均每日热量摄入超过推荐值约{calories_percentage - 100:.1f}%。长期过量摄入热量可能导致体重增加和相关健康问题。")
        elif calories_percentage < 80:
            advice.append(f"您的平均每日热量摄入低于推荐值约{100 - calories_percentage:.1f}%。长期热量摄入不足可能影响身体机能和代谢。")
        else:
            advice.append("您的平均每日热量摄入在推荐范围内，这有助于保持健康体重。")
        
        # 检查蛋白质摄入
        protein_percentage = stats["protein_percentage"]
        protein_ratio = stats["protein_ratio"]
        if protein_percentage < 80:
            advice.append(f"您的蛋白质摄入较低，仅达到推荐量的{protein_percentage:.1f}%。适当增加瘦肉、鱼、豆类、奶制品等富含优质蛋白质的食物。")
        elif protein_ratio < 10:
            advice.append(f"您的饮食中蛋白质占比偏低({protein_ratio:.1f}%)。建议增加蛋白质的摄入，它对维持肌肉量和提高饱腹感很重要。")
        elif protein_ratio > 35:
            advice.append(f"您的饮食中蛋白质占比较高({protein_ratio:.1f}%)。虽然蛋白质重要，但过高比例可能导致其他营养素摄入不足。")
        
        # 检查脂肪摄入
        fat_ratio = stats["fat_ratio"]
        if fat_ratio < 15:
            advice.append(f"您的脂肪摄入比例偏低({fat_ratio:.1f}%)。健康的脂肪对吸收脂溶性维生素和维持内分泌功能很重要。")
        elif fat_ratio > 40:
            advice.append(f"您的脂肪摄入比例偏高({fat_ratio:.1f}%)。建议减少饱和脂肪和反式脂肪的摄入，多选择不饱和脂肪如橄榄油、坚果类等。")
        
        # 检查碳水化合物摄入
        carbs_ratio = stats["carbs_ratio"]
        if carbs_ratio < 40:
            advice.append(f"您的碳水化合物摄入比例较低({carbs_ratio:.1f}%)。适量的复合碳水化合物如全谷物、根茎类蔬菜等可提供持久能量。")
        elif carbs_ratio > 70:
            advice.append(f"您的碳水化合物摄入比例偏高({carbs_ratio:.1f}%)。建议减少精制碳水化合物如白面包、甜点等，多选择复合碳水化合物。")
        
        # 综合营养素平衡建议
        advice.append("均衡的饮食应包含适量的蛋白质(10-35%)、脂肪(20-35%)和碳水化合物(45-65%)，同时确保摄入足够的维生素、矿物质和膳食纤维。")
        
        return advice
        
    def _generate_sleep_advice(self, stats):
        """生成睡眠建议"""
        advice = []
        
        sleep_days = stats["sleep_days"]
        if sleep_days == 0:
            advice.append("本周没有记录任何睡眠数据。建议每晚保持规律的睡眠习惯，这对身心健康至关重要。")
            return advice
            
        # 检查睡眠时长
        sleep_percentage = stats["sleep_percentage_of_recommended"]
        avg_duration_per_day = stats["avg_duration_per_day"]
        
        if sleep_percentage < 80:
            advice.append(f"您的平均睡眠时间不足，仅为推荐时间的{sleep_percentage:.1f}%。长期睡眠不足可能影响认知功能、情绪和免疫系统。")
            advice.append(f"成年人通常需要7-9小时的睡眠，而您的平均睡眠时间约为{avg_duration_per_day / 60:.1f}小时。")
        elif sleep_percentage > 120:
            advice.append(f"您的平均睡眠时间超过推荐值。过长的睡眠时间有时也可能与某些健康问题相关，建议保持规律的睡眠习惯。")
        else:
            advice.append("您的睡眠时间在健康范围内，这有助于身体恢复和维持认知功能。")
        
        # 检查睡眠质量
        avg_quality = stats["avg_quality"]
        if avg_quality < 2.5:
            advice.append("您的睡眠质量评分较低。可以尝试以下方法改善睡眠质量：保持规律的作息时间、睡前避免使用电子设备、创造舒适的睡眠环境等。")
        elif avg_quality < 3.5:
            advice.append("您的睡眠质量评分中等。可以通过改善睡眠环境（如调整室温、减少噪音）、睡前放松（如热水浴、轻度伸展）等方式提高睡眠质量。")
        else:
            advice.append("您的睡眠质量评分良好。继续保持健康的睡眠习惯，有助于维持整体健康状态。")
        
        # 睡眠规律性建议
        if sleep_days < stats["total_days"] * 0.8:
            advice.append(f"本周仅记录了{sleep_days}天的睡眠数据。保持规律的睡眠时间对健康十分重要，包括周末在内。")
        
        return advice
        
    def _generate_overall_advice(self, exercise_stats, diet_stats, sleep_stats):
        """生成综合健康建议"""
        advice = []
        
        # 基于三个方面的综合分析
        exercise_recommendation_met = exercise_stats["meets_recommendation"]
        has_diet_data = diet_stats["diet_days"] > 0
        sleep_recommendation_met = sleep_stats["meets_recommendation"]
        
        # 综合健康状况评估
        if exercise_recommendation_met and sleep_recommendation_met and has_diet_data:
            advice.append("综合来看，您在运动、饮食和睡眠三个方面都表现良好。这种平衡的生活方式有助于保持长期健康。")
        else:
            advice.append("健康的生活方式需要在运动、饮食和睡眠三个方面取得平衡。根据您的数据，我们建议您重点关注以下方面：")
            
            if not exercise_recommendation_met:
                advice.append("- 增加身体活动：设定每周运动目标，逐步增加运动频率和时长，选择您喜欢的运动方式。")
                
            if not has_diet_data:
                advice.append("- 记录饮食习惯：了解自己的饮食模式是改善营养的第一步。")
            elif diet_stats["calories_percentage"] > 110:
                advice.append("- 调整饮食结构：控制总热量摄入，增加蔬果摄入，减少高糖、高脂食品的比例。")
                
            if not sleep_recommendation_met:
                advice.append("- 改善睡眠习惯：保持规律的作息时间，创造舒适的睡眠环境，睡前避免刺激性活动。")
        
        # 坚持记录的重要性
        missing_data = []
        if exercise_stats["exercise_days"] < exercise_stats["total_days"]:
            missing_data.append("运动")
        if diet_stats["diet_days"] < diet_stats["total_days"]:
            missing_data.append("饮食")
        if sleep_stats["sleep_days"] < sleep_stats["total_days"]:
            missing_data.append("睡眠")
            
        if missing_data:
            advice.append(f"我们注意到您在{', '.join(missing_data)}方面的记录不完整。坚持记录有助于更准确地分析和改进您的健康状况。")
        
        # 长期健康目标
        advice.append("建议设定长期健康目标：适度的身体活动、均衡的饮食结构、充足的睡眠质量是维持健康的基础。随着时间的推移，这些小习惯将累积成显著的健康益处。")
        
        return advice
    
    def _calculate_recommended_calories(self):
        """计算推荐的每日卡路里摄入量"""
        # 默认值
        default_calories = 2000
        
        # 如果没有用户资料，返回默认值
        if not self.user_profile:
            return default_calories
            
        try:
            # 获取用户信息
            gender = self.user_profile.get("gender", "")
            age = self.user_profile.get("age", 25)
            height = self.user_profile.get("height", 170)  # 厘米
            weight = self.user_profile.get("weight", 65)   # 公斤
            
            # 使用Harris-Benedict公式计算基础代谢率(BMR)
            if gender.lower() in ["男", "male", "m"]:
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:  # 女性
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
                
            # 假设中等活动水平（PAL=1.55）
            return int(bmr * 1.55)
        except:
            return default_calories
    
    def _calculate_recommended_protein(self):
        """计算推荐的每日蛋白质摄入量(克)"""
        # 默认值
        default_protein = 65  # 克
        
        # 如果没有用户资料，返回默认值
        if not self.user_profile:
            return default_protein
            
        try:
            # 获取用户体重
            weight = self.user_profile.get("weight", 65)  # 公斤
            
            # 一般建议每公斤体重1.2-2.0克蛋白质
            # 使用中间值1.6
            return int(weight * 1.6)
        except:
            return default_protein
    
    def _calculate_recommended_fat(self, calories):
        """计算推荐的每日脂肪摄入量(克)"""
        # 假设脂肪提供总热量的30%
        # 每克脂肪提供9卡路里
        return int((calories * 0.3) / 9)
    
    def _calculate_recommended_carbs(self, calories):
        """计算推荐的每日碳水化合物摄入量(克)"""
        # 假设碳水化合物提供总热量的55%
        # 每克碳水化合物提供4卡路里
        return int((calories * 0.55) / 4)
    
    def _calculate_recommended_sleep(self):
        """计算推荐的每日睡眠时间(小时)"""
        # 默认值
        default_sleep = 8  # 小时
        
        # 如果没有用户资料，返回默认值
        if not self.user_profile:
            return default_sleep
            
        try:
            # 根据年龄计算推荐睡眠时间
            age = self.user_profile.get("age", 25)
            
            if age < 18:
                return 9  # 青少年8-10小时
            elif age < 65:
                return 8  # 成年人7-9小时
            else:
                return 7.5  # 老年人7-8小时
        except:
            return default_sleep 