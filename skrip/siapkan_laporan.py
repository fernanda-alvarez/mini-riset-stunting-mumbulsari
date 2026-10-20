"""Siapkan bahan laporan akhir: gambar PNG dan tabel_laporan.json (angka berformat Indonesia) dari tabel analisis + anak_bersih.csv.
Pakai: python -I skrip/siapkan_laporan.py <data/sigizi/analisis> <anak_bersih.csv> <folder keluaran laporan>
Hanya agregat yang ditulis. Laporan Word dibangun terpisah oleh skrip/bangun_laporan.js dari berkas ini."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import norm  # noqa: E402

DESA = ["KARANGKEDAWUNG", "KAWANGREJO", "LAMPEJI", "LENGKONG", "MUMBULSARI", "SUCO", "TAMANSARI"]
SINGKAT = dict(zip(DESA, ["KD", "KW", "LP", "LK", "MB", "SC", "TS"]))
TAHUN = [2024, 2025, 2026]
WARNA = {2024: "#4C78A8", 2025: "#F58518", 2026: "#54A24B"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "figure.dpi": 100})


def f(x, n=1):
    if pd.isna(x):
        return "–"
    x = np.sign(x) * np.floor(abs(x) * 10 ** n + 0.5 + 1e-9) / 10 ** n  # bulatkan ke atas seperti Excel
    return f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


KOMA = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))  # sumbu desimal gaya Indonesia


def nm(d):
    return "Seluruh Puskesmas" if d == "SEMUA" else d.title()


def simpan(fig, folder, nama):
    fig.tight_layout()
    fig.savefig(folder / f"{nama}.png", dpi=200)
    plt.close(fig)


def main(analisis, anak, keluar):
    analisis, keluar = Path(analisis), Path(keluar)
    gam = keluar / "gambar"
    gam.mkdir(parents=True, exist_ok=True)
    T = lambda n: pd.read_csv(analisis / "tabel" / f"{n}.csv")
    a1, a4, a6, a7, a8, a9k, a9t = T("a1_prevalensi_desa_tahun"), T("a4_cakupan_bulan"), T("a6_zscore_ringkas"), T("a7_kurva_umur"), T("a8_faktor_risiko"), T("a9_km_stunting"), T("a9_transisi_status")
    hist = T("a6_zscore_histogram_tbu_s0")
    d = pd.read_csv(anak, low_memory=False)
    tb = {}

    # ---- Tabel 1: karakteristik data (S0) ----
    from importlib import import_module
    sys.path.insert(0, str(Path(__file__).parent))
    s0 = import_module("bersihkan_data_anak").skenario(d)["S0"]
    x = d[s0]
    rows = []
    for th in TAHUN:
        y = x[x.tahun == th]
        ch = y.drop_duplicates("id_anak")
        rows.append([str(th), f(len(d[d.tahun == th]), 0), f(len(y), 0), f(y.id_anak.nunique(), 0), f(100 * (ch.jk == "P").mean()), f(y.umur_bln.mean()),
                     f(100 * ch.bblr.mean()), f(100 * ch.pblr.mean())])
    tb["t1"] = {"kepala": ["Tahun", "Pengukuran mentah", "Pengukuran dianalisis (S0)", "Anak unik", "Perempuan (%)", "Rerata umur (bln)", "BBLR (%)", "PBLR (%)"], "baris": rows}

    # ---- Tabel 2: prevalensi stunting per desa-tahun (S0) ----
    P = a1[(a1.skenario == "S0") & (a1.outcome == "stunting")]
    rows = []
    for ds in ["SEMUA"] + DESA:
        r = [nm(ds)]
        for th in TAHUN:
            z = P[(P.desa == ds) & (P.tahun == th)].iloc[0]
            r.append(f"{f(z.pct)} ({f(z.ci_low)}–{f(z.ci_high)})")
        rows.append(r)
    tb["t2"] = {"kepala": ["Desa", "2024", "2025", "2026"], "baris": rows}
    rows = []
    for o, jud in (("wasting", "Wasting"), ("underweight", "Underweight")):
        for ds in ["SEMUA"] + DESA:
            r = [jud, nm(ds)]
            for th in TAHUN:
                z = a1[(a1.skenario == "S0") & (a1.outcome == o) & (a1.desa == ds) & (a1.tahun == th)].iloc[0]
                r.append(f"{f(z.pct)} ({f(z.ci_low)}–{f(z.ci_high)})")
            rows.append(r)
    tb["tL1"] = {"kepala": ["Outcome", "Desa", "2024", "2025", "2026"], "baris": rows}

    # ---- Tabel 3: kualitas data ----
    flags = [("f_zs_penanda", "Z-score penanda (|ZS| ≥ 999)", "keras"), ("f_nol", "Tinggi atau berat 0", "keras"), ("f_aneh", "Berat > 40 kg atau tinggi > 130 cm", "keras"),
             ("f_umur_luar", "Umur di luar 0–<60 bulan", "keras"), ("f_keras", "Gabungan flag keras", "keras"), ("f_tbu_outlier", "TB/U Outlier", "informasi"),
             ("f_cara_ukur_salah", "Cara ukur tidak sesuai umur", "informasi"), ("f_pos_kosong", "Posyandu kosong", "informasi"),
             ("f_tgl_seragam", "Satu tanggal ukur ≥ 30% anak desa-bulan", "informasi"), ("f_anomali_desabulan", "Desa-bulan anomali", "lunak (S3)"),
             ("f_heaping_tinggi", "Desa-tahun heaping tinggi ≥ 70%", "lunak (S2)")]
    rows = []
    for k, lab, jn in flags:
        rows.append([lab, jn] + [f"{f(d[d.tahun == th][k].sum(), 0)} ({f(100 * d[d.tahun == th][k].mean())}%)" for th in TAHUN])
    tb["t3"] = {"kepala": ["Masalah kualitas", "Jenis", "2024", "2025", "2026"], "baris": rows}

    # ---- Tabel 4: heaping dan diharapkan vs tercatat (S3, TB/U) ----
    z = a6[(a6.skenario == "S3") & (a6.zscore == "zs_tbu")].copy()
    z["harapan"] = 100 * norm.cdf((-2 - z["mean"]) / z["sd"])
    hp = d.groupby(["desa", "tahun"])["pct_heaping_desa_tahun"].first() * 100
    rows = []
    for ds in ["SEMUA"] + DESA:
        for th in TAHUN:
            r = z[(z.desa == ds) & (z.tahun == th)].iloc[0]
            rows.append([nm(ds), str(th), "–" if ds == "SEMUA" else f(hp[(ds, th)], 0), f(r["mean"], 2), f(r.sd, 2), f(r.pct_di_bawah_min2), f(r.harapan), f(r.rasio_tumpuk)])
    tb["t4"] = {"kepala": ["Desa", "Tahun", "Tinggi bulat (%)", "Rerata z TB/U", "SD", "Tercatat < −2 SD (%)", "Diharapkan (%)", "Rasio penumpukan"], "baris": rows}

    # ---- Tabel 5: faktor risiko (model C, S3) ----
    m = a8[(a8.model == "C") & (a8.skenario == "S3")]
    nmf = {"bblr": "BBLR (<2.500 g)", "pblr": "PBLR (<48 cm)", "jk_P": "Perempuan (vs laki-laki)"}
    rows = []
    for t, lab in nmf.items():
        r = [lab]
        for o in ("stunting", "wasting", "underweight"):
            z_ = m[(m.outcome == o) & (m.term == t)].iloc[0]
            r.append(f"{f(z_.OR, 2)} ({f(z_.ci_low, 2)}–{f(z_.ci_high, 2)})")
            r.append("<0,001" if z_.p < 0.001 else f(z_.p, 3))
        rows.append(r)
    n0 = m[m.outcome == "stunting"].iloc[0]
    tb["t5"] = {"kepala": ["Faktor", "Stunting OR (IK 95%)", "p", "Wasting OR (IK 95%)", "p", "Underweight OR (IK 95%)", "p"], "baris": rows,
                "n": [int(n0.n_obs), int(n0.n_anak), int(n0.n_kasus)]}
    rb = a8[(a8.outcome == "stunting") & a8.term.isin(["bblr", "pblr", "jk_P"])]
    rows = []
    for t, mod in (("bblr", "A"), ("bblr", "C"), ("pblr", "B"), ("pblr", "C"), ("jk_P", "C")):
        r = [nmf[t], mod]
        for sk in ("S0", "S1", "S3"):
            z_ = rb[(rb.skenario == sk) & (rb.model == mod) & (rb.term == t)].iloc[0]
            r.append(f"{f(z_.OR, 2)} ({f(z_.ci_low, 2)}–{f(z_.ci_high, 2)})")
        rows.append(r)
    tb["tL2"] = {"kepala": ["Faktor", "Model", "S0", "S1", "S3"], "baris": rows}

    # ---- Tabel 6: cakupan ----
    c = a4.dropna(subset=["sasaran"]).assign(th=lambda z_: z_.bulan_berkas.str[:4])
    rows = [[th, f(g.sasaran.mean(), 0), f(g.terukur.mean(), 0), f(g.cakupan_pct.min(), 0) + "–" + f(g.cakupan_pct.max(), 0)] for th, g in c.groupby("th")]
    tb["t6"] = {"kepala": ["Tahun", "Sasaran rerata/bulan", "Terukur rerata/bulan", "Cakupan (%, rentang bulanan)"], "baris": rows}

    # ---- Tabel 7: longitudinal ringkas (S3 KM; S0 transisi SEMUA) ----
    k = a9k[(a9k.skenario == "S3") & a9k.faktor.isin(["bblr", "jk"])]
    rows = []
    for fak, nil, lab in (("bblr", "0.0", "Tanpa BBLR"), ("bblr", "1.0", "BBLR"), ("jk", "L", "Laki-laki"), ("jk", "P", "Perempuan")):
        g = k[(k.faktor == fak) & (k.nilai == nil)]
        s12, s24 = g[g.waktu_bln == 12].iloc[0], g[g.waktu_bln == 24].iloc[0]
        rows.append([lab, f(s12.n_anak, 0), f(s12.n_kejadian, 0), f(100 * s12.S, 0) + "%", f(100 * s24.S, 0) + "%"])
    tb["t7"] = {"kepala": ["Kelompok", "Anak", "Kejadian stunting (seluruh pengamatan)", "Belum stunting 12 bln", "Belum stunting 24 bln"], "baris": rows}

    # ---- Gambar 1: prevalensi stunting per desa-tahun ----
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    urut = ["SEMUA"] + DESA
    w = 0.26
    for i, th in enumerate(TAHUN):
        z_ = P[P.tahun == th].set_index("desa").reindex(urut)
        ax.bar(np.arange(len(urut)) + (i - 1) * w, z_.pct, w, color=WARNA[th], label=str(th), yerr=[z_.pct - z_.ci_low, z_.ci_high - z_.pct], error_kw={"lw": .8, "capsize": 1.5})
    ax.set_xticks(range(len(urut)), [nm(u).replace("Seluruh Puskesmas", "Puskesmas") for u in urut], rotation=30, ha="right")
    ax.set_ylabel("Stunting (% anak-bulan)")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    simpan(fig, gam, "g1_prevalensi_desa_tahun")

    # ---- Gambar 2: histogram z-score TB/U ----
    h = hist[hist.desa == "SEMUA"].pivot(index="bin_awal", columns="tahun", values="n")
    h = (100 * h / h.sum())
    h = h[(h.index >= -5) & (h.index <= 4)]
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    for th in TAHUN:
        ax.plot(h.index + .125, h[th], color=WARNA[th], label=str(th), lw=1.6)
    ax.axvline(-2, color="k", ls="--", lw=.8)
    ax.text(-1.95, ax.get_ylim()[1] * .92, "−2 SD", fontsize=8)
    ax.set_xlabel("z-score TB/U")
    ax.set_ylabel("% anak per interval 0,25 SD")
    ax.legend(frameon=False)
    simpan(fig, gam, "g2_histogram_zscore")

    # ---- Gambar 3: tercatat vs diharapkan ----
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    zz = z[z.desa != "SEMUA"]
    BENTUK = dict(zip(DESA, "osD^vPX"))  # bentuk = desa, warna = tahun; label teks bertumpuk di gugus 15-20%
    for _, r in zz.iterrows():
        ax.scatter(r.harapan, r.pct_di_bawah_min2, color=WARNA[r.tahun], marker=BENTUK[r.desa], s=36, zorder=3, edgecolor="k", lw=.3)
    lim = max(zz.harapan.max(), zz.pct_di_bawah_min2.max()) + 3
    ax.plot([0, lim], [0, lim], color="gray", ls="--", lw=.8)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("Diharapkan bila z-score normal (% < −2 SD)")
    ax.set_ylabel("Tercatat (% < −2 SD)")
    ax.set_aspect("equal")
    from matplotlib.lines import Line2D
    l1 = ax.legend([Line2D([], [], marker="o", ls="", color=WARNA[t]) for t in TAHUN], [str(t) for t in TAHUN], frameon=False, title="Tahun", loc="upper left", bbox_to_anchor=(1.02, 1))
    ax.add_artist(l1)
    ax.legend([Line2D([], [], marker=BENTUK[d_], ls="", color="gray", markeredgecolor="k", markeredgewidth=.3) for d_ in DESA], [nm(d_) for d_ in DESA], frameon=False, title="Desa", loc="upper left", bbox_to_anchor=(1.02, .62))
    simpan(fig, gam, "g3_tercatat_vs_diharapkan")

    # ---- Gambar 4: kurva umur ----
    q = a7[a7.skenario == "S3"]
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    for th in TAHUN:
        g = q[q.tahun == th]
        ax.plot(g.umur_awal_bln, g.zs_tbu_mean, color=WARNA[th], label=str(th), lw=1.6)
    ax.set_xlabel("Umur (bulan, awal interval 3 bulan)")
    ax.set_ylabel("Rerata z-score TB/U")
    ax.yaxis.set_major_formatter(KOMA)
    ax.legend(frameon=False)
    simpan(fig, gam, "g4_kurva_umur")

    # ---- Gambar 5: forest plot OR ----
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    pos, lab = 0, []
    warna_o = {"stunting": "#4C78A8", "wasting": "#E45756", "underweight": "#72B7B2"}
    for t in ("bblr", "pblr", "jk_P"):
        for o in ("stunting", "wasting", "underweight"):
            r = m[(m.outcome == o) & (m.term == t)].iloc[0]
            ax.errorbar(r.OR, pos, xerr=[[r.OR - r.ci_low], [r.ci_high - r.OR]], fmt="o", color=warna_o[o], capsize=2, ms=4, label=o.title() if t == "bblr" else None)
            pos -= 1
        pos -= .6
        lab.append(nmf[t])
    ax.axvline(1, color="k", lw=.8)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 0.7, 1, 1.5, 2, 3], ["0,5", "0,7", "1", "1,5", "2", "3"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks([-1, -4.6, -8.2], lab)
    ax.set_xlabel("Odds ratio (IK 95%), skala logaritmik")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    simpan(fig, gam, "g5_forest_faktor_risiko")

    # ---- Gambar 6: Kaplan-Meier BBLR ----
    fig, ax = plt.subplots(figsize=(6.0, 3.7))
    titik = [1, 6, 12, 18, 24, 30]
    ax.text(-.02, -.32, "Berisiko:", transform=ax.transAxes, ha="right", va="top", fontsize=7.5)
    for j, (nil, lab_, col) in enumerate((("0.0", "Tanpa BBLR", "#4C78A8"), ("1.0", "BBLR", "#E45756"))):
        g = k[(k.faktor == "bblr") & (k.nilai == nil)]
        ax.plot(g.waktu_bln, g.S, color=col, label=lab_, lw=1.8)
        ax.fill_between(g.waktu_bln, g.ci_low, g.ci_high, color=col, alpha=.15)
        nr = g.set_index("waktu_bln").n_berisiko
        for t in titik:
            ax.text(t, -.32 - .08 * j, f(nr.get(t, np.nan), 0), transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7.5, color=col)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(KOMA)
    ax.set_xlabel("Bulan sejak pertama kali terlihat tidak stunting")
    ax.set_ylabel("Proporsi belum stunting")
    ax.legend(frameon=False)
    simpan(fig, gam, "g6_kaplan_meier_bblr")

    # ---- Gambar 7: cakupan ----
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    cc = a4.dropna(subset=["cakupan_pct"])
    ax.plot(cc.bulan_berkas, cc.cakupan_pct, color="#4C78A8", marker="o", ms=3)
    ax.set_xticks(range(0, len(cc), 3), cc.bulan_berkas.iloc[::3], rotation=45, ha="right")
    ax.set_ylabel("Cakupan (% terukur / sasaran)")
    ax.set_ylim(0, 105)
    simpan(fig, gam, "g7_cakupan")

    (keluar / "tabel_laporan.json").write_text(json.dumps(tb, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK", sorted(p.name for p in gam.glob("*.png")), list(tb))


if __name__ == "__main__":
    main(*sys.argv[1:4])
