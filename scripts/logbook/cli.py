"""Command-line interface for Polinema Monthly Logbook Generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .author import AuthorMatcher
from .compiler import compile_latex
from .config import AppConfig, load_app_config
from .discovery import discover_repositories
from .git_reader import collect_git_evidence, parse_month_string
from .renderer import render_latex_files
from .report import save_generation_report
from .schemas import (
    CommitEvidence,
    DailyActivityEntry,
    EvidenceLevel,
    MonthlyLogbook,
    MonthTimeline,
)
from .timeline import build_month_timeline, load_manual_evidence
from .validator import validate_logbook_entries


def get_month_key(raw_month: str) -> str:
    year, month = parse_month_string(raw_month)
    return f"{year:04d}-{month:02d}"


def get_month_dir(config: AppConfig, month_key: str) -> Path:
    d = config.project_dir / "generated" / month_key
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_discover(args: argparse.Namespace, config: AppConfig) -> int:
    root = args.root or config.internship.project_root
    if not root:
        print("[ERROR] project_root is not configured in internship.yaml and no --root was provided.", file=sys.stderr)
        return 1

    print(f"[*] Scanning for Git repositories under: {root}")
    repos = discover_repositories(root)
    print(f"[+] Found {len(repos)} Git repositories:")
    for r in repos:
        print(f"  - {r.name:24s} -> {r.canonical_path}")
    return 0


def cmd_scan(args: argparse.Namespace, config: AppConfig) -> int:
    month_key = get_month_key(args.month)
    month_dir = get_month_dir(config, month_key)

    root = args.root or config.internship.project_root
    if not root:
        print("[ERROR] project_root is not configured.", file=sys.stderr)
        return 1

    print(f"[*] Discovering repositories under {root}...")
    repos = discover_repositories(root)
    if not repos:
        print(f"[!] No Git repositories found under {root}.", file=sys.stderr)

    author_matcher = AuthorMatcher(
        names=config.internship.git_author_names,
        emails=config.internship.git_author_emails,
    )
    print(f"[*] Filtering commits for month {month_key} by author(s):")
    for e in author_matcher.emails:
        print(f"  - Email: {e}")
    for n in author_matcher.names:
        print(f"  - Name: {n}")

    commits = collect_git_evidence(
        repos=repos,
        month_str=month_key,
        author_matcher=author_matcher,
        timezone_str=config.logbook.timezone,
        include_merges=config.logbook.include_merges,
        include_files=config.logbook.include_file_names,
    )

    evidence_file = month_dir / "evidence.json"
    commits_data = [c.model_dump() for c in commits]
    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(commits_data, f, indent=2, ensure_ascii=False)

    print(f"[+] Collected {len(commits)} commits across {len(repos)} repositories.")
    print(f"[+] Evidence saved to: {evidence_file}")
    return 0


def cmd_timeline(args: argparse.Namespace, config: AppConfig) -> int:
    month_key = get_month_key(args.month)
    month_dir = get_month_dir(config, month_key)
    evidence_file = month_dir / "evidence.json"

    if not evidence_file.is_file():
        print(f"[ERROR] evidence.json not found in {month_dir}. Run scan or prepare first.", file=sys.stderr)
        return 1

    with open(evidence_file, "r", encoding="utf-8") as f:
        commits_data = json.load(f)
    commits = [CommitEvidence(**c) for c in commits_data]

    # Load manual evidence
    manual_dir = config.project_dir / "manual"
    manual_notes = load_manual_evidence(manual_dir, month_key)

    year, month = parse_month_string(month_key)
    timeline = build_month_timeline(
        year=year,
        month=month,
        commits=commits,
        manual_notes=manual_notes,
        working_days=config.logbook.working_days,
        only_working_days=True,
    )

    timeline_file = month_dir / "timeline.json"
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"[+] Monthly timeline built for {month_key} ({len(timeline.days)} working days).")
    print(f"[+] Timeline saved to: {timeline_file}")
    return 0


def cmd_prepare(args: argparse.Namespace, config: AppConfig) -> int:
    print(f"=== [STEP 1/3] DISCOVERY & SCAN ===")
    res_scan = cmd_scan(args, config)
    if res_scan != 0:
        return res_scan

    print(f"\n=== [STEP 2/3] TIMELINE GENERATION ===")
    res_tl = cmd_timeline(args, config)
    if res_tl != 0:
        return res_tl

    month_key = get_month_key(args.month)
    month_dir = get_month_dir(config, month_key)
    timeline_file = month_dir / "timeline.json"
    with open(timeline_file, "r", encoding="utf-8") as f:
        tl_data = json.load(f)
    timeline = MonthTimeline(**tl_data)

    direct_count = sum(1 for d in timeline.days if d.evidence_level == EvidenceLevel.DIRECT)
    manual_count = sum(1 for d in timeline.days if d.evidence_level == EvidenceLevel.MANUAL)
    none_count = sum(1 for d in timeline.days if d.evidence_level == EvidenceLevel.NONE)

    print(f"\n=== PREPARE SUMMARY ({month_key}) ===")
    print(f"Total Workdays: {len(timeline.days)}")
    print(f"Direct Git Evidence: {direct_count} days")
    print(f"Manual Evidence: {manual_count} days")
    print(f"Needs Review / Empty: {none_count} days")
    print(f"\nReady for AI Synthesis. Generate 'logbook.draft.json' using timeline.json.")
    return 0


def cmd_render(args: argparse.Namespace, config: AppConfig) -> int:
    month_key = get_month_key(args.month)
    month_dir = get_month_dir(config, month_key)

    final_file = month_dir / "logbook.final.json"
    draft_file = month_dir / "logbook.draft.json"

    if final_file.is_file():
        target_file = final_file
    elif draft_file.is_file():
        print("[!] Warning: logbook.final.json not found, rendering from logbook.draft.json")
        target_file = draft_file
    else:
        print(f"[ERROR] Neither logbook.final.json nor logbook.draft.json found in {month_dir}.", file=sys.stderr)
        return 1

    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        entries = [DailyActivityEntry(**e) for e in data]
        logbook = MonthlyLogbook(
            month=month_key,
            student_name=config.student.name,
            nim=config.student.nim,
            company=config.internship.company,
            entries=entries,
        )
    else:
        logbook = MonthlyLogbook(**data)

    current_dir = config.project_dir / "generated" / "current"
    render_latex_files(
        output_dir=month_dir,
        config=config,
        logbook=logbook,
        current_dir=current_dir,
    )

    print(f"[+] Rendered LaTeX files:")
    print(f"  - {month_dir / 'metadata.tex'}")
    print(f"  - {month_dir / 'activities.tex'}")
    print(f"  - Synced to {current_dir}")
    return 0


def cmd_compile(args: argparse.Namespace, config: AppConfig) -> int:
    month_key = get_month_key(args.month)
    engine = args.engine or config.logbook.latex_engine

    print(f"[*] Compiling LaTeX for month {month_key} using {engine}...")
    res = compile_latex(
        project_dir=config.project_dir,
        month_key=month_key,
        engine=engine,
    )

    if res.success:
        print(f"[+] Compilation SUCCESSFUL!")
        print(f"[+] Generated PDF: {res.pdf_path}")
        return 0
    else:
        print(f"[ERROR] Compilation FAILED with exit code {res.exit_code}:", file=sys.stderr)
        if res.error:
            print(res.error, file=sys.stderr)
        if res.output:
            print("--- Compiler Output (last 20 lines) ---", file=sys.stderr)
            lines = res.output.strip().split("\n")
            print("\n".join(lines[-20:]), file=sys.stderr)
        return 1


def cmd_finalize(args: argparse.Namespace, config: AppConfig) -> int:
    month_key = get_month_key(args.month)
    month_dir = get_month_dir(config, month_key)

    print(f"=== [STEP 1/4] VALIDATING ACTIVITIES ===")
    final_file = month_dir / "logbook.final.json"
    if not final_file.is_file():
        # Check draft
        draft_file = month_dir / "logbook.draft.json"
        if draft_file.is_file():
            print("[!] logbook.final.json missing, using logbook.draft.json")
            final_file = draft_file
        else:
            print(f"[ERROR] No logbook.final.json or logbook.draft.json in {month_dir}.", file=sys.stderr)
            return 1

    timeline_file = month_dir / "timeline.json"
    if not timeline_file.is_file():
        print(f"[ERROR] timeline.json missing in {month_dir}.", file=sys.stderr)
        return 1

    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline = MonthTimeline(**json.load(f))

    with open(final_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if isinstance(raw_data, list):
        entries = [DailyActivityEntry(**e) for e in raw_data]
        logbook = MonthlyLogbook(
            month=month_key,
            student_name=config.student.name,
            nim=config.student.nim,
            company=config.internship.company,
            entries=entries,
        )
    else:
        logbook = MonthlyLogbook(**raw_data)

    validation = validate_logbook_entries(
        entries=logbook.entries,
        timeline=timeline,
        max_words=config.logbook.max_activity_words,
        allow_inferred=config.logbook.allow_inferred_activity,
    )

    if validation.warnings:
        print("[!] Validation Warnings:")
        for w in validation.warnings:
            print(f"  - {w}")

    if not validation.is_valid:
        print("[ERROR] Validation failed with errors:", file=sys.stderr)
        for err in validation.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("[+] Validation PASSED.")

    print(f"\n=== [STEP 2/4] RENDERING LATEX ===")
    res_render = cmd_render(args, config)
    if res_render != 0:
        return res_render

    print(f"\n=== [STEP 3/4] COMPILING PDF ===")
    res_compile = cmd_compile(args, config)
    if res_compile != 0:
        return res_compile

    print(f"\n=== [STEP 4/4] GENERATING REPORT ===")
    pdf_path = config.project_dir / "dist" / f"logbook-{month_key}.pdf"
    report_file = month_dir / "generation-report.md"
    report = save_generation_report(
        output_file=report_file,
        timeline=timeline,
        logbook=logbook,
        pdf_path=str(pdf_path) if pdf_path.is_file() else None,
    )
    print(f"[+] Generation report saved to: {report_file}")
    print(f"\n=== ALL STEPS FINISHED SUCCESSFULLY ===")
    print(f"PDF Location: {report.pdf_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="logbook",
        description="Polinema Monthly Internship Logbook Generator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # discover
    p_disc = subparsers.add_parser("discover", help="Discover local Git repositories")
    p_disc.add_argument("--root", type=str, help="Custom project root directory to scan")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan and collect student commits for a target month")
    p_scan.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")
    p_scan.add_argument("--root", type=str, help="Custom project root directory to scan")

    # timeline
    p_tl = subparsers.add_parser("timeline", help="Build month timeline binding git and manual notes")
    p_tl.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")

    # prepare
    p_prep = subparsers.add_parser("prepare", help="Run discover, scan, and timeline in sequence")
    p_prep.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")
    p_prep.add_argument("--root", type=str, help="Custom project root directory to scan")

    # render
    p_rnd = subparsers.add_parser("render", help="Render LaTeX metadata and activities files")
    p_rnd.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")

    # compile
    p_cmp = subparsers.add_parser("compile", help="Compile LaTeX into dist/logbook-YYYY-MM.pdf")
    p_cmp.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")
    p_cmp.add_argument("--engine", type=str, choices=["xelatex", "pdflatex"], help="LaTeX engine")

    # finalize
    p_fin = subparsers.add_parser("finalize", help="Validate, render, compile, and report")
    p_fin.add_argument("--month", type=str, required=True, help="Target month (YYYY-MM)")
    p_fin.add_argument("--engine", type=str, choices=["xelatex", "pdflatex"], help="LaTeX engine")

    args = parser.parse_args()
    config = load_app_config()

    handlers = {
        "discover": cmd_discover,
        "scan": cmd_scan,
        "timeline": cmd_timeline,
        "prepare": cmd_prepare,
        "render": cmd_render,
        "compile": cmd_compile,
        "finalize": cmd_finalize,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)

    exit_code = handler(args, config)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
