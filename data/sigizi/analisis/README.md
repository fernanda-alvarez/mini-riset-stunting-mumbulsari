# Hasil cleaning (Tahap 1) — dataset analisis

Dibuat 19 Okt 2026 oleh `skrip/bersihkan_data_anak.py`. Sumber: 33 berkas `Daftar_Status_Gizi_2024-01..2026-09` (Okt 2026 dibuang). Rencana: `../RENCANA_ANALISIS.md`.

## Berkas
| Berkas | Isi | Di git |
|---|---|---|
| `desa_bulan.csv` | 7 desa × 33 bulan × 4 skenario (741 baris): n, jumlah dan persen stunting/wasting/underweight, kolom kualitas | ya (agregat) |
| `log_cleaning.txt` | jumlah baris kena tiap flag per tahun, baris per skenario, desa-bulan anomali, heaping per desa-tahun | ya |
| `data/sumber/anak_bersih/anak_bersih.csv` | dataset anak-bulan (108.322 baris, 6.312 anak) dengan ID acak | **tidak** (gitignore, di laptop saja) |
| `data/sumber/anak_bersih/.garam` | garam HMAC untuk ID acak; hilang = ID tidak bisa direproduksi, jangan dibagikan | **tidak** |

`anak_bersih.csv` tanpa NIK, nama, nama orang tua, alamat, RT/RW, tanggal lahir (diganti `umur_bln`). Kolom: id_anak, bulan_berkas, tahun, bulan, desa, posyandu, jk, tgl_ukur, umur_bln, bb_lahir_g, tb_lahir_cm, bblr, pblr, berat, tinggi, lila, cara_ukur, zs_*, kat_*, naik_bb, vit_a, mbg, outcome biner (stunting, stunting_berat, wasting, wasting_berat, underweight, gizi_lebih; label Outlier → kosong), dan semua flag `f_*`.

## Validasi
Stunting, wasting, dan underweight yang dihitung dari data per anak (semua baris, sebelum flag) **sama persis** dengan sheet "Laporan Puskesmas" pada 147 dari 147 desa-bulan yang bisa dibandingkan (Jan 2025–Sep 2026; jumlah stunting 6.754, wasting 5.192, underweight 8.454). Definisi outcome sudah mereproduksi angka situs. ID anak konsisten sebagai kunci: tidak ada ID dengan lebih dari satu JK atau tanggal lahir.

## Flag
**Keras** (baris keluar dari semua skenario; gabungan `f_keras`: 241 baris 2024, 945 baris 2025, 1.534 baris 2026): `f_zs_penanda` (|ZS| ≥ 999), `f_nol` (tinggi/berat 0), `f_aneh` (berat > 40 atau tinggi > 130), `f_nik_ganda`, `f_umur_luar` (umur di luar 0–<60 bulan).

**Lunak**: `f_anomali_desabulan` (TB/U Outlier ≥ 10% atau stunting ≥ 50% dalam desa-bulan; dasar normal 0,3–3% dan 4–17%) dipakai di S3; `f_heaping_tinggi` (digit desimal tinggi .0/.5 ≥ 70% per desa-tahun, diharapkan ±20%) dipakai di S2; sisanya informasi: `f_tgl_seragam` (satu tanggal ukur memuat ≥ 30% baris desa-bulan), `f_tbu_outlier`, `f_cara_ukur_salah` (umur < 24 bulan berdiri atau ≥ 24 bulan terlentang; Cara Ukur "-" tidak dinilai), `f_tgl_luar`, `f_pos_kosong`, `f_nik_pendek` (NIK bukan 16 digit; 42% baris, tetapi konsisten sebagai kunci).

## Skenario
- **S0**: semua baris tanpa flag keras dan dengan desa terisi.
- **S1**: S0 tanpa Lampeji, Mumbulsari, Lengkong untuk 2026-01..2026-09 (Sep ditambahkan 19 Okt 2026 karena berpola sama).
- **S2**: S0 hanya desa-tahun dengan heaping rendah (< 70%).
- **S3**: S0 tanpa desa-bulan anomali (15 desa-bulan, antara lain Lampeji/Mumbulsari/Lengkong 2026-06 dan 2026-07).

Persen stunting menurut skenario (dari `desa_bulan.csv`, gabungan semua desa):

| Skenario | 2024 | 2025 | 2026 |
|---|---|---|---|
| S0 | 6,5% | 13,1% | 7,0% |
| S1 | 6,5% | 13,1% | 12,4% |
| S2 | 6,1% | 20,6% | 1,8% |
| S3 | 6,2% | 13,0% | 7,1% |

Angka antar skenario berbeda jauh. S2 dan S1 mengubah komposisi desa (bukan hanya membuang data buruk), jadi bandingkan per desa, bukan gabungan.

## Temuan baru saat cleaning
- **Di Lampeji, Mumbulsari, Lengkong pada 2026, hampir semua anak dalam satu desa-bulan bertanggal ukur sama** pada Jan dan Apr–Sep (30 Jan, 23 Apr, 22 Mei, 30 Jun, 31 Jul, 28 Ags, 28 Sep; 83–100% baris; Feb sebagian, Mar tidak). Stunting pada bulan-bulan itu hanya 0–3%, kecuali **Juli 2026 = 84–87% stunting dengan 89–94% TB/U Outlier** (entri massal yang sudah diketahui). Jadi bukan hanya Juli yang janggal: pola satu-tanggal-per-bulan dengan stunting ±1% berlangsung Jan–Sep 2026, sedangkan S1 hanya membuang Jan–Agu. **Sep 2026 di tiga desa itu berpola sama dan tetap masuk S1.**
- **Pola satu-tanggal juga ada di 2024 untuk Lengkong dan Mumbulsari** (stunting 14% dan 4%). Tanggal ukur di desa-desa itu mungkin tanggal entri, bukan tanggal pengukuran sebenarnya.
- Tamansari 2026 punya tanggal seragam hanya dari Jun 2026.

## Belum dilakukan
- Hitung ulang z-score WHO (opsional; label situs sudah konsisten dengan z-score).
- Paket `statsmodels` tidak bisa dipasang di laptop ini (Windows ARM64, tidak ada wheel, build butuh Visual Studio). Terpasang: `pandas`, `scipy`, `matplotlib`. Regresi logistik dan GEE untuk analisis 8–9 perlu ditulis dengan `scipy` (standard error robust per anak dihitung manual).
