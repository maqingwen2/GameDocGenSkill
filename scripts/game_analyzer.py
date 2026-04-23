"""Merge template profile + visual analysis results into standardized Markdown design documents."""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .template_parser import TemplateProfile
    from .utils import ensure_dir, read_json, sanitize_filename, write_json
except ImportError:
    from template_parser import TemplateProfile
    from utils import ensure_dir, read_json, sanitize_filename, write_json


class DesignDocGenerator:
    """Generates game design documents from template profile and analysis results."""

    def __init__(
        self,
        template_profile: TemplateProfile,
        analysis_results: Dict[str, Any],
        output_dir: str,
    ):
        self.profile = template_profile
        self.analysis = analysis_results
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        ensure_dir(str(self.images_dir))

    def generate_all(self) -> List[str]:
        """Generate one design document per detected functional module.

        Returns list of generated file paths.
        """
        generated = []
        modules = self.analysis.get("modules", {})

        if not modules:
            # Fallback: generate a single document with all analysis
            doc_path = self._generate_single_doc("design_doc")
            generated.append(doc_path)
            return generated

        for module_name, module_data in modules.items():
            doc_path = self._generate_module_doc(module_name, module_data)
            generated.append(doc_path)

        return generated

    def _generate_module_doc(self, module_name: str, module_data: Dict[str, Any]) -> str:
        """Generate a design document for a single functional module."""
        safe_name = sanitize_filename(module_name)
        doc_path = self.output_dir / f"{safe_name}.md"
        mod_images_dir = self.images_dir / safe_name
        ensure_dir(str(mod_images_dir))

        lines = []

        # Title
        lines.append(f"# {module_name} — 功能策划案")
        lines.append("")
        lines.append(f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Template notices
        if self.profile.notices:
            lines.append("## 注意事项")
            lines.append("")
            for notice in self.profile.notices[:4]:
                lines.append(f"- {notice}")
            lines.append("")

        # Module overview
        lines.append(f"## ●{module_name} 概述")
        lines.append("")
        overview = module_data.get("overview", module_data.get("ui_layout", ""))
        if overview:
            lines.append(overview)
        else:
            lines.append("【需补充】功能概述待补充")
        lines.append("")

        # UI Layout
        lines.append("### 界面布局")
        lines.append("")
        ui_layout = module_data.get("ui_layout", "")
        if ui_layout:
            lines.append(ui_layout)
        else:
            lines.append("【需补充】界面布局描述待补充")
        lines.append("")

        # Screenshots
        screenshot_refs = module_data.get("screenshots", [])
        if screenshot_refs:
            lines.append("#### 界面截图")
            lines.append("")
            for idx, ref in enumerate(screenshot_refs):
                copied = self._copy_screenshot(ref, mod_images_dir, idx)
                if copied:
                    rel_path = f"images/{safe_name}/{copied.name}"
                    lines.append(f"![{module_name} 截图{idx+1}]({rel_path})")
                    lines.append("")

        # Interaction Flow
        lines.append("### 交互流程")
        lines.append("")
        flow = module_data.get("interaction_flow", "")
        if flow:
            lines.append(flow)
        else:
            lines.append("【需补充】交互流程待补充")
        lines.append("")

        # Detailed Logic
        lines.append("### 详细逻辑")
        lines.append("")
        logic = module_data.get("detailed_logic", "")
        if logic:
            lines.append(logic)
        else:
            lines.append("【需补充】详细逻辑待补充")
        lines.append("")

        # Visible Text / Copy
        visible_text = module_data.get("visible_text", [])
        if visible_text:
            lines.append("### 文案与文本")
            lines.append("")
            for text in visible_text:
                lines.append(f"- {text}")
            lines.append("")

        # Numeric Info
        numeric = module_data.get("numeric_info", {})
        if numeric:
            lines.append("### 数值信息")
            lines.append("")
            for key, value in numeric.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        # Buttons / Controls
        controls = module_data.get("controls", [])
        if controls:
            lines.append("### 按钮与控件")
            lines.append("")
            for ctrl in controls:
                name = ctrl.get("name", "未命名")
                action = ctrl.get("action", "")
                lines.append(f"- **{name}**: {action if action else '【需补充】点击效果待补充'}")
            lines.append("")

        # Uncertain areas
        uncertain = module_data.get("uncertain_areas", [])
        if uncertain:
            lines.append("### 【需补充】待确认项")
            lines.append("")
            for item in uncertain:
                lines.append(f"- {item}")
            lines.append("")

        # Config references (from template)
        if self.profile.config_refs:
            lines.append("### 关联配置表")
            lines.append("")
            for ref in self.profile.config_refs[:10]:
                lines.append(f"- {ref}")
            lines.append("")

        # Write document
        content = "\n".join(lines)
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(doc_path)

    def _generate_single_doc(self, doc_name: str) -> str:
        """Generate a single document when no modules are detected."""
        doc_path = self.output_dir / f"{doc_name}.md"
        lines = []

        lines.append("# 游戏功能策划案")
        lines.append("")
        lines.append(f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        if self.profile.notices:
            lines.append("## 注意事项")
            lines.append("")
            for notice in self.profile.notices[:4]:
                lines.append(f"- {notice}")
            lines.append("")

        raw_analysis = json.dumps(self.analysis, ensure_ascii=False, indent=2)
        lines.append("## 原始分析结果")
        lines.append("")
        lines.append("```json")
        lines.append(raw_analysis)
        lines.append("```")
        lines.append("")

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(doc_path)

    def _copy_screenshot(self, ref: str, dest_dir: Path, idx: int) -> Optional[Path]:
        """Copy screenshot to destination directory."""
        src = Path(ref)
        if not src.exists():
            return None

        ext = src.suffix or ".png"
        dest = dest_dir / f"screenshot_{idx:03d}{ext}"
        try:
            shutil.copy2(src, dest)
            return dest
        except Exception:
            return None


def generate_design_docs(
    template_profile_path: str,
    analysis_results_path: str,
    output_dir: str,
) -> List[str]:
    """Main entry point: generate design documents from profile and analysis.

    Args:
        template_profile_path: Path to template_profile.json.
        analysis_results_path: Path to analysis_results.json.
        output_dir: Directory to write output Markdown files and images.

    Returns:
        List of generated Markdown file paths.
    """
    profile_data = read_json(template_profile_path)
    profile = TemplateProfile.from_dict(profile_data)

    analysis = read_json(analysis_results_path)

    ensure_dir(output_dir)
    generator = DesignDocGenerator(profile, analysis, output_dir)
    return generator.generate_all()
