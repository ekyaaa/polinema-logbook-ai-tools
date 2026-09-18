"""Deterministic LaTeX escaping utility."""

from __future__ import annotations

import re


def escape_latex(text: str | None) -> str:
    """Escapes special LaTeX characters in a given string.

    Characters handled:
    \\ -> \\textbackslash{}
    { -> \\{
    } -> \\}
    & -> \\&
    % -> \\%
    $ -> \\$
    # -> \\#
    _ -> \\_
    ~ -> \\textasciitilde{}
    ^ -> \\textasciicircum{}
    """
    if not text:
        return ""

    # Use Unicode private-use placeholders to prevent double-escaping
    BS_PH = "\uE000"
    LB_PH = "\uE001"
    RB_PH = "\uE002"
    TL_PH = "\uE003"
    CR_PH = "\uE004"

    res = text.replace("\\", BS_PH)
    res = res.replace("{", LB_PH)
    res = res.replace("}", RB_PH)
    res = res.replace("~", TL_PH)
    res = res.replace("^", CR_PH)

    # Replace standard specials
    res = res.replace("&", r"\&")
    res = res.replace("%", r"\%")
    res = res.replace("$", r"\$")
    res = res.replace("#", r"\#")
    res = res.replace("_", r"\_")

    # Restore placeholders into valid LaTeX commands
    res = res.replace(LB_PH, r"\{")
    res = res.replace(RB_PH, r"\}")
    res = res.replace(BS_PH, r"\textbackslash{}")
    res = res.replace(TL_PH, r"\textasciitilde{}")
    res = res.replace(CR_PH, r"\textasciicircum{}")

    # Normalize multiple whitespace
    res = re.sub(r"[ \t]+", " ", res)
    return res.strip()
