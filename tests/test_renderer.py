import unittest
from scripts.logbook.config import AppConfig, InternshipConfig, LogbookConfig, StudentConfig
from scripts.logbook.renderer import format_indonesian_date, render_activities_tex, render_metadata_tex
from scripts.logbook.schemas import ActivityStatus, DailyActivityEntry, EvidenceLevel


class TestRenderer(unittest.TestCase):
    def test_format_indonesian_date(self):
        s = format_indonesian_date("2026-09-14", include_day_name=True)
        self.assertEqual(s, "Senin, 14 September 2026")

        s_no_day = format_indonesian_date("2026-09-14", include_day_name=False)
        self.assertEqual(s_no_day, "14 September 2026")

    def test_render_activities_tex(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-14",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.DIRECT,
                activity="Menguji modul user_auth & session.",
                check_in="07:00",
                check_out="16:20",
            ),
            DailyActivityEntry(
                date="2026-09-15",
                status=ActivityStatus.NEEDS_REVIEW,
                evidence_level=EvidenceLevel.NONE,
                activity=None,
            ),
        ]
        tex = render_activities_tex(entries)
        self.assertIn(r"\LogbookEntry", tex)
        self.assertIn(r"user\_auth \& session.", tex)
        self.assertIn(r"\textit{[Perlu Review Kegiatan / Tidak Ada Catatan]}", tex)

    def test_render_metadata_tex(self):
        config = AppConfig(
            project_dir=None,
            student=StudentConfig(
                name="Ekya M. Hasfi",
                nim="2341720111",
                program="D-IV TI",
                institution="Polinema",
                academic_advisor="Dosen A",
                field_supervisor="Pembimbing B",
            ),
            internship=InternshipConfig(company="PT SAI"),
            logbook=LogbookConfig(),
        )
        meta = render_metadata_tex(config, 2026, 9)
        self.assertIn(r"\newcommand{\StudentName}{Ekya M. Hasfi}", meta)
        self.assertIn(r"\newcommand{\StudentNIM}{2341720111}", meta)
        self.assertIn(r"\newcommand{\CompanyFullName}{PT SAI}", meta)
        self.assertIn(r"\newcommand{\LogbookPeriod}{01 September 2026 -- 30 September 2026}", meta)


if __name__ == "__main__":
    unittest.main()
