"""Markdown generation report generator."""

from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Optional

from .schemas import ActivityStatus, EvidenceLevel, GenerationReport, MonthlyLogbook, MonthTimeline


def build_generation_report(
    timeline: MonthTimeline,
    logbook: MonthlyLogbook,
    pdf_path: Optional[str] = None,
) -> GenerationReport:
    """Builds structured metrics for the logbook generation."""
    total_commits = sum(len(d.commits) for d in timeline.days)
    working_days = sum(1 for d in timeline.days if d.working_day)

    direct_days = sum(1 for e in logbook.entries if e.evidence_level == EvidenceLevel.DIRECT)
    manual_days = sum(1 for e in logbook.entries if e.evidence_level == EvidenceLevel.MANUAL)
    inferred_days = sum(1 for e in logbook.entries if e.evidence_level == EvidenceLevel.INFERRED)
    needs_review = sum(1 for e in logbook.entries if e.status == ActivityStatus.NEEDS_REVIEW)

    return GenerationReport(
        month=timeline.month,
        repository_count=len(timeline.repositories),
        relevant_commit_count=total_commits,
        total_days=len(timeline.days),
        working_days=working_days,
        direct_evidence_days=direct_days,
        manual_days=manual_days,
        inferred_days=inferred_days,
        needs_review_days=needs_review,
        pdf_path=pdf_path,
        compiled_at=datetime.datetime.now().isoformat() if pdf_path else None,
    )


def render_report_markdown(report: GenerationReport, timeline: MonthTimeline) -> str:
    """Renders the generation report as a clean Markdown document."""
    pdf_size_str = "-"
    if report.pdf_path and os.path.isfile(report.pdf_path):
        size_bytes = os.path.getsize(report.pdf_path)
        pdf_size_str = f"{size_bytes / 1024:.1f} KB"

    repos_list = "\n".join(f"- `{r}`" for r in timeline.repositories) or "- *(Tidak ada repositori)*"

    md = f"""# Laporan Hasil Generate Logbook Magang

- **Bulan**: `{report.month}`
- **Waktu Generate**: `{report.compiled_at or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
- **Status Kompilasi**: `{"SUKSES" if report.pdf_path else "BELUM/GAGAL"}`

---

## 1. Ringkasan Metrik

| Indikator | Jumlah |
| :--- | :--- |
| Total Repositori Magang | {report.repository_count} |
| Total Commit Relevan | {report.relevant_commit_count} |
| Total Hari Terdata | {report.total_days} |
| Hari Kerja (Senin - Jumat) | {report.working_days} |
| Hari dengan Direct Evidence (Git) | {report.direct_evidence_days} |
| Hari dengan Manual Evidence (Catatan) | {report.manual_days} |
| Hari dengan Inferred Evidence | {report.inferred_days} |
| Hari yang Perlu Direview (`NEEDS_REVIEW`) | {report.needs_review_days} |

---

## 2. Repositori yang Terlibat

{repos_list}

---

## 3. Hasil Berkas PDF

- **Lokasi File**: `{report.pdf_path or "-"}`
- **Ukuran File**: {pdf_size_str}

"""
    return md


def save_generation_report(
    output_file: Path,
    timeline: MonthTimeline,
    logbook: MonthlyLogbook,
    pdf_path: Optional[str] = None,
) -> GenerationReport:
    report = build_generation_report(timeline, logbook, pdf_path)
    content = render_report_markdown(report, timeline)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    return report
