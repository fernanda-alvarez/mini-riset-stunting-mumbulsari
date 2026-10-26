# Hasil analisis di R

Dijalankan 26 Okt 2026 dengan R 4.6.1 (hanya base R; semua metode ditulis ulang agar sama dengan Python). Skrip: `skrip/analisis_r_1.R` (a1, a2, a5 tabel, a6, a7), `analisis_r_2.R` (a8, a9), `analisis_r_3.R` (p1, p3); fungsi bersama di `skrip/r_umum.R`.

Berkas keluaran memakai nama dan kolom yang sama dengan `data/sigizi/analisis/tabel/`. Hasil perbandingan lengkap: `perbandingan_dengan_python.txt` (dibuat `skrip/bandingkan_hasil.R`).

**Yang sama persis dengan Python (selisih 0):** semua n, kasus, persen, CI Wilson (a1 bulanan), Mann-Kendall (tau, p), Sen (kemiringan dan CI), regresi segmented Newey-West, ringkasan z-score, kurva umur (rerata), regresi logistik klaster a8 (OR, CI, p), Kaplan-Meier dan log-rank a9, P1 (termasuk verifikasi kohort 2.995 anak, 1.152 kejadian, S(12) 0,7304, log-rank BBLR 13,17), tumpukan digit P3 dan validasi LMS. Satu pengecualian pembulatan: `p5` di `a6_zscore_ringkas` berbeda 0,01 pada satu baris.

**Yang berbeda sedikit karena RNG R tidak sama dengan numpy (B = 500, seed 20261019):**
- batas CI bootstrap klaster (a1 desa-tahun, a5, a6, a7, a9 transisi). Selisih rerata 0,1–0,2 poin persen; terbesar pada kelompok kecil (a9 transisi sampai 6 poin).
- simulasi pembulatan P3 (20 ulangan): rasio rerata berbeda ≤ 0,04, persen < -2 SD ≤ 0,18.
Titik estimasi, n, dan kasus tidak terpengaruh. Kalau angka CI di laporan perlu persis seperti Python, tetap pakai tabel Python; bila dipindah ke R, ganti angka CI di teks.

Prasyarat: `data/sumber/anak_analisis/anak_analisis.csv` dari `skrip/siapkan_data_spss_r.py` (Python, gitignored). Cleaning dan flag skenario S0–S3 tetap di Python (`bersihkan_data_anak.py`).
