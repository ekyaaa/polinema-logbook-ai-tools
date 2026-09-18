import unittest
from scripts.logbook.schemas import (
    ActivityStatus,
    CommitEvidence,
    DailyActivityEntry,
    DayTimeline,
    EvidenceLevel,
    MonthTimeline,
)
from scripts.logbook.validator import validate_logbook_entries


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.timeline = MonthTimeline(
            month="2026-09",
            repositories=["shin-ac"],
            days=[
                DayTimeline(
                    date="2026-09-01",
                    day_name="Selasa",
                    working_day=True,
                    evidence_level=EvidenceLevel.DIRECT,
                    repositories=["shin-ac"],
                    commits=[
                        CommitEvidence(
                            sha="abc1234567890",
                            short_sha="abc1234",
                            repository="shin-ac",
                            repo_path="/path",
                            author_name="ekyaaa",
                            author_email="ekyamuhammad@gmail.com",
                            authored_at="2026-09-01T10:00:00+07:00",
                            subject="feat: login",
                        )
                    ],
                ),
                DayTimeline(
                    date="2026-09-02",
                    day_name="Rabu",
                    working_day=True,
                    evidence_level=EvidenceLevel.NONE,
                    repositories=[],
                    commits=[],
                ),
            ],
        )

    def test_valid_entries(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-01",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.DIRECT,
                activity="Mengimplementasikan fitur login pada modul shin-ac.",
                repositories=["shin-ac"],
                evidence_refs=["shin-ac:abc1234"],
            ),
            DailyActivityEntry(
                date="2026-09-02",
                status=ActivityStatus.NEEDS_REVIEW,
                evidence_level=EvidenceLevel.NONE,
                activity=None,
                repositories=[],
                evidence_refs=[],
            ),
        ]
        res = validate_logbook_entries(entries, self.timeline)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.errors), 0)

    def test_fabricated_entry_on_empty_day_fails(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-01",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.DIRECT,
                activity="Mengimplementasikan fitur login.",
                repositories=["shin-ac"],
                evidence_refs=["shin-ac:abc1234"],
            ),
            DailyActivityEntry(
                date="2026-09-02",
                status=ActivityStatus.OK,  # Should be rejected because day is NONE
                evidence_level=EvidenceLevel.DIRECT,
                activity="Mengarang pekerjaan tanpa bukti.",
                repositories=["shin-ac"],
                evidence_refs=[],
            ),
        ]
        res = validate_logbook_entries(entries, self.timeline)
        self.assertFalse(res.is_valid)
    def test_inferred_activity_allowed(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-01",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.DIRECT,
                activity="Mengimplementasikan fitur login.",
                repositories=["shin-ac"],
                evidence_refs=["shin-ac:abc1234"],
            ),
            DailyActivityEntry(
                date="2026-09-02",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.INFERRED,
                activity="Mempersiapkan perancangan antarmuka pengguna pada proyek shin-ac.",
                repositories=["shin-ac"],
                evidence_refs=[],
            ),
        ]
        res = validate_logbook_entries(entries, self.timeline, allow_inferred=True)
        self.assertTrue(res.is_valid)

    def test_inferred_activity_rejected_when_disabled(self):
        entries = [
            DailyActivityEntry(
                date="2026-09-01",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.DIRECT,
                activity="Mengimplementasikan fitur login.",
                repositories=["shin-ac"],
                evidence_refs=["shin-ac:abc1234"],
            ),
            DailyActivityEntry(
                date="2026-09-02",
                status=ActivityStatus.OK,
                evidence_level=EvidenceLevel.INFERRED,
                activity="Mempersiapkan perancangan antarmuka pengguna pada proyek shin-ac.",
                repositories=["shin-ac"],
                evidence_refs=[],
            ),
        ]
        res = validate_logbook_entries(entries, self.timeline, allow_inferred=False)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("allow_inferred is disabled" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()
