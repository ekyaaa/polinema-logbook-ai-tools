# Workflow: Generate Monthly Logbook

Workflow untuk menghasilkan dokumen logbook bulanan magang Polinema secara otomatis berbasis bukti kerja Git.

---

## Prasyarat
- Konfigurasi mahasiswa dan magang sudah terisi di folder `config/`.
- Perangkat lokal memiliki `git`, `python3`, dan `latexmk` (dengan `xelatex`).

---

## Langkah-langkah

### 1. Tentukan Bulan Target
Tanyakan kepada user bulan yang ingin dibuat jika belum ditentukan. Format: `YYYY-MM` (contoh: `2026-09`).

### 2. Jalankan Prepare
```bash
python3 -m scripts.logbook.cli prepare --month <YYYY-MM>
```
Perintah ini akan:
1. Menemukan semua repositori Git di bawah `project_root`.
2. Mengumpulkan commit sesuai identitas mahasiswa untuk bulan tersebut (`evidence.json`).
3. Membangun kalender jadwal kerja dan mengikat bukti kerja ke tanggal yang sesuai (`timeline.json`).

### 3. Buat Draft Logbook Harian
Baca berkas `generated/<YYYY-MM>/timeline.json` dan hasilkan `generated/<YYYY-MM>/logbook.draft.json`.
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
Jika tidak ada bukti:
```json
{
  "date": "YYYY-MM-DD",
  "status": "NEEDS_REVIEW",
  "evidence_level": "none",
  "confidence": 0.0,
  "activity": null,
  "repositories": [],
  "evidence_refs": []
}
```

### 4. Lakukan Monthly Editing
Poles narasi kalimat pada `generated/<YYYY-MM>/logbook.final.json` agar bervariasi dan mengalir tanpa mengubah substansi fakta dan referensi commit.

### 5. Finalisasi, Render, dan Compile PDF
```bash
python3 -m scripts.logbook.cli finalize --month <YYYY-MM>
```
Perintah ini akan:
1. Memvalidasi skema dan relasi bukti terhadap timeline.
2. Merender `metadata.tex` dan `activities.tex` dengan karakter LaTeX yang telah di-*escape*.
3. Mengompilasi PDF menggunakan `latexmk -xelatex`.
4. Menghasilkan ringkasan di `generated/<YYYY-MM>/generation-report.md`.

### 6. Berikan Hasil ke Pengguna
Tampilkan ringkasan metrik (total commit, hari langsung, hari manual, hari review) dan tautan berkas PDF di `dist/logbook-<YYYY-MM>.pdf`.
