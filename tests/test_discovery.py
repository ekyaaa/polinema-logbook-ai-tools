import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts.logbook.discovery import discover_repositories


class TestDiscovery(unittest.TestCase):
    def test_discover_repositories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create repo1
            repo1 = tmp / "project-a"
            repo1.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=str(repo1), capture_output=True, check=True)

            # Create repo2 inside a subfolder
            repo2 = tmp / "nested" / "project-b"
            repo2.mkdir(parents=True)
            subprocess.run(["git", "init", "-b", "main"], cwd=str(repo2), capture_output=True, check=True)

            # Create ignored repo inside node_modules
            ignored_repo = tmp / "node_modules" / "some-lib"
            ignored_repo.mkdir(parents=True)
            subprocess.run(["git", "init", "-b", "main"], cwd=str(ignored_repo), capture_output=True, check=True)

            discovered = discover_repositories(tmp)
            names = [r.name for r in discovered]

            self.assertIn("project-a", names)
            self.assertIn("project-b", names)
            self.assertNotIn("some-lib", names)


if __name__ == "__main__":
    unittest.main()
