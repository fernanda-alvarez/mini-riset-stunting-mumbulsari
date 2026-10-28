# Skrip

Semua kode analisis proyek ini. Data per anak tidak ada di repo (lihat `README.md` di akar), jadi skrip yang membacanya tidak bisa dijalankan di sini, tetapi isinya bisa dibaca untuk memeriksa cara kerjanya. Jalur di bawah relatif terhadap akar repo.

## Alur analisis utama (SigiziKesga, 2024–2026)

```
Daftar_Status_Gizi_YYYY-MM.xls (per anak, lokal)
   │  bersihkan_data_anak.py        pembersihan, pseudonim, penanda skenario
   ▼
anak_bersih.csv (lokal)
   │  siapkan_data_spss_r.py        penanda s0–s3, sampel 1 pengukuran per anak per tahun
   ▼
anak_analisis.csv (lokal)
   ├─ spss/analisis_spss.sps        A3, A4, A5 (uji), P2      → data/sigizi/analisis_spss/
   └─ analisis_r_1..3.R             A1, A2, A5–A9, P1, P3     → data/sigizi/analisis_r/
            │  bandingkan_hasil.R   cek silang dengan hasil Python
            │  gabung_hasil_rs.py   gabung R + SPSS           → data/sigizi/analisis_rs/
            ▼
   bangun_workbook_analisis.py      workbook Excel akhir
   siapkan_laporan.py               gambar PNG + tabel_laporan.json
   bangun_laporan.js                laporan Word
```

`jalankan_analisis_sigizi.sh` di akar repo menjalankan urutan ini dari `siapkan_data_spss_r.py` sampai `siapkan_laporan.py`.

**Skenario S0–S3.** Hasil dihitung pada empat himpunan data untuk menguji kekokohan terhadap masalah kualitas pengukuran: S0 semua data yang lolos pembersihan; S1 tanpa Lampeji, Mumbulsari, dan Lengkong untuk Jan–Sep 2026; S2 hanya desa-tahun dengan heaping tinggi badan rendah (< 70%); S3 tanpa desa-bulan anomali (TB/U Outlier ≥ 10% atau stunting ≥ 50%). Definisi mengikuti subbab 3.8.2 laporan; aturan lengkap ada di `data/sigizi/RENCANA_ANALISIS.md`.

**Metode bersama.** Estimasi titik memakai anak-bulan yang dikumpulkan; IK 95% memakai bootstrap klaster per anak (B = 500). Uji hipotesis memakai satu pengukuran acak per anak per tahun supaya sampel bebas. Python dan R/SPSS sengaja mengerjakan analisis yang sama supaya bisa dibandingkan; selisih hanya pada batas IK bootstrap (RNG berbeda).

### Pembersihan dan persiapan data

| Skrip | Fungsi |
|---|---|
| `baca_export_sigizi.py` | Pembaca berkas export SigiziKesga (HTML bergaya `.xls`) berbasis regex. Dipakai skrip audit dan pembersihan. |
| `bersihkan_data_anak.py` | Tahap 1: gabung berkas bulanan, beri ID acak (HMAC-SHA256 dengan garam lokal), buang nama, NIK, alamat, dan tanggal lahir, tandai baris bermasalah (`f_*`), definisikan skenario S0–S3. Keluaran agregat: `desa_bulan.csv` dan `log_cleaning.txt`. |
| `siapkan_data_spss_r.py` | Menambah kolom `s0..s3`, `pa_s0..pa_s3`, `kel_umur`, `t` agar R dan SPSS memakai sampel yang sama dengan Python. |

### Audit kualitas data (hanya mencetak agregat)

| Skrip | Fungsi |
|---|---|
| `audit_daftar_status_gizi.py` | Audit akhir berkas bulanan; diagnosis selisih jumlah anak posyandu vs Puskesmas. |
| `audit_kualitas_daftar.py` | Per bulan: kolom kosong, tanggal ukur terpadat, outlier z-score, nilai aneh, NIK berulang. |
| `audit_heaping_tinggi.py` | Penumpukan digit desimal tinggi badan dan penumpukan z-score TB/U tepat di atas −2 SD. |
| `periksa_kolom_faktor.py` | Kelengkapan faktor risiko (BB/TB lahir, BBLR, PBLR, MBG, KPSP) dan jumlah bulan terukur per anak. |

### Analisis versi Python (acuan)

| Skrip | Fungsi |
|---|---|
| `analisis_tahap2.py` | A1–A5: prevalensi, tren, perbedaan antar desa, cakupan, umur dan jenis kelamin. |
| `analisis_tahap2b.py` | A6–A9: distribusi z-score, kurva umur, faktor risiko (regresi logistik IRLS dengan SE robust klaster, ditulis sendiri karena `statsmodels` tidak tersedia di ARM64), analisis longitudinal. |
| `analisis_tahap2c.py` | P1–P3: Kaplan-Meier kejadian terkonfirmasi dengan delayed entry, bulan terukur per anak, penumpukan digit, simulasi pembulatan dengan LMS WHO. |

### Analisis versi R dan SPSS (dipakai untuk laporan)

| Skrip | Fungsi |
|---|---|
| `r_umum.R` | Fungsi bersama: bootstrap klaster, interval Wilson, pengelompokan desa, penulisan tabel. |
| `analisis_r_1.R` | A1, A2 (Mann-Kendall, Sen, regresi segmen), tabel A5, A6, A7. |
| `analisis_r_2.R` | A8 (regresi logistik klaster) dan A9 (longitudinal). |
| `analisis_r_3.R` | P1 (Kaplan-Meier, log-rank terstratifikasi desa) dan P3. |
| `spss/analisis_spss.sps` | A3, A4, A5 (uji chi-kuadrat), P2 di SPSS 27. |
| `spss/jalankan_spss.py` | Menjalankan syntax SPSS tanpa antarmuka lewat Python bawaan SPSS. |
| `bandingkan_hasil.R` | Membandingkan tabel Python dengan R/SPSS: kolom deterministik harus sama, kolom acak boleh beda tipis. |
| `gabung_hasil_rs.py` | Menggabung tabel R dan SPSS ke `data/sigizi/analisis_rs/` dengan struktur yang dibaca skrip laporan. |

### Rekap situs dan sasaran cakupan

| Skrip | Fungsi |
|---|---|
| `bangun_rekap_status_gizi.py` | Excel dan CSV rekap status gizi per desa dan posyandu dari JSON hasil pengambilan situs. |
| `bangun_sasaran_cakupan.py` | Excel sasaran, cakupan (terukur / sasaran), dan pengecekan 2024. |

### Workbook, gambar, dan laporan

| Skrip | Fungsi |
|---|---|
| `bangun_workbook_analisis.py` | `Analisis_Stunting_Mumbulsari.xlsx` dari tabel agregat. |
| `siapkan_laporan.py` | Gambar laporan dan `tabel_laporan.json` (angka berformat Indonesia). |
| `buat_gambar_laporan.py` | Tiga gambar tambahan: diagram alir, sebaran digit tinggi, tren bulanan. |
| `gambar_kerangka.py` | Kerangka teori dan konsep (Bab 2). |
| `bangun_laporan.js` | Menyusun laporan Word (Node, paket `docx`). Narasi dan penanda sitasi ada di sini. |
| `pasang_sitasi_zotero.py` | Mengubah penanda `[@id]` menjadi field Zotero dan menyisipkan daftar pustaka APA 7 (butuh Zotero terbuka). |
| `perbarui_daftar_isi.ps1` | Memperbarui nomor keterangan, daftar isi, daftar tabel, dan daftar gambar lewat Word (Windows). |

Membangun ulang `.docx` dari skrip menghapus field Zotero. Urutan yang benar ada di `data/sigizi/laporan/README.md`.

## Alur lama: register MTBS (2025–2026)

Analisis awal atas register MTBS Klaster 2 sebelum data SigiziKesga tersedia. Dijalankan lewat `jalankan_semua.sh` di akar repo. Masukannya (register sumber dan berkas olahan) tidak ada di repo.

| Skrip | Fungsi |
|---|---|
| `cleanup_mtbs.py` | Membersihkan register; semua koreksi dicatat di sheet `Log_Perubahan`. |
| `siap_olah_mtbs.py` | Menyaring kriteria inklusi; baris yang dikeluarkan dipindah ke sheet `Dikeluarkan` beserta alasannya. |
| `zscore_mtbs.R` | Z-score WHO 2006 (paket `anthro`) dan tabel deskriptif. |
| `analisis_lanjut_mtbs.R` | Konsistensi PB/BB antar kunjungan dan hubungan status gizi dengan diagnosis MTBS. |
| `kelengkapan_mtbs.R`, `kualitas_tambahan_mtbs.R` | Kelengkapan data, prevalensi SD-adjusted, digit preference, sensitivitas termasuk 2024. |
| `tabel_grafik_mtbs.R` | Tabel dan grafik laporan MTBS. |
| `ringkasan_html.py`, `percantik_excel.py` | Ringkasan HTML dan penataan tampilan Excel. |
| `buat_laporan_docx.py` | Menyusun laporan Word MTBS dari draf proposal dan hasil analisis. |
| `daftar_tindak_lanjut.py`, `buat_form_docx.py`, `sinkronkan_isian_docx.py` | Daftar balita untuk tindak lanjut Puskesmas dan formulir verifikasi. Hasilnya memuat identitas (internal), tidak diunggah. |
