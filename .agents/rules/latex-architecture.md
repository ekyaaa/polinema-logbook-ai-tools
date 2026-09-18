---
trigger: always_on
---

# Polinema Monthly Logbook Generator
## Architecture & Implementation Plan

> Tujuan: mengubah template LaTeX logbook menjadi tool bulanan berbasis Git yang dapat dijalankan AI/agent.
>
> Referensi implementasi: project lokal `git_trace` pada `~/Project/git_trace`. Untuk versi online ada di github yaitu: `https://github.com/ekyaaa/git_trace/`

---

## 1. Tujuan Sistem

Workflow utama:

```text
Run workflow
→ AI bertanya bulan logbook
→ scan folder project magang
→ temukan repository Git
→ ambil commit bulan tersebut
→ kelompokkan per tanggal
→ AI ubah evidence menjadi aktivitas
→ validasi JSON
→ render LaTeX
→ compile PDF
```

Prinsip:

```text
Git = evidence
AI = interpretation
JSON = contract
LaTeX = presentation
MCP = optional transport
```

AI tidak menangani pekerjaan deterministik yang dapat dilakukan script.

---

## 2. Arsitektur

```text
User
 ↓
AI Workflow
 ↓
CLI / Semi-MCP Tools
 ├─ discover repositories
 ├─ collect Git evidence
 ├─ build timeline
 ├─ validate
 ├─ render LaTeX
 └─ compile PDF
 ↓
Structured JSON
 ↓
LaTeX Template
 ↓
logbook-YYYY-MM.pdf
```

Versi awal menggunakan CLI lokal. Setelah stabil, fungsi yang sama dapat dibungkus menjadi MCP tools.

---

## 3. Struktur Project

```text
project/
├── main.tex
├── pyproject.toml
├── latexmkrc
├── config/
│   ├── student.yaml
│   ├── internship.yaml
│   └── logbook.yaml
├── template/
│   ├── preamble.tex
│   ├── commands.tex
│   ├── cover.tex
│   ├── identity.tex
│   └── signatures.tex
├── generated/
│   ├── current/
│   └── YYYY-MM/
│       ├── evidence.json
│       ├── timeline.json
│       ├── logbook.draft.json
│       ├── logbook.final.json
│       ├── activities.tex
│       └── generation-report.md
├── manual/
│   └── YYYY-MM.yaml
├── prompts/
│   ├── system.md
│   ├── daily-activity.md
│   ├── monthly-editor.md
│   └── workflow-agent.md
├── scripts/logbook/
│   ├── cli.py
│   ├── config.py
│   ├── discovery.py
│   ├── git_reader.py
│   ├── author.py
│   ├── timeline.py
│   ├── schemas.py
│   ├── validator.py
│   ├── renderer.py
│   ├── latex_escape.py
│   └── compiler.py
├── workflows/
│   └── generate-monthly-logbook.md
└── tests/
```

---

## 4. Konfigurasi

### `config/internship.yaml`

```yaml
company: "Nama Perusahaan"
project_root: "/home/user/Project/Internship"

git_authors:
  names:
    - "Nama Mahasiswa"
  emails:
    - "student@example.com"
```

### `config/logbook.yaml`

```yaml
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

ai:
  allow_inferred_activity: false

latex:
  engine: "xelatex"
```

Konfigurasi diisi sekali. Workflow bulanan tidak perlu menanyakan ulang data yang sudah tersedia.

---

## 5. Repository Discovery

Scanner menerima `project_root`, lalu mencari repository secara rekursif.

`.git` hanya digunakan untuk deteksi repository.

Jangan membaca manual:

```text
.git/objects
.git/index
.git/refs
.git/logs
```

Gunakan Git CLI:

```bash
git rev-parse --show-toplevel
git log
git show
git diff-tree
git config
```

Ini lebih aman untuk repository normal, worktree, submodule, dan packed refs.

Tambahkan `.logbookignore` untuk folder seperti:

```text
node_modules/
vendor/
dist/
build/
.next/
.gradle/
.dart_tool/
coverage/
backup/
```

---

## 6. Git Evidence Collector

Untuk bulan `2026-09`, gunakan:

```text
2026-09-01T00:00:00
<= commit <
2026-10-01T00:00:00
```

Data minimum per commit:

```json
{
  "sha": "abc123",
  "repository": "backend",
  "author_name": "Nama",
  "author_email": "mail@example.com",
  "authored_at": "2026-09-14T10:31:00+07:00",
  "subject": "feat: add session validation",
  "files": ["src/auth/session.py"]
}
```

Changed files:

```bash
git diff-tree --no-commit-id --name-only -r <sha>
```

Diff stat bersifat opsional dan tidak digunakan sebagai ukuran produktivitas.

---

## 7. Author Filtering

Mahasiswa dapat memiliki beberapa identitas Git.

Prioritas:

```text
email config
→ nama config
→ git config lokal
→ git config global
```

Jangan memasukkan commit contributor lain secara otomatis.

---

## 8. Timeline Bulanan

Setelah Git dikumpulkan, script membuat timeline seluruh hari kerja.

```json
{
  "date": "2026-09-14",
  "working_day": true,
  "evidence_level": "direct",
  "repositories": ["backend"],
  "commits": []
}
```

AI tidak menentukan tanggal. Tanggal berasal dari script.

---

## 9. Evidence Level

Gunakan:

```text
direct
manual
inferred
none
```

- `direct`: ada Git evidence pada tanggal tersebut.
- `manual`: aktivitas ditulis mahasiswa, misalnya meeting atau presentasi.
- `inferred`: disimpulkan dari evidence sekitar; default-nya mati.
- `none`: evidence tidak cukup.

Jika `none`:

```text
status = NEEDS_REVIEW
```

Jangan membuat aktivitas palsu untuk mengisi kalender.

---

## 10. Manual Evidence

Gunakan:

```text
manual/YYYY-MM.yaml
```

Contoh:

```yaml
2026-09-03:
  - "Diskusi requirement bersama pembimbing lapangan."
2026-09-10:
  - "Presentasi progress sprint."
```

Penting:

```text
tidak ada commit ≠ tidak ada pekerjaan
```

---

## 11. Input dan Output AI

Jangan kirim seluruh source code.

Default context:

```text
tanggal
repository
commit subject
commit body
changed filenames
manual notes
```

Diff hanya dipakai jika commit terlalu ambigu, setelah secret dan file sensitif disaring.

Output AI wajib JSON:

```json
{
  "date": "2026-09-14",
  "status": "OK",
  "evidence_level": "direct",
  "confidence": 0.94,
  "activity": "Memperbaiki mekanisme autentikasi sesi pada perangkat mobile.",
  "repositories": ["backend"],
  "evidence_refs": ["backend:abc123"]
}
```

Jika evidence tidak cukup:

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

Validasi output menggunakan schema, misalnya Pydantic.

---

## 12. Prompt Architecture

Pisahkan prompt:

```text
system.md
daily-activity.md
monthly-editor.md
workflow-agent.md
```

Peran:

```text
system
→ aturan evidence dan anti-hallucination

daily-activity
→ satu hari menjadi satu aktivitas

monthly-editor
→ rapikan bahasa tanpa mengubah fakta

workflow-agent
→ orkestrasi end-to-end
```

---

## 13. LaTeX Architecture

AI tidak menulis seluruh `.tex`.

`main.tex` hanya membaca template dan data hasil generate.

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

Generated entry:

```tex
\LogbookEntry
  {14 September 2026}
  {08:00}
  {17:00}
  {Memperbaiki mekanisme autentikasi sesi.}
```

Python melakukan escaping karakter LaTeX seperti:

```text
& % $ # _ { } ~ ^ \
```

---

## 14. CLI

Command utama:

```bash
logbook discover
logbook scan --month YYYY-MM
logbook timeline --month YYYY-MM
logbook prepare --month YYYY-MM
logbook render --month YYYY-MM
logbook compile --month YYYY-MM
logbook finalize --month YYYY-MM
```

`prepare`:

```text
discover
→ scan
→ timeline
```

`finalize`:

```text
validate
→ render
→ compile
→ report
```

AI synthesis dilakukan di antara `prepare` dan `finalize`.

---

## 15. Semi-MCP Boundary

Core logic tidak boleh bergantung pada CLI.

Gunakan fungsi reusable:

```python
discover_repositories(root)
collect_git_evidence(root, month, authors)
build_month_timeline(month, evidence, schedule)
validate_logbook(logbook, timeline)
render_latex(month, logbook)
compile_latex(month)
```

Fungsi ini nantinya dapat dibungkus menjadi MCP tools tanpa mengubah business logic.

---

## 16. Workflow Agent

Urutan workflow:

```text
1. cek bulan
2. jika belum ada, tanya bulan dan tahun
3. ubah ke YYYY-MM
4. baca project_root dari config
5. run logbook prepare
6. baca timeline.json
7. generate daily activity JSON
8. validasi evidence
9. monthly editing
10. simpan logbook.final.json
11. run logbook finalize
12. tampilkan hasil
```

Pertanyaan awal:

```text
Logbook bulan dan tahun berapa yang ingin dibuat?
Contoh: September 2026.
```

Jangan bertanya `project_root` jika sudah ada di config.

---

## 17. Security

Git collector harus read-only.

Boleh:

```text
git rev-parse
git log
git show
git diff-tree
git config --get
```

Jangan jalankan otomatis:

```text
git checkout
git reset
git clean
git commit
git push
git rebase
```

Tool tidak boleh mengubah repository magang.

Write hanya ke:

```text
generated/
dist/
```

Jangan kirim ke AI:

```text
.env
*.pem
*.key
credentials
tokens
passwords
service accounts
```

---

## 18. Reference `git_trace`

Folder lokal `git_trace` yang diberikan user harus dipelajari sebelum implementasi Git scanner.

Cari:

```text
repository discovery
commit reader
month filtering
author filtering
daily aggregation
AI prompt
empty-day handling
error handling
```

Buat mapping:

```text
git_trace behavior
→ reusable concept
→ implementation baru
```

Jangan copy-paste seluruh arsitektur. Ambil pola yang relevan dan sesuaikan dengan project LaTeX.

---

## 19. Implementation Plan

### Phase 1 — Analyze LaTeX
Identifikasi main document, table logbook, metadata, signature, dan date format. Refactor agar aktivitas berasal dari `generated/current/activities.tex`.

### Phase 2 — Analyze `git_trace`
Pelajari logic Git dan AI yang relevan. Buat mapping ke project baru.

### Phase 3 — Repository Discovery
Implement `discovery.py` untuk recursive scanning, ignore rules, `.git` directory/file, dan deduplication.

### Phase 4 — Monthly Git Reader
Implement `git_reader.py`, `author.py`, dan `schemas.py`. Output: `evidence.json`.

### Phase 5 — Timeline
Implement `timeline.py` untuk menggabungkan Git evidence, manual notes, dan working days. Output: `timeline.json`.

### Phase 6 — AI Synthesis
Generate `logbook.draft.json` dengan evidence refs dan `NEEDS_REVIEW`.

### Phase 7 — Monthly Editor
Rapikan gaya bahasa tanpa mengubah fakta. Output: `logbook.final.json`.

### Phase 8 — Renderer
Implement `latex_escape.py` dan `renderer.py`. Generate `metadata.tex` dan `activities.tex`.

### Phase 9 — Compiler
Gunakan:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Output:

```text
dist/logbook-YYYY-MM.pdf
```

### Phase 10 — Workflow
Buat `workflows/generate-monthly-logbook.md`.

### Phase 11 — Testing
Test discovery, author matching, month filtering, timeline, escaping, renderer, dan compile menggunakan fixture Git repository.

### Phase 12 — MCP
Setelah CLI stabil, tambahkan MCP wrapper. Jangan rewrite core logic.

---

## 20. MVP Scope

Versi pertama cukup memiliki:

```text
config YAML
repository discovery
monthly Git scanner
author matching
changed filenames
timeline JSON
manual evidence
AI structured output
validator
LaTeX renderer
PDF compiler
monthly workflow
```

Belum perlu:

```text
GUI
GitHub/GitLab API
holiday API
automatic signatures
complex code analysis
full MCP server
```

---

## 21. Definition of Done

Project siap jika mahasiswa dapat:

```text
clone project
→ isi config sekali
→ run workflow
→ pilih bulan
→ Git project otomatis discan
→ aktivitas dibuat dari evidence
→ hari tanpa evidence ditandai
→ LaTeX dirender
→ PDF dihasilkan
```

Target:

```text
mahasiswa tidak perlu menyalin commit satu per satu ke logbook.
```

---

## 22. Engineering Rule

```text
Jika pekerjaan dapat diselesaikan secara deterministik dengan code,
gunakan code.

Gunakan AI hanya untuk memahami konteks dan menghasilkan bahasa manusia.
```
