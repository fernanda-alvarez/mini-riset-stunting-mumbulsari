# Laporan akhir mini riset (Word)

`Laporan_Mini_Riset_Stunting_Mumbulsari.docx` (±53 halaman, A4, Times New Roman 12, sitasi APA 7 lewat Zotero). Dibuat 20 Okt 2026; struktur disesuaikan 21 Okt 2026 dengan naskah contoh fakultas (Halaman Judul, Halaman Sampul, Daftar Isi/Tabel/Gambar bernomor romawi; BAB 1 Pendahuluan, BAB 2 Tinjauan Pustaka, BAB 3 Metodologi Penelitian, BAB 4 Hasil dan Pembahasan, BAB 5 Kesimpulan dan Saran). Tanpa abstrak. Pembingkaian tujuan disetujui peneliti: gambaran status gizi dan kualitas data, faktor risiko (BBLR, PBLR, JK, umur), rekomendasi pencatatan.

## Yang harus diisi/dicek peneliti
- Sampul dan halaman sampul mengikuti draf proposal di `naskah/` (logo `gambar/logo_unej.png`), dengan judul laporan. Subbab 3.10: nomor dan tanggal surat izin, status kaji etik.
- **Setiap sitasi dicek sendiri** terhadap sumber aslinya. Ref. lama (13) dicek 20 Okt 2026 terhadap Crossref, Europe PMC, situs jurnal, peraturan.go.id/JDIH, dan PDF DHS. Bab 2 (20 ref. baru) disusun 21 Okt 2026 dari penelusuran web: DOI dicek di Crossref; angka Christian 2013, Titaley 2019, Rahmadiani 2025, Laksono 2024, Victora 2010, Stewart 2013, Dewey 2011, Bilukha 2020, Silva 2023 dicek terhadap abstrak Europe PMC; Mataheru 2026, Sanda 2022, Ishak 2026, UN Global Pulse 2023, dan WHO (BBLR) terhadap halaman sumbernya. Belum dicek ke teks lengkap: Black 2013, Walker 2007, Victora 2008, Hoddinott 2008 (abstrak Lancet tidak terbuka), angka JME 2025, isi Permenkes 155/2010 dan Permenkes 2/2020 (PDF resmi tidak terbaca).
- Panduan format fakultas (margin, spasi) belum diketahui; margin 3 cm dan spasi 1,5 dipakai sebagai asumsi.

## Membangun ulang
```bash
python -I skrip/siapkan_laporan.py data/sigizi/analisis data/sumber/anak_bersih/anak_bersih.csv data/sigizi/laporan   # gambar + tabel_laporan.json
python -I skrip/gambar_kerangka.py data/sigizi/laporan/gambar                                                          # kerangka teori dan konsep
NODE_PATH=<folder node_modules berisi docx@9> node skrip/bangun_laporan.js data/sigizi/laporan data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx
python -I skrip/pasang_sitasi_zotero.py data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx data/sigizi/laporan/referensi_zotero.json
powershell -File skrip/perbarui_daftar_isi.ps1 data/sigizi/laporan/Laporan_Mini_Riset_Stunting_Mumbulsari.docx
```
Di `bangun_laporan.js` sitasi ditulis `[@id; @id]` (naratif: `Penulis dkk. [-@id]` → "Penulis dkk. (tahun)"); `id` dipetakan ke key Zotero di `referensi_zotero.json`. `pasang_sitasi_zotero.py` (Zotero terbuka; bila tertutup memakai salinan JSON) mengambil teks APA 7 locale id-ID dari Zotero, mengganti penanda dengan field Zotero, dan menyisipkan daftar pustaka urut abjad sebagai field bibliografi. Referensi baru: tambahkan ke koleksi Zotero "Mini Riset Stunting Mumbulsari" (key `K9EKXJC7`), lalu tambahkan `{"id", "key"}` ke `referensi_zotero.json`. **Membangun ulang docx dari skrip menghapus field Zotero**; jalankan ulang dua perintah terakhir, lalu Refresh di tab Zotero Word.

`perbarui_daftar_isi.ps1` memperbarui nomor keterangan (field SEQ), Daftar Isi, Daftar Tabel, dan Daftar Gambar. Nomor tabel/gambar di teks ditulis manual dan harus urut sesuai kemunculan.

Isi narasi ada di `skrip/bangun_laporan.js`; angka tabel dan gambar dari `tabel_laporan.json` dan `gambar/` (semua agregat). Angka di teks ditulis manual dan diperiksa terhadap `data/sigizi/analisis/tabel/`.
