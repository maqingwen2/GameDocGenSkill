"""Plugin-based multi-format template parser for game design documents."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SectionNode:
    """Represents a hierarchical section in a template."""

    def __init__(self, title: str, level: int = 1, content: str = "", children: Optional[List["SectionNode"]] = None):
        self.title = title
        self.level = level
        self.content = content
        self.children = children or []
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "level": self.level,
            "content": self.content,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SectionNode":
        node = cls(data["title"], data["level"], data.get("content", ""))
        node.metadata = data.get("metadata", {})
        node.children = [cls.from_dict(c) for c in data.get("children", [])]
        return node


class TemplateProfile:
    """Extracted profile from a game design document template."""

    def __init__(self, source_path: str, doc_type: str = "unknown"):
        self.source_path = source_path
        self.doc_type = doc_type  # "release" or "design_doc"
        self.sections: List[SectionNode] = []
        self.terminology: Dict[str, str] = {}  # term -> typical usage
        self.formatting_rules: Dict[str, Any] = {}
        self.module_catalog: List[Dict[str, Any]] = []  # functional module list
        self.notices: List[str] = []  # 注意事项
        self.config_refs: List[str] = []  # config table references

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_path": self.source_path,
            "doc_type": self.doc_type,
            "sections": [s.to_dict() for s in self.sections],
            "terminology": self.terminology,
            "formatting_rules": self.formatting_rules,
            "module_catalog": self.module_catalog,
            "notices": self.notices,
            "config_refs": self.config_refs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateProfile":
        profile = cls(data["source_path"], data.get("doc_type", "unknown"))
        profile.sections = [SectionNode.from_dict(s) for s in data.get("sections", [])]
        profile.terminology = data.get("terminology", {})
        profile.formatting_rules = data.get("formatting_rules", {})
        profile.module_catalog = data.get("module_catalog", [])
        profile.notices = data.get("notices", [])
        profile.config_refs = data.get("config_refs", [])
        return profile


class TemplateParser(ABC):
    """Abstract base for template parsers."""

    SUPPORTED_EXTS: List[str] = []

    @abstractmethod
    def parse(self, file_path: str) -> TemplateProfile:
        """Parse template file and return profile."""
        ...

    @classmethod
    def supports(cls, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in cls.SUPPORTED_EXTS


class ExcelParser(TemplateParser):
    """Parse .xlsx game design templates."""

    SUPPORTED_EXTS = [".xlsx", ".xlsm"]

    def parse(self, file_path: str) -> TemplateProfile:
        import pandas as pd

        profile = TemplateProfile(file_path, doc_type=self._detect_doc_type(file_path))
        xl = pd.ExcelFile(file_path)

        for sheet_name in xl.sheet_names:
            if "详细逻辑设计" in sheet_name:
                self._parse_logic_design(profile, xl, sheet_name)
            elif "系统效果图" in sheet_name:
                self._parse_ui_screens(profile, xl, sheet_name)
            elif "配置" in sheet_name or "配置档" in sheet_name:
                self._parse_config_sheet(profile, xl, sheet_name)
            elif "设计概要" in sheet_name:
                self._parse_overview(profile, xl, sheet_name)

        self._extract_terminology(profile)
        self._extract_formatting_rules(profile)
        return profile

    def _detect_doc_type(self, file_path: str) -> str:
        name = Path(file_path).name
        if "Release" in name or "release" in name:
            return "release"
        return "design_doc"

    def _parse_logic_design(self, profile: TemplateProfile, xl: Any, sheet_name: str) -> None:
        import pandas as pd

        df = xl.parse(sheet_name, header=None)
        df = df.fillna("")

        # Extract notices (注意事项)
        for _, row in df.iterrows():
            for val in row:
                val_str = str(val).strip()
                if val_str.startswith("注意事项"):
                    # Find the notice content in the same row or next cells
                    for v in row:
                        v_str = str(v).strip()
                        if v_str and not v_str.startswith("注意事项") and len(v_str) > 5:
                            profile.notices.append(v_str)
                            break

        # Extract module catalog
        catalog_start = False
        current_module: Optional[Dict[str, Any]] = None
        for _, row in df.iterrows():
            vals = [str(v).strip() for v in row if str(v).strip()]
            if not vals:
                continue

            joined = " ".join(vals)
            if "功能模块划分" in joined or "模块划分" in joined:
                catalog_start = True
                continue

            if catalog_start and "详细设计" in joined:
                catalog_start = False
                continue

            if catalog_start:
                # Parse module entry like "3 主界面&通用功能" or "3.1 主界面"
                mod = self._parse_module_entry(vals)
                if mod:
                    if mod.get("is_submodule"):
                        if current_module:
                            current_module.setdefault("submodules", []).append(mod)
                    else:
                        profile.module_catalog.append(mod)
                        current_module = mod

        # Extract config references
        for _, row in df.iterrows():
            for val in row:
                val_str = str(val)
                matches = re.findall(r"【(\w+DB)】", val_str)
                profile.config_refs.extend(matches)
                matches2 = re.findall(r"(\w+DB)\s*[【.]", val_str)
                profile.config_refs.extend(matches2)

        profile.config_refs = sorted(set(profile.config_refs))

    def _parse_module_entry(self, vals: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a single module entry from row values."""
        joined = " ".join(vals)
        # Pattern: number + title, e.g. "3 主界面&通用功能" or "3.1 主界面"
        m = re.match(r"^(\d+(?:\.\d+)?)\s+(.+)$", joined)
        if m:
            num, title = m.groups()
            return {
                "number": num,
                "title": title,
                "is_submodule": "." in num,
            }
        # Try other patterns
        for v in vals:
            m = re.match(r"^(\d+(?:\.\d+)?)[\.\s]+(.+)$", v)
            if m:
                num, title = m.groups()
                return {
                    "number": num,
                    "title": title,
                    "is_submodule": "." in num,
                }
        return None

    def _parse_ui_screens(self, profile: TemplateProfile, xl: Any, sheet_name: str) -> None:
        # UI screens sheet mainly contains screenshot descriptions
        pass

    def _parse_config_sheet(self, profile: TemplateProfile, xl: Any, sheet_name: str) -> None:
        # Config sheet contains table schemas
        pass

    def _parse_overview(self, profile: TemplateProfile, xl: Any, sheet_name: str) -> None:
        pass

    def _extract_terminology(self, profile: TemplateProfile) -> None:
        """Extract common game design terminology from parsed content."""
        # Common patterns in Chinese game design docs
        terms = {
            "解锁条件": "活动/功能开启的前置要求",
            "玩法时间": "活动可参与的时间段",
            "领奖时间": "活动结束后可领取奖励的时间段",
            "主界面": "玩家进入活动后看到的第一个界面",
            "排行榜": "展示玩家排名的界面",
            "配置表": "策划提供给程序的数据表格",
        }
        profile.terminology.update(terms)

    def _extract_formatting_rules(self, profile: TemplateProfile) -> None:
        profile.formatting_rules = {
            "heading_prefix": "●",
            "module_prefix": "模块",
            "notice_prefix": "注意事项",
            "numbering_style": "decimal",  # 1, 1.1, 1.1.1
            "config_ref_format": "【TableName】",  # or "TableName.field"
            "section_order": ["注意事项", "功能模块划分", "模块详细设计"],
        }


class WordParser(TemplateParser):
    """Parse .doc/.docx templates."""

    SUPPORTED_EXTS = [".doc", ".docx"]

    def parse(self, file_path: str) -> TemplateProfile:
        from docx import Document

        profile = TemplateProfile(file_path, doc_type="word_doc")
        doc = Document(file_path)

        current_section: Optional[SectionNode] = None
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            level = self._heading_level(para)
            if level > 0:
                node = SectionNode(title=text, level=level)
                if level == 1:
                    profile.sections.append(node)
                    current_section = node
                elif current_section and level > current_section.level:
                    current_section.children.append(node)
                else:
                    profile.sections.append(node)
                    current_section = node
            else:
                if current_section:
                    current_section.content += text + "\n"

            # Extract notices
            if text.startswith("注意事项") or text.startswith("注意"):
                profile.notices.append(text)

        self._extract_modules_from_sections(profile)
        return profile

    def _heading_level(self, para: Any) -> int:
        """Return heading level (1-9) or 0 if not a heading."""
        if para.style.name.startswith("Heading"):
            try:
                return int(para.style.name.replace("Heading", ""))
            except ValueError:
                return 0
        # Fallback: detect by prefix patterns
        text = para.text.strip()
        if text.startswith("# "):
            return 1
        if text.startswith("## "):
            return 2
        if text.startswith("### "):
            return 3
        return 0

    def _extract_modules_from_sections(self, profile: TemplateProfile) -> None:
        """Extract module catalog from section hierarchy."""
        for sec in profile.sections:
            if "模块" in sec.title or "功能" in sec.title:
                for child in sec.children:
                    profile.module_catalog.append({
                        "number": "",
                        "title": child.title,
                        "is_submodule": False,
                    })


class MarkdownParser(TemplateParser):
    """Parse .md templates."""

    SUPPORTED_EXTS = [".md", ".markdown"]

    def parse(self, file_path: str) -> TemplateProfile:
        profile = TemplateProfile(file_path, doc_type="markdown")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        current_section: Optional[SectionNode] = None
        section_stack: List[SectionNode] = []

        for line in lines:
            line = line.rstrip()
            if not line:
                continue

            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)
                node = SectionNode(title=title.strip(), level=level)

                # Pop stack to find parent
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    section_stack[-1].children.append(node)
                else:
                    profile.sections.append(node)

                section_stack.append(node)
                current_section = node
            else:
                if current_section:
                    current_section.content += line + "\n"

        self._extract_modules_from_sections(profile)
        return profile

    def _extract_modules_from_sections(self, profile: TemplateProfile) -> None:
        for sec in profile.sections:
            if "模块" in sec.title or "功能" in sec.title:
                for child in sec.children:
                    profile.module_catalog.append({
                        "number": "",
                        "title": child.title,
                        "is_submodule": False,
                    })


class TemplateParserRegistry:
    """Registry for template parsers."""

    _parsers: List[type[TemplateParser]] = [ExcelParser, WordParser, MarkdownParser]

    @classmethod
    def get_parser(cls, file_path: str) -> Optional[TemplateParser]:
        for parser_cls in cls._parsers:
            if parser_cls.supports(file_path):
                return parser_cls()
        return None

    @classmethod
    def register(cls, parser_cls: type[TemplateParser]) -> None:
        cls._parsers.append(parser_cls)


def parse_templates(template_dir: str) -> List[TemplateProfile]:
    """Parse all templates in a directory."""
    import os
    from pathlib import Path

    ext_set = {".xlsx", ".xlsm", ".doc", ".docx", ".md", ".markdown"}
    files = []
    for root, _, fnames in os.walk(template_dir):
        for fname in fnames:
            fpath = Path(root) / fname
            if fpath.suffix.lower() in ext_set:
                files.append(fpath)
    files = sorted(files)
    profiles = []
    for fpath in files:
        parser = TemplateParserRegistry.get_parser(str(fpath))
        if parser:
            try:
                profile = parser.parse(str(fpath))
                profiles.append(profile)
            except Exception as e:
                print(f"[WARN] Failed to parse {fpath}: {e}")
    return profiles


def merge_profiles(profiles: List[TemplateProfile]) -> TemplateProfile:
    """Merge multiple template profiles into a unified profile."""
    if not profiles:
        return TemplateProfile("", "unknown")

    merged = TemplateProfile("merged", profiles[0].doc_type)
    all_modules = {}
    all_terms = {}
    all_notices = []
    all_config_refs = []

    for p in profiles:
        for mod in p.module_catalog:
            key = mod.get("title", "")
            if key and key not in all_modules:
                all_modules[key] = mod
        all_terms.update(p.terminology)
        all_notices.extend(p.notices)
        all_config_refs.extend(p.config_refs)

    merged.module_catalog = list(all_modules.values())
    merged.terminology = all_terms
    merged.notices = sorted(set(all_notices), key=len, reverse=True)
    merged.config_refs = sorted(set(all_config_refs))
    merged.formatting_rules = profiles[0].formatting_rules
    return merged
