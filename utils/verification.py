import random
import time
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from PyQt5.QtGui import QPixmap
import os
import math
import hashlib
import string

def validate_phone_number(phone):
    """验证手机号格式是否正确（中国大陆手机号）"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_password_strength(password):
    """验证密码强度
    规则：至少8位，包含字母和数字，不能是简单数字或字母
    """
    if len(password) < 8:
        return False, "密码长度必须至少为8位"
    
    if password.isdigit():
        return False, "密码不能仅包含数字"
    
    if password.isalpha():
        return False, "密码不能仅包含字母"
    
    return True, "密码强度合格"

def generate_salt(length=16):
    """生成随机盐值
    
    参数:
        length: 盐值长度，默认16字符
        
    返回:
        随机盐值字符串
    """
    salt_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(salt_chars) for _ in range(length))

def hash_password(password, salt=None):
    """使用SHA-256算法和盐值哈希密码
    
    参数:
        password: 原始密码
        salt: 盐值，如果未提供则自动生成
        
    返回:
        (hashed_password, salt) 元组，包含哈希后的密码和使用的盐值
    """
    if salt is None:
        salt = generate_salt()
        
    # 将密码和盐值组合并进行哈希
    salted_password = password + salt
    hash_obj = hashlib.sha256(salted_password.encode('utf-8'))
    hashed_password = hash_obj.hexdigest()
    
    return hashed_password, salt

def verify_password(password, stored_hash, salt):
    """验证密码是否与存储的哈希值匹配
    
    参数:
        password: 需要验证的密码
        stored_hash: 存储的哈希值
        salt: 存储的盐值
        
    返回:
        布尔值，密码是否匹配
    """
    # 使用相同盐值计算哈希
    calculated_hash, _ = hash_password(password, salt)
    
    # 比较计算出的哈希值与存储的哈希值
    return calculated_hash == stored_hash


def generate_captcha_text(length=4):
    """生成随机验证码文本，使用数字和大写字母，保留一定的混淆性"""
    # 保留一些混淆字符，但不使用太难区分的
    characters = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    return ''.join(random.choices(characters, k=length))

def generate_captcha_image(text, width=160, height=60):
    """生成验证码图片，增加适度干扰但保持可读性"""
    # 使用随机浅色背景
    bg_color = (random.randint(230, 245), random.randint(230, 245), random.randint(230, 245))
    image = Image.new('RGB', (width, height), color=bg_color)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体
    try:
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
            '/System/Library/Fonts/Tahoma.ttf',  # macOS
            'C:/Windows/Fonts/Arial.ttf',  # Windows
            'C:/Windows/Fonts/Georgia.ttf',  # Windows
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
                
        font_size = random.randint(32, 38)  # 稍微随机字体大小
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 计算文本总宽度以便居中显示
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    # 计算文字起始位置
    x = (width - text_width) // 2
    if x < 10:
        x = 10  # 确保不靠得太左
    y = (height - text_height) // 2
    
    # 添加背景干扰点
    for _ in range(60):  # 增加干扰点数量
        draw.point(
            (random.randint(0, width), random.randint(0, height)),
            fill=(random.randint(160, 220), random.randint(160, 220), random.randint(160, 220))
        )
    
    # 添加干扰线
    for _ in range(3):  # 3条干扰线
        start = (random.randint(0, width//4), random.randint(0, height))
        end = (random.randint(3*width//4, width), random.randint(0, height))
        color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
        draw.line([start, end], fill=color, width=1)
    
    # 绘制文字 - 每个字符单独绘制，使用不同颜色和轻微旋转
    char_width = text_width // len(text)
    for i, char in enumerate(text):
        # 随机深色
        color = (
            random.randint(0, 60),
            random.randint(0, 60),
            random.randint(0, 60)
        )
        
        # 轻微偏移
        char_x = x + i * char_width + random.randint(-3, 3)
        char_y = y + random.randint(-3, 3)
        
        # 创建单个字符图像用于旋转
        char_img = Image.new('RGBA', (char_width + 10, text_height + 10), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        
        # 绘制字符
        char_draw.text((5, 5), char, font=font, fill=color)
        
        # 轻微旋转（角度较小）
        angle = random.randint(-10, 10)  # 较小的旋转角度
        rotated = char_img.rotate(angle, expand=1, resample=Image.BICUBIC)
        
        # 粘贴到主图像
        image.paste(rotated, (char_x, char_y), rotated)
    
    # 添加波形扭曲（程度较轻）
    image = apply_wave_distortion(image, amplitude=2.0)  # 使用较小的振幅
    
    # 将PIL图像转换为QPixmap
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.read())
    
    return pixmap, text

def random_light_color():
    """生成随机浅色"""
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return (r, g, b)

def random_dark_color():
    """生成随机深色"""
    r = random.randint(0, 100)
    g = random.randint(0, 100)
    b = random.randint(0, 100)
    return (r, g, b)

def apply_wave_distortion(image, amplitude=2.0):
    """应用轻微的波浪扭曲效果"""
    width, height = image.size
    new_img = Image.new('RGB', (width, height))
    
    for i in range(width):
        for j in range(height):
            # 水平波动
            offset_x = int(amplitude * math.sin(j / height * 2 * math.pi))
            # 垂直波动
            offset_y = int(amplitude * math.cos(i / width * 2 * math.pi))
            
            src_x = min(max(i + offset_x, 0), width - 1)
            src_y = min(max(j + offset_y, 0), height - 1)
                
            # 复制像素
            new_img.putpixel((i, j), image.getpixel((src_x, src_y)))
            
    return new_img 