"""Git author filtering and matching logic."""

from __future__ import annotations

import re
import subprocess
from typing import List, Optional, Set


class AuthorMatcher:
    """Matches git commit authors against configured student identities."""

    def __init__(
        self,
        names: Optional[List[str]] = None,
        emails: Optional[List[str]] = None,
    ):
        self.emails: Set[str] = {e.strip().lower() for e in (emails or []) if e and e.strip()}
        self.names: Set[str] = {n.strip().lower() for n in (names or []) if n and n.strip()}

        # If empty, fallback to git config
        if not self.emails or not self.names:
            self._load_git_config_defaults()

    def _load_git_config_defaults(self):
        try:
            res_email = subprocess.run(
                ["git", "config", "--get", "user.email"],
                capture_output=True,
                text=True,
                check=False,
            )
            if res_email.returncode == 0:
                e = res_email.stdout.strip().lower()
                if e:
                    self.emails.add(e)
        except Exception:
            pass

        try:
            res_name = subprocess.run(
                ["git", "config", "--get", "user.name"],
                capture_output=True,
                text=True,
                check=False,
            )
            if res_name.returncode == 0:
                n = res_name.stdout.strip().lower()
                if n:
                    self.names.add(n)
        except Exception:
            pass

    def matches(self, author_name: str, author_email: str) -> bool:
        """Determines whether the given author name/email belongs to the student."""
        norm_email = author_email.strip().lower()
        norm_name = author_name.strip().lower()

        # 1. Primary check: Email match
        if norm_email in self.emails:
            return True

        # 2. Check GitHub noreply format: 12345+username@users.noreply.github.com
        noreply_match = re.match(r"^\d+\+([^@]+)@users\.noreply\.github\.com$", norm_email)
        if noreply_match:
            handle = noreply_match.group(1).lower()
            if handle in self.names or handle in self.emails:
                return True

        # 3. Secondary check: Exact Name match
        if norm_name in self.names:
            return True

        # 4. Partial / Substring name match if names are distinctive (>= 4 chars)
        for configured_name in self.names:
            if len(configured_name) >= 4:
                if configured_name in norm_name or norm_name in configured_name:
                    return True

        return False
