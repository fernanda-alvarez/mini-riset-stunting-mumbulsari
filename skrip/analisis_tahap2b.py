"""Tahap 2, analisis 6-9 (distribusi z-score, kurva umur, faktor risiko BBLR/PBLR/JK/umur, longitudinal).
Pakai: python -I skrip/analisis_tahap2b.py <anak_bersih.csv> <folder keluaran tabel>
Memakai fungsi dan konvensi analisis_tahap2.py (bootstrap klaster per anak, skenario S0-S3). Keluaran hanya agregat.
Regresi logistik ditulis sendiri (statsmodels tidak bisa dipasang di ARM64): IRLS + SE robust klaster per anak, dengan self-test."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from analisis_tahap2 import B, IDX, UMUR, UTAMA, grup_desa, rng  # noqa: E402
from bersihkan_data_anak import skenario  # noqa: E402

Z = {"zs_tbu": "kat_tbu", "zs_bbu": "kat_bbu", "zs_bbtb": "kat_bbtb"}


def boot_mean(x, col):
    """Rerata col (anak-bulan) dengan CI bootstrap klaster per anak."""
    v = x[x[col].notna()]
    if v.empty:
        return dict(n_anak=0, n=0, mean=np.nan, ci_low=np.nan, ci_high=np.nan)
    g = v.groupby("id_anak")[col].agg(["sum", "count"])
    c, n = g["sum"].to_numpy(float), g["count"].to_numpy(float)
    idx = rng.integers(0, len(c), (B, len(c)))
    m = c[idx].sum(1) / n[idx].sum(1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return dict(n_anak=len(c), n=int(n.sum()), mean=round(c.sum() / n.sum(), 4), ci_low=round(lo, 4), ci_high=round(hi, 4))


def zvalid(z, zc):
    kc = Z[zc]
    return z[(z[kc] != "Outlier") & z[zc].notna() & (z[zc].abs() < 99)]


# ---------- Analisis 6: distribusi z-score ----------
def a6(d, sk):
    ring, hist, bulanan = [], [], []
    bins = np.arange(-6, 6.25, 0.25)
    for nama in ("S0", "S3"):
        x = d[sk[nama]]
        for desa, y in grup_desa(x):
            for th, z in y.groupby("tahun"):
                for zc in Z:
                    v = zvalid(z, zc)
                    if len(v) < 30:
                        continue
                    s = v[zc]
                    r = dict(skenario=nama, desa=desa, tahun=th, zscore=zc, **boot_mean(v, zc), sd=round(s.std(), 3), skew=round(s.skew(), 3),
                             p5=round(s.quantile(.05), 2), p25=round(s.quantile(.25), 2), median=round(s.median(), 2),
                             p75=round(s.quantile(.75), 2), p95=round(s.quantile(.95), 2), pct_di_bawah_min2=round(100 * (s < -2).mean(), 2))
                    if zc == "zs_tbu":
                        atas, bawah = ((s >= -2.0) & (s < -1.9)).sum(), ((s >= -2.1) & (s < -2.0)).sum()
                        r.update(n_min2_0_min1_9=int(atas), n_min2_1_min2_0=int(bawah), rasio_tumpuk=round(atas / bawah, 2) if bawah else np.nan)
                    ring.append(r)
                    if nama == "S0" and zc == "zs_tbu":
                        cnt, _ = np.histogram(s.clip(-5.99, 5.99), bins)
                        hist += [dict(desa=desa, tahun=th, bin_awal=round(b, 2), n=int(c)) for b, c in zip(bins[:-1], cnt)]
        if nama == "S0":
            for desa, y in grup_desa(x):
                for b, z in y.groupby("bulan_berkas"):
                    for zc in Z:
                        v = zvalid(z, zc)[zc]
                        if len(v) >= 30:
                            bulanan.append(dict(desa=desa, bulan=b, zscore=zc, n=len(v), mean=round(v.mean(), 3), sd=round(v.std(), 3)))
    return pd.DataFrame(ring), pd.DataFrame(hist), pd.DataFrame(bulanan)


# ---------- Analisis 7: kurva umur ----------
def a7(d, sk):
    d = d.assign(umur3=(d["umur_bln"] // 3 * 3).clip(0, 57))
    baris = []
    for nama in ("S0", "S3"):
        x = d[sk[nama]]
        for (th, u3), z in x.groupby(["tahun", "umur3"]):
            r = dict(skenario=nama, tahun=th, umur_awal_bln=int(u3), n=len(z))
            for zc in Z:
                b = boot_mean(zvalid(z, zc), zc)
                r.update({f"{zc}_mean": b["mean"], f"{zc}_lo": b["ci_low"], f"{zc}_hi": b["ci_high"]})
            for o in UTAMA:
                b = boot_mean(z, o)
                r.update({f"{o}_pct": round(100 * b["mean"], 2), f"{o}_lo": round(100 * b["ci_low"], 2), f"{o}_hi": round(100 * b["ci_high"], 2)})
            baris.append(r)
    return pd.DataFrame(baris)


# ---------- Analisis 8: faktor risiko (regresi logistik, SE robust klaster) ----------
def logit_cluster(X, y, cl, iters=40):
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
        H = X.T @ (X * (p * (1 - p))[:, None])
        step = np.linalg.solve(H, X.T @ (y - p))
        beta += step
        if np.abs(step).max() < 1e-9:
            break
    p = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
    H = X.T @ (X * (p * (1 - p))[:, None])
    order = np.argsort(cl, kind="stable")
    cs = cl[order]
    starts = np.r_[0, np.flatnonzero(cs[1:] != cs[:-1]) + 1]
    S = np.add.reduceat((X * (y - p)[:, None])[order], starts, axis=0)
    bread = np.linalg.inv(H)
    G = len(starts)
    V = G / (G - 1) * bread @ (S.T @ S) @ bread
    return beta, np.sqrt(np.diag(V)), G


def selftest():
    r = np.random.default_rng(1)
    x = (r.random(5000) < .3).astype(float)
    y = (r.random(5000) < np.where(x == 1, .2, .1)).astype(float)
    a, b, c, d_ = ((x == 1) & (y == 1)).sum(), ((x == 1) & (y == 0)).sum(), ((x == 0) & (y == 1)).sum(), ((x == 0) & (y == 0)).sum()
    beta, se, _ = logit_cluster(np.column_stack([np.ones(5000), x]), y, np.arange(5000))
    assert abs(beta[1] - np.log(a * d_ / (b * c))) < 1e-6, "logit != OR silang"
    assert abs(se[1] - np.sqrt(1 / a + 1 / b + 1 / c + 1 / d_)) / se[1] < 0.02, "SE robust != SE Woolf (klaster=baris)"


MODEL = {"A": ["bblr"], "B": ["pblr"], "C": ["bblr", "pblr"]}


def a8(d, sk):
    d = d.assign(kel=pd.cut(d["umur_bln"], [u[0] for u in UMUR] + [60], right=False, labels=[u[2] for u in UMUR]).astype(str),
                 stratum=d["desa"].astype(str) + "_" + d["tahun"].astype(str), jk_p=(d["jk"] == "P").astype(float))
    baris = []
    for nama in ("S0", "S1", "S3"):
        for o in UTAMA:
            for mn, faktor in MODEL.items():
                x = d[sk[nama] & d[o].notna() & d[faktor].notna().all(axis=1)]
                sm = x.groupby("stratum")[o].mean()
                x = x[x["stratum"].isin(sm[(sm > 0) & (sm < 1)].index)]  # strata tanpa variasi outcome tidak informatif
                kolom = [np.ones(len(x))] + [x[f].to_numpy(float) for f in faktor] + [x["jk_p"].to_numpy(float)]
                nama_k = ["const"] + faktor + ["jk_P"]
                for k in [u[2] for u in UMUR[1:]]:
                    kolom.append((x["kel"] == k).to_numpy(float)); nama_k.append(f"umur_{k}")
                for s in sorted(x["stratum"].unique())[1:]:
                    kolom.append((x["stratum"] == s).to_numpy(float)); nama_k.append(f"FE_{s}")
                X = np.column_stack(kolom)
                beta, se, G = logit_cluster(X, x[o].to_numpy(float), pd.factorize(x["id_anak"])[0])
                for i, k in enumerate(nama_k):
                    if k.startswith("FE_") or k == "const":
                        continue
                    z = beta[i] / se[i]
                    baris.append(dict(skenario=nama, outcome=o, model=mn, term=k, OR=round(np.exp(beta[i]), 3),
                                      ci_low=round(np.exp(beta[i] - 1.96 * se[i]), 3), ci_high=round(np.exp(beta[i] + 1.96 * se[i]), 3),
                                      p=round(2 * (1 - stats.norm.cdf(abs(z))), 5), n_obs=len(x), n_anak=G, n_kasus=int(x[o].sum())))
    return pd.DataFrame(baris)


# ---------- Analisis 9: longitudinal ----------
def pasangan(x):
    x = x[["id_anak", "bulan_berkas", "desa", "tahun", "umur_bln", "tinggi", "stunting", "wasting"]].copy()
    x["t"] = x["bulan_berkas"].map(IDX)
    x = x.sort_values(["id_anak", "t"])
    nxt = x.groupby("id_anak").shift(-1)
    ok = nxt["t"] == x["t"] + 1
    p = x[ok].copy()
    for o in ("stunting", "wasting"):
        a, b = p[o], nxt.loc[ok, o]
        p[f"{o}_ins"] = b.where(a == 0)
        p[f"{o}_pem"] = (1 - b).where(a == 1)
        p[f"{o}_flip"] = (a != b).astype(float).where(a.notna() & b.notna())
    p["dtinggi"] = nxt.loc[ok, "tinggi"] - p["tinggi"]
    p["turun1"] = (p["dtinggi"] <= -1).astype(float).where(p["dtinggi"].notna())
    p["naik5"] = (p["dtinggi"] >= 5).astype(float).where(p["dtinggi"].notna())
    return p


def a9_transisi(d, sk):
    trans, tumbuh = [], []
    for nama in ("S0", "S1", "S3"):
        p = pasangan(d[sk[nama]])
        for desa, y in grup_desa(p):
            for th, z in y.groupby("tahun"):
                for o in ("stunting", "wasting"):
                    for m in ("ins", "pem", "flip"):
                        b = boot_mean(z, f"{o}_{m}")
                        trans.append(dict(skenario=nama, desa=desa, tahun=th, outcome=o, ukuran={"ins": "insiden_per_bulan", "pem": "pemulihan_per_bulan", "flip": "berubah_status"}[m],
                                          n_pasangan=b["n"], n_anak=b["n_anak"], pct=round(100 * b["mean"], 2), ci_low=round(100 * b["ci_low"], 2), ci_high=round(100 * b["ci_high"], 2)))
        if nama == "S0":
            p["kel"] = pd.cut(p["umur_bln"], [u[0] for u in UMUR] + [60], right=False, labels=[u[2] for u in UMUR]).astype(str)
            for (desa, th), z in [(("SEMUA", t), g) for t, g in p.groupby("tahun")] + list(p.groupby(["desa", "tahun"])):
                v = z[z["dtinggi"].notna()]
                tumbuh.append(dict(desa=desa, tahun=th, kel_umur="semua", n_pasangan=len(v), mean_cm=round(v["dtinggi"].mean(), 3), sd_cm=round(v["dtinggi"].std(), 3),
                                   pct_turun_ge1cm=round(100 * v["turun1"].mean(), 2), pct_naik_ge5cm=round(100 * v["naik5"].mean(), 2)))
            for (th, k), z in p.groupby(["tahun", "kel"]):
                v = z[z["dtinggi"].notna()]
                tumbuh.append(dict(desa="SEMUA", tahun=th, kel_umur=k, n_pasangan=len(v), mean_cm=round(v["dtinggi"].mean(), 3), sd_cm=round(v["dtinggi"].std(), 3),
                                   pct_turun_ge1cm=round(100 * v["turun1"].mean(), 2), pct_naik_ge5cm=round(100 * v["naik5"].mean(), 2)))
    return pd.DataFrame(trans), pd.DataFrame(tumbuh)


def km_kohort(d, sk, nama):
    """Waktu (bulan) sampai stunting pertama, anak yang pertama kali terlihat tidak stunting pada umur < 24 bulan."""
    x = d[sk[nama] & d["stunting"].notna()].copy()
    x["t"] = x["bulan_berkas"].map(IDX)
    x = x.sort_values(["id_anak", "t"])
    pertama = x.groupby("id_anak").first()
    k = pertama[(pertama["stunting"] == 0) & (pertama["umur_bln"] < 24)][["t", "tahun", "jk", "bblr", "umur_bln"]].rename(columns={"t": "t0", "tahun": "tahun_masuk"})
    ev = x[x["stunting"] == 1].groupby("id_anak")["t"].min()
    akhir = x.groupby("id_anak")["t"].max()
    k["t_ev"] = ev.reindex(k.index)
    k["waktu"] = np.where(k["t_ev"].notna(), k["t_ev"] - k["t0"], akhir.reindex(k.index) - k["t0"])
    k["event"] = k["t_ev"].notna().astype(int)
    k["masuk_umur"] = pd.cut(k["umur_bln"], [0, 6, 12, 24], right=False, labels=["0-5", "6-11", "12-23"]).astype(str)
    return k[k["waktu"] > 0]


def km(g):
    out, S, var = [], 1.0, 0.0
    for t in range(1, int(g["waktu"].max()) + 1):
        nr = (g["waktu"] >= t).sum()
        dt = ((g["waktu"] == t) & (g["event"] == 1)).sum()
        if nr == 0:
            break
        S *= 1 - dt / nr
        var += dt / (nr * (nr - dt)) if nr > dt else 0
        se = S * np.sqrt(var)
        out.append(dict(waktu_bln=t, n_berisiko=int(nr), kejadian=int(dt), S=round(S, 4), ci_low=round(max(S - 1.96 * se, 0), 4), ci_high=round(min(S + 1.96 * se, 1), 4)))
    return out


def logrank(a, b):
    O = E = V = 0.0
    for t in range(1, int(max(a["waktu"].max(), b["waktu"].max())) + 1):
        n1, n2 = (a["waktu"] >= t).sum(), (b["waktu"] >= t).sum()
        n = n1 + n2
        dd = ((a["waktu"] == t) & (a["event"] == 1)).sum() + ((b["waktu"] == t) & (b["event"] == 1)).sum()
        if n < 2 or dd == 0:
            continue
        O += ((a["waktu"] == t) & (a["event"] == 1)).sum()
        E += dd * n1 / n
        V += dd * (n1 / n) * (1 - n1 / n) * (n - dd) / (n - 1)
    chi2 = (O - E) ** 2 / V
    return round(chi2, 2), round(1 - stats.chi2.cdf(chi2, 1), 5)


def a9_km(d, sk):
    kurva, lr = [], []
    for nama in ("S0", "S3"):
        k = km_kohort(d, sk, nama)
        strata = [("semua", "semua", k)]
        for kolom in ("tahun_masuk", "jk", "bblr", "masuk_umur"):
            for v, g in k.dropna(subset=[kolom]).groupby(kolom):
                strata.append((kolom, str(v), g))
        for fak, v, g in strata:
            kurva += [dict(skenario=nama, faktor=fak, nilai=v, n_anak=len(g), n_kejadian=int(g["event"].sum()), **r) for r in km(g)]
        for kolom in ("jk", "bblr"):
            gg = [g for _, g in k.dropna(subset=[kolom]).groupby(kolom)]
            lr.append(dict(skenario=nama, faktor=kolom, n_anak=sum(len(g) for g in gg), n_kejadian=int(sum(g["event"].sum() for g in gg)), chi2=logrank(*gg)[0], p=logrank(*gg)[1]))
    return pd.DataFrame(kurva), pd.DataFrame(lr)


def verifikasi(d, sk, trans, km_k):
    n_baris = len(d[sk["S0"]])
    t = trans[(trans.skenario == "S0") & (trans.desa == "SEMUA") & (trans.outcome == "stunting") & (trans.ukuran == "berubah_status")]
    assert t["n_pasangan"].sum() < n_baris, "pasangan > baris"
    for _, g in km_k.groupby(["skenario", "faktor", "nilai"]):
        assert g["S"].is_monotonic_decreasing, "KM tidak menurun"
    print("Verifikasi analisis 6-9 lolos.")


if __name__ == "__main__":
    anak, keluar = Path(sys.argv[1]), Path(sys.argv[2])
    keluar.mkdir(parents=True, exist_ok=True)
    selftest()
    d = pd.read_csv(anak, low_memory=False)
    sk = skenario(d)
    a6_r, a6_h, a6_b = a6(d, sk)
    a7_t = a7(d, sk)
    a8_t = a8(d, sk)
    a9_t, a9_g = a9_transisi(d, sk)
    a9_k, a9_l = a9_km(d, sk)
    verifikasi(d, sk, a9_t, a9_k)
    for nm, df in (("a6_zscore_ringkas", a6_r), ("a6_zscore_histogram_tbu_s0", a6_h), ("a6_zscore_bulanan_s0", a6_b), ("a7_kurva_umur", a7_t),
                   ("a8_faktor_risiko", a8_t), ("a9_transisi_status", a9_t), ("a9_kecepatan_tumbuh", a9_g), ("a9_km_stunting", a9_k), ("a9_logrank", a9_l)):
        df.to_csv(keluar / f"{nm}.csv", index=False, encoding="utf-8")
        print(nm, df.shape)
