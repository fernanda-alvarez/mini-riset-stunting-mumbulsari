# Daftar Status Gizi balita (per anak), SigiziKesga, Puskesmas Mumbulsari

Berkas ini hanya dokumentasi. **Datanya sendiri memuat identitas anak** (NIK, nama, nama orang tua, alamat) dan berada di folder yang di-`.gitignore`: `data/sumber/sigizi_daftar_status_gizi_2026-10-19/`. Jangan dicommit, dibagikan di grup, atau dicetak ke chat/log. Untuk analisis, pseudonimkan NIK dulu dan buang kolom identitas.

## Isi

34 berkas `Daftar_Status_Gizi_YYYY-MM.xls` (2024-01 s.d. 2026-10, ±230 MB total; 2024 diunduh belakangan). Sumber: **Laporan > Anak - Gizi > Daftar Status Gizi** (`/ppgbm/index.php/Laporan/daftar_status_gizi_balita.html`), akun Puskesmas Mumbulsari, diambil 19 Okt 2026. Filter: semua desa dan posyandu, usia 0–59 bulan, status gizi = semua, tanpa filter MBG/BBLR/PBLR/LILA/IMD. Setiap berkas = satu bulan pengukuran, satu baris per pengukuran/anak (NIK tidak ada yang ganda dalam satu bulan).

| Bulan | Baris | Bulan | Baris | Bulan | Baris |
|---|---|---|---|---|---|
| 2025-01 | 3.355 | 2025-09 | 2.898 | 2026-05 | 4.234 |
| 2025-02 | 2.632 | 2025-10 | 3.024 | 2026-06 | 4.194 |
| 2025-03 | 2.806 | 2025-11 | 3.025 | 2026-07 | 4.068 |
| 2025-04 | 2.982 | 2025-12 | 2.732 | 2026-08 | 4.025 |
| 2025-05 | 3.032 | 2026-01 | 4.249 | 2026-09 | 3.998 |
| 2025-06 | 2.555 | 2026-02 | 4.250 | 2026-10 | 20 (bulan berjalan) |
| 2025-07 | 2.798 | 2026-03 | 4.255 | **Total 2025–2026** | **72.079** |
| 2025-08 | 2.703 | 2026-04 | 4.244 | | |

Jumlah baris sama dengan "Jumlah Data" yang dilaporkan situs untuk tiap bulan.

Tahun 2024 (diunduh belakangan; jumlah baris = hitungan situs = total rekap Puskesmas, tidak ada anak tanpa desa): 2024-01 2.741, 02 2.875, 03 2.796, 04 2.849, 05 2.903, 06 3.104, 07 3.193, 08 3.173, 09 3.216, 10 3.132, 11 3.131, 12 3.150 (total 36.263). Total seluruh berkas: **108.342 baris**. Des 2023 hanya 269 anak menurut rekap (belum diunduh), jadi riwayat efektif mulai Jan 2024.


36 kolom: No, NIK, Nama, JK, Tgl Lahir, BB Lahir, TB Lahir, Nama Ortu, Prov, Kab/Kota, Kec, Pukesmas, Desa/Kel, Posyandu, RT, RW, Alamat, Usia Saat Ukur, Tanggal Pengukuran, Berat, Tinggi, Cara Ukur, LiLA, BB/U, ZS BB/U, TB/U, ZS TB/U, BB/TB, ZS BB/TB, Naik Berat Badan, Jml Vit A, KPSP, KIA, Kelas Ibu Balita, MBG, Detail.

## Membaca berkas

Berkas `.xls` sebenarnya HTML (satu `<table>`), bukan Excel asli, dan pandas tidak terpasang. Pakai `skrip/baca_export_sigizi.py` (`baca(path)` mengembalikan daftar baris; baris pertama = header). Catatan: header export memuat kolom **"Total Pengukuran"** yang tidak punya sel data pendamping, dan pembaca membuangnya supaya sejajar.

Audit agregat (tanpa mencetak data pribadi): `python -I skrip/audit_daftar_status_gizi.py "<folder proyek>"`. Skrip itu mencocokkan jumlah baris dengan hitungan situs dan merekonsiliasi dengan rekap per posyandu.

## Rekonsiliasi dengan rekap (hasil 19 Okt 2026)

72.079 anak di daftar = 72.071 (laporan Puskesmas; semuanya punya desa) + 8 anak yang kolom Desa-nya kosong. Dari 72.071: 71.261 punya posyandu valid (persis jumlah semua baris posyandu pada `../rekap_status_gizi/`) + 810 anak yang **Posyandu-nya kosong**. Rinciannya di `../rekap_status_gizi/README.md` (butir 2).

## Masalah kualitas data yang sudah terlihat

- **Posyandu kosong**: 818 anak (termasuk 8 tanpa desa). Terpusat di Mumbulsari (586), Lengkong (173), Lampeji (37); naik dari 0–6/bulan di 2025 menjadi 50–110/bulan di 2026.
- **Entri massal bernilai keliru (dugaan)**: pada Jan–Agu 2026 di Lampeji, Mumbulsari, Lengkong banyak anak berlabel TB/U "Outlier". Contoh Lampeji Jul 2026: 888 anak, semuanya bertanggal ukur 2026-07-31, umur median 37 bulan tetapi tinggi median 67 cm, ZS TB/U −6,3 s.d. −8,9, cara ukur "-". Jangan pakai angka stunting periode/desa itu sebelum dikonfirmasi ke petugas entri.
- **Nilai penanda/salah satuan**: ZS TB/U = 1000 (Mumbulsari Jan 2025), berat 3700 (kemungkinan gram diisi sebagai kg), tinggi/berat 0 pada sebagian baris.
- **Tanggal ukur di luar bulan berkas**: 1–2 baris per bulan bertanggal tahun-tahun lalu (2021–2025), kemungkinan salah ketik.
- Bulan terakhir (2026-10) belum final; laporan dihitung langsung, jadi angka bulan lama bisa berubah kalau ada entri susulan.

## Audit kualitas per bulan (34 bulan, 19 Okt 2026)

Tabel lengkap: [audit_kualitas_per_bulan.txt](audit_kualitas_per_bulan.txt) (dibuat `skrip/audit_kualitas_daftar.py`, agregat saja). Hal yang menonjol:

- **2024 jauh lebih bersih daripada 2025–2026**: Desa dan Posyandu tidak pernah kosong; TB/U Outlier hanya 0,1–1,5%; nilai aneh (ZS = ±1000, tinggi/berat 0, berat > 40, tinggi > 130) 0–14 baris per bulan. Posyandu kosong baru muncul sejak Jan 2025 dan naik terus sampai 110/bulan (Sep 2026).
- **Kontinuitas anak**: 89–97% NIK pada 2024 juga ada di bulan sebelumnya (81–94% pada 2025). Jan 2026 hanya 61%: sekitar 39% anak pada Jan 2026 tidak terukur di Des 2025. Ini selaras dengan lonjakan cakupan (`../rekap_tambahan/README.md`).
- **Tanggal ukur menumpuk di satu hari pada 2026**: pada Jan, Apr–Sep 2026, 51–57% baris bertanggal sama (2024: 12–30%; 2025: 9–15%). Selaras dengan dugaan perubahan cara pencatatan/entri massal sejak awal 2026.
- **Persentase stunting dari data per anak tidak stabil dan tidak bisa dibaca sebagai tren nyata**: 2024 turun 8,3% → 4,4%; 2025 naik 8,9% → 17,0% (dengan Nov 2025 turun ke 6,7%); 2026 3,5–8,5% lalu 25,0% pada Jul 2026 (entri massal, lihat atas). Label TB/U situs konsisten dengan ZS TB/U (100% sesuai ambang −2), jadi masalahnya bukan klasifikasi.
- **Bentuk sebaran z-score TB/U tidak wajar** (belum dibuktikan penyebabnya): median tinggi anak 12–23 bulan konstan 78,0 cm di 12 bulan yang dicek (Jul 2024–Jun 2025), dan z-score menumpuk persis di atas ambang −2 SD (Des 2024: persentil 5 = −2,00, persentil 25 = −1,82, median −1,48) lalu menumpuk di sekitar nilai tengah (Mei 2026: persentil 25 = −1,09, median −0,21, persentil 75 = −0,07). Bentuk seperti ini lazim pada pembulatan/pengisian tinggi yang tidak diukur sungguh-sungguh (heaping, tinggi dikira-kira atau disalin dari acuan), dan stunting 4–6% jauh di bawah angka umum balita Indonesia. Ini dugaan yang perlu diverifikasi (heaping digit tinggi, perbandingan dengan alat ukur, konfirmasi petugas), dan membuat prevalensi dari situs tidak bisa dianggap valid begitu saja. Perbandingan 2024 vs 2025 vs 2026 belum layak sebelum itu jelas.
- **Hasil cek heaping (`audit_heaping_tinggi.txt`, skrip `skrip/audit_heaping_tinggi.py`, agregat saja)**: bila tinggi diukur teliti, digit desimal .0 dan .5 masing-masing ±10%. Yang teramati: .0+.5 = 35–79% per bulan di 2024, 56–93% di 2025, 44–95% di 2026. Per desa (tahun penuh): Lampeji 2024 91% dan 2025 98%, Suco 92–93%, Karangkedawung 84–93% (tinggi hampir selalu bulat); Lengkong 35–44% dan Tamansari 42% (2024), lebih wajar. Pada 2026 Lampeji (39%), Mumbulsari (32%), Lengkong (44%) justru turun jauh, bertepatan dengan lonjakan TB/U Outlier dan entri massal (pola isian berbeda, bukan tanda pengukuran lebih teliti). Agu 2026 .5 = 32% (entri massal). Catatan: belum dipastikan apakah ".0" berasal dari entri cm bulat atau pemformatan situs; variasi besar antar desa menunjukkan itu kebiasaan entri.
- **Penumpukan tepat di atas −2 SD ada di semua tahun**: rasio jumlah anak di z [−2,0; −1,9) terhadap [−2,1; −2,0) seharusnya sekitar 1. Teramati 1,4–18 per bulan (2024-10: 18,4; Lampeji 2025: 18,9; Kawangrejo 2025: 10,6; Suco 2025: 7,0). Desa yang mendekati wajar: Lengkong 2025 (1,09), Mumbulsari 2025 (1,17), Tamansari 2025 (1,18). Pembulatan tinggi ke cm membuat z-score bergerombol, tetapi tidak menjelaskan rasio sebesar itu, jadi dugaan tinggi disesuaikan agar tidak masuk kategori stunting belum bisa disingkirkan. Karena 2024 ikut dianalisis, stunting 2024 juga tidak bisa dianggap lebih valid daripada 2025–2026.

## Mengambil ulang

Server menyimpan filter di sesi login, jadi **berurutan**, bukan paralel (paralel membuat HTTP 500).
1. Kirim POST pencarian ke halaman Daftar (field seperti form: `prov=35, kab=3509, kec=3509090, kode_pusk=P3509090201, pkm=5335, kel=, POSY=, usia=059, status_gz=0, mbg=, bblr=, pblr=, LILA=, imd=, bulan, tahun, cari=`). Halaman menampilkan "Jumlah Data : N" dan hanya 10 baris per halaman (jangan pakai paginasi: 7.000+ request).
2. Buka `/ppgbm/index.php/Laporan/daftar_status_gizi_balita_print.html` (tombol Export Excel). Server membuat seluruh hasil filter dalam satu berkas (±7–9 MB, 30–60 detik) dengan nama `Daftar-Anak-Berdasarkan-Status-Gizi-<kode>.xls`.
3. Di browser pane aplikasi, navigasi ke URL itu dilaporkan "gagal" tetapi unduhan tetap jalan ke folder Download (sementara bernama `.tmp`). **Tunggu sampai jumlah baris = N sebelum memindahkan**: browser masih menulis setelah berkasnya muncul, dan memindahkan terlalu dini menghasilkan berkas terpotong (kejadian di Sep dan Okt 2025, terdeteksi dan diperbaiki).
4. Pane memblokir koneksi ke localhost, jadi data tidak bisa dikirim dari halaman ke server lokal.
