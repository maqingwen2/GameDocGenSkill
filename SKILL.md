---
name: game-imitation-designer
description: "This skill should be used when the user needs to analyze a target game's videos and screenshots against existing game design document templates, then automatically generate standardized, production-ready game feature design documents in Markdown format. Trigger when the user mentions: game design document generation, 游戏策划案生成, 模仿游戏写策划, 根据视频生成策划案, game feature analysis from screenshots, 游戏功能拆解, UI analysis for game design, 自动策划案, or when providing game video files + design templates. Also trigger when the user wants to reverse-engineer game features from visual materials into professional Chinese game design documents following industry-standard formats."
---

# GameDocGenSkill — 游戏策划案生成工具

## Overview

Analyze target game materials (videos + screenshots) against multiple game design document templates,
then generate standardized, production-ready game feature design documents in Markdown format with
organized image folders.

This skill operates in a three-phase hybrid pipeline: Python scripts handle deterministic automation
(parsing, preprocessing, assembly), while the platform's built-in multimodal model handles visual
understanding through a structured workflow.

## Workflow Decision Tree

```
User provides:
├── Template directory (.docx/.xlsx/.md files)
├── Video files + Screenshot directory
└── Optional: target functional modules to generate

Phase 1: Preprocessing (Python scripts)
├── Parse all templates → template_profile.json
├── Extract keyframes from videos → screenshots/
├── Copy and deduplicate screenshots
└── Generate screenshots_index.json

Phase 2: Visual Analysis (Agent multimodal)
├── Load analysis_prompts.md and module_classification.md
├── Read screenshots_index.json
├── Analyze each screenshot group using vision capabilities
├── Write structured results → analysis_results.json

Phase 3: Document Generation (Python scripts)
├── Merge template_profile.json + analysis_results.json
├── Generate one .md per functional module
├── Copy referenced images to images/ folder
└── Output: Markdown docs + images/
```

## Phase 1: Preprocessing

### Step 1.1: Parse Templates

Run `scripts/template_parser.py` to extract template structures:

```python
from scripts.template_parser import parse_templates, merge_profiles
from scripts.utils import write_json

profiles = parse_templates("<template_dir>")
merged = merge_profiles(profiles)
write_json(merged.to_dict(), "<work_dir>/template_profile.json")
```

The parser supports `.xlsx`, `.docx`, and `.md` formats with an extensible plugin architecture.
For `.xlsx` templates (common in Chinese game design), it extracts:
- Sheet structures (e.g., `2-3.详细逻辑设计`, `2-2.系统效果图`, `5.配置档需求`)
- Module catalogs with hierarchical numbering (1, 1.1, 1.1.1)
- Standard notices (注意事项)
- Config table references (e.g., `【SystemUnlockDB】`)

### Step 1.2: Process Video and Screenshots

Run `scripts/video_processor.py` to prepare visual assets:

```python
from scripts.video_processor import extract_keyframes, deduplicate_frames, copy_screenshots, create_screenshots_index
from scripts.utils import ensure_dir

work_dir = "<work_dir>"
screenshots_dir = ensure_dir(f"{work_dir}/screenshots")

# Extract keyframes from videos
all_frames = []
for video_path in video_files:
    frames = extract_keyframes(video_path, str(screenshots_dir), max_frames=50)
    all_frames.extend(frames)

# Copy user-provided screenshots
user_frames = copy_screenshots("<screenshot_dir>", str(screenshots_dir))
all_frames.extend(user_frames)

# Deduplicate
unique_frames = deduplicate_frames(all_frames, threshold=5)

# Create index for Phase 2
create_screenshots_index(unique_frames, f"{work_dir}/screenshots_index.json")
```

Key parameters:
- `scene_threshold=0.3`: Scene change sensitivity (lower = more frames)
- `max_frames=50`: Per-video frame limit
- `min_interval=1.0`: Minimum seconds between keyframes

### Step 1.3: Checkpoint

Verify these files exist before proceeding to Phase 2:
- `<work_dir>/template_profile.json`
- `<work_dir>/screenshots_index.json`
- `<work_dir>/screenshots/` (contains extracted frames)

## Phase 2: Multimodal Visual Analysis

### Step 2.1: Load Reference Materials

Load into context:
- `references/analysis_prompts.md` — multimodal analysis prompt templates
- `references/module_classification.md` — functional module classification guide

### Step 2.2: Analyze Screenshots

For each screenshot group in `screenshots_index.json`, perform multimodal analysis:

1. Read the screenshot image using available vision tools
2. Apply the analysis framework from `references/analysis_prompts.md`
3. For each frame, extract:
   - Detected functional modules
   - UI layout description
   - All visible text/copy
   - Controls (buttons, tabs, inputs) with positions and actions
   - Numeric information (scores, currencies, levels)
   - Interaction flows
   - Uncertain areas marked with 【需补充】

4. Aggregate per-frame results into module-level summaries following
   the JSON schema in `references/analysis_prompts.md`

### Step 2.3: Write Analysis Results

Compile all analysis into a single structured JSON file:

```json
{
  "analysis_metadata": {
    "total_frames": 42,
    "total_modules_detected": 6,
    "analyzed_at": "2026-04-21T10:00:00"
  },
  "modules": {
    "主界面": {
      "overview": "活动入口主界面，展示活动标题、背景图和主要功能按钮",
      "ui_layout": "顶部为活动标题和倒计时，中央为背景图和开始按钮，底部为排行榜、规则、商店入口",
      "interaction_flow": "点击开始按钮 → 进入玩法界面；点击排行榜 → 打开排行面板；点击规则 → 打开规则弹窗",
      "detailed_logic": "【需补充】进入条件检查规则待补充",
      "visible_text": ["活动标题", "剩余时间: 3天12小时", "开始挑战"],
      "numeric_info": {"倒计时": "3天12小时"},
      "controls": [
        {"name": "开始挑战", "action": "进入玩法界面"},
        {"name": "排行榜", "action": "打开排行榜面板"}
      ],
      "screenshots": ["screenshots/video_frame_0001_0.00s.png"],
      "uncertain_areas": ["【需补充】活动解锁条件未在截图中展示"]
    }
  }
}
```

Save to `<work_dir>/analysis_results.json`.

## Phase 3: Document Generation

### Step 3.1: Generate Markdown Documents

Run `scripts/game_analyzer.py` to produce final deliverables:

```python
from scripts.game_analyzer import generate_design_docs

generated = generate_design_docs(
    template_profile_path="<work_dir>/template_profile.json",
    analysis_results_path="<work_dir>/analysis_results.json",
    output_dir="<output_dir>",
)
print(f"Generated {len(generated)} documents:")
for path in generated:
    print(f"  - {path}")
```

Output structure:
```
<output_dir>/
├── 主界面.md
├── 玩法界面.md
├── 排行榜.md
├── ...
└── images/
    ├── 主界面/
    │   ├── screenshot_000.png
    │   └── screenshot_001.png
    ├── 玩法界面/
    │   └── ...
```

### Step 3.2: Quality Check

For each generated Markdown document, verify:
- [ ] Document starts with `# 模块名称 — 功能策划案`
- [ ] Contains 注意事项 section (from template)
- [ ] Each section has content or 【需补充】 marker
- [ ] No fabricated information — all descriptions traceable to screenshots
- [ ] Image references use relative paths: `images/模块名/screenshot_XXX.png`
- [ ] Professional terminology used throughout (no colloquial language)

## Formatting Standards

### Document Structure

Generated documents follow this standard structure:

```markdown
# [模块名称] — 功能策划案

> 生成时间: YYYY-MM-DD HH:MM

## 注意事项
- [从模板提取的标准注意事项]

## ●[模块名称] 概述
[功能概述]

### 界面布局
[UI layout description]

#### 界面截图
![描述](images/模块名/screenshot_000.png)

### 交互流程
[Interaction flow]

### 详细逻辑
[Detailed logic rules]

### 文案与文本
- [Visible text items]

### 数值信息
- **键**: 值

### 按钮与控件
- **控件名**: 点击效果

### 【需补充】待确认项
- [Uncertain items]

### 关联配置表
- [Config table references from template]
```

### Heading Conventions

- Primary sections: `## ●模块名 概述`
- Subsections: `### 界面布局`, `### 交互流程`
- Module numbering follows template convention (1, 1.1, 1.1.1)

### Professional Language Requirements

- Use industry-standard game design terminology
- Avoid colloquial expressions (e.g., replace "玩家点一下" with "玩家点击后")
- Use precise descriptions: "界面顶部居中显示活动标题" instead of "上面有个标题"
- Mark all unverifiable information with `【需补充】`

## Resources

### scripts/

- `template_parser.py` — Multi-format template parser (Excel/Word/Markdown)
- `video_processor.py` — Video keyframe extraction and screenshot deduplication
- `game_analyzer.py` — Document generator merging templates + analysis results
- `utils.py` — Common utilities (JSON I/O, path helpers, file collection)

### references/

- `analysis_prompts.md` — Multimodal analysis prompt templates and JSON schema
- `module_classification.md` — Functional module classification guide and numbering rules

## Extending This Skill

### Adding New Template Formats

Implement a new parser class inheriting from `TemplateParser` in `scripts/template_parser.py`:

```python
class NewFormatParser(TemplateParser):
    SUPPORTED_EXTS = [".newfmt"]

    def parse(self, file_path: str) -> TemplateProfile:
        # Implementation
        ...
```

Then register it:
```python
TemplateParserRegistry.register(NewFormatParser)
```

### Customizing Analysis Prompts

Edit `references/analysis_prompts.md` to adjust:
- Analysis granularity
- Module detection criteria
- Output JSON schema
- Language and terminology preferences

### Adjusting Video Processing

Modify parameters in `scripts/video_processor.py`:
- `scene_threshold`: Increase for more frames, decrease for fewer
- `max_frames`: Adjust based on video length and analysis depth needs
- `min_interval`: Prevent excessive similar frames
