# Bahan laporan akhir

Folder ini berisi bahan untuk laporan akhir mini riset: gambar (`gambar/`), tabel dalam format JSON (`tabel_laporan.json`), dan daftar referensi untuk Zotero (`referensi_zotero.json`). Seluruhnya hanya berisi hasil agregat.

Laporan Word-nya sendiri (`Laporan_Mini_Riset_Stunting_Mumbulsari.docx`, sekitar 53 halaman, A4, Times New Roman 12, sitasi APA 7) tidak disertakan di repo ini. Laporan itu disusun dengan struktur naskah fakultas: halaman judul dan sampul, daftar isi, daftar tabel, dan daftar gambar, lalu Bab 1 Pendahuluan, Bab 2 Tinjauan Pustaka, Bab 3 Metodologi Penelitian, Bab 4 Hasil dan Pembahasan, dan Bab 5 Kesimpulan dan Saran. Tujuannya menggambarkan status gizi dan kualitas data rutin, menganalisis faktor risiko (BBLR, PBLR, jenis kelamin, umur), dan memberi rekomendasi untuk pencatatan.

## Isi folder

| Berkas | Isi |
|---|---|
| `gambar/` | Gambar yang dipakai di laporan (PNG). Sebagian dibuat oleh `skrip/siapkan_laporan.py`, kerangka teori dan konsep oleh `skrip/gambar_kerangka.py`, dan tiga gambar tambahan oleh `skrip/buat_gambar_laporan.py`. |
| `tabel_laporan.json` | Angka untuk semua tabel laporan, sudah diformat dengan pemisah ribuan titik dan desimal koma. |
| `referensi_zotero.json` | Pemetaan penanda sitasi di naskah (`id`) ke item di koleksi Zotero (`key`), serta gaya sitasi yang diambil dari Zotero. |

## Sumber angka

Sejak 26 Oktober 2026, tabel dan gambar berasal dari hasil R dan SPSS (`data/sigizi/analisis_rs/`), bukan dari versi Python. Selisih antara keduanya hanya pada batas interval kepercayaan bootstrap, yaitu sel IK di Tabel 8, Lampiran 1 dan 2, serta Gambar 6, karena generator angka acak R berbeda dari numpy. Angka di teks laporan ditulis manual dan diperiksa terhadap tabel di `data/sigizi/analisis/tabel/`.

## Membangun ulang laporan

Langkah ini butuh data per anak lokal dan hanya bisa dijalankan oleh penulis. Perintah dijalankan dari akar repo:

```bash
# 1. Gabung tabel hasil R dan SPSS
python -I skrip/gabung_hasil_rs.py data/sigizi/analisis data/sigizi/analisis_r data/sigizi/analisis_spss data/sigizi/analisis_rs

# 2. Buat gambar dan tabel_laporan.json
python -I skrip/siapkan_laporan.py data/sigizi/analisis_rs data/sumber/anak_bersih/anak_bersih.csv data/sigizi/laporan

# 3. Gambar kerangka teori dan konsep
python -I skrip/gambar_kerangka.py data/sigizi/laporan/gambar

# 4. Susun dokumen Word (butuh folder node_modules berisi paket docx versi 9)
NODE_PATH=<folder node_modules> node skrip/bangun_laporan.js data/sigizi/laporan data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx

# 5. Ubah penanda sitasi menjadi field Zotero (Zotero harus terbuka)
python -I skrip/pasang_sitasi_zotero.py data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx data/sigizi/laporan/referensi_zotero.json

# 6. Perbarui daftar isi, daftar tabel, dan daftar gambar lewat Word (Windows)
powershell -File skrip/perbarui_daftar_isi.ps1 data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx
```

Beberapa hal tentang langkah 4 sampai 6:

- Narasi laporan ada di `skrip/bangun_laporan.js`. Sitasi ditulis sebagai `[@id; @id]`, dan untuk sitasi naratif sebagai `Penulis dkk. [-@id]` yang menjadi "Penulis dkk. (tahun)". Setiap `id` dipetakan ke key Zotero di `referensi_zotero.json`.
- Untuk menambah referensi, tambahkan item ke koleksi Zotero "Mini Riset Stunting Mumbulsari", lalu tambahkan pasangan `{"id", "key"}` ke `referensi_zotero.json`.
- Membangun ulang `.docx` dari skrip menghapus semua field Zotero. Setelah langkah 4, langkah 5 dan 6 harus diulang, lalu pilih Refresh di tab Zotero pada Word.
- Nomor tabel dan gambar di dalam teks ditulis manual dan harus urut sesuai kemunculannya. Nomor pada keterangan tabel dan gambar diperbarui otomatis oleh langkah 6.
