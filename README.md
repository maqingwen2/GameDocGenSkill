# GameDocGenSkill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎮 基于视觉分析的游戏策划案自动生成工具
> 
> 分析目标游戏素材（视频/截图），结合策划案模板，自动生成标准化的功能策划文档

---

## 📖 项目简介

GameDocGenSkill 是一个面向游戏策划的自动化工具，通过三阶段混合流水线（Python 预处理 + 多模态视觉分析 + 文档生成），帮助策划人员快速从游戏素材中提取功能设计并生成标准化的策划案文档。

### 核心能力

- 🔍 **视觉分析**：自动分析游戏截图/视频，识别 UI 布局、交互流程、功能模块
- 📝 **模板融合**：支持多格式策划案模板（Excel/Word/Markdown），提取通用结构
- 📄 **文档生成**：输出符合行业标准的专业策划案（Markdown 格式）
- 🖼️ **图片整理**：自动整理相关截图，按模块分类归档

### 适用场景

- 竞品分析：快速拆解对标游戏的功能设计
- 功能还原：根据截图/视频还原已下线活动的策划案
- 文档标准化：统一团队策划案输出格式
- 外包对接：生成带截图参考的详细功能说明

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（视频处理，可选）
- 依赖包：`pillow`, `pandas`, `openpyxl`, `python-docx`, `imagehash`

### 安装依赖

```bash
pip install pillow pandas openpyxl python-docx imagehash
```

### FFmpeg 安装（可选，用于视频处理）

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 下载地址：https://ffmpeg.org/download.html
```

### 基本用法

```python
from scripts.template_parser import parse_templates, merge_profiles
from scripts.video_processor import extract_keyframes, copy_screenshots
from scripts.game_analyzer import generate_design_docs
from scripts.utils import ensure_dir, write_json

# 1. 解析模板
profiles = parse_templates("templates/")
merged = merge_profiles(profiles)
write_json(merged.to_dict(), "work/template_profile.json")

# 2. 处理视频和截图
frames = extract_keyframes("input/gameplay.mp4", "work/screenshots/")
write_json({"screenshots": [f.path for f in frames]}, "work/screenshots_index.json")

# 3. 生成策划案（视觉分析由 Agent 完成）
generated = generate_design_docs(
    template_profile_path="work/template_profile.json",
    analysis_results_path="work/analysis_results.json",
    output_dir="output/策划案/",
)
print(f"已生成 {len(generated)} 份策划文档")
```

---

## 📁 项目结构

```
game-imitation-designer/
├── README.md                      # 项目说明
├── SKILL.md                       # Skill 定义文件
├── scripts/                       # Python 脚本
│   ├── template_parser.py         # 模板解析器（Excel/Word/Markdown）
│   ├── video_processor.py         # 视频处理与截图去重
│   ├── game_analyzer.py           # 策划案生成引擎
│   └── utils.py                   # 通用工具函数
├── references/                    # 参考文档
│   ├── analysis_prompts.md        # 视觉分析提示词模板
│   └── module_classification.md   # 功能模块分类指南
└── examples/                      # 示例（可选）
    ├── templates/                 # 示例模板
    └── output/                    # 示例输出
```

---

## 🔄 工作流程

### 三阶段流水线

```
┌─────────────────────────────────────────────────────────────────┐
│                         Phase 1: 预处理                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ 解析模板      │ →  │ 提取视频帧    │ →  │ 整理截图      │       │
│  │ (.xlsx/.md)  │    │ (ffmpeg)     │    │ (去重/索引)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         ↓                  ↓                  ↓                  │
│  template_profile.json  screenshots/    screenshots_index.json   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Phase 2: 视觉分析                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 多模态模型分析                           │    │
│  │  • 识别功能模块    • 提取 UI 布局                        │    │
│  │  • 记录可见文本    • 标注交互控件                        │    │
│  │  • 收集数值信息    • 标记待确认项                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│                    analysis_results.json                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Phase 3: 文档生成                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              融合模板 + 分析结果 → Markdown              │    │
│  │  • 模块结构      • 界面布局      • 交互流程              │    │
│  │  • 详细逻辑      • 文案文本      • 数值信息              │    │
│  │  • 控件说明      • 配置表引用    • 待确认项              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│              输出目录：模块名.md + images/模块名/                 │
└─────────────────────────────────────────────────────────────────┘
```

### 输入规范

#### 模板目录 (`templates/`)

支持以下格式的策划案模板：

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Excel | `.xlsx`, `.xlsm` | 最常用，支持多工作表 |
| Word | `.doc`, `.docx` | 传统文档格式 |
| Markdown | `.md`, `.markdown` | 轻量格式 |

模板文件命名建议：
- `【Release】功能名称.xlsx` — Release 版本策划案
- `【策划案】功能名称.xlsx` — 常规策划案

#### 素材目录 (`input/`)

```
input/
├── video/                    # 游戏视频（可选）
│   └── gameplay.mp4
└── screenshots/              # 游戏截图（推荐）
    ├── main_ui.png
    ├── battle.png
    └── shop.png
```

### 输出结构

```
output/
└── 功能名称策划案/
    ├── README.md                    # 总索引
    ├── 主界面.md                    # 模块策划案
    ├── 核心玩法.md
    ├── 排行榜.md
    ├── ...
    └── images/                      # 引用截图
        ├── 主界面/
        │   ├── screenshot_000.png
        │   └── screenshot_001.png
        ├── 核心玩法/
        └── ...
```

---

## 🛠️ 模块详解

### 1. Template Parser (`template_parser.py`)

解析策划案模板，提取结构化信息。

```python
from scripts.template_parser import parse_templates, merge_profiles

# 解析目录下所有模板
profiles = parse_templates("templates/")

# 合并多模板，提取通用结构
merged = merge_profiles(profiles)

# 提取的信息
print(f"模块目录: {merged.module_catalog}")
print(f"注意事项: {merged.notices}")
print(f"配置表引用: {merged.config_refs}")
print(f"术语表: {merged.terminology}")
```

**支持的解析内容（Excel 模板）**：

- 工作表结构识别（`2-3.详细逻辑设计`、`2-2.系统效果图`、`5.配置档需求`）
- 功能模块划分（层级编号：1, 1.1, 1.1.1）
- 标准注意事项提取
- 配置表引用（`【TableName】` 格式）

### 2. Video Processor (`video_processor.py`)

视频关键帧提取与截图去重。

```python
from scripts.video_processor import (
    extract_keyframes,
    deduplicate_frames,
    copy_screenshots,
    create_screenshots_index,
)

# 从视频提取关键帧
frames = extract_keyframes(
    video_path="input/gameplay.mp4",
    output_dir="work/screenshots/",
    scene_threshold=0.3,      # 场景变化敏感度
    max_frames=50,            # 每视频最大帧数
    min_interval=1.0,         # 最小帧间隔（秒）
)

# 复制用户提供的截图
user_frames = copy_screenshots("input/screenshots/", "work/screenshots/")

# 去重
unique_frames = deduplicate_frames(frames + user_frames, threshold=5)

# 生成索引
create_screenshots_index(unique_frames, "work/screenshots_index.json")
```

### 3. Game Analyzer (`game_analyzer.py`)

融合模板结构与视觉分析结果，生成最终策划案。

```python
from scripts.game_analyzer import generate_design_docs

generated = generate_design_docs(
    template_profile_path="work/template_profile.json",
    analysis_results_path="work/analysis_results.json",
    output_dir="output/策划案/",
)

for path in generated:
    print(f"已生成: {path}")
```

---

## 📋 文档格式标准

### 生成的策划案结构

```markdown
# 模块名称 — 功能策划案

> 生成时间: YYYY-MM-DD HH:MM

## 注意事项
- 界面说明需要精确到每一个按钮点击后是什么效果...
- 逻辑设计结合UI设计检查是否有潜规则...

## ●模块名称 概述
功能概述描述...

### 界面布局
界面整体布局描述：有哪些区域、分区名称、排列方式

#### 界面截图
![主界面](images/模块名/screenshot_000.png)

### 交互流程
从当前界面出发，玩家可以进行哪些操作...

### 详细逻辑
1. 进入条件检查规则...
2. 点击按钮后的处理逻辑...

### 文案与文本
- 活动标题：魔女之夜
- 按钮文字：开始挑战

### 数值信息
- **单次消耗**: 1 个魔力水晶
- **活动持续时间**: 3 天

### 按钮与控件
- **开始挑战**: 点击进入玩法界面
- **排行榜**: 打开排行榜面板

### 【需补充】待确认项
- 【需补充】活动解锁条件未在截图中展示
```

### 专业术语规范

| 术语 | 说明 |
|------|------|
| 解锁条件 | 活动/功能开启的前置要求 |
| 玩法时间 | 活动可参与的时间段 |
| 领奖时间 | 活动结束后可领取奖励的时间段 |
| 配置表 | 策划提供给程序的数据表格 |
| 【需补充】 | 无法从截图确认的信息标记 |

---

## 🔧 扩展开发

### 添加新模板格式支持

在 `template_parser.py` 中实现新的解析器：

```python
class CustomParser(TemplateParser):
    SUPPORTED_EXTS = [".custom"]

    def parse(self, file_path: str) -> TemplateProfile:
        profile = TemplateProfile(file_path, doc_type="custom")
        # 实现解析逻辑
        return profile

# 注册解析器
TemplateParserRegistry.register(CustomParser)
```

### 自定义视觉分析提示词

编辑 `references/analysis_prompts.md` 调整分析策略：
- 修改模块识别特征
- 调整输出 JSON 结构
- 定制专业术语库

### 调整视频处理参数

修改 `video_processor.py` 中的默认参数：

```python
# 提高场景敏感度，提取更多帧
scene_threshold=0.2

# 增加单视频最大帧数
max_frames=100

# 降低最小帧间隔
min_interval=0.5
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

### 开发流程

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/awesome-feature`
3. 提交变更：`git commit -m 'Add awesome feature'`
4. 推送分支：`git push origin feature/awesome-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 风格
- 所有函数添加 docstring
- 新功能需附带测试用例

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- 感谢 WorkBuddy 平台提供的多模态分析能力
- 感谢游戏策划行业贡献的标准文档模板

---

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [GitHub Issue](../../issues)
- 发送邮件至：your.email@example.com

---

<p align="center">Made with ❤️ for Game Designers</p>
