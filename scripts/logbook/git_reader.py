"""Git commit evidence reader and extractor."""

from __future__ import annotations

import datetime
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from dateutil import tz
from dateutil.parser import parse as parse_date

from .author import AuthorMatcher
from .discovery import DiscoveredRepo
from .schemas import CommitEvidence


def get_month_range(year: int, month: int, timezone_str: str = "Asia/Jakarta") -> Tuple[datetime.datetime, datetime.datetime]:
    """Calculates start datetime (inclusive) and end datetime (exclusive) for target month."""
    local_tz = tz.gettz(timezone_str) or tz.UTC
    start_dt = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=local_tz)

    if month == 12:
        end_dt = datetime.datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=local_tz)
    else:
        end_dt = datetime.datetime(year, month + 1, 1, 0, 0, 0, tzinfo=local_tz)

    return start_dt, end_dt


def parse_month_string(month_str: str) -> Tuple[int, int]:
    """Parses 'YYYY-MM' or 'Month YYYY' or 'YYYY-M' into (year, month)."""
    clean = month_str.strip()
    # Try YYYY-MM
    if "-" in clean:
        parts = clean.split("-")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            y, m = int(parts[0]), int(parts[1])
            if 1 <= m <= 12:
                return y, m

    # Try dateutil parse
    dt = parse_date(clean)
    return dt.year, dt.month


def get_commit_changed_files(repo_path: str, commit_sha: str) -> List[str]:
    """Extracts changed filenames for a commit using git diff-tree."""
    try:
        res = subprocess.run(
            ["git", "-C", repo_path, "diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
            return lines
    except Exception:
        pass
    return []


def collect_commits_from_repo(
    repo: DiscoveredRepo,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    author_matcher: AuthorMatcher,
    include_merges: bool = False,
    include_files: bool = True,
) -> List[CommitEvidence]:
    """Collects student commits from a single repository within the datetime range."""
    # Buffer after/before query slightly to ensure git covers all timezone boundaries
    buffer_after = (start_dt - datetime.timedelta(days=2)).isoformat()
    buffer_before = (end_dt + datetime.timedelta(days=2)).isoformat()

    cmd = [
        "git",
        "-C",
        repo.canonical_path,
        "log",
        "--all",
        f"--after={buffer_after}",
        f"--before={buffer_before}",
        "--format=%H%x00%an%x00%ae%x00%ai%x00%s%x00%b%x1e",
    ]
    if not include_merges:
        cmd.append("--no-merges")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
    except Exception:
        return []

    if res.returncode != 0 or not res.stdout.strip():
        return []

    records = res.stdout.strip("\x1e\n").split("\x1e")
    commits: List[CommitEvidence] = []
    target_tz = start_dt.tzinfo or tz.UTC

    for rec in records:
        if not rec.strip():
            continue
        fields = rec.strip().split("\x00")
        if len(fields) < 5:
            continue

        sha = fields[0].strip()
        author_name = fields[1].strip()
        author_email = fields[2].strip()
        date_str = fields[3].strip()
        subject = fields[4].strip()
        body = fields[5].strip() if len(fields) > 5 else ""

        # Filter by author
        if not author_matcher.matches(author_name, author_email):
            continue

        # Parse date and normalize timezone
        try:
            commit_dt = parse_date(date_str)
            if commit_dt.tzinfo is None:
                commit_dt = commit_dt.replace(tzinfo=target_tz)
            else:
                commit_dt = commit_dt.astimezone(target_tz)
        except Exception:
            continue

        # Strict month check: start_dt <= commit_dt < end_dt
        if not (start_dt <= commit_dt < end_dt):
            continue

        files: List[str] = []
        if include_files:
            files = get_commit_changed_files(repo.canonical_path, sha)

        commits.append(
            CommitEvidence(
                sha=sha,
                short_sha=sha[:7] if len(sha) >= 7 else sha,
                repository=repo.name,
                repo_path=repo.canonical_path,
                author_name=author_name,
                author_email=author_email,
                authored_at=commit_dt.isoformat(),
                subject=subject,
                body=body,
                files=files,
            )
        )

    return commits


def collect_git_evidence(
    repos: List[DiscoveredRepo],
    month_str: str,
    author_matcher: AuthorMatcher,
    timezone_str: str = "Asia/Jakarta",
    include_merges: bool = False,
    include_files: bool = True,
) -> List[CommitEvidence]:
    """Collects and aggregates student commits from all discovered repositories."""
    year, month = parse_month_string(month_str)
    start_dt, end_dt = get_month_range(year, month, timezone_str)

    all_commits: List[CommitEvidence] = []
    for repo in repos:
        repo_commits = collect_commits_from_repo(
            repo=repo,
            start_dt=start_dt,
            end_dt=end_dt,
            author_matcher=author_matcher,
            include_merges=include_merges,
            include_files=include_files,
        )
        all_commits.extend(repo_commits)

    # Sort chronologically
    all_commits.sort(key=lambda c: c.authored_at)
    return all_commits
