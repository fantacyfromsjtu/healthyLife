# healthyLife

长期舒适——一款更适合大学生的健康生活小程序

## 目标

实现一个大学生健康生活小程序，具体功能包括：

用户注册与登录

用户信息采集（性别，年龄，身高，体重，饮食习惯，运动习惯，睡眠习惯）
整体是一个日历的界面，每个日期点进去后可以编辑当天的：
一日三餐/零食摄入情况
每日运动情况
每日睡眠情况

预定锻炼/吃饭/睡觉功能，在预定时间提醒用户锻炼/吃饭/睡觉

生成每日/每周健康报告（智能分析？综合用户信息和每日表现包括吃饭，运动，睡觉三方面，给出建议）
报告导出pdf功能


## 运行方法

操作系统：Windows/Linux

环境配置

```bash
cd healthyLife
conda create -n healthy python=3.10
conda activate healthy
pip install -r requirements.txt
```

运行

```bash
python app.py
```