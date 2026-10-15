# Aturan Konfigurasi & Privasi (Configuration & Privacy Rules)

Aturan ini mengatur standar pengelolaan konfigurasi, identitas pengguna, aset tanda tangan, dan perlindungan data sensitif dalam sistem Polinema Logbook Generator.

---

## 1. Konfigurasi Terpadu (`config.json`)
1. Seluruh data profil mahasiswa, pembimbing, mitra industri, dan repositori dikelola terpusat di `config.json` pada root repositori.
2. Template resmi disediakan pada `config.example.json`.
3. `config.json` **WAJIB** masuk ke dalam `.gitignore` dan **DILARANG KERAS** dicommit ke remote Git untuk melindungi data identitas mahasiswa (NIM, email, path direktori lokal).
4. Struktur `config.json` memuat:
   - `student.name`: Nama lengkap resmi mahasiswa (digunakan di tabel identitas).
   - `student.signature_name`: Nama singkat resmi untuk teks tanda tangan di bawah gambar ttd (contoh: `Ekya Muhammad Hasfi F.`).
   - `student.nim`: Nomor Induk Mahasiswa.
   - `student.program`: Program Studi (default: `D-IV Teknik Informatika`).
   - `student.academic_advisor`: Nama Dosen Pembimbing lengkap dengan gelar.
   - `student.field_supervisor`: Nama Pembimbing Lapangan / Mentor industri.
   - `internship.company`: Nama resmi mitra industri tempat magang.
   - `internship.project_root`: Path absolut ke folder tempat repositori magang berada.
   - `internship.git_authors`: Daftar `names` dan `emails` Git author mahasiswa.
   - `logbook.check_in` & `logbook.check_out`: Jam kerja standar (default: `07:00` dan `16:20`).

---

## 2. Manajemen Ketidakhadiran (`config/absences.yaml`)
1. Seluruh catatan izin, sakit, lomba, dan bimbingan skripsi disimpan di `config/absences.yaml`.
2. Template contoh disediakan di `config/absences.example.yaml`.
3. `config/absences.yaml` bersifat privat dan di-ignore oleh Git via `.gitignore`.
4. Generator logbook memprioritaskan data ini di atas commit Git atau inferensi tugas. Hari tidak masuk otomatis dirender dengan teks berwarna merah (`\textcolor{red}{...}`).

---

## 3. Keamanan Tanda Tangan Digital (`assets/`)
1. Gambar tanda tangan digital:
   - `assets/ttd_mahasiswa.png`: Tanda tangan mahasiswa.
   - `assets/ttd_pendamping_industri.png`: Tanda tangan mentor / pembimbing lapangan industri.
2. Folder `assets/` di-ignore secara ketat oleh `.gitignore` (`assets/*.png`, `assets/*.jpg`, dll.) sehingga tanda tangan legal mahasiswa dan industri tidak bocor ke publik.
3. Posisi tanda tangan:
   - Mahasiswa: Ditampilkan di atas `\StudentSignatureName`.
   - Pembimbing Lapangan: Ditampilkan di kanan bawah di atas `\FieldSupervisor`.
   - Dosen Pembimbing: Dibiarkan kosong untuk tanda tangan basah / persetujuan kampus.

---

## 4. Perlindungan Artefak & Konteks Crawling
1. Folder `generated/` menyimpan linimasa komit, berkas yang disentuh (*changed files*), dan ringkasan kerja. Folder ini bersifat lokal dan masuk ke `.gitignore`.
2. Folder `dist/` (termasuk `dist/final/`) berisi hasil kompilasi PDF dan berkas sementara LaTeX (`.aux`, `.log`, `.xdv`, dll.), di-ignore secara penuh.
3. Seluruh sesi dan log agen (`.agents/logs/`, `events.jsonl`, `scratch/`) tidak dicommit agar repositori tetap bersih.
