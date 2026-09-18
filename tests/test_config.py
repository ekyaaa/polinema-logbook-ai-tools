import tempfile
import unittest
from pathlib import Path

from scripts.logbook.config import (
    AppConfig,
    StudentConfig,
    InternshipConfig,
    LogbookConfig,
    detect_git_defaults,
    is_config_complete,
    load_app_config,
    save_app_config,
)


class TestConfig(unittest.TestCase):
    def test_detect_git_defaults(self):
        info = detect_git_defaults()
        self.assertIn("name", info)
        self.assertIn("email", info)

    def test_save_and_load_config_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template_dir = tmp_path / "template"
            template_dir.mkdir()

            config_data = {
                "student": {
                    "name": "Budi Santoso",
                    "nim": "2341720999",
                    "program": "D-IV Teknik Informatika",
                    "institution": "Politeknik Negeri Malang",
                    "academic_advisor": "Dr. Dosen, M.Kom.",
                    "field_supervisor": "Mentor A",
                },
                "internship": {
                    "company": "PT Inovasi",
                    "division": "Tech",
                    "project_root": "/tmp/project",
                    "git_authors": {
                        "names": ["budi"],
                        "emails": ["budi@example.com"],
                    },
                },
                "logbook": {
                    "timezone": "Asia/Jakarta",
                    "working_days": ["monday", "tuesday"],
                    "check_in": "08:00",
                    "check_out": "17:00",
                    "allow_inferred_activity": True,
                },
            }

            saved_file = save_app_config(config_data, root_dir=tmp_path)
            self.assertTrue(saved_file.is_file())

            loaded = load_app_config(tmp_path)
            self.assertEqual(loaded.student.name, "Budi Santoso")
            self.assertEqual(loaded.student.nim, "2341720999")
            self.assertEqual(loaded.internship.company, "PT Inovasi")
            self.assertEqual(loaded.internship.git_author_names, ["budi"])
            self.assertTrue(loaded.logbook.allow_inferred_activity)
            self.assertTrue(is_config_complete(loaded))

    def test_incomplete_config(self):
        empty_cfg = AppConfig(
            project_dir=Path("/tmp"),
            student=StudentConfig(name="", nim=""),
            internship=InternshipConfig(company=""),
            logbook=LogbookConfig(),
        )
        self.assertFalse(is_config_complete(empty_cfg))


if __name__ == "__main__":
    unittest.main()
