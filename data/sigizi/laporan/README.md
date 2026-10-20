# Laporan akhir mini riset (Word)

`Laporan_Mini_Riset_Stunting_Mumbulsari.docx` (±27 halaman, A4, Times New Roman 12, sitasi Vancouver). Dibuat 20 Okt 2026. Pembingkaian tujuan disetujui peneliti: gambaran status gizi dan kualitas data, faktor risiko (BBLR, PBLR, JK, umur), rekomendasi pencatatan.

## Yang harus diisi/dicek peneliti
- Sampul: nama penulis, NIM, nama pembimbing. Bab II 2.8: nomor dan tanggal surat izin, status kaji etik.
- **Setiap sitasi dicek sendiri** terhadap sumber aslinya. 20 Okt 2026: metadata ref. 1–13 dicocokkan dengan Crossref, Europe PMC, situs jurnal, peraturan.go.id/JDIH, dan PDF DHS; daftar penulis ref. 11 cocok (PMID 23920141). Klaim yang disitasi baru dicek terhadap abstrak, belum terhadap teks lengkap. Ref. 12 (Victora 2010) dan 13 (Thurstans 2020) ditambahkan pada tinjauan itu.
- Panduan format fakultas (margin, spasi, jumlah halaman) belum diketahui; margin 3 cm dan spasi 1,5 dipakai sebagai asumsi.
- Daftar isi diperbarui lewat Word (klik kanan > Perbarui bidang) bila isi diubah.

## Membangun ulang
```bash
python -I skrip/siapkan_laporan.py data/sigizi/analisis data/sumber/anak_bersih/anak_bersih.csv data/sigizi/laporan   # gambar + tabel_laporan.json
NODE_PATH=<folder node_modules berisi docx> node skrip/bangun_laporan.js data/sigizi/laporan data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx
```
Sitasi native Zotero (koleksi "Mini Riset Stunting Mumbulsari", key `K9EKXJC7`) dipasang sesudah build, dengan Zotero terbuka:
```bash
python -I skrip/pasang_sitasi_zotero.py data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx data/sigizi/laporan/referensi_zotero.json V68GNN2G,6PVFFE5R,JJ8J2IZK,TIZ9IFPS,XZXTY2JY,GX7ZSILR,TRB8QMED,SDX42E75,7ZWBZW9M,9IU7GNCU,CVAISV2Y,EEYPJRNB,LGQWFDIX
```
Urutan key = nomor Vancouver [1]–[13]. **Membangun ulang docx dari skrip menghapus field Zotero**; jalankan ulang perintah di atas sesudahnya, lalu Refresh di tab Zotero Word. Sitasi baru sebaiknya disisipkan lewat tab Zotero, bukan ditulis [n].

Isi narasi ada di `skrip/bangun_laporan.js`; angka tabel dan gambar dari `tabel_laporan.json` dan `gambar/` (semua agregat). Angka di teks ditulis manual dan diperiksa terhadap `data/sigizi/analisis/tabel/`.
