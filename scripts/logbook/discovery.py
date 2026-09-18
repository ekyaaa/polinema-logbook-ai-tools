"""Git repository discovery engine."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set


DEFAULT_IGNORES = {
    "node_modules",
    "vendor",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".gradle",
    ".dart_tool",
    "Pods",
    "coverage",
    ".cache",
    "tmp",
    "temp",
    "backup",
    "backup_db",
    "archive",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "env",
    "venv",
}


@dataclass
class DiscoveredRepo:
    name: str
    path: str
    canonical_path: str


def load_ignore_patterns(ignore_file_path: Optional[Path]) -> Set[str]:
    patterns = set(DEFAULT_IGNORES)
    if ignore_file_path and ignore_file_path.is_file():
        try:
            with open(ignore_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception:
            pass
    return patterns


def is_git_repo(path: Path) -> Optional[str]:
    """Checks if a directory is a git repo and returns its canonical top-level path."""
    git_entry = path / ".git"
    if not (git_entry.is_dir() or git_entry.is_file()):
        return None
    try:
        res = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            top_level = res.stdout.strip()
            if top_level:
                return os.path.realpath(top_level)
    except Exception:
        pass
    return None


def discover_repositories(
    root: Path | str,
    ignore_file: Optional[Path | str] = None,
    max_depth: int = 6,
) -> List[DiscoveredRepo]:
    """Recursively discovers all Git repositories under root.

    Handles:
    - .git directories and .git files (submodules, worktrees)
    - canonicalization via git rev-parse --show-toplevel
    - deduplication of canonical paths
    - ignore patterns (.logbookignore)
    - safe error handling for unreadable folders
    """
    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        return []

    ignore_file_path = Path(ignore_file).resolve() if ignore_file else (root_path / ".logbookignore")
    # If not in root_path, check current logbook project dir
    if not ignore_file_path.is_file():
        curr_ignore = Path.cwd() / ".logbookignore"
        if curr_ignore.is_file():
            ignore_file_path = curr_ignore

    ignore_patterns = load_ignore_patterns(ignore_file_path)

    discovered: List[DiscoveredRepo] = []
    seen_canonical: Set[str] = set()

    def _scan(curr_dir: Path, current_depth: int):
        if current_depth > max_depth:
            return

        # Check if current directory is itself a git repo
        canonical = is_git_repo(curr_dir)
        if canonical:
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                repo_name = Path(canonical).name
                discovered.append(
                    DiscoveredRepo(
                        name=repo_name,
                        path=str(curr_dir),
                        canonical_path=canonical,
                    )
                )
            # Do not recurse into internal directories of a discovered repo unless necessary
            return

        try:
            entries = list(os.scandir(curr_dir))
        except (PermissionError, OSError):
            return

        for entry in entries:
            try:
                if not entry.is_dir(follow_symlinks=False):
                    continue
            except OSError:
                continue

            dir_name = entry.name
            if dir_name.startswith(".") and dir_name != ".git":
                continue
            if dir_name in ignore_patterns:
                continue

            sub_path = Path(entry.path)
            _scan(sub_path, current_depth + 1)

    _scan(root_path, 0)
    discovered.sort(key=lambda r: r.name.lower())
    return discovered
