#!/bin/sh
# Jalankan ulang seluruh pipeline analisis MTBS (dari Data Bersih sampai laporan docx; PDF tidak dibuat ulang).
# Usage: sh jalankan_semua.sh   (dari folder induk proyek ini)
#
# Langkah 0 (sekali saja, tidak ikut dijalankan di sini): Data Bersih dibuat dari data sumber dengan
#   python skrip/cleanup_mtbs.py "data/sumber/Snapshot Data PKM Mumbulsari/13102026 Klaster 2 PKM Mumbulsari.xlsx" \
#          "data/olahan/MTBS Balita PKM Mumbulsari 2025-2026 - Data Bersih.xlsx"
set -e
PY="/c/Users/Fitranda Taslim/AppData/Local/Programs/Python/Python311/python.exe"
RS="/c/PROGRA~2/R/R-46~1.1/bin/x64/Rscript"
PS="powershell"
S="skrip"
F="data/olahan/MTBS Balita PKM Mumbulsari 2025-2026 - "
SENS="data/sensitivitas"
GRAFIK="grafik"
LAP="naskah/Laporan Mini Riset - Status Gizi Balita pada Kunjungan MTBS Puskesmas Mumbulsari 2025-2026"
mkdir -p "$SENS" "$GRAFIK"

"$PY" -W ignore -I "$S/siap_olah_mtbs.py" "${F}Data Bersih.xlsx" "${F}Siap Olah.xlsx"
"$RS" "$S/zscore_mtbs.R" "${F}Siap Olah.xlsx" "${F}Z-score & Deskriptif.xlsx" || true
"$RS" "$S/analisis_lanjut_mtbs.R" "${F}Data Bersih.xlsx" "${F}Z-score & Deskriptif.xlsx" "${F}Analisis Lanjut.xlsx" || true
"$RS" "$S/tabel_grafik_mtbs.R" "${F}Siap Olah.xlsx" "${F}Analisis Lanjut.xlsx" "${F}Tabel & Grafik.xlsx" "$GRAFIK" || true
"$RS" "$S/kelengkapan_mtbs.R" "${F}Data Bersih.xlsx" "${F}Analisis Lanjut.xlsx" "${F}Kelengkapan & Kualitas.xlsx" || true

# Sensitivitas: periode lengkap termasuk kunjungan Juli-Des 2024
"$PY" -W ignore -I "$S/siap_olah_mtbs.py" "${F}Data Bersih.xlsx" "$SENS/Siap Olah - termasuk 2024.xlsx" --semua-periode
"$RS" "$S/zscore_mtbs.R" "$SENS/Siap Olah - termasuk 2024.xlsx" "$SENS/Z-score - termasuk 2024.xlsx" || true
"$RS" "$S/analisis_lanjut_mtbs.R" "${F}Data Bersih.xlsx" "$SENS/Z-score - termasuk 2024.xlsx" "$SENS/Analisis Lanjut - termasuk 2024.xlsx" || true

"$RS" "$S/kualitas_tambahan_mtbs.R" "${F}Data Bersih.xlsx" "${F}Analisis Lanjut.xlsx" "$SENS/Analisis Lanjut - termasuk 2024.xlsx" "${F}Kualitas Tambahan.xlsx" "$GRAFIK" || true
"$PY" -W ignore -I "$S/daftar_tindak_lanjut.py" "${F}Analisis Lanjut.xlsx" "${F}Daftar Tindak Lanjut (INTERNAL).xlsx"
"$PY" -W ignore -I "$S/buat_laporan_docx.py"
"$PY" -W ignore -I "$S/pasang_sitasi_zotero.py"
"$PS" -ExecutionPolicy Bypass -File "$S/perbarui_daftar_isi.ps1" "$LAP.docx" || true
