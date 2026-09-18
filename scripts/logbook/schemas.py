"""Pydantic data schemas for logbook generation contract."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceLevel(str, Enum):
    DIRECT = "direct"
    MANUAL = "manual"
    INFERRED = "inferred"
    NONE = "none"


class ActivityStatus(str, Enum):
    OK = "OK"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class CommitEvidence(BaseModel):
    sha: str
    short_sha: str
    repository: str
    repo_path: str
    author_name: str
    author_email: str
    authored_at: str
    subject: str
    body: str = ""
    files: List[str] = Field(default_factory=list)


class DayTimeline(BaseModel):
    date: str
    day_name: str
    working_day: bool
    evidence_level: EvidenceLevel
    repositories: List[str] = Field(default_factory=list)
    commits: List[CommitEvidence] = Field(default_factory=list)
    manual_notes: List[str] = Field(default_factory=list)


class MonthTimeline(BaseModel):
    month: str
    repositories: List[str] = Field(default_factory=list)
    days: List[DayTimeline] = Field(default_factory=list)


class DailyActivityEntry(BaseModel):
    date: str
    status: ActivityStatus = ActivityStatus.OK
    evidence_level: EvidenceLevel = EvidenceLevel.DIRECT
    confidence: float = 1.0
    activity: Optional[str] = None
    repositories: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    check_in: Optional[str] = None
    check_out: Optional[str] = None


class MonthlyLogbook(BaseModel):
    month: str
    student_name: str
    nim: str
    company: str
    entries: List[DailyActivityEntry] = Field(default_factory=list)


class GenerationReport(BaseModel):
    month: str
    repository_count: int = 0
    relevant_commit_count: int = 0
    total_days: int = 0
    working_days: int = 0
    direct_evidence_days: int = 0
    manual_days: int = 0
    inferred_days: int = 0
    needs_review_days: int = 0
    pdf_path: Optional[str] = None
    compiled_at: Optional[str] = None
