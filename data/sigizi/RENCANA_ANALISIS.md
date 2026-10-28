# Rencana analisis data SigiziKesga

Dokumen ini memuat keputusan dasar, tahap pembersihan data, dan daftar analisis yang dikerjakan pada data SigiziKesga Puskesmas Mumbulsari. Rencana disusun pada 19 Oktober 2026 sebelum analisis dijalankan. Sumber data dan kualitasnya dijelaskan di [`daftar_status_gizi/README.md`](daftar_status_gizi/README.md), [`rekap_status_gizi/README.md`](rekap_status_gizi/README.md), dan [`rekap_tambahan/README.md`](rekap_tambahan/README.md).

## Tahap 0: keputusan dasar

- **Periode.** Januari 2024 sampai September 2026. Oktober 2026 tidak dipakai karena bulannya masih berjalan dan datanya belum final.
- **Dua unit analisis.** Desa-bulan (7 desa × 33 bulan) dan anak-bulan (sekitar 108 ribu pengukuran dari sekitar 6.300 anak).
- **Data bermasalah ditandai (flag) dan tidak dihapus**, lalu dampaknya diuji lewat empat skenario sensitivitas:
  - **S0**: semua baris tanpa flag keras dan dengan desa terisi.
  - **S1**: S0 tanpa Lampeji, Mumbulsari, dan Lengkong untuk Januari sampai September 2026.
  - **S2**: S0 hanya pada desa-tahun dengan penumpukan digit tinggi badan rendah (kurang dari 70%).
  - **S3**: S0 tanpa desa-bulan anomali.

## Tahap 1: pembersihan data

Dikerjakan oleh `skrip/bersihkan_data_anak.py`. Definisi flag dan skenario yang dipakai ada di [`analisis/README.md`](analisis/README.md). Langkah-langkahnya:

1. NIK diganti ID acak. Kolom nama, nama orang tua, alamat, dan RT/RW dibuang, begitu juga kolom yang hampir kosong (KPSP, KIA, Kelas Ibu).
2. Berat lahir (dalam kg) diubah ke gram, lalu diturunkan BBLR (berat lahir di bawah 2.500 g) dan PBLR (panjang lahir di bawah 48 cm). Umur dihitung ulang dari tanggal lahir dan tanggal ukur.
3. Setiap aturan kualitas menjadi satu kolom flag: z-score penanda, tinggi atau berat nol, berat di atas 40 kg, tinggi di atas 130 cm, tanggal ukur di luar bulan berkas, desa atau posyandu kosong, NIK ganda dalam satu bulan, tanggal ukur yang seragam, TB/U outlier, cara ukur yang tidak sesuai umur, dan penumpukan digit tinggi badan per desa-tahun. Pada pelaksanaan, "entri massal" dipecah menjadi `f_tgl_seragam` (informasi) dan `f_anomali_desabulan` (dipakai di S3).
4. Keluarannya: dataset anak-bulan, tabel desa-bulan (persen stunting, wasting, underweight, cakupan, dan kolom kualitas), dan log jumlah baris yang terkena tiap flag.

Perhitungan ulang z-score WHO bersifat opsional dan tidak dikerjakan di tahap ini, karena label situs sudah konsisten dengan z-score.

## Tahap 2: analisis

| # | Analisis | Metode | Catatan |
|---|---|---|---|
| 1 | Prevalensi stunting, wasting, dan underweight | Persentase dengan interval kepercayaan, per desa dan bulan | Dibaca bersama masalah penumpukan digit |
| 2 | Tren 2024 sampai 2026 | Mann-Kendall dan kemiringan Sen, regresi segmented | Dibaca bersama perubahan cakupan |
| 3 | Perbedaan antar desa | Chi-kuadrat dan residual terstandar | |
| 4 | Cakupan (terukur dibagi sasaran) | Deskriptif dan tren | Sasaran tersedia sejak Januari 2025 |
| 5 | Status gizi menurut umur dan jenis kelamin | Tabel silang dan chi-kuadrat | |
| 6 | Distribusi z-score | Rerata, SD, histogram per tahun | Sebagai pemeriksaan kualitas data |
| 7 | Prevalensi menurut kelompok umur dan jenis kelamin | Tabel dan kurva umur | |
| 8 | Faktor risiko (BBLR, PBLR, jenis kelamin, umur) | Regresi logistik dengan galat baku robust klaster per anak | MBG, KPSP, KIA, dan Kelas Ibu tidak dianalisis karena hampir kosong atau tidak konsisten |
| 9 | Longitudinal | Insiden dan pemulihan stunting, Kaplan-Meier, kecepatan tumbuh | Memanfaatkan pengukuran berulang |
| 10 | MBG | Deskriptif saja | Terlalu sedikit pengukuran berstatus "ya" untuk inferensi |
| 11 | Profil per desa | Tingkat desa (7 titik) | Tanpa peta, dan posyandu tidak dipakai |
| 12 | Kualitas data | Penumpukan digit, penumpukan z-score, tanggal ukur seragam | Masuk ke metode dan keterbatasan |

Analisis tambahan P1 (Kaplan-Meier dengan kejadian terkonfirmasi), P2 (jumlah bulan terukur per anak), dan P3 (penumpukan digit dan simulasi pembulatan) dikerjakan kemudian saat telaah laporan. Prioritas analisis: tren dan perbandingan desa (1–5) sebagai utama, faktor risiko dan longitudinal (7–9) sebagai sekunder.

## Tahap 3: workbook Excel

Satu workbook, `analisis/Analisis_Stunting_Mumbulsari.xlsx`, dibuat dengan openpyxl. Isinya ringkasan, kamus, satu sheet per analisis (tabel dan grafik Excel), data desa-bulan, dan kualitas data. Tampilannya memakai header berwarna, panel yang dibekukan, filter, format angka dan persen, lebar kolom otomatis, color scale, dan setelan cetak.

## Tahap 4: urutan kerja

Pembersihan data, dataset desa-bulan, analisis 1–5, lalu 6–9, lalu 10–12, dan terakhir workbook. Setiap tahap diakhiri dengan commit.

## Keputusan tentang perangkat lunak

Pembersihan data dan penandaan skenario dikerjakan di Python (`pandas`, `scipy`, `matplotlib`). Paket `statsmodels` tidak bisa dipasang di komputer ARM64 yang dipakai (tidak ada wheel dan build-nya membutuhkan Visual Studio), sehingga regresi logistik dengan galat baku robust klaster ditulis sendiri dengan `scipy`. Pada pelaksanaan akhir, analisis statistik dikerjakan ulang di R dan SPSS dan dibandingkan dengan hasil Python (lihat [`analisis_r/README.md`](analisis_r/README.md) dan [`analisis_spss/README.md`](analisis_spss/README.md)).
