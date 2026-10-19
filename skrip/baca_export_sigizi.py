"""Validasi ringkas export (HTML bergaya xls): hanya agregat, tanpa mencetak data pribadi.
Pembaca berbasis regex: HTMLParser menghilangkan baris pada berkas Sep 2025 (kemungkinan atribut/kutip tak seimbang)."""
import html
import re
import sys
from collections import Counter

TAG = re.compile(r"<[^>]*>")


def baca(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for tr in re.findall(r"<tr\b.*?</tr>", t, re.S | re.I):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.S | re.I)
        out.append([html.unescape(TAG.sub("", c)).strip() for c in cells])
    # header export punya 'Total Pengukuran' tanpa sel data pendampingnya (kolom tersembunyi di situs)
    if len(out) > 1 and "Total Pengukuran" in out[0] and len(out[0]) == len(out[1]) + 1:
        out[0].remove("Total Pengukuran")
    return out


if __name__ == "__main__":
    rows = baca(sys.argv[1])
    h, data = rows[0], rows[1:]
    ix = {n: i for i, n in enumerate(h)}
    print("kolom:", len(h), "| baris data:", len(data), "| baris dgn jumlah kolom beda:", sum(len(r) != len(h) for r in data))
    print("bulan pengukuran:", dict(Counter(r[ix["Tanggal Pengukuran"]][:7] for r in data).most_common(3)))
    print("per desa:", dict(Counter(r[ix["Desa/Kel"]] for r in data)))
    nik = [r[ix["NIK"]] for r in data]
    print("NIK kosong:", sum(not x for x in nik), "| NIK ganda:", len(nik) - len(set(nik)))
