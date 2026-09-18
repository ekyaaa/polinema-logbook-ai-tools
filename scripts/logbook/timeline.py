"""Timeline builder for constructing full monthly schedule and evidence binding."""

from __future__ import annotations

import calendar
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from .schemas import CommitEvidence, DayTimeline, EvidenceLevel, MonthTimeline

DAY_NAMES_ID = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}

WEEKDAY_NAME_TO_INT = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def load_manual_evidence(manual_dir: Path, month_key: str) -> Dict[str, List[str]]:
    """Loads manual notes from manual/YYYY-MM.yaml if present.

    Format expected:
    2026-09-03:
      - "Diskusi requirement bersama pembimbing lapangan."
    or
    2026-09-03: "Diskusi requirement bersama pembimbing lapangan."
    """
    manual_file = manual_dir / f"{month_key}.yaml"
    if not manual_file.is_file():
        return {}

    try:
        with open(manual_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return {}

            result: Dict[str, List[str]] = {}
            for k, v in data.items():
                date_str = str(k).strip()
                if isinstance(v, list):
                    result[date_str] = [str(item).strip() for item in v if item]
                elif isinstance(v, str):
                    result[date_str] = [v.strip()]
            return result
    except Exception:
        return {}


def build_month_timeline(
    year: int,
    month: int,
    commits: List[CommitEvidence],
    manual_notes: Optional[Dict[str, List[str]]] = None,
    working_days: Optional[List[str]] = None,
    only_working_days: bool = True,
) -> MonthTimeline:
    """Builds a deterministic month timeline, associating commits and manual notes by date."""
    if manual_notes is None:
        manual_notes = {}

    if working_days is None:
        working_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    allowed_weekday_ints = {
        WEEKDAY_NAME_TO_INT[d.lower()]
        for d in working_days
        if d.lower() in WEEKDAY_NAME_TO_INT
    }

    # Group commits by date string "YYYY-MM-DD"
    commits_by_date: Dict[str, List[CommitEvidence]] = {}
    for c in commits:
        date_str = c.authored_at[:10]
        commits_by_date.setdefault(date_str, []).append(c)

    days_in_month = calendar.monthrange(year, month)[1]
    month_key = f"{year:04d}-{month:02d}"

    all_days: List[DayTimeline] = []
    all_repos: set[str] = set()

    for day in range(1, days_in_month + 1):
        dt = datetime.date(year, month, day)
        date_str = dt.isoformat()
        weekday = dt.weekday()
        day_name = DAY_NAMES_ID[weekday]
        is_working_day = weekday in allowed_weekday_ints

        day_commits = commits_by_date.get(date_str, [])
        day_manual = manual_notes.get(date_str, [])

        day_repos = sorted({c.repository for c in day_commits})
        all_repos.update(day_repos)

        # Determine evidence level
        if day_commits:
            evidence_level = EvidenceLevel.DIRECT
        elif day_manual:
            evidence_level = EvidenceLevel.MANUAL
        else:
            evidence_level = EvidenceLevel.NONE

        # By default, logbooks only record working days unless weekend had explicit work/commits
        if only_working_days and not is_working_day and not day_commits and not day_manual:
            continue

        all_days.append(
            DayTimeline(
                date=date_str,
                day_name=day_name,
                working_day=is_working_day,
                evidence_level=evidence_level,
                repositories=day_repos,
                commits=day_commits,
                manual_notes=day_manual,
            )
        )

    return MonthTimeline(
        month=month_key,
        repositories=sorted(all_repos),
        days=all_days,
    )
