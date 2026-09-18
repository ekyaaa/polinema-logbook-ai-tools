import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.logbook.author import AuthorMatcher
from scripts.logbook.config import AppConfig, InternshipConfig, LogbookConfig, StudentConfig
from scripts.logbook.discovery import discover_repositories
from scripts.logbook.git_reader import collect_git_evidence
from scripts.logbook.renderer import render_latex_files
from scripts.logbook.schemas import ActivityStatus, DailyActivityEntry, EvidenceLevel, MonthlyLogbook
from scripts.logbook.timeline import build_month_timeline
from scripts.logbook.validator import validate_logbook_entries


class TestEndToEnd(unittest.TestCase):
    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            work_root = Path(tmpdir) / "workspace"
            work_root.mkdir()

            # 1. Initialize mock repo
            repo = work_root / "mobile-app"
            repo.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tester Ekya"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "tester@ekya.id"], check=True)

            # Create commit on 2026-09-04
            test_file = repo / "main.dart"
            test_file.write_text("// test code\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)

            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = "2026-09-04T10:00:00+07:00"
            env["GIT_COMMITTER_DATE"] = "2026-09-04T10:00:00+07:00"
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-m", "feat: setup mobile authentication"],
                env=env,
                check=True,
                capture_output=True,
            )

            # 2. Discovery
            repos = discover_repositories(work_root)
            self.assertEqual(len(repos), 1)
            self.assertEqual(repos[0].name, "mobile-app")

            # 3. Commit Collection
            matcher = AuthorMatcher(names=["Tester Ekya"], emails=["tester@ekya.id"])
            commits = collect_git_evidence(
                repos=repos,
                month_str="2026-09",
                author_matcher=matcher,
            )
            self.assertEqual(len(commits), 1)
            self.assertEqual(commits[0].subject, "feat: setup mobile authentication")

            # 4. Timeline
            timeline = build_month_timeline(
                year=2026,
                month=9,
                commits=commits,
                manual_notes={"2026-09-01": ["Kickoff meeting"]},
            )
            self.assertGreater(len(timeline.days), 15)

            # 5. Synthesize Activities
            entries = []
            for d in timeline.days:
                if d.date == "2026-09-04":
                    entries.append(
                        DailyActivityEntry(
                            date=d.date,
                            status=ActivityStatus.OK,
                            evidence_level=EvidenceLevel.DIRECT,
                            activity="Mengimplementasikan modul autentikasi mobile pada repositori mobile-app.",
                            repositories=["mobile-app"],
                            evidence_refs=[f"mobile-app:{commits[0].short_sha}"],
                        )
                    )
                elif d.date == "2026-09-01":
                    entries.append(
                        DailyActivityEntry(
                            date=d.date,
                            status=ActivityStatus.OK,
                            evidence_level=EvidenceLevel.MANUAL,
                            activity="Mengikuti pertemuan koordinasi kickoff proyek.",
                            repositories=[],
                            evidence_refs=[],
                        )
                    )
                else:
                    entries.append(
                        DailyActivityEntry(
                            date=d.date,
                            status=ActivityStatus.NEEDS_REVIEW,
                            evidence_level=EvidenceLevel.NONE,
                            activity=None,
                        )
                    )

            # 6. Validate
            val_res = validate_logbook_entries(entries, timeline)
            self.assertTrue(val_res.is_valid, f"Validation failed: {val_res.errors}")

            # 7. Render LaTeX
            app_dir = Path(__file__).resolve().parent.parent
            config = AppConfig(
                project_dir=app_dir,
                student=StudentConfig(
                    name="Tester Ekya",
                    nim="2341720111",
                    program="D-IV TI",
                    institution="Polinema",
                    academic_advisor="Advisor A",
                    field_supervisor="Supervisor B",
                ),
                internship=InternshipConfig(company="PT Mock"),
                logbook=LogbookConfig(),
            )

            out_dir = Path(tmpdir) / "generated" / "2026-09"
            logbook = MonthlyLogbook(
                month="2026-09",
                student_name="Tester Ekya",
                nim="2341720111",
                company="PT Mock",
                entries=entries,
            )
            render_latex_files(out_dir, config, logbook)

            self.assertTrue((out_dir / "metadata.tex").is_file())
            self.assertTrue((out_dir / "activities.tex").is_file())


if __name__ == "__main__":
    unittest.main()
