# Mini Riset Stunting Puskesmas Mumbulsari, 2024–2026

Repositori ini berisi kode dan hasil agregat dari analisis data rutin pengukuran balita di wilayah kerja Puskesmas Mumbulsari, Kabupaten Jember. Data berasal dari aplikasi SigiziKesga (modul e-PPGBM) dan mencakup Januari 2024 sampai September 2026. Analisis ini dikerjakan sebagai mini riset pada Kepaniteraan Ilmu Kesehatan Masyarakat, Fakultas Kedokteran Universitas Jember, oleh Thalia Anisya Dewi dan Fitranda Kusyanto Taslim.

Pertanyaan awalnya sederhana: berapa prevalensi stunting, wasting, dan underweight di tujuh desa wilayah Puskesmas, bagaimana trennya, dan faktor apa yang berhubungan dengannya (berat dan panjang lahir rendah, jenis kelamin, umur). Di tengah pengerjaan muncul pertanyaan kedua: seberapa jauh data rutin ini bisa dipercaya. Tinggi badan banyak yang dibulatkan, sebagian desa hanya mengisi satu tanggal ukur untuk seluruh bulan, dan angka di beberapa desa berubah drastis dari satu bulan ke bulan berikutnya. Karena itu sebagian besar skrip di sini mengerjakan pemeriksaan kualitas data, dan semua hasil prevalensi dihitung ulang pada beberapa skenario pembersihan.

## Data tidak ada di repo ini

Data per anak memuat nama, NIK, dan nomor rekam medis, sehingga tidak diunggah. Yang ada di repo hanya hasil agregat pada tingkat desa, bulan, atau kelompok umur. Skrip yang membaca data per anak tidak bisa dijalankan tanpa data sumber, tetapi kodenya tetap bisa dibaca untuk memeriksa cara kerjanya. Berkas yang dikecualikan tercantum di `.gitignore`: data sumber, data bersih per anak, rekap per posyandu, dan laporan Word atau PDF.

## Metodologi singkat

Ini adalah analisis data sekunder dari catatan rutin. Populasinya 108.322 pengukuran dari 6.312 balita (0–59 bulan) di tujuh desa. Tidak ada sampling: semua pengukuran dianalisis, kecuali baris yang tidak masuk akal secara biologis atau administratif (lihat "flag keras" di bawah), sehingga tersisa 105.600 pengukuran.

**Outcome dan faktor risiko.** Stunting didefinisikan sebagai TB/U di bawah −2 SD, wasting sebagai BB/TB di bawah −2 SD, dan underweight sebagai BB/U di bawah −2 SD, sesuai Permenkes 2/2020 yang mengacu pada standar pertumbuhan WHO 2006. Faktor risiko yang dianalisis adalah BBLR (berat lahir di bawah 2.500 g), PBLR (panjang lahir di bawah 48 cm), jenis kelamin, dan kelompok umur.

**Pembersihan data.** NIK diganti dengan ID acak (HMAC-SHA256 dengan garam yang hanya disimpan lokal), lalu nama, alamat, dan tanggal lahir dibuang. Data yang bermasalah ditandai, tidak dihapus. Ada dua jenis tanda. Flag keras (z-score penanda, tinggi atau berat nol, nilai mustahil, NIK ganda dalam satu bulan, umur di luar 0–59 bulan) mengeluarkan baris dari semua analisis. Flag lunak (desa-bulan dengan banyak z-score outlier, desa-tahun dengan penumpukan digit tinggi, satu tanggal ukur untuk banyak anak) tidak membuang baris, tetapi dipakai untuk membentuk skenario sensitivitas.

**Skenario sensitivitas.** Karena tidak bisa dipastikan di mana saja masalah kualitas data berada, semua hasil dihitung pada empat himpunan data. S0 adalah semua baris tanpa flag keras. S1 membuang tiga desa yang pola datanya berubah pada Januari–September 2026 (Lampeji, Mumbulsari, Lengkong). S2 hanya memakai desa-tahun dengan penumpukan digit rendah (kurang dari 70%). S3 membuang desa-bulan yang anomali. Jika sebuah temuan hanya muncul di satu skenario, temuan itu tidak dianggap kokoh.

**Metode statistik.**
- Prevalensi dihitung dari seluruh pengukuran anak-bulan. Karena anak yang sama diukur berulang, interval kepercayaan memakai bootstrap klaster per anak (500 ulangan), bukan rumus binomial biasa.
- Perbandingan antar desa, jenis kelamin, dan umur memakai uji chi-kuadrat pada satu pengukuran acak per anak per tahun, supaya sampel yang diuji saling bebas.
- Tren bulanan diuji dengan Mann-Kendall dan kemiringan Sen, ditambah regresi segmented dengan titik patah Januari 2026.
- Faktor risiko dianalisis dengan regresi logistik pada anak-bulan, disesuaikan jenis kelamin, umur, dan efek tetap desa × tahun, dengan galat baku robust klaster per anak. Efek tetap desa × tahun membuat anak hanya dibandingkan dengan anak lain di desa dan tahun yang sama, sehingga artefak pencatatan yang seragam dalam satu desa-tahun tidak ikut terbaca sebagai faktor risiko.
- Waktu hingga stunting pertama dianalisis dengan Kaplan-Meier dan uji log-rank, termasuk analisis sensitivitas dengan kejadian yang harus terkonfirmasi dua kali berturut-turut.
- Untuk menguji apakah pembulatan tinggi badan saja bisa menimbulkan penumpukan z-score di atas −2 SD, dilakukan simulasi dengan parameter LMS WHO 2006.

**Alat.** Python 3.12 untuk pembersihan, penandaan skenario, workbook, dan gambar; R 4.6 untuk prevalensi, tren, regresi, survival, dan simulasi; SPSS 27 untuk chi-kuadrat, cakupan, dan jumlah bulan terukur per anak. Analisis yang sama juga dikerjakan di Python dan dibandingkan dengan hasil R atau SPSS untuk memastikan tidak ada kesalahan implementasi. Selisihnya hanya pada batas interval bootstrap, karena generator angka acaknya berbeda.

### Alur analisis

```mermaid
flowchart TD
    A["Daftar Status Gizi bulanan<br/>SigiziKesga, 33 bulan, per anak"] --> B["Pseudonimisasi<br/>NIK diganti ID acak, identitas dibuang"]
    B --> C["Penandaan data<br/>flag keras dan flag lunak"]
    C --> D["Skenario sensitivitas S0–S3"]
    D --> E["Python: kontrol kualitas<br/>penumpukan digit, sebaran z-score, tanggal ukur"]
    D --> F["R: prevalensi dan IK bootstrap, tren,<br/>regresi logistik, Kaplan-Meier, simulasi"]
    D --> G["SPSS: chi-kuadrat, cakupan,<br/>bulan terukur per anak"]
    F --> H["Cek silang dengan hasil Python"]
    G --> H
    H --> I["Tabel agregat<br/>data/sigizi/analisis_rs/"]
    E --> I
    I --> J["Workbook Excel"]
    I --> K["Gambar dan tabel laporan"]
    K --> L["Laporan Word<br/>(tidak disertakan di repo)"]
```

Penjelasan tiap skrip ada di [`skrip/README.md`](skrip/README.md). Aturan pembersihan yang lengkap ada di [`data/sigizi/RENCANA_ANALISIS.md`](data/sigizi/RENCANA_ANALISIS.md).

## Isi folder

| Folder | Isi |
|---|---|
| `skrip/` | Semua kode: pembersihan data, audit kualitas, analisis di Python, R, dan SPSS, serta pembuatan workbook, gambar, dan laporan. Lihat [`skrip/README.md`](skrip/README.md). |
| `data/sigizi/analisis/` | Hasil analisis versi Python: tabel CSV, workbook Excel akhir, dan tabel LMS WHO (`who_lhfa_lms.csv`). |
| `data/sigizi/analisis_r/` | Hasil analisis versi R: tren, regresi segmen, Kaplan-Meier, bootstrap klaster, simulasi pembulatan. |
| `data/sigizi/analisis_rs/`, `analisis_spss/` | Hasil gabungan R dan SPSS yang dipakai untuk laporan, serta perbandingannya dengan hasil Python. |
| `data/sigizi/laporan/` | Gambar dan tabel yang dipakai di laporan, beserta catatan cara membangunnya. |
| `data/sigizi/rekap_*/` | Rekap agregat yang diunduh dari situs SigiziKesga (per desa, per jenis kelamin, insiden stunting, sasaran). |
| `referensi/` | Daftar pustaka (`.bib` dan ekspor Zotero) dan gaya sitasi (`.csl`). |
| `data/sigizi/RENCANA_ANALISIS.md` | Rencana analisis: aturan pembersihan, skenario, dan daftar analisis. |

## Format data sumber

Skrip mengharapkan data sumber di `data/sumber/` dengan tata letak berikut. Folder ini ada di `.gitignore` dan harus disediakan sendiri.

```
data/sumber/
├── sigizi_daftar_status_gizi_2026-10-19/
│   └── Daftar_Status_Gizi_YYYY-MM.xls     satu berkas per bulan, 2024-01 sampai 2026-09
├── anak_bersih/
│   ├── anak_bersih.csv                    keluaran bersihkan_data_anak.py
│   └── .garam                             garam HMAC untuk ID acak, dibuat otomatis, jangan dibagikan
└── anak_analisis/
    ├── anak_analisis.csv                  keluaran siapkan_data_spss_r.py
    └── sasaran.csv                        sasaran per desa-bulan, dibuat dari sasaran_cakupan_cek2024.xlsx
```

**Berkas ekspor `Daftar_Status_Gizi_YYYY-MM.xls`.** Ini adalah laporan "Daftar Status Gizi" dari SigiziKesga: satu baris per pengukuran per anak. Berkasnya sebenarnya HTML dengan ekstensi `.xls`. Kolom yang dibaca skrip: `NIK`, `JK`, `Tgl Lahir`, `BB Lahir`, `TB Lahir`, `Desa/Kel`, `Posyandu`, `Tanggal Pengukuran`, `Berat`, `Tinggi`, `Cara Ukur`, `LiLA`, `BB/U`, `ZS BB/U`, `TB/U`, `ZS TB/U`, `BB/TB`, `ZS BB/TB`, `Naik Berat Badan`, `Jml Vit A`, dan `MBG`.

**`anak_bersih.csv` dan `anak_analisis.csv`.** Satu baris adalah satu pengukuran seorang anak pada satu bulan. NIK sudah diganti `id_anak` (ID acak), dan nama, alamat, serta tanggal lahir tidak ada. Kolomnya terbagi menjadi beberapa kelompok:

| Kelompok | Kolom |
|---|---|
| Identitas dan waktu | `id_anak`, `bulan_berkas`, `tahun`, `bulan`, `desa`, `posyandu`, `jk`, `tgl_ukur`, `umur_bln` |
| Pengukuran | `berat`, `tinggi`, `lila`, `cara_ukur`, `bb_lahir_g`, `tb_lahir_cm`, `bblr`, `pblr`, `naik_bb`, `vit_a`, `mbg` |
| Z-score dan kategori | `zs_bbu`, `zs_tbu`, `zs_bbtb`, `kat_bbu`, `kat_tbu`, `kat_bbtb` |
| Outcome (0/1) | `stunting`, `stunting_berat`, `wasting`, `wasting_berat`, `underweight`, `gizi_lebih` |
| Flag kualitas | `f_keras` dan kolom `f_*` lainnya (`f_zs_penanda`, `f_nol`, `f_aneh`, `f_nik_ganda`, `f_umur_luar`, `f_tgl_luar`, `f_pos_kosong`, `f_nik_pendek`, `f_id_tak_konsisten`, `f_tbu_outlier`, `f_cara_ukur_salah`, `f_tgl_seragam`, `f_anomali_desabulan`, `f_heaping_tinggi`), serta `pct_heaping_desa_tahun` |
| Turunan untuk analisis | `kel_umur`, `t` (indeks bulan, 0 = Januari 2024), `s0`–`s3` (masuk skenario atau tidak), `pa_s0`–`pa_s3` (pengukuran acak terpilih per anak per tahun) |

`anak_analisis.csv` adalah `anak_bersih.csv` ditambah kolom turunan pada baris terakhir tabel di atas. Arti skenario, flag, dan outcome dijelaskan di sheet "Kamus" pada `data/sigizi/analisis/Analisis_Stunting_Mumbulsari.xlsx` dan di `data/sigizi/analisis/README.md`.

## Menjalankan ulang

Dengan data sumber di komputer lokal, analisis R dan SPSS beserta workbook dan bahan laporan dijalankan dengan:

```bash
sh jalankan_analisis_sigizi.sh
```

Skrip ini mengasumsikan `anak_bersih.csv` sudah dibuat oleh `skrip/bersihkan_data_anak.py`. Lokasi perangkat lunak bisa diatur lewat variabel lingkungan: `PYTHON`, `RSCRIPT`, dan `SPSS_PYTHON` (Python bawaan SPSS). Contoh:

```bash
RSCRIPT="/c/Program Files/R/R-4.6.1/bin/Rscript" sh jalankan_analisis_sigizi.sh
```

Tanpa data sumber, yang bisa dijalankan hanyalah pembuatan gambar laporan dari hasil agregat yang ada di repo:

```bash
python skrip/buat_gambar_laporan.py [folder_keluaran]
```

**Lingkungan.** Python 3.12 dengan paket yang dikunci di `requirements.txt` (`pip install -r requirements.txt`). R 4.6.1: analisis utama hanya memakai base R, sedangkan paket untuk alur MTBS lama (`anthro`, `openxlsx`, `readxl`, `ggplot2`) dipasang dengan `Rscript install_paket_r.R`. Analisis SPSS membutuhkan SPSS 27 dan dijalankan lewat `skrip/spss/jalankan_spss.py` (lokasi instalasi bisa diatur dengan variabel `SPSS_DIR`).

## Hal yang perlu diperhatikan

Beberapa baris di `desa_bulan.csv` dan tabel per desa memiliki jumlah anak yang kecil (n kurang dari 20, terendah 2). Persentase dari angka sekecil itu tidak stabil dan tidak boleh dibaca sebagai prevalensi desa tersebut. Prevalensi absolut dalam repo ini juga sebaiknya tidak dipakai sebagai angka resmi, karena adanya masalah kualitas data pada pencatatan rutin (lihat bagian metodologi).

## Lisensi

Kode (skrip dan sintaks) memakai lisensi MIT, lihat [`LICENSE`](LICENSE). Hasil agregat, tabel, dan gambar memakai CC BY 4.0, lihat [`LICENSE-HASIL.txt`](LICENSE-HASIL.txt). Keduanya boleh dipakai dan dimodifikasi dengan menyebut sumber; cara sitasi ada di [`CITATION.cff`](CITATION.cff).
