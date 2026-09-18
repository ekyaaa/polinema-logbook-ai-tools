"""Configuration loader and schema validation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml


@dataclass
class StudentConfig:
    name: str = ""
    nim: str = ""
    program: str = ""
    institution: str = ""
    academic_advisor: str = ""
    field_supervisor: str = ""


@dataclass
class InternshipConfig:
    company: str = ""
    division: str = ""
    project_root: str = ""
    git_author_names: List[str] = field(default_factory=list)
    git_author_emails: List[str] = field(default_factory=list)


@dataclass
class LogbookConfig:
    timezone: str = "Asia/Jakarta"
    working_days: List[str] = field(
        default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    )
    check_in: str = "07:00"
    check_out: str = "16:20"
    include_merges: bool = False
    include_file_names: bool = True
    include_diff_stat: bool = False
    allow_inferred_activity: bool = False
    max_activity_words: int = 35
    latex_engine: str = "xelatex"


@dataclass
class AppConfig:
    project_dir: Path
    student: StudentConfig
    internship: InternshipConfig
    logbook: LogbookConfig


def find_project_root(start_dir: Optional[Path] = None) -> Path:
    """Finds the root directory of this logbook project."""
    if start_dir is None:
        start_dir = Path.cwd()
    curr = start_dir.resolve()
    for _ in range(10):
        if (curr / "config").is_dir() and (curr / "template").is_dir():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    # Fallback to current working directory
    return start_dir.resolve()


def load_yaml_file(path: Path) -> dict:
    if not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def load_app_config(project_dir: Optional[Path] = None) -> AppConfig:
    root = find_project_root(project_dir)
    config_dir = root / "config"

    student_data = load_yaml_file(config_dir / "student.yaml")
    internship_data = load_yaml_file(config_dir / "internship.yaml")
    logbook_data = load_yaml_file(config_dir / "logbook.yaml")

    student = StudentConfig(
        name=str(student_data.get("name", "")),
        nim=str(student_data.get("nim", "")),
        program=str(student_data.get("program", "")),
        institution=str(student_data.get("institution", "")),
        academic_advisor=str(student_data.get("academic_advisor", "")),
        field_supervisor=str(student_data.get("field_supervisor", "")),
    )

    git_authors = internship_data.get("git_authors", {}) or {}
    author_names = [str(n) for n in git_authors.get("names", [])]
    author_emails = [str(e) for e in git_authors.get("emails", [])]

    # Resolve project root (expand ~ or relative path)
    raw_project_root = str(internship_data.get("project_root", ""))
    resolved_project_root = os.path.expanduser(raw_project_root) if raw_project_root else ""

    internship = InternshipConfig(
        company=str(internship_data.get("company", "")),
        division=str(internship_data.get("division", "")),
        project_root=resolved_project_root,
        git_author_names=author_names,
        git_author_emails=author_emails,
    )

    default_hours = logbook_data.get("default_hours", {}) or {}
    git_opts = logbook_data.get("git", {}) or {}
    ai_opts = logbook_data.get("ai", {}) or {}
    latex_opts = logbook_data.get("latex", {}) or {}

    logbook = LogbookConfig(
        timezone=str(logbook_data.get("timezone", "Asia/Jakarta")),
        working_days=[
            str(d).strip().lower()
            for d in logbook_data.get(
                "working_days", ["monday", "tuesday", "wednesday", "thursday", "friday"]
            )
        ],
        check_in=str(default_hours.get("check_in", "07:00")),
        check_out=str(default_hours.get("check_out", "16:20")),
        include_merges=bool(git_opts.get("include_merges", False)),
        include_file_names=bool(git_opts.get("include_file_names", True)),
        include_diff_stat=bool(git_opts.get("include_diff_stat", False)),
        allow_inferred_activity=bool(ai_opts.get("allow_inferred_activity", False)),
        max_activity_words=int(ai_opts.get("max_activity_words", 35)),
        latex_engine=str(latex_opts.get("engine", "xelatex")),
    )

    return AppConfig(
        project_dir=root,
        student=student,
        internship=internship,
        logbook=logbook,
    )
