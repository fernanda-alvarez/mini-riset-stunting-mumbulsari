# Inventaris data SigiziKesga (akun Puskesmas Mumbulsari) dan analisis yang layak

Dibuat 19 Okt 2026. Situs: SISFO Gizi Terpadu / SigiziKesga. Alamat dasar semua laporan: `https://sigizikesga.kemkes.go.id/ppgbm/index.php/` (path di tabel ditulis setelah alamat ini). Berkas ini tidak memuat data per anak, hanya nama kolom, jumlah, dan agregat.

## 0. Status pemeriksaan (baca dulu)

- **Sudah**: ±70 halaman dibuka dengan GET (menu Entry, seluruh Laporan Anak, sebagian Rematri dan Bumil, Dashboard, beranda). Dibaca: judul, nama field filter, pilihan tiap filter, tombol, dan judul kolom bila tabel tampil saat halaman dibuka. Tidak ada Cari Data, Export, POST, atau perubahan data. Halaman Tambah Balita dan Permintaan Pindah (Masuk) hanya dilihat, tidak dikirim atau diklik. Tidak ada nilai per anak yang dibaca.
- **Belum** (ditandai `?` di tabel): kolom keluaran hampir semua laporan, tombol Export, tahun data paling awal, dan volume. Semuanya butuh menekan Cari Data. Pengguna menjawab "belum, tunggu dulu" ketika ditanya apakah unduhan Daftar Status Gizi sudah dinyatakan selesai (22 berkas sudah ada di folder sumber, terakhir ditulis 12.34 WIB), jadi query tidak dijalankan. Prosedur melengkapinya ada di bagian 8.
- **Tidak dibuka sama sekali** (aksi yang bisa mengubah data): Backup/Restore (Backup, Init Data, Restore, Populate PKM, Populate Pemeriksaan ANC Pertama, Sinkronisasi Data), Sinkron Data Wilayah Ukur, semua halaman Import, serta Ganti Password, Lapor Masalah, Detail User.
- **Buku Panduan** (`/ppgbm/assets/mabook/panduan_ppgbm_new_final.pdf`) hanya bisa diakses setelah login (HTTP 403 untuk akses tanpa login). Isinya belum dibaca. Itu sumber resmi untuk definisi Outlier, insiden stunting, "Naik BB", dan cara hitung z-score. Membukanya berarti mengunduh berkas, jadi perlu izin pengguna.

Legenda kolom tabel: **[F]** dibaca dari form, **[D]** dari dokumentasi proyek (`../README`, `rekap_status_gizi/README.md`, `daftar_status_gizi/README.md`), **[J]** dugaan dari judul laporan, `?` belum diperiksa.

## 1. Tujuan dan batasan (jawaban pengguna)

- **Pertanyaan riset**: belum ditentukan ("belum tahu, mau lihat dulu"). Inventaris sengaja luas. Usulan urutan pertanyaan ada di bagian 5.
- **Luaran yang diinginkan**: keempatnya: prevalensi per desa, tren bulanan/musiman, faktor risiko, evaluasi intervensi/MBG.
- **Etik/izin**: pengguna menyatakan aman, izin ada karena memegang akses, dan analisis hanya lokal di laptop ini. Dicatat sebagai batasan kerja: NIK dipseudonimkan, kolom identitas dibuang, tidak ada data per anak di git/chat/grup, laporan hanya memuat agregat. Dokumen izin tertulis dan status persetujuan etik tetap masuk daftar pertanyaan terbuka (butir 11) karena laporan akhir akan menyebut nama desa.

## 2. Peta data di situs

Tiga lapis data, semuanya berbasis NIK anak:

1. **Registri anak** (menu Entry). Sekitar 4.291 sampai 4.300 anak terdaftar (halaman terakhir Daftar Balita mulai pada offset 4290, 10 baris per halaman; filter bawaan, usia dan status aktif belum dibedah). Variabel yang dicatat saat registrasi (dari form Tambah Balita, tidak diisi): tanggal lahir, jenis kelamin, no KK, NIK (ada opsi "tanpa NIK" → NIK dummy), nama, **BB lahir, panjang lahir, lingkar kepala lahir**, KMS, **KIA bayi kecil**, **tatalaksana BBLR**, **IMD**, dua field numerik yang artinya belum jelas (`OP_VAL`, `alergi`), nama dan NIK orang tua, telepon, wilayah (desa, posyandu, PAUD), alamat, RT, RW.
2. **Pengukuran bulanan** di posyandu: berat, tinggi/panjang, cara ukur, LiLA → z-score dan kategori BB/U, TB/U, BB/TB, flag Outlier, "Naik Berat Badan".
3. **Layanan dan intervensi**: Vitamin A, ASI eksklusif (recall), MPASI (termasuk protein hewani), imunisasi, Taburia, tindakan/PMT, KPSP, KIA, Kelas Ibu Balita, MBG, jumlah penimbangan/pengukuran/pemantauan per tahun.

Yang **tidak ada** di situs: pendidikan dan pekerjaan orang tua, pendapatan, tinggi ibu, paritas dan jarak lahir, sanitasi dan air bersih, riwayat infeksi (diare, ISPA), status JKN, jarak ke fasilitas. Hanya RT/RW dan alamat sebagai proksi geografis.

Dataset yang **sudah ada di folder proyek**:

| Dataset | Isi | Volume | Lokasi |
|---|---|---|---|
| Daftar Status Gizi | per anak per bulan, 36 kolom [D] | 72.079 baris (Jan 2025–Okt 2026; Okt baru 20 baris) | `data/sumber/sigizi_daftar_status_gizi_2026-10-19/` (identitas, tidak masuk git) |
| Rekap Status Gizi | per posyandu dan per desa per bulan, 20 angka [D] | 154 baris desa-bulan (7 × 22) | `rekap_status_gizi/rekap_status_gizi_per_posyandu.xlsx`, sheet `Laporan Puskesmas` |
| Rekap Insiden Stunting | per desa × jenis kelamin per bulan [diverifikasi dari berkas] | 10 berkas (Jan–Okt 2026), ±4 KB | `data/sigizi/rekap_insiden_stunting/` |

Kolom Daftar Status Gizi [D]: No, NIK, Nama, JK, Tgl Lahir, BB Lahir, TB Lahir, Nama Ortu, Prov, Kab/Kota, Kec, Pukesmas, Desa/Kel, Posyandu, RT, RW, Alamat, Usia Saat Ukur, Tanggal Pengukuran, Berat, Tinggi, Cara Ukur, LiLA, BB/U, ZS BB/U, TB/U, ZS TB/U, BB/TB, ZS BB/TB, Naik Berat Badan, Jml Vit A, KPSP, KIA, Kelas Ibu Balita, MBG, Detail.

Konsekuensinya: BBLR (BB lahir < 2.500 g) dan PBLR (panjang lahir < 48 cm) bisa diturunkan sendiri dari `BB Lahir` dan `TB Lahir`, jadi tidak perlu query terpisah. KPSP, KIA, Kelas Ibu, MBG, Vit A, LiLA sudah ada di file per anak. **IMD, ASI eksklusif, MPASI, imunisasi, Taburia, tindakan/PMT tidak ada** di file itu dan hanya ada di laporan masing-masing.

## 3. Inventaris laporan

Komponen form yang sama di hampir semua laporan: `kel` (desa; 7 desa + kosong = semua), `POSY` (posyandu; kosong sampai desa dipilih, daftar dari `Common/posy/?desa_id=<kode>&type=DESA`), `usia` (kelompok umur preset), `bulan`, `tahun` (pilihan 2015–2026). Semua form adalah POST ke alamat halaman itu sendiri, tombol `cari`, field tersembunyi `kode_pusk`. Kode wilayah: prov 35, kab 3509, kec 3509090, pkm 5335, kode puskesmas P3509090201, desa 3509090001–3509090007 (Kawangrejo, Tamansari, Suco, Lampeji, Mumbulsari, Lengkong, Karangkedawung). 78 posyandu terdaftar [D]. Di tabel, "Daftar" = per anak (berisi NIK dan nama, jenis [J]), "Rekap" = agregat [J]. Kolom Periode: dropdown tahun selalu 2015–2026, tetapi **tahun data paling awal belum dicek** kecuali Jan 2025–Okt 2026 untuk tiga dataset di atas.

Singkatan filter: `m`=mbg (Ya/Tidak), `b`=bblr, `p`=pblr (Ya/Tidak). Angka dalam kurung pada `usia` = jumlah pilihan.

### 3a. Laporan > Anak - Gizi (14)

| # | Laporan | Path | Jenis | Filter | Keluaran | Export | Volume | Catatan |
|---|---|---|---|---|---|---|---|---|
| 1 | Daftar Status Gizi | `Laporan/daftar_status_gizi_balita.html` | Daftar | kel, POSY, usia(19, termasuk "Bayi Baru Lahir Prematur", "6 Bulan", "6 Bulan 29 Hari"), status_gz(21: BB/U 4 kategori, TB/U 4, BB/TB 6, STUNTING, WASTING, WASTING dan STUNTING, KOMPOSIT, UNDERWEIGHT, UNDERWEIGHT NON WASTING), m, b, p, LILA(Ya), imd(Ya/Tidak), bulan, tahun [F] | 36 kolom [D] | ada: `Laporan/daftar_status_gizi_balita_print.html`, satu berkas HTML-xls untuk seluruh hasil (±7–9 MB, 30–60 dtk) [D] | 72.079 baris, 22 bulan [D] | 10 baris per halaman di layar. Satu-satunya laporan dengan z-score per anak. Filter `imd` hanya ada di laporan ini (dan bukan kolom), jadi IMD hanya bisa dipakai lewat filter Ya/Tidak. |
| 2 | Rekap Status Gizi | `Laporan/rkp_status_gizi_balita.html` | Rekap | kel, POSY, usia(16), m, b, p, bulan, tahun [F] | BB/U 5 kategori, TB/U 5, BB/TB 7 (termasuk Outlier), Stunting, Wasting, Underweight [D] | tidak ada [D] | 154 desa-bulan, 72.071 balita [D] | Sumber sheet `Laporan Puskesmas`. Dengan kel kosong keluar satu baris per desa. Filter m/b/p memungkinkan tabel 2×2 tanpa data per anak (bagian 5, A5). |
| 3 | Rekap Status Gizi per Desa | `Laporan/rkp_status_gizi_balita_desa.html` | Rekap | kel, usia(16), bulan, tahun [F] (tanpa POSY, m, b, p) | ? (dugaan: sama dengan #2, satu baris per desa) | ? | ? | Kemungkinan duplikat #2 dengan kel kosong. Cocokkan dulu sebelum dipakai. |
| 4 | Rekap Status Gizi & Usia | `Laporan/rkp_status_gizi_balita_usia.html` | Rekap | kel, b, p, bulan, tahun [F] | ? (dugaan: status gizi per kelompok umur) | ? | ? | Tanpa filter usia karena baris = kelompok umur [J]. Berguna untuk kurva stunting menurut umur (A10). |
| 5 | Rekap Status Gizi, Usia, & Jenis Kelamin | `Laporan/rkp_status_gizi_balita_usia_kelamin.html` | Rekap | kel, b, p, bulan, tahun [F] | ? (dugaan: #4 dipecah menurut JK) | ? | ? | Judul halaman tertulis "Rekap ... Status Gizi & Usia" (sama dengan #4), jadi perlu dibuktikan memang berbeda. |
| 6 | Daftar Insiden Stunting | `Laporan/daftar_insiden_stunting.html` | Daftar | kel, POSY, usia(16), bulan, tahun [F] | 30 kolom, semuanya ada di #1 (No sampai Naik Berat Badan) [diperiksa 19 Okt, header saja] | ada: `daftar_insiden_stunting_print.html` | Jan 2026 = 138 anak, cocok dengan Rekap Insiden (87 + 51). **Tidak perlu diunduh**: kolom subset #1; yang tidak ada di #1 hanya label insidennya, bisa dihitung sendiri dan dicocokkan dengan #7. | Definisi "insiden" (kemungkinan anak yang baru terdeteksi stunting dibanding pengukuran sebelumnya) harus dibaca di Buku Panduan. |
| 7 | Rekap Insiden Stunting | `Laporan/rkp_insiden_stunting.html` | Rekap | kel, POSY, usia(16), bulan, tahun [F] | desa × jenis kelamin (laki-laki, perempuan), baris JUMLAH [diverifikasi dari berkas] | ada (berkas .xls sudah diunduh sesi lain) | 10 berkas Jan–Okt 2026; tahun lain belum dicek | Total L+P per bulan 2026: Jan 138, Feb 108, Mar 57, Apr 74, Mei 41, Jun 116, Jul 191, Agu 42, Sep 70, Okt 0. Lonjakan Jul dan nol di Lampeji, Mumbulsari, Lengkong pada Agu cocok dengan artefak entri massal (dugaan, bagian 4 K8). |
| 8 | Daftar Balita Dengan Masalah Status Gizi | `Laporan/daftar_masalah_status_gizi_balita.html` | Daftar | kel, POSY, usia(16), status_gz(16 kategori "masalah", mis. BB tidak naik dengan BB normal, Underweight tanpa wasting/stunting, Gizi Kurang tanpa stunting, Gizi Buruk, STUNTING dan kombinasinya dengan gizi buruk/kurang/BB kurang/BB/TB normal), b, p, LILA, bulan, tahun [F] | 34 kolom, semuanya ada di #1 (termasuk Jml Vit A, KPSP, KIA) [diperiksa 19 Okt, header saja] | ada (tautan Export mengarah ke `daftar_status_gizi_balita_print.html`) | tergantung filter status_gz (bawaan = kategori pertama; Jan 2026: 671) | Judul halaman sama dengan #1 ("Daftar Anak Berdasarkan Status Gizi"). Kategori eksklusif ini berguna untuk beban ganda (A7). |
| 9 | Rekap Balita Dengan Masalah Status Gizi | `Laporan/rkp_status_gizi_balita_masalah.html` | Rekap | kel, POSY, usia(16), b, p, bulan, tahun [F] | ? | ? | ? | |
| 10 | Rekap Balita Dengan Masalah Status Gizi per Desa | `Laporan/rkp_status_gizi_balita_masalah_desa.html` | Rekap | kel, POSY, usia(16), bulan, tahun [F] | ? | ? | ? | Ada field POSY walau "per Desa". |
| 11 | Rekap Bayi Baru Lahir | `Laporan/rkp_bayi_baru_lahir.html` | Rekap | kel, POSY, kia_bayi_kecil(Ya/Tidak), bulan, tahun [F] | ? (dugaan: jumlah lahir, BBLR, PBLR, IMD) | ? | ? | Sumber tren BBLR/PBLR sebagai faktor hulu (A5). |
| 12 | Data Meninggal | `Laporan/daftar_meninggal.html` | Daftar | kel, POSY, usia(12), bulan, tahun [F] | ? | ? | ? (jumlah kecil dugaan) | Judul halaman "Daftar Balita Meninggal". Hanya deskriptif. |
| 13 | Rekap Sasaran Anak | `Laporan/rkp_sasaran_balita.html` | Rekap | kel, POSY, usia(18), bulan, tahun [F] | ? (dugaan: jumlah sasaran per kelompok umur, penyebut cakupan) | ? | ? | Penyebut cakupan pengukuran dan intervensi (A8). |
| 14 | Rekap Sasaran Anak Per Desa | `Laporan/rkp_sasaran_balita_desa.html` | Rekap | kel, usia(16), bulan, tahun [F] | ? | ? | ? | |

### 3b. Laporan > Anak - Tumbuh Kembang (14)

| # | Laporan | Path | Jenis | Filter | Keluaran | Export | Catatan |
|---|---|---|---|---|---|---|---|
| 15 | Daftar Ditimbang | `Laporan/daftar_ditimbang.html` | Daftar | kel, POSY, usia(13, sampai "60–72" dan "60–83 Bulan"), bulan, tahun [F] | ? | ? | Judul "Daftar Anak Ditimbang". Kelompok usia sampai 83 bulan menunjukkan modul prasekolah. |
| 16 | Daftar Tidak Ditimbang | `Laporan/daftar_tidak_ditimbang.html` | Daftar | kel, POSY, usia(11), bulan, tahun [F] | ? | ? | Judul "Daftar Anak Tidak Diukur". Pasangan #15 untuk menghitung anak terdaftar yang tidak terukur (D/S). |
| 17 | Pemantauan Pertumbuhan | `Laporan/rkp_pertumbuhan.html` | Rekap | kel, POSY, usia(13), m, bulan, tahun [F] | ? (dugaan: N/T, naik atau tidak naik BB) | ? | Rekap selain #2 yang punya filter MBG. |
| 18 | KOHORT | `Laporan/kohort.html` | ? | kel, POSY, usia(17, wajib pilih), bulan, tahun [F] | ? | ? | Kohort buatan situs. Bisa menghemat pekerjaan longitudinal bila definisinya jelas. |
| 19 | Analisa KOHORT | `Laporan/analisa_kohort.html` | Rekap | kel, POSY, usia(12), tahun [F] (tanpa bulan) | ? | ? | |
| 20 | Daftar Outlier | `Laporan/daftar_outlier.html` | Daftar | kel, POSY, usia(12), bulan, tahun [F] | ? | ? | Alat resmi untuk menemukan entri janggal (lihat bagian 4 K2). |
| 21 | Rekap Outlier | `Laporan/rkp_outlier.html` | Rekap | kel, usia(11), bulan, tahun [F] | ? | ? | |
| 22 | Daftar LiLA | `Laporan/daftar_lila_anak.html` | Daftar | kel, POSY, usia(10, mulai 6 bulan), LILA(Gizi Buruk, Gizi Kurang, Normal), bulan, tahun [F] | ? | ? | LiLA juga ada di #1 sebagai kolom. |
| 23 | Rekap LiLA | `Laporan/rkp_lila_anak.html` | Rekap | kel, POSY, usia(10), b, p, bulan, tahun [F] | ? | ? | |
| 24 | Perkembangan KIA | `Laporan/rkp_perkembangan_kia.html` | Rekap | kel, bulan, tahun [F] | ? | ? | Judul "Rekapitulasi Hasil Pemantauan Perkembangan KIA Balita". |
| 25 | Perkembangan KPSP | `Laporan/rkp_perkembangan_kpsp.html` | Rekap | kel, bulan, tahun [F] | ? | ? | Daftar per anak sudah ada sebagai kolom `KPSP` di #1. |
| 26 | Rekap Perkembangan | `Laporan/rkp_perkembangan_balita.html` | Rekap | kel, bulan, tahun [F] | ? | ? | |
| 27 | Daftar Pantau Tumbang | `Laporan/daftar_pantau_tumbang.html` | Daftar | kel, POSY, usia(2: "12–23 (ulang tahun 12 bulan)", "24–59 (ulang tahun 24, 36, 48, 60 bulan)"), jml_timbang(1–12), jml_ukur(1–12), jml_pantau(1–2), bulan (boleh kosong), tahun [F] | ? | ? | Mengukur kepatuhan pemantauan: berapa kali anak ditimbang dan diukur dalam setahun. Dugaan kuat [J]. |
| 28 | Daftar Kelas Ibu Balita | `Laporan/daftar_kelas_ibu_balita.html` | Daftar | kel, POSY, usia(2), jml_kelas(1, 2, 3, ≥4), bulan, tahun [F] | ? | ? | Kolom `Kelas Ibu Balita` juga ada di #1. |

### 3c. Laporan > Anak - Intervensi (13)

| # | Laporan | Path | Jenis | Filter | Catatan |
|---|---|---|---|---|---|
| 29 | Daftar Asi Eks. | `Laporan/daftar_asieks.html` | Daftar | kel, POSY, usia(2), recall(Ya, Tidak, Tidak Di Recall), bulan, tahun [F] | Pilihan "Tidak Di Recall" membuat penyebut tidak sama dengan jumlah anak. |
| 30 | Rekap Asi Eks. | `Laporan/rkp_asieks.html` | Rekap | kel, POSY, usia(2), recall(Ya, Tidak, Tidak Di Recall), bulan, tahun [F] | |
| 31 | Daftar MPASI | `Laporan/daftar_mpasi.html` | Daftar | kel, POSY, usia(2), intervensi(Mendapat/Tidak Mendapat), recall MPASI(Ya/Tidak), mpasi(YA/TIDAK), protein_hewani("Mengonsumsi telur, daging, ikan" YA/TIDAK), bulan, tahun [F] | Satu-satunya sumber protein hewani. Faktor risiko yang secara gizi paling masuk akal untuk stunting usia 6–23 bulan. |
| 32 | Rekap MPASI | `Laporan/rkp_mpasi.html` | Rekap | kel, POSY, usia(2), status_gz(20), intervensi, bulan, tahun [F] | Filter status_gz membuat tabel silang MPASI × status gizi agregat. |
| 33 | Daftar Imunisasi | `Laporan/daftar_imunisasi.html` | Daftar | kel, usia(11), jenis_imunisasi(14: IDL, HB-0, BCG, Polio 1–4, DPT-HB-Hib 1–3, IPV, Campak, DPT-HB-Hib Lanjutan, Campak Lanjutan), bulan, tahun [F] | Tanpa filter POSY. |
| 34 | Rekap Imunisasi | `Laporan/rkp_imunisasi.html` | Rekap | kel, usia(11), bulan, tahun [F] | |
| 35 | Daftar Vit. A | `Laporan/daftar_vita.html` | Daftar | kel, POSY, usia(6–11, 12–59), vita(Ya/Tidak), bulan(Februari, Agustus, Februari & Agustus), tahun [F] | Vitamin A hanya dua periode per tahun. Kolom `Jml Vit A` di #1 memberi jumlah dosis kumulatif. |
| 36 | Rekap Vit. A | `Laporan/rkp_vita.html` | Rekap | kel, POSY, bulan(Februari, Agustus), tahun [F] | |
| 37 | Daftar Taburia | `Laporan/daftar_taburia.html` | Daftar | kel, POSY, usia(11), kumulatif(Ya/Tidak), bulan, tahun [F] | |
| 38 | Rekap Taburia | `Laporan/rkp_taburia.html` | Rekap | kel, usia(11), bulan, tahun [F] | |
| 39 | Daftar Tindakan | `Laporan/daftar_tindakan.html` | Daftar | kel, POSY, usia(9), status_gz(21), bulan, tahun [F] | Judul "Daftar Riwayat Tindakan". Isi tindakan (PMT, rujukan, konseling) belum diketahui. |
| 40 | Rekap Tindakan | `Laporan/rkp_tindakan.html` | Rekap | kel, usia(9), status_gz(20), bulan, tahun [F] | |
| 41 | Rekap Sasaran Anak Prasekolah | `Laporan/rkp_sasaran_anak_prasekolah.html` | Rekap | kel, POSY, usia(2), bulan, tahun [F] | Di luar rentang balita. |

Kolom Keluaran, Export, Periode, dan Volume untuk #29–#41 semuanya `?`.

### 3d. Data Dashboard dan beranda (5)

| # | Laporan | Path | Filter | Catatan |
|---|---|---|---|---|
| 42 | Rekap Balita Bermasalah Gizi | `Laporan/rkp_balita_bermasalah.html` | bulan(Juni–Desember), tahun [F] | Tanpa filter desa. Pilihan bulan hanya 7, mungkin baru ada dari Juni (tahun yang mana belum diketahui). |
| 43 | Rekap Balita BB Tidak Naik (T) | `Laporan/rkp_balita_pmt/1.html` | bulan(7), tahun [F] | Menu menyebutnya "Rekap Balita T". |
| 44 | Rekap Balita BB Kurang | `Laporan/rkp_balita_pmt/2.html` | bulan(6), tahun [F] | |
| 45 | Rekap Balita Gizi Kurang | `Laporan/rkp_balita_pmt/3.html` | bulan(7), tahun [F] | |
| 46 | Beranda | `index_ppgbm.html` | bulan, tahun, tombol "Tampilkan Data" [F] | Delapan penghitung: Tidak Naik BB, Underweight (ZS < −2), Gizi Kurang (Tidak Stunting), Stunting, Menyimpang, Gizi Buruk, Bumil KEK, Bumil Anemia. Isi belum dibaca. |

### 3e. Entry: daftar sasaran (hanya daftar dan form dibaca)

| Halaman | Path | Filter | Kolom tabel [F] | Catatan |
|---|---|---|---|---|
| Daftar Balita | `Balita/daftar.html` | kel, POSY, usia(14), nama, nik, nik_ibu [F] | No, NIK, Nama, JK, Tgl Lahir, Nama Ortu, Prov, Kab/Kota, Kec, Puskesmas, Desa/Kel, Posyandu, Tindakan | Tabel langsung terisi saat halaman dibuka (10 baris, tidak dibaca). Tombol Export Excel: `balita/print_daftar_old`. Total ≈ 4.291–4.300 anak. **Ada filter NIK Ibu**, tetapi tidak ada kolom NIK Ibu di tabel. |
| Daftar Balita Pindah | `Balita/daftar_pindah.html` | kel, POSY, usia(15), nik | ? | Anak yang pindah keluar (kehilangan follow-up). Jumlah belum dicek. |
| Daftar Balita Hapus (Recycle Bin) | `Balita/daftar_sampah.html` | kel, POSY, usia(15), nik | ? | Anak dihapus (duplikat atau salah entri). Jumlah belum dicek. |
| Data Balita NIK Dummy | `Balita/daftar_balita_nik_dummy.html` | kel, POSY, usia(15), nik | ? | Anak ber-NIK sementara. Jumlahnya menentukan seberapa banyak anak yang tidak bisa dilacak lintas bulan atau lintas dataset. |
| Permintaan Pindah (Masuk) | `Transfer/request_masuk.html` | tombol tolak/terima | No, Tipe, NIK, Nama, PKM Tujuan, Alasan, Tanggal Request, Status, Tindakan | Halaman aksi, hanya dilihat. Ada permintaan menunggu. Jangan diklik. |
| Daftar Ibu Hamil | `Bumil/daftar_bumil.html` | kel, POSY, status(Masih Hamil, Sudah Melahirkan, Sudah Melewati HPL, Abortus, Meninggal, Semua), bulan, tahun(3), nama, nik | ? | |
| Daftar Ibu | `Bumil/daftar_ibu.html` | kel, POSY, nik | ? | |
| Daftar Anak Prasekolah / SD | `Anak_prasekolah/daftar_anak_prasekolah.html`, `Anak_sekolah/daftar_anak_sekolah_sd.html` | wilayah/sekolah (36 sekolah), nama, nik | ? | Di luar balita. |

Halaman lain di Entry (Tambah Ibu Hamil, Cari by NIK, SMP/SMA, Ibu Nifas/Menyusui) tidak dibuka. Form Tambah Balita dibuka dan tidak dikirim.

### 3f. Rematri dan Bumil (di luar fokus balita; hanya dicek bentuk form)

| Laporan | Path | Filter | Catatan |
|---|---|---|---|
| Rekap Skrining Anemia Rematri | `Rematri_laporan/rkp_skrining_anemia_rematri.html` | tidak terbaca | Halaman kosong (tanpa judul, tanpa form) saat dibuka, diulang dua kali. |
| Rekap Status Gizi Rematri | `Rematri_laporan/rkp_status_gizi_rematri.html` | tidak terbaca | Halaman kosong. |
| Daftar TTD Rematri | `Rematri_laporan/daftar_ttd_rematri.html` | tidak terbaca | "An Error Was Encountered". |
| Rekap TTD Rematri | `Rematri_laporan/rkp_ttd_rematri.html` | kel, POSY, bulan, tahun | |
| Daftar Ukur Rematri | `Rematri_laporan/daftar_ukur_rematri.html` | kel, POSY, bulan, tahun | |
| Rekap TTD Rematri Per Sekolah | `Rematri_laporan/rkp_ttd_rematri_sekolah.html` | prov/kab/kec/pkm sekolah, jenjang, jenis(Sekolah, SLB, Madrasah, Pesantren, Sekolah Rakyat), sekolah(57 pilihan), bulan, tahun | |
| KOHORT IBU | `Bumil_laporan/kohort_bumil.html` | kel, POSY, mbg, tahun, bulan, jml_periksa(1–8, >8) | MBG berlaku juga untuk ibu hamil. |
| Daftar Pemeriksaan ANC | `Bumil_laporan/daftar_pemeriksaan_bumil_anc.html` | kel, POSY, mbg, tahun(3), bulan, nik | |
| Rekap 12T Ibu Bersalin | `Bumil_laporan/rkp_pemeriksaan_12t.html` | kel, tahun(2) | Judul menyebut Tahun 2026. |
| Daftar Ibu Hamil KEK | `Bumil/daftar_bumil_kek.html` | kel, POSY, status_intervensi (PMT lokal 2025), status_pemberian (PMT lokal 2026), bulan, tahun(7), nik | |
| Daftar Suplementasi Gizi | `Bumil_laporan/daftar_bumil_suplementasi_gizi.html` | kel, POSY, tahun(3), bulan, jenis(TTD, MMS), total dapat dan total minum (≥180, <180), nik | |
| Rekap Pemeriksaan HB | `Bumil_laporan/rkp_bumil_periksa_hb.html` | kel, bulan, tahun | |
| Rekap Sasaran Bumil | `Bumil_laporan/rkp_sasaran_bumil.html` | kel | |

Tidak dibuka: Daftar Pemeriksaan HB, Rekap Evaluasi/Pemantauan Anemia, Daftar Ibu Hamil Pemantauan ANC, Daftar Ibu Bersalin K6 dan 12T, Daftar Ibu Hamil Meninggal, Daftar Kantong Bersalin, Daftar Ukur Rematri By Sekolah, Daftar TTD Rematri By Sekolah.

## 4. Catatan kualitas data yang sudah diketahui

Dari dokumentasi proyek [D]:

- **K1. Posyandu kosong**: 818 anak (810 punya desa, 8 tanpa desa), terpusat di Mumbulsari (586), Lengkong (173), Lampeji (37). Naik dari 0–6 per bulan di 2025 menjadi 50–110 per bulan di 2026. Inilah penyebab selisih 810 balita antara baris posyandu dan baris Puskesmas. Analisis per desa aman memakai sheet `Laporan Puskesmas`; analisis per posyandu tidak.
- **K2. Entri massal diduga keliru**: Jan–Agu 2026 di Lampeji, Mumbulsari, Lengkong banyak anak berlabel TB/U "Outlier". Contoh Lampeji Jul 2026: 888 anak, semua bertanggal ukur 31 Jul 2026, tinggi median 67 cm untuk umur median 37 bulan, ZS TB/U −6,3 sampai −8,9, cara ukur "-". Angka stunting periode dan desa itu tidak boleh dipakai sebelum dikonfirmasi ke petugas entri.
- **K3. Nilai penanda dan salah satuan**: ZS TB/U = 1000, berat 3700 (kemungkinan gram), tinggi atau berat 0 pada sebagian baris.
- **K4. Tanggal ukur di luar bulan berkas**: 1–2 baris per bulan bertanggal 2021–2025.
- **K5. Okt 2026 belum final**: 20 baris di Daftar, insiden 0. Laporan dihitung saat diminta, sehingga angka bulan lama bisa berubah bila ada entri susulan.
- **K6. Koneksi server**: filter disimpan di sesi login, request harus berurutan, HTTP 500 muncul sendiri.

Temuan baru dari inventaris ini (semuanya perlu verifikasi, bukan kesimpulan):

- **K7. Lonjakan jumlah baris per bulan**. Rata-rata baris per bulan 2025 ≈ 2.880 (rentang 2.555–3.355); 2026 Jan–Sep ≈ 4.170 (rentang 3.998–4.255). Des 2025 → Jan 2026: 2.732 → 4.249 (+56%). Jumlah anak terdaftar saat ini ≈ 4.29 ribu, jadi pada 2026 hampir setiap anak terdaftar punya satu baris tiap bulan (93–99%). Dugaan: perubahan praktik pencatatan atau entri massal; belum dibuktikan. Akibatnya "cakupan pengukuran", penyebut prevalensi, dan tren 2025 vs 2026 tidak sebanding sampai alasannya jelas.
- **K8. Insiden stunting 2026 mengikuti artefak K2**: total insiden melonjak di Jul (191, dibanding 41–138 pada bulan lain) lalu 0 di Lampeji, Mumbulsari, Lengkong pada Agu (ketiganya 33–39 pada Jul). Pola ini cocok dengan penandaan massal pada 31 Jul. Dugaan saja. Jangan memakai insiden dari situs sebelum K2 dibersihkan.
- **K9. Anak ber-NIK dummy**: ada menu khusus "NIK Dummy" dan opsi "tanpa NIK" saat registrasi. Jumlahnya belum diketahui. Anak seperti ini tidak bisa dilacak andal lintas bulan atau ditautkan ke register MTBS.
- **K10. Anak pindah dan dihapus**: ada daftar Pindah dan Recycle Bin. Kehilangan follow-up dan duplikat belum terukur.
- **K11. Struktur variabel**: tidak ada data sosial ekonomi atau lingkungan (bagian 2). BB lahir dan panjang lahir diisi saat registrasi, mungkin dari buku KIA atau ingatan orang tua; kelengkapannya belum diperiksa.
- **K12. Definisi tidak terdokumentasi di luar Buku Panduan**: Outlier (kemungkinan batas WHO: |z| besar), insiden stunting, "Naik Berat Badan", dan sumber standar (WHO 2006 vs Permenkes 2/2020) belum terkonfirmasi.
- **K13. Kekacauan antarmuka**: judul halaman ganda (#1 dan #8; #4 dan #5), tiga halaman Rematri kosong atau error, dropdown tahun selalu 2015–2026 padahal data belum tentu ada, kelompok umur berbeda antar laporan (9 sampai 19 pilihan). Pastikan filter `usia` sama sebelum membandingkan dua laporan.
- **K14. Tombol Export tidak seragam**: Rekap Status Gizi tidak punya, Daftar Status Gizi dan Rekap Insiden punya, Daftar Balita punya. Sisanya belum dicek.

## 5. Analisis yang layak (diurutkan menurut nilai untuk riset ini)

Penilaian: **Nilai** = seberapa langsung menjawab empat luaran yang diminta dan sekaligus kuat secara metodologis. **Status** = Layak, Layak bersyarat (ada syarat yang harus dipenuhi dulu), atau Tidak layak (bagian 6).

Usulan rumusan pertanyaan, dari yang paling pasti terjawab:

1. (Primer) Berapa beban stunting, wasting, dan underweight per desa di wilayah Puskesmas Mumbulsari, dan bagaimana tren bulanannya Jan 2025 sampai Sep 2026?
2. (Sekunder) Faktor program dan biologis apa (BBLR, PBLR, jenis kelamin, umur, KPSP, Kelas Ibu, Vit A, MPASI, MBG) yang berasosiasi dengan stunting dan wasting, dan seberapa sering anak masuk, bertahan, atau keluar dari status stunting?
3. (Eksploratori) Adakah perbedaan perubahan z-score antara anak yang menerima MBG dan yang tidak?
4. (Kualitas data) Seberapa valid data SigiziKesga untuk pemantauan gizi, dan di mana letak masalahnya? Ini temuan yang sah untuk KOAS IKM, dan bagian dari pertanyaan 1–3 yang harus dijawab lebih dulu.
5. (Pendukung proyek utama) Bagaimana prevalensi stunting dari register MTBS (42,5%) dibanding prevalensi di posyandu, dan apakah anak MTBS yang stunting sudah terdeteksi di posyandu?

### A1. Prevalensi stunting, wasting, underweight per desa (nilai tinggi, layak setelah pembersihan)

- **Data**: sheet `Laporan Puskesmas` (7 desa × 22 bulan) sebagai dasar. Konfirmasi dengan Daftar Status Gizi yang sudah dibersihkan (K2, K3).
- **Metode**: persen dengan interval Wilson per desa per bulan, per semester, dan periode gabungan; penyebut = anak dengan status terhitung (keluarkan Outlier, nyatakan eksplisit); bandingkan antardesa dengan uji proporsi atau regresi binomial dengan efek desa; tampilkan juga jumlah anak (n) setiap sel.
- **Keterbatasan**: populasi = anak terdaftar yang diukur di posyandu, bukan sampel acak penduduk, sehingga tidak sebanding langsung dengan SSGI atau SKI. Jan–Agu 2026 di tiga desa terkontaminasi (K2). Okt 2026 tidak final. Anak yang sama muncul tiap bulan, jadi "prevalensi bulanan" bukan estimasi independen; untuk periode gabungan hitung per anak (misal pengukuran terakhir) agar tidak menghitung ganda.

### A2. Tren bulanan dan musiman (nilai tinggi, layak terbatas)

- **Data**: seri bulanan dari A1 (22 titik, 21 bila Okt dibuang).
- **Metode**: grafik tren dengan CI, regresi logistik/binomial dengan tren linier dan efek bulan kalender, perbandingan Jan–Sep 2025 vs Jan–Sep 2026 (selisih tahunan), dan titik Februari serta Agustus (bulan penimbangan dan Vit A).
- **Keterbatasan**: hanya 1,75 siklus tahunan, jadi pola **musiman tidak bisa dipastikan**, hanya "terlihat" atau "tidak terlihat". Perubahan pencatatan awal 2026 (K7) bisa meniru tren turun atau naik. Peramalan atau model deret waktu formal tidak layak (bagian 6).

### A3. Penelusuran longitudinal per anak (nilai tinggi, layak bersyarat)

- **Syarat**: NIK dipseudonimkan (mis. HMAC-SHA256 dengan garam rahasia yang disimpan di luar repo), anak NIK dummy dikeluarkan atau ditandai (K9), K2 sampai K4 dibersihkan.
- **Data**: Daftar Status Gizi 22 bulan: NIK pseudonim, JK, tanggal lahir, tanggal ukur, tinggi, berat, cara ukur, ZS, kategori.
- **Keluaran**: (a) kohort anak tidak stunting pada pengukuran pertama → waktu sampai stunting pertama (Kaplan–Meier, Cox); (b) matriks transisi status antar bulan (stunting bertahan, pulih, atau baru); (c) lintasan HAZ menurut umur (model campuran dengan efek acak anak); (d) berapa anak yang tidak punya cukup pengukuran.
- **Keterbatasan**: left truncation (anak masuk pada umur berbeda), interval pengukuran tidak teratur, galat pengukuran tinggi 0,5–1 cm cukup untuk membuat perubahan HAZ palsu, pergantian cara ukur (berbaring ke berdiri) di 24 bulan, regresi ke rata-rata, anak pindah atau keluar. Hasil sensitif terhadap kebersihan data.

### A4. Hitung ulang z-score WHO 2006 dan bandingkan dengan klasifikasi situs (nilai tinggi sebagai langkah kualitas, layak, murah)

- **Data**: tanggal lahir, tanggal ukur, JK, berat, tinggi, cara ukur dari Daftar Status Gizi. Proyek sudah punya `skrip/zscore_mtbs.R` (paket R `anthro`), tinggal diadaptasi.
- **Metode**: hitung HAZ, WAZ, WHZ; cocokkan dengan kolom `ZS TB/U`, `ZS BB/U`, `ZS BB/TB` dan kategori situs; ukur kesepakatan (kappa), tabel reklasifikasi, pemeriksaan flag batas biologis WHO (HAZ < −6 atau > +6, WAZ < −6 atau > +5, WHZ < −5 atau > +5); periksa apakah umur dihitung dari tanggal yang benar.
- **Manfaat**: menjadi alat pembersih (menandai entri janggal K2 dan K3) dan hasil tersendiri tentang validitas aplikasi.
- **Keterbatasan**: bila situs memakai tabel selain WHO 2006 atau pembulatan umur berbeda, ketidaksepakatan kecil tidak berarti salah. Pastikan sumber standar dari Buku Panduan (K12).

### A5. Faktor yang bisa dikaitkan dengan stunting dan wasting (nilai tinggi, layak sebagai asosiasi)

- **Faktor yang sudah ada per anak**: JK, umur, BBLR (turunan `BB Lahir`), PBLR (turunan `TB Lahir`), LiLA, `Naik Berat Badan`, `Jml Vit A`, `KPSP`, `KIA`, `Kelas Ibu Balita`, `MBG`.
- **Faktor yang butuh laporan tambahan**: IMD (filter `imd` di Daftar Status Gizi, satu query tambahan per bulan), ASI eksklusif, MPASI dan protein hewani, imunisasi, Taburia, tindakan. Semuanya laporan Daftar terpisah yang harus diekspor lalu digabung lewat NIK pseudonim (biaya besar).
- **Jalur murah tanpa data per anak**: Rekap Status Gizi (dan Rekap Status Gizi & Usia) dengan filter `b`, `p`, `m` = Ya atau Tidak dan `kel` kosong menghasilkan tabel 2×2 per desa per bulan (22 bulan × 6 filter = 132 request, ±20 menit). Cukup untuk rasio prevalensi kasar BBLR/PBLR/MBG terhadap stunting.
- **Metode per anak**: regresi Poisson/binomial dengan galat baku robust terklaster per anak (atau GEE), outcome stunting dan wasting, model univariat lalu multivariat disesuaikan umur, JK, desa, bulan.
- **Keterbatasan**: tanpa variabel sosial ekonomi, residual confounding besar. Confounding by indication (anak yang BB-nya tidak naik justru mendapat intervensi), reverse causation, healthy-participant bias (anak yang hadir KPSP atau Kelas Ibu mungkin lebih sehat). `Jml Vit A` bergantung umur, wajib disesuaikan umur. BB lahir bisa kosong atau 0. Hasil hanya asosiasi, tidak kausal.

### A6. Evaluasi MBG (nilai sedang, layak eksploratori dan bersyarat)

- **Syarat**: cek dulu kapan penerima MBG pertama muncul per desa, berapa anak per bulan, dan apakah pola penerima acak atau terpusat di desa tertentu. Ini bisa dilihat murah dari Rekap Status Gizi dengan `mbg=Ya`, `kel` kosong (44 request untuk Ya dan Tidak).
- **Metode bila datanya memadai**: perubahan z-score per anak sebelum dan sesudah bulan MBG pertama (efek tetap anak, studi kejadian), difference-in-differences antar desa yang mulai berbeda waktu, atau perbandingan anak menerima vs tidak yang dicocokkan umur dan status awal.
- **Keterbatasan**: MBG di sini hanya penanda biner "menerima bulan ini", tanpa dosis atau mutu. Paparan paling lama < 22 bulan dan kemungkinan jauh lebih pendek, padahal HAZ lambat berubah (WHZ dan WAZ lebih responsif). Seleksi penerima tidak acak. Perubahan pencatatan 2026 (K7) tumpang tindih dengan waktu MBG. Hasilnya harus ditulis sebagai asosiasi eksploratori, bukan dampak program.

### A7. Beban ganda dan komposit kegagalan antropometri (nilai sedang, layak, murah)

- **Data**: kategori eksklusif dari Daftar atau Rekap Masalah (#8–#10): stunting + gizi buruk/kurang, underweight tanpa wasting, "KOMPOSIT" (wasting, stunting, underweight).
- **Metode**: prevalensi komposit dan irisan per desa dan umur, diagram Venn atau tabel irisan.
- **Keterbatasan**: definisi kategori situs harus dikonfirmasi; wasting dan stunting bersamaan lebih sensitif terhadap galat berat/tinggi.

### A8. Cakupan layanan dan intervensi (nilai sedang sampai tinggi untuk evaluasi kinerja Puskesmas, layak)

- **Data**: Rekap Sasaran (penyebut), Rekap Pemantauan Pertumbuhan, Rekap Vit A (Feb dan Agu), Rekap ASI Eks, MPASI, Imunisasi, Taburia, Tindakan, Perkembangan KIA/KPSP, Daftar Ditimbang vs Tidak Ditimbang, Daftar Pantau Tumbang (kepatuhan penimbangan dan pengukuran), Daftar Kelas Ibu Balita.
- **Metode**: proporsi dengan CI per desa dan bulan; alur layanan ("cascade"): anak bermasalah terdeteksi → mendapat tindakan → pulih bulan berikutnya (butuh A3 untuk bagian pulih).
- **Keterbatasan**: penyebut = anak terdaftar, bukan proyeksi penduduk; cakupan bisa kurang atau lebih dari 100% jika registrasi tidak lengkap. K7 membuat cakupan 2025 dan 2026 tidak sebanding. Daftar tindakan hanya menyatakan yang tercatat; "tidak tercatat" bukan "tidak dilakukan".

### A9. Kelengkapan dan indikator kualitas data (nilai tinggi sebagai temuan dan prasyarat, layak, murah)

- **Indikator**: kelengkapan TB/PB, BB lahir, TB lahir, LiLA, KPSP, Posyandu, Desa; heaping digit pada tinggi (angka .0 dan .5); SD dari HAZ, WAZ, WHZ (acuan kasar: HAZ ≈ 1,1–1,3, WAZ dan WHZ ≈ 1; SD jauh di atas itu menandakan masalah); proporsi flag biologis; ketepatan tanggal (pengukuran di luar bulan, tanggal menumpuk di hari yang sama); NIK ganda atau dummy; perbandingan Rekap vs Daftar. Sebagian sudah dikerjakan oleh `skrip/audit_daftar_status_gizi.py`.
- **Keluaran**: tabel kualitas per desa dan bulan, dan daftar tindak lanjut ke petugas entri (tanpa identitas anak di berkas yang dibagikan).

### A10. Kurva stunting menurut umur dan jenis kelamin (nilai sedang, layak, murah)

- **Data**: Rekap Status Gizi & Usia, dan Usia & Jenis Kelamin (#4, #5), 22 request.
- **Metode**: prevalensi stunting dan wasting per kelompok umur dan JK; dipakai untuk menentukan jendela usia paling rawan.
- **Keterbatasan**: isi laporan #4 dan #5 belum dilihat (apakah benar berbeda). Pergeseran cara ukur pada 24 bulan bisa menambah lompatan.

### A11. Perbandingan dengan register MTBS (nilai tinggi untuk proyek utama, layak bersyarat)

- **Syarat**: NIK register MTBS tersedia dan valid; pengguna menyetujui penautan dua dataset secara lokal dengan NIK pseudonim yang sama.
- **Metode**: hitung berapa persen anak di register MTBS yang ada di SigiziKesga, status gizi mereka pada pengukuran posyandu terdekat sebelum kunjungan, dan apakah stunting 42,5% di MTBS lebih tinggi daripada di posyandu (bias seleksi anak sakit). Bisa juga mengecek apakah anak stunting di posyandu muncul di kunjungan sakit.
- **Keterbatasan**: sebagian NIK salah atau dummy; selang waktu antara kunjungan MTBS dan pengukuran posyandu; sampel MTBS bukan sampel penduduk.

### A12. Penelusuran kembali insiden stunting dan pemulihan dari data sendiri (nilai sedang, layak bersyarat)

- **Syarat**: A3 selesai dan definisi insiden situs sudah dibaca dari Buku Panduan. Bandingkan hitungan sendiri dengan Rekap Insiden Stunting (per desa × JK, hanya 2026 yang sudah diunduh; tahun 2025 belum dicek).
- **Keterbatasan**: lihat K8.

### A13. Peta atau visualisasi per desa (nilai rendah sampai sedang, layak sebagai penyajian)

- Peta koroplet 7 desa memakai batas administrasi BPS (data luar). Hanya visualisasi, bukan inferensi spasial.

### A14. Deskripsi bayi baru lahir dan kematian (nilai rendah sampai sedang, layak deskriptif)

- Rekap Bayi Baru Lahir (BBLR, PBLR, KIA bayi kecil per desa dan bulan) untuk tren faktor hulu; Data Meninggal hanya dihitung jumlahnya per desa dan tahun dengan jumlah kecil dilaporkan sebagai angka, bukan persen.
- **Keterbatasan**: jumlah kecil, sel < 5 sebaiknya digabung atau ditekan di laporan.

### Rangkuman prioritas

| Urutan | Analisis | Nilai | Biaya data | Status |
|---|---|---|---|---|
| 1 | A9 Kelengkapan dan kualitas | tinggi | rendah (data sudah ada) | Layak |
| 2 | A4 Hitung ulang z-score WHO 2006 | tinggi | rendah | Layak |
| 3 | A1 Prevalensi per desa | tinggi | rendah | Layak setelah K2 |
| 4 | A2 Tren bulanan dan musiman | tinggi | rendah | Layak terbatas |
| 5 | A3 Longitudinal per anak | tinggi | sedang (sudah ada, butuh pembersihan) | Layak bersyarat |
| 6 | A5 Faktor risiko | tinggi | sedang (rekap 2×2) sampai tinggi (ekspor per anak) | Layak sebagai asosiasi |
| 7 | A11 Tautan ke register MTBS | tinggi untuk proyek utama | rendah | Layak bersyarat |
| 8 | A8 Cakupan layanan | sedang–tinggi | sedang (banyak rekap) | Layak |
| 9 | A6 MBG | sedang | rendah–sedang | Layak eksploratori |
| 10 | A7, A10, A12, A13, A14 | sedang–rendah | rendah | Layak |

## 6. Analisis yang tidak layak dan alasannya

- **Estimasi prevalensi populasi kecamatan atau generalisasi ke seluruh balita Mumbulsari**: tidak layak. Data berasal dari anak terdaftar yang diukur di posyandu, bukan sampel acak, dan cakupan sebenarnya tidak diketahui (K7, K9, K10).
- **Penentu sosial ekonomi dan lingkungan** (pendapatan, pendidikan ibu, sanitasi, air, paritas, jarak lahir, infeksi): tidak layak, variabelnya tidak ada di situs (bagian 2).
- **Klaim kausal efek MBG atau intervensi**: tidak layak. Penerima tidak acak, tidak ada dosis, paparan pendek, dan pencatatan berubah di waktu yang sama. Hanya asosiasi eksploratori (A6).
- **Analisis per posyandu atau pemetaan klaster kecil**: tidak layak. Angka per posyandu kecil dan tidak stabil (keputusan peneliti), 818 anak tanpa posyandu, dan hanya 7 desa untuk deteksi klaster.
- **Korelasi ekologis antar desa** (mis. KEK ibu hamil per desa vs stunting per desa): tidak layak sebagai inferensi, hanya 7 titik dan rentan ekologi palsu.
- **Peramalan dan model deret waktu formal dengan musiman**: tidak layak, 22 titik dan kurang dari dua siklus.
- **Menautkan ibu hamil ke anak lewat Nama Ortu**: tidak layak. Nama bukan identitas unik dan menambah risiko privasi. Bisa dipertimbangkan hanya bila sebuah ekspor memuat NIK Ibu (filter `nik_ibu` ada, kolomnya belum terlihat).
- **Memakai angka Jan–Agu 2026 di Lampeji, Mumbulsari, Lengkong sebelum dikonfirmasi**, dan **Okt 2026**: tidak layak sampai dibersihkan atau final.
- **Memakai insiden stunting situs sebagai hasil** sebelum K8 selesai: tidak layak.
- **Analisis Rematri, Bumil, anak sekolah**: di luar populasi balita. Hanya relevan sebagai konteks hulu, dan tiga halaman Rematri tidak bisa dibuka.
- **Analisis sebelum 2025**: belum bisa dinilai karena tahun data paling awal belum dicek.

## 7. Pertanyaan terbuka untuk peneliti

1. Mana pertanyaan primer? Usulan: 1 (beban dan tren per desa), 2 sekunder, 3 eksploratori, 4 sebagai syarat, 5 bila register MTBS bisa ditautkan.
2. Populasi dan penyebut: seluruh anak terdaftar, atau hanya yang terukur per bulan? Apa arti lonjakan baris awal 2026 (K7): perubahan cara entri, entri massal, atau registrasi baru? Perlu ditanyakan ke petugas entri.
3. Periode analisis: Jan 2025 sampai Sep 2026 (Okt dibuang)? Apakah ada data sebelum 2025 yang perlu diambil untuk pembanding?
4. Perlakuan Jan–Agu 2026 di Lampeji, Mumbulsari, Lengkong: dikeluarkan, dikoreksi, atau menunggu konfirmasi petugas?
5. Boleh membuka Buku Panduan (butuh login, berarti mengunduh PDF) untuk definisi Outlier, insiden, "Naik BB", dan standar z-score?
6. Standar klasifikasi yang dipakai di laporan: WHO 2006 atau Permenkes 2/2020; ambang BBLR (< 2.500 g) dan PBLR (< 48 cm)?
7. Boleh mengekspor laporan Daftar tambahan (ASI Eks, MPASI, Imunisasi, Vit A, Taburia, Tindakan, Kelas Ibu, Pantau Tumbang, LiLA)? Biaya kira-kira 22 bulan × beberapa laporan × 30–60 dtk, dan tiap ekspor berisi identitas anak.
8. MBG: kapan mulai di tiap desa, dan apa arti "menerima MBG bulan ini" di entri (diberi, diterima, atau sasaran)?
9. Boleh menautkan register MTBS dan SigiziKesga dengan NIK pseudonim yang sama, secara lokal?
10. Apakah anak ber-NIK dummy, pindah, dan di Recycle Bin dikeluarkan atau dihitung? Perlu jumlahnya dulu (bagian 8, langkah 4).
11. Dokumen izin dan etik: apakah ada surat izin tertulis penggunaan data Puskesmas atau Dinkes, dan status persetujuan etik atau pernyataan pengecualian? Laporan akan menyebut nama desa; apakah itu diizinkan?
12. Baris `Posyandu` kosong (818 anak): diminta dilengkapi petugas, atau cukup dianalisis sampai desa?

## 8. Rencana melengkapi inventaris (setelah pengguna menyatakan unduhan selesai)

Prosedur aman: satu request pada satu waktu, jeda 2–3 dtk, ulang hingga 3 kali bila HTTP 500, tidak mengubah apa pun, tidak membaca atau menyalin baris data per anak (hanya judul kolom, "Jumlah Data", dan keberadaan tautan Export).

1. **Tahun data paling awal**: Rekap Status Gizi per Desa (#3, kecil) pada Januari 2024, 2023, ..., sampai nol baris (maks 10 request). Ulangi untuk Daftar Status Gizi hanya bila rekap ada isinya.
2. **Keluaran tiap laporan**: satu Cari Data per laporan #3–#45 untuk satu bulan contoh (mis. Agu 2025 dan Agu 2026), catat judul kolom, "Jumlah Data", tombol Export dan alamatnya. Sekitar 45 request, ±10 menit. Untuk laporan Daftar cukup lihat hitungan dan header halaman pertama; jangan membaca baris.
3. **Pastikan #3 vs #2, #4 vs #5** apakah berbeda isinya (tabel silang saja).
4. **Hitungan agregat murah**: jumlah di Daftar Balita (default, Pindah, Recycle Bin, NIK Dummy) tanpa melihat baris; Rekap Status Gizi dengan `mbg`, `bblr`, `pblr` = Ya/Tidak untuk 22 bulan; Rekap Sasaran Anak per Desa; Rekap Bayi Baru Lahir; Rekap Insiden Stunting 2025.
5. **Rekap intervensi** (#30, #32, #34, #36, #38, #40, #24, #25, #26): satu tahun penuh dulu untuk melihat apakah terisi.
6. **Daftar per anak tambahan**: hanya setelah pertanyaan terbuka 7 dijawab dan A5 membutuhkannya.

## 9. Cara situs bekerja (ringkas, dari dokumentasi proyek)

Form laporan adalah POST ke alamat halaman yang sama. Laporan Daftar berhalaman 10 baris dan punya Export Excel (`..._print.html`) yang menghasilkan seluruh hasil filter terakhir dalam satu berkas HTML bergaya .xls. Filter disimpan di sesi server, jadi dua pengguna atau dua tab dengan login yang sama saling menimpa filter. Server membalas HTTP 500 jika banyak request datang bersamaan. Browser pane aplikasi memblokir koneksi ke localhost, sehingga data tidak bisa dikirim dari halaman ke server lokal.
