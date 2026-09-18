# Workflow Agent Execution Guide

Panduan bagi AI Agent saat pengguna meminta pembuatan logbook bulanan (misal: *"Tolong buatkan logbook bulan ini"* atau *"Tolong generate logbook September 2026"*).

---

## Alur Kerja Terpadu (Zero-Friction Workflow)

### Langkah 1: Pemeriksaan Konfigurasi & Onboarding Otomatis
1. Periksa apakah konfigurasi pengguna sudah lengkap menggunakan `scripts.logbook.config`:
   - Cek keberadaan `config.json`.
   - Jalankan fungsi `is_config_complete(config)`.
2. **Jika konfigurasi belum ada atau masih berisi placeholder**:
   - Deteksi konfigurasi Git lokal pengguna dengan menjalankan helper `detect_git_defaults()` (mengambil `user.name` dan `user.email`).
   - Berikan sambutan ramah dan minta data yang diperlukan dalam 1 format formulir kuesioner rapi di chat:
     ```text
     Halo! Sebelum membuat logbook, saya perlu sedikit informasi mengenai profil magang Anda:
     1. Folder Project Magang (path absolut tempat repositori magang Anda berada)
     2. Nama Lengkap Mahasiswa
     3. NIM Mahasiswa
     4. Program Studi (default: D-IV Teknik Informatika)
     5. Nama Mitra Industri (perusahaan tempat magang)
     6. Nama Dosen Pembimbing (lengkap dengan gelar)
     7. Nama Pembimbing Lapangan / Mentor Industri
     8. Identitas Git Anda (Nama & Email yang Anda pakai di commit Git)
     ```
   - Setelah pengguna menjawab, simpan data tersebut secara permanen ke `config.json` menggunakan fungsi `save_app_config(...)`.
   - Lanjutkan langsung ke Langkah 2 tanpa meminta pengguna mengulangi prompt.
3. **Jika konfigurasi sudah lengkap**:
   - Langsung lanjutkan ke Langkah 2 tanpa bertanya ulang data profil.

---

### Langkah 2: Penentuan Bulan Target
1. Jika pengguna mengatakan *"bulan ini"* atau *"logbook bulan ini"*:
   - Tentukan bulan berjalan berdasarkan waktu sistem saat ini (misal: `2026-09`).
2. Jika pengguna menyebutkan bulan tertentu (misal: *"September 2026"* atau *"bulan Agustus"*):
   - Parse bulan tersebut ke dalam format `YYYY-MM`.
3. Informasikan kepada pengguna bulan yang sedang diproses secara ringkas.

---

### Langkah 3: Eksekusi Fase Prepare (Crawling Git Lokal)
Jalankan perintah CLI:
```bash
python3 -m scripts.logbook.cli prepare --month YYYY-MM
```
Sistem akan:
- Memindai seluruh repositori Git di dalam `project_root` (mengabaikan folder build/vendor).
- Mengumpulkan commit milik pengguna pada bulan tersebut ke `generated/YYYY-MM/evidence.json`.
- Menyusun linimasa seluruh hari kerja ke `generated/YYYY-MM/timeline.json` lengkap dengan konteks commit terdekat berikutnya (*subsequent commits*).

---

### Langkah 4: Sintesis Kegiatan Harian (AI Infilling ala `git_trace`)
1. Baca berkas `generated/YYYY-MM/timeline.json`.
2. Untuk setiap hari kerja:
   - **Hari dengan Commit (`direct`)**: Buat ringkasan 1 kalimat formal mengalir yang mencantumkan nama repositori dan fungsi teknis yang dikerjakan. Cantumkan `evidence_refs`.
   - **Hari dengan Catatan Manual (`manual`)**: Gunakan isi `manual_notes` menjadi narasi kegiatan resmi.
   - **Hari Kosong / Tanpa Commit (`inferred`)**:
     - Ambil data `subsequent_commits` (commit hari kerja terdekat berikutnya).
     - Buat deskripsi persiapan/riset/perancangan/koordinasi yang relevan menuju fitur tersebut.
     - Jika tidak ada `subsequent_commits`, gunakan `prior_commits` (pengujian/dokumentasi fitur sebelumnya).
     - Set `evidence_level: "inferred"`, `status: "OK"`.
     - Variasikan pilihan kata agar tidak ada 2 hari kosong berurutan dengan kalimat identik.
3. Simpan seluruh entri kegiatan ke `generated/YYYY-MM/logbook.final.json` (dan `logbook.draft.json`).

---

### Langkah 5: Eksekusi Fase Finalize (Validasi, Render, Compile)
Jalankan perintah CLI:
```bash
python3 -m scripts.logbook.cli finalize --month YYYY-MM
```
Sistem akan:
- Memvalidasi integritas data dan kepatuhan skema.
- Merender `generated/YYYY-MM/metadata.tex` dan `activities.tex`.
- Menyinkronkan berkas ke `generated/current/`.
- Mengompilasi PDF resmi berstandar Polinema melalui XeLaTeX.
- Menghasilkan laporan ringkasan di `generated/YYYY-MM/generation-report.md`.

---

### Langkah 6: Tampilkan Hasil ke Pengguna
1. Tampilkan ringkasan metrik pembuatan logbook (total hari kerja, total commit, hari direct, hari inferensi).
2. Berikan tautan berkas PDF yang siap diunduh/dicetak di `dist/logbook-YYYY-MM.pdf`.
