import random
import time
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from PyQt5.QtGui import QPixmap
import os
import math

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

# 在真实环境中，这个函数会调用短信API
def send_verification_code(phone, code):
    """模拟发送验证码到手机"""
    # 在实际应用中，这里会调用短信服务API
    print(f"向手机号 {phone} 发送验证码: {code}")
    # 模拟发送成功
    return True 

def generate_captcha_text(length=4):
    """生成随机验证码文本"""
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choices(characters, k=length))

def generate_captcha_image(text, width=160, height=60):
    """生成更美观的验证码图片"""
    # 创建图像，使用浅色背景
    background = random_light_color()
    image = Image.new('RGB', (width, height), color=background)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制渐变背景
    for i in range(0, width, 2):
        for j in range(height):
            if random.randint(0, 20) == 5:
                draw.point((i, j), fill=random_light_color())
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        # 尝试找到系统字体
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
                
        font_size = random.randint(32, 38)
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 计算文本总宽度以便居中显示
    try:
        # 新版本 Pillow 的方法 (9.0.0+)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # 旧版本 Pillow 的方法
        text_width, text_height = draw.textsize(text, font=font)
    
    # 文字起始位置
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 逐个绘制字符，使用不同颜色和角度
    for i, char in enumerate(text):
        # 计算每个字符的位置，略微偏移以产生不规则效果
        char_x = x + i * (text_width // len(text)) + random.randint(-5, 5)
        char_y = y + random.randint(-5, 5)
        
        # 随机旋转角度
        angle = random.randint(-30, 30)
        
        # 随机深色（确保与背景对比明显）
        text_color = random_dark_color()
        
        # 创建单个字符图像并旋转
        char_img = Image.new('RGBA', (text_width // len(text) + 10, text_height + 10), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        
        # 绘制字符
        try:
            # 新版本 Pillow
            char_bbox = font.getbbox(char)
            char_width = char_bbox[2] - char_bbox[0]
            char_height = char_bbox[3] - char_bbox[1]
            char_draw.text(((text_width // len(text) - char_width) // 2 + 5, 5), char, font=font, fill=text_color)
        except AttributeError:
            # 旧版本 Pillow
            char_draw.text((5, 5), char, font=font, fill=text_color)
        
        # 旋转字符
        rotated_char = char_img.rotate(angle, expand=1, resample=Image.BICUBIC)
        
        # 粘贴到主图像
        image.paste(rotated_char, (char_x, char_y), rotated_char)
    
    # 添加干扰线
    for _ in range(random.randint(3, 6)):
        start_x = random.randint(0, width // 4)
        start_y = random.randint(0, height)
        end_x = random.randint(3 * width // 4, width)
        end_y = random.randint(0, height)
        
        # 曲线控制点
        control_x = random.randint(width // 4, 3 * width // 4)
        control_y = random.randint(0, height)
        
        # 随机线条颜色
        line_color = random_dark_color()
        line_width = random.randint(1, 2)
        
        # 绘制贝塞尔曲线
        for t in range(0, 100, 2):
            t /= 100
            # 二次贝塞尔曲线
            x = int((1-t)**2 * start_x + 2*(1-t)*t*control_x + t**2*end_x)
            y = int((1-t)**2 * start_y + 2*(1-t)*t*control_y + t**2*end_y)
            
            if 0 <= x < width and 0 <= y < height:
                # 绘制粗线条
                for dx in range(-line_width, line_width+1):
                    for dy in range(-line_width, line_width+1):
                        if dx*dx + dy*dy <= line_width*line_width:
                            px, py = x + dx, y + dy
                            if 0 <= px < width and 0 <= py < height:
                                draw.point((px, py), fill=line_color)
    
    # 轻微扭曲整个图像
    image = apply_wave_distortion(image)
    
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

def apply_wave_distortion(image, amplitude=4.0):
    """应用波浪扭曲效果"""
    width, height = image.size
    new_img = Image.new('RGB', (width, height))
    
    for i in range(width):
        for j in range(height):
            # 水平波动
            offset_x = int(amplitude * math.sin(j / height * 2 * math.pi))
            # 垂直波动
            offset_y = int(amplitude * math.cos(i / width * 2 * math.pi))
            
            src_x = i + offset_x
            src_y = j + offset_y
            
            # 确保坐标在有效范围内
            if src_x >= width:
                src_x = width - 1
            if src_x < 0:
                src_x = 0
            if src_y >= height:
                src_y = height - 1
            if src_y < 0:
                src_y = 0
                
            # 复制像素
            new_img.putpixel((i, j), image.getpixel((src_x, src_y)))
            
    return new_img 