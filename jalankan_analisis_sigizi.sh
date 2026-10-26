#!/bin/sh
# Analisis SIGIZI di SPSS dan R (Python hanya untuk cleaning dan penandaan skenario). Padanan skrip/analisis_tahap2*.py.
# Usage: sh jalankan_analisis_sigizi.sh   (dari folder induk proyek; data/sumber/anak_bersih/anak_bersih.csv harus sudah ada)
set -e
PY="python"
RS="/c/PROGRA~2/R/R-4.6.1/bin/x64/Rscript"
SPSSPY="/c/Program Files/IBM/SPSS/Statistics/27/Python3/python.exe"
AN="data/sumber/anak_analisis/anak_analisis.csv"
TAB="data/sigizi/analisis/tabel"

# 1. Berkas masukan: anak_bersih + penanda skenario + sampel acak per anak per tahun (+ sasaran.csv)
"$PY" -I skrip/siapkan_data_spss_r.py data/sumber/anak_bersih/anak_bersih.csv "$AN" data/sigizi/rekap_tambahan/sasaran_cakupan_cek2024.xlsx

# 2. SPSS: A3, A4, A5 (uji JK dan umur), P2  -> data/sigizi/analisis_spss/
"$SPSSPY" skrip/spss/jalankan_spss.py skrip/spss/analisis_spss.sps

# 3. R: A1, A2, A5 (tabel), A6, A7, A8, A9, P1, P3  -> data/sigizi/analisis_r/ (A1/A5/A6/A7 + bootstrap makan ±6 menit)
"$RS" skrip/analisis_r_1.R "$AN" data/sigizi/analisis_r
"$RS" skrip/analisis_r_2.R "$AN" data/sigizi/analisis_r
"$RS" skrip/analisis_r_3.R "$AN" "$TAB/who_lhfa_lms.csv" data/sigizi/analisis_r

# 4. Bandingkan dengan tabel Python
"$RS" skrip/bandingkan_hasil.R "$TAB" data/sigizi/analisis_r > data/sigizi/analisis_r/perbandingan_dengan_python.txt
"$RS" skrip/bandingkan_hasil.R "$TAB" data/sigizi/analisis_spss a3_antar_desa,a4_cakupan_desa_bulan,a4_cakupan_bulan,a5_uji_jk_umur,p2_bulan_terukur > data/sigizi/analisis_spss/perbandingan_dengan_python.txt

# 5. Gabungkan tabel R + SPSS untuk laporan dan workbook, lalu bangun ulang workbook dan bahan laporan
"$PY" -I skrip/gabung_hasil_rs.py data/sigizi/analisis data/sigizi/analisis_r data/sigizi/analisis_spss data/sigizi/analisis_rs
"$PY" -I skrip/bangun_workbook_analisis.py data/sigizi/analisis_rs data/sumber/anak_bersih/anak_bersih.csv data/sigizi/analisis/Analisis_Stunting_Mumbulsari.xlsx
"$PY" -I skrip/siapkan_laporan.py data/sigizi/analisis_rs data/sumber/anak_bersih/anak_bersih.csv data/sigizi/laporan
