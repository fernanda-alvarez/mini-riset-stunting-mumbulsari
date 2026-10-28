# Rekap tambahan SigiziKesga (agregat)

Folder ini berisi rekap tambahan yang diambil dari SigiziKesga pada 19 Oktober 2026. Semuanya agregat per desa tanpa identitas anak, untuk Puskesmas Mumbulsari, usia 0–59 bulan, dan semua desa (filter `kel` dikosongkan).

| Berkas | Isi |
|---|---|
| `rekap_tambahan_2026-10-19.json` | Tabel mentah apa adanya (satu baris adalah larik sel, dan `{cN}` menandai colspan N). Kunci: `sasaran`, `usia`, dan `usiajk` (masing-masing 22 bulan, Januari 2025 sampai Oktober 2026), serta `cek2024` (Rekap Status Gizi tingkat Puskesmas untuk Desember 2023 dan Januari sampai Desember 2024). |
| `sasaran_cakupan_cek2024.xlsx` | Sheet `Sasaran` (per desa dan bulan, laki-laki, perempuan, dan total), `Cakupan` (anak terukur dibagi sasaran per bulan), dan `Cek 2024`. Dibuat oleh `skrip/bangun_sasaran_cakupan.py`. |

## Laporan yang menjadi sumber

- **Rekap Sasaran Anak per Desa** (`rkp_sasaran_balita_desa`): jumlah anak sasaran per desa menurut jenis kelamin. Ini penyebut untuk cakupan. Penyebut ini tidak bisa diturunkan dari data per anak, karena anak terdaftar yang tidak terukur tidak muncul di sana.
- **Rekap Status Gizi dan Usia** (`rkp_status_gizi_balita_usia`, kunci `usia`): per desa, BB/U (4 kategori), TB/U (4 kategori), dan BB/TB (6 kategori) untuk dua kelompok umur, 0–23 dan 0–59 bulan, tanpa kolom Outlier. Total 0–59 bulan cocok persis dengan sheet `Laporan Puskesmas` pada seluruh 22 bulan, yang menjadi pembanding resmi.
- **Rekap Status Gizi, Usia, dan Jenis Kelamin** (`rkp_status_gizi_balita_usia_kelamin`, kunci `usiajk`): seperti di atas dengan 5, 5, dan 7 kategori (termasuk Outlier). Setiap sel dipecah menurut umur (0–23 dan 0–59 bulan) lalu laki-laki dan perempuan. Pemeriksaan pada satu bulan (Agustus 2025) menunjukkan jumlah laki-laki dan perempuan 0–59 bulan sama dengan angka pada laporan `usia`.

Susunan tabel pada tiap laporan: dua sampai tiga baris header (kelompok indikator, kategori, kelompok umur, dan L/P), satu baris per desa, dan baris `JUMLAH`.

## Catatan

- Sasaran hanya tersedia untuk Januari 2025 sampai September 2026. Cakupan 2024 tidak bisa dihitung karena tidak ada penyebut.
- Data 2024 pada `cek2024` memuat rekap tingkat Puskesmas, dan dipakai untuk memeriksa total data per anak 2024. Desember 2023 hanya berisi 269 anak, jadi riwayat efektif dimulai Januari 2024.
- Oktober 2026 belum final dan tidak dianalisis.
