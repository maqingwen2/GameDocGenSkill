# GameDocGenSkill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🕵️‍♂️ 游戏策划的「像素级模仿大师」
>
> 看到别家游戏的好玩法？截图丢给我，分分钟给你仿写一份专业策划案！
> 从竞品视频到策划文档，只需三步：截图 → 分析 → 产出。像学霸抄作业一样高效，像福尔摩斯破案一样细致 🔍
>
> *我们不做原创，我们是游戏设计的「高级复读机」*

---

## 📖 项目简介

GameDocGenSkill 是一款专注于「像素级模仿」的智能工具。它像一位经验丰富的策划老手，只需要你丢给它几张竞品截图或一段演示视频，就能自动「仿写」出一份结构完整、术语专业的策划案。

核心思路很简单：**先模仿，再创新**。不用从零开始写文档，让 AI 先帮你把竞品的框架扒下来，你再在此基础上优化迭代。

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

## 🤖 作为 AI Agent Skill 使用

本项目可以作为 **AI Agent Skill** 集成到各类 AI 助手平台（如 WorkBuddy、CodeBuddy 等），实现一键式游戏策划案生成。

### Skill 安装方式

#### 方式一：用户级安装（推荐）

将本 Skill 安装到用户目录，所有项目均可使用：

```bash
# 复制到用户 Skill 目录
mkdir -p ~/.workbuddy/skills/game-imitation-designer/
cp -r GameDocGenSkill/* ~/.workbuddy/skills/game-imitation-designer/
```

#### 方式二：项目级安装

仅当前项目可用：

```bash
# 复制到项目 .workbuddy/skills/ 目录
mkdir -p .workbuddy/skills/game-imitation-designer/
cp -r GameDocGenSkill/* .workbuddy/skills/game-imitation-designer/
```

### 输入目录规范

使用 Skill 时需按以下结构准备输入文件：

```
project-root/
├── input/                      # 输入素材目录（必须）
│   ├── screenshots/            # 游戏截图（推荐）
│   │   ├── main_ui.png
│   │   ├── battle_scene.png
│   │   └── reward_popup.png
│   └── video/                  # 游戏视频（可选）
│       └── gameplay_demo.mp4
│
├── templates/                  # 策划案模板目录（必须）
│   ├── 【Release】xxx.xlsx    # Release版本策划案模板
│   └── 【策划案】xxx.xlsx     # 常规策划案模板
│
├── output/                     # 输出目录（自动生成）
│   └── 功能名称策划案/
│       ├── README.md
│       ├── 主界面.md
│       └── images/
│
└── work/                       # 工作目录（自动生成）
    ├── template_profile.json
    ├── screenshots_index.json
    └── analysis_results.json
```

### 在 OpenClaw 中使用

#### 触发词

在 OpenClaw 中，使用以下关键词触发本 Skill：

- `游戏策划案生成`
- `根据截图写策划案`
- `分析游戏视频生成策划案`
- `仿写策划案`
- `游戏功能拆解`
- `像素级模仿`

#### 使用示例

**示例 1：基础使用**

> 用户：根据我放在 input 目录下的截图，帮我写一份活动策划案

OpenClaw 会自动：
1. 扫描 `templates/` 目录解析策划案模板
2. 分析 `input/screenshots/` 下的截图
3. 生成标准化 Markdown 策划案到 `output/` 目录

**示例 2：指定模板**

> 用户：参考 Release 版本的模板格式，分析 input/video/demo.mp4 生成策划案

**示例 3：完整流程**

> 用户：我上传了一个新游戏的录屏和几张关键界面截图，帮我仿写一份完整的策划案，参考我 templates 目录下的历史模板

### 在 CodeBuddy 中使用

```typescript
// 在 Agent 配置中使用本 Skill
import { loadSkill } from '@tencent-ai/agent-sdk';

const gameDesignSkill = await loadSkill('game-imitation-designer');

// 执行策划案生成
const result = await gameDesignSkill.execute({
  inputDir: './input',
  templatesDir: './templates',
  outputDir: './output',
  options: {
    extractKeyframes: true,      // 从视频提取关键帧
    deduplicateScreenshots: true, // 截图去重
    mergeTemplates: true,        // 合并多模板
  }
});

console.log(`已生成策划案: ${result.outputPath}`);
```

### 在其他 AI Agent 平台使用

#### 通用集成方式

1. **准备环境**
   ```bash
   pip install pillow pandas openpyxl python-docx imagehash
   # 如需视频处理：安装 FFmpeg
   ```

2. **调用脚本**
   ```python
   # 完整流水线
   from scripts.template_parser import parse_templates, merge_profiles
   from scripts.video_processor import extract_keyframes, copy_screenshots
   from scripts.game_analyzer import generate_design_docs
   from scripts.utils import ensure_dir, write_json
   import os

   # 准备目录
   INPUT_DIR = "input"
   TEMPLATES_DIR = "templates"
   OUTPUT_DIR = "output"
   WORK_DIR = "work"

   ensure_dir(WORK_DIR)
   ensure_dir(OUTPUT_DIR)

   # Phase 1: 预处理
   profiles = parse_templates(TEMPLATES_DIR)
   merged = merge_profiles(profiles)
   write_json(merged.to_dict(), f"{WORK_DIR}/template_profile.json")

   # 处理视频截图
   frames = []
   video_dir = os.path.join(INPUT_DIR, "video")
   if os.path.exists(video_dir):
       for video in os.listdir(video_dir):
           if video.endswith(('.mp4', '.mov', '.avi')):
               frames.extend(extract_keyframes(
                   os.path.join(video_dir, video),
                   f"{WORK_DIR}/screenshots/"
               ))

   # 复制用户截图
   screenshot_dir = os.path.join(INPUT_DIR, "screenshots")
   if os.path.exists(screenshot_dir):
       frames.extend(copy_screenshots(screenshot_dir, f"{WORK_DIR}/screenshots/"))

   write_json({"screenshots": [f.path for f in frames]}, f"{WORK_DIR}/screenshots_index.json")

   # Phase 2: 视觉分析（由 AI Agent 完成）
   # Agent 读取截图，输出 analysis_results.json

   # Phase 3: 文档生成
   generated = generate_design_docs(
       template_profile_path=f"{WORK_DIR}/template_profile.json",
       analysis_results_path=f"{WORK_DIR}/analysis_results.json",
       output_dir=OUTPUT_DIR,
   )
   ```

### Skill 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `inputDir` | string | `"input"` | 输入素材目录 |
| `templatesDir` | string | `"templates"` | 模板文件目录 |
| `outputDir` | string | `"output"` | 输出策划案目录 |
| `workDir` | string | `"work"` | 中间文件工作目录 |
| `extractKeyframes` | boolean | `true` | 是否从视频提取关键帧 |
| `sceneThreshold` | float | `0.3` | 场景变化敏感度 |
| `maxFrames` | int | `50` | 每视频最大提取帧数 |
| `deduplicateScreenshots` | boolean | `true` | 是否对截图去重 |
| `mergeTemplates` | boolean | `true` | 是否合并多模板结构 |

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

---

<p align="center">Made with ❤️ for Game Designers</p>
