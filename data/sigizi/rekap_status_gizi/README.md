# Rekap status gizi balita per desa, SigiziKesga

Rekap ini diambil pada 19 Oktober 2026 dari laporan **Laporan > Anak - Gizi > Rekap Status Gizi** di SigiziKesga, dengan akun Puskesmas Mumbulsari. Cakupannya tujuh desa selama 22 bulan (Januari 2025 sampai Oktober 2026), usia 0–59 bulan, tanpa filter MBG, BBLR, dan PBLR. Data berupa agregat dan tidak memuat identitas anak.

## Berkas yang disertakan dan yang tidak

Folder ini di repo hanya berisi dokumentasi. Berkas `rekap_status_gizi_per_posyandu.xlsx` dan data mentah hasil parsing tabel (`_mentah/`) tidak diunggah, karena rekap per posyandu berisi banyak sel kecil (0–3 anak) dengan nama posyandu. Skrip pembuatnya tetap tersedia: `skrip/bangun_rekap_status_gizi.py`.

Isi `rekap_status_gizi_per_posyandu.xlsx` (hanya di komputer lokal) adalah sheet `Data` (1.870 baris, per posyandu dan baris `Jumlah Desa`), `Selisih`, `Laporan Puskesmas` (154 baris, yaitu 7 desa × 22 bulan), dan `Catatan`.

Setiap baris memiliki 20 angka: BB/U (Sangat Kurang, Kurang, Berat Badan Normal, Risiko Lebih, Outlier), TB/U (Sangat Pendek, Pendek, Normal, Tinggi, Outlier), BB/TB (Gizi Buruk, Gizi Kurang, Normal, Risiko Gizi Lebih, Gizi Lebih, Obesitas, Outlier), lalu Stunting, Wasting, dan Underweight. Stunting adalah Sangat Pendek ditambah Pendek, wasting adalah Gizi Buruk ditambah Gizi Kurang, dan underweight adalah Sangat Kurang ditambah Kurang. Ketiga kelompok (BB/U, TB/U, BB/TB) masing-masing berjumlah total balita.

## Dataset yang dipakai untuk analisis

Analisis tingkat desa atau Puskesmas memakai sheet `Laporan Puskesmas`. Analisis dibatasi sampai tingkat desa karena angka per posyandu kecil dan tidak stabil. Sheet `Data` (per posyandu) tidak dipakai untuk total desa, sebab jumlah baris posyandu lebih kecil daripada angka desa pada laporan Puskesmas (lihat berikutnya).

## Catatan penting

1. **Selisih antara baris posyandu dan baris desa.** Pada 55 dari 154 desa-bulan, angka desa di laporan Puskesmas berbeda dari penjumlahan posyandu. Selisihnya selalu satu arah (Puskesmas lebih besar atau sama), total 810 dari 72.071 balita (sekitar 1,1%).
2. **Penyebab selisih.** Dengan membandingkan data per anak ("Daftar Status Gizi", lihat [`../daftar_status_gizi/README.md`](../daftar_status_gizi/README.md)), selisih itu berasal dari anak yang kolom **Posyandu**-nya kosong pada data entri: mereka dihitung di total desa tetapi tidak masuk baris posyandu mana pun. Tidak ada anak yang posyandunya berada di desa lain atau di luar daftar 78 posyandu. Konsekuensinya, untuk total desa atau Puskesmas pakai sheet `Laporan Puskesmas`, dan baris posyandu hanya mencerminkan anak yang posyandunya terisi.
3. **Sebaran TB/U yang janggal** pada beberapa desa dalam periode tertentu di 2026 muncul pada kedua tampilan laporan, jadi berasal dari data sumber dan bukan dari proses pengambilan. Rinciannya dibahas pada dokumentasi data per anak.
4. **Oktober 2026** masih berjalan dan belum final.
5. Laporan dihitung langsung saat diminta (stempel "Data Tanggal" menunjukkan jam pengambilan), sehingga angka bulan yang sudah lewat bisa berubah bila ada entri susulan.

## Membangun ulang

```bash
python -I skrip/bangun_rekap_status_gizi.py <folder _mentah> <folder keluaran>
```

Skrip ini membuat Excel dan CSV dari `part_*.json` dan `puskesmas.json` (hasil parsing tabel dari server, dengan pemeriksaan checksum), lalu menjalankan pemeriksaan konsistensi. Format `part_*.json` dijelaskan pada docstring skrip.
