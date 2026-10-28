# -*- coding: utf-8 -*-
"""Membuat tiga gambar tambahan Laporan Mini Riset Stunting Mumbulsari.

Gambar 3  : diagram alir data dan skenario analisis   (diagram_alir.png)
Gambar 5  : sebaran angka desimal tinggi badan        (desimal.png)
Gambar 9  : prevalensi stunting bulanan + tren segmented (tren_bulanan.png)

Pakai (dari folder akar proyek):
    python skrip/buat_gambar_laporan.py [folder_keluaran]

Masukan:
    data/sigizi/analisis_r/a2_seri_bulanan.csv
    data/sigizi/analisis_r/a2_tren_segmented.csv
    data/sumber/anak_analisis/anak_analisis.csv   (data tingkat anak, tidak diunggah ke mana pun)
Keluaran: tiga file PNG 300 dpi di folder keluaran (bawaan: data/sigizi/laporan/gambar).
Butuh: pandas, numpy, matplotlib.
"""
import sys
from pathlib import Path
import csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

AKAR = Path(__file__).resolve().parent.parent
R = AKAR / "data/sigizi/analisis_r"
ANAK = AKAR / "data/sumber/anak_analisis/anak_analisis.csv"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else AKAR / "data/sigizi/laporan/gambar"
OUT.mkdir(parents=True, exist_ok=True)

BIRU, ORANYE, ABU, HIJAU = "#1f5fa8", "#c4571a", "#555555", "#6a8f3a"


def gaya(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- Gambar 9
def tren_bulanan():
    rows = list(csv.DictReader(open(R / "a2_seri_bulanan.csv", encoding="utf-8")))

    def seri(sk):
        d = [(int(r["t"]), float(r["pct"]), r["bulan"]) for r in rows
             if r["skenario"] == sk and r["desa"] == "SEMUA" and r["outcome"] == "stunting"]
        return sorted(d)

    s0, s3 = seri("S0"), seri("S3")
    seg = {r["parameter"]: float(r["est"]) for r in csv.DictReader(open(R / "a2_tren_segmented.csv", encoding="utf-8"))
           if r["skenario"] == "S0" and r["desa"] == "SEMUA" and r["outcome"] == "stunting"}
    a = seg["level_awal"]; b = seg["slope_pra_pp_per_bulan"]
    j = seg["lompatan_2026-01_pp"]; ds = seg["perubahan_slope_pp_per_bulan"]

    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=300)
    ax.plot([x[0] for x in s0], [x[1] for x in s0], "o-", color=BIRU, ms=3.5, lw=1.2, label="Skenario S0 (data tercatat)")
    ax.plot([x[0] for x in s3], [x[1] for x in s3], "s--", color=ORANYE, ms=3, lw=1, label="Skenario S3 (tanpa desa-bulan anomali)")
    t1, t2 = range(0, 24), range(24, 33)
    ax.plot(list(t1), [a + b * t for t in t1], color=ABU, lw=1.6, ls=":")
    ax.plot(list(t2), [a + b * t + j + ds * (t - 24) for t in t2], color=ABU, lw=1.6, ls=":",
            label="Garis tren regresi segmen (S0)")
    ax.axvline(23.5, color="#888", lw=0.8)
    ax.set_ylim(0, max(x[1] for x in s0) * 1.12)
    ax.text(23.3, ax.get_ylim()[1] * 0.97, "Januari 2026:\ncakupan melonjak dan\ncara pencatatan berubah",
            ha="right", va="top", fontsize=7, color="#333")
    tk = [0, 6, 12, 18, 24, 30]
    ax.set_xticks(tk); ax.set_xticklabels([s0[i][2] for i in tk], fontsize=7.5)
    ax.set_ylabel("Prevalensi stunting (%)", fontsize=8.5); ax.set_xlabel("Bulan", fontsize=8.5)
    ax.tick_params(axis="y", labelsize=8); ax.grid(axis="y", alpha=.25); gaya(ax)
    ax.legend(fontsize=7.2, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.82))
    fig.tight_layout(); fig.savefig(OUT / "tren_bulanan.png"); plt.close(fig)


# ---------------------------------------------------------------- Gambar 3
def diagram_alir():
    fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=300)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    def kotak(x, y, w, h, teks, fc="#eaf1fa", ec=BIRU, fs=7.4):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=1))
        ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center", fontsize=fs, color="#111", linespacing=1.4)

    def panah(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, lw=1, color="#444"))

    kotak(3, 82, 50, 14, "108.322 pengukuran dari 6.312 anak\nJanuari 2024–September 2026\ntujuh desa")
    kotak(3, 56, 50, 14, "105.600 pengukuran (97,5%)\nSkenario S0: dasar prevalensi,\ntren, dan penilaian mutu data")
    kotak(3, 30, 50, 14, "90.838 pengukuran dari 5.661 anak\n(7.531 kasus stunting)\nbahan regresi logistik model A, B, dan C")
    kotak(3, 4, 50, 14, "Waktu sampai stunting (Kaplan-Meier)\n2.995 anak untuk jenis kelamin\n2.895 anak untuk BBLR")
    panah(28, 81.5, 28, 70.8); panah(28, 55.5, 28, 44.8); panah(28, 29.5, 28, 18.8)
    kotak(62, 82, 35, 14, "2.722 pengukuran dikeluarkan\n(masalah berat atau\nnama desa kosong)", fc="#fbeee6", ec=ORANYE, fs=7)
    panah(53.8, 89, 61.5, 89)
    ax.text(79.5, 67.5, "Skenario sensitivitas dari S0", ha="center", fontsize=7.4, style="italic", color="#333")
    sc = [(48, "S1: tanpa tiga desa pada\nJanuari–September 2026"),
          (32, "S2: hanya desa-tahun dengan\npembulatan < 70%"),
          (16, "S3: tanpa desa-bulan\nanomali")]
    for y, t in sc:
        kotak(62, y, 35, 11, t, fs=7)
        panah(58, y + 5.5, 61.5, y + 5.5)
    ax.plot([53.8, 58, 58], [63, 63, 21.5], color="#444", lw=1)
    fig.savefig(OUT / "diagram_alir.png", bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------- Gambar 5
def desimal():
    d = pd.read_csv(ANAK, low_memory=False, usecols=["tinggi", "tahun", "s0"])
    d = d[(d.s0 == 1) & d.tinggi.notna()].copy()
    d["dig"] = np.round(d.tinggi * 10).astype(int) % 10
    warna = {2024: BIRU, 2025: ORANYE, 2026: HIJAU}
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
    w = 0.27
    for i, y in enumerate(warna):
        pct = d[d.tahun == y].dig.value_counts(normalize=True).reindex(range(10), fill_value=0) * 100
        ax.bar(np.arange(10) + (i - 1) * w, pct.values, w, color=warna[y], label=str(y))
    ax.axhline(10, color="#444", ls=":", lw=1.2)
    ax.text(9.55, 10.6, "10% jika merata", ha="right", fontsize=7.5, color="#333")
    ax.set_xticks(range(10)); ax.set_xticklabels([f".{i}" for i in range(10)], fontsize=8)
    ax.set_xlabel("Angka desimal tinggi badan (cm)", fontsize=8.5)
    ax.set_ylabel("Persentase pengukuran (%)", fontsize=8.5)
    ax.tick_params(axis="y", labelsize=8); ax.grid(axis="y", alpha=.25); gaya(ax)
    ax.legend(frameon=False, fontsize=8, title="Tahun", title_fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "desimal.png"); plt.close(fig)


if __name__ == "__main__":
    tren_bulanan(); diagram_alir(); desimal()
    print("Selesai. Gambar tersimpan di", OUT)
