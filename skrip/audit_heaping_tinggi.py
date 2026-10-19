"""Heaping tinggi badan + penumpukan z-score TB/U di sekitar -2 SD. HANYA mencetak agregat, tanpa data pribadi.
Pakai: python -I skrip/audit_heaping_tinggi.py <folder berkas Daftar_Status_Gizi_YYYY-MM.xls>
Heaping: bila tinggi diukur teliti (1 desimal), digit desimal ~seragam: .0 dan .5 masing-masing ~10% (jumlah ~20%).
Z-score: rasio anak di [-2.0,-1.9) terhadap [-2.1,-2.0); rasio ~1 wajar, >>1 = menumpuk tepat di atas batas stunting."""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baca_export_sigizi import baca  # noqa: E402


def angka(x):
    try:
        return float(x.replace(",", "."))
    except ValueError:
        return None


def desimal(x):
    """Digit desimal pertama dari teks angka, tanpa pembulatan float; None bila tidak ada angka."""
    t = x.strip().replace(",", ".")
    if angka(t) is None:
        return None
    return int(t.split(".")[1][0]) if "." in t and t.split(".")[1] else 0


def baris(nama, a):
    n, nol, lima, bulat, k_atas, k_bawah = a
    if not n:
        return
    rasio = k_atas / k_bawah if k_bawah else float("nan")
    print(f"{nama:22s} {n:6d}  .0={100*nol/n:5.1f}%  .5={100*lima/n:5.1f}%  .0+.5={100*(nol+lima)/n:5.1f}%  z[-2.0,-1.9)/z[-2.1,-2.0)={k_atas:4d}/{k_bawah:4d}={rasio:4.2f}")


def baru():
    return [0, 0, 0, 0, 0, 0]


per_bulan, per_tahun_desa = {}, defaultdict(baru)
for f in sorted(Path(sys.argv[1]).glob("Daftar_Status_Gizi_*.xls")):
    ym = f.stem[-7:]
    h, *d = baca(f)
    ix = {c: i for i, c in enumerate(h)}
    a = per_bulan.setdefault(ym, baru())
    for r in d:
        desa = r[ix["Desa/Kel"]].strip() or "(kosong)"
        tg = desimal(r[ix["Tinggi"]])
        z = angka(r[ix["ZS TB/U"]])
        for acc in (a, per_tahun_desa[(ym[:4], desa)]):
            if tg is not None:
                acc[0] += 1
                acc[1] += tg == 0
                acc[2] += tg == 5
            if z is not None and abs(z) < 999:
                acc[4] += -2.0 <= z < -1.9
                acc[5] += -2.1 <= z < -2.0

print("== per bulan (semua desa) ==")
for ym, a in per_bulan.items():
    baris(ym, a)
print("\n== per tahun x desa ==")
for (th, desa), a in sorted(per_tahun_desa.items()):
    baris(f"{th} {desa}", a)
