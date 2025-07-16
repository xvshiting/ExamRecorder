# MVC 架构重构总结

## 重构目标

将原本承担过多功能的 `main_window.py` 按照 MVC（Model-View-Controller）架构进行重构，提高代码的可维护性、可扩展性和可测试性。

## 重构前后对比

### 重构前
- `main_window.py`: 560行，承担了UI构建、事件处理、业务逻辑、数据管理等多种职责
- 代码耦合度高，难以维护和扩展
- 单一文件承担过多功能

### 重构后
采用 MVC 架构，将功能分离到不同的模块：

## 新的文件结构

```
gui/
├── models/                          # 模型层 - 数据管理和业务逻辑
│   ├── __init__.py
│   ├── data_collection_model.py     # 数据采集模型
│   └── recording_model.py           # 录制管理模型
├── controllers/                     # 控制器层 - 协调Model和View
│   ├── __init__.py
│   └── main_controller.py           # 主控制器
├── ui_components.py                 # UI组件定义
├── ui_builder.py                    # UI构建器
├── event_handlers.py                # 事件处理器
├── region_utils.py                  # 区域获取工具
├── main_window.py                   # 主窗口（简化后）
└── ... (其他原有文件)
```

## 各层职责

### 1. Model（模型层）
**职责**: 数据管理和业务逻辑

#### `DataCollectionModel`
- 管理题目数据
- 管理按键记录
- 管理采集状态
- 数据保存功能

#### `RecordingModel`
- 管理屏幕录制
- 管理webcam录制
- 录制状态控制
- 录制器生命周期管理

### 2. View（视图层）
**职责**: UI显示和用户交互

#### `ui_components.py`
- `QuestionDisplayWidget`: 题目显示组件
- `InputSectionWidget`: 输入区域组件
- `ControlButtonsWidget`: 控制按钮组件
- `WebcamControlWidget`: 摄像头控制组件
- `RecordingControlWidget`: 录制控制组件
- `WebcamDisplayWidget`: 摄像头显示组件

#### `ui_builder.py`
- `MainWindowUIBuilder`: 负责组装和布局所有UI组件

### 3. Controller（控制器层）
**职责**: 处理用户交互，协调Model和View

#### `MainController`
- 初始化Model和View
- 处理用户事件
- 协调数据流
- 管理应用状态

#### `event_handlers.py`
- `WebcamEventHandler`: 处理摄像头相关事件
- `RecordingEventHandler`: 处理录制相关事件
- `InputEventHandler`: 处理输入相关事件

## 重构优势

### 1. 职责分离
- **Model**: 专注于数据管理和业务逻辑
- **View**: 专注于UI显示
- **Controller**: 专注于用户交互和协调

### 2. 可维护性提升
- 代码结构清晰，易于理解
- 各模块职责单一，修改影响范围小
- 便于定位和修复问题

### 3. 可扩展性增强
- 新增功能时只需修改相应层
- 可以轻松添加新的UI组件
- 可以轻松添加新的业务逻辑

### 4. 可测试性改善
- Model层可以独立测试
- Controller层可以独立测试
- View层可以独立测试

### 5. 代码复用
- UI组件可以在其他地方复用
- 业务逻辑可以在其他地方复用
- 工具类可以在其他地方复用

## 重构后的代码行数对比

| 文件 | 重构前行数 | 重构后行数 | 说明 |
|------|------------|------------|------|
| main_window.py | 560 | 14 | 大幅简化，只保留基本窗口设置 |
| ui_components.py | - | 226 | 新增，UI组件定义 |
| ui_builder.py | - | 92 | 新增，UI构建器 |
| event_handlers.py | - | 174 | 新增，事件处理器 |
| region_utils.py | - | 40 | 新增，工具类 |
| data_collection_model.py | - | 95 | 新增，数据模型 |
| recording_model.py | - | 85 | 新增，录制模型 |
| main_controller.py | - | 280 | 新增，主控制器 |

## 使用方式

重构后的使用方式保持不变：

```python
from gui.main_window import MainWindow

window = MainWindow()
window.show()
```

## 总结

通过 MVC 架构重构，我们成功地将原本臃肿的 `main_window.py` 分解为多个职责明确的模块。这样的架构使得代码更加清晰、可维护、可扩展，为后续的功能开发和维护奠定了良好的基础。 