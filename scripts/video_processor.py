"""Video keyframe extraction and screenshot deduplication pipeline."""

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image


try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


@dataclass
class FrameInfo:
    """Information about an extracted frame."""
    path: str
    timestamp: float  # seconds
    source: str  # video filename or 'screenshot'
    hash_value: Optional[str] = None
    tags: List[str] = field(default_factory=list)


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_keyframes(
    video_path: str,
    output_dir: str,
    scene_threshold: float = 0.3,
    max_frames: int = 50,
    min_interval: float = 1.0,
) -> List[FrameInfo]:
    """Extract keyframes from video using scene change detection.

    Args:
        video_path: Path to video file.
        output_dir: Directory to save extracted frames.
        scene_threshold: Scene change threshold (0.0-1.0), lower = more sensitive.
        max_frames: Maximum number of frames to extract per video.
        min_interval: Minimum interval between keyframes in seconds.
    """
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")

    ensure_dir(output_dir)
    video_name = Path(video_path).stem
    temp_dir = Path(output_dir) / f"_temp_{video_name}"
    ensure_dir(str(temp_dir))

    # Step 1: Use ffmpeg scene detection to find keyframes
    scene_file = temp_dir / "scenes.txt"
    filter_str = (
        f"select='gt(scene,{scene_threshold})',showinfo"
    )

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", filter_str,
        "-f", "null",
        "-",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        stderr = result.stderr
    except Exception as e:
        raise RuntimeError(f"ffmpeg scene detection failed: {e}")

    # Parse scene timestamps from showinfo output
    timestamps = [0.0]  # Always include first frame
    for line in stderr.splitlines():
        if "pts_time:" in line:
            m = __import__('re').search(r"pts_time:([\d.]+)", line)
            if m:
                ts = float(m.group(1))
                if ts - timestamps[-1] >= min_interval:
                    timestamps.append(ts)

    # If scene detection yields too few frames, add fixed-interval frames
    if len(timestamps) < 5:
        duration = _get_video_duration(video_path)
        if duration > 0:
            interval = max(duration / max_frames, min_interval)
            timestamps = [i * interval for i in range(int(duration / interval) + 1)]

    # Limit frames
    if len(timestamps) > max_frames:
        # Keep first, last, and evenly spaced middle frames
        indices = [0] + [
            int(i * (len(timestamps) - 1) / (max_frames - 1))
            for i in range(1, max_frames - 1)
        ] + [len(timestamps) - 1]
        timestamps = [timestamps[i] for i in sorted(set(indices))]

    # Step 2: Extract frames at selected timestamps
    frames = []
    for idx, ts in enumerate(timestamps):
        out_name = f"{video_name}_frame_{idx:04d}_{ts:.2f}s.png"
        out_path = Path(output_dir) / out_name

        extract_cmd = [
            "ffmpeg",
            "-ss", str(ts),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            "-y",
            str(out_path),
        ]
        subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if out_path.exists():
            frames.append(FrameInfo(
                path=str(out_path),
                timestamp=ts,
                source=video_name,
            ))

    # Cleanup temp dir
    shutil.rmtree(temp_dir, ignore_errors=True)
    return frames


def _get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def compute_image_hashes(frames: List[FrameInfo]) -> None:
    """Compute perceptual hashes for all frames."""
    if not IMAGEHASH_AVAILABLE:
        # Fallback: compute simple MD5 of resized image
        for frame in frames:
            try:
                with Image.open(frame.path) as img:
                    img = img.resize((16, 16)).convert("L")
                    frame.hash_value = hashlib.md5(img.tobytes()).hexdigest()
            except Exception:
                frame.hash_value = None
        return

    for frame in frames:
        try:
            with Image.open(frame.path) as img:
                phash = str(imagehash.phash(img))
                ahash = str(imagehash.average_hash(img))
                frame.hash_value = f"{phash}:{ahash}"
        except Exception:
            frame.hash_value = None


def deduplicate_frames(frames: List[FrameInfo], threshold: int = 5) -> List[FrameInfo]:
    """Remove near-duplicate frames using perceptual hash comparison.

    Args:
        frames: List of FrameInfo with computed hashes.
        threshold: Maximum hash difference to consider duplicate.
    """
    if not frames:
        return []

    # Ensure hashes are computed
    if frames[0].hash_value is None:
        compute_image_hashes(frames)

    unique_frames = [frames[0]]

    if IMAGEHASH_AVAILABLE and ":" in (frames[0].hash_value or ""):
        for frame in frames[1:]:
            if frame.hash_value is None:
                unique_frames.append(frame)
                continue

            phash_f = imagehash.hex_to_hash(frame.hash_value.split(":")[0])
            ahash_f = imagehash.hex_to_hash(frame.hash_value.split(":")[1])

            is_dup = False
            for uframe in unique_frames:
                if uframe.hash_value is None:
                    continue
                phash_u = imagehash.hex_to_hash(uframe.hash_value.split(":")[0])
                ahash_u = imagehash.hex_to_hash(uframe.hash_value.split(":")[1])

                if (phash_f - phash_u) <= threshold and (ahash_f - ahash_u) <= threshold:
                    is_dup = True
                    break

            if not is_dup:
                unique_frames.append(frame)
    else:
        # MD5 exact dedup
        seen = {f.hash_value for f in unique_frames if f.hash_value}
        for frame in frames[1:]:
            if frame.hash_value not in seen:
                unique_frames.append(frame)
                seen.add(frame.hash_value)

    return unique_frames


def copy_screenshots(
    screenshot_dir: str,
    output_dir: str,
    max_size: Optional[Tuple[int, int]] = (1920, 1080),
) -> List[FrameInfo]:
    """Copy and optionally resize screenshot images.

    Args:
        screenshot_dir: Directory containing screenshot images.
        output_dir: Directory to copy processed screenshots.
        max_size: Maximum (width, height) for resizing. None to skip.
    """
    from .utils import collect_files

    ensure_dir(output_dir)
    img_exts = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
    files = collect_files(screenshot_dir, img_exts)

    frames = []
    for idx, fpath in enumerate(files):
        out_name = f"screenshot_{idx:04d}{fpath.suffix}"
        out_path = Path(output_dir) / out_name

        try:
            with Image.open(fpath) as img:
                if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                    img.thumbnail(max_size, Image.LANCZOS)
                img.save(out_path)
        except Exception as e:
            print(f"[WARN] Failed to process {fpath}: {e}")
            continue

        frames.append(FrameInfo(
            path=str(out_path),
            timestamp=0.0,
            source=f"screenshot:{fpath.name}",
        ))

    return frames


def create_screenshots_index(
    frames: List[FrameInfo],
    output_path: str,
    group_by_source: bool = True,
) -> None:
    """Create a JSON index of all screenshots for analysis workflow.

    The index is consumed by the Agent's multimodal analysis phase.
    """
    from .utils import write_json

    if group_by_source:
        groups = {}
        for frame in frames:
            src = frame.source
            if src not in groups:
                groups[src] = []
            groups[src].append({
                "path": frame.path,
                "timestamp": frame.timestamp,
                "tags": frame.tags,
            })
        data = {
            "total_frames": len(frames),
            "groups": groups,
        }
    else:
        data = {
            "total_frames": len(frames),
            "frames": [
                {
                    "path": f.path,
                    "timestamp": f.timestamp,
                    "source": f.source,
                    "tags": f.tags,
                }
                for f in frames
            ],
        }

    write_json(data, output_path)


def ensure_dir(path: str) -> Path:
    """Ensure directory exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
