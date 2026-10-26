"""Siapkan berkas masukan untuk analisis di SPSS dan R: anak_bersih.csv + penanda skenario + sampel acak satu pengukuran per anak per tahun.
Pakai: python -I skrip/siapkan_data_spss_r.py <anak_bersih.csv> <anak_analisis.csv> [sasaran_cakupan_cek2024.xlsx]
Bila xlsx sasaran diberikan, sheet "Sasaran" ditulis sebagai sasaran.csv di folder yang sama (SPSS 27 gagal membaca xlsx itu).
Cleaning dan penandaan skenario S0-S3 tetap di Python (bersihkan_data_anak.py). Kolom tambahan:
  s0..s3     1 bila baris masuk skenario (0/1)
  pa_s0..pa_s3  1 bila baris adalah pengukuran acak terpilih per anak per tahun dalam skenario itu (sama persis dengan pertama() di
                analisis_tahap2.py, supaya uji chi-kuadrat di SPSS memakai sampel yang sama dengan Python)
  kel_umur   kelompok umur 0-5, 6-11, 12-23, 24-35, 36-47, 48-59 bln
  t          indeks bulan (0 = 2024-01 ... 32 = 2026-09)
Keluaran berisi data per anak: simpan di folder gitignored, jangan dibagikan."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from analisis_tahap2 import IDX, UMUR, pertama  # noqa: E402
from bersihkan_data_anak import skenario  # noqa: E402

if __name__ == "__main__":
    d = pd.read_csv(sys.argv[1], low_memory=False)
    sk = skenario(d)
    d["kel_umur"] = pd.cut(d["umur_bln"], [u[0] for u in UMUR] + [60], right=False, labels=[u[2] for u in UMUR]).astype(str).replace("nan", "")
    d["t"] = d["bulan_berkas"].map(IDX)
    for nama, m in sk.items():
        d[nama.lower()] = m.astype(int)
        d["pa_" + nama.lower()] = 0
        d.loc[pertama(d[m]).index, "pa_" + nama.lower()] = 1
    for c in d.columns:
        if d[c].dtype == bool:
            d[c] = d[c].astype(int)
    d.to_csv(sys.argv[2], index=False, encoding="utf-8")
    if len(sys.argv) > 3:
        sas = pd.read_excel(sys.argv[3], sheet_name="Sasaran").rename(columns={"Tahun": "tahun", "Bulan": "bulan", "Desa": "desa", "Laki-laki": "laki", "Perempuan": "perempuan", "Total sasaran": "sasaran"})
        sas.to_csv(Path(sys.argv[2]).with_name("sasaran.csv"), index=False, encoding="utf-8")
    print(d.shape, {n: int(v.sum()) for n, v in sk.items()})
