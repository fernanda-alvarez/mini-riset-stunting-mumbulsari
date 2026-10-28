# Hasil analisis di SPSS

Folder ini berisi tabel hasil analisis yang dikerjakan di SPSS 27 pada 26 Oktober 2026. Sintaksnya ada di `skrip/spss/analisis_spss.sps`, dan dijalankan tanpa antarmuka oleh `skrip/spss/jalankan_spss.py`. Hasilnya adalah padanan analisis 3, 4, 5 (uji), dan P2 pada versi Python (`analisis_tahap2.py` dan `analisis_tahap2c.py`). Analisis lainnya dikerjakan di R (`skrip/analisis_r_*.R`).

| Berkas | Isi |
|---|---|
| `a3_antar_desa.csv` | Jumlah anak, kasus, persen, interval Wilson, residual terstandar, dan chi-kuadrat antar desa (perintah `CROSSTABS`). |
| `a4_cakupan_desa_bulan.csv`, `a4_cakupan_bulan.csv` | Anak terukur dibagi sasaran, per desa dan bulan, dan per bulan untuk seluruh Puskesmas. |
| `a5_uji_jk_umur.csv` | Chi-kuadrat untuk jenis kelamin (tabel 2×2 dengan koreksi kontinuitas) dan kelompok umur. |
| `p2_bulan_terukur.csv` | Jumlah bulan terukur per anak. |
| `perbandingan_dengan_python.txt` | Selisih terhadap tabel Python di `data/sigizi/analisis/tabel/`. |
| `tmp/` | Berkas perantara dari fitur OMS SPSS. Boleh dihapus, dan tidak ikut repo. |

## Hasil perbandingan dengan Python

Semua kolom pada `a3`, `a4`, `a5`, dan `p2` sama dengan hasil Python (selisih 0). Syarat agar sama persis: sampel "satu pengukuran acak per anak per tahun" dipilih di Python (`siapkan_data_spss_r.py`, kolom `pa_s0` sampai `pa_s3`) dan dibaca SPSS apa adanya. SPSS tidak mengundi sendiri.

## Catatan teknis

- Untuk tabel 2×2 (jenis kelamin, dan antar desa yang hanya berisi dua desa seperti S2 tahun 2025), nilai yang dipakai adalah baris "Continuity Correction". Itu sama dengan `scipy.stats.chi2_contingency` di Python. Chi-kuadrat Pearson tanpa koreksi menghasilkan angka yang lebih besar.
- Persentil p25 dan p75 pada `p2` memakai definisi SPSS. Pada data ini hasilnya sama dengan numpy.
- SPSS 27 gagal membaca berkas xlsx sasaran (pesan "All sheets appear to be empty"). Karena itu sheet `Sasaran` diekspor menjadi `sasaran.csv` oleh `siapkan_data_spss_r.py`.
- Cara menjalankan lewat antarmuka SPSS: buka `File > Open > Syntax`, atur `CD` ke folder induk proyek, lalu `Run > All`. Jalur di dalam sintaks relatif terhadap folder induk itu.
