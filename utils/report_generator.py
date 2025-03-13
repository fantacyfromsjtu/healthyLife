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
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
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
        styles = getSampleStyleSheet()
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
        
        story.append(Paragraph("健康生活周报告", title_style))
        story.append(Paragraph(
            f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}",
            subtitle_style
        ))
        
        # 用户信息
        if self.user_info:
            user_info_data = [
                ["姓名", self.user_info.get("username", "")],
                ["性别", self.user_info.get("gender", "")],
                ["年龄", str(self.user_info.get("age", ""))],
                ["身高", f"{self.user_info.get('height', '')}厘米"],
                ["体重", f"{self.user_info.get('weight', '')}公斤"]
            ]
            
            user_table = Table(
                user_info_data, 
                colWidths=[2*cm, 5*cm],
                style=TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('PADDING', (0, 0), (-1, -1), 6)
                ])
            )
            
            story.append(Paragraph("个人信息", section_title_style))
            story.append(user_table)
            story.append(Spacer(1, 0.5*cm))
        
        # 总体健康建议
        story.append(Paragraph("本周健康总结", section_title_style))
        for advice in self.results.get("overall_advice", []):
            story.append(Paragraph(advice, advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 运动部分
        exercise_stats = self.results.get("exercise_stats", {})
        story.append(Paragraph("运动分析", section_title_style))
        
        # 运动数据统计
        exercise_data = [
            ["指标", "数值", "建议值", "达标情况"],
            ["运动天数", f"{exercise_stats.get('exercise_days', 0)}天", "≥3天/周", "✓" if exercise_stats.get('exercise_days', 0) >= 3 else "✗"],
            ["总运动时间", f"{exercise_stats.get('total_duration', 0)}分钟", "≥150分钟/周", "✓" if exercise_stats.get('meets_recommendation', False) else "✗"],
            ["平均每天运动", f"{exercise_stats.get('avg_duration_per_day', 0):.1f}分钟", "≥30分钟/天", "✓" if exercise_stats.get('avg_duration_per_day', 0) >= 30 else "✗"],
            ["总消耗卡路里", f"{exercise_stats.get('total_calories', 0)}卡路里", "-", "-"]
        ]
        
        exercise_table = Table(
            exercise_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(exercise_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 运动建议
        story.append(Paragraph("运动建议", subsection_title_style))
        for advice in self.results.get("exercise_advice", []):
            story.append(Paragraph(advice, advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 饮食部分
        diet_stats = self.results.get("diet_stats", {})
        story.append(Paragraph("饮食分析", section_title_style))
        
        # 饮食数据统计
        diet_data = [
            ["指标", "日均摄入", "推荐值", "达标比例"],
            ["总热量", f"{diet_stats.get('avg_calories_per_day', 0):.1f}卡路里", f"{diet_stats.get('recommended_calories', 0)}卡路里", f"{diet_stats.get('calories_percentage', 0):.1f}%"],
            ["蛋白质", f"{diet_stats.get('avg_protein_per_day', 0):.1f}克", f"{diet_stats.get('recommended_protein', 0)}克", f"{diet_stats.get('protein_percentage', 0):.1f}%"],
            ["脂肪", f"{diet_stats.get('avg_fat_per_day', 0):.1f}克", f"{diet_stats.get('recommended_fat', 0)}克", f"{diet_stats.get('fat_percentage', 0):.1f}%"],
            ["碳水化合物", f"{diet_stats.get('avg_carbs_per_day', 0):.1f}克", f"{diet_stats.get('recommended_carbs', 0)}克", f"{diet_stats.get('carbs_percentage', 0):.1f}%"]
        ]
        
        diet_table = Table(
            diet_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(diet_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 营养比例
        nutrition_ratio = [
            ["营养素", "占比", "推荐范围"],
            ["蛋白质", f"{diet_stats.get('protein_ratio', 0):.1f}%", "10-35%"],
            ["脂肪", f"{diet_stats.get('fat_ratio', 0):.1f}%", "20-35%"],
            ["碳水化合物", f"{diet_stats.get('carbs_ratio', 0):.1f}%", "45-65%"]
        ]
        
        nutrition_table = Table(
            nutrition_ratio, 
            colWidths=[4*cm, 3*cm, 4*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(Paragraph("营养素比例", subsection_title_style))
        story.append(nutrition_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 饮食建议
        story.append(Paragraph("饮食建议", subsection_title_style))
        for advice in self.results.get("diet_advice", []):
            story.append(Paragraph(advice, advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 睡眠部分
        sleep_stats = self.results.get("sleep_stats", {})
        story.append(Paragraph("睡眠分析", section_title_style))
        
        # 睡眠数据统计
        sleep_data = [
            ["指标", "数值", "建议值", "达标情况"],
            ["睡眠天数", f"{sleep_stats.get('sleep_days', 0)}天", f"{sleep_stats.get('total_days', 7)}天", "✓" if sleep_stats.get('sleep_days', 0) >= sleep_stats.get('total_days', 7) else "✗"],
            ["平均睡眠时长", f"{sleep_stats.get('avg_duration_per_day', 0) / 60:.1f}小时", f"{sleep_stats.get('recommended_sleep', 8)}小时", "✓" if sleep_stats.get('meets_recommendation', False) else "✗"],
            ["平均睡眠质量", f"{sleep_stats.get('avg_quality', 0):.1f}分", "≥3.5分", "✓" if sleep_stats.get('avg_quality', 0) >= 3.5 else "✗"]
        ]
        
        sleep_table = Table(
            sleep_data, 
            colWidths=[3*cm, 3*cm, 3*cm, 2*cm],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 6)
            ])
        )
        
        story.append(sleep_table)
        story.append(Spacer(1, 0.3*cm))
        
        # 睡眠建议
        story.append(Paragraph("睡眠建议", subsection_title_style))
        for advice in self.results.get("sleep_advice", []):
            story.append(Paragraph(advice, advice_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 注意事项
        story.append(Paragraph("温馨提示", section_title_style))
        story.append(Paragraph("1. 本报告基于您记录的数据生成，数据越完整分析越准确。", advice_style))
        story.append(Paragraph("2. 健康建议仅供参考，如有特殊健康问题请咨询专业医生。", advice_style))
        story.append(Paragraph("3. 建议定期生成并对比周报告，观察健康状况变化趋势。", advice_style))
        
        # 页脚
        footer_style = ParagraphStyle(
            "Footer", 
            parent=normal_style,
            alignment=1,  # 居中
            fontSize=8,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph(f"健康生活应用生成 - {today.strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        
        # 构建PDF
        doc.build(story)
        
        return filepath 