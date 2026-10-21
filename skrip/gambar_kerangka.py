"""Gambar kerangka teori dan kerangka konsep (Bab 2 laporan akhir).
Usage: python gambar_kerangka.py <folder gambar>   (mis. data/sigizi/laporan/gambar)
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Times New Roman"
out = sys.argv[1]


def kotak(ax, x, y, w, h, teks, putus=False, tebal=False, abu=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.01", fc="#EDEDED" if abu else "white",
                                ec="black", lw=1.4 if tebal else 1, ls=(0, (4, 3)) if putus else "-"))
    ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center", fontsize=10, fontweight="bold" if tebal else "normal", wrap=True)


def panah(ax, x1, y1, x2, y2, putus=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1, ls=(0, (4, 3)) if putus else "-", color="black"))


def kanvas(h):
    fig, ax = plt.subplots(figsize=(7.5, h))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return fig, ax


# ---------- kerangka teori: kerangka WHO (Stewart dkk. 2013) + jalur pengukuran dan pencatatan ----------
fig, ax = kanvas(7.2)
kotak(ax, 0.03, 0.86, 0.94, 0.11, "Faktor kontekstual: ekonomi politik, kesehatan dan layanan kesehatan, pendidikan,\nsosial budaya, sistem pertanian dan pangan, air, sanitasi, dan lingkungan", abu=True)
kotak(ax, 0.03, 0.66, 0.29, 0.13, "Faktor ibu dan\nrumah tangga\n(gizi dan tinggi ibu,\nantenatal, sosial ekonomi)")
kotak(ax, 0.355, 0.66, 0.29, 0.13, "Pemberian makan\n(ASI eksklusif,\nmakanan pendamping)")
kotak(ax, 0.68, 0.66, 0.29, 0.13, "Infeksi\n(diare, ISPA,\ninfeksi berulang)")
kotak(ax, 0.03, 0.45, 0.29, 0.13, "Pertumbuhan janin:\nBBLR dan PBLR", tebal=True)
kotak(ax, 0.03, 0.22, 0.26, 0.16, "Karakteristik anak:\njenis kelamin\ndan umur (1000 HPK)", tebal=True)
kotak(ax, 0.335, 0.22, 0.33, 0.16, "Status gizi sebenarnya:\nstunting, wasting,\nunderweight")
kotak(ax, 0.71, 0.22, 0.26, 0.16, "Pengukuran dan pencatatan:\nalat, teknik, pembulatan,\ntanggal ukur, entri data", putus=True)
kotak(ax, 0.19, 0.04, 0.62, 0.11, "Status gizi tercatat di data rutin (SigiziKesga / e-PPGBM)", tebal=True)
for x in (0.175, 0.5, 0.825):
    panah(ax, x, 0.86, x, 0.79)
panah(ax, 0.175, 0.66, 0.175, 0.58)
panah(ax, 0.30, 0.45, 0.40, 0.38)
panah(ax, 0.5, 0.66, 0.5, 0.38)
panah(ax, 0.80, 0.66, 0.62, 0.38)
panah(ax, 0.29, 0.30, 0.335, 0.30)
panah(ax, 0.5, 0.22, 0.5, 0.15)
panah(ax, 0.84, 0.22, 0.76, 0.15, putus=True)
ax.text(0.03, 0.005, "Kotak tebal = faktor yang tersedia di data rutin; garis putus-putus = pengaruh kualitas pengukuran dan pencatatan.", fontsize=8.5, style="italic")
fig.savefig(os.path.join(out, "g0a_kerangka_teori.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- kerangka konsep ----------
fig, ax = kanvas(5.6)
ax.text(0.17, 0.95, "Variabel bebas", ha="center", fontsize=10.5, fontweight="bold")
ax.text(0.80, 0.95, "Variabel terikat", ha="center", fontsize=10.5, fontweight="bold")
for i, t in enumerate(["BBLR", "PBLR", "Jenis kelamin", "Umur"]):
    kotak(ax, 0.03, 0.78 - i * 0.14, 0.28, 0.10, t, tebal=True)
    panah(ax, 0.31, 0.83 - i * 0.14, 0.62, 0.62)
kotak(ax, 0.62, 0.48, 0.35, 0.28, "Status gizi tercatat:\nstunting (TB/U < −2 SD)\nwasting (BB/TB < −2 SD)\nunderweight (BB/U < −2 SD)", tebal=True)
kotak(ax, 0.62, 0.20, 0.35, 0.18, "Kualitas data: preferensi digit,\nsebaran z-score, tanggal ukur,\nperubahan tinggi antarbulan,\ncakupan, kontinuitas", putus=True)
panah(ax, 0.795, 0.38, 0.795, 0.48, putus=True)
kotak(ax, 0.03, 0.06, 0.50, 0.14, "Tidak diteliti: sosial ekonomi, ASI dan makanan\npendamping, infeksi, sanitasi, faktor ibu", putus=True, abu=True)
panah(ax, 0.53, 0.13, 0.66, 0.48, putus=True)
ax.text(0.03, 0.0, "Garis tegas = hubungan yang diuji; garis putus-putus = faktor yang dinilai terpisah atau tidak diteliti.", fontsize=8.5, style="italic")
fig.savefig(os.path.join(out, "g0b_kerangka_konsep.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
print("OK", out)
