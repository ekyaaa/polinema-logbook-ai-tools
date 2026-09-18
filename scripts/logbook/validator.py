"""Validator for logbook entries and evidence contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from .schemas import ActivityStatus, DailyActivityEntry, EvidenceLevel, MonthTimeline


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_logbook_entries(
    entries: List[DailyActivityEntry],
    timeline: MonthTimeline,
    max_words: int = 35,
    allow_inferred: bool = True,
) -> ValidationResult:
    """Validates generated daily activities against the source timeline."""
    errors: List[str] = []
    warnings: List[str] = []

    # Map timeline days
    timeline_days = {d.date: d for d in timeline.days}
    entry_dates: Set[str] = set()

    # Collect valid evidence refs and repos across the timeline
    valid_evidence_refs: Set[str] = set()
    valid_repos: Set[str] = set(timeline.repositories)

    for d in timeline.days:
        for c in d.commits:
            valid_evidence_refs.add(f"{c.repository}:{c.short_sha}")
            valid_evidence_refs.add(f"{c.repository}:{c.sha}")
            valid_evidence_refs.add(c.short_sha)
            valid_evidence_refs.add(c.sha)

    for entry in entries:
        date = entry.date
        if date in entry_dates:
            errors.append(f"Duplicate entry for date: {date}")
        entry_dates.add(date)

        if date not in timeline_days:
            errors.append(f"Entry date {date} not found in month timeline.")
            continue

        day_tl = timeline_days[date]

        # Check status and evidence level
        if day_tl.evidence_level == EvidenceLevel.NONE:
            if entry.evidence_level == EvidenceLevel.DIRECT:
                errors.append(
                    f"Date {date} has NO evidence but claims direct evidence."
                )
            elif entry.evidence_level == EvidenceLevel.INFERRED:
                if not allow_inferred:
                    errors.append(
                        f"Date {date} has inferred activity, but allow_inferred is disabled."
                    )
            elif entry.status == ActivityStatus.OK and entry.activity:
                errors.append(
                    f"Date {date} has NO evidence but status is marked OK with activity: '{entry.activity}'. Should be NEEDS_REVIEW or INFERRED."
                )
        elif day_tl.evidence_level == EvidenceLevel.DIRECT:
            if not day_tl.commits and entry.evidence_level == EvidenceLevel.DIRECT:
                errors.append(f"Date {date} claims direct evidence, but 0 commits found.")

        # Check repositories
        for r in entry.repositories:
            if r not in valid_repos:
                warnings.append(f"Date {date}: repository '{r}' not in timeline repositories.")

        # Check evidence refs
        for ref in entry.evidence_refs:
            if ref not in valid_evidence_refs:
                warnings.append(f"Date {date}: evidence ref '{ref}' not found in collected commits.")

        # Check word limit
        if entry.activity:
            word_count = len(entry.activity.strip().split())
            if word_count > max_words:
                warnings.append(
                    f"Date {date}: activity length ({word_count} words) exceeds max allowed {max_words} words."
                )

    # Check for missing dates
    for expected_date in timeline_days.keys():
        if expected_date not in entry_dates:
            errors.append(f"Missing expected date in logbook entries: {expected_date}")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
