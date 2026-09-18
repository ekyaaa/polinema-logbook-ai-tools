# Daily Activity Synthesis Prompt

## Tugas
Menganalisis linimasa harian pada satu tanggal tertentu dan menyusun satu objek JSON ringkasan kegiatan harian yang formal dan profesional.

---

## 1. Format Output JSON
```json
{
  "date": "YYYY-MM-DD",
  "status": "OK",
  "evidence_level": "direct",
  "confidence": 0.95,
  "activity": "Deskripsi kegiatan dalam 1 kalimat formal Bahasa Indonesia (maksimal 35 kata)...",
  "repositories": ["nama-repo"],
  "evidence_refs": ["nama-repo:short_sha"]
}
```

---

## 2. Aturan untuk Hari dengan Commit Langsung (`evidence_level: "direct"`)
- Rangkum inti pesan commit dan berkas yang disentuh menjadi 1 kalimat padat yang mengalir.
- Sebutkan nama modul/repositori secara eksplisit.
- Cantumkan `evidence_refs: ["<repo>:<short_sha>"]`.
- `status: "OK"`.

---

## 3. Aturan untuk Hari dengan Catatan Manual (`evidence_level: "manual"`)
- Jika tanggal memiliki `manual_notes`, jadikan catatan tersebut sebagai dasar kegiatan.
- Rumuskan menjadi kalimat formal (misal: *"Mengikuti diskusi mingguan dan sinkronisasi kebutuhan modul bersama tim pembimbing lapangan."*).
- `status: "OK"`.

---

## 4. Aturan untuk Hari Kosong (Inferensi Cerdas ala `git_trace`)
Jika tanggal tidak memiliki commit langsung dan tidak ada catatan manual:
1. **Periksa `subsequent_commits` (Commit Terdekat Berikutnya)**:
   - Rumuskan kegiatan sebagai persiapan, riset teknis, analisis kebutuhan, perancangan antarmuka/skema data, atau penyiapan lingkungan kerja menuju fitur commit tersebut.
   - Contoh: Jika hari berikutnya commit *fitur filter DPS*, kegiatan hari kosong dapat berupa: *"Menganalisis kebutuhan logika filter status dokumen dan merancang parameter pencarian pada modul shin_buzai."*
2. **Jika `subsequent_commits` Kosong, Periksa `prior_commits` (Commit Sebelumnya)**:
   - Rumuskan kegiatan sebagai pengujian fungsionalitas, peninjauan kode (*code review*), refaktorisasi, atau dokumentasi teknis fitur yang baru selesai dikerjakan.
3. **Format JSON Hari Inferensi**:
```json
{
  "date": "YYYY-MM-DD",
  "status": "OK",
  "evidence_level": "inferred",
  "confidence": 0.85,
  "activity": "Deskripsi kegiatan persiapan/analisis/pengujian relevan...",
  "repositories": ["nama-repo-terkait"],
  "evidence_refs": []
}
```
4. **Variasi Kalimat**: DILARANG KERAS mengulang-ulang kalimat yang sama persis untuk hari kosong yang berurutan. Variasikan kata kerja (misal: merancang, meninjau, menganalisis, menguji, mempersiapkan).
