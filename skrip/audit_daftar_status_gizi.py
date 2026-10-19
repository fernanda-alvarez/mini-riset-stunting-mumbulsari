"""Audit akhir 22 berkas Daftar Status Gizi dan diagnosis selisih posyandu vs Puskesmas. HANYA mencetak agregat."""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baca_export_sigizi import baca  # noqa: E402

PROJ = Path(sys.argv[1])
SRC = PROJ / "data/sumber/sigizi_daftar_status_gizi_2026-10-19"
MENTAH = PROJ / "arsip/sigizi_2026-10-19/data/sigizi/rekap_status_gizi/_mentah"
HARAP = {"2025-01": 3355, "2025-02": 2632, "2025-03": 2806, "2025-04": 2982, "2025-05": 3032, "2025-06": 2555,
         "2025-07": 2798, "2025-08": 2703, "2025-09": 2898, "2025-10": 3024, "2025-11": 3025, "2025-12": 2732,
         "2026-01": 4249, "2026-02": 4250, "2026-03": 4255, "2026-04": 4244, "2026-05": 4234, "2026-06": 4194,
         "2026-07": 4068, "2026-08": 4025, "2026-09": 3998, "2026-10": 20}
norm = lambda s: re.sub(r"\s+", " ", s.strip().upper())

# master posyandu per desa dari rekap per posyandu
master = defaultdict(set)
for p in MENTAH.glob("part_*.json"):
    for key, (desa, th, bl, st, rows) in json.loads(p.read_text(encoding="utf-8"))["data"].items():
        master[desa] |= {norm(r[0]) for r in rows if r[0] != "JUMLAH"}
pusk = json.loads((MENTAH / "puskesmas.json").read_text(encoding="utf-8"))["data"]
semua_master = {n: d for d, s in master.items() for n in s}

print("bulan, baris, harap, status, total Puskesmas(rekap BB/U), posyandu desa sendiri, posyandu desa LAIN, kosong, lain")
tot = Counter()
for ym, harap in HARAP.items():
    rows = baca(SRC / f"Daftar_Status_Gizi_{ym}.xls")
    h, d = rows[0], rows[1:]
    ix = {c: i for i, c in enumerate(h)}
    ok = len(d) == harap and all(len(r) == len(h) for r in d)
    th, bl = ym.split("-")
    tot_rek = sum(pusk[f"{int(th)}-{int(bl)}"][-1][1:6])
    c = Counter()
    for r in d:
        desa, pos = norm(r[ix["Desa/Kel"]]), norm(r[ix["Posyandu"]])
        if not pos:
            k = "kosong"
        elif pos in master.get(desa, ()):
            k = "sendiri"
        elif pos in semua_master:
            k = "desa_lain"
        else:
            k = "lain"
        c[k] += 1
    tot.update(c)
    print(f"{ym}, {len(d)}, {harap}, {'OK' if ok else 'BEDA'}, {tot_rek}, {c['sendiri']}, {c['desa_lain']}, {c['kosong']}, {c['lain']}")
print("TOTAL seluruh bulan:", dict(tot), "| semua anak:", sum(tot.values()))
