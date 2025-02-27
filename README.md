# healthyLife
项目管理小作业

大学生健康生活小程序（使用python语言，需要给出图形化界面。桌面端使用）

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
报告导出pdf功能？（绑定微信，一键分享等，这个功能后面再实现）


healthyLife/
│
├── main.py                 # 程序入口
├── database/
│   ├── __init__.py
│   ├── db_manager.py       # 数据库管理
│   └── models.py           # 数据模型
│
├── ui/
│   ├── __init__.py
│   ├── login.py            # 登录/注册界面
│   ├── main_window.py      # 主窗口(日历视图)
│   ├── profile.py          # 用户信息界面
│   ├── daily_entry.py      # 每日记录界面
│   ├── schedule.py         # 计划安排界面
│   └── report.py           # 健康报告界面
│
├── utils/
│   ├── __init__.py
│   ├── reminder.py         # 提醒功能
│   ├── analyzer.py         # 数据分析
│   └── report_generator.py # 报告生成
│
└── resources/
    ├── icons/              # 图标
    ├── styles/             # 样式表
    └── templates/          # 报告模板