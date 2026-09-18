# Workflow Agent Execution Guide

Instruksi bagi AI Agent untuk mengeksekusi pembuatan logbook bulanan mahasiswa Polinema secara end-to-end.

---

## Alur Eksekusi (12 Langkah)

1. **Konfirmasi Bulan Target**:
   - Tanyakan kepada pengguna: *"Logbook bulan dan tahun berapa yang ingin dibuat? (Contoh: September 2026)"*.
   - Ubah jawaban ke format `YYYY-MM`.
   - JANGAN menanyakan project root atau data mahasiswa jika sudah ada di file konfigurasi.

2. **Eksekusi Fase Prepare**:
   - Jalankan perintah CLI:
     ```bash
     python3 -m scripts.logbook.cli prepare --month YYYY-MM
     ```
   - Verifikasi file `generated/YYYY-MM/evidence.json` dan `timeline.json` berhasil dibuat.

3. **Analisis Timeline**:
   - Baca file `generated/YYYY-MM/timeline.json`.
   - Periksa hari dengan bukti kerja (`direct`, `manual`) dan hari kosong (`none`).

4. **Sintesis Entri Harian (Drafting)**:
   - Untuk setiap hari kerja:
     - Jika ada commit: Rangkum pesan commit dan file yang disentuh menjadi 1 kalimat formal (lihat `prompts/daily-activity.md`). Cantumkan `evidence_refs`.
     - Jika ada catatan manual: Rangkum catatan manual menjadi narasi kegiatan formal.
     - Jika tidak ada bukti kerja: Buat entri dengan status `NEEDS_REVIEW`, `activity: null`.
   - Simpan hasil sintesis ke `generated/YYYY-MM/logbook.draft.json`.

5. **Penyelarasan Bahasa (Monthly Editing)**:
   - Terapkan panduan `prompts/monthly-editor.md`.
   - Haluskan gaya bahasa antarkalimat dan variasikan kata kerja pembuka.
   - Simpan hasil akhir ke `generated/YYYY-MM/logbook.final.json`.

6. **Eksekusi Fase Finalize**:
   - Jalankan perintah CLI:
     ```bash
     python3 -m scripts.logbook.cli finalize --month YYYY-MM
     ```
   - CLI akan memvalidasi skema JSON, merender template LaTeX, mengompilasi PDF via `latexmk`, dan membuat file `generation-report.md`.

7. **Pelaporan Hasil ke Pengguna**:
   - Tampilkan ringkasan metrik dari `generation-report.md`.
   - Berikan tautan berkas PDF yang dihasilkan di `dist/logbook-YYYY-MM.pdf`.
