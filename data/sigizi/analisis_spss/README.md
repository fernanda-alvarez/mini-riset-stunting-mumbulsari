# Hasil analisis di SPSS

Dijalankan 26 Okt 2026 dengan SPSS 27 lewat `skrip/spss/analisis_spss.sps` (dipanggil oleh `skrip/spss/jalankan_spss.py`, tanpa antarmuka). Padanan analisis_tahap2.py (a3, a4, a5 uji) dan analisis_tahap2c.py (p2).

| Berkas | Isi |
|---|---|
| `a3_antar_desa.csv` | n, kasus, persen, CI Wilson, residual terstandar, chi-kuadrat antar desa (CROSSTABS) |
| `a4_cakupan_desa_bulan.csv`, `a4_cakupan_bulan.csv` | terukur dibanding sasaran |
| `a5_uji_jk_umur.csv` | chi-kuadrat JK (2×2, dengan koreksi kontinuitas) dan kelompok umur |
| `p2_bulan_terukur.csv` | jumlah bulan terukur per anak |
| `perbandingan_dengan_python.txt` | selisih terhadap `data/sigizi/analisis/tabel/` |
| `tmp/` | berkas perantara OMS (boleh dihapus) |

**Hasil perbandingan:** semua kolom a3, a4, a5, dan p2 sama dengan hasil Python (selisih 0). Syarat sama persisnya: sampel "satu pengukuran acak per anak per tahun" dipilih di Python (`siapkan_data_spss_r.py`, kolom `pa_s0..pa_s3`) dan dibaca SPSS apa adanya, jadi SPSS tidak mengundi sendiri.

Catatan:
- Tabel 2×2 (jk, dan a3 dengan hanya dua desa, mis. S2 2025) memakai baris "Continuity Correction", sama dengan `scipy.stats.chi2_contingency`. Pearson tanpa koreksi akan memberi angka lebih besar.
- Persentil p25/p75 p2 memakai definisi SPSS; di data ini sama dengan numpy.
- SPSS 27 gagal membaca xlsx sasaran ("All sheets appear to be empty"), jadi sheet `Sasaran` diekspor ke `data/sumber/anak_analisis/sasaran.csv` oleh `siapkan_data_spss_r.py`.
- Menjalankan lewat antarmuka: `File > Open > Syntax`, atur `CD` ke folder induk proyek, `Run > All`.
