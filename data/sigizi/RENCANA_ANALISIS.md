# Rencana analisis data SigiziKesga (Puskesmas Mumbulsari)

Dibuat 19 Okt 2026. Status tiap tahap ada di judulnya. Sumber data dan kualitasnya: `daftar_status_gizi/README.md`, `rekap_status_gizi/README.md`, `rekap_tambahan/README.md`, `inventaris_sigizikesga.md`.

## Tahap 0 — Keputusan dasar [DISETUJUI 19 Okt 2026]
- **Periode**: Jan 2024–Sep 2026. Okt 2026 dibuang (belum final). 2024 ikut dianalisis atas persetujuan pembimbing.
- **Dua unit analisis**: desa-bulan (7 desa × 33 bulan) dan anak-bulan (±108 ribu pengukuran, ±6.300 anak).
- **Data bermasalah ditandai (flag), tidak dihapus**, lalu dibandingkan lewat skenario sensitivitas:
  - **S0**: semua data.
  - **S1**: tanpa Lampeji, Mumbulsari, Lengkong untuk Jan–Agu 2026.
  - **S2**: hanya desa-tahun dengan heaping tinggi badan rendah.
  - **S3**: tanpa hari entri massal.

## Tahap 1 — Data cleaning [DISETUJUI, SELESAI 19 Okt 2026; hasil dan definisi flag aktual: `analisis/README.md`]
Perubahan dari usulan: "entri massal" dipecah menjadi `f_tgl_seragam` (informasi) dan `f_anomali_desabulan` (dipakai di S3); `statsmodels` tidak bisa dipasang (ARM64), regresi ditulis dengan `scipy`.
1. NIK diganti ID acak; Nama, Nama Ortu, Alamat, RT/RW dibuang; kolom kosong dibuang (KPSP, KIA, Kelas Ibu).
2. BB Lahir (kg) → gram, turunkan BBLR (<2.500 g) dan PBLR (<48 cm); hitung ulang umur dari Tgl Lahir dan tanggal ukur.
3. Flag kualitas, satu kolom per aturan: ZS = ±1000; tinggi/berat 0; berat > 40; tinggi > 130; tanggal ukur di luar bulan berkas; Desa/Posyandu kosong; NIK ganda dalam satu bulan; entri massal (tanggal modus menumpuk di desa-bulan); TB/U Outlier; Cara Ukur tidak sesuai umur; heaping per desa-tahun.
4. Opsional: hitung ulang z-score WHO (butuh tabel LMS).
5. Keluaran: `anak_bersih` (anak-bulan), `desa_bulan` (7 × 33: persen stunting, wasting, underweight, cakupan, kolom kualitas), log jumlah baris kena tiap flag.

## Tahap 2 — Analisis 1–12 [DISETUJUI]
| # | Analisis | Metode | Catatan kelayakan |
|---|---|---|---|
| 1 | Prevalensi stunting, wasting, underweight | persen + CI Wilson, per desa dan bulan | layak, dengan caveat heaping |
| 2 | Tren 2024→2026 | uji tren (Cochran-Armitage/Mann-Kendall), regresi segmented | dibaca bersama perubahan cakupan |
| 3 | Antar desa | chi-square, forest plot | layak |
| 4 | Cakupan ukur/sasaran | deskriptif + tren | 22 bulan sudah ada, 2024 dihitung baru |
| 5 | Status gizi menurut umur dan JK | tabel silang | layak |
| 6 | Distribusi z-score | rerata, SD, histogram per tahun | bukti kualitas data |
| 7 | Prevalensi per kelompok umur dan JK | tabel, kurva umur | layak |
| 8 | Faktor risiko BBLR, PBLR, JK, umur | regresi logistik (GEE per anak) | MBG, KPSP, KIA, Kelas Ibu dikeluarkan |
| 9 | Longitudinal | insiden dan pemulihan stunting, Kaplan-Meier, lintasan z-score | layak, kekuatan utama dataset |
| 10 | Dampak MBG | deskriptif saja | hanya 275 pengukuran "ya", tidak layak inferensial |
| 11 | Spasial | tingkat desa (7 titik) | tanpa peta kecuali ada shapefile; posyandu tidak dipakai |
| 12 | Kualitas data | heaping, z-score piling, entri massal | masuk Metode dan Keterbatasan |

Fokus: utama tren dan perbandingan desa (1–5), sekunder faktor risiko dan longitudinal (7–9).

## Tahap 3 — Excel [USULAN]
Satu workbook `Analisis_Stunting_Mumbulsari.xlsx` (openpyxl): Ringkasan, Kamus Data, satu sheet per analisis (tabel + grafik native), Data Desa-Bulan, Kualitas. Gaya: header berwarna, panel dibekukan, filter, format angka/persen, lebar kolom otomatis, color scale, setelan cetak. Excel lama (`rekap_status_gizi_per_posyandu.xlsx`, `sasaran_cakupan_cek2024.xlsx`) dirapikan dengan gaya yang sama.

## Tahap 4 — Urutan kerja
Cleaning → dataset desa-bulan → analisis 1–5 → 6–9 → 10–12 → workbook akhir. Berhenti dan komit di tiap akhir tahap.

## Keputusan terbuka
1. Pertanyaan utama (usulan: tren + antar desa utama; faktor risiko + longitudinal sekunder).
2. Dataset per anak yang dipseudonimkan masuk git atau tetap di `data/sumber/` (sementara: tetap di `data/sumber/`).
3. Pemasangan paket Python `pandas`, `scipy`, `statsmodels`, `matplotlib` (belum terpasang; dibutuhkan analisis 2, 8, 9).
4. Satu workbook utama atau beberapa berkas (usulan: satu).
