# Polinema Monthly Logbook AI Generator

> **Generator Logbook Magang Industri Bulanan Otomatis Berbasis Git & AI untuk Mahasiswa Politeknik Negeri Malang (Polinema)**  
> Mengubah riwayat commit Git lokal yang berserakan menjadi dokumen logbook resmi berstandar institusi (Kop Surat, Metadata, Tabel Berwarna, dan Susunan Tanda Tangan Resmi) dalam hitungan detik.

---

## ✨ Keunggulan Utama

- 🎯 **Format 100% Resmi Polinema**: Mengikuti template resmi institusi (lengkap dengan Kop Surat Polinema di tiap halaman, tabel identitas 6 baris, header tabel abu-abu, dan tata letak tanda tangan berjenjang).
- 🤖 **Zero-Friction Prompting**: Cukup katakan ke AI: *"Tolong buatkan logbook bulan ini"*.
- 🧙‍♂️ **Interactive Onboarding**: Jika baru pertama kali di-clone, AI akan otomatis menanyakan profil magangmu dan menyimpannya secara permanen di `config.json`.
- 🔍 **Multi-Repo Auto-Discovery**: Memindai seluruh repositori Git di folder magangmu secara otomatis dan aman (read-only).
- 🧠 **Smart Empty-Day Infilling (ala GitTrace)**: Hari kerja tanpa commit akan otomatis diisikan kegiatan persiapan teknis, perancangan, riset, atau pengujian yang relevan mengarah ke commit terdekat berikutnya tanpa mengarang halusinasi di luar proyek.
- 🖨️ **Print-Ready PDF**: Menghasilkan PDF siap cetak berukuran A4 via XeLaTeX.

---

## 🚀 Cara Penggunaan (Sangat Cepat & Mudah)

### 1. Clone Repositori
```bash
git clone <url-repo-ini> polinema-logbook
cd polinema-logbook
```

### 2. Pasang Dependensi Python
```bash
pip install pyyaml pydantic
```
*(Pastikan sistem memiliki TeX Live / XeLaTeX untuk kompilasi PDF).*

### 3. Jalankan Lewat AI Assistant (Antigravity / Cursor / Claude Code / dll)
Buka folder ini di editor AI kamu, lalu ketikkan:
```text
Tolong buatkan logbook bulan ini
```
*(atau sebutkan bulan spesifik seperti: "Tolong buatkan logbook September 2026")*.

- **Penggunaan Pertama Kali**: AI akan menyapa dan meminta informasi singkat (folder proyek magang, namamu, NIM, nama mitra industri, dosen pembimbing, pembimbing lapangan).
- Jawabanmu disimpan di `config.json` sehingga kamu **tidak perlu mengisinya lagi** di bulan-bulan berikutnya.
- AI akan langsung merayapi repositori, menyusun kegiatan harian, mengisi hari kosong, dan menghasilkan berkas PDF di:
  ```text
  dist/logbook-YYYY-MM.pdf
  ```

---

## ⚙️ Format Konfigurasi (`config.json`)

Kamu juga bisa mengisi atau mengubah `config.json` secara manual kapan saja:

```json
{
  "student": {
    "name": "Nama Lengkap Mahasiswa",
    "nim": "2341720000",
    "program": "D-IV Teknik Informatika",
    "institution": "Politeknik Negeri Malang",
    "academic_advisor": "Nama Dosen Pembimbing, S.Kom., M.T.",
    "field_supervisor": "Nama Pembimbing Lapangan"
  },
  "internship": {
    "company": "Nama Perusahaan Mitra",
    "division": "Software Engineering",
    "project_root": "/home/user/Project/Magang",
    "git_authors": {
      "names": ["username_git", "Nama Lengkap"],
      "emails": ["email@example.com"]
    }
  },
  "logbook": {
    "timezone": "Asia/Jakarta",
    "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "check_in": "07:00",
    "check_out": "16:20",
    "allow_inferred_activity": true,
    "latex_engine": "xelatex"
  }
}
```

Tersedia juga berkas referensi di [`config.example.json`](file:///home/mashupsoat/Project/polinema-logbook-ai-tools/config.example.json).

---

## 🛠️ Perintah CLI Manual (Opsional)

Jika ingin menjalankan tanpa percakapan AI:

```bash
# 1. Pindai repositori & siapkan linimasa bulan target
python3 -m scripts.logbook.cli prepare --month 2026-09

# 2. Sintesis entri kegiatan di generated/2026-09/logbook.final.json

# 3. Validasi, render template LaTeX, dan kompilasi PDF
python3 -m scripts.logbook.cli finalize --month 2026-09
```

---

## 📁 Struktur Berkas

```text
polinema-logbook/
├── config.json                     # Konfigurasi aktif profil magang
├── config.example.json             # Berkas acuan konfigurasi
├── main.tex                        # Dokumen utama LaTeX
├── template/
│   ├── preamble.tex                # Setup geometri, font, & Kop Surat Polinema
│   ├── cover.tex                   # Judul dokumen resmi
│   ├── identity.tex                # Tabel 6 baris identitas mahasiswa
│   ├── commands.tex                # Format tabel longtable dengan header abu-abu
│   ├── signatures.tex              # Susunan tanda tangan resmi berjenjang
│   └── logo_polinema.jpg           # Logo resmi Polinema
├── scripts/logbook/
│   ├── cli.py                      # Antarmuka CLI terpadu
│   ├── config.py                   # Loader konfigurasi & auto-detect Git
│   ├── discovery.py                # Pemindai repositori Git lokal rekursif
│   ├── git_reader.py               # Pengumpul commit bulanan read-only
│   ├── timeline.py                 # Penyusun linimasa hari kerja & binding bukti
│   ├── validator.py                # Validasi kepatuhan data logbook
│   ├── renderer.py                 # Generator LaTeX escaping aman
│   └── compiler.py                 # Kompilator latexmk -xelatex
├── prompts/                        # Sistem prompt untuk AI Agent
├── workflows/                      # Panduan langkah workflow
└── dist/                           # Tempat PDF hasil kompilasi
```

---

## 📄 Lisensi & Kontribusi

Dibuat untuk memudahkan mahasiswa dan rekan-rekan magang Politeknik Negeri Malang agar fokus pada pekerjaan rekayasa tanpa terbebani administrasi manual. Silakan gunakan dan sesuaikan sesuai kebutuhan magang masing-masing!
