# Mini Riset: Status Gizi Balita pada Kunjungan MTBS, Puskesmas Mumbulsari 2025–2026

KOAS Ilmu Kesehatan Masyarakat, FK Universitas Jember.

## Struktur folder

| Folder | Isi |
|---|---|
| `data/sumber/` | Snapshot register asli dari puskesmas. Hanya dibaca, jangan diubah. Memuat identitas anak (tidak masuk git). |
| `data/olahan/` | Hasil tiap tahap (kosong sampai dataset baru diproses): Data Bersih → Siap Olah → Z-score → Analisis Lanjut → Tabel & Grafik, Kelengkapan & Kualitas, Kualitas Tambahan, Daftar Tindak Lanjut (INTERNAL). |
| `data/sensitivitas/` | Analisis sensitivitas yang memasukkan kunjungan Juli–Desember 2024. |
| `grafik/` | Gambar G0–G4 yang dipakai di laporan. |
| `skrip/` | Semua skrip Python, R, dan PowerShell. |
| `referensi/` | 16 referensi (`.bib`, salinan `.json` dari Zotero) dan gaya sitasi `.csl`. |
| `naskah/` | Draf proposal (sumber laporan). Laporan `.docx` dibuat di folder induk ini, PDF lama ada di `arsip/`. |
| `presentasi/` | Slide presentasi. |
| `arsip/` | Hasil kerja yang sudah selesai/dibekukan, satu subfolder per snapshot (struktur sama dengan folder induk). `snapshot_2026-10-13` = data register 13 Okt 2026 beserta laporan, grafik, presentasi, form, dan TODO-nya. |
| `data/sigizi/` | Data SigiziKesga Jan 2025–Okt 2026. `rekap_status_gizi/` = Excel rekap per desa (agregat; **sheet `Laporan Puskesmas` = dataset analisis tingkat desa**). `daftar_status_gizi/` = dokumentasi dataset per anak. Baca `README.md` di tiap subfolder dulu. Data per anak (memuat identitas anak, tidak masuk git) ada di `data/sumber/sigizi_daftar_status_gizi_2026-10-19/`; `rekap_insiden_stunting/` = 10 berkas rekap insiden stunting per desa dan jenis kelamin (agregat, Jan–Okt 2026). `rekap_tambahan/` = Sasaran Anak (penyebut), Status Gizi & Usia (+JK), dan cek volume 2024. `inventaris_sigizikesga.md` = peta semua laporan situs dan analisis yang layak. |

Daftar pekerjaan untuk dataset baru ada di `TODO.md`.

## Menjalankan ulang

```bash
sh jalankan_semua.sh
```

Dijalankan dari folder ini. Urutannya: siap olah → z-score (WHO 2006, paket R `anthro`) → analisis lanjut → tabel dan grafik → kelengkapan dan kualitas → sensitivitas 2024 → daftar tindak lanjut → laporan `.docx` → sitasi Zotero → daftar isi. PDF tidak dibuat ulang otomatis (ekspor manual dari Word bila perlu).

Data Bersih dibuat sekali dari data sumber dengan `skrip/cleanup_mtbs.py` (perintah ada di komentar `jalankan_semua.sh`).

## Catatan

- Laporan di folder induk ini dihasilkan skrip `buat_laporan_docx.py` dari draf proposal. Jangan diedit langsung, karena akan tertimpa saat build. Ubah teksnya di skrip.
- Skrip membaca draf per nomor paragraf. Kalau struktur draf berubah, build berhenti dengan pesan "draf tidak sesuai peta".
- Sitasi memakai field Zotero (gaya NLM/Vancouver bernomor). Di Word: tab Zotero → Refresh.
- File yang memuat identitas anak (data sumber, Data Bersih, Daftar Tindak Lanjut, form isian) tidak masuk git dan tidak boleh dibagikan di grup.
