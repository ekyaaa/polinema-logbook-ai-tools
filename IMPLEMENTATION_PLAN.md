# Project Prompt — Polinema Monthly Logbook Generator

You are the engineering agent responsible for building a local-first monthly internship logbook generator for Politeknik Negeri Malang students.

The project already contains a LaTeX logbook template.

I will also provide a local folder containing the source code of another project named `git_trace`. Here's the folder path: `~/Project/git_trace`.

Treat `git_trace` as an implementation reference for Git crawling, commit aggregation, timeline logic, and AI-assisted activity generation.

Do not assume the two projects should have the same architecture.

Your responsibility is to understand the useful behavior from `git_trace`, extract the underlying ideas, and implement them cleanly inside the current LaTeX project.

---

# 1. Primary Goal

Build a tool with this experience:

```text
User runs monthly logbook workflow
        ↓
Agent asks:
"Logbook bulan dan tahun berapa yang ingin dibuat?"
        ↓
User answers:
"September 2026"
        ↓
Tool scans configured internship project root
        ↓
Tool discovers all relevant local Git repositories
        ↓
Tool collects Git activity for September 2026
        ↓
Tool groups evidence by date
        ↓
Agent generates professional Indonesian activity descriptions
        ↓
Tool validates structured output
        ↓
Tool renders generated LaTeX entries
        ↓
Tool compiles final PDF
```

The final system should be usable every month.

---

# 2. Core Architecture Rule

Always preserve:

```text
Git = evidence
AI = interpretation
JSON = contract
LaTeX = presentation
MCP = optional transport
```

Do not mix these responsibilities.

---

# 3. First Action When Starting the Project

Before implementing code, inspect the current project.

Understand:

```text
LaTeX file structure
main entrypoint
table structure
student metadata
date format
attendance columns
activity columns
signature section
existing scripts
existing workflows
existing configuration
```

Do not refactor blindly.

Write down the current structure before modifying it.

---

# 4. Local `git_trace` Reference

The user will provide a local folder path for `git_trace`.

Once the folder is available, inspect it as a reference.

You must identify:

```text
repository discovery logic
Git history reading
date/month filtering
author filtering
commit parsing
multi-repository behavior
daily aggregation
prompt structure
AI synthesis behavior
empty-day behavior
output models
error handling
```

Create a short internal mapping:

```text
git_trace behavior
→ useful concept
→ target implementation
```

Example:

```text
git_trace recursive repo scan
→ useful
→ reimplement in discovery.py

git_trace monthly commit aggregation
→ useful
→ reimplement in git_reader.py + timeline.py

git_trace UI-specific logic
→ not useful
→ do not copy
```

Do not copy code simply because it exists.

Prefer rewriting the behavior in a way that fits this project.

---

# 5. Important Constraint About `.git`

Use `.git` only for repository discovery.

Do not manually parse:

```text
.git/objects
.git/refs
.git/logs
.git/index
```

After discovering a repository, use Git CLI.

Preferred commands:

```bash
git rev-parse
git log
git show
git diff-tree
git config
```

This is required for correct support of:

```text
packed objects
packed refs
worktrees
submodules
normal repositories
```

---

# 6. Technology Direction

Use:

```text
Python 3.11+
LaTeX
latexmk
Git CLI
JSON
YAML
```

Recommended Python dependencies:

```text
pydantic
PyYAML
python-dateutil
rich
```

Avoid unnecessary heavy frameworks.

The first version must work as a local CLI.

---

# 7. Target Repository Structure

Move toward:

```text
project/
│
├── main.tex
├── pyproject.toml
├── latexmkrc
│
├── config/
│   ├── student.yaml
│   ├── internship.yaml
│   └── logbook.yaml
│
├── template/
│   ├── preamble.tex
│   ├── commands.tex
│   ├── cover.tex
│   ├── identity.tex
│   ├── logbook-table.tex
│   └── signatures.tex
│
├── generated/
│   ├── current/
│   └── YYYY-MM/
│
├── manual/
│   └── YYYY-MM.yaml
│
├── prompts/
│   ├── system.md
│   ├── daily-activity.md
│   ├── monthly-editor.md
│   └── workflow-agent.md
│
├── scripts/
│   └── logbook/
│       ├── cli.py
│       ├── config.py
│       ├── discovery.py
│       ├── git_reader.py
│       ├── author.py
│       ├── timeline.py
│       ├── schemas.py
│       ├── validator.py
│       ├── latex_escape.py
│       ├── renderer.py
│       ├── compiler.py
│       └── report.py
│
├── workflows/
│   └── generate-monthly-logbook.md
│
└── tests/
```

Do not force this structure if the existing project already has an equivalent clean structure.

Preserve good existing architecture where possible.

---

# 8. Configuration Requirements

Create persistent project configuration.

Example:

```yaml
# config/student.yaml

name: "Nama Mahasiswa"
nim: "2241XXXXXX"
program: "D-IV Teknik Informatika"
institution: "Politeknik Negeri Malang"
```

```yaml
# config/internship.yaml

company: "Nama Perusahaan"
division: "Software Development"

project_root: "/home/user/Project/Internship"

git_authors:
  names:
    - "Nama Mahasiswa"
  emails:
    - "student@example.com"
```

```yaml
# config/logbook.yaml

timezone: "Asia/Jakarta"

working_days:
  - monday
  - tuesday
  - wednesday
  - thursday
  - friday

default_hours:
  check_in: "08:00"
  check_out: "17:00"

git:
  include_merges: false
  include_file_names: true
  include_diff_stat: true

ai:
  allow_inferred_activity: false
  max_activity_words: 35

latex:
  engine: "xelatex"
```

The workflow must not repeatedly ask for values already stored here.

---

# 9. Repository Discovery Requirements

Implement a recursive repository scanner.

It receives:

```text
project_root
```

It must support:

```text
.git directory
.git file
nested repositories
multiple sibling repositories
ignored folders
unreadable directories
duplicate roots
worktrees
submodules
```

Use:

```bash
git rev-parse --show-toplevel
```

to canonicalize repository roots.

Add `.logbookignore`.

Suggested defaults:

```text
node_modules
vendor
dist
build
.next
.gradle
.dart_tool
Pods
coverage
.cache
tmp
backup
archive
```

---

# 10. Git Collection Requirements

For target month:

```text
YYYY-MM
```

calculate:

```text
first moment of month
first moment of next month
```

Use:

```text
start <= commit timestamp < end
```

Do not use fragile `23:59:59` month endings.

Collect:

```text
SHA
author name
author email
authored date
subject
body
repository
changed filenames
optional diff stats
```

Default to excluding merge commits.

Do not read full source files unless absolutely necessary.

---

# 11. Author Matching

Do not assume the student has only one Git identity.

Support:

```text
multiple names
multiple emails
```

Prefer email matching.

Repository-local and global Git configuration may be used as fallback context.

Never silently include every contributor's commits.

---

# 12. Evidence Model

Every generated activity must have an evidence level:

```text
direct
manual
inferred
none
```

Definitions:

```text
direct
    same-day Git evidence exists

manual
    student supplied a manual activity

inferred
    activity conservatively inferred from nearby evidence

none
    insufficient evidence
```

Inference must be disabled by default.

If evidence is insufficient:

```text
status = NEEDS_REVIEW
```

Do not fabricate an activity.

---

# 13. Manual Evidence

Support:

```text
manual/YYYY-MM.yaml
```

Example:

```yaml
2026-09-03:
  - "Diskusi requirement bersama pembimbing lapangan."

2026-09-10:
  - "Presentasi progress sprint."
```

Reason:

```text
no commit != no work
```

Manual evidence is valid evidence.

---

# 14. Timeline Requirements

After Git extraction, generate a deterministic monthly timeline.

The timeline must contain every expected workday.

AI must not decide what dates exist.

Example:

```json
{
  "month": "2026-09",
  "days": [
    {
      "date": "2026-09-01",
      "working_day": true,
      "evidence_level": "direct",
      "commits": []
    }
  ]
}
```

Weekend behavior comes from config.

Holiday support can be added later.

---

# 15. AI Context Policy

Do not give the AI entire repositories.

Default context:

```text
date
repository
commit subject
commit body
changed filenames
small diff stats
manual notes
```

Only use code diff as fallback when commit context is too ambiguous.

Before sending diff content:

```text
redact secrets
exclude binary files
exclude generated files
exclude environment files
truncate large patches
```

Never expose:

```text
.env
private keys
API tokens
passwords
service credentials
private customer data
```

---

# 16. AI Output Contract

AI must return structured JSON.

Example:

```json
{
  "date": "2026-09-14",
  "status": "OK",
  "evidence_level": "direct",
  "confidence": 0.94,
  "activity": "Memperbaiki mekanisme autentikasi sesi pada perangkat mobile serta menyesuaikan pengujian validasi token.",
  "repositories": [
    "backend"
  ],
  "evidence_refs": [
    "backend:abc123"
  ]
}
```

For unsupported date:

```json
{
  "date": "2026-09-15",
  "status": "NEEDS_REVIEW",
  "evidence_level": "none",
  "confidence": 0.0,
  "activity": null,
  "repositories": [],
  "evidence_refs": []
}
```

Validate all AI output with Pydantic.

Do not trust raw model output.

---

# 17. AI Writing Rules

Generated logbook activity must:

```text
use formal Indonesian
describe actual work
prefer 1 concise sentence
avoid excessive Git terminology
avoid unsupported claims
avoid confidential detail
avoid exaggeration
```

Good verbs:

```text
Mengembangkan
Mengimplementasikan
Memperbaiki
Mengintegrasikan
Menguji
Menganalisis
Merancang
Mengoptimalkan
Menyesuaikan
Memvalidasi
Mendokumentasikan
```

Avoid writing:

```text
melakukan commit
push Git
update repository
```

unless repository management itself was the real activity.

---

# 18. Monthly Editing

After daily generation, perform one monthly editing pass.

The editor may:

```text
improve readability
reduce repeated phrasing
vary sentence openings
remove unnecessary technical noise
```

The editor may not:

```text
change dates
invent new work
change repositories
change evidence refs
increase confidence
turn NEEDS_REVIEW into OK
```

---

# 19. LaTeX Rules

AI does not generate the whole document.

AI produces JSON.

Python renders safe LaTeX.

Desired structure:

```tex
\input{template/preamble}
\input{template/commands}
\input{generated/current/metadata}

\begin{document}

\input{template/cover}
\input{template/identity}

\LogbookTableStart
\input{generated/current/activities}
\LogbookTableEnd

\input{template/signatures}

\end{document}
```

Generated entries:

```tex
\LogbookEntry
  {14 September 2026}
  {08:00}
  {17:00}
  {Memperbaiki mekanisme autentikasi sesi ...}
```

---

# 20. LaTeX Escaping

All AI text must be escaped before writing `.tex`.

Handle:

```text
&
%
$
#
_
{
}
~
^
\
```

This is deterministic application logic.

Do not ask AI to escape LaTeX manually.

---

# 21. CLI Requirements

Create a clean CLI.

Recommended commands:

```bash
logbook discover
logbook scan --month YYYY-MM
logbook timeline --month YYYY-MM
logbook prepare --month YYYY-MM
logbook render --month YYYY-MM
logbook compile --month YYYY-MM
logbook finalize --month YYYY-MM
```

Meaning:

```text
prepare
    discover
    scan
    timeline

finalize
    validate
    render
    compile
    report
```

AI synthesis stays between `prepare` and `finalize`.

---

# 22. Application Service Boundary

Keep core logic independent from CLI.

Functions should resemble:

```python
discover_repositories(root)

collect_git_evidence(root, month, authors)

build_month_timeline(month, evidence, schedule)

validate_logbook(logbook, timeline)

render_latex(month, logbook)

compile_latex(month)
```

This is important because these functions can later be wrapped as MCP tools.

---

# 23. MCP Strategy

Do not start by building MCP.

First finish:

```text
CLI
domain logic
tests
LaTeX renderer
workflow
```

Only then add:

```text
mcp_server.py
```

Potential MCP tools:

```text
discover_repositories
collect_month
get_timeline
validate_logbook
render_logbook
compile_logbook
```

MCP is only transport.

The business logic must remain reusable outside MCP.

---

# 24. Agent Workflow

Create:

```text
workflows/generate-monthly-logbook.md
```

Required behavior:

## Start

If month is not known, ask exactly one useful question:

```text
Logbook bulan dan tahun berapa yang ingin dibuat?
Contoh: September 2026.
```

Convert the answer to:

```text
YYYY-MM
```

Do not ask for project root if it already exists in configuration.

## Prepare

Run deterministic evidence collection.

Expected:

```text
discover
scan
timeline
```

## Draft

Read `timeline.json`.

Generate structured daily entries.

Write:

```text
logbook.draft.json
```

## Validate

Verify:

```text
all dates exist
all repository names exist
all evidence refs exist
direct activities have evidence
manual activities have notes
unsupported claims are rejected
```

## Monthly edit

Improve only valid entries.

Write:

```text
logbook.final.json
```

## Finalize

Run:

```text
validate
render
compile
report
```

Do not claim success if LaTeX compilation fails.

---

# 25. Error Handling

Use clear machine-readable errors.

Examples:

```json
{
  "error": "GIT_NOT_FOUND"
}
```

```json
{
  "error": "PROJECT_ROOT_NOT_FOUND"
}
```

```json
{
  "error": "NO_REPOSITORIES_FOUND"
}
```

If repositories exist but no matching commits exist:

```json
{
  "status": "NO_GIT_ACTIVITY"
}
```

This is not necessarily an application failure.

Manual notes may still exist.

---

# 26. Security Rules

Git collection is read-only.

Allowed:

```text
git rev-parse
git log
git show
git diff-tree
git config --get
```

Never run destructive or mutating Git operations without explicit user instruction.

Do not run:

```text
git reset
git clean
git checkout
git rebase
git commit
git push
```

The logbook tool must never modify internship project repositories.

Allowed writes should remain inside the logbook project:

```text
generated/
dist/
```

---

# 27. Testing Requirements

Create tests before considering each subsystem complete.

Unit tests:

```text
month parser
repo discovery
ignore logic
Git log parser
author matching
timezone conversion
timeline generation
LaTeX escaping
renderer
```

Integration test:

```text
fixture repo A
fixture repo B
    ↓
scan month
    ↓
timeline
    ↓
mock AI output
    ↓
validate
    ↓
render
    ↓
compile
```

Use fixture repositories with known authors and dates.

---

# 28. Implementation Order

Use this order unless the existing codebase strongly justifies another order:

```text
1. inspect existing LaTeX project
2. inspect user-provided git_trace folder
3. document architecture mapping
4. refactor LaTeX into static template + generated data
5. implement configuration
6. implement repository discovery
7. implement monthly Git scanner
8. implement author matching
9. implement timeline builder
10. add manual evidence
11. add schemas and validation
12. add AI prompts
13. add draft generation workflow
14. add monthly editor
15. add renderer
16. add compiler
17. add generation report
18. add tests
19. add workflow command
20. optionally add MCP wrapper
```

---

# 29. Work Style

When modifying the project:

```text
inspect first
make small changes
preserve working behavior
test after each subsystem
avoid unnecessary rewrites
prefer deterministic code over prompt logic
```

Do not introduce a framework solely because it is popular.

Do not increase complexity without a concrete requirement.

---

# 30. Definition of Done

The project is ready when this flow works:

```text
fresh agent session
    ↓
run monthly workflow
    ↓
agent asks target month
    ↓
student answers month
    ↓
configured project root is scanned automatically
    ↓
multiple Git repositories are discovered
    ↓
correct student commits are collected
    ↓
activities are generated from evidence
    ↓
unsupported dates are clearly flagged
    ↓
LaTeX is rendered deterministically
    ↓
PDF compiles successfully
```

Final output should include:

```text
target month
repository count
relevant commit count
direct evidence days
manual days
inferred days
needs-review days
PDF output path
```

---

# 31. Non-Goals for Initial Version

Do not prioritize:

```text
GUI
web application
GitHub API
GitLab API
automatic cloud sync
automatic signatures
multi-university support
complex semantic code analysis
automatic timesheet inference
full MCP architecture
```

These can be added after the local monthly workflow is stable.

---

# 32. Final Engineering Principle

When choosing between prompt logic and deterministic implementation:

```text
If a task can be solved reliably with code,
solve it with code.

Use AI only where interpretation or language understanding is genuinely useful.
```

The final system should be easy to understand by humans and agents, easy to test, and safe to run against real internship repositories.
