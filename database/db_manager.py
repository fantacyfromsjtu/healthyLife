import sqlite3
import os
import time
import json
import functools
import logging
from utils.verification import hash_password, verify_password
import traceback

# 数据库操作重试装饰器
def db_retry(max_attempts=3, delay=0.5):
    """
    数据库操作重试装饰器，处理锁定和超时情况
    
    参数:
        max_attempts: 最大尝试次数
        delay: 重试前的延迟(秒)，每次重试后加倍
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_error = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    # 只有当错误是数据库锁定时才重试
                    if "database is locked" in str(e) or "timeout" in str(e):
                        attempt += 1
                        last_error = e
                        if attempt < max_attempts:
                            logging.warning(f"数据库锁定，{current_delay}秒后重试(尝试 {attempt}/{max_attempts})")
                            time.sleep(current_delay)
                            current_delay *= 2  # 指数级延迟
                        continue
                    raise  # 其他操作错误直接抛出
                except Exception as e:
                    # 非数据库锁定错误直接抛出
                    raise
            
            # 如果达到最大尝试次数仍失败
            raise last_error
        return wrapper
    return decorator

class DatabaseManager:

    def __init__(self, db_path="database/health_life.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize()

    def initialize(self):
        """初始化数据库，包括连接数据库、创建表结构、初始化基础数据和升级密码"""
        try:
            # 确保连接到数据库
            if not hasattr(self, 'conn') or self.conn is None:
                self.connect()
                
            print("开始初始化数据库...")
            
            # 创建表结构
            self.create_tables()
            print("数据库表结构初始化完成")
            
            # 初始化食物数据库
            food_init_result = self.initialize_food_database()
            if food_init_result:
                print("食物数据库初始化成功")
            else:
                print("食物数据库初始化失败或已经初始化过")
            
            # 升级老用户的明文密码到哈希密码
            self.upgrade_passwords()
            
            print("数据库初始化完成")
            return True
        except Exception as e:
            print(f"数据库初始化过程出错: {e}")
            traceback.print_exc()
            return False

    def connect(self):
        """创建数据库连接"""
        self.conn = sqlite3.connect(self.db_path, timeout=30.0)  # 增加超时时间
        # 启用WAL模式，提高并发性能
        self.conn.execute("PRAGMA journal_mode=WAL")
        # 启用外键约束
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.cursor = self.conn.cursor()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                # 确保提交所有未决事务
                self.conn.commit()
            except sqlite3.Error:
                # 如果提交失败，尝试回滚
                try:
                    self.conn.rollback()
                except:
                    pass
            finally:
                self.conn.close()
                self.conn = None
                self.cursor = None

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭连接"""
        self.close()

    def create_tables(self):
        """创建数据库表"""
        try:
            # 检查users表是否存在
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = self.cursor.fetchone()
            
            # 创建用户表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                diet_habit TEXT,
                exercise_habit TEXT,
                sleep_habit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 如果表已存在但可能缺少列，尝试添加这些列
            if table_exists:
                # 获取现有列
                self.cursor.execute("PRAGMA table_info(users)")
                existing_columns = [row[1] for row in self.cursor.fetchall()]
                print(f"现有users表列: {existing_columns}")
                
                # 检查并添加缺失的列
                for column, type_ in [
                    ("salt", "TEXT"),
                    ("gender", "TEXT"),
                    ("age", "INTEGER"),
                    ("height", "REAL"),
                    ("weight", "REAL"),
                    ("diet_habit", "TEXT"),
                    ("exercise_habit", "TEXT"),
                    ("sleep_habit", "TEXT")
                ]:
                    if column not in existing_columns:
                        try:
                            alter_sql = f"ALTER TABLE users ADD COLUMN {column} {type_}"
                            print(f"添加缺失列: {alter_sql}")
                            self.cursor.execute(alter_sql)
                        except Exception as e:
                            print(f"添加列 {column} 时出错: {e}")
            
            # 创建用户资料表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                gender TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                diet_habit TEXT,
                exercise_habit TEXT,
                sleep_habit TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')

            # 创建食物数据表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL,
                fiber REAL,
                unit TEXT,
                standard_weight REAL DEFAULT 100
            )
            ''')

            # 创建饮食记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_id INTEGER,
                food_name TEXT,
                amount REAL,
                unit TEXT,
                meal_type TEXT,
                record_date DATE,
                record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL
            )
            ''')

            # 创建运动记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                category TEXT,
                duration INTEGER,  -- 以分钟为单位
                intensity TEXT,    -- 低/中/高
                calories_burned INTEGER,
                record_date DATE,
                record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')

            # 创建提醒表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reminder_date DATE,
                reminder_time TIME,
                reminder_type TEXT,
                content TEXT,
                is_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # 创建睡眠记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sleep_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sleep_date DATE,
                sleep_time TIME,
                wake_date DATE,
                wake_time TIME,
                duration INTEGER,  -- 以分钟为单位
                quality INTEGER,   -- 0-5，0表示未评价，1-5表示从很差到优秀
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')

            self.conn.commit()
            print("数据库表创建/更新成功")
        except Exception as e:
            print(f"创建表错误: {e}")

    @db_retry()
    def add_user(self, username, password):
        """添加新用户"""
        try:
            # 对密码进行哈希处理
            hashed_password, salt = hash_password(password)
            
            self.cursor.execute(
                "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                (username, hashed_password, salt)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def verify_user(self, username, password):
        """验证用户登录"""
        try:
            # 获取用户的哈希密码和盐值
            self.cursor.execute(
                "SELECT id, password, salt FROM users WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return None
                
            user_id, stored_hash, salt = result
            
            # 兼容老密码（明文存储）
            if salt is None or salt == "":
                # 旧版验证方式 - 直接比较密码
                self.cursor.execute(
                    "SELECT id FROM users WHERE username = ? AND password = ?",
                    (username, password)
                )
                old_result = self.cursor.fetchone()
                
                if old_result:
                    # 存在旧密码匹配，自动升级到新的哈希密码格式
                    hashed_password, new_salt = hash_password(password)
                    self.cursor.execute(
                        "UPDATE users SET password = ?, salt = ? WHERE id = ?",
                        (hashed_password, new_salt, old_result[0])
                    )
                    self.conn.commit()
                    return old_result[0]
                return None
            
            # 新版验证方式 - 验证哈希密码
            if verify_password(password, stored_hash, salt):
                return user_id
            
            return None
        except Exception as e:
            print(f"用户验证出错: {e}")
            return None

    def get_user_profile(self, user_id):
        """获取用户资料"""
        try:
            # 打印调试信息
            print(f"正在获取用户ID为 {user_id} 的资料")
            
            # 确保users表有正确的结构
            self.cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='users'
            """)
            table_schema = self.cursor.fetchone()
            print(f"用户表结构: {table_schema}")
            
            # 查询用户信息
            sql = """
            SELECT id, username, gender, age, height, weight, 
                   diet_habit, exercise_habit, sleep_habit
            FROM users WHERE id = ?
            """
            print(f"执行SQL: {sql} 参数: {user_id}")
            
            self.cursor.execute(sql, (user_id,))
            user = self.cursor.fetchone()
            
            if user:
                # 获取列名
                columns = [description[0] for description in self.cursor.description]
                print(f"查询结果列: {columns}")
                
                # 创建用户信息字典
                user_dict = {}
                for i, col in enumerate(columns):
                    user_dict[col] = user[i]
                
                print(f"用户资料: {user_dict}")
                return user_dict
            else:
                print(f"未找到用户ID: {user_id}")
                # 返回包含所有必需字段的空字典
                return {
                    "id": user_id,
                    "username": "",
                    "gender": None,
                    "age": None,
                    "height": None,
                    "weight": None,
                    "diet_habit": None,
                    "exercise_habit": None,
                    "sleep_habit": None
                }
        except Exception as e:
            print(f"获取用户资料错误: {str(e)}")
            # 同样返回带有必需字段的空字典
            return {
                "id": user_id,
                "username": "",
                "gender": None,
                "age": None,
                "height": None,
                "weight": None,
                "diet_habit": None,
                "exercise_habit": None,
                "sleep_habit": None
            }

    @db_retry()
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
        """
        获取指定分类的食物列表，如果不指定分类则返回所有食物
        
        参数:
            category: 食物分类（可选）
            
        返回:
            食物列表
        """
        try:
            cursor = self.conn.cursor()
            
            if category and category != "全部":
                cursor.execute('''
                    SELECT * FROM foods 
                    WHERE category = ? 
                    ORDER BY name
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT * FROM foods 
                    ORDER BY category, name
                ''')
                
            foods = cursor.fetchall()
            print(f"从数据库获取食物: 分类='{category if category else '全部'}', 找到{len(foods)}条记录")
            
            # 如果找不到数据，尝试初始化食物数据库
            if not foods or len(foods) == 0:
                print("数据库中没有食物数据，尝试初始化...")
                self.initialize_food_database()
                
                # 再次查询
                if category and category != "全部":
                    cursor.execute('''
                        SELECT * FROM foods 
                        WHERE category = ? 
                        ORDER BY name
                    ''', (category,))
                else:
                    cursor.execute('''
                        SELECT * FROM foods 
                        ORDER BY category, name
                    ''')
                    
                foods = cursor.fetchall()
                print(f"初始化后再次获取: 找到{len(foods)}条记录")
            
            return foods
        except sqlite3.Error as e:
            print(f"获取食物列表失败: {str(e)}")
            return []

    def search_foods(self, keyword):
        """
        搜索食物
        
        参数:
            keyword: 搜索关键词
            
        返回:
            匹配的食物列表
        """
        try:
            cursor = self.conn.cursor()
            
            # 使用LIKE进行模糊搜索
            cursor.execute('''
                SELECT * FROM foods 
                WHERE name LIKE ? 
                ORDER BY category, name
            ''', (f'%{keyword}%',))
            
            foods = cursor.fetchall()
            print(f"搜索食物: 关键词='{keyword}', 找到{len(foods)}条记录")
            
            return foods
        except sqlite3.Error as e:
            print(f"搜索食物失败: {str(e)}")
            return []

    @db_retry()
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
            print(f"查询用户ID:{user_id}在日期:{date}的饮食记录")
            
            # 修改查询，使返回的列名更清晰
            self.cursor.execute(
                """
                SELECT 
                    dr.id, dr.user_id, dr.food_id, dr.food_name, dr.amount, dr.unit, 
                    dr.meal_type, dr.record_date, dr.record_time, dr.notes, dr.created_at,
                    f.calories, f.protein, f.fat, f.carbs, f.fiber, f.standard_weight
                FROM diet_records dr
                LEFT JOIN foods f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date = ?
                ORDER BY dr.record_time
                """,
                (user_id, date)
            )
            
            records = self.cursor.fetchall()
            print(f"找到{len(records)}条记录")
            
            # 打印第一条记录的结构，帮助调试
            if records and len(records) > 0:
                print(f"第一条记录包含{len(records[0])}个字段")
                column_names = [
                    "id", "user_id", "food_id", "food_name", "amount", "unit", 
                    "meal_type", "record_date", "record_time", "notes", "created_at",
                    "calories", "protein", "fat", "carbs", "fiber", "standard_weight"
                ]
                record_dict = {column_names[i]: records[0][i] for i in range(min(len(column_names), len(records[0])))}
                print(f"记录详情: {record_dict}")
                
            return records
        except sqlite3.Error as e:
            print(f"获取饮食记录错误: {e}")
            return []

    def get_diet_records_by_date_and_meal(self, user_id, date, meal_type):
        """获取用户特定日期和餐食类型的饮食记录"""
        try:
            print(f"查询用户ID:{user_id}在日期:{date}的{meal_type}记录")
            
            # 修改查询，使返回的列名更清晰
            self.cursor.execute(
                """
                SELECT 
                    dr.id, dr.user_id, dr.food_id, dr.food_name, dr.amount, dr.unit, 
                    dr.meal_type, dr.record_date, dr.record_time, dr.notes, dr.created_at,
                    f.calories, f.protein, f.fat, f.carbs, f.fiber, f.standard_weight
                FROM diet_records dr
                LEFT JOIN foods f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date = ? AND dr.meal_type = ?
                ORDER BY dr.record_time
                """,
                (user_id, date, meal_type)
            )
            
            records = self.cursor.fetchall()
            print(f"找到{len(records)}条记录")
            
            # 打印第一条记录的结构，帮助调试
            if records and len(records) > 0:
                print(f"第一条记录包含{len(records[0])}个字段")
                column_names = [
                    "id", "user_id", "food_id", "food_name", "amount", "unit", 
                    "meal_type", "record_date", "record_time", "notes", "created_at",
                    "calories", "protein", "fat", "carbs", "fiber", "standard_weight"
                ]
                record_dict = {column_names[i]: records[0][i] for i in range(min(len(column_names), len(records[0])))}
                print(f"记录详情: {record_dict}")
                
            return records
        except sqlite3.Error as e:
            print(f"获取饮食记录错误: {e}")
            return []

    @db_retry()
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
        """初始化食物数据库，导入基础食物数据"""
        try:
            print("开始初始化食物数据库...")
            cursor = self.conn.cursor()
            
            # 首先检查是否已有数据
            cursor.execute("SELECT COUNT(*) FROM foods")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"食物数据库已包含{count}条记录，跳过初始化")
                return True
                
            # 从food_data模块导入数据
            from data.food_data import load_food_data
            foods = load_food_data()
            
            if not foods:
                print("无法加载食物数据，初始化失败")
                return False
                
            print(f"从food_data模块加载了{len(foods)}条食物记录")
            
            # 批量插入记录
            for food in foods:
                try:
                    cursor.execute('''
                        INSERT INTO foods (name, category, calories, protein, fat, carbs, fiber, unit, standard_weight)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        food.get('name', ''),
                        food.get('category', ''),
                        food.get('calories', 0),
                        food.get('protein', 0),
                        food.get('fat', 0),
                        food.get('carbs', 0),
                        food.get('fiber', 0),
                        food.get('unit', '克'),
                        food.get('standard_weight', 100)
                    ))
                except sqlite3.Error as e:
                    print(f"插入食物记录失败: {str(e)}, 食物={food.get('name', '')}")
            
            self.conn.commit()
            print("食物数据库初始化完成")
            
            # 验证数据是否成功插入
            cursor.execute("SELECT COUNT(*) FROM foods")
            new_count = cursor.fetchone()[0]
            print(f"当前食物数据库包含{new_count}条记录")
            
            return True
        except Exception as e:
            print(f"初始化食物数据库时出错: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False

    def add_reminder(self, user_id, date, time, reminder_type, content):
        """添加提醒
        
        参数:
            user_id (int): 用户ID
            date (str): 提醒日期，格式为 'YYYY-MM-DD'
            time (str): 提醒时间，格式为 'HH:MM'
            reminder_type (str): 提醒类型，如'饮食'，'运动'，'睡眠'等
            content (str): 提醒内容
            
        返回:
            int or None: 成功返回提醒ID，失败返回None
        """
        try:
            print(f"添加提醒: user_id={user_id}, date={date}, time={time}, type={reminder_type}")
            
            # 查看reminders表结构
            self.cursor.execute("PRAGMA table_info(reminders)")
            columns = [row[1] for row in self.cursor.fetchall()]
            print(f"reminders表列: {columns}")
            
            # 使用正确的列名
            self.cursor.execute(
                """
                INSERT INTO reminders (user_id, reminder_date, reminder_time, reminder_type, content)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, date, time, reminder_type, content)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加提醒失败: {str(e)}")
            return None

    def get_reminders_by_user_date(self, user_id, date=None):
        """
        获取用户在指定日期的所有提醒
        
        参数:
            user_id: 用户ID
            date: 日期 (可选，默认为当前日期)
            
        返回:
            提醒列表
        """
        try:
            cursor = self.conn.cursor()
            
            if date:
                # 使用正确的列名 reminder_date 而不是 date
                cursor.execute('''
                SELECT * FROM reminders 
                WHERE user_id = ? AND reminder_date = ?
                ORDER BY reminder_time
                ''', (user_id, date))
            else:
                # 获取所有未完成的提醒
                cursor.execute('''
                SELECT * FROM reminders 
                WHERE user_id = ? AND is_completed = 0
                ORDER BY reminder_date, reminder_time
                ''', (user_id,))
                
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取提醒失败: {str(e)}")
            return []

    def get_reminders_for_time_range(self, user_id, start_time, end_time):
        """
        获取特定时间范围内的提醒
        
        参数:
            user_id: 用户ID
            start_time: 起始时间 (date_str, time_str)
            end_time: 结束时间 (date_str, time_str)
            
        返回:
            提醒列表
        """
        try:
            start_date, start_time_str = start_time
            end_date, end_time_str = end_time
            
            print(f"查询时间范围内的提醒: {start_date} {start_time_str} - {end_date} {end_time_str}")
            
            cursor = self.conn.cursor()
            
            # 构建查询
            # 简化查询以确保能够捕获到今天所有时间范围内的提醒
            cursor.execute(
                """
                SELECT * FROM reminders 
                WHERE user_id = ? 
                AND reminder_date = ? 
                AND reminder_time BETWEEN ? AND ?
                AND is_completed = 0
                ORDER BY reminder_time
                """,
                (user_id, start_date, start_time_str, end_time_str)
            )
            
            reminders = cursor.fetchall()
            
            if reminders:
                print(f"找到{len(reminders)}条时间范围内的提醒")
                if len(reminders) > 0:
                    for i, reminder in enumerate(reminders):
                        print(f"  提醒 {i+1}: ID={reminder[0]}, 日期={reminder[2]}, 时间={reminder[3]}, 内容={reminder[5]}")
            else:
                print("未找到时间范围内的提醒")
                
            return reminders
        except sqlite3.Error as e:
            print(f"获取时间范围内的提醒失败: {str(e)}")
            return []

    def update_reminder(self, reminder_id, date=None, time=None, content=None, is_completed=None):
        """更新提醒
        
        参数:
            reminder_id (int): 提醒ID
            date (str, optional): 新的日期，格式'YYYY-MM-DD'
            time (str, optional): 新的时间，格式'HH:MM'
            content (str, optional): 新的内容
            is_completed (bool, optional): 是否完成
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            # 构建更新字段
            update_fields = []
            params = []
            
            if date is not None:
                update_fields.append("reminder_date = ?")
                params.append(date)
                
            if time is not None:
                update_fields.append("reminder_time = ?")
                params.append(time)
                
            if content is not None:
                update_fields.append("content = ?")
                params.append(content)
                
            if is_completed is not None:
                update_fields.append("is_completed = ?")
                params.append(1 if is_completed else 0)
                
            if not update_fields:
                # 没有字段需要更新
                return True
                
            # 构建SQL语句
            sql = f"UPDATE reminders SET {', '.join(update_fields)} WHERE id = ?"
            params.append(reminder_id)
            
            # 执行更新
            self.cursor.execute(sql, params)
            self.conn.commit()
            
            return True
        except sqlite3.Error as e:
            print(f"更新提醒失败: {str(e)}")
            return False

    def delete_reminder(self, reminder_id):
        """删除提醒
        
        参数:
            reminder_id (int): 提醒ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            print(f"删除提醒: ID={reminder_id}")
            cursor = self.conn.cursor()
            
            # 执行删除
            cursor.execute(
                "DELETE FROM reminders WHERE id = ?",
                (reminder_id,)
            )
            self.conn.commit()
            
            # 检查是否删除了数据
            if cursor.rowcount > 0:
                print(f"提醒{reminder_id}已删除")
                return True
            else:
                print(f"未找到提醒{reminder_id}")
                return False
        except sqlite3.Error as e:
            print(f"删除提醒失败: {str(e)}")
            return False

    def mark_reminder_completed(self, reminder_id):
        """将提醒标记为已完成
        
        参数:
            reminder_id: 提醒ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            print(f"标记提醒为已完成: ID={reminder_id}")
            
            # 确认提醒存在
            self.cursor.execute("SELECT id FROM reminders WHERE id = ?", (reminder_id,))
            if not self.cursor.fetchone():
                print(f"提醒不存在: ID={reminder_id}")
                return False
            
            # 更新完成状态
            self.cursor.execute(
                "UPDATE reminders SET is_completed = 1 WHERE id = ?",
                (reminder_id,)
            )
            self.conn.commit()
            
            # 验证更新是否成功
            self.cursor.execute("SELECT is_completed FROM reminders WHERE id = ?", (reminder_id,))
            result = self.cursor.fetchone()
            if result and result[0] == 1:
                print(f"提醒已成功标记为完成: ID={reminder_id}")
                return True
            else:
                print(f"标记提醒完成失败: ID={reminder_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"标记提醒完成时出错: {str(e)}")
            return False

    @db_retry()
    def add_exercise_record(self, user_id, exercise_name, category, duration, intensity, calories_burned, record_date, record_time, notes=""):
        """
        添加运动记录
        
        参数:
            user_id: 用户ID
            exercise_name: 运动名称
            category: 运动分类
            duration: 持续时间(分钟)
            intensity: 强度(低/中/高)
            calories_burned: 消耗的卡路里
            record_date: 记录日期
            record_time: 记录时间
            notes: 备注
            
        返回:
            成功返回记录ID，失败返回None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO exercise_records 
            (user_id, exercise_name, category, duration, intensity, calories_burned, record_date, record_time, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, exercise_name, category, duration, intensity, calories_burned, record_date, record_time, notes))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"添加运动记录时出错: {str(e)}")
            return None

    def get_exercise_records_by_date(self, user_id, date):
        """
        获取指定日期的运动记录
        
        参数:
            user_id: 用户ID
            date: 日期(YYYY-MM-DD)
            
        返回:
            运动记录列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM exercise_records
            WHERE user_id = ? AND record_date = ?
            ORDER BY record_time
            ''', (user_id, date))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"获取运动记录时出错: {str(e)}")
            return []

    @db_retry()
    def update_exercise_record(self, record_id, exercise_name=None, category=None, 
                              duration=None, intensity=None, calories_burned=None,
                              record_date=None, record_time=None, notes=None):
        """
        更新运动记录
        
        参数:
            record_id: 记录ID
            其他参数: 要更新的字段
            
        返回:
            成功返回True，失败返回False
        """
        try:
            cursor = self.conn.cursor()

            # 检索当前记录
            cursor.execute("SELECT * FROM exercise_records WHERE id = ?", (record_id,))
            record = cursor.fetchone()
            if not record:
                return False

            # 准备更新语句
            update_fields = []
            values = []

            if exercise_name is not None:
                update_fields.append("exercise_name = ?")
                values.append(exercise_name)

            if category is not None:
                update_fields.append("category = ?")
                values.append(category)

            if duration is not None:
                update_fields.append("duration = ?")
                values.append(duration)

            if intensity is not None:
                update_fields.append("intensity = ?")
                values.append(intensity)

            if calories_burned is not None:
                update_fields.append("calories_burned = ?")
                values.append(calories_burned)

            if record_date is not None:
                update_fields.append("record_date = ?")
                values.append(record_date)

            if record_time is not None:
                update_fields.append("record_time = ?")
                values.append(record_time)

            if notes is not None:
                update_fields.append("notes = ?")
                values.append(notes)

            if not update_fields:
                return True  # 没有要更新的字段

            # 构建SQL语句
            sql = f"UPDATE exercise_records SET {', '.join(update_fields)} WHERE id = ?"
            values.append(record_id)

            cursor.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"更新运动记录时出错: {str(e)}")
            return False

    def delete_exercise_record(self, record_id):
        """
        删除运动记录
        
        参数:
            record_id: 记录ID
            
        返回:
            成功返回True，失败返回False
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM exercise_records WHERE id = ?", (record_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"删除运动记录时出错: {str(e)}")
            return False

    def get_total_calories_burned_by_date(self, user_id, date):
        """
        获取指定日期消耗的总卡路里
        
        参数:
            user_id: 用户ID
            date: 日期(YYYY-MM-DD)
            
        返回:
            消耗的总卡路里
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT SUM(calories_burned) FROM exercise_records
            WHERE user_id = ? AND record_date = ?
            ''', (user_id, date))
            result = cursor.fetchone()[0]
            return result if result else 0
        except sqlite3.Error as e:
            logger.error(f"获取消耗总卡路里时出错: {str(e)}")
            return 0

    def get_weekly_exercise_summary(self, user_id, start_date, end_date):
        """获取每周运动摘要"""
        try:
            self.cursor.execute("""
            SELECT record_date, SUM(duration), SUM(calories_burned)
            FROM exercise_records
            WHERE user_id = ? AND record_date BETWEEN ? AND ?
            GROUP BY record_date
            ORDER BY record_date
            """, (user_id, start_date, end_date))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取每周运动摘要出错: {str(e)}")
            return []
            
    def get_weekly_diet_summary(self, user_id, start_date, end_date):
        """获取每周饮食摘要，包含每日摄入的总卡路里、蛋白质、脂肪和碳水化合物"""
        try:
            self.cursor.execute("""
            SELECT dr.record_date, 
                   SUM(f.calories * dr.amount / f.standard_weight) AS total_calories,
                   SUM(f.protein * dr.amount / f.standard_weight) AS total_protein,
                   SUM(f.fat * dr.amount / f.standard_weight) AS total_fat,
                   SUM(f.carbs * dr.amount / f.standard_weight) AS total_carbs
            FROM diet_records dr
            LEFT JOIN foods f ON dr.food_id = f.id
            WHERE dr.user_id = ? AND dr.record_date BETWEEN ? AND ?
            GROUP BY dr.record_date
            ORDER BY dr.record_date
            """, (user_id, start_date, end_date))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取每周饮食摘要出错: {str(e)}")
            return []
            
    def get_weekly_sleep_summary(self, user_id, start_date, end_date):
        """获取每周睡眠摘要，包含每日睡眠时长和质量"""
        try:
            self.cursor.execute("""
            SELECT sleep_date, AVG(duration) AS avg_duration, AVG(quality) AS avg_quality
            FROM sleep_records
            WHERE user_id = ? AND sleep_date BETWEEN ? AND ?
            GROUP BY sleep_date
            ORDER BY sleep_date
            """, (user_id, start_date, end_date))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取每周睡眠摘要出错: {str(e)}")
            return []
            
    def get_user_profile_for_analysis(self, user_id):
        """获取用户资料用于分析"""
        try:
            self.cursor.execute("""
            SELECT gender, age, height, weight, diet_habit, exercise_habit, sleep_habit
            FROM users 
            WHERE id = ?
            """, (user_id,))
            
            result = self.cursor.fetchone()
            if result:
                return {
                    "gender": result[0],
                    "age": result[1],
                    "height": result[2],
                    "weight": result[3],
                    "diet_habit": result[4],
                    "exercise_habit": result[5],
                    "sleep_habit": result[6]
                }
            return None
        except Exception as e:
            print(f"获取用户资料出错: {str(e)}")
            return None
            
    # 睡眠记录相关方法
    @db_retry()
    def add_sleep_record(self, user_id, sleep_date, sleep_time, wake_date, wake_time, duration, quality, notes=""):
        """添加睡眠记录"""
        try:
            self.cursor.execute("""
            INSERT INTO sleep_records 
            (user_id, sleep_date, sleep_time, wake_date, wake_time, duration, quality, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, sleep_date, sleep_time, wake_date, wake_time, duration, quality, notes))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加睡眠记录出错: {str(e)}")
            return False
            
    def get_sleep_records_by_date(self, user_id, date):
        """获取指定日期的睡眠记录"""
        try:
            self.cursor.execute("""
            SELECT * FROM sleep_records
            WHERE user_id = ? AND (sleep_date = ? OR wake_date = ?)
            ORDER BY sleep_date DESC, sleep_time DESC
            """, (user_id, date, date))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取睡眠记录出错: {str(e)}")
            return []
            
    def get_sleep_record_by_id(self, record_id):
        """根据ID获取睡眠记录"""
        try:
            self.cursor.execute("""
            SELECT * FROM sleep_records
            WHERE id = ?
            """, (record_id,))
            
            return self.cursor.fetchone()
        except Exception as e:
            print(f"获取睡眠记录出错: {str(e)}")
            return None
            
    @db_retry()
    def update_sleep_record(self, record_id, sleep_date=None, sleep_time=None, 
                           wake_date=None, wake_time=None, duration=None, 
                           quality=None, notes=None):
        """更新睡眠记录"""
        try:
            # 获取现有记录
            self.cursor.execute("SELECT * FROM sleep_records WHERE id = ?", (record_id,))
            record = self.cursor.fetchone()
            
            if not record:
                print(f"未找到ID为{record_id}的睡眠记录")
                return False
                
            # 使用现有值作为默认值
            sleep_date = sleep_date if sleep_date is not None else record[3]
            sleep_time = sleep_time if sleep_time is not None else record[4]
            wake_date = wake_date if wake_date is not None else record[5]
            wake_time = wake_time if wake_time is not None else record[6]
            duration = duration if duration is not None else record[7]
            quality = quality if quality is not None else record[8]
            notes = notes if notes is not None else record[9]
            
            # 更新记录
            self.cursor.execute("""
            UPDATE sleep_records
            SET sleep_date = ?, sleep_time = ?, wake_date = ?, wake_time = ?,
                duration = ?, quality = ?, notes = ?
            WHERE id = ?
            """, (sleep_date, sleep_time, wake_date, wake_time, duration, quality, notes, record_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新睡眠记录出错: {str(e)}")
            return False
            
    def delete_sleep_record(self, record_id):
        """删除睡眠记录"""
        try:
            self.cursor.execute("DELETE FROM sleep_records WHERE id = ?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除睡眠记录出错: {str(e)}")
            return False

    def upgrade_passwords(self):
        """升级数据库中的明文密码到哈希密码"""
        try:
            # 检查是否有用户的salt为空，表示是明文密码
            self.cursor.execute("SELECT id, username, password FROM users WHERE salt IS NULL OR salt = ''")
            users_to_upgrade = self.cursor.fetchall()
            
            if not users_to_upgrade:
                # print("所有用户密码已经是哈希格式，不需要升级")
                return
                
            print(f"需要升级密码的用户数: {len(users_to_upgrade)}")
            
            for user_id, username, plain_password in users_to_upgrade:
                try:
                    # 对明文密码进行哈希处理
                    hashed_password, salt = hash_password(plain_password)
                    
                    # 更新用户的密码和盐值
                    self.cursor.execute(
                        "UPDATE users SET password = ?, salt = ? WHERE id = ?",
                        (hashed_password, salt, user_id)
                    )
                    print(f"已升级用户 {username} (ID: {user_id}) 的密码")
                except Exception as e:
                    print(f"升级用户 {username} (ID: {user_id}) 的密码时出错: {e}")
            
            self.conn.commit()
            print("密码升级完成")
        except Exception as e:
            print(f"升级密码过程出错: {e}") 