import unittest
from pathlib import Path
import tempfile
import yaml

from scripts.logbook.config import (
    AbsenceItem,
    get_absences_map_by_date,
    load_absences_config,
)
from scripts.logbook.renderer import render_activities_tex
from scripts.logbook.schemas import (
    ActivityStatus,
    CommitEvidence,
    DailyActivityEntry,
    EvidenceLevel,
    MonthTimeline,
)
from scripts.logbook.timeline import build_month_timeline
from scripts.logbook.validator import validate_logbook_entries


class TestAbsences(unittest.TestCase):
    def test_load_and_expand_absences(self):
        items = [
            AbsenceItem(
                start_date="2026-07-23",
                end_date="2026-07-24",
                category="Izin",
                reason="Izin: Mengikuti Lomba di Solo",
            ),
            AbsenceItem(
                start_date="2026-08-10",
                end_date="2026-08-10",
                category="Sakit",
                reason="Sakit",
            ),
        ]
        mapping = get_absences_map_by_date(items)
        self.assertIn("2026-07-23", mapping)
        self.assertIn("2026-07-24", mapping)
        self.assertIn("2026-08-10", mapping)
        self.assertEqual(mapping["2026-07-23"].category, "Izin")
        self.assertEqual(mapping["2026-08-10"].category, "Sakit")

    def test_timeline_with_absences_and_weekend_policy(self):
        # 12 September 2026 is a Saturday
        absences = {
            "2026-09-01": AbsenceItem("2026-09-01", "2026-09-01", "Izin", "Izin: Mengikuti Lomba KMIPN"),
            "2026-09-12": AbsenceItem("2026-09-12", "2026-09-12", "Izin", "Bimbingan skripsi offline"),
            "2026-09-28": AbsenceItem("2026-09-28", "2026-09-28", "Sakit", "Sakit"),
        }
        timeline = build_month_timeline(
            year=2026,
            month=9,
            commits=[],
            manual_notes={},
            absences=absences,
            working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            only_working_days=True,
        )

        dates = [d.date for d in timeline.days]
        # 2026-09-01 (Tuesday) and 2026-09-28 (Monday) must be present
        self.assertIn("2026-09-01", dates)
        self.assertIn("2026-09-28", dates)

        # 2026-09-12 (Saturday) must NOT be present because only working days are recorded
        self.assertNotIn("2026-09-12", dates)

        # Check evidence level of absent days
        day_01 = next(d for d in timeline.days if d.date == "2026-09-01")
        self.assertEqual(day_01.evidence_level, EvidenceLevel.ABSENT)
        self.assertTrue(day_01.is_absent)
        self.assertEqual(day_01.absence_category, "Izin")

        day_28 = next(d for d in timeline.days if d.date == "2026-09-28")
        self.assertEqual(day_28.evidence_level, EvidenceLevel.ABSENT)
        self.assertTrue(day_28.is_absent)
        self.assertEqual(day_28.absence_category, "Sakit")

    def test_renderer_outputs_red_text_for_absences(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-01",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.ABSENT,
                check_in="Izin",
                check_out="Izin",
                activity="Izin: Mengikuti Lomba KMIPN",
            ),
            DailyActivityEntry(
                date="2026-09-28",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.ABSENT,
                check_in="Sakit",
                check_out="Sakit",
                activity="Sakit",
            ),
        ]
        tex = render_activities_tex(entries)
        # Verify check_in, check_out, and activity are wrapped with \textcolor{red}{...}
        self.assertIn(r"\textcolor{red}{Izin}", tex)
        self.assertIn(r"\textcolor{red}{Izin: Mengikuti Lomba KMIPN}", tex)
        self.assertIn(r"\textcolor{red}{Sakit}", tex)

    def test_validator_with_absences(self):
        absences = {
            "2026-09-28": AbsenceItem("2026-09-28", "2026-09-28", "Sakit", "Sakit"),
        }
        timeline = build_month_timeline(
            year=2026,
            month=9,
            commits=[],
            absences=absences,
            only_working_days=True,
        )

        entries = []
        for d in timeline.days:
            if d.date == "2026-09-28":
                entries.append(
                    DailyActivityEntry(
                        date=d.date,
                        status=ActivityStatus.OK,
                        evidence_level=EvidenceLevel.ABSENT,
                        check_in="Sakit",
                        check_out="Sakit",
                        activity="Sakit",
                    )
                )
            else:
                entries.append(
                    DailyActivityEntry(
                        date=d.date,
                        status=ActivityStatus.OK,
                        evidence_level=EvidenceLevel.INFERRED,
                        activity="Menganalisis arsitektur sistem.",
                    )
                )

        result = validate_logbook_entries(entries=entries, timeline=timeline)
        self.assertTrue(result.is_valid, f"Validation failed with: {result.errors}")


if __name__ == "__main__":
    unittest.main()
