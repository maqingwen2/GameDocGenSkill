"""Common utilities for game-imitation-designer skill."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: str) -> Path:
    """Ensure directory exists, return Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(data: Any, path: str, indent: int = 2) -> None:
    """Write data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def read_json(path: str) -> Any:
    """Read JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_timestamp() -> str:
    """Return current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def collect_files(directory: str, extensions: List[str]) -> List[Path]:
    """Recursively collect files with given extensions."""
    ext_set = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}
    results = []
    for root, _, files in os.walk(directory):
        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix.lower() in ext_set:
                results.append(fpath)
    return sorted(results)


def sanitize_filename(name: str) -> str:
    """Sanitize string for use as filename."""
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, "_")
    return name.strip()


def load_or_create_json(path: str, default: Any = None) -> Any:
    """Load JSON if exists, otherwise create with default and return."""
    if os.path.exists(path):
        return read_json(path)
    write_json(default if default is not None else {}, path)
    return default if default is not None else {}
