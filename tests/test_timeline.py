import unittest
from scripts.logbook.schemas import CommitEvidence, EvidenceLevel
from scripts.logbook.timeline import build_month_timeline


class TestTimeline(unittest.TestCase):
    def test_timeline_structure_and_evidence(self):
        fake_commits = [
            CommitEvidence(
                sha="1111111111111111111111111111111111111111",
                short_sha="1111111",
                repository="backend",
                repo_path="/fake/backend",
                author_name="Ekya",
                author_email="ekyamuhammad@gmail.com",
                authored_at="2026-09-04T10:00:00+07:00",
                subject="feat: login endpoint",
            )
        ]

        manual_notes = {
            "2026-09-01": ["Meeting koordinasi proyek"]
        }

        timeline = build_month_timeline(
            year=2026,
            month=9,
            commits=fake_commits,
            manual_notes=manual_notes,
            working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            only_working_days=True,
        )

        self.assertEqual(timeline.month, "2026-09")
        self.assertIn("backend", timeline.repositories)

        # 2026-09-01 should be MANUAL
        day_01 = next(d for d in timeline.days if d.date == "2026-09-01")
        self.assertEqual(day_01.evidence_level, EvidenceLevel.MANUAL)
        self.assertEqual(day_01.manual_notes, ["Meeting koordinasi proyek"])

        # 2026-09-04 should be DIRECT
        day_04 = next(d for d in timeline.days if d.date == "2026-09-04")
        self.assertEqual(day_04.evidence_level, EvidenceLevel.DIRECT)
        self.assertEqual(len(day_04.commits), 1)

        # 2026-09-02 should be NONE
        day_02 = next(d for d in timeline.days if d.date == "2026-09-02")
        self.assertEqual(day_02.evidence_level, EvidenceLevel.NONE)


if __name__ == "__main__":
    unittest.main()
