import sqlite3
import os
import time
import json

class DatabaseManager:
    def __init__(self, db_path="healthylife.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize()
        
    def initialize(self):
        """初始化数据库连接并创建必要的表"""
        self.connect()
        self.create_tables()
        
    def connect(self):
        """创建数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """创建所需的数据表"""
        # 用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            height FLOAT,
            weight FLOAT,
            diet_habit TEXT,
            exercise_habit TEXT,
            sleep_habit TEXT,
            register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 运动记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            exercise_type TEXT,
            duration INTEGER,  -- 分钟
            calories_burned FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 睡眠记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sleep_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            sleep_time TEXT,
            wake_time TEXT,
            sleep_quality TEXT,  -- 好/一般/差
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 计划提醒表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            time TEXT,
            reminder_type TEXT,  -- 锻炼/吃饭/睡觉
            content TEXT,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 食物表 - 存储常见食物及其营养信息
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            calories FLOAT,  -- 每100克的热量(千卡)
            protein FLOAT,   -- 每100克的蛋白质(克)
            fat FLOAT,       -- 每100克的脂肪(克)
            carbs FLOAT,     -- 每100克的碳水化合物(克)
            fiber FLOAT,     -- 每100克的膳食纤维(克)
            unit TEXT,       -- 计量单位(克、份、杯等)
            standard_weight FLOAT  -- 标准单位重量(克)
        )
        ''')
        
        # 用户饮食记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS diet_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_id INTEGER,
            food_name TEXT,  -- 冗余存储，方便查询
            amount FLOAT,    -- 食用量
            unit TEXT,       -- 单位
            meal_type TEXT,  -- 早餐/午餐/晚餐/加餐
            record_date DATE,
            record_time TIME,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
        ''')
        
        self.conn.commit()
        
    def add_user(self, username, password):
        """添加新用户"""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
            
    def verify_user(self, username, password):
        """验证用户登录"""
        self.cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_profile(self, user_id):
        """获取用户个人资料"""
        try:
            self.cursor.execute(
                "SELECT gender, age, height, weight, diet_habit, exercise_habit, sleep_habit FROM users WHERE id = ?",
                (user_id,)
            )
            result = self.cursor.fetchone()
            if result:
                return {
                    'gender': result[0],
                    'age': result[1],
                    'height': result[2],
                    'weight': result[3],
                    'diet_habit': result[4],
                    'exercise_habit': result[5],
                    'sleep_habit': result[6]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取用户资料错误: {e}")
            return None

    def update_user_profile(self, user_id, gender, age, height, weight, diet_habit, exercise_habit, sleep_habit):
        """更新用户个人资料"""
        try:
            self.cursor.execute(
                """
                UPDATE users 
                SET gender = ?, age = ?, height = ?, weight = ?, 
                    diet_habit = ?, exercise_habit = ?, sleep_habit = ?
                WHERE id = ?
                """,
                (gender, age, height, weight, diet_habit, exercise_habit, sleep_habit, user_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新用户资料错误: {e}")
            return False

    def is_profile_complete(self, user_id):
        """检查用户资料是否完整"""
        try:
            self.cursor.execute(
                "SELECT gender, age, height, weight FROM users WHERE id = ?",
                (user_id,)
            )
            result = self.cursor.fetchone()
            # 如果任何一项基本信息为空，则认为资料不完整
            if not result or None in result or "" in result or 0 in (result[1], result[2], result[3]):
                return False
            return True
        except sqlite3.Error as e:
            print(f"检查用户资料完整性错误: {e}")
            return False

    def add_food(self, name, category, calories, protein, fat, carbs, fiber, unit, standard_weight):
        """添加食物到数据库"""
        try:
            self.cursor.execute(
                """
                INSERT INTO foods (name, category, calories, protein, fat, carbs, fiber, unit, standard_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, category, calories, protein, fat, carbs, fiber, unit, standard_weight)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加食物错误: {e}")
            return None

    def get_foods_by_category(self, category=None):
        """获取特定类别或所有食物"""
        try:
            if category:
                self.cursor.execute("SELECT * FROM foods WHERE category = ? ORDER BY name", (category,))
            else:
                self.cursor.execute("SELECT * FROM foods ORDER BY category, name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取食物错误: {e}")
            return []

    def search_foods(self, keyword):
        """搜索食物"""
        try:
            self.cursor.execute(
                "SELECT * FROM foods WHERE name LIKE ? ORDER BY name",
                (f"%{keyword}%",)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"搜索食物错误: {e}")
            return []

    def add_diet_record(self, user_id, food_id, food_name, amount, unit, meal_type, record_date, record_time, notes=""):
        """添加饮食记录"""
        try:
            self.cursor.execute(
                """
                INSERT INTO diet_records (user_id, food_id, food_name, amount, unit, meal_type, record_date, record_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, food_id, food_name, amount, unit, meal_type, record_date, record_time, notes)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加饮食记录错误: {e}")
            return None

    def get_diet_records_by_date(self, user_id, date):
        """获取用户特定日期的饮食记录"""
        try:
            self.cursor.execute(
                """
                SELECT dr.*, f.calories, f.protein, f.fat, f.carbs, f.fiber, f.standard_weight
                FROM diet_records dr
                LEFT JOIN foods f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date = ?
                ORDER BY dr.record_time
                """,
                (user_id, date)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取饮食记录错误: {e}")
            return []

    def get_diet_records_by_date_and_meal(self, user_id, date, meal_type):
        """获取用户特定日期和餐食类型的饮食记录"""
        try:
            self.cursor.execute(
                """
                SELECT dr.*, f.calories, f.protein, f.fat, f.carbs, f.fiber, f.standard_weight
                FROM diet_records dr
                LEFT JOIN foods f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date = ? AND dr.meal_type = ?
                ORDER BY dr.record_time
                """,
                (user_id, date, meal_type)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取饮食记录错误: {e}")
            return []

    def update_diet_record(self, record_id, amount, unit, meal_type, record_date, record_time, notes):
        """更新饮食记录"""
        try:
            self.cursor.execute(
                """
                UPDATE diet_records
                SET amount = ?, unit = ?, meal_type = ?, record_date = ?, record_time = ?, notes = ?
                WHERE id = ?
                """,
                (amount, unit, meal_type, record_date, record_time, notes, record_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新饮食记录错误: {e}")
            return False

    def delete_diet_record(self, record_id):
        """删除饮食记录"""
        try:
            self.cursor.execute("DELETE FROM diet_records WHERE id = ?", (record_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"删除饮食记录错误: {e}")
            return False

    def initialize_food_database(self):
        """从JSON文件加载食物数据并初始化数据库"""
        # 检查食物表是否为空
        self.cursor.execute("SELECT COUNT(*) FROM foods")
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            return  # 已经有数据，不需要初始化
        
        # 读取食物数据JSON文件
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'foods.json')
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    foods = json.load(f)
                    
                # 批量插入以提高性能
                for food in foods:
                    self.add_food(
                        food['name'],
                        food['category'],
                        food['calories'],
                        food['protein'],
                        food['fat'],
                        food['carbs'],
                        food['fiber'],
                        food['unit'],
                        food['standard_weight']
                    )
                
                print(f"从JSON文件导入了{len(foods)}种食物")
            except json.JSONDecodeError as e:
                print(f"JSON格式错误: {e}")
            except Exception as e:
                print(f"导入食物数据时出错: {e}")
        else:
            print("未找到食物数据文件，路径:", json_path) 