# examRecorder 数据采集与回放系统

## 项目简介

examRecorder 是一套用于考试/问卷/行为数据采集与回放的桌面端系统，支持屏幕录制、摄像头录制、键盘输入采集与同步回放。界面美观，交互流畅，适合科研、教育、行为分析等场景。

## 主要功能

- **数据采集**：
  - 屏幕录制、摄像头录制同步采集
  - 键盘输入实时记录
  - 题目展示与用户输入采集
  - 采集数据自动保存为JSON和视频文件

- **数据回放**：
  - 支持选择历史采集记录回放
  - 屏幕与摄像头视频同步播放
  - 时间轴缩略图、进度拖动、跳转、倍速播放
  - 联动/独立回放模式切换
  - 详细信息面板与虚拟键盘高亮

## 安装与运行

1. **环境准备**
   - Python 3.8+
   - 推荐使用虚拟环境

2. **依赖安装**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

## 界面演示

- **数据采集 Demo**

  <video src="docs/demo_collect.mp4" controls width="600"></video>

- **数据回放 Demo**

  <video src="docs/demo_replay.mp4" controls width="600"></video>

## 目录结构

```
examRecorder/
├── refactory_gui/         # 主程序代码
├── docs/                 # 文档与演示视频
│   ├── demo_collect.mp4
│   └── demo_replay.mp4
├── requirements.txt      # 依赖列表
├── README.md             # 项目说明
└── ...
```

## 联系方式

- 作者：Your Name
- 邮箱：your.email@example.com
- Issues/PR 欢迎提交！ 