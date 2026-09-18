# Workflow: Generate Monthly Logbook

Workflow untuk menghasilkan dokumen logbook bulanan magang Polinema secara otomatis berbasis bukti kerja Git.

---

## Prasyarat
- Konfigurasi profil magang sudah tersedia di `config.json` (atau otomatis dipandu kuesioner AI saat pertama kali dijalankan).
- Perangkat lokal memiliki `git`, `python3`, dan `latexmk` (dengan engine `xelatex`).

---

## Langkah-langkah

### 1. Deteksi Profil & Bulan Target
- Periksa kelengkapan konfigurasi `config.json`. Jika belum ada, pandu pengisian data secara interaktif.
- Tentukan bulan target: otomatis gunakan bulan berjalan (misal: `2026-09`) jika user meminta *"bulan ini"*, atau parse bulan yang disebutkan.

### 2. Jalankan Prepare (Crawling Git)
```bash
python3 -m scripts.logbook.cli prepare --month <YYYY-MM>
```
Perintah ini akan:
1. Menemukan semua repositori Git di bawah `project_root` secara rekursif.
2. Mengumpulkan commit sesuai identitas mahasiswa untuk bulan tersebut (`evidence.json`).
3. Membangun kalender jadwal kerja dan mengikat bukti kerja serta konteks commit hari berikutnya (`timeline.json`).

### 3. Sintesis Kegiatan Harian (AI Infilling ala git_trace)
Baca berkas `generated/<YYYY-MM>/timeline.json` dan hasilkan `generated/<YYYY-MM>/logbook.final.json`:
- **Hari dengan commit (`direct`)**: Buat deskripsi formal berdasarkan commit dan berkas yang disentuh.
- **Hari dengan catatan manual (`manual`)**: Rangkum catatan manual.
- **Hari kosong (`inferred`)**: Inferensikan kegiatan persiapan/perancangan/riset menuju commit hari kerja terdekat berikutnya (`subsequent_commits`).
Setiap tanggal memiliki struktur:
```json
{
  "date": "YYYY-MM-DD",
  "status": "OK",
  "evidence_level": "direct",
  "confidence": 0.95,
  "activity": "Deskripsi kegiatan dalam bahasa Indonesia baku...",
  "repositories": ["repo-name"],
  "evidence_refs": ["repo-name:short_sha"]
}
```

### 4. Finalisasi, Render, dan Compile PDF
```bash
python3 -m scripts.logbook.cli finalize --month <YYYY-MM>
```
Perintah ini akan:
1. Memvalidasi skema dan kepatuhan aturan bukti kerja.
2. Merender `metadata.tex` dan `activities.tex` dengan karakter LaTeX yang telah di-*escape*.
3. Mengompilasi PDF resmi berstandar Polinema menggunakan `latexmk -xelatex`.
4. Menghasilkan ringkasan di `generated/<YYYY-MM>/generation-report.md`.

### 5. Berikan Hasil ke Pengguna
Tampilkan ringkasan metrik (total commit, hari direct, hari inferensi) dan tautan berkas PDF di `dist/logbook-<YYYY-MM>.pdf`.
