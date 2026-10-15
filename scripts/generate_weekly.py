"""Script to generate all 15 weekly logbooks into dist/final/."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from scripts.logbook.config import load_app_config, load_absences_config, get_absences_map_by_date
from scripts.logbook.renderer import render_latex_files
from scripts.logbook.schemas import ActivityStatus, DailyActivityEntry, EvidenceLevel, MonthlyLogbook


WEEK_SCHEDULE = [
    ("Juli-1", "01 Juli 2026 -- 05 Juli 2026", "2026-07-01", "2026-07-05"),
    ("Juli-2", "06 Juli 2026 -- 12 Juli 2026", "2026-07-06", "2026-07-12"),
    ("Juli-3", "13 Juli 2026 -- 19 Juli 2026", "2026-07-13", "2026-07-19"),
    ("Juli-4", "20 Juli 2026 -- 26 Juli 2026", "2026-07-20", "2026-07-26"),
    ("Juli-5", "27 Juli 2026 -- 02 Agustus 2026", "2026-07-27", "2026-08-02"),
    ("Agustus-1", "03 Agustus 2026 -- 09 Agustus 2026", "2026-08-03", "2026-08-09"),
    ("Agustus-2", "10 Agustus 2026 -- 16 Agustus 2026", "2026-08-10", "2026-08-16"),
    ("Agustus-3", "17 Agustus 2026 -- 23 Agustus 2026", "2026-08-17", "2026-08-23"),
    ("Agustus-4", "24 Agustus 2026 -- 30 Agustus 2026", "2026-08-24", "2026-08-30"),
    ("Agustus-5", "31 Agustus 2026 -- 06 September 2026", "2026-08-31", "2026-09-06"),
    ("September-1", "07 September 2026 -- 13 September 2026", "2026-09-07", "2026-09-13"),
    ("September-2", "14 September 2026 -- 20 September 2026", "2026-09-14", "2026-09-20"),
    ("September-3", "21 September 2026 -- 27 September 2026", "2026-09-21", "2026-09-27"),
    ("September-4", "28 September 2026 -- 04 Oktober 2026", "2026-09-28", "2026-10-04"),
    ("Oktober-1", "05 Oktober 2026 -- 11 Oktober 2026", "2026-10-05", "2026-10-11"),
]


# Master daily activities mapping (YYYY-MM-DD -> DailyActivityEntry kwargs)
MASTER_ENTRIES: Dict[str, dict] = {
    # Juli-1 (1-5 Juli 2026)
    "2026-07-01": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengintegrasikan API pengambilan loading plan dari shin-preparation ke shin_buzai serta menyempurnakan fitur ekspor serah terima pada modul shin_usage.",
        "repositories": ["shin-preparation", "shin_buzai", "shin_usage"],
        "evidence_refs": ["shin_buzai:a812a9c", "shin-preparation:e468b8d", "shin_usage:f8d5ffb", "shin_usage:a7ecaea"],
    },
    "2026-07-02": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan penanganan data nullable untuk tanggal aktivitas berstatus TBA pada modul ppc_activity_control di sistem shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": ["shin-ac:02ce57b"],
    },
    "2026-07-03": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Melakukan pengujian validasi input tanggal implementasi dan analisis kebutuhan pembatasan format angka desimal pada modul ppc_activity_control di aplikasi shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": [],
    },

    # Juli-2 (6-12 Juli 2026)
    "2026-07-06": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Menganalisis spesifikasi kebutuhan validasi input numerik dan format pembatasan desimal pada modul ppc_activity_control di aplikasi shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": [],
    },
    "2026-07-07": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan batas maksimal angka desimal pada kolom input kapasitas modul ppc_activity_control di sistem shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": ["shin-ac:10b7c58"],
    },
    "2026-07-08": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Menambahkan filter waktu serah terima serta mengoptimalkan indeks basis data untuk mempercepat proses impor pada aplikasi shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": ["shin_usage:ad9ad9e", "shin_usage:481d5f4"],
    },
    "2026-07-09": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Merancang skema format ekspor berkas loading plan dan menguji konsistensi parameter filter waktu serah terima data.",
        "repositories": ["shin_buzai", "shin_usage"],
        "evidence_refs": [],
    },
    "2026-07-10": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan fitur ekspor berkas pada modul loading plan shin_buzai serta memperbaiki filter tanggal dan waktu di shin_usage.",
        "repositories": ["shin_buzai", "shin_usage"],
        "evidence_refs": ["shin_buzai:ec81266", "shin_usage:e63b9aa"],
    },

    # Juli-3 (13-19 Juli 2026)
    "2026-07-13": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Mempersiapkan inisialisasi struktur modul shin-cap dan merancang standarisasi tata letak laporan ekspor Excel pada shin_usage.",
        "repositories": ["shin-cap", "shin_usage"],
        "evidence_refs": [],
    },
    "2026-07-14": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Menginisialisasi proyek modul shin-cap, mengonfigurasi rute URL dan hak akses tamu, serta merapikan styling ekspor Excel di shin_usage.",
        "repositories": ["shin-cap", "shin_usage"],
        "evidence_refs": ["shin-cap:c4accc7", "shin-cap:fb9471e", "shin_usage:de003d4"],
    },
    "2026-07-15": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengonfigurasi pengaturan keamanan cookie, encoding URL spasi, dan refaktorisasi pengontrol otorisasi peran pada modul shin-cap.",
        "repositories": ["shin-cap"],
        "evidence_refs": ["shin-cap:b715edf", "shin-cap:cf50864"],
    },
    "2026-07-16": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengembangkan komponen SearchableSelect dan mengimplementasikan operasi CRUD untuk manajemen data PIC pada modul shin-cap.",
        "repositories": ["shin-cap"],
        "evidence_refs": ["shin-cap:6358eb7"],
    },
    "2026-07-17": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengoptimalkan pipeline impor berkas MPL menggunakan Celery chords dan menyempurnakan filter status approval pada sistem shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": ["shin_usage:051db78", "shin_usage:0a52c1f", "shin_usage:500d769"],
    },

    # Juli-4 (20-26 Juli 2026)
    "2026-07-20": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Menambahkan status pembatalan aktivitas pada shin-ac serta mengimplementasikan modul pengalamatan rak stok pada shin_buzai.",
        "repositories": ["shin-ac", "shin_buzai"],
        "evidence_refs": ["shin-ac:7c3de69", "shin_buzai:df8d5e4"],
    },
    "2026-07-21": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan modul master data car maker, project, dan phase beserta integrasi API dan komponen antarmuka pada shin_buzai.",
        "repositories": ["shin_buzai"],
        "evidence_refs": ["shin_buzai:f122773"],
    },
    "2026-07-22": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengintegrasikan data Ethernet assembly ke loading plan serta menambahkan kalkulasi total kuantitas pada pembuatan dokumen DPS di shin_buzai.",
        "repositories": ["shin_buzai"],
        "evidence_refs": ["shin_buzai:6661c6c", "shin_buzai:66981d5", "shin_buzai:54af9a2", "shin_buzai:e745da4"],
    },
    "2026-07-23": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.ABSENT,
        "activity": "Izin: Mengikuti Lomba di Solo",
        "check_in": "Izin",
        "check_out": "Izin",
        "repositories": [],
        "evidence_refs": [],
    },
    "2026-07-24": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.ABSENT,
        "activity": "Izin: Mengikuti Lomba di Solo",
        "check_in": "Izin",
        "check_out": "Izin",
        "repositories": [],
        "evidence_refs": [],
    },

    # Juli-5 (27 Juli - 2 Agustus 2026)
    "2026-07-27": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Menyesuaikan logika ekspor rencana perakitan (assembly plan) berdasarkan nomor perakitan pada modul shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": ["shin_usage:5c1dca2"],
    },
    "2026-07-28": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan ekspor asinkron dengan Celery, mekanisme session heartbeat pada shin-ac, dan kontrol versi situs pada shin-cap.",
        "repositories": ["shin_usage", "shin-ac", "shin-cap"],
        "evidence_refs": ["shin_usage:0205084", "shin-ac:f6a41fb", "shin-cap:20802a8"],
    },
    "2026-07-29": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengoptimalkan pemrosesan data frame perakitan komponen dan memperbarui penanganan event modal berbasis Vanilla JS pada shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": ["shin_usage:c99f905"],
    },
    "2026-07-30": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Merestrukturisasi model otorisasi AirFreight dan menambahkan status aktif PIC pada tabel data antarmuka modul shin-cap.",
        "repositories": ["shin-cap"],
        "evidence_refs": ["shin-cap:7b915e6", "shin-cap:34f6be2"],
    },
    "2026-07-31": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan fitur lampiran berkas pertemuan secara aman dan memperbarui dependensi pustaka Select2 lokal pada modul shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": ["shin-ac:5593fce", "shin-ac:75afc7c", "shin-ac:005692c", "shin-ac:4c8e9d2"],
    },

    # September-4 (28 Sep - 4 Okt 2026) special days
    "2026-09-28": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.ABSENT,
        "activity": "Sakit",
        "check_in": "Sakit",
        "check_out": "Sakit",
        "repositories": [],
        "evidence_refs": [],
    },
    "2026-10-01": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Mempersiapkan dependensi Celery queue dan skema tabel riwayat impor berkas latar belakang pada modul shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": [],
    },
    "2026-10-02": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan antrean tugas latar belakang impor berkas di shin_usage serta filter part dan multi-line pada shin_buzai.",
        "repositories": ["shin_usage", "shin_buzai"],
        "evidence_refs": ["shin_usage:b61e0b5", "shin_buzai:86860d5"],
    },

    # Oktober-1 (5-11 Oktober 2026)
    "2026-10-05": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Memperbaiki penanganan task pipeline yang tertunda (stale) dan meningkatkan notifikasi event Celery pada modul shin_usage.",
        "repositories": ["shin_usage"],
        "evidence_refs": ["shin_usage:4d7ba9b"],
    },
    "2026-10-06": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Menganalisis logika filter multi-carline dan merancang validasi status proyek perakitan pada modul shin_buzai.",
        "repositories": ["shin_buzai"],
        "evidence_refs": [],
    },
    "2026-10-07": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Menambahkan filter multi-carline untuk seluruh proyek perakitan dan menyesuaikan kriteria seleksi data pada modul shin_buzai.",
        "repositories": ["shin_buzai"],
        "evidence_refs": ["shin_buzai:8d30e3d"],
    },
    "2026-10-08": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.INFERRED,
        "activity": "Mengevaluasi performa pengiriman form laporan dan merancang fitur debounce untuk mencegah duplikasi simpan data pada shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": [],
    },
    "2026-10-09": {
        "status": ActivityStatus.OK,
        "evidence_level": EvidenceLevel.DIRECT,
        "activity": "Mengimplementasikan fungsi debounce pada penyimpanan laporan dan menambahkan fitur pencarian marusoku pada modul shin-ac.",
        "repositories": ["shin-ac"],
        "evidence_refs": ["shin-ac:1a660d5", "shin-ac:a61d152"],
    },
}


def load_existing_month_entries(project_dir: Path, month_key: str) -> Dict[str, dict]:
    p = project_dir / "generated" / month_key / "logbook.final.json"
    if not p.is_file():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {e["date"]: e for e in data.get("entries", [])}


def get_entry_for_date(date_str: str, existing_aug: dict, existing_sep: dict, absences_map: dict) -> DailyActivityEntry:
    # 1. First priority: Check absence records
    if date_str in absences_map:
        item = absences_map[date_str]
        cat = getattr(item, "category", "Izin")
        reason = getattr(item, "reason", cat)
        short_label = "Sakit" if cat.lower() == "sakit" else "Izin"
        full_activity = "Sakit" if cat.lower() == "sakit" else (reason if reason.startswith("Izin") else f"Izin: {reason}")
        return DailyActivityEntry(
            date=date_str,
            status=ActivityStatus.OK,
            evidence_level=EvidenceLevel.ABSENT,
            confidence=1.0,
            activity=full_activity,
            check_in=short_label,
            check_out=short_label,
            repositories=[],
            evidence_refs=[],
        )

    # 2. Check master curated entries
    if date_str in MASTER_ENTRIES:
        d = MASTER_ENTRIES[date_str]
        return DailyActivityEntry(
            date=date_str,
            status=d.get("status", ActivityStatus.OK),
            evidence_level=d.get("evidence_level", EvidenceLevel.DIRECT),
            confidence=d.get("confidence", 0.95),
            activity=d.get("activity"),
            check_in=d.get("check_in", "07:00"),
            check_out=d.get("check_out", "16:20"),
            repositories=d.get("repositories", []),
            evidence_refs=d.get("evidence_refs", []),
        )

    # 3. Check existing August entries
    if date_str in existing_aug:
        e = existing_aug[date_str]
        return DailyActivityEntry(**e)

    # 4. Check existing September entries
    if date_str in existing_sep:
        e = existing_sep[date_str]
        return DailyActivityEntry(**e)

    raise ValueError(f"No entry found for date: {date_str}")


def compile_week_pdf(project_dir: Path, week_name: str, period_label: str, entries: List[DailyActivityEntry], config) -> Path:
    week_dir = project_dir / "generated" / "weeks" / week_name
    week_dir.mkdir(parents=True, exist_ok=True)

    month_key = entries[0].date[:7]
    logbook = MonthlyLogbook(
        month=month_key,
        student_name=config.student.name,
        nim=config.student.nim,
        company=config.internship.company,
        entries=entries,
    )

    with open(week_dir / "logbook.json", "w", encoding="utf-8") as f:
        json.dump(logbook.model_dump(), f, indent=2, ensure_ascii=False)

    current_dir = project_dir / "generated" / "current"
    render_latex_files(
        output_dir=week_dir,
        config=config,
        logbook=logbook,
        current_dir=current_dir,
        period_label=period_label,
    )

    # Compile with latexmk
    cmd = [
        "latexmk",
        "-xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-outdir=dist",
        "main.tex",
    ]
    res = subprocess.run(cmd, cwd=str(project_dir), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Compilation failed for {week_name}:", file=sys.stderr)
        print(res.stderr or res.stdout, file=sys.stderr)
        raise RuntimeError(f"LaTeX compilation failed for {week_name}")

    final_dir = project_dir / "dist" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    target_pdf = final_dir / f"logbook-{week_name}.pdf"
    shutil.copyfile(project_dir / "dist" / "main.pdf", target_pdf)
    return target_pdf


def main():
    config = load_app_config()
    absences = get_absences_map_by_date(load_absences_config(config.project_dir / "config"))
    existing_aug = load_existing_month_entries(config.project_dir, "2026-08")
    existing_sep = load_existing_month_entries(config.project_dir, "2026-09")

    final_dir = config.project_dir / "dist" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    from datetime import date, timedelta
    results = []

    print(f"[*] Generating {len(WEEK_SCHEDULE)} weekly logbooks into {final_dir}...\n")

    for week_name, period_label, start_date_str, end_date_str in WEEK_SCHEDULE:
        s_dt = date.fromisoformat(start_date_str)
        e_dt = date.fromisoformat(end_date_str)
        cur = s_dt
        entries: List[DailyActivityEntry] = []
        while cur <= e_dt:
            if cur.weekday() < 5:  # Mon-Fri
                ds = cur.isoformat()
                entry = get_entry_for_date(ds, existing_aug, existing_sep, absences)
                entries.append(entry)
            cur += timedelta(days=1)

        pdf_path = compile_week_pdf(config.project_dir, week_name, period_label, entries, config)

        # Check page count with pdfinfo or pdftotext
        pdfinfo_cmd = ["pdfinfo", str(pdf_path)]
        info_res = subprocess.run(pdfinfo_cmd, capture_output=True, text=True)
        pages = 1
        for line in info_res.stdout.splitlines():
            if "Pages:" in line:
                pages = int(line.split(":")[1].strip())

        print(f"[+] {week_name:12s} | Period: {period_label:33s} | Entries: {len(entries)} | Pages: {pages} -> {pdf_path.name}")
        results.append((week_name, period_label, len(entries), pages, pdf_path))

    print(f"\n[SUCCESS] All {len(results)} weekly logbooks generated in {final_dir}!")


if __name__ == "__main__":
    main()
