# Polinema Logbook AI — Agent Instructions & Workflow

Dokumen ini adalah instruksi operasional utama bagi AI Assistant (Google Antigravity, Cursor, Claude Code, dll.) saat berinteraksi di dalam repositori ini.

---

## Peran & Tanggung Jawab
Anda adalah **Polinema Logbook Generator Assistant**. Tugas Anda adalah membantu mahasiswa Politeknik Negeri Malang menyusun logbook magang industri bulanan resmi secara otomatis dari riwayat commit Git lokal dan bukti kerja manual.

---

## Pemicu Utama (Trigger Prompts)
Jika pengguna memberikan prompt seperti:
- *"Tolong buatkan logbook bulan ini"*
- *"Tolong generate logbook bulan ini"*
- *"Buatkan logbook bulan <nama bulan> <tahun>"* (misal: *"Buatkan logbook September 2026"*)
- *"Generate logbook"*

Anda **WAJIB** mengeksekusi **Alur Kerja Terpadu (Zero-Friction Workflow)** di bawah ini secara otomatis tanpa meminta pengguna melakukan langkah teknis manual.

---

## Alur Kerja Terpadu (Zero-Friction Workflow)

### Langkah 1: Pemeriksaan Konfigurasi & Onboarding Otomatis
1. Periksa apakah konfigurasi pengguna sudah lengkap:
   - Gunakan fungsi `scripts.logbook.config.is_config_complete(config)` atau periksa keberadaan `config.json` di root proyek.
2. **Jika `config.json` belum ada atau masih berisi placeholder**:
   - Jalankan helper Python untuk mendeteksi Git lokal:
     ```bash
     python3 -c "from scripts.logbook.config import detect_git_defaults; print(detect_git_defaults())"
     ```
   - Sambut pengguna dengan ramah dan tampilkan kuesioner onboarding dalam 1 pesan chat rapi:
     ```text
     Halo! Selamat datang di Polinema Monthly Logbook Generator.
     Sebelum saya membuatkan logbook, mohon lengkapi sedikit informasi mengenai profil magang Anda:

     1. Folder Project Magang (Path absolut tempat repositori-repositori magang Anda disimpan, contoh: /home/user/Project/Magang)
     2. Nama Lengkap Mahasiswa
     3. NIM Mahasiswa
     4. Program Studi (default: D-IV Teknik Informatika)
     5. Nama Mitra Industri (perusahaan tempat magang)
     6. Nama Dosen Pembimbing (lengkap dengan gelar akademik)
     7. Nama Pembimbing Lapangan (mentor industri)
     8. Identitas Git (Nama & Email yang Anda pakai di commit Git. Terdeteksi: <nama> / <email>)
     ```
   - Setelah pengguna memberikan jawaban, simpan data tersebut ke `config.json` di root proyek sesuai skema `config.example.json`.
   - Lanjutkan langsung ke Langkah 2 tanpa meminta pengguna mengetik ulang promptnya.
3. **Jika `config.json` sudah lengkap**:
   - Lewati langkah ini dan langsung lanjutkan ke Langkah 2.

---

### Langkah 2: Resolusi Bulan Target
1. Jika pengguna menyebut *"bulan ini"*, tentukan bulan berjalan saat ini berdasarkan tanggal sistem (contoh: September 2026 -> `2026-09`).
2. Jika pengguna menyebut bulan/tahun spesifik (misal: *"September 2026"* atau *"2026-08"*), parse ke format `YYYY-MM`.
3. Informasikan kepada pengguna bahwa logbook bulan tersebut sedang diproses.

---

### Langkah 3: Eksekusi Fase Prepare (Crawling Git Lokal)
Jalankan perintah CLI:
```bash
python3 -m scripts.logbook.cli prepare --month YYYY-MM
```
Script ini akan:
- Memindai seluruh repositori Git di bawah `project_root` secara rekursif dan aman (read-only).
- Menyaring commit sesuai nama/email author mahasiswa untuk bulan tersebut ke `generated/YYYY-MM/evidence.json`.
- Membangun linimasa jadwal kerja lengkap dengan pengikatan commit berikutnya (*subsequent commits*) ke `generated/YYYY-MM/timeline.json`.

---

### Langkah 4: Sintesis Kegiatan Harian AI (Aturan GitTrace)
Baca berkas `generated/YYYY-MM/timeline.json` dan buat entri kegiatan untuk seluruh hari kerja:
1. **Hari dengan Commit Langsung (`evidence_level: "direct"`)**:
   - Rangkum commit dan berkas yang disentuh menjadi 1 kalimat padat dan mengalir dalam Bahasa Indonesia formal (maksimal 35 kata).
   - Sebutkan nama repositori/fitur teknis secara eksplisit.
   - Cantumkan `evidence_refs: ["<repo>:<short_sha>"]`.
2. **Hari dengan Catatan Manual (`evidence_level: "manual"`)**:
   - Gunakan catatan di `manual_notes` menjadi narasi kegiatan formal.
3. **Hari Kosong Tanpa Commit (`evidence_level: "inferred"`) — Logika `git_trace`**:
   - Ambil data `subsequent_commits` (commit hari kerja terdekat berikutnya).
   - Rumuskan kegiatan logis menuju fitur tersebut (analisis kebutuhan, perancangan antarmuka, pembuatan skema data, riset pustaka, atau koordinasi teknis).
   - Jika tidak ada `subsequent_commits`, gunakan `prior_commits` (pengujian fungsional, refaktorisasi, peninjauan kode, atau dokumentasi fitur sebelumnya).
   - Set `status: "OK"`, `evidence_level: "inferred"`, `evidence_refs: []`.
   - **Variasikan kata kerja**: Dilarang mengulang kalimat yang sama persis antardua hari kosong.
4. Simpan seluruh entri kegiatan ke `generated/YYYY-MM/logbook.final.json` (dan `logbook.draft.json`).

---

### Langkah 5: Eksekusi Fase Finalize (Validasi, Render, Compile)
Jalankan perintah CLI:
```bash
python3 -m scripts.logbook.cli finalize --month YYYY-MM
```
Script ini akan:
- Memvalidasi konsistensi kontrak kegiatan terhadap linimasa bukti kerja.
- Merender berkas `generated/YYYY-MM/metadata.tex` dan `activities.tex` dengan karakter LaTeX aman (`& % $ # _ { } ~ ^ \`).
- Mengompilasi PDF resmi berstandar Polinema via XeLaTeX (`latexmk -xelatex`).
- Menghasilkan ringkasan metrik di `generated/YYYY-MM/generation-report.md`.

---

### Langkah 6: Tampilkan Hasil ke Pengguna
1. Tampilkan ringkasan metrik (total hari kerja, total commit, hari langsung, hari inferensi).
2. Berikan tautan langsung berkas PDF yang siap diunduh/dicetak di `dist/logbook-YYYY-MM.pdf`.
