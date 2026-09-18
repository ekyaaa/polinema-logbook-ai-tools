"""Configuration loader and schema validation."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
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
    allow_inferred_activity: bool = True
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
        if (curr / "template").is_dir() and ((curr / "config").is_dir() or (curr / "config.json").is_file()):
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    # Fallback to current working directory
    return start_dir.resolve()


def load_json_file(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_yaml_file(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def detect_git_defaults() -> Dict[str, str]:
    """Detects local git user.name and user.email safely."""
    name, email = "", ""
    try:
        res_name = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res_name.returncode == 0:
            name = res_name.stdout.strip()
    except Exception:
        pass

    try:
        res_email = subprocess.run(
            ["git", "config", "--get", "user.email"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res_email.returncode == 0:
            email = res_email.stdout.strip()
    except Exception:
        pass

    return {"name": name, "email": email}


def is_config_complete(config: AppConfig) -> bool:
    """Checks if all required onboarding fields are properly set."""
    placeholders = {
        "",
        "nama lengkap mahasiswa",
        "nama perusahaan mitra",
        "nama dosen pembimbing, s.kom., m.t.",
        "nama pembimbing lapangan / mentor",
        "/home/user/project/magang",
    }
    required_vals = [
        config.student.name.strip().lower(),
        config.student.nim.strip(),
        config.student.academic_advisor.strip().lower(),
        config.student.field_supervisor.strip().lower(),
        config.internship.company.strip().lower(),
        config.internship.project_root.strip(),
    ]
    for val in required_vals:
        if not val or val in placeholders:
            return False
    return True


def save_app_config(config_dict: dict, root_dir: Optional[Path] = None, filename: str = "config.json") -> Path:
    """Saves app configuration to config.json."""
    root = find_project_root(root_dir)
    target_path = root / filename
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return target_path


def load_app_config(project_dir: Optional[Path] = None) -> AppConfig:
    root = find_project_root(project_dir)

    # 1. Try unified config.json first (root or config/config.json)
    json_path = root / "config.json"
    if not json_path.is_file():
        json_path = root / "config" / "config.json"

    if json_path.is_file():
        data = load_json_file(json_path)
        student_data = data.get("student", {}) or {}
        internship_data = data.get("internship", {}) or {}
        logbook_data = data.get("logbook", {}) or {}

        student = StudentConfig(
            name=str(student_data.get("name", "")),
            nim=str(student_data.get("nim", "")),
            program=str(student_data.get("program", "D-IV Teknik Informatika")),
            institution=str(student_data.get("institution", "Politeknik Negeri Malang")),
            academic_advisor=str(student_data.get("academic_advisor", "")),
            field_supervisor=str(student_data.get("field_supervisor", "")),
        )

        git_authors = internship_data.get("git_authors", {}) or {}
        author_names = [str(n) for n in git_authors.get("names", [])]
        author_emails = [str(e) for e in git_authors.get("emails", [])]

        raw_project_root = str(internship_data.get("project_root", ""))
        resolved_project_root = os.path.expanduser(raw_project_root) if raw_project_root else ""

        internship = InternshipConfig(
            company=str(internship_data.get("company", "")),
            division=str(internship_data.get("division", "")),
            project_root=resolved_project_root,
            git_author_names=author_names,
            git_author_emails=author_emails,
        )

        logbook = LogbookConfig(
            timezone=str(logbook_data.get("timezone", "Asia/Jakarta")),
            working_days=[
                str(d).strip().lower()
                for d in logbook_data.get(
                    "working_days", ["monday", "tuesday", "wednesday", "thursday", "friday"]
                )
            ],
            check_in=str(logbook_data.get("check_in", "07:00")),
            check_out=str(logbook_data.get("check_out", "16:20")),
            include_merges=bool(logbook_data.get("include_merges", False)),
            include_file_names=bool(logbook_data.get("include_file_names", True)),
            include_diff_stat=bool(logbook_data.get("include_diff_stat", False)),
            allow_inferred_activity=bool(logbook_data.get("allow_inferred_activity", True)),
            max_activity_words=int(logbook_data.get("max_activity_words", 35)),
            latex_engine=str(logbook_data.get("latex_engine", "xelatex")),
        )

        return AppConfig(
            project_dir=root,
            student=student,
            internship=internship,
            logbook=logbook,
        )

    # 2. Fallback to legacy YAML configs in config/
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
        allow_inferred_activity=bool(ai_opts.get("allow_inferred_activity", True)),
        max_activity_words=int(ai_opts.get("max_activity_words", 35)),
        latex_engine=str(latex_opts.get("engine", "xelatex")),
    )

    return AppConfig(
        project_dir=root,
        student=student,
        internship=internship,
        logbook=logbook,
    )
