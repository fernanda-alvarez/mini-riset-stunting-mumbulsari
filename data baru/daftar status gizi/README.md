# Daftar Status Gizi balita (per anak), SigiziKesga, Puskesmas Mumbulsari

Berkas ini hanya dokumentasi. **Datanya sendiri memuat identitas anak** (NIK, nama, nama orang tua, alamat) dan berada di folder yang di-`.gitignore`: `data/sumber/sigizi_daftar_status_gizi_2026-10-19/`. Jangan dicommit, dibagikan di grup, atau dicetak ke chat/log. Untuk analisis, pseudonimkan NIK dulu dan buang kolom identitas.

## Isi

22 berkas `Daftar_Status_Gizi_YYYY-MM.xls` (2025-01 s.d. 2026-10, ±150 MB total). Sumber: **Laporan > Anak - Gizi > Daftar Status Gizi** (`/ppgbm/index.php/Laporan/daftar_status_gizi_balita.html`), akun Puskesmas Mumbulsari, diambil 19 Okt 2026. Filter: semua desa dan posyandu, usia 0–59 bulan, status gizi = semua, tanpa filter MBG/BBLR/PBLR/LILA/IMD. Setiap berkas = satu bulan pengukuran, satu baris per pengukuran/anak (NIK tidak ada yang ganda dalam satu bulan).

| Bulan | Baris | Bulan | Baris | Bulan | Baris |
|---|---|---|---|---|---|
| 2025-01 | 3.355 | 2025-09 | 2.898 | 2026-05 | 4.234 |
| 2025-02 | 2.632 | 2025-10 | 3.024 | 2026-06 | 4.194 |
| 2025-03 | 2.806 | 2025-11 | 3.025 | 2026-07 | 4.068 |
| 2025-04 | 2.982 | 2025-12 | 2.732 | 2026-08 | 4.025 |
| 2025-05 | 3.032 | 2026-01 | 4.249 | 2026-09 | 3.998 |
| 2025-06 | 2.555 | 2026-02 | 4.250 | 2026-10 | 20 (bulan berjalan) |
| 2025-07 | 2.798 | 2026-03 | 4.255 | **Total** | **72.079** |
| 2025-08 | 2.703 | 2026-04 | 4.244 | | |

Jumlah baris sama dengan "Jumlah Data" yang dilaporkan situs untuk tiap bulan.

36 kolom: No, NIK, Nama, JK, Tgl Lahir, BB Lahir, TB Lahir, Nama Ortu, Prov, Kab/Kota, Kec, Pukesmas, Desa/Kel, Posyandu, RT, RW, Alamat, Usia Saat Ukur, Tanggal Pengukuran, Berat, Tinggi, Cara Ukur, LiLA, BB/U, ZS BB/U, TB/U, ZS TB/U, BB/TB, ZS BB/TB, Naik Berat Badan, Jml Vit A, KPSP, KIA, Kelas Ibu Balita, MBG, Detail.

## Membaca berkas

Berkas `.xls` sebenarnya HTML (satu `<table>`), bukan Excel asli, dan pandas tidak terpasang. Pakai `skrip/baca_export_sigizi.py` (`baca(path)` mengembalikan daftar baris; baris pertama = header). Catatan: header export memuat kolom **"Total Pengukuran"** yang tidak punya sel data pendamping, dan pembaca membuangnya supaya sejajar.

Audit agregat (tanpa mencetak data pribadi): `python -I skrip/audit_daftar_status_gizi.py "<folder proyek>"`. Skrip itu mencocokkan jumlah baris dengan hitungan situs dan merekonsiliasi dengan rekap per posyandu.

## Rekonsiliasi dengan rekap (hasil 19 Okt 2026)

72.079 anak di daftar = 72.071 (laporan Puskesmas; semuanya punya desa) + 8 anak yang kolom Desa-nya kosong. Dari 72.071: 71.261 punya posyandu valid (persis jumlah semua baris posyandu pada `../rekap status gizi/`) + 810 anak yang **Posyandu-nya kosong**. Rinciannya di `../rekap status gizi/README.md` (butir 2).

## Masalah kualitas data yang sudah terlihat

- **Posyandu kosong**: 818 anak (termasuk 8 tanpa desa). Terpusat di Mumbulsari (586), Lengkong (173), Lampeji (37); naik dari 0–6/bulan di 2025 menjadi 50–110/bulan di 2026.
- **Entri massal bernilai keliru (dugaan)**: pada Jan–Agu 2026 di Lampeji, Mumbulsari, Lengkong banyak anak berlabel TB/U "Outlier". Contoh Lampeji Jul 2026: 888 anak, semuanya bertanggal ukur 2026-07-31, umur median 37 bulan tetapi tinggi median 67 cm, ZS TB/U −6,3 s.d. −8,9, cara ukur "-". Jangan pakai angka stunting periode/desa itu sebelum dikonfirmasi ke petugas entri.
- **Nilai penanda/salah satuan**: ZS TB/U = 1000 (Mumbulsari Jan 2025), berat 3700 (kemungkinan gram diisi sebagai kg), tinggi/berat 0 pada sebagian baris.
- **Tanggal ukur di luar bulan berkas**: 1–2 baris per bulan bertanggal tahun-tahun lalu (2021–2025), kemungkinan salah ketik.
- Bulan terakhir (2026-10) belum final; laporan dihitung langsung, jadi angka bulan lama bisa berubah kalau ada entri susulan.

## Mengambil ulang

Server menyimpan filter di sesi login, jadi **berurutan**, bukan paralel (paralel membuat HTTP 500).
1. Kirim POST pencarian ke halaman Daftar (field seperti form: `prov=35, kab=3509, kec=3509090, kode_pusk=P3509090201, pkm=5335, kel=, POSY=, usia=059, status_gz=0, mbg=, bblr=, pblr=, LILA=, imd=, bulan, tahun, cari=`). Halaman menampilkan "Jumlah Data : N" dan hanya 10 baris per halaman (jangan pakai paginasi: 7.000+ request).
2. Buka `/ppgbm/index.php/Laporan/daftar_status_gizi_balita_print.html` (tombol Export Excel). Server membuat seluruh hasil filter dalam satu berkas (±7–9 MB, 30–60 detik) dengan nama `Daftar-Anak-Berdasarkan-Status-Gizi-<kode>.xls`.
3. Di browser pane aplikasi, navigasi ke URL itu dilaporkan "gagal" tetapi unduhan tetap jalan ke folder Download (sementara bernama `.tmp`). **Tunggu sampai jumlah baris = N sebelum memindahkan**: browser masih menulis setelah berkasnya muncul, dan memindahkan terlalu dini menghasilkan berkas terpotong (kejadian di Sep dan Okt 2025, terdeteksi dan diperbaiki).
4. Pane memblokir koneksi ke localhost, jadi data tidak bisa dikirim dari halaman ke server lokal.
