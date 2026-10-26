"""Gabungkan tabel hasil R (data/sigizi/analisis_r) dan SPSS (data/sigizi/analisis_spss) ke satu folder dengan struktur yang dibaca
siapkan_laporan.py dan bangun_workbook_analisis.py (<folder>/tabel/*.csv + desa_bulan.csv + log_cleaning.txt).
Pakai: python -I skrip/gabung_hasil_rs.py <folder python lama> <folder R> <folder SPSS> <folder keluaran>
desa_bulan.csv, log_cleaning.txt, who_lhfa_lms.csv berasal dari tahap cleaning Python dan disalin apa adanya.
CSV SPSS ditulis dengan BOM UTF-8; di sini BOM dibuang dan semua berkas ditulis ulang tanpa BOM."""
import shutil
import sys
from pathlib import Path

import pandas as pd

lama, r, spss, keluar = map(Path, sys.argv[1:5])
(keluar / "tabel").mkdir(parents=True, exist_ok=True)
n = 0
for sumber in (r, spss):
    for f in sorted(sumber.glob("*.csv")):
        pd.read_csv(f, encoding="utf-8-sig", na_values=[" ", ""], skipinitialspace=True).to_csv(keluar / "tabel" / f.name, index=False, encoding="utf-8")
        n += 1
for nama in ("desa_bulan.csv", "log_cleaning.txt"):
    shutil.copy(lama / nama, keluar / nama)
shutil.copy(lama / "tabel" / "who_lhfa_lms.csv", keluar / "tabel" / "who_lhfa_lms.csv")
print(n, "tabel digabung ke", keluar)
