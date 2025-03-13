import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

class WeeklyReportGenerator:
    """生成健康周报的工具类，支持导出为PDF格式"""
    
    def __init__(self, analysis_results, user_info=None, output_dir="reports"):
        """
        初始化周报生成器
        
        参数:
            analysis_results: 健康分析结果，包含统计数据和建议
            user_info: 用户信息(可选)
            output_dir: 输出目录
        """
        self.results = analysis_results
        self.user_info = user_info or {}
        self.output_dir = output_dir
        self.has_chinese_support = False  # 是否支持中文
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 检查是否安装了pypinyin
        self.has_pinyin = self._check_pypinyin()
        
    def _check_pypinyin(self):
        """检查是否安装了pypinyin，如果没有则提示安装"""
        try:
            import pypinyin
            return True
        except ImportError:
            print("\n警告: 未安装pypinyin库，无法将中文转换为拼音")
            print("建议安装pypinyin以获得更好的PDF中文支持: pip install pypinyin\n")
            return False
        
    def _translate_chinese_to_ascii(self, text):
        """将中文转换为拼音或ASCII表示，用于在没有中文字体时使用"""
        if not isinstance(text, str):
            return str(text)
            
        try:
            # 检查是否有中文字符
            has_chinese = False
            for char in text:
                if ord(char) > 127:  # 非ASCII字符
                    has_chinese = True
                    break
                    
            if not has_chinese:
                return text  # 如果没有中文，直接返回原文本
                
            # 尝试使用pypinyin将中文转为拼音
            if self.has_pinyin:
                try:
                    from pypinyin import lazy_pinyin
                    result = ' '.join(lazy_pinyin(text))
                    return result
                except Exception as e:
                    print(f"拼音转换失败: {e}")
                
            # 如果无法转为拼音，使用Unicode编码方式表示
            result = ""
            for char in text:
                if ord(char) > 127:  # 非ASCII字符
                    result += f"[U+{ord(char):04X}]"  # 使用Unicode编码表示
                else:
                    result += char
            return result
        except Exception as e:
            print(f"转换中文失败: {e}")
            return str(text)  # 确保返回字符串
        
    def _convert_text_if_needed(self, text):
        """如果需要，转换文本为ASCII格式"""
        if not self.has_chinese_support:
            return self._translate_chinese_to_ascii(text)
        return text
        
    def _get_available_font(self):
        """获取可用的中文字体"""
        # 常见中文字体列表，按优先级排序
        chinese_fonts = ['SimSun', 'Microsoft YaHei', 'SimHei', 'KaiTi', 'NSimSun', 'STSong', 'Arial Unicode MS']
        
        # 尝试从reportlab注册的字体中找可用的中文字体
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 尝试注册字体
        try:
            # 首先尝试使用内置的中文支持
            try:
                # 注册思源宋体 Source Han Sans - 一种开源中文字体
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                self.has_chinese_support = True
                return 'STSong-Light'
            except:
                print("无法注册内置中文字体，尝试系统字体...")
            
            # 检查环境变量中的字体目录
            import os
            import sys
            
            if sys.platform.startswith('win'):
                # Windows字体目录
                font_dirs = [
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Windows\\Fonts')
                ]
            else:
                # Linux/Mac字体目录
                font_dirs = [
                    '/usr/share/fonts',
                    '/usr/local/share/fonts',
                    os.path.expanduser('~/.fonts')
                ]
            
            # 尝试找到并注册中文字体
            for font_name in chinese_fonts:
                for font_dir in font_dirs:
                    # 检查常见的字体文件名
                    possible_files = [
                        f"{font_name}.ttf",
                        f"{font_name}.ttc",
                        f"{font_name}.TTF",
                        f"{font_name}.TTC"
                    ]
                    
                    for file_name in possible_files:
                        font_path = os.path.join(font_dir, file_name)
                        if os.path.exists(font_path):
                            try:
                                # 注册字体
                                font_reg_name = f"custom_{font_name}"
                                pdfmetrics.registerFont(TTFont(font_reg_name, font_path))
                                print(f"成功注册字体: {font_name} 从 {font_path}")
                                self.has_chinese_support = True
                                return font_reg_name
                            except Exception as e:
                                print(f"注册字体 {font_name} 时出错: {e}")
            
            # 如果没有找到中文字体，使用ReportLab支持的默认Unicode字体
            try:
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                for font_name in ['HeiseiMin-W3', 'HeiseiKakuGo-W5', 'STSong-Light']:
                    try:
                        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
                        print(f"使用ReportLab内置Unicode字体: {font_name}")
                        self.has_chinese_support = True
                        return font_name
                    except:
                        pass
            except:
                pass
                
            # 最后的方案：使用默认字体
            print("警告: 未找到可用的中文字体，PDF中的中文将被转换为ASCII表示")
            self.has_chinese_support = False
            return 'Helvetica'
            
        except Exception as e:
            print(f"字体处理时出错: {e}")
            self.has_chinese_support = False
            return 'Helvetica'  # 返回默认字体
    
    def generate_pdf(self, filename=None):
        """
        生成PDF格式的健康周报
        
        参数:
            filename: 输出文件名(可选)，如不提供将使用当前日期
        
        返回:
            生成的PDF文件路径
        """
        # 设置文件名
        if not filename:
            today = datetime.datetime.now()
            filename = f"健康周报_{today.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # 确保文件名以.pdf结尾
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # 完整的文件路径
        filepath = os.path.join(self.output_dir, filename)
        
        # 获取字体
        font_name = self._get_available_font()
        
        # 添加中文支持
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        styles = getSampleStyleSheet()
        
        # 修改段落样式使用我们的字体
        for style_name in styles.byName:
            styles[style_name].fontName = font_name
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # 构建PDF内容
        story = []
        normal_style = styles["Normal"]
        heading1_style = styles["Heading1"]
        heading2_style = styles["Heading2"]
        
        # 自定义样式
        title_style = ParagraphStyle(
            "CustomTitle", 
            parent=styles["Title"],
            alignment=1,  # 居中
            spaceAfter=0.5*cm
        )
        subtitle_style = ParagraphStyle(
            "CustomSubTitle", 
            parent=styles["Heading2"],
            alignment=1,  # 居中
            fontSize=14,
            spaceAfter=1*cm
        )
        section_title_style = ParagraphStyle(
            "SectionTitle", 
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=0.5*cm,
            spaceAfter=0.3*cm
        )
        subsection_title_style = ParagraphStyle(
            "SubSectionTitle", 
            parent=styles["Heading3"],
            fontSize=12,
            spaceBefore=0.3*cm,
            spaceAfter=0.2*cm
        )
        advice_style = ParagraphStyle(
            "Advice", 
            parent=normal_style,
            leftIndent=0.5*cm,
            fontSize=10,
            spaceBefore=0.1*cm,
            spaceAfter=0.1*cm
        )
        
        # 标题和日期
        today = datetime.datetime.now()
        week_start = datetime.datetime.now() - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        
        title_text = self._convert_text_if_needed("健康生活周报告")
        story.append(Paragraph(title_text, title_style))
        
        date_text = self._convert_text_if_needed(
            f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
        )
        story.append(Paragraph(date_text, subtitle_style))
        
        # 用户信息
        if self.user_info:
            user_info_data = [
                [self._convert_text_if_needed("姓名"), self._convert_text_if_needed(self.user_info.get("username", ""))],
                [self._convert_text_if_needed("性别"), self._convert_text_if_needed(self.user_info.get("gender", ""))],
                [self._convert_text_if_needed("年龄"), self._convert_text_if_needed(str(self.user_info.get("age", "")))],
                [self._convert_text_if_needed("身高"), self._convert_text_if_needed(f"{self.user_info.get('height', '')}厘米")],
                [self._convert_text_if_needed("体重"), self._convert_text_if_needed(f"{self.user_info.get('weight', '')}公斤")]
            ]
            
            # 用户表格样式
            user_table = Table(
                user_info_data, 
                colWidths=[2*cm, 5*cm],
                style=TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('PADDING', (0, 0), (-1, -1), 6)
                ])
            )
            
            story.append(Paragraph(self._convert_text_if_needed("个人信息"), section_title_style))
            story.append(user_table)
            story.append(Spacer(1, 0.5*cm))
        
        # 总体健康建议
        story.append(Paragraph(self._convert_text_if_needed("本周健康总结"), section_title_style))
        for advice in self.results.get("overall_advice", []):
            story.append(Paragraph(self._convert_text_if_needed(advice), advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 运动部分
        exercise_stats = self.results.get("exercise_stats", {})
        story.append(Paragraph(self._convert_text_if_needed("运动分析"), section_title_style))
        
        # 运动数据统计
        exercise_data = [
            [self._convert_text_if_needed("指标"), self._convert_text_if_needed("数值"), self._convert_text_if_needed("建议值"), self._convert_text_if_needed("达标情况")],
            [self._convert_text_if_needed("运动天数"), self._convert_text_if_needed(f"{exercise_stats.get('exercise_days', 0)}天"), self._convert_text_if_needed("≥3天/周"), self._convert_text_if_needed("达标" if exercise_stats.get('exercise_days', 0) >= 3 else "未达标")],
            [self._convert_text_if_needed("总运动时间"), self._convert_text_if_needed(f"{exercise_stats.get('total_duration', 0)}分钟"), self._convert_text_if_needed("≥150分钟/周"), self._convert_text_if_needed("达标" if exercise_stats.get('meets_recommendation', False) else "未达标")],
            [self._convert_text_if_needed("平均每天运动"), self._convert_text_if_needed(f"{exercise_stats.get('avg_duration_per_day', 0):.1f}分钟"), self._convert_text_if_needed("≥30分钟/天"), self._convert_text_if_needed("达标" if exercise_stats.get('avg_duration_per_day', 0) >= 30 else "未达标")],
            [self._convert_text_if_needed("总消耗卡路里"), self._convert_text_if_needed(f"{exercise_stats.get('total_calories', 0)}卡路里"), "-", "-"]
        ]
        
        exercise_table = Table(
            exercise_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(exercise_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 运动建议
        story.append(Paragraph(self._convert_text_if_needed("运动建议"), subsection_title_style))
        for advice in self.results.get("exercise_advice", []):
            story.append(Paragraph(self._convert_text_if_needed(advice), advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 饮食部分
        diet_stats = self.results.get("diet_stats", {})
        story.append(Paragraph(self._convert_text_if_needed("饮食分析"), section_title_style))
        
        # 饮食数据统计
        diet_data = [
            [self._convert_text_if_needed("指标"), self._convert_text_if_needed("日均摄入"), self._convert_text_if_needed("推荐值"), self._convert_text_if_needed("达标比例")],
            [self._convert_text_if_needed("总热量"), self._convert_text_if_needed(f"{diet_stats.get('avg_calories_per_day', 0):.1f}卡路里"), self._convert_text_if_needed(f"{diet_stats.get('recommended_calories', 0)}卡路里"), self._convert_text_if_needed(f"{diet_stats.get('calories_percentage', 0):.1f}%")],
            [self._convert_text_if_needed("蛋白质"), self._convert_text_if_needed(f"{diet_stats.get('avg_protein_per_day', 0):.1f}克"), self._convert_text_if_needed(f"{diet_stats.get('recommended_protein', 0)}克"), self._convert_text_if_needed(f"{diet_stats.get('protein_percentage', 0):.1f}%")],
            [self._convert_text_if_needed("脂肪"), self._convert_text_if_needed(f"{diet_stats.get('avg_fat_per_day', 0):.1f}克"), self._convert_text_if_needed(f"{diet_stats.get('recommended_fat', 0)}克"), self._convert_text_if_needed(f"{diet_stats.get('fat_percentage', 0):.1f}%")],
            [self._convert_text_if_needed("碳水化合物"), self._convert_text_if_needed(f"{diet_stats.get('avg_carbs_per_day', 0):.1f}克"), self._convert_text_if_needed(f"{diet_stats.get('recommended_carbs', 0)}克"), self._convert_text_if_needed(f"{diet_stats.get('carbs_percentage', 0):.1f}%")]
        ]
        
        diet_table = Table(
            diet_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(diet_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 营养比例
        nutrition_ratio = [
            [self._convert_text_if_needed("营养素"), self._convert_text_if_needed("占比"), self._convert_text_if_needed("推荐范围")],
            [self._convert_text_if_needed("蛋白质"), self._convert_text_if_needed(f"{diet_stats.get('protein_ratio', 0):.1f}%"), self._convert_text_if_needed("10-35%")],
            [self._convert_text_if_needed("脂肪"), self._convert_text_if_needed(f"{diet_stats.get('fat_ratio', 0):.1f}%"), self._convert_text_if_needed("20-35%")],
            [self._convert_text_if_needed("碳水化合物"), self._convert_text_if_needed(f"{diet_stats.get('carbs_ratio', 0):.1f}%"), self._convert_text_if_needed("45-65%")]
        ]
        
        nutrition_table = Table(
            nutrition_ratio, 
            colWidths=[4*cm, 3*cm, 4*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(Paragraph(self._convert_text_if_needed("营养素比例"), subsection_title_style))
        story.append(nutrition_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 饮食建议
        story.append(Paragraph(self._convert_text_if_needed("饮食建议"), subsection_title_style))
        for advice in self.results.get("diet_advice", []):
            story.append(Paragraph(self._convert_text_if_needed(advice), advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 睡眠部分
        sleep_stats = self.results.get("sleep_stats", {})
        story.append(Paragraph(self._convert_text_if_needed("睡眠分析"), section_title_style))
        
        # 睡眠数据统计
        sleep_data = [
            [self._convert_text_if_needed("指标"), self._convert_text_if_needed("数值"), self._convert_text_if_needed("建议值"), self._convert_text_if_needed("达标情况")],
            [self._convert_text_if_needed("睡眠天数"), self._convert_text_if_needed(f"{sleep_stats.get('sleep_days', 0)}天"), self._convert_text_if_needed(f"{sleep_stats.get('total_days', 7)}天"), self._convert_text_if_needed("达标" if sleep_stats.get('sleep_days', 0) >= sleep_stats.get('total_days', 7) else "未达标")],
            [self._convert_text_if_needed("平均睡眠时长"), self._convert_text_if_needed(f"{sleep_stats.get('avg_duration_per_day', 0) / 60:.1f}小时"), self._convert_text_if_needed(f"{sleep_stats.get('recommended_sleep', 8)}小时"), self._convert_text_if_needed("达标" if sleep_stats.get('meets_recommendation', False) else "未达标")],
            [self._convert_text_if_needed("平均睡眠质量"), self._convert_text_if_needed(f"{sleep_stats.get('avg_quality', 0):.1f}分"), self._convert_text_if_needed("≥3.5分"), self._convert_text_if_needed("达标" if sleep_stats.get('avg_quality', 0) >= 3.5 else "未达标")]
        ]
        
        sleep_table = Table(
            sleep_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(sleep_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 睡眠建议
        story.append(Paragraph(self._convert_text_if_needed("睡眠建议"), subsection_title_style))
        for advice in self.results.get("sleep_advice", []):
            story.append(Paragraph(self._convert_text_if_needed(advice), advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 注意事项
        story.append(Paragraph(self._convert_text_if_needed("温馨提示"), section_title_style))
        story.append(Paragraph(self._convert_text_if_needed("1. 本报告基于您记录的数据生成，数据越完整分析越准确。"), advice_style))
        story.append(Paragraph(self._convert_text_if_needed("2. 健康建议仅供参考，如有特殊健康问题请咨询专业医生。"), advice_style))
        story.append(Paragraph(self._convert_text_if_needed("3. 建议定期生成并对比周报告，观察健康状况变化趋势。"), advice_style))
        
        # 页脚
        footer_style = ParagraphStyle(
            "Footer", 
            parent=normal_style,
            alignment=1,  # 居中
            fontSize=8,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph(self._convert_text_if_needed(f"健康生活应用生成 - {today.strftime('%Y-%m-%d %H:%M:%S')}"), footer_style))
        
        # 构建PDF
        doc.build(story)
        
        return filepath 