# Hasil pembersihan data dan analisis versi Python

Folder ini berisi keluaran tahap 1 (pembersihan data) dan tahap 2 (analisis) versi Python, seluruhnya berupa agregat. Pembersihan dikerjakan oleh `skrip/bersihkan_data_anak.py` pada 19 Oktober 2026 dari 33 berkas `Daftar_Status_Gizi_YYYY-MM.xls` (Januari 2024 sampai September 2026). Berkas Oktober 2026 tidak dipakai karena baru berisi 20 pengukuran dan belum final. Rencana analisisnya ada di [`../RENCANA_ANALISIS.md`](../RENCANA_ANALISIS.md).

## Isi folder

| Berkas | Isi | Ada di repo |
|---|---|---|
| `desa_bulan.csv` | Satu baris per desa, bulan, dan skenario (7 desa × 33 bulan × 4 skenario = 741 baris): jumlah anak, jumlah dan persen stunting, wasting, dan underweight, serta kolom kualitas data. | ya |
| `log_cleaning.txt` | Jumlah baris yang terkena tiap flag per tahun, jumlah baris per skenario, daftar desa-bulan anomali, dan persentase penumpukan digit per desa-tahun. | ya |
| `tabel/` | CSV hasil analisis 1–9 dan analisis tambahan P1–P3. Penjelasan tiap tabel ada di [`tabel/README.md`](tabel/README.md). | ya |
| `Analisis_Stunting_Mumbulsari.xlsx` | Workbook akhir dengan 16 sheet (ringkasan, analisis 1–12, kamus, dan data desa-bulan), lengkap dengan grafik Excel. Hanya berisi agregat. | ya |
| `anak_bersih.csv` | Dataset anak-bulan (108.322 baris dari 6.312 anak) dengan ID acak. Disimpan di `data/sumber/anak_bersih/`. | tidak |
| `.garam` | Garam HMAC untuk membuat ID acak. Tanpa berkas ini ID tidak bisa dibuat ulang, dan berkas ini tidak boleh dibagikan. Disimpan di `data/sumber/anak_bersih/`. | tidak |

`anak_bersih.csv` tidak memuat NIK, nama, nama orang tua, alamat, RT/RW, dan tanggal lahir (diganti `umur_bln`). Kolomnya sudah diuraikan di [`README.md`](../../../README.md) utama pada bagian "Format data sumber".

## Validasi terhadap laporan situs

Setelah pembersihan, jumlah kasus stunting, wasting, dan underweight yang dihitung dari data per anak (semua baris, sebelum flag diterapkan) dibandingkan dengan sheet "Laporan Puskesmas" dari rekap status gizi SigiziKesga. Hasilnya sama persis pada seluruh 147 desa-bulan yang bisa dibandingkan (Januari 2025 sampai September 2026). Artinya definisi outcome di skrip sudah mereproduksi angka resmi situs. Satu pemeriksaan lain: tidak ada ID anak yang memiliki lebih dari satu jenis kelamin atau tanggal lahir, sehingga ID acak dari NIK cukup layak dipakai sebagai kunci untuk menautkan pengukuran antarbulan.

## Flag kualitas data

Baris yang bermasalah tidak dihapus, hanya ditandai di kolom berawalan `f_`. Ada dua jenis.

**Flag keras** mengeluarkan baris dari semua analisis. Gabungannya ada di kolom `f_keras`, dan terdiri dari lima aturan:
- `f_zs_penanda`: nilai z-score berupa penanda (|z| ≥ 999) dan bukan hasil hitung.
- `f_nol`: tinggi atau berat bernilai nol.
- `f_aneh`: berat lebih dari 40 kg atau tinggi lebih dari 130 cm pada balita.
- `f_nik_ganda`: NIK yang sama muncul lebih dari sekali dalam satu bulan.
- `f_umur_luar`: umur di luar 0 sampai kurang dari 60 bulan.

**Flag lunak** hanya menandai. Beberapa dipakai untuk membentuk skenario, sisanya sebagai informasi:
- `f_anomali_desabulan`: desa-bulan dengan TB/U outlier minimal 10% atau stunting minimal 50%. Pada bulan normal, proporsi ini 0,3–3% dan 4–17%. Dipakai di skenario S3.
- `f_heaping_tinggi`: desa-tahun dengan digit desimal tinggi badan .0 atau .5 minimal 70% (pengukuran yang teliti seharusnya menghasilkan sekitar 20%). Dipakai di skenario S2.
- `f_tgl_seragam`: satu tanggal ukur memuat minimal 30% baris dalam satu desa-bulan.
- `f_tbu_outlier`: label TB/U dari situs adalah "Outlier".
- `f_cara_ukur_salah`: cara ukur tidak sesuai umur (berdiri pada anak di bawah 24 bulan, atau terlentang pada anak 24 bulan ke atas). Cara ukur "-" tidak dinilai.
- `f_tgl_luar`: tanggal ukur di luar bulan berkas.
- `f_pos_kosong`: kolom posyandu kosong.
- `f_nik_pendek`: NIK bukan 16 digit. Banyak baris (sekitar 42%) terkena flag ini, tetapi NIK tersebut tetap konsisten sebagai kunci.

## Skenario sensitivitas

Karena sulit memastikan di mana saja masalah pencatatan berada, setiap hasil dihitung pada empat himpunan data.

| Skenario | Definisi |
|---|---|
| S0 | Semua baris tanpa flag keras dan dengan desa terisi. |
| S1 | S0 tanpa Lampeji, Mumbulsari, dan Lengkong untuk Januari sampai September 2026. |
| S2 | S0 hanya pada desa-tahun dengan penumpukan digit tinggi badan rendah (kurang dari 70%). |
| S3 | S0 tanpa desa-bulan anomali (15 desa-bulan, antara lain tiga desa di atas pada Juni dan Juli 2026). |

Skenario S1 dan S2 mengubah komposisi desa, bukan hanya membuang data yang buruk. Karena itu angka gabungan antar skenario tidak boleh dibandingkan langsung, dan perbandingan sebaiknya dilakukan per desa.

Alasan S1 mencakup sampai September 2026: pada tiga desa tersebut, hampir semua anak dalam satu desa-bulan tercatat dengan tanggal ukur yang sama, dan pola ini berlanjut dari Januari hingga September 2026. Petugas entri sudah mengonfirmasi bahwa sebagian desa memang mengisi satu tanggal per bulan dan membulatkan tinggi badan. Akibatnya tanggal ukur di desa-desa itu adalah tanggal entri, dan analisis di sana hanya bisa setingkat bulan.

## Pembatasan periode

Data diambil dari SigiziKesga pada 19 Oktober 2026. Analisis memakai pengukuran 1 Januari 2024 sampai 30 September 2026.

## Membangun ulang workbook

```bash
python -I skrip/bangun_workbook_analisis.py data/sigizi/analisis data/sumber/anak_bersih/anak_bersih.csv data/sigizi/analisis/Analisis_Stunting_Mumbulsari.xlsx
```

Workbook dibangun dari tabel di `tabel/`. `anak_bersih.csv` hanya dipakai untuk menghitung ulang agregat pada sheet 10 (MBG), 11 (profil desa), dan 12 (kualitas data), yang dihitung langsung di skrip, bukan dari CSV. Tidak ada data pribadi yang ditulis ke workbook.
