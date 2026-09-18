"""LaTeX code renderer for dynamic logbook content."""

from __future__ import annotations

import calendar
import datetime
import os
import shutil
from pathlib import Path
from typing import List, Optional

from .config import AppConfig
from .latex_escape import escape_latex
from .schemas import ActivityStatus, DailyActivityEntry, MonthlyLogbook
from .timeline import DAY_NAMES_ID

MONTH_NAMES_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def format_indonesian_date(date_str: str, include_day_name: bool = True) -> str:
    """Formats 'YYYY-MM-DD' into 'Hari, DD Bulan YYYY' or 'DD Bulan YYYY'."""
    dt = datetime.date.fromisoformat(date_str)
    day_name = DAY_NAMES_ID[dt.weekday()]
    month_name = MONTH_NAMES_ID[dt.month]
    formatted = f"{dt.day:02d} {month_name} {dt.year}"
    if include_day_name:
        return f"{day_name}, {formatted}"
    return formatted


def get_period_label(year: int, month: int) -> str:
    """Returns '01 Bulan YYYY -- DD Bulan YYYY'."""
    month_name = MONTH_NAMES_ID[month]
    last_day = calendar.monthrange(year, month)[1]
    return f"01 {month_name} {year} -- {last_day:02d} {month_name} {year}"


def render_metadata_tex(config: AppConfig, year: int, month: int) -> str:
    """Generates LaTeX metadata variable declarations."""
    period_str = get_period_label(year, month)

    lines = [
        r"% Auto-generated logbook metadata",
        rf"\newcommand{{\StudentName}}{{{escape_latex(config.student.name)}}}",
        rf"\newcommand{{\StudentNIM}}{{{escape_latex(config.student.nim)}}}",
        rf"\newcommand{{\StudentProgram}}{{{escape_latex(config.student.program)}}}",
        rf"\newcommand{{\CompanyFullName}}{{{escape_latex(config.internship.company)}}}",
        rf"\newcommand{{\AcademicAdvisor}}{{{escape_latex(config.student.academic_advisor)}}}",
        rf"\newcommand{{\FieldSupervisor}}{{{escape_latex(config.student.field_supervisor)}}}",
        rf"\newcommand{{\LogbookPeriod}}{{{escape_latex(period_str)}}}",
    ]
    return "\n".join(lines) + "\n"


def render_activities_tex(
    entries: List[DailyActivityEntry],
    default_check_in: str = "07:00",
    default_check_out: str = "16:20",
) -> str:
    """Generates LaTeX table entries."""
    formatted_entries = []
    for entry in entries:
        date_formatted = escape_latex(format_indonesian_date(entry.date, include_day_name=True))

        if entry.status == ActivityStatus.NEEDS_REVIEW or not entry.activity:
            check_in = "-"
            check_out = "-"
            activity_text = r"\textit{[Perlu Review Kegiatan / Tidak Ada Catatan]}"
        else:
            check_in = escape_latex(entry.check_in or default_check_in)
            check_out = escape_latex(entry.check_out or default_check_out)
            activity_text = escape_latex(entry.activity)

        formatted_entries.append(
            f"\\LogbookEntry\n"
            f"  {{{date_formatted}}}\n"
            f"  {{{check_in}}}\n"
            f"  {{{check_out}}}\n"
            f"  {{{activity_text}}}"
        )

    if not formatted_entries:
        return "% Auto-generated logbook activities\n"

    joined = "\n\\\\ \\hline\n".join(formatted_entries)
    return f"% Auto-generated logbook activities\n{joined}\n"


def render_latex_files(
    output_dir: Path,
    config: AppConfig,
    logbook: MonthlyLogbook,
    current_dir: Optional[Path] = None,
) -> None:
    """Writes metadata.tex and activities.tex to target month dir and syncs to current dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    parts = logbook.month.split("-")
    year, month = int(parts[0]), int(parts[1])

    metadata_content = render_metadata_tex(config, year, month)
    activities_content = render_activities_tex(
        entries=logbook.entries,
        default_check_in=config.logbook.check_in,
        default_check_out=config.logbook.check_out,
    )

    metadata_path = output_dir / "metadata.tex"
    activities_path = output_dir / "activities.tex"

    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(metadata_content)

    with open(activities_path, "w", encoding="utf-8") as f:
        f.write(activities_content)

    # Copy / update generated/current/
    if current_dir:
        current_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(metadata_path, current_dir / "metadata.tex")
        shutil.copyfile(activities_path, current_dir / "activities.tex")
