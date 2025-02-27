import sqlite3
import os

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
        
        # 饮食记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS diet_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            meal_type TEXT,  -- 早餐/午餐/晚餐/零食
            food_name TEXT,
            calories FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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