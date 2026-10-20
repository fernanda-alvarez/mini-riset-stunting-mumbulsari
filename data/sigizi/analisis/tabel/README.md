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

# Analisis 6–9 (`skrip/analisis_tahap2b.py`, 19 Okt 2026)

Metode tambahan: regresi logistik ditulis sendiri (`statsmodels` tidak bisa dipasang di ARM64), IRLS dengan SE robust klaster per anak; **self-test lolos** (reproduksi OR silang tabel 2×2 dan SE Woolf). Verifikasi: jumlah pasangan ≤ jumlah baris, kurva KM menurun monoton.

| Berkas | Isi |
|---|---|
| `a6_zscore_ringkas.csv`, `a6_zscore_histogram_tbu_s0.csv`, `a6_zscore_bulanan_s0.csv` | rerata, SD, persentil z-score per desa-tahun (S0, S3); histogram TB/U; deret bulanan |
| `a7_kurva_umur.csv` | rerata z-score dan prevalensi per kelompok umur 3 bulan × tahun (S0, S3) |
| `a8_faktor_risiko.csv` | OR (CI 95%) BBLR, PBLR, JK, umur terhadap stunting, wasting, underweight; model A (BBLR), B (PBLR), C (keduanya); S0, S1, S3 |
| `a9_transisi_status.csv` | insiden, pemulihan, dan perubahan status per bulan pada anak yang terukur di dua bulan berturutan |
| `a9_kecepatan_tumbuh.csv` | selisih tinggi antar bulan berturutan (cm/bulan) menurut desa-tahun dan umur |
| `a9_km_stunting.csv`, `a9_logrank.csv` | Kaplan-Meier waktu sampai stunting pertama (anak pertama kali terlihat tidak stunting pada umur < 24 bulan) |

## Analisis 6 — distribusi z-score: bukti kualitas data
- **Rerata TB/U (S0)**: Puskesmas −0,98 (2024), −1,23 (2025), −0,49 (2026). Tiga desa bermasalah bergeser tidak masuk akal pada 2026: Lampeji −1,56 → **+0,01**, Mumbulsari −1,22 → **+0,13**, Lengkong −1,37 → **−0,10**. Pergeseran sekitar +1,5 SD dalam setahun tidak mungkin terjadi pada populasi nyata. Desa yang stabil: Karangkedawung −1,14/−1,27/−1,13, Kawangrejo −1,09/−1,17/−1,08, Suco −0,96/−0,97/−1,12.
- **Kekurangan anak di bawah −2 SD**: bila z-score TB/U kira-kira normal, stunting yang diharapkan dari rerata dan SD yang teramati jauh lebih tinggi daripada yang tercatat. S3, desa yang stabil: Karangkedawung 2024 diharapkan 20,5% vs tercatat 7,5%; Kawangrejo 19,4% vs 7,1%; Suco 18,1% vs 8,7%; seluruh Puskesmas 2024 17,8% vs 6,2%, 2025 26,1% vs 13,0%. Selaras dengan penumpukan tepat di atas −2 SD (rasio 5,8 pada 2024, 4,8 pada 2025, Lampeji 2025: 19,2). Ini mendukung dugaan tinggi badan dibulatkan/disesuaikan ke arah tidak stunting, tetapi belum membuktikannya (asumsi normal hanya pendekatan).
- **Pengecualian yang menarik**: Mumbulsari 2025 (tercatat 29,4% vs diharapkan 31,0%) dan Lengkong 2025 (29,3% vs 35,9%), dekat dengan harapan (heaping Lengkong 35%, Mumbulsari 75%, jadi bukan hanya soal heaping rendah). Hipotesis (perlu diverifikasi): prevalensi stunting sebenarnya di desa lain juga mungkin 20–30%, dan 6–9% adalah angka yang diperkecil.

## Analisis 7 — kurva umur
Pada 2024 (S3) rerata TB/U turun dari −0,39 (0–2 bln) ke −1,15 (30 bln) lalu mendatar sekitar −1,0, pola yang lazim (*growth faltering*). 2025 serupa tetapi lebih rendah (sampai −1,43). **2026 rusak**: rerata anak 6–11 bulan sekitar −0,07, lebih tinggi daripada bayi 0–2 bulan (−0,50). Stunting menurut umur 2024 datar 6–8% sampai 36 bulan lalu turun ke 3% pada 54–59 bulan; anak yang sudah stunting jarang pulih, jadi penurunan itu tidak lazim.

## Analisis 8 — faktor risiko: hasil yang paling tahan banting
Regresi logistik anak-bulan, disesuaikan JK, kelompok umur, dan **efek tetap desa × tahun** (membandingkan anak di desa dan tahun yang sama, sehingga artefak pencatatan per desa-tahun tersingkir), SE robust klaster per anak. Model C (BBLR dan PBLR bersama), S3: n = 90.838 pengukuran, 5.661 anak, 7.531 kasus stunting.

| Faktor | Stunting OR (CI 95%) | Underweight OR | Wasting OR |
|---|---|---|---|
| BBLR (<2.500 g) | **2,11** (1,64–2,71) | 2,30 (1,82–2,90) | 1,89 (1,50–2,37) |
| PBLR (<48 cm) | **1,47** (1,15–1,88) | 1,51 (1,19–1,91) | 1,24 (0,99–1,56; p = 0,068) |
| Perempuan (vs laki-laki) | **0,68** (0,60–0,78) | 0,71 (0,61–0,81) | 0,64 (0,56–0,74) |

Hasil hampir identik di S0 dan S1 (mis. BBLR→stunting 2,09 dan 2,11), jadi tidak bergantung pada pembuangan data bermasalah. Model BBLR saja: OR 2,45; PBLR saja: 2,03 (S3). Rentang ini sejalan dengan literatur (BBLR sekitar 2–3×). Keterbatasan: BB/TB lahir diisi petugas dan 4–9% kosong; BBLR dan PBLR berkorelasi; asosiasi, bukan kausal.

## Analisis 9 — longitudinal
- **Status berubah sangat sering antar bulan**: 5,6% (2024), 7,6% (2025) pasangan bulan berturutan berganti status stunting; **pemulihan 43% per bulan (2024), 32% (2025)** dan insiden 3,0–3,9% per bulan. Stunting tidak pulih 43% per bulan dalam kenyataan; ini kebisingan pengukuran di sekitar ambang −2 SD. Desa yang paling "tenang" tetap 17–25% pulih per bulan (Suco 2025: 18%, Kawangrejo 2026: 17%). **Insiden dan pemulihan per bulan tidak boleh ditafsirkan sebagai kejadian nyata.** Di tiga desa bermasalah 2026: insiden 0,5–1,1%, pemulihan 66–77% (data seragam).
- **Kecepatan tumbuh tinggi (S0)**: 2024 masuk akal: 2,2 cm/bulan pada 0–5 bln, 0,75 cm pada 12–23 bln, 0,5 cm pada 24–47 bln; 4,9% pasangan turun ≥ 1 cm. **2026 tiga desa bermasalah** punya SD 16–17 cm (selisih tinggi antar bulan melompat) dan 24–29% pasangan turun ≥ 1 cm, jadi tinggi badan mereka tidak bisa dipakai. Desa lain SD 1,8–2,3 cm.
- **Kaplan-Meier** (S3; 2.995 anak yang pertama kali terlihat tidak stunting pada umur < 24 bulan): S(12 bln) = 0,73 dan S(24 bln) = 0,56, yaitu 44% menjadi stunting dalam 24 bulan. Angka ini terlalu tinggi dibanding prevalensi 6–13% dan kemungkinan besar terdorong kebisingan pengukuran di sekitar −2 SD, jadi besaran absolutnya tidak dapat dipakai. **Perbandingan relatif** lebih tahan: BBLR S(12) = 0,64 vs 0,74 tanpa BBLR (log-rank p = 0,0003), laki-laki 0,68 vs perempuan 0,78 (p < 0,0001), searah dengan analisis 8.

## Implikasi
Hasil yang layak jadi inti laporan: **analisis 8** (faktor risiko BBLR, PBLR, JK, umur dengan efek tetap desa-tahun) dan perbandingan relatif di analisis 9, ditambah analisis 6, 7, 12 sebagai bukti kualitas data dan keterbatasan. Prevalensi absolut, insiden, pemulihan, dan tren 2026 untuk Lampeji/Mumbulsari/Lengkong tidak layak dilaporkan sebagai temuan.
