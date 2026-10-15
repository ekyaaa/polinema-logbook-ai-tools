# Aturan Ketidakhadiran Magang (Absence & Leave Policy)

Aturan ini mendefinisikan standar penanganan hari tidak masuk (sakit, izin, dispensasi lomba, bimbingan skripsi, dll.) saat menghasilkan logbook bulanan.

---

## 1. Sumber Data Utama
Data seluruh tanggal tidak masuk dikelola secara terpusat di `config/absences.yaml`.
AI Generator dan script CLI **WAJIB** membaca file ini sebelum melakukan inferensi aktivitas harian (`inferred`) atau sintesis bukti Git (`direct`).

---

## 2. Prioritas Status Aktivitas
Jika suatu tanggal terdaftar di dalam `config/absences.yaml`:
1. **Prioritas Utama**: Tanggal tersebut **DILARANG** diisi dengan inferensi tugas magang (`inferred`) dan **DILARANG** dihubungkan dengan Git commits hari berikutnya/sebelumnya.
2. **Tingkat Bukti**: Tetapkan `evidence_level: "absent"` dan `status: "OK"`.
3. **Pengisian Kolom Tabel**:
   - **Hari, Tanggal**: Format normal (hitam), contoh: `Senin, 28 Sep 2026`.
   - **Jam Masuk**: Status singkat merah `\textcolor{red}{Sakit}` atau `\textcolor{red}{Izin}`.
   - **Jam Pulang**: Status singkat merah `\textcolor{red}{Sakit}` atau `\textcolor{red}{Izin}`.
   - **Kegiatan**: Deskripsi alasan lengkap berwarna merah `\textcolor{red}{<Alasan>}`, contoh: `\textcolor{red}{Sakit}` atau `\textcolor{red}{Izin: Mengikuti Lomba KMIPN}`.
4. **Kategori Status**:
   - Jika kategori `Sakit`: Jam Masuk & Jam Pulang diisi `Sakit`. Kegiatan diisi `Sakit` (atau keterangan sakit jika ada diagnosa/alasan spesifik).
   - Jika kategori `Izin` (termasuk lomba, bimbingan, keperluan akademik/pribadi): Jam Masuk & Jam Pulang diisi `Izin`. Kegiatan diisi alasan lengkap berawalan `Izin: ...`.

---

## 3. Kebijakan Hari Kerja & Akhir Pekan
1. Tabel logbook resmi Polinema hanya mencatat **hari kerja resmi (Senin s.d. Jumat)**.
2. Jika tanggal pada `config/absences.yaml` jatuh pada akhir pekan (Sabtu atau Minggu, contoh: 12 September 2026 atau rentang akhir pekan lomba 5-6 September 2026):
   - Data tetap tersimpan rapi di `config/absences.yaml` sebagai arsip riwayat.
   - Tanggal akhir pekan tersebut **TIDAK PERLU** dimunculkan ke dalam baris tabel logbook.

---

## 4. Format Kontrak JSON Harian (`DailyActivityEntry`)
```json
{
  "date": "2026-09-28",
  "status": "OK",
  "evidence_level": "absent",
  "confidence": 1.0,
  "activity": "Sakit",
  "check_in": "Sakit",
  "check_out": "Sakit",
  "repositories": [],
  "evidence_refs": []
}
```
Contoh untuk Izin:
```json
{
  "date": "2026-09-01",
  "status": "OK",
  "evidence_level": "absent",
  "confidence": 1.0,
  "activity": "Izin: Mengikuti Lomba KMIPN",
  "check_in": "Izin",
  "check_out": "Izin",
  "repositories": [],
  "evidence_refs": []
}
```

---

## 5. Standar Render LaTeX
Ketika dirender ke `activities.tex`, script renderer secara otomatis membungkus nilai dengan `\textcolor{red}{...}`:
```latex
\LogbookEntry
  {Senin, 28 Sep 2026}
  {\textcolor{red}{Sakit}}
  {\textcolor{red}{Sakit}}
  {\textcolor{red}{Sakit}}
```
```latex
\LogbookEntry
  {Selasa, 01 Sep 2026}
  {\textcolor{red}{Izin}}
  {\textcolor{red}{Izin}}
  {\textcolor{red}{Izin: Mengikuti Lomba KMIPN}}
```
