"""Analisis tambahan P1-P3 (20 Okt 2026), diusulkan saat telaah laporan. Keluaran hanya agregat.
Pakai: python -I skrip/analisis_tahap2c.py <anak_bersih.csv> <who_lhfa_lms.csv> <folder keluaran>
who_lhfa_lms.csv = tabel LMS TB/U WHO 2006 dari paket R 'anthro':
  Rscript -e "write.csv(anthro:::growthstandards_lenanthro, 'who_lhfa_lms.csv', row.names=FALSE)"
P1: Kaplan-Meier dengan kejadian terkonfirmasi (dua pengukuran berurutan < -2 SD, jarak <= 3 bulan), skala umur dengan
    delayed entry, log-rank terstratifikasi desa. P2: jumlah bulan terukur per anak. P3: penumpukan z-score di atas -2 SD
    menurut digit desimal tinggi, dan simulasi pembulatan tinggi memakai LMS WHO (L = 1 untuk TB/U, jadi z linear terhadap tinggi)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from analisis_tahap2 import IDX  # noqa: E402
from analisis_tahap2b import km_kohort, logrank as logrank_lama, zvalid  # noqa: E402
from bersihkan_data_anak import skenario  # noqa: E402

SEED, ULANG = 20261019, 20
JEDA_MAKS = 3  # bulan; pengukuran berikutnya yang lebih jauh tidak dipakai untuk konfirmasi
HARI_PER_BLN = 30.4375


# ---------- P1 ----------
def kohort(d, mask, konfirmasi):
    """Anak yang pertama kali terlihat tidak stunting pada umur < 24 bulan; kejadian = stunting pertama (terkonfirmasi bila diminta)."""
    x = d[mask & d["stunting"].notna()].copy()
    x["t"] = x["bulan_berkas"].map(IDX)
    x = x.sort_values(["id_anak", "t"])
    g = x.groupby("id_anak")
    ev = x["stunting"] == 1
    if konfirmasi:
        ev &= (g["stunting"].shift(-1) == 1) & (g["t"].shift(-1) - x["t"] <= JEDA_MAKS)
    pertama = g.first()
    k = pertama[(pertama["stunting"] == 0) & (pertama["umur_bln"] < 24)][["t", "umur_bln", "jk", "bblr", "desa"]].rename(columns={"t": "t0", "umur_bln": "u0"})
    k = k.join(x[ev].groupby("id_anak")[["t", "umur_bln"]].first().add_suffix("_ev")).join(g[["t", "umur_bln"]].last().add_suffix("_akhir"))
    k["event"] = k["t_ev"].notna().astype(int)
    k["waktu"] = np.where(k["event"] == 1, k["t_ev"], k["t_akhir"]) - k["t0"]
    k["umur_keluar"] = np.where(k["event"] == 1, k["umur_bln_ev"], k["umur_bln_akhir"])
    k["masuk_umur"] = pd.cut(k["u0"], [0, 6, 12, 24], right=False, labels=["0-5", "6-11", "12-23"]).astype(str)
    return k[k["waktu"] > 0]


def km_titik(masuk, keluar, event, titik):
    """Product-limit dengan delayed entry: berisiko pada t bila masuk < t <= keluar. Kembalikan S pada tiap titik."""
    S, kurva = 1.0, []
    for t in np.unique(keluar[event == 1]):
        r = (masuk < t) & (keluar >= t)
        S *= 1 - ((keluar == t) & (event == 1) & r).sum() / r.sum()
        kurva.append((t, S))
    return [next((s for t, s in reversed(kurva) if t <= q), 1.0) for q in titik]


def logrank(masuk, keluar, event, grup, strata):
    """Log-rank (terstratifikasi) dengan delayed entry. grup bernilai 1/0; O dan E untuk grup 1."""
    O = E = V = 0.0
    for s in np.unique(strata):
        m = strata == s
        mk, kl, ev, gr = masuk[m], keluar[m], event[m], grup[m]
        for t in np.unique(kl[ev == 1]):
            r = (mk < t) & (kl >= t)
            n, n1 = r.sum(), (r & (gr == 1)).sum()
            dd, d1 = ((kl == t) & (ev == 1) & r).sum(), ((kl == t) & (ev == 1) & r & (gr == 1)).sum()
            if n < 2:
                continue
            O += d1
            E += dd * n1 / n
            V += dd * (n1 / n) * (1 - n1 / n) * (n - dd) / (n - 1)
    chi2 = (O - E) ** 2 / V
    return dict(chi2=round(chi2, 2), p=round(1 - stats.chi2.cdf(chi2, 1), 5), O_grup1=int(O), E_grup1=round(E, 1))


def p1(d, sk):
    kurva, uji = [], []
    for nama in ("S3", "S0"):
        for konf in (False, True):
            k = kohort(d, sk[nama], konf)
            definisi = "terkonfirmasi" if konf else "satu pengukuran"
            for fak, kol, satu in (("semua", None, None), ("bblr", "bblr", 1.0), ("jk", "jk", "L")):
                kk = k if kol is None else k.dropna(subset=[kol])
                grup_list = [("semua", kk)] if kol is None else [(str(v), g) for v, g in kk.groupby(kol)]
                for v, g in grup_list:
                    s_masuk = km_titik(np.zeros(len(g)), g["waktu"].to_numpy(float), g["event"].to_numpy(), [12, 24])
                    gu = g[g["umur_keluar"] > g["u0"]]  # umur keluar <= umur masuk (tanggal ukur janggal) tidak bisa dipakai di skala umur
                    s_umur = km_titik(gu["u0"].to_numpy(float), gu["umur_keluar"].to_numpy(float), gu["event"].to_numpy(), [24, 36])
                    kurva.append(dict(skenario=nama, definisi=definisi, faktor=fak, nilai=v, n_anak=len(g), n_kejadian=int(g["event"].sum()),
                                      S_12bln_sejak_masuk=round(s_masuk[0], 4), S_24bln_sejak_masuk=round(s_masuk[1], 4),
                                      S_umur24=round(s_umur[0], 4), S_umur36=round(s_umur[1], 4), n_umur_tak_valid=len(g) - len(gu)))
                if kol is None:
                    continue
                gr = (kk[kol] == satu).astype(int).to_numpy()
                ev, nol = kk["event"].to_numpy(), np.zeros(len(kk))
                for skala, mk, kl in (("sejak masuk", nol, kk["waktu"].to_numpy(float)), ("umur", kk["u0"].to_numpy(float), kk["umur_keluar"].to_numpy(float))):
                    # pada skala umur, anak dengan umur keluar <= umur masuk otomatis tidak pernah berisiko (masuk < t <= keluar)
                    for strat, st in (("tanpa", np.zeros(len(kk))), ("desa", kk["desa"].to_numpy()), ("desa x umur masuk", (kk["desa"] + "|" + kk["masuk_umur"]).to_numpy())):
                        if skala == "umur" and strat == "desa x umur masuk":
                            continue  # skala umur sudah memperhitungkan umur masuk
                        uji.append(dict(skenario=nama, definisi=definisi, faktor=fak, grup1=str(satu), skala=skala, strata=strat, n_anak=len(kk),
                                        n_kejadian=int(ev.sum()), **logrank(mk, kl, ev, gr, st)))
    return pd.DataFrame(kurva), pd.DataFrame(uji)


# ---------- P2 ----------
def p2(d, sk):
    baris = []
    for nama, m in (("semua baris", pd.Series(True, index=d.index)), ("S0", sk["S0"])):
        nb = d[m].groupby("id_anak")["bulan_berkas"].nunique()
        baris.append(dict(data=nama, n_anak=len(nb), pct_ge12=round(100 * (nb >= 12).mean(), 1), pct_ge24=round(100 * (nb >= 24).mean(), 1),
                          median=nb.median(), p25=nb.quantile(.25), p75=nb.quantile(.75), maks=nb.max()))
    return pd.DataFrame(baris)


# ---------- P3 ----------
def rasio(z):
    atas, bawah = ((z >= -2.0) & (z < -1.9)).sum(), ((z >= -2.1) & (z < -2.0)).sum()
    return atas, bawah, (atas / bawah if bawah else np.nan)


def p3_digit(d, sk):
    v = zvalid(d[sk["S3"]], "zs_tbu")
    v = v[v["tinggi"].notna()]
    v = v.assign(kelompok=np.where((np.round(v["tinggi"] * 10) % 5) == 0, "desimal .0/.5", "desimal lain"))
    baris = []
    for th, y in list(v.groupby("tahun")) + [("2024-2026", v)]:
        for kel, z in y.groupby("kelompok"):
            a, b, r = rasio(z["zs_tbu"])
            baris.append(dict(tahun=th, kelompok=kel, n=len(z), n_atas=int(a), n_bawah=int(b), rasio_tumpuk=round(r, 2), pct_di_bawah_min2=round(100 * (z["zs_tbu"] < -2).mean(), 2)))
    return pd.DataFrame(baris)


def lms_untuk(v, lms):
    hari = (v["umur_bln"] * HARI_PER_BLN).round().clip(0, lms["age"].max()).astype(int).to_numpy()
    sex = np.where(v["jk"] == "L", 1, 2)
    t = lms.set_index(["sex", "age"])
    idx = pd.MultiIndex.from_arrays([sex, hari])
    return t.loc[idx, "m"].to_numpy(), t.loc[idx, "s"].to_numpy(), hari


def p3_simulasi(d, sk, lms):
    v = zvalid(d[sk["S3"]], "zs_tbu")
    v = v[v["tinggi"].notna() & v["jk"].isin(["L", "P"])].copy()
    M, S, hari = lms_untuk(v, lms)
    # validasi LMS: z dari tinggi tercatat (dengan dan tanpa koreksi 0,7 cm posisi ukur) dibanding z situs
    h = v["tinggi"].to_numpy(float)
    kor = np.where((hari < 731) & (v["cara_ukur"] == "Berdiri"), 0.7, np.where((hari >= 731) & (v["cara_ukur"] == "Terlentang"), -0.7, 0))
    val = []
    for lab, hh in (("tanpa koreksi posisi", h), ("dengan koreksi posisi", h + kor)):
        selisih = np.abs((hh / M - 1) / S - v["zs_tbu"].to_numpy())
        val.append(dict(validasi=lab, median_selisih=round(np.median(selisih), 3), pct_selisih_le_0_1=round(100 * (selisih <= 0.1).mean(), 1)))
    # simulasi: z "benar" halus N(rerata, SD desa-tahun), tinggi dibulatkan, z dihitung ulang
    par = v.groupby(["desa", "tahun"])["zs_tbu"].agg(["mean", "std"])
    mu = par.loc[pd.MultiIndex.from_frame(v[["desa", "tahun"]]), "mean"].to_numpy()
    sd = par.loc[pd.MultiIndex.from_frame(v[["desa", "tahun"]]), "std"].to_numpy()
    tahun = v["tahun"].to_numpy()
    cara = {"tanpa pembulatan": lambda x: x, "terdekat 0,5 cm": lambda x: np.round(x * 2) / 2, "terdekat 1 cm": np.round,
            "ke bawah 1 cm": np.floor, "ke atas 1 cm": np.ceil}
    rng, hasil = np.random.default_rng(SEED), []
    for u in range(ULANG):
        zb = rng.normal(mu, sd)
        hb = M * (1 + S * zb)
        for nama, f in cara.items():
            zr = (f(hb) / M - 1) / S
            for th in (2024, 2025, 2026):
                z = zr[tahun == th]
                a, b, r = rasio(z)
                hasil.append(dict(ulang=u, cara=nama, tahun=th, rasio=r, pct_bawah=100 * (z < -2).mean()))
    h_ = pd.DataFrame(hasil).groupby(["cara", "tahun"]).agg(rasio_rerata=("rasio", "mean"), rasio_min=("rasio", "min"), rasio_maks=("rasio", "max"),
                                                              pct_di_bawah_min2=("pct_bawah", "mean")).round(2).reset_index()
    teramati = [dict(cara="TERAMATI (data)", tahun=th, rasio_rerata=round(rasio(v.loc[v.tahun == th, "zs_tbu"])[2], 2),
                     pct_di_bawah_min2=round(100 * (v.loc[v.tahun == th, "zs_tbu"] < -2).mean(), 2)) for th in (2024, 2025, 2026)]
    return pd.concat([h_, pd.DataFrame(teramati)], ignore_index=True), pd.DataFrame(val)


def verifikasi(d, sk):
    """Definisi lama harus mereproduksi a9_km_stunting / a9_logrank (S3)."""
    k, lama = kohort(d, sk["S3"], False), km_kohort(d, sk, "S3")
    assert len(k) == len(lama) == 2995 and k["event"].sum() == lama["event"].sum() == 1152, "kohort tidak sama dengan a9"
    s12 = km_titik(np.zeros(len(k)), k["waktu"].to_numpy(float), k["event"].to_numpy(), [12])[0]
    assert abs(s12 - 0.7304) < 1e-4, s12
    kb = lama.dropna(subset=["bblr"])
    lr_lama = logrank_lama(*[g for _, g in kb.groupby("bblr")])[0]
    kb2 = k.dropna(subset=["bblr"])
    lr_baru = logrank(np.zeros(len(kb2)), kb2["waktu"].to_numpy(float), kb2["event"].to_numpy(), (kb2["bblr"] == 1).astype(int).to_numpy(), np.zeros(len(kb2)))["chi2"]
    assert abs(lr_lama - lr_baru) < 0.01 and abs(lr_baru - 13.17) < 0.01, (lr_lama, lr_baru)
    print("Verifikasi P1 lolos: kohort 2.995 anak, 1.152 kejadian, S(12) 0,7304, log-rank BBLR 13,17.")


if __name__ == "__main__":
    anak, lms_path, keluar = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    keluar.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(anak, low_memory=False)
    sk = skenario(d)
    verifikasi(d, sk)
    km_t, lr_t = p1(d, sk)
    sim, val = p3_simulasi(d, sk, pd.read_csv(lms_path))
    for nm, df in (("p1_km_konfirmasi", km_t), ("p1_logrank", lr_t), ("p2_bulan_terukur", p2(d, sk)), ("p3_tumpuk_digit", p3_digit(d, sk)),
                   ("p3_simulasi_pembulatan", sim), ("p3_validasi_lms", val)):
        df.to_csv(keluar / f"{nm}.csv", index=False, encoding="utf-8")
        print(nm, df.shape)
