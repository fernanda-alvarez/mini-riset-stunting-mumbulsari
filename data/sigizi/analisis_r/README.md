# Hasil analisis di R

Folder ini berisi tabel hasil analisis versi R, dijalankan pada 26 Oktober 2026 dengan R 4.6.1. Semua metode ditulis ulang dengan base R tanpa paket tambahan, dan dibuat sama dengan versi Python supaya hasil kedua perangkat lunak bisa dibandingkan.

Skrip yang menghasilkan folder ini:
- `skrip/analisis_r_1.R`: analisis 1, 2, tabel 5, 6, dan 7.
- `skrip/analisis_r_2.R`: analisis 8 (faktor risiko) dan 9 (longitudinal).
- `skrip/analisis_r_3.R`: analisis tambahan P1 dan P3.
- `skrip/r_umum.R`: fungsi yang dipakai bersama.

Berkas keluarannya memakai nama dan kolom yang sama dengan tabel Python di `data/sigizi/analisis/tabel/` (penjelasan kolom ada di [README tabel](../analisis/tabel/README.md)). Hasil perbandingan lengkap dengan versi Python ada di `perbandingan_dengan_python.txt`, yang dibuat oleh `skrip/bandingkan_hasil.R`.

## Hasil perbandingan dengan Python

**Sama persis (selisih 0)**: semua jumlah anak, jumlah kasus, dan persentase; interval Wilson pada prevalensi bulanan; Mann-Kendall (tau dan p); kemiringan Sen beserta interval kepercayaannya; regresi segmented dengan galat baku Newey-West; ringkasan z-score; rerata pada kurva umur; regresi logistik klaster pada analisis 8 (OR, interval, dan p); Kaplan-Meier dan log-rank pada analisis 9; P1 (termasuk verifikasi kohort: 2.995 anak, 1.152 kejadian, S(12 bulan) = 0,7304, log-rank BBLR 13,17); penumpukan digit dan validasi LMS pada P3. Satu pengecualian karena pembulatan: kolom `p5` di `a6_zscore_ringkas` berbeda 0,01 pada satu baris.

**Berbeda sedikit** karena generator angka acak R tidak sama dengan numpy (B = 500, seed 20261019):
- Batas interval bootstrap klaster pada analisis 1 (desa-tahun), 5, 6, 7, dan transisi status di analisis 9. Selisih rata-ratanya 0,1–0,2 poin persen, dan terbesar pada kelompok kecil (sampai 6 poin pada transisi status).
- Simulasi pembulatan P3 (20 ulangan): rasio rerata berbeda paling banyak 0,04 dan persentase di bawah −2 SD paling banyak 0,18.

Titik estimasi, jumlah anak, dan jumlah kasus tidak terpengaruh oleh perbedaan ini. Jika angka interval kepercayaan pada laporan harus persis seperti hasil Python, pakai tabel Python. Jika dipindahkan ke R, angka interval di teks laporan perlu diganti.

## Prasyarat

Skrip R membaca `data/sumber/anak_analisis/anak_analisis.csv`, yang dibuat oleh `skrip/siapkan_data_spss_r.py` dan tidak ada di repo. Pembersihan data dan penandaan skenario S0–S3 tetap dikerjakan di Python (`bersihkan_data_anak.py`).
