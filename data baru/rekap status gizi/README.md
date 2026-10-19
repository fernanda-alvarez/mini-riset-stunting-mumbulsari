# Rekap status gizi balita per desa, SigiziKesga (Puskesmas Mumbulsari)

Diambil 19 Okt 2026 dari laporan **Laporan > Anak - Gizi > Rekap Status Gizi** (`sigizikesga.kemkes.go.id/ppgbm/index.php/Laporan/rkp_status_gizi_balita.html`), akun Puskesmas Mumbulsari. Cakupan: 7 desa × 22 bulan (Jan 2025–Okt 2026). Usia 0–59 bulan, tanpa filter MBG/BBLR/PBLR. Data agregat, tidak memuat identitas anak.

## Dataset yang dipakai

**Untuk analisis tingkat desa atau Puskesmas: sheet `Laporan Puskesmas`** (154 baris = 7 desa × 22 bulan) di `rekap_status_gizi_per_posyandu.xlsx`. Keputusan peneliti: analisis cukup sampai tingkat desa, karena angka per posyandu kecil dan tidak stabil.

Sheet `Data` (per posyandu) **tidak** dipakai untuk total desa. Jumlah baris posyandu lebih kecil dari angka desa pada laporan Puskesmas.

## Berkas

| Berkas | Isi |
|---|---|
| `rekap_status_gizi_per_posyandu.xlsx` | Sheet `Data` (1.870 baris, per posyandu + baris `Jumlah Desa`), `Selisih`, `Laporan Puskesmas`, `Catatan`. |
| `rekap_status_gizi_per_posyandu.csv` | Isi sheet `Data`. |
| `_mentah/part_*.json`, `_mentah/puskesmas.json` | Hasil parse tabel dari server. Bahan pembuat Excel. Hasilnya dicek dengan checksum. |
| `../../skrip/bangun_rekap_status_gizi.py` | Membuat xlsx/csv dari `_mentah/` dan menjalankan pemeriksaan konsistensi. `python -I skrip/bangun_rekap_status_gizi.py "data baru/rekap status gizi/_mentah" "data baru/rekap status gizi"` |

Kolom (20 angka per baris): BB/U (Sangat Kurang, Kurang, Berat Badan Normal, Risiko Lebih, Outlier), TB/U (Sangat Pendek, Pendek, Normal, Tinggi, Outlier), BB/TB (Gizi Buruk, Gizi Kurang, Normal, Risiko Gizi Lebih, Gizi Lebih, Obesitas, Outlier), Stunting, Wasting, Underweight. Stunting = Sangat Pendek + Pendek; Wasting = Gizi Buruk + Gizi Kurang; Underweight = Sangat Kurang + Kurang. Ketiga kelompok (BB/U, TB/U, BB/TB) masing-masing berjumlah total balita.

## Temuan yang harus diketahui

1. **Selisih posyandu vs Puskesmas.** 55 dari 154 desa-bulan berbeda antara baris desa di laporan Puskesmas dan penjumlahan posyandu. Selalu satu arah (Puskesmas >= posyandu), total 810 dari 72.071 balita (~1,1%). Terpusat di Mumbulsari (19 bulan), Lengkong (16), Lampeji (12), membesar di 2026 (maks 73 balita, Mumbulsari Sep 2026). Rincian per desa-bulan di sheet `Selisih`.
2. **Penyebab selisih (TERJAWAB, 19 Okt 2026, dari data per anak "Daftar Status Gizi", lihat `../daftar status gizi/README.md`).** Selisih = anak yang kolom **Posyandu-nya kosong** di data entri: mereka dihitung di total desa tetapi tidak masuk baris posyandu mana pun. Rekonsiliasi 22 bulan: 72.079 anak di daftar per anak = 72.071 (laporan Puskesmas, semuanya punya desa) + 8 anak yang kolom Desa-nya juga kosong (tidak ada di rekap mana pun). 72.071 = 71.261 (posyandu valid, persis sama dengan jumlah semua baris posyandu di sheet `Data`) + 810 (desa ada, posyandu kosong). Tidak ada anak dengan posyandu di desa lain atau di luar daftar 78 posyandu. Posyandu kosong per desa (22 bulan): Mumbulsari 586 (4,3%), Lengkong 173 (2,1%), Lampeji 37, Suco 6, Karangkedawung 4, Tamansari 3, Kawangrejo 1. Jumlahnya naik: 0–6 anak/bulan sepanjang 2025, lalu 50 (Jan 2026) sampai 110 (Sep 2026) per bulan. Arti praktis: untuk total desa/Puskesmas pakai sheet `Laporan Puskesmas`; baris posyandu hanya untuk anak yang posyandunya terisi.
3. **Sebaran TB/U janggal** di Lampeji, Mumbulsari, Lengkong pada Jan–Agu 2026 (mis. Lampeji Jul 2026: TB/U Outlier 886 dari ~950 balita, Normal 4). Muncul di kedua tampilan, jadi berasal dari data sumber, bukan dari pengambilan. Dari data per anak: bukan karena tinggi badan kosong (tinggi terisi di hampir semua baris Outlier 2026). Pada Lampeji Jul 2026, seluruh 888 baris Outlier punya **tanggal ukur yang sama (2026-07-31)**, umur saat ukur median 37 bulan (4–61), tinggi median 67 cm, ZS TB/U −6,3 sampai −8,9, cara ukur "-". Itu tidak masuk akal secara biologis dan cocok dengan entri/impor massal bernilai keliru (dugaan, belum dibuktikan ke petugas entri). Di 2025 juga ada nilai penanda aneh (ZS TB/U = 1000 pada baris Outlier Mumbulsari Jan 2025) dan salah satuan (berat 3700 kg). Jangan pakai angka stunting desa-desa itu pada periode tersebut sebelum dibersihkan atau dikonfirmasi petugas.
4. **Okt 2026** masih berjalan, belum final.
5. Laporan dihitung langsung saat diminta (stempel "Data Tanggal" = jam pengambilan), jadi angka bulan lama bisa berubah kalau ada entri susulan.

## Cara kerja pengambilan (kalau perlu mengulang)

Tombol "Cari Data" adalah form POST biasa ke alamat halaman itu sendiri; tidak ada tombol export. Field: `prov=35, kab=3509, kec=3509090, kode_pusk=P3509090201, pkm=5335, kel=<kode desa 3509090001..07>, POSY=, usia=059, mbg=, bblr=, pblr=, bulan, tahun, cari=`. Dengan `kel` kosong, server mengembalikan satu baris per desa (laporan tingkat Puskesmas). Hasilnya tabel HTML `#simple-table` (2 baris header). Daftar posyandu: `Common/posy/?desa_id=<kode>&type=DESA`.

Pelajaran: kirim **berurutan dengan jeda** (~2 dtk). Tujuh request paralel membuat server membalas HTTP 500 (kosong), dan sesekali 500 muncul sendiri, jadi beri ulang otomatis. Satu request butuh ~7–9 detik. Dikerjakan dari sesi login yang sudah terbuka di browser; kredensial tidak disimpan di mana pun.
