# To-do: dataset baru

Hasil dan laporan dari data snapshot 13 Okt 2026 sudah dibekukan di `arsip/snapshot_2026-10-13/` (TODO lamanya ada di sana). Folder `data/sumber/` dan `data/olahan/` kosong, menunggu dataset baru.

## A. Data masuk
- [ ] Tunggu download selesai, lalu taruh di `data/sumber/<nama snapshot>/` (folder ini tidak masuk git).
- [ ] Cek berkas bisa dibuka dan ukurannya wajar (bandingkan dengan ukuran sumber asli).
- [ ] Catat tanggal snapshot dan klaster/sheet yang dicakup. Snapshot lama: 13-10-2026, Klaster 2–5, hanya Klaster 2 yang dianalisis.
- [ ] Bandingkan struktur dengan data lama: nama sheet, kolom, format tanggal lahir/umur. Kalau berbeda, catat bedanya sebelum menyentuh skrip.

## B. Sesuaikan skrip (isi lama masih tertanam)
- [ ] `skrip/cleanup_mtbs.py`: `SNAPSHOT`, daftar sheet (`SHEETS`), `TAHUN_OK`, batas tahun lahir, dan aturan penukaran tanggal khusus register 2025/2026.
- [ ] `skrip/siap_olah_mtbs.py` dan skrip R (`kelengkapan`, `kualitas_tambahan`, `tabel_grafik`, `zscore`): filter periode analisis (saat ini tahun ≥ 2025, tab "2025"/"2026").
- [ ] Label periode `2025-2026` pada nama berkas dan judul: `jalankan_semua.sh`, `ringkasan_html.py`, `percantik_excel.py`, `buat_form_docx.py`, `sinkronkan_isian_docx.py`, `daftar_tindak_lanjut.py`, `pasang_sitasi_zotero.py`, `buat_laporan_docx.py`.
- [ ] Putuskan: periode analisis tetap 2025–2026, atau diperluas mengikuti data baru? Ini menentukan nama berkas dan angka di laporan.
- [ ] `jalankan_semua.sh`: perbarui perintah langkah 0 (path data sumber baru).

## C. Jalankan dan periksa
- [ ] Langkah 0: `cleanup_mtbs.py` pada data sumber baru, lalu periksa sheet ringkasan pembersihan (duplikat, umur tidak valid, tanggal lahir ditukar).
- [ ] `sh jalankan_semua.sh` sampai selesai tanpa error.
- [ ] Bandingkan angka utama dengan snapshot lama (jumlah kunjungan dan balita, stunting 42,5%, kelengkapan TB/PB 57%). Selisih besar harus bisa dijelaskan.

## D. Laporan
- [ ] Tentukan: laporan baru atau pembaruan laporan lama. Kalau pembaruan, draf proposal di `naskah/` tetap sumbernya.
- [ ] Salin sisa pekerjaan laporan lama yang masih berlaku dari `arsip/snapshot_2026-10-13/TODO.md` (isian administratif di form, cek Word, verifikasi 16 referensi, konsultasi pembimbing, izin data, ekspor PDF final).

## E. Data sensitif
- [ ] Data sumber, Data Bersih, Daftar Tindak Lanjut (INTERNAL), dan form isian memuat identitas anak (NIK, nama). Semua sudah di `.gitignore`. Cek `git status` sebelum commit.
- [ ] Serahkan Daftar Tindak Lanjut ke petugas gizi atau penanggung jawab MTBS secara langsung, bukan lewat grup.
