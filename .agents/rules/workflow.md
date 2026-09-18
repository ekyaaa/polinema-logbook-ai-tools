# Polinema Logbook AI Workflow Rule

When the user asks to generate or create a logbook (e.g. *"Tolong buatkan logbook bulan ini"* or *"Generate logbook YYYY-MM"*), the AI assistant must automatically execute the following end-to-end pipeline:

1. **Config Onboarding Check**:
   - Check if `config.json` exists and is complete using `scripts.logbook.config.is_config_complete`.
   - If not complete, greet the user, run `detect_git_defaults()` to auto-detect local Git name/email, present the friendly onboarding questionnaire in chat, and save answers to `config.json`.
   - If already complete, proceed directly.

2. **Target Month Resolution**:
   - If user says *"bulan ini"*, automatically use the current system calendar month (e.g. `2026-09`).
   - If an explicit month/year is stated, parse it to `YYYY-MM`.

3. **Crawl & Prepare**:
   - Run: `python3 -m scripts.logbook.cli prepare --month YYYY-MM`
   - This scans repositories under `project_root` and produces `generated/YYYY-MM/timeline.json` with commit and subsequent commit context.

4. **Synthesize Activities (git_trace logic)**:
   - Read `generated/YYYY-MM/timeline.json`.
   - For days with commits: summarize into 1 formal Indonesian sentence with `evidence_refs` and `evidence_level: "direct"`.
   - For empty days without commits: apply the `git_trace` inference logic using `subsequent_commits` (or `prior_commits`) to deduce realistic preparation, technical research, architecture planning, testing, or coordination activities. Set `evidence_level: "inferred"` and status `"OK"`.
   - Write synthesized activities to `generated/YYYY-MM/logbook.final.json`.

5. **Finalize & Compile PDF**:
   - Run: `python3 -m scripts.logbook.cli finalize --month YYYY-MM`
   - Validates entries, renders LaTeX files, and compiles `dist/logbook-YYYY-MM.pdf` via XeLaTeX.

6. **Present Results**:
   - Show summary metrics from `generation-report.md` and provide a clickable file link to `dist/logbook-YYYY-MM.pdf`.
