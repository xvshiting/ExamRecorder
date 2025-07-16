# GUI重构说明

## 重构目标

将原有的`gui`文件夹中的代码进行重构，实现清晰的职责分离和更好的可维护性。

## 重构架构

### 目录结构

```
refactory_gui/
├── controllers/                 # 控制器层
│   ├── event_handlers/         # 事件处理器
│   │   ├── chinese_input_handler.py
│   │   ├── input_handler.py
│   │   ├── recording_handler.py
│   │   └── webcam_handler.py
│   └── main_controller.py      # 主控制器
├── models/                     # 数据模型层
│   ├── data_collection_model.py
│   └── recording_model.py
├── services/                   # 服务层
│   ├── input/                 # 输入相关服务
│   │   └── keyboard_listener.py
│   ├── playback/              # 回放相关服务
│   │   └── video_player_service.py
│   └── recording/             # 录制相关服务
│       ├── screen_recorder.py
│       ├── webcam_manager.py
│       └── webcam_recorder.py
├── utils/                     # 工具类
│   ├── region_utils.py
│   └── styles.py
├── views/                     # 视图层
│   ├── components/            # 业务组件（含业务逻辑）
│   │   ├── timeline_widget.py
│   │   └── virtual_keyboard.py
│   └── pages/                # 页面视图
│       ├── main_view.py
│       └── playback_view.py
├── widgets/                   # 纯UI控件（无业务逻辑）
│   ├── control_buttons.py
│   ├── input_section.py
│   ├── question_display.py
│   ├── recording_control.py
│   ├── webcam_control.py
│   └── webcam_display.py
└── main_window.py            # 主窗口入口
```

### 架构说明

#### 1. 控制器层 (Controllers)
- **主控制器**: 负责协调各个组件和服务
- **事件处理器**: 专门处理特定类型的事件（输入、录制、webcam等）

#### 2. 服务层 (Services)
- **录制服务**: 屏幕录制、webcam录制等核心功能
- **输入服务**: 键盘监听、输入处理等
- **回放服务**: 视频播放、时间轴控制等

#### 3. 模型层 (Models)
- **数据采集模型**: 管理题目、按键记录等数据
- **录制模型**: 管理录制状态和配置

#### 4. 视图层 (Views)
- **页面视图**: 组合多个组件形成完整页面
- **业务组件**: 包含业务逻辑的组合控件

#### 5. 控件层 (Widgets)
- **纯UI控件**: 只负责界面显示，不包含业务逻辑

#### 6. 工具层 (Utils)
- **区域工具**: 屏幕区域计算等
- **样式工具**: UI样式定义

## 重构成果

### 1. 职责分离
- 将原本混杂在`playback_window.py`中的功能拆分到不同层次
- 每个文件都有明确的职责和边界

### 2. 代码复用
- 将通用UI控件提取到`widgets`层
- 将业务逻辑提取到`services`层

### 3. 可维护性提升
- 文件大小合理，单个文件不超过300行
- 依赖关系清晰，便于修改和扩展

### 4. 测试友好
- 各层之间通过接口交互，便于单元测试
- 业务逻辑与UI分离，便于测试

## 使用说明

### 启动应用
```python
from refactory_gui.main_window import MainWindow
# 启动主窗口
```

### 主要组件
- `MainController`: 主控制器，协调所有功能
- `DataCollectionModel`: 数据模型，管理录制数据
- `ScreenRecorder`: 屏幕录制服务
- `WebcamManager`: webcam管理服务
- `KeyboardListener`: 键盘监听服务

## 迁移指南

从原有`gui`文件夹迁移到重构版本：

1. 更新导入路径
2. 调整组件初始化顺序
3. 更新事件处理逻辑
4. 测试功能完整性

## 下一步计划

1. 完善错误处理和日志记录
2. 添加配置管理
3. 优化性能
4. 添加单元测试
5. 完善文档 