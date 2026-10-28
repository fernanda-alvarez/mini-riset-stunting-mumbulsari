# Skrip

Folder ini berisi seluruh kode analisis. Sebagian besar skrip membaca data per anak yang tidak diunggah ke repo (alasannya ada di [`README.md`](../README.md) di akar), sehingga tidak bisa dijalankan di sini. Kodenya tetap bisa dibaca untuk memeriksa bagaimana angka dihitung. Semua jalur di bawah dihitung dari akar repo, dan semua skrip dijalankan dari sana.

Folder ini memuat dua alur kerja yang berbeda. Alur utama (SigiziKesga, 2024–2026) adalah analisis yang menjadi dasar laporan. Alur lama (register MTBS) adalah analisis awal yang dikerjakan sebelum data SigiziKesga tersedia; kodenya dibiarkan untuk dokumentasi.

## Alur utama: data SigiziKesga 2024–2026

Alurnya berjalan dari berkas ekspor mentah sampai laporan, dalam urutan berikut.

```
Daftar_Status_Gizi_YYYY-MM.xls   (berkas ekspor per anak, hanya di komputer lokal)
   │  bersihkan_data_anak.py      pseudonimisasi, penandaan baris bermasalah, definisi skenario
   ▼
anak_bersih.csv                  (lokal)
   │  siapkan_data_spss_r.py      kolom skenario s0–s3, sampel satu pengukuran per anak per tahun
   ▼
anak_analisis.csv                (lokal)
   ├─ spss/analisis_spss.sps      A3, A4, A5 (uji), P2        → data/sigizi/analisis_spss/
   └─ analisis_r_1..3.R           A1, A2, A5–A9, P1, P3       → data/sigizi/analisis_r/
            │  bandingkan_hasil.R     cek silang dengan hasil Python
            │  gabung_hasil_rs.py     gabung hasil R dan SPSS → data/sigizi/analisis_rs/
            ▼
   bangun_workbook_analisis.py    workbook Excel akhir
   siapkan_laporan.py             gambar PNG dan tabel_laporan.json
   bangun_laporan.js              laporan Word
```

Skrip `jalankan_analisis_sigizi.sh` di akar repo menjalankan urutan ini mulai dari `siapkan_data_spss_r.py` sampai `siapkan_laporan.py`. Langkah pembersihan (`bersihkan_data_anak.py`) dijalankan sekali secara terpisah.

### Istilah yang dipakai di semua skrip

**Skenario S0–S3.** Karena masalah kualitas data tidak bisa dipastikan menyebar di mana saja, setiap hasil dihitung pada empat himpunan data. S0 adalah semua baris yang lolos pembersihan. S1 adalah S0 tanpa Lampeji, Mumbulsari, dan Lengkong pada Januari–September 2026, yaitu tiga desa yang pola datanya berubah mendadak. S2 hanya memakai desa-tahun dengan penumpukan digit tinggi badan rendah (kurang dari 70%). S3 adalah S0 tanpa desa-bulan anomali (TB/U outlier minimal 10% atau stunting minimal 50%). Skenario ini ditandai sebagai kolom `s0` sampai `s3` pada data per anak. Definisinya mengikuti subbab 3.8.2 laporan, dan aturan lengkapnya ada di [`data/sigizi/RENCANA_ANALISIS.md`](../data/sigizi/RENCANA_ANALISIS.md).

**Flag keras dan lunak.** Baris dengan flag keras (z-score penanda, tinggi atau berat nol, nilai mustahil, NIK ganda dalam satu bulan, umur di luar 0–59 bulan) dikeluarkan dari semua analisis. Flag lunak hanya menandai baris, dan baru dipakai ketika skenario dibentuk. Kolom flag diberi awalan `f_`.

**Anak-bulan dan klaster.** Satu baris data adalah satu pengukuran seorang anak pada satu bulan. Prevalensi dihitung dari gabungan semua baris, sehingga anak yang lebih sering diukur mendapat bobot lebih besar, sama seperti pada laporan Puskesmas. Karena baris-baris dari anak yang sama tidak saling bebas, interval kepercayaan dihitung dengan bootstrap klaster: yang diambil ulang adalah anak beserta seluruh pengukurannya, bukan baris satu per satu (500 ulangan, seed tetap). Uji hipotesis seperti chi-kuadrat memakai satu pengukuran acak per anak per tahun supaya sampel yang diuji saling bebas.

**Kode analisis.** A1–A9 adalah analisis utama: A1 prevalensi, A2 tren, A3 perbedaan antar desa, A4 cakupan, A5 umur dan jenis kelamin, A6 distribusi z-score, A7 kurva umur, A8 faktor risiko, A9 analisis longitudinal. P1–P3 adalah analisis tambahan yang diusulkan saat telaah laporan: P1 Kaplan-Meier dengan kejadian terkonfirmasi, P2 jumlah bulan terukur per anak, P3 penumpukan digit dan simulasi pembulatan.

### Pembersihan dan persiapan data

| Skrip | Fungsi |
|---|---|
| `baca_export_sigizi.py` | Membaca berkas ekspor SigiziKesga. Berkas berekstensi `.xls` itu sebenarnya HTML, dan pembacanya memakai regex karena pengurai HTML standar menghilangkan baris pada berkas September 2025. Dipakai oleh skrip audit dan pembersihan. |
| `bersihkan_data_anak.py` | Tahap 1. Menggabung berkas bulanan, mengganti NIK dengan ID acak (HMAC-SHA256 dengan garam lokal), membuang nama, alamat, dan tanggal lahir, menandai baris bermasalah, lalu mendefinisikan skenario S0–S3. Keluarannya `anak_bersih.csv` (lokal), serta `desa_bulan.csv` dan `log_cleaning.txt` yang hanya berisi agregat. |
| `siapkan_data_spss_r.py` | Menambahkan kolom `s0`–`s3`, `pa_s0`–`pa_s3` (penanda pengukuran acak terpilih per anak per tahun), `kel_umur`, dan `t` (indeks bulan). Pengacakan dilakukan di Python supaya R dan SPSS memakai sampel yang persis sama. |

### Audit kualitas data

Skrip-skrip ini hanya mencetak agregat, tanpa data pribadi, dan hasil cetakannya disimpan di `data/sigizi/daftar_status_gizi/`.

| Skrip | Fungsi |
|---|---|
| `audit_daftar_status_gizi.py` | Audit akhir seluruh berkas bulanan, termasuk mencari penyebab selisih jumlah anak antara data posyandu dan data Puskesmas. |
| `audit_kualitas_daftar.py` | Per bulan: kolom yang kosong, tanggal ukur yang paling padat, proporsi z-score outlier, nilai yang mustahil, dan NIK yang juga muncul pada bulan sebelumnya. |
| `audit_heaping_tinggi.py` | Penumpukan digit desimal tinggi badan (pengukuran teliti seharusnya menghasilkan sekitar 10% untuk .0 dan 10% untuk .5) serta rasio jumlah anak di rentang −2,0 sampai −1,9 SD terhadap rentang −2,1 sampai −2,0 SD. |
| `periksa_kolom_faktor.py` | Kelengkapan kolom faktor risiko (berat dan panjang lahir, BBLR, PBLR, MBG, KPSP) dan sebaran jumlah bulan terukur per anak. |

### Analisis versi Python

Versi Python dibuat lebih dulu dan menjadi acuan. Versi R dan SPSS dibuat kemudian untuk memeriksa hasilnya dengan perangkat lunak lain.

| Skrip | Fungsi |
|---|---|
| `analisis_tahap2.py` | A1–A5: prevalensi per desa, bulan, dan tahun dengan IK bootstrap klaster; tren Mann-Kendall, Sen, dan regresi segmented; chi-kuadrat antar desa; cakupan terhadap sasaran; prevalensi menurut umur dan jenis kelamin. |
| `analisis_tahap2b.py` | A6–A9: distribusi z-score, kurva umur, regresi logistik faktor risiko, dan analisis longitudinal (Kaplan-Meier, transisi status, kecepatan tumbuh). Regresi logistiknya ditulis sendiri dengan metode IRLS dan galat baku robust klaster, karena `statsmodels` tidak bisa dipasang di komputer ARM64 yang dipakai; ada uji internal yang mereproduksi odds ratio tabel 2×2. |
| `analisis_tahap2c.py` | P1–P3: Kaplan-Meier dengan kejadian terkonfirmasi (dua pengukuran berurutan di bawah −2 SD yang berjarak paling lama 3 bulan), skala umur dengan delayed entry, log-rank terstratifikasi desa, penumpukan z-score menurut digit desimal tinggi, dan simulasi pembulatan memakai tabel LMS WHO. |

### Analisis versi R dan SPSS

Versi inilah yang dipakai untuk tabel dan gambar laporan.

| Skrip | Fungsi |
|---|---|
| `r_umum.R` | Fungsi yang dipakai bersama oleh ketiga skrip R: membaca data, bootstrap klaster, interval Wilson, pengelompokan desa, dan penulisan tabel. |
| `analisis_r_1.R` | A1, A2, tabel A5, A6, dan A7. |
| `analisis_r_2.R` | A8 (regresi logistik klaster) dan A9 (longitudinal). |
| `analisis_r_3.R` | P1 (Kaplan-Meier dan log-rank terstratifikasi) dan P3 (penumpukan digit dan simulasi pembulatan). |
| `spss/analisis_spss.sps` | A3, A4, uji chi-kuadrat A5, dan P2 di SPSS 27. |
| `spss/jalankan_spss.py` | Menjalankan sintaks SPSS tanpa antarmuka melalui Python bawaan SPSS. |
| `bandingkan_hasil.R` | Membandingkan tabel Python dengan tabel R atau SPSS. Kolom deterministik (n, kasus, persen, p-value) harus sama persis, sedangkan kolom yang bergantung pada pengacakan (batas IK bootstrap, simulasi) boleh berbeda tipis. |
| `gabung_hasil_rs.py` | Menggabung tabel R dan SPSS ke `data/sigizi/analisis_rs/` dengan struktur folder yang dibaca skrip workbook dan laporan. |

### Rekap situs dan sasaran

| Skrip | Fungsi |
|---|---|
| `bangun_rekap_status_gizi.py` | Membuat Excel dan CSV rekap status gizi per desa dan posyandu dari JSON hasil pengambilan situs SigiziKesga. |
| `bangun_sasaran_cakupan.py` | Membuat Excel sasaran, cakupan (anak terukur dibagi sasaran), dan pengecekan angka 2024. |

### Workbook, gambar, dan laporan

| Skrip | Fungsi |
|---|---|
| `bangun_workbook_analisis.py` | Membuat `Analisis_Stunting_Mumbulsari.xlsx` dari tabel agregat, lengkap dengan grafik Excel. Tidak ada data pribadi di dalamnya. |
| `siapkan_laporan.py` | Membuat gambar laporan dan `tabel_laporan.json` yang berisi angka berformat Indonesia. |
| `buat_gambar_laporan.py` | Tiga gambar tambahan: diagram alir data dan skenario, sebaran digit desimal tinggi badan, dan tren bulanan dengan garis regresi segmented. |
| `gambar_kerangka.py` | Kerangka teori dan kerangka konsep untuk Bab 2. |
| `bangun_laporan.js` | Menyusun laporan Word dengan paket Node `docx`. Narasi dan penanda sitasi ada di skrip ini. |
| `pasang_sitasi_zotero.py` | Mengubah penanda `[@id]` menjadi field sitasi Zotero dan menyisipkan daftar pustaka APA 7. Zotero harus terbuka. |
| `perbarui_daftar_isi.ps1` | Memperbarui nomor keterangan tabel dan gambar, daftar isi, daftar tabel, dan daftar gambar lewat Word di Windows. |

Membangun ulang `.docx` dari skrip akan menghapus field Zotero, jadi `pasang_sitasi_zotero.py` dan `perbarui_daftar_isi.ps1` harus dijalankan lagi sesudahnya. Urutan lengkapnya ada di [`data/sigizi/laporan/README.md`](../data/sigizi/laporan/README.md).

## Alur lama: register MTBS 2025–2026

Sebelum data SigiziKesga tersedia, analisis pertama dikerjakan pada register MTBS Klaster 2 Puskesmas Mumbulsari. Alur ini dijalankan dengan `jalankan_semua.sh` di akar repo. Register sumber dan berkas olahannya tidak ada di repo.

| Skrip | Fungsi |
|---|---|
| `cleanup_mtbs.py` | Membersihkan register. File sumber tidak diubah, dan semua koreksi dicatat di sheet `Log_Perubahan`. |
| `siap_olah_mtbs.py` | Menerapkan kriteria inklusi. Baris yang tidak memenuhi syarat tidak dihapus, tetapi dipindah ke sheet `Dikeluarkan` beserta alasannya. |
| `zscore_mtbs.R` | Menghitung z-score WHO 2006 dengan paket `anthro` dan tabel deskriptif. |
| `analisis_lanjut_mtbs.R` | Memeriksa konsistensi berat dan panjang badan antar kunjungan pada anak yang sama, dan hubungan status gizi dengan diagnosis MTBS. |
| `kelengkapan_mtbs.R`, `kualitas_tambahan_mtbs.R` | Kelengkapan data, prevalensi dengan penyesuaian SD, preferensi digit, dan analisis sensitivitas yang menyertakan 2024. |
| `tabel_grafik_mtbs.R` | Tabel dan grafik untuk laporan MTBS. |
| `ringkasan_html.py`, `percantik_excel.py` | Halaman ringkasan HTML dan penataan tampilan berkas Excel. |
| `buat_laporan_docx.py` | Menyusun laporan Word MTBS dari draf proposal dan hasil analisis. |
| `daftar_tindak_lanjut.py`, `buat_form_docx.py`, `sinkronkan_isian_docx.py` | Daftar balita bermasalah gizi untuk tindak lanjut Puskesmas dan formulir verifikasinya. Keluarannya memuat identitas dan bersifat internal, jadi tidak diunggah. |
