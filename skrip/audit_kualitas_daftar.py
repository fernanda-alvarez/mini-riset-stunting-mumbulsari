"""Audit kualitas semua berkas Daftar Status Gizi (per anak) per bulan. HANYA mencetak agregat, tanpa data pribadi.
Pakai: python -I skrip/audit_kualitas_daftar.py <folder berkas Daftar_Status_Gizi_YYYY-MM.xls>
Kolom: n, desa kosong, posyandu kosong, tanggal ukur di luar bulan, tanggal ukur terpadat (% baris), TB/U Outlier (%),
nilai aneh (ZS TB/U = +-1000 atau tinggi 0 atau berat 0 atau berat >40 atau tinggi >130), stunting (% dari TB/U non-Outlier),
NIK yang juga ada bulan sebelumnya (%)."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baca_export_sigizi import baca  # noqa: E402


def angka(x):
    try:
        return float(x.replace(",", "."))
    except ValueError:
        return None


print("bulan   n     desa0 pos0 tglLuar tglTerpadat%  outlierTBU%  aneh  stunting%  NIKdariBlnLalu%")
prev = set()
for f in sorted(Path(sys.argv[1]).glob("Daftar_Status_Gizi_*.xls")):
    ym = f.stem[-7:]
    h, *d = baca(f)
    ix = {c: i for i, c in enumerate(h)}
    n = len(d)
    desa0 = sum(not r[ix["Desa/Kel"]].strip() for r in d)
    pos0 = sum(not r[ix["Posyandu"]].strip() for r in d)
    luar = sum(r[ix["Tanggal Pengukuran"]][:7] != ym for r in d)
    padat = Counter(r[ix["Tanggal Pengukuran"]] for r in d).most_common(1)[0][1] / n
    tbu = [r[ix["TB/U"]].strip().lower() for r in d]
    outl = tbu.count("outlier") / n
    aneh = 0
    for r in d:
        t, b, z = angka(r[ix["Tinggi"]]), angka(r[ix["Berat"]]), angka(r[ix["ZS TB/U"]])
        if (z is not None and abs(z) >= 999) or t == 0 or b == 0 or (b or 0) > 40 or (t or 0) > 130:
            aneh += 1
    valid = [x for x in tbu if x and x != "outlier"]
    stunt = sum(x in ("sangat pendek", "pendek") for x in valid) / len(valid) if valid else float("nan")
    nik = {r[ix["NIK"]] for r in d}
    lanjut = len(nik & prev) / len(nik) if prev else float("nan")
    print(f"{ym}  {n:5d}  {desa0:4d} {pos0:4d} {luar:6d}  {100*padat:9.0f}%  {100*outl:9.1f}%  {aneh:4d}  {100*stunt:7.1f}%  {100*lanjut:12.0f}%")
    prev = nik
