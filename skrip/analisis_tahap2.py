"""Tahap 2, analisis 1-5 (prevalensi, tren, antar desa, cakupan, umur & JK). Input: anak_bersih.csv (lokal, gitignored) + sasaran_cakupan.
Pakai: python -I skrip/analisis_tahap2.py <anak_bersih.csv> <sasaran_cakupan_cek2024.xlsx> <folder keluaran tabel>
Titik estimasi = anak-bulan dikumpulkan (sama dengan situs/Laporan Puskesmas). CI 95% = bootstrap klaster per anak (anak yang sama
terukur berulang). Uji hipotesis (antar desa, JK, umur) memakai satu pengukuran acak per anak per tahun supaya sampel bebas.
Skenario S0-S3 dari skrip/bersihkan_data_anak.py. Keluaran hanya agregat."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from bersihkan_data_anak import skenario  # noqa: E402

B, SEED = 500, 20261019
OUTCOME = ["stunting", "wasting", "underweight", "gizi_lebih"]
UTAMA = OUTCOME[:3]
BULAN = [f"{t}-{m:02d}" for t in (2024, 2025, 2026) for m in range(1, 13) if f"{t}-{m:02d}" <= "2026-09"]
IDX = {b: i for i, b in enumerate(BULAN)}
POST0 = IDX["2026-01"]  # titik patah: awal 2026 (cakupan melonjak, pencatatan berubah)
UMUR = [(0, 6, "0-5 bln"), (6, 12, "6-11 bln"), (12, 24, "12-23 bln"), (24, 36, "24-35 bln"), (36, 48, "36-47 bln"), (48, 60, "48-59 bln")]
rng = np.random.default_rng(SEED)


def wilson(k, n):
    if n == 0:
        return np.nan, np.nan
    z, p = 1.96, k / n
    pen = 1 + z * z / n
    c = (p + z * z / (2 * n)) / pen
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / pen
    return 100 * (c - h), 100 * (c + h)


def prev_boot(x, col):
    """x: baris anak-bulan. Kembalikan n_anak, n_valid, kasus, pct, CI klaster."""
    v = x[x[col].notna()]
    if v.empty:
        return dict(n_anak=0, n_valid=0, kasus=0, pct=np.nan, ci_low=np.nan, ci_high=np.nan)
    g = v.groupby("id_anak")[col].agg(["sum", "count"])
    c, n = g["sum"].to_numpy(float), g["count"].to_numpy(float)
    idx = rng.integers(0, len(c), (B, len(c)))
    p = 100 * c[idx].sum(1) / n[idx].sum(1)
    lo, hi = np.percentile(p, [2.5, 97.5])
    return dict(n_anak=len(c), n_valid=int(n.sum()), kasus=int(c.sum()), pct=round(100 * c.sum() / n.sum(), 2),
                ci_low=round(lo, 2), ci_high=round(hi, 2))


def grup_desa(x):
    yield "SEMUA", x
    for desa, y in x.groupby("desa"):
        yield desa, y


def a1(d, sk):
    desa_tahun, bulan = [], []
    for nama, m in sk.items():
        x = d[m]
        for desa, y in grup_desa(x):
            for th, z in y.groupby("tahun"):
                for o in OUTCOME:
                    desa_tahun.append(dict(skenario=nama, desa=desa, tahun=th, outcome=o, **prev_boot(z, o)))
        for b, z in x.groupby("bulan_berkas"):
            for o in OUTCOME:
                v = z[o].dropna()
                lo, hi = wilson(v.sum(), len(v))
                bulan.append(dict(skenario=nama, bulan=b, outcome=o, n_valid=len(v), kasus=int(v.sum()),
                                  pct=round(100 * v.mean(), 2), ci_low=round(lo, 2), ci_high=round(hi, 2)))
    return pd.DataFrame(desa_tahun), pd.DataFrame(bulan)


def seri(d, sk):
    baris = []
    for nama, m in sk.items():
        for desa, y in grup_desa(d[m]):
            for b, z in y.groupby("bulan_berkas"):
                for o in UTAMA:
                    v = z[o].dropna()
                    baris.append(dict(skenario=nama, desa=desa, bulan=b, t=IDX[b], outcome=o, n_valid=len(v), pct=100 * v.mean()))
    return pd.DataFrame(baris)


def nw_ols(X, y, lag=3):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ beta
    xe = X * e[:, None]
    S = xe.T @ xe
    for L in range(1, lag + 1):
        G = xe[L:].T @ xe[:-L]
        S += (1 - L / (lag + 1)) * (G + G.T)
    bread = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(bread @ S @ bread))
    df = len(y) - X.shape[1]
    p = 2 * (1 - stats.t.cdf(np.abs(beta / se), df))
    return beta, se, p


def a2(s):
    tren, seg = [], []
    for (sk, desa, o), g in s.groupby(["skenario", "desa", "outcome"]):
        g = g.sort_values("t")
        if len(g) < 12:
            continue
        tau, p = stats.kendalltau(g["t"], g["pct"])
        sl, _, lo, hi = stats.theilslopes(g["pct"], g["t"])
        tren.append(dict(skenario=sk, desa=desa, outcome=o, n_bulan=len(g), tau=round(tau, 3), p_mk=round(p, 4),
                         sen_pp_per_bulan=round(sl, 3), sen_ci_low=round(lo, 3), sen_ci_high=round(hi, 3),
                         sen_pp_per_tahun=round(12 * sl, 2)))
        post = (g["t"] >= POST0).to_numpy(float)
        if post.sum() >= 6 and (1 - post).sum() >= 6:
            t = g["t"].to_numpy(float)
            X = np.column_stack([np.ones(len(g)), t, post, (t - POST0) * post])
            b, se, pv = nw_ols(X, g["pct"].to_numpy())
            for nm, i in (("level_awal", 0), ("slope_pra_pp_per_bulan", 1), ("lompatan_2026-01_pp", 2), ("perubahan_slope_pp_per_bulan", 3)):
                seg.append(dict(skenario=sk, desa=desa, outcome=o, n_bulan=len(g), parameter=nm, est=round(b[i], 3),
                                se_nw=round(se[i], 3), p=round(pv[i], 4)))
    return pd.DataFrame(tren), pd.DataFrame(seg)


def pertama(x):
    """Satu pengukuran acak (seed tetap) per anak per tahun; 'pertama' bias karena Januari sering anomali."""
    return x.sample(frac=1, random_state=SEED).drop_duplicates(["id_anak", "tahun"], keep="first")


def a3(d, sk):
    baris = []
    for nama, m in sk.items():
        for th, y in pertama(d[m]).groupby("tahun"):
            for o in UTAMA:
                v = y[y[o].notna()]
                tab = pd.crosstab(v["desa"], v[o].astype(int)).reindex(columns=[0, 1], fill_value=0)
                chi2, p, dof, exp = stats.chi2_contingency(tab)
                pt = tab[1].sum() / tab.to_numpy().sum()
                for desa in tab.index:
                    k, n = int(tab.loc[desa, 1]), int(tab.loc[desa].sum())
                    lo, hi = wilson(k, n)
                    e = exp[tab.index.get_loc(desa), 1]
                    rs = (k - e) / np.sqrt(e * (1 - n / tab.to_numpy().sum()) * (1 - pt))
                    baris.append(dict(skenario=nama, tahun=th, outcome=o, desa=desa, n_anak=n, kasus=k, pct=round(100 * k / n, 2),
                                      ci_low=round(lo, 2), ci_high=round(hi, 2), resid_std=round(rs, 2),
                                      chi2=round(chi2, 2), df=dof, p_chi2=round(p, 5)))
    return pd.DataFrame(baris)


def a4(d, sasaran, cakupan):
    t = d[d["desa"].notna()].groupby(["desa", "bulan_berkas"]).agg(terukur=("id_anak", "size")).reset_index()
    sasaran["bulan_berkas"] = sasaran["Tahun"].astype(str) + "-" + sasaran["Bulan"].astype(str).str.zfill(2)
    sas = sasaran.rename(columns={"Desa": "desa", "Total sasaran": "sasaran"})[["desa", "bulan_berkas", "sasaran"]]
    x = t.merge(sas, on=["desa", "bulan_berkas"], how="left")
    x["cakupan_pct"] = (100 * x["terukur"] / x["sasaran"]).round(1)
    bln = x.groupby("bulan_berkas").agg(terukur=("terukur", "sum"), sasaran=("sasaran", lambda s: s.sum(min_count=1))).reset_index()
    bln["cakupan_pct"] = (100 * bln["terukur"] / bln["sasaran"]).round(1)
    # cek silang dengan sheet Cakupan (Laporan Puskesmas, termasuk 8 anak tanpa desa)
    cak = cakupan.copy()
    cak["bulan_berkas"] = cak["Tahun"].astype(str) + "-" + cak["Bulan"].astype(str).str.zfill(2)
    chk = bln.merge(cak[["bulan_berkas", "Terukur (total BB/U, Laporan Puskesmas)", "Sasaran (laporan Sasaran Anak)"]], on="bulan_berkas")
    assert (chk["sasaran"] == chk["Sasaran (laporan Sasaran Anak)"]).all(), "sasaran tidak cocok"
    selisih = (chk["Terukur (total BB/U, Laporan Puskesmas)"] - chk["terukur"]).abs().max()
    assert selisih <= 8, f"terukur selisih {selisih}"
    return x, bln


def umur_jk(d, sk):
    d = d.assign(kel_umur=pd.cut(d["umur_bln"], [u[0] for u in UMUR] + [60], right=False, labels=[u[2] for u in UMUR]))
    tabel, uji = [], []
    for nama in ("S0", "S1"):
        x = d[sk[nama]]
        for (th, jk, ku), z in x.groupby(["tahun", "jk", "kel_umur"], observed=True):
            for o in UTAMA:
                tabel.append(dict(skenario=nama, tahun=th, jk=jk, kel_umur=ku, outcome=o, **prev_boot(z, o)))
        for th, y in pertama(x).groupby("tahun"):
            for o in UTAMA:
                v = y[y[o].notna()]
                for faktor in ("jk", "kel_umur"):
                    tab = pd.crosstab(v[faktor], v[o].astype(int)).reindex(columns=[0, 1], fill_value=0)
                    tab = tab[tab.sum(axis=1) > 0]
                    chi2, p, dof, _ = stats.chi2_contingency(tab)
                    uji.append(dict(skenario=nama, tahun=th, outcome=o, faktor=faktor, n_anak=int(tab.to_numpy().sum()), chi2=round(chi2, 2),
                                    df=dof, p_chi2=round(p, 5)))
    return pd.DataFrame(tabel), pd.DataFrame(uji)


def verifikasi(d, sk, a1_dt, a1_b, a4_x, a5_t):
    # (a) kasus desa-tahun = jumlah dari desa_bulan.csv; (b) SEMUA = jumlah desa; (c) A5 n = A1 n (S0, SEMUA)
    for nama in sk:
        for o in UTAMA:
            dt = a1_dt[(a1_dt.skenario == nama) & (a1_dt.outcome == o)]
            assert dt[dt.desa == "SEMUA"].set_index("tahun")["kasus"].equals(dt[dt.desa != "SEMUA"].groupby("tahun")["kasus"].sum())
            bl = a1_b[(a1_b.skenario == nama) & (a1_b.outcome == o)]
            bl = bl.assign(tahun=bl["bulan"].str[:4].astype(int)).groupby("tahun")["kasus"].sum()
            assert bl.equals(dt[dt.desa == "SEMUA"].set_index("tahun")["kasus"]), (nama, o)
    for o in UTAMA:
        s = a5_t[(a5_t.skenario == "S0") & (a5_t.outcome == o)].groupby("tahun")["n_valid"].sum()
        r = a1_dt[(a1_dt.skenario == "S0") & (a1_dt.outcome == o) & (a1_dt.desa == "SEMUA")].set_index("tahun")["n_valid"]
        assert s.equals(r), ("A5 vs A1", o, s.to_dict(), r.to_dict())
    db = pd.read_csv(Path(__file__).parent.parent / "data/sigizi/analisis/desa_bulan.csv")
    ref = db[db.skenario == "S0"].assign(tahun=lambda z: z.bulan_berkas.str[:4].astype(int)).groupby("tahun")["n_stunting"].sum()
    got = a1_dt[(a1_dt.skenario == "S0") & (a1_dt.outcome == "stunting") & (a1_dt.desa == "SEMUA")].set_index("tahun")["kasus"]
    assert (ref.values == got.values).all(), "tidak cocok dengan desa_bulan.csv"
    print("Verifikasi silang lolos.")


if __name__ == "__main__":
    anak, xlsx, keluar = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    keluar.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(anak, low_memory=False)
    sk = skenario(d)
    a1_dt, a1_b = a1(d, sk)
    s = seri(d, sk)
    a2_t, a2_s = a2(s)
    a3_t = a3(d, sk)
    a4_x, a4_b = a4(d, pd.read_excel(xlsx, sheet_name="Sasaran"), pd.read_excel(xlsx, sheet_name="Cakupan"))
    a5_t, a5_u = umur_jk(d, sk)
    verifikasi(d, sk, a1_dt, a1_b, a4_x, a5_t)
    for nm, df in (("a1_prevalensi_desa_tahun", a1_dt), ("a1_prevalensi_bulan", a1_b), ("a2_seri_bulanan", s), ("a2_tren_mannkendall", a2_t),
                   ("a2_tren_segmented", a2_s), ("a3_antar_desa", a3_t), ("a4_cakupan_desa_bulan", a4_x), ("a4_cakupan_bulan", a4_b),
                   ("a5_umur_jk", a5_t), ("a5_uji_jk_umur", a5_u)):
        df.to_csv(keluar / f"{nm}.csv", index=False, encoding="utf-8")
        print(nm, df.shape)
