# Daftar Status Gizi balita (per anak), SigiziKesga

Berkas ini hanya dokumentasi. Data aslinya memuat identitas anak (NIK, nama, nama orang tua, alamat), jadi tidak ada di repo dan disimpan di folder yang diabaikan Git (`data/sumber/sigizi_daftar_status_gizi_2026-10-19/`). Data itu tidak boleh di-commit, dibagikan di grup, atau dicetak ke log. Untuk analisis, NIK dipseudonimkan dan kolom identitas dibuang oleh `skrip/bersihkan_data_anak.py`.

## Sumber dan isi

Laporan yang dipakai adalah **Laporan > Anak - Gizi > Daftar Status Gizi** di SigiziKesga (modul e-PPGBM), diambil dengan akun Puskesmas Mumbulsari pada 19 Oktober 2026. Filternya: semua desa dan posyandu, usia 0–59 bulan, semua status gizi, tanpa filter MBG, BBLR, PBLR, LILA, dan IMD. Setiap berkas mewakili satu bulan pengukuran dengan satu baris per pengukuran per anak. Dalam satu bulan tidak ada NIK yang muncul dua kali.

Ada 34 berkas `Daftar_Status_Gizi_YYYY-MM.xls`, dari Januari 2024 sampai Oktober 2026, dengan total 108.342 baris. Berkas Oktober 2026 hanya berisi 20 baris karena bulannya masih berjalan, dan tidak dianalisis; yang dianalisis adalah 33 bulan (108.322 baris). Jumlah baris tiap berkas sama dengan "Jumlah Data" yang dilaporkan situs untuk bulan itu. Berkas tahun 2024 diunduh belakangan, dan jumlah barisnya sama dengan total rekap tingkat Puskesmas. Desember 2023 hanya berisi 269 anak menurut rekap dan tidak diunduh, jadi riwayat efektif dimulai Januari 2024.

Setiap berkas memiliki 36 kolom: No, NIK, Nama, JK, Tgl Lahir, BB Lahir, TB Lahir, Nama Ortu, Prov, Kab/Kota, Kec, Pukesmas, Desa/Kel, Posyandu, RT, RW, Alamat, Usia Saat Ukur, Tanggal Pengukuran, Berat, Tinggi, Cara Ukur, LiLA, BB/U, ZS BB/U, TB/U, ZS TB/U, BB/TB, ZS BB/TB, Naik Berat Badan, Jml Vit A, KPSP, KIA, Kelas Ibu Balita, MBG, dan Detail.

## Membaca berkas

Berkas berekstensi `.xls` itu sebenarnya HTML dengan satu `<table>`, bukan Excel asli, sehingga `pandas.read_excel` tidak bisa membacanya. Pembacanya adalah `skrip/baca_export_sigizi.py` (fungsi `baca(path)` mengembalikan daftar baris, baris pertama adalah header). Header ekspor memuat kolom "Total Pengukuran" yang tidak memiliki sel data pendamping, dan pembaca membuangnya supaya kolom tetap sejajar. Pembaca memakai regex karena pengurai HTML standar menghilangkan baris pada berkas September 2025.

Audit agregat yang tidak mencetak data pribadi dijalankan dengan:

```bash
python -I skrip/audit_daftar_status_gizi.py "<folder proyek>"
```

Skrip ini mencocokkan jumlah baris dengan hitungan situs dan merekonsiliasi dengan rekap per posyandu.

## Rekonsiliasi dengan rekap Puskesmas

Untuk 22 bulan (Januari 2025 sampai Oktober 2026), jumlah anak di daftar per anak dicocokkan dengan laporan rekap: 72.079 anak di daftar sama dengan 72.071 anak pada laporan Puskesmas (semuanya punya desa) ditambah 8 anak yang kolom Desa-nya kosong. Dari 72.071 itu, 71.261 punya posyandu yang valid dan jumlahnya persis sama dengan seluruh baris posyandu di rekap, sedangkan 810 anak punya desa tetapi kolom Posyandu-nya kosong. Rincian lebih lanjut ada di [`../rekap_status_gizi/README.md`](../rekap_status_gizi/README.md).

## Jenis masalah kualitas data

Pemeriksaan kualitas dilakukan per bulan dan hasil agregatnya disimpan dalam tiga berkas teks di folder ini: `audit_kualitas_per_bulan.txt` (dari `skrip/audit_kualitas_daftar.py`), `audit_heaping_tinggi.txt` (dari `skrip/audit_heaping_tinggi.py`), dan `kelengkapan_faktor_risiko.txt` (dari `skrip/periksa_kolom_faktor.py`). Jenis masalah yang diperiksa:

- **Kolom desa atau posyandu kosong.** Anak tanpa posyandu dihitung di total desa tetapi tidak masuk baris posyandu mana pun.
- **Nilai penanda dan salah satuan.** Misalnya z-score bernilai 1000, berat 3700 (kemungkinan gram yang diisi sebagai kilogram), dan tinggi atau berat nol.
- **Tanggal ukur di luar bulan berkas.** Biasanya salah ketik tahun.
- **Tanggal ukur yang menumpuk.** Pada beberapa desa-bulan, hampir semua anak tercatat dengan tanggal ukur yang sama, dan petugas entri sudah mengonfirmasi bahwa sebagian desa mengisi satu tanggal per bulan. Tanggal itu lalu bukan tanggal pengukuran sebenarnya.
- **Entri massal dengan nilai yang tidak masuk akal.** Misalnya ratusan anak dengan umur median 37 bulan tetapi tinggi median 67 cm, berlabel TB/U "Outlier".
- **Penumpukan digit tinggi badan (heaping).** Tinggi badan yang diukur teliti seharusnya memiliki digit desimal .0 dan .5 masing-masing sekitar 10%. Proporsi yang jauh lebih tinggi menandakan pembulatan atau pengisian yang dikira-kira, dan petugas mengonfirmasi bahwa tinggi badan memang dibulatkan.
- **Penumpukan z-score tepat di atas −2 SD.** Rasio jumlah anak di rentang −2,0 sampai −1,9 SD terhadap −2,1 sampai −2,0 SD seharusnya sekitar 1.
- **Kontinuitas anak antarbulan,** yaitu persentase NIK yang juga ada pada bulan sebelumnya.
- **Kelengkapan kolom faktor risiko.** `BB Lahir` tertulis dalam kilogram dan diubah ke gram. `MBG`, `KPSP`, `KIA`, dan `Kelas Ibu Balita` hampir seluruhnya kosong atau tidak konsisten sehingga tidak dipakai sebagai variabel analisis. Faktor risiko yang dipakai adalah BBLR, PBLR, jenis kelamin, dan umur.

Label TB/U dari situs konsisten dengan z-score TB/U (seluruhnya sesuai ambang −2 SD), jadi masalahnya terletak pada nilai ukur dan pencatatannya, bukan pada klasifikasinya.

Data bulan berjalan dihitung langsung saat laporan diminta, sehingga angka bulan yang sudah lewat bisa berubah bila ada entri susulan.
