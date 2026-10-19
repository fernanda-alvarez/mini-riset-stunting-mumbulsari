# Tabel analisis 1–5 (Tahap 2)

Dibuat 19 Okt 2026 oleh `skrip/analisis_tahap2.py` dari `anak_bersih.csv` (lokal) dan `rekap_tambahan/sasaran_cakupan_cek2024.xlsx`. Semua agregat, aman di git. Definisi flag dan skenario S0–S3: `../README.md`. Skrip menjalankan verifikasi silang (kasus per desa-tahun = jumlah per bulan = `desa_bulan.csv`; n analisis 5 = n analisis 1; sasaran dan terukur cocok dengan sheet Cakupan, selisih ≤ 8 anak tanpa desa).

## Metode
- **Titik estimasi**: anak-bulan dikumpulkan, sama dengan situs dan Laporan Puskesmas. Outcome biner dari label situs; kategori Outlier dikeluarkan dari penyebut.
- **CI 95%**: bootstrap klaster per anak (500 ulangan, seed 20261019), karena anak yang sama diukur berulang. CI bulanan: Wilson (satu bulan = anak berbeda).
- **Uji hipotesis** (antar desa, JK, umur): satu pengukuran acak per anak per tahun (seed tetap) supaya sampel bebas. "Pertama" tidak dipakai karena Januari sering anomali.
- **Tren**: Mann-Kendall + Sen slope (33 titik bulanan). **Segmented**: OLS dengan titik patah Jan 2026, SE Newey-West (lag 3); parameter `lompatan_2026-01_pp` = lompatan level pada Jan 2026.

## Berkas
| Berkas | Isi |
|---|---|
| `a1_prevalensi_desa_tahun.csv` | prevalensi stunting, wasting, underweight, gizi lebih per skenario × desa (+SEMUA) × tahun, dengan CI klaster |
| `a1_prevalensi_bulan.csv` | prevalensi bulanan gabungan semua desa per skenario |
| `a2_seri_bulanan.csv`, `a2_tren_mannkendall.csv`, `a2_tren_segmented.csv` | deret bulanan per desa dan hasil uji tren |
| `a3_antar_desa.csv` | prevalensi, residual terstandar, dan uji chi-square antar 7 desa per tahun |
| `a4_cakupan_desa_bulan.csv`, `a4_cakupan_bulan.csv` | terukur / sasaran (sasaran hanya ada 2025-01..2026-09; 2024 tanpa penyebut) |
| `a5_umur_jk.csv`, `a5_uji_jk_umur.csv` | prevalensi menurut kelompok umur × JK (S0, S1) dan uji chi-square JK dan umur |

## Temuan utama (baca bersama peringatan)
1. **Prevalensi gabungan Puskesmas (S0)**: stunting 6,5% (2024), 13,1% (2025), 7,0% (2026); wasting 7,8%, 8,9%, 6,1%; underweight 10,1%, 12,4%, 10,6%. Naik-turun ini **bukan tren nyata**, lihat poin 2–3.
2. **Prevalensi per desa berubah tidak masuk akal antar tahun**: stunting Mumbulsari 4,2% → 28,4% → 1,9%; Lengkong 14,0% → 24,2% → 2,4%; Tamansari 1,3% → 14,9% → 8,9%; Suco 8,7% → 8,5% → **21,5%** (satu-satunya desa yang naik tajam di 2026); Lampeji 4,8% → 6,2% → 1,4%. Perubahan sebesar itu pada populasi yang stabil tidak lazim, dan yang melonjak/ambruk adalah desa-desa yang diketahui bermasalah pencatatannya (`../README.md`). Selisih antar desa signifikan (chi-square p < 0,001 tiap tahun, termasuk S3), tetapi **lebih mencerminkan cara pencatatan per desa daripada beda biologis**.
3. **Tren pooled tidak dapat ditafsirkan sebagai tren**: segmented S0 menunjukkan lompatan −10,6 poin stunting pada Jan 2026 (p < 0,001); itu terjadi bersamaan dengan lonjakan cakupan dan perubahan pencatatan. Pada S1 komposisi desa berubah setelah Jan 2026 (tiga desa dibuang), jadi tren naik yang tampak di S1 (Sen +3,0 poin/tahun, p = 0,0004) adalah artefak komposisi, bukan kenaikan stunting. Tren harus dibaca **per desa dan dalam periode yang metode pencatatannya sama**.
4. **Cakupan**: 56–72% sepanjang 2025, **92–95% sejak Jan 2026**. Per desa 2026: Lampeji, Lengkong, Mumbulsari rata-rata **100%** dari sasaran, tepat pada tiga desa yang berpola satu tanggal ukur per bulan dan stunting ±1–2%. Cakupan 100% dengan satu tanggal per bulan lebih mirip pengisian daftar sasaran massal daripada pengukuran nyata. Suco justru turun (86% → 79%). 2024 tanpa sasaran; jumlah terukur 2.741–3.216 per bulan.
5. **Umur dan JK** (uji pada satu pengukuran acak per anak per tahun, S0): menurut kelompok umur, ketiga outcome berbeda bermakna hampir di semua tahun (p < 0,05; pengecualian underweight 2025, p = 0,06). Menurut JK: stunting bermakna di 2025 dan 2026 (p = 0,006 dan 0,001) tetapi tidak di 2024 (p = 0,08); wasting bermakna semua tahun (p 0,017–0,030); underweight bermakna 2024 dan 2026 (p = 0,004 dan 0,048) tetapi tidak 2025 (p = 0,54). Arah dan besar efek ada di `a5_umur_jk.csv` dan belum dibaca di sini. Uji ini juga terpengaruh kualitas data per desa, dan beberapa p mendekati 0,05 tanpa koreksi perbandingan ganda (18 uji).

## Implikasi
Prevalensi absolut per desa-tahun dan perbandingan antar desa tidak boleh dilaporkan tanpa kualifikasi. Analisis yang lebih tahan terhadap masalah ini: perubahan **dalam anak** (analisis 9, longitudinal), distribusi z-score (analisis 6), dan analisis hanya pada desa-periode dengan pencatatan yang konsisten (Karangkedawung, Kawangrejo, Suco sepanjang 2024–2026; Lampeji/Lengkong/Mumbulsari 2025).
