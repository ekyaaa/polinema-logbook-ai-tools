# Standar Logbook Mingguan (Weekly Logbook Rules)

Aturan ini mendefinisikan arsitektur dan standar kompilasi untuk **Logbook Mingguan (*Weekly Logbook*)** dengan output di direktori `dist/final/`.

---

## 1. Definisi 15 Minggu Kerja
Logbook mingguan membagi masa magang (Juli s.d. Oktober 2026) menjadi 15 periode:
1. `Juli-1`: 1 – 5 Juli 2026 (Rabu – Minggu, 3 hari kerja)
2. `Juli-2`: 6 – 12 Juli 2026 (Senin – Minggu, 5 hari kerja)
3. `Juli-3`: 13 – 19 Juli 2026 (Senin – Minggu, 5 hari kerja)
4. `Juli-4`: 20 – 26 Juli 2026 (Senin – Minggu, 5 hari kerja; 23–24 Jul: Lomba Solo)
5. `Juli-5`: 27 Juli – 2 Agustus 2026 (Senin – Minggu, 5 hari kerja)
6. `Agustus-1`: 3 – 9 Agustus 2026 (Senin – Minggu, 5 hari kerja)
7. `Agustus-2`: 10 – 16 Agustus 2026 (Senin – Minggu, 5 hari kerja; 10 Agu: Sakit)
8. `Agustus-3`: 17 – 23 Agustus 2026 (Senin – Minggu, 5 hari kerja)
9. `Agustus-4`: 24 – 30 Agustus 2026 (Senin – Minggu, 5 hari kerja)
10. `Agustus-5`: 31 Agustus – 6 September 2026 (Senin – Minggu, 5 hari kerja; 1–4 Sep: Lomba KMIPN)
11. `September-1`: 7 – 13 September 2026 (Senin – Minggu, 5 hari kerja; 7–11 Sep: Lomba KMIPN)
12. `September-2`: 14 – 20 September 2026 (Senin – Minggu, 5 hari kerja)
13. `September-3`: 21 – 27 September 2026 (Senin – Minggu, 5 hari kerja)
14. `September-4`: 28 September – 4 Oktober 2026 (Senin – Minggu, 5 hari kerja; 28 Sep: Sakit)
15. `Oktober-1`: 5 – 11 Oktober 2026 (Senin – Minggu, 5 hari kerja)

---

## 2. Standar Tepat 1 Halaman (*Strict Single-Page Layout*)
Seluruh berkas PDF mingguan **WAJIB pas dalam 1 halaman** (tidak boleh tumpah ke halaman 2).

Parameter vertikal LaTeX yang telah distandarisasi untuk mencapai 1 halaman:
- **Geometry (`template/preamble.tex`)**:
  - `top=4.4cm` (ruang untuk Kop Surat header Polinema)
  - `bottom=1.4cm` (margin bawah optimal)
  - `headheight=3.3cm`, `headsep=0.4cm`, `footskip=0.4cm`
- **Spasi Paragraf & Tabel**:
  - `\setlength{\parindent}{0pt}`
  - `\setlength{\parskip}{0pt}`
  - `\renewcommand{\arraystretch}{1.08}` pada tabel logbook
- **Judul Cover (`template/cover.tex`)**:
  - Menggunakan `{\centering ... \par}\vspace{4pt}` untuk menghindari margin berlebih dari environment `center`.
- **Tabel Identitas (`template/identity.tex`)**:
  - `\renewcommand{\arraystretch}{1.05}` dan `\vspace{4pt}` setelah tabel.
- **Blok Tanda Tangan (`template/signatures.tex`)**:
  - Tanda tangan dibungkus dalam `\begin{minipage}{\textwidth} ... \end{minipage}`.
  - Spasi vertikal antarbagian: `\vspace{2pt}`.
  - `Mengetahui,` ditulis menggunakan `{\centering Mengetahui,\par}`.
  - Ketinggian ruang gambar tanda tangan: `\\[1.2cm]`.

---

## 3. Direktori Output & Naming Convention
1. Seluruh PDF mingguan dikompilasi dan disimpan di direktori:
   `dist/final/logbook-<NamaMinggu>.pdf`
   Contoh:
   - `dist/final/logbook-Juli-1.pdf`
   - `dist/final/logbook-Agustus-2.pdf`
   - `dist/final/logbook-Oktober-1.pdf`
2. Generator batch dijalankan melalui:
   ```bash
   python3 -m scripts.generate_weekly
   ```
