# Daily Activity Synthesis Prompt

## Tugas
Menganalisis kumpulan bukti kerja harian (Git commit, daftar berkas yang diubah, atau catatan manual) pada satu tanggal tertentu, kemudian menghasilkan satu objek JSON ringkasan kegiatan harian.

## Aturan Format JSON Output
```json
{
  "date": "YYYY-MM-DD",
  "status": "OK",
  "evidence_level": "direct",
  "confidence": 0.95,
  "activity": "Deskripsi kegiatan dalam 1 kalimat formal Bahasa Indonesia (maks 35 kata)...",
  "repositories": ["nama-repo"],
  "evidence_refs": ["nama-repo:short_sha"]
}
```

## Aturan Khusus untuk Hari Tanpa Bukti
Jika pada tanggal tersebut tidak ada Git commit dan tidak ada catatan manual:
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
DILARANG mengarang aktivitas jika tidak ada bukti kerja sama sekali.
