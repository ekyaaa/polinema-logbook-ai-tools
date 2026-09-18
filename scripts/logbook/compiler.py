"""LaTeX compilation service using latexmk and XeLaTeX."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CompileResult:
    success: bool
    pdf_path: Optional[str] = None
    output: str = ""
    error: str = ""
    exit_code: int = 0


def compile_latex(
    project_dir: Path,
    month_key: str,
    engine: str = "xelatex",
    dist_dir: Optional[Path] = None,
) -> CompileResult:
    """Compiles main.tex into dist/logbook-YYYY-MM.pdf using latexmk."""
    if dist_dir is None:
        dist_dir = project_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    main_tex = project_dir / "main.tex"
    if not main_tex.is_file():
        return CompileResult(
            success=False,
            error=f"Main TeX file not found: {main_tex}",
            exit_code=1,
        )

    # Check generated/current files exist
    current_dir = project_dir / "generated" / "current"
    if not (current_dir / "metadata.tex").is_file() or not (current_dir / "activities.tex").is_file():
        # Check if target month files exist and copy them over
        month_dir = project_dir / "generated" / month_key
        if (month_dir / "metadata.tex").is_file() and (month_dir / "activities.tex").is_file():
            current_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(month_dir / "metadata.tex", current_dir / "metadata.tex")
            shutil.copyfile(month_dir / "activities.tex", current_dir / "activities.tex")
        else:
            return CompileResult(
                success=False,
                error="Required generated files (metadata.tex, activities.tex) not found in generated/current/.",
                exit_code=1,
            )

    cmd = [
        "latexmk",
        "-g",
        f"-{engine}",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-outdir=dist",
        "main.tex",
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except Exception as ex:
        return CompileResult(
            success=False,
            error=f"Failed to execute latexmk: {ex}",
            exit_code=-1,
        )

    main_pdf = dist_dir / "main.pdf"
    target_pdf = dist_dir / f"logbook-{month_key}.pdf"

    if proc.returncode == 0 and main_pdf.is_file():
        # Move or copy main.pdf to logbook-YYYY-MM.pdf
        shutil.copyfile(main_pdf, target_pdf)
        return CompileResult(
            success=True,
            pdf_path=str(target_pdf),
            output=proc.stdout,
            error=proc.stderr,
            exit_code=proc.returncode,
        )
    else:
        return CompileResult(
            success=False,
            output=proc.stdout,
            error=proc.stderr,
            exit_code=proc.returncode,
        )
