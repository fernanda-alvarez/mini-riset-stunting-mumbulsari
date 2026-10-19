"""Kelengkapan kolom faktor risiko + pengukuran berulang per anak. HANYA agregat, tanpa data pribadi.
Pakai: python -I skrip/periksa_kolom_faktor.py <folder berkas Daftar_Status_Gizi_YYYY-MM.xls>
Per tahun: terisi/masuk akal BB Lahir (500-6000 g; nilai <10 dianggap kg) & TB Lahir (30-60 cm), BBLR (<2500), PBLR (<48), nilai Cara Ukur, MBG, KPSP, KIA,
Kelas Ibu, Jml Vit A. Lalu: sebaran jumlah bulan terukur per NIK, dan apakah MBG berubah per anak (awal MBG = bulan pertama 'ya')."""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baca_export_sigizi import baca  # noqa: E402


def angka(x):
    try:
        return float(x.replace(",", "."))
    except ValueError:
        return None


per_th = defaultdict(lambda: defaultdict(Counter))
n_th = Counter()
bulan_nik = defaultdict(list)  # NIK -> [(ym, mbg)]
for f in sorted(Path(sys.argv[1]).glob("Daftar_Status_Gizi_*.xls")):
    ym = f.stem[-7:]
    h, *d = baca(f)
    ix = {c: i for i, c in enumerate(h)}
    for r in d:
        th, c = ym[:4], per_th[ym[:4]]
        n_th[th] += 1
        bb, tb = angka(r[ix["BB Lahir"]]), angka(r[ix["TB Lahir"]])
        if bb and bb < 10:  # umumnya tertulis kg (median 3,0); sebagian gram
            bb *= 1000
        c["BB Lahir"]["kosong/0" if not bb else "masuk akal" if 500 <= bb <= 6000 else "janggal"] += 1
        c["TB Lahir"]["kosong/0" if not tb else "masuk akal" if 30 <= tb <= 60 else "janggal"] += 1
        if bb and 500 <= bb <= 6000:
            c["BBLR"]["ya" if bb < 2500 else "tidak"] += 1
        if tb and 30 <= tb <= 60:
            c["PBLR"]["ya" if tb < 48 else "tidak"] += 1
        for k in ("Cara Ukur", "MBG", "KPSP", "KIA", "Kelas Ibu Balita", "Jml Vit A"):
            c[k][r[ix[k]].strip().lower()[:30] or "(kosong)"] += 1
        bulan_nik[r[ix["NIK"]]].append((ym, r[ix["MBG"]].strip().lower()))

for th in sorted(per_th):
    print(f"\n=== {th} (n={n_th[th]}) ===")
    for k, cnt in per_th[th].items():
        tot = sum(cnt.values())
        print(f"{k:17s}", ", ".join(f"{v}: {c} ({100*c/tot:.1f}%)" for v, c in cnt.most_common(8)))

print("\n=== Pengukuran berulang (34 bulan, per NIK) ===")
jml = Counter(len({ym for ym, _ in v}) for v in bulan_nik.values())
tot = sum(jml.values())
print(f"anak unik: {tot}")
for lo, hi in ((1, 1), (2, 5), (6, 11), (12, 23), (24, 34)):
    c = sum(v for k, v in jml.items() if lo <= k <= hi)
    print(f"  {lo}-{hi} bulan terukur: {c} ({100*c/tot:.1f}%)")
# 2024 saja & 2025+ saja
for nama, pola in (("2024", lambda y: y == "2024"), ("2025-2026", lambda y: y >= "2025")):
    j = Counter(len({ym for ym, _ in v if pola(ym[:4])}) for v in bulan_nik.values())
    j.pop(0, None)
    t = sum(j.values())
    print(f"  {nama}: >=2 bulan {100*sum(v for k,v in j.items() if k>=2)/t:.1f}%, >=6 bulan {100*sum(v for k,v in j.items() if k>=6)/t:.1f}% dari {t} anak")

print("\n=== MBG per anak ===")
ber = Counter()
for v in bulan_nik.values():
    nilai = [m for _, m in sorted(v)]
    pola = "".join("1" if m in ("ya", "1", "y", "mbg") else "0" for m in nilai)
    ber["tak pernah"] += "1" not in pola
    ber["selalu"] += "0" not in pola
    ber["berubah 0->1"] += "01" in pola
    ber["berubah 1->0"] += "10" in pola
print(dict(ber))
