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

## F. Data SigiziKesga (`data/sigizi/`)
- [x] Penyebab selisih posyandu vs laporan Puskesmas: anak dengan Posyandu kosong (818 anak, terpusat di Mumbulsari, Lengkong, Lampeji). Rinciannya di README kedua folder itu.
- [ ] Minta petugas entri Puskesmas melengkapi Posyandu yang kosong (818 anak, naik 50–110/bulan sepanjang 2026) dan 8 anak tanpa Desa.
- [ ] Konfirmasi ke petugas entri: entri massal bertanggal 31 Jul 2026 di Lampeji, Mumbulsari, Lengkong (tinggi/berat tidak sesuai umur, ZS TB/U −6 s.d. −9). Jangan pakai angka stunting periode itu sebelum dibersihkan.
- [ ] Bersihkan data per anak sebelum analisis: nilai penanda (ZS = 1000), salah satuan (berat 3700), tinggi/berat 0, tanggal ukur di luar bulan berkas. Pseudonimkan NIK, buang kolom identitas.
- [ ] Putuskan dataset analisis: sheet `Laporan Puskesmas` (agregat per desa) atau data per anak yang sudah dibersihkan. Rencana analisis menunggu hasil sesi inventaris SigiziKesga (lihat `data/sigizi/inventaris_sigizikesga.md` bila sudah ada).
- [ ] Buat berkas khusus tingkat desa (7 desa × 22 bulan) dengan persen stunting, wasting, underweight.
- [x] Rekap Sasaran Anak, Status Gizi & Usia (+JK) 22 bulan, dan cek volume 2024 sudah diambil (`data/sigizi/rekap_tambahan/`). Filter MBG/BBLR/PBLR dan insiden 2025 tidak diunduh: dihitung dari data per anak.
- [x] Data per anak 2024 diunduh (12 bulan, 36.263 baris) dan diaudit: lebih bersih daripada 2025–2026. Lihat bagian "Audit kualitas" di `data/sigizi/daftar_status_gizi/README.md`.
- [x] Keputusan 19 Okt 2026: data **2024 ikut dianalisis** (disetujui pembimbing), jadi periode analisis Jan 2024–Sep 2026.
- [x] Cek heaping tinggi dan penumpukan z-score (`skrip/audit_heaping_tinggi.py`, hasil di `data/sigizi/daftar_status_gizi/audit_heaping_tinggi.txt`): heaping ada di semua tahun, bukan hanya 2025–2026 (lihat README daftar_status_gizi).
- [x] Kelengkapan kolom faktor risiko (`data/sigizi/daftar_status_gizi/kelengkapan_faktor_risiko.txt`): BBLR (BB Lahir dalam kg, terisi ±95%, BBLR ±8%) dan PBLR (±10%) layak; MBG, KPSP, KIA, Kelas Ibu tidak layak (kosong atau terlalu jarang; MBG "ya" hanya 275 pengukuran, 2026); Jml Vit A ambigu (kosong vs belum dapat); Cara Ukur kosong 22% (2025) dan 53% (2026). Faktor risiko yang realistis: BBLR, PBLR, jenis kelamin, umur. Longitudinal layak: 6.328 anak, 60% terukur ≥12 bulan.
- [x] Tahap 1 cleaning selesai (`skrip/bersihkan_data_anak.py`, hasil di `data/sigizi/analisis/`; rencana di `data/sigizi/RENCANA_ANALISIS.md`). Dataset anak berpseudonim ada di `data/sumber/anak_bersih/` (tidak di git). Angka cocok 147/147 desa-bulan dengan Laporan Puskesmas.
- [x] Keputusan 19 Okt 2026: S1 diperluas sampai Sep 2026 untuk Lampeji/Mumbulsari/Lengkong; Lengkong/Mumbulsari 2024 (tanggal ukur seragam) tetap di S0 dan dicatat sebagai keterbatasan.
- [ ] Tahap 2–4 rencana analisis: dataset desa-bulan → analisis 1–12 → workbook Excel akhir.
- [ ] Tentukan perlakuan heaping/penumpukan z-score di analisis (analisis sensitivitas per desa, atau pakai desa dengan pengukuran teliti saja). Prevalensi stunting dari situs belum bisa dianggap valid.
- [ ] Tanya petugas entri: apa yang berubah di pencatatan sejak Jan 2026 (anak terukur naik dari ±61% ke ±95% sasaran padahal sasaran datar).
- [ ] Ambil ulang Okt 2026 setelah bulan berakhir.
