# Tabel hasil analisis (versi Python)

Folder ini berisi tabel CSV keluaran `skrip/analisis_tahap2.py` (analisis 1–5), `analisis_tahap2b.py` (analisis 6–9), dan `analisis_tahap2c.py` (analisis tambahan P1–P3). Semuanya agregat. Tabel dihitung dari `anak_bersih.csv` (lokal) dan `data/sigizi/rekap_tambahan/sasaran_cakupan_cek2024.xlsx`. Definisi flag dan skenario S0–S3 ada di [`../README.md`](../README.md). Tabel versi R dan SPSS memakai nama dan kolom yang sama (lihat [`../../analisis_r/README.md`](../../analisis_r/README.md) dan [`../../analisis_spss/README.md`](../../analisis_spss/README.md)).

Skrip menjalankan pemeriksaan silang saat berjalan: kasus per desa-tahun harus sama dengan jumlah kasus per bulan di `desa_bulan.csv`, jumlah anak pada analisis 5 harus sama dengan analisis 1, dan jumlah sasaran serta anak terukur harus cocok dengan sheet Cakupan (selisihnya paling banyak 8 anak yang tidak punya desa).

## Metode yang berlaku di semua tabel

**Titik estimasi.** Prevalensi dihitung dari seluruh pengukuran anak-bulan yang dikumpulkan, sama seperti situs SigiziKesga dan Laporan Puskesmas. Outcome biner diambil dari label situs, dan pengukuran berkategori "Outlier" dikeluarkan dari penyebut.

**Interval kepercayaan.** Untuk prevalensi per desa dan tahun dipakai bootstrap klaster per anak (500 ulangan, seed 20261019), karena anak yang sama diukur berulang dan barisnya tidak saling bebas. Untuk prevalensi bulanan dipakai interval Wilson, karena dalam satu bulan setiap anak hanya muncul sekali.

**Uji hipotesis.** Perbandingan antar desa, jenis kelamin, dan umur memakai chi-kuadrat pada satu pengukuran acak per anak per tahun (seed tetap), supaya sampelnya saling bebas. Pengukuran "pertama" tidak dipakai karena Januari sering bermasalah.

**Tren.** Deret bulanan (33 titik) diuji dengan Mann-Kendall dan kemiringan Sen. Regresi segmented memakai OLS dengan titik patah pada Januari 2026 dan galat baku Newey-West (lag 3); parameter `lompatan_2026-01_pp` adalah lompatan level pada Januari 2026 dalam poin persen.

**Regresi logistik.** Ditulis sendiri dengan metode IRLS dan galat baku robust klaster per anak, karena `statsmodels` tidak tersedia di komputer ARM64 yang dipakai. Ada uji internal yang mereproduksi odds ratio dari tabel 2×2 dan galat baku Woolf. Pemeriksaan lain: jumlah pasangan pengukuran tidak boleh melebihi jumlah baris, dan kurva Kaplan-Meier harus menurun monoton.

## Analisis 1–5: prevalensi, tren, antar desa, cakupan, umur dan jenis kelamin

| Berkas | Isi dan kolom utama |
|---|---|
| `a1_prevalensi_desa_tahun.csv` | Prevalensi stunting, wasting, underweight, dan gizi lebih per skenario, desa (ditambah `SEMUA` untuk seluruh Puskesmas), dan tahun. Kolom: `n_anak`, `n_valid` (pengukuran yang masuk penyebut), `kasus`, `pct`, `ci_low`, `ci_high`. |
| `a1_prevalensi_bulan.csv` | Prevalensi bulanan gabungan semua desa per skenario, dengan interval Wilson. |
| `a2_seri_bulanan.csv` | Deret bulanan per desa dan outcome: `t` (indeks bulan, 0 = Januari 2024), `n_valid`, `pct`. |
| `a2_tren_mannkendall.csv` | Hasil Mann-Kendall (`tau`, `p_mk`) dan kemiringan Sen dalam poin persen per bulan dan per tahun, dengan interval kepercayaannya. |
| `a2_tren_segmented.csv` | Parameter regresi segmented (`parameter`, `est`, `se_nw`, `p`). |
| `a3_antar_desa.csv` | Prevalensi per desa dalam satu tahun, residual terstandar (`resid_std`, nilai di luar ±2 menandai desa yang menyimpang), serta statistik chi-kuadrat antar tujuh desa (`chi2`, `df`, `p_chi2`). |
| `a4_cakupan_bulan.csv`, `a4_cakupan_desa_bulan.csv` | Anak terukur dibagi sasaran (`cakupan_pct`). Sasaran hanya tersedia Januari 2025 sampai September 2026, jadi 2024 tidak punya penyebut. |
| `a5_umur_jk.csv` | Prevalensi menurut kelompok umur dan jenis kelamin (skenario S0 dan S1). |
| `a5_uji_jk_umur.csv` | Uji chi-kuadrat untuk jenis kelamin dan kelompok umur terhadap tiap outcome. |

## Analisis 6–9: distribusi z-score, kurva umur, faktor risiko, longitudinal

| Berkas | Isi dan kolom utama |
|---|---|
| `a6_zscore_ringkas.csv` | Ringkasan z-score per desa dan tahun (S0 dan S3): rerata dengan interval, SD, kemencengan, persentil, persentase di bawah −2 SD, dan `rasio_tumpuk`, yaitu rasio jumlah anak di rentang −2,0 sampai −1,9 SD terhadap −2,1 sampai −2,0 SD (nilai sekitar 1 wajar). |
| `a6_zscore_histogram_tbu_s0.csv` | Histogram z-score TB/U per desa dan tahun (`bin_awal`, `n`). |
| `a6_zscore_bulanan_s0.csv` | Rerata dan SD z-score per desa dan bulan. |
| `a7_kurva_umur.csv` | Rerata z-score dan prevalensi per kelompok umur 3 bulan dan tahun, dengan interval. |
| `a8_faktor_risiko.csv` | Odds ratio (`OR`, `ci_low`, `ci_high`, `p`) untuk BBLR, PBLR, jenis kelamin, dan umur terhadap stunting, wasting, dan underweight. Model A hanya berisi BBLR, model B hanya PBLR, model C keduanya. Semua model disesuaikan dengan jenis kelamin, kelompok umur, dan efek tetap desa × tahun, dan tersedia untuk S0, S1, dan S3. |
| `a9_transisi_status.csv` | Insiden, pemulihan, dan perubahan status stunting antara dua bulan berurutan pada anak yang terukur di keduanya. |
| `a9_kecepatan_tumbuh.csv` | Selisih tinggi badan antara dua bulan berurutan (cm per bulan) menurut desa, tahun, dan umur, termasuk persentase pasangan yang tinggi badannya turun 1 cm atau lebih. |
| `a9_km_stunting.csv`, `a9_logrank.csv` | Kaplan-Meier dan log-rank untuk waktu hingga stunting pertama, pada anak yang pertama kali terlihat tidak stunting di umur kurang dari 24 bulan. |

Catatan tentang tabel `a8`: pada model dengan efek tetap desa × tahun, anak hanya dibandingkan dengan anak lain di desa dan tahun yang sama, sehingga artefak pencatatan yang seragam dalam satu desa-tahun tidak ikut terbaca sebagai faktor risiko. BBLR dan PBLR diisi oleh petugas dan sebagian kosong, dan keduanya saling berkorelasi, itulah alasan model A, B, dan C disediakan terpisah.

## Analisis tambahan P1–P3

Dijalankan dengan `python -I skrip/analisis_tahap2c.py <anak_bersih.csv> data/sigizi/analisis/tabel/who_lhfa_lms.csv data/sigizi/analisis/tabel`. Definisi lama Kaplan-Meier direproduksi lebih dulu sebagai pemeriksaan: pada S3 harus menghasilkan 2.995 anak, 1.152 kejadian, S(12 bulan) = 0,7304, dan log-rank BBLR χ² = 13,17.

| Berkas | Isi dan kolom utama |
|---|---|
| `who_lhfa_lms.csv` | Tabel LMS TB/U standar WHO 2006 (umur 0–1.826 hari, L = 1), diekspor dari paket R `anthro` 1.1.0 (`anthro:::growthstandards_lenanthro`). Ini data acuan publik. |
| `p1_km_konfirmasi.csv` | Kaplan-Meier (S0 dan S3) dengan dua definisi kejadian: satu pengukuran di bawah −2 SD, atau terkonfirmasi (dua pengukuran berurutan di bawah −2 SD dengan jarak paling lama 3 bulan). Berisi nilai survival pada 12 dan 24 bulan sejak masuk, dan pada umur 24 dan 36 bulan (skala umur dengan delayed entry). |
| `p1_logrank.csv` | Log-rank untuk BBLR dan jenis kelamin pada beberapa skala waktu dan strata: tanpa strata, strata desa, dan strata desa × umur masuk. |
| `p2_bulan_terukur.csv` | Jumlah bulan terukur per anak: persentase anak yang terukur minimal 12 dan 24 bulan, median, kuartil, dan maksimum. |
| `p3_tumpuk_digit.csv` | Rasio penumpukan z-score di sekitar −2 SD menurut digit desimal tinggi badan (.0 atau .5 dibanding digit lain). |
| `p3_simulasi_pembulatan.csv` | Simulasi: z-score halus dari N(rerata, SD desa-tahun) diubah menjadi tinggi dengan parameter LMS, dibulatkan dengan lima cara (tanpa pembulatan, ke 0,5 cm, ke 1 cm, ke bawah 1 cm, ke atas 1 cm), lalu z-score dihitung ulang. 20 ulangan, seed 20261019. Dipakai untuk menguji apakah pembulatan saja bisa menimbulkan penumpukan di atas −2 SD. |
| `p3_validasi_lms.csv` | Kecocokan z-score yang dihitung dari tinggi tercatat dan LMS WHO dengan z-score yang ditampilkan situs. |
