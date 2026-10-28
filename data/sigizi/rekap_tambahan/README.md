# Rekap tambahan SigiziKesga (agregat), diambil 19 Okt 2026

Semua agregat per desa, tanpa identitas anak. Diambil berurutan lewat POST form laporan (lihat `../daftar_status_gizi/README.md` untuk cara kerja server), Puskesmas Mumbulsari, usia 0–59 bulan, semua desa (`kel` kosong).

| Berkas | Isi |
|---|---|
| `rekap_tambahan_2026-10-19.json` | Tabel mentah apa adanya (baris = array sel; `{cN}` = colspan N). Kunci: `sasaran`, `usia`, `usiajk` (masing-masing 22 bulan, 2025-01..2026-10) dan `cek2024` (Rekap Status Gizi tingkat Puskesmas, 2023-12 dan 2024-01..12). |
| `sasaran_cakupan_cek2024.xlsx` | Sheet `Sasaran` (per desa, per bulan, L/P/total), `Cakupan` (terukur / sasaran per bulan), `Cek 2024`. Dibuat oleh `skrip/bangun_sasaran_cakupan.py`. |

## Laporan

- **Rekap Sasaran Anak per Desa** (`Laporan/rkp_sasaran_balita_desa.html`): jumlah anak sasaran per desa menurut jenis kelamin. Penyebut untuk cakupan; tidak bisa diturunkan dari data per anak karena anak terdaftar yang tidak terukur tidak muncul di sana.
- **Rekap Status Gizi & Usia** (`.../rkp_status_gizi_balita_usia.html`, kunci `usia`): per desa, BB/U (4 kategori), TB/U (4), BB/TB (6) untuk dua kelompok umur, 0–23 dan 0–59 bulan (tanpa kolom Outlier). **Total 0–59 bulan cocok persis dengan sheet `Laporan Puskesmas` pada 22 dari 22 bulan** (pembanding resmi).
- **Rekap Status Gizi, Usia, & Jenis Kelamin** (`.../rkp_status_gizi_balita_usia_kelamin.html`, kunci `usiajk`): seperti di atas dengan 5/5/7 kategori (termasuk Outlier), tiap sel dipecah umur (0–23, 0–59) lalu laki-laki dan perempuan. Diuji pada satu bulan (Agu 2025): 0–59 bulan laki-laki + perempuan = angka laporan `usia`.

Susunan baris: dua sampai tiga baris header (kelompok indikator, kategori, kelompok umur, L/P), baris per desa, baris `JUMLAH`.

## Temuan

- **Cakupan** (terukur / sasaran, Laporan Puskesmas): 55–72% sepanjang 2025 (Jan 72%, Jun 55%), lalu **95% pada Jan–Jun 2026** dan 92% Jul–Sep. Sasaran sendiri hampir datar dan turun pelan (4.678 pada Jan 2025 menjadi 4.347 pada Sep 2026), jadi lonjakan jumlah anak terukur pada Jan 2026 **bukan karena registrasi baru**, melainkan perubahan cara pencatatan (dugaan; belum dikonfirmasi petugas entri). Akibatnya cakupan dan prevalensi 2025 vs 2026 tidak sebanding. Okt 2026 belum final (19 anak terukur).
- **Data 2024 ada**: 2.741–3.216 anak per bulan pada Jan–Des 2024 (setara 2025: 2.555–3.355). Des 2023 hanya 269 anak (awal pencatatan atau sisa), jadi riwayat efektif mulai Jan 2024. Kelengkapan per anak (posyandu kosong, entri massal, dll.) pada 2024 belum diperiksa karena data per anak 2024 belum diunduh.
