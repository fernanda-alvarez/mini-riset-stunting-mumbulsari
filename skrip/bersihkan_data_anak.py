"""Tahap 1 cleaning: data per anak (Daftar_Status_Gizi_YYYY-MM.xls, 2024-01..2026-09) -> dataset anak-bulan yang
dipseudonimkan + tabel desa-bulan per skenario + log. Aturan lengkap: data/sigizi/RENCANA_ANALISIS.md.
Pakai: python -I skrip/bersihkan_data_anak.py <folder berkas xls> <folder keluaran anak (gitignored)> <folder keluaran agregat>
- anak_bersih.csv (folder anak): ID acak (HMAC-SHA256 dengan garam lokal .garam), tanpa nama/NIK/alamat/RT/RW/tgl lahir.
- desa_bulan.csv, log_cleaning.txt (folder agregat): hanya agregat.
Flag keras (baris dikeluarkan dari semua analisis): zs_penanda, nol, aneh, nik_ganda, umur_luar.
Flag lunak: anomali_desabulan dan heaping_tinggi (desa-tahun) dipakai di skenario S3 dan S2; sisanya informasi (tgl_seragam, tbu_outlier,
cara_ukur_salah, tgl_luar, nik_pendek, pos_kosong, id_tak_konsisten)."""
import hmac
import hashlib
import secrets
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from baca_export_sigizi import baca  # noqa: E402

AKHIR = "2026-09"
KOLOM = ["NIK", "JK", "Tgl Lahir", "BB Lahir", "TB Lahir", "Desa/Kel", "Posyandu", "Tanggal Pengukuran", "Berat", "Tinggi",
         "Cara Ukur", "LiLA", "BB/U", "ZS BB/U", "TB/U", "ZS TB/U", "BB/TB", "ZS BB/TB", "Naik Berat Badan", "Jml Vit A", "MBG"]
DESA_26 = {"LAMPEJI", "MUMBULSARI", "LENGKONG"}  # S1: tanpa tiga desa ini pada 2026-01..2026-09
AMBANG_SERAGAM = 0.30  # tgl_seragam: satu tanggal ukur memuat >= 30% baris desa-bulan (dan >= 100 baris)
# anomali desa-bulan (S3): TB/U Outlier >= 10% (dasar 0,3-3%) atau stunting >= 50% (dasar 4-17%); mis. 2026-07 di tiga desa
AMBANG_OUTLIER, AMBANG_STUNTING = 0.10, 0.50
AMBANG_HEAPING = 0.70  # heaping tinggi: digit desimal .0/.5 >= 70% (diharapkan ~20%) per desa-tahun


def muat(folder):
    bagian = []
    for f in sorted(Path(folder).glob("Daftar_Status_Gizi_*.xls")):
        ym = f.stem[-7:]
        if ym > AKHIR:
            continue
        h, *d = baca(f)
        ix = {c: i for i, c in enumerate(h)}
        df = pd.DataFrame({c: [r[ix[c]].strip() for r in d] for c in KOLOM})
        df.insert(0, "bulan_berkas", ym)
        bagian.append(df)
    return pd.concat(bagian, ignore_index=True)


def angka(s):
    return pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")


def garam(folder):
    p = Path(folder) / ".garam"
    if not p.exists():
        p.write_text(secrets.token_hex(32))
    return p.read_text().strip().encode()


def bersihkan(raw, g):
    d = pd.DataFrame(index=raw.index)
    d["id_anak"] = raw["NIK"].map(lambda n: "A" + hmac.new(g, n.encode(), hashlib.sha256).hexdigest()[:10])
    d["bulan_berkas"] = raw["bulan_berkas"]
    d["tahun"] = raw["bulan_berkas"].str[:4].astype(int)
    d["bulan"] = raw["bulan_berkas"].str[5:].astype(int)
    d["desa"] = raw["Desa/Kel"].str.upper().replace("", pd.NA)
    d["posyandu"] = raw["Posyandu"].replace("", pd.NA)
    d["jk"] = raw["JK"]
    tgl_ukur = pd.to_datetime(raw["Tanggal Pengukuran"], format="%Y-%m-%d", errors="coerce")
    tgl_lahir = pd.to_datetime(raw["Tgl Lahir"], format="%Y-%m-%d", errors="coerce")
    d["tgl_ukur"] = tgl_ukur.dt.strftime("%Y-%m-%d")
    d["umur_bln"] = ((tgl_ukur - tgl_lahir).dt.days / 30.4375).round(1)
    bb = angka(raw["BB Lahir"])
    bb = bb.where(~((bb > 0) & (bb < 10)), bb * 1000)  # kg -> g
    tb = angka(raw["TB Lahir"])
    d["bb_lahir_g"] = bb.where((bb >= 500) & (bb <= 6000))
    d["tb_lahir_cm"] = tb.where((tb >= 30) & (tb <= 60))
    d["bblr"] = (d["bb_lahir_g"] < 2500).astype("Int8").where(d["bb_lahir_g"].notna())
    d["pblr"] = (d["tb_lahir_cm"] < 48).astype("Int8").where(d["tb_lahir_cm"].notna())
    d["berat"], d["tinggi"], d["lila"] = angka(raw["Berat"]), angka(raw["Tinggi"]), angka(raw["LiLA"])
    d["cara_ukur"] = raw["Cara Ukur"].replace("-", pd.NA)
    for k, c in (("zs_bbu", "ZS BB/U"), ("zs_tbu", "ZS TB/U"), ("zs_bbtb", "ZS BB/TB")):
        d[k] = angka(raw[c])
    d["kat_bbu"], d["kat_tbu"], d["kat_bbtb"] = raw["BB/U"], raw["TB/U"], raw["BB/TB"]
    d["naik_bb"] = raw["Naik Berat Badan"].replace("", pd.NA)
    d["vit_a"] = raw["Jml Vit A"].replace("", pd.NA)
    d["mbg"] = raw["MBG"].replace("-", pd.NA)

    # outcome biner dari label situs (konsisten dengan z-score); Outlier -> kosong
    def biner(kat, ya):
        return kat.isin(ya).astype("Int8").where(~kat.isin(["Outlier", ""]))
    d["stunting"] = biner(d["kat_tbu"], ["Pendek", "Sangat Pendek"])
    d["stunting_berat"] = biner(d["kat_tbu"], ["Sangat Pendek"])
    d["wasting"] = biner(d["kat_bbtb"], ["Gizi Kurang", "Gizi Buruk"])
    d["wasting_berat"] = biner(d["kat_bbtb"], ["Gizi Buruk"])
    d["underweight"] = biner(d["kat_bbu"], ["Kurang", "Sangat Kurang"])
    d["gizi_lebih"] = biner(d["kat_bbtb"], ["Gizi Lebih", "Obesitas"])

    # flag keras
    zs = d[["zs_bbu", "zs_tbu", "zs_bbtb"]]
    d["f_zs_penanda"] = (zs.abs() >= 999).any(axis=1)
    d["f_nol"] = (d["tinggi"] == 0) | (d["berat"] == 0)
    d["f_aneh"] = (d["berat"] > 40) | (d["tinggi"] > 130)
    d["f_nik_ganda"] = pd.Series(list(zip(d["id_anak"], d["bulan_berkas"])), index=d.index).duplicated(keep="first")
    d["f_umur_luar"] = ~d["umur_bln"].between(0, 60, inclusive="left")
    d["f_keras"] = d[["f_zs_penanda", "f_nol", "f_aneh", "f_nik_ganda", "f_umur_luar"]].any(axis=1)

    # flag lunak
    d["f_tgl_luar"] = d["tgl_ukur"].str[:7] != d["bulan_berkas"]
    d["f_pos_kosong"] = d["posyandu"].isna()
    d["f_nik_pendek"] = raw["NIK"].str.len() != 16
    kunci = pd.DataFrame({"id": d["id_anak"], "jk": raw["JK"], "lahir": raw["Tgl Lahir"]})
    d["f_id_tak_konsisten"] = (kunci.groupby("id")["jk"].transform("nunique") > 1) | (kunci.groupby("id")["lahir"].transform("nunique") > 1)
    d["f_tbu_outlier"] = d["kat_tbu"] == "Outlier"
    d["f_cara_ukur_salah"] = ((d["umur_bln"] < 24) & (d["cara_ukur"] == "Berdiri")) | ((d["umur_bln"] >= 24) & (d["cara_ukur"] == "Terlentang"))
    n_dbt = d.groupby(["desa", "bulan_berkas"], dropna=False)["id_anak"].transform("size")
    n_tgl = d.groupby(["desa", "bulan_berkas", "tgl_ukur"], dropna=False)["id_anak"].transform("size")
    d["f_tgl_seragam"] = (n_tgl >= 100) & (n_tgl / n_dbt >= AMBANG_SERAGAM)
    dbt = d.groupby(["desa", "bulan_berkas"], dropna=False)
    d["f_anomali_desabulan"] = (dbt["f_tbu_outlier"].transform("mean") >= AMBANG_OUTLIER) | (dbt["stunting"].transform("mean") >= AMBANG_STUNTING)
    desim = raw["Tinggi"].str.replace(",", ".", regex=False).str.extract(r"\.(\d)")[0].fillna("0")
    d["_bulat"] = desim.isin(["0", "5"]).where(d["tinggi"].notna())
    d["pct_heaping_desa_tahun"] = d.groupby(["desa", "tahun"], dropna=False)["_bulat"].transform("mean").round(3)
    d["f_heaping_tinggi"] = d["pct_heaping_desa_tahun"] >= AMBANG_HEAPING
    return d.drop(columns="_bulat")


def skenario(d):
    s0 = ~d["f_keras"] & d["desa"].notna()
    s1 = s0 & ~(d["desa"].isin(DESA_26) & (d["bulan_berkas"] >= "2026-01") & (d["bulan_berkas"] <= "2026-09"))
    return {"S0": s0, "S1": s1, "S2": s0 & ~d["f_heaping_tinggi"], "S3": s0 & ~d["f_anomali_desabulan"]}


def desa_bulan(d):
    hasil = []
    for nama, m in skenario(d).items():
        x = d[m]
        g = x.groupby(["desa", "bulan_berkas"]).agg(
            n=("id_anak", "size"), n_stunting=("stunting", "sum"), n_tbu_valid=("stunting", "count"),
            n_wasting=("wasting", "sum"), n_bbtb_valid=("wasting", "count"),
            n_underweight=("underweight", "sum"), n_bbu_valid=("underweight", "count"))
        g.insert(0, "skenario", nama)
        hasil.append(g.reset_index())
    out = pd.concat(hasil, ignore_index=True)
    for k, v in (("stunting", "tbu"), ("wasting", "bbtb"), ("underweight", "bbu")):
        out[f"pct_{k}"] = (100 * out[f"n_{k}"] / out[f"n_{v}_valid"]).round(2)
    # kolom kualitas dari seluruh baris (S0 sebelum flag)
    kual = d.groupby(["desa", "bulan_berkas"]).agg(
        n_mentah=("id_anak", "size"), n_keras=("f_keras", "sum"), pct_tgl_seragam=("f_tgl_seragam", "mean"),
        pct_tbu_outlier=("f_tbu_outlier", "mean"), pct_pos_kosong=("f_pos_kosong", "mean"),
        pct_heaping_desa_tahun=("pct_heaping_desa_tahun", "first")).reset_index()
    for c in ("pct_tgl_seragam", "pct_tbu_outlier", "pct_pos_kosong"):
        kual[c] = (100 * kual[c]).round(1)
    return out.merge(kual, on=["desa", "bulan_berkas"], how="left")


def log(d):
    baris = [f"Baris mentah: {len(d)} (anak unik {d['id_anak'].nunique()}), {d['bulan_berkas'].min()}..{d['bulan_berkas'].max()}", ""]
    flag = [c for c in d.columns if c.startswith("f_")]
    baris.append("Jumlah baris kena flag per tahun (flag keras: f_keras = gabungan):")
    baris.append(d.groupby("tahun")[flag].sum().T.to_string())
    baris += ["", "Jumlah baris per skenario per tahun:"]
    baris.append(pd.DataFrame({k: d[m].groupby(d["tahun"]).size() for k, m in skenario(d).items()}).to_string())
    baris += ["", "Desa-bulan anomali (f_anomali_desabulan; baris kena flag):"]
    em = d[d["f_anomali_desabulan"]].groupby(["desa", "bulan_berkas"]).size()
    baris.append(em.to_string() if len(em) else "(tidak ada)")
    baris += ["", "Heaping desa-tahun (>= %.0f%% = heaping_tinggi):" % (100 * AMBANG_HEAPING)]
    baris.append(d.groupby(["tahun", "desa"])["pct_heaping_desa_tahun"].first().to_string())
    return "\n".join(baris)


if __name__ == "__main__":
    sumber, k_anak, k_agregat = map(Path, sys.argv[1:4])
    k_anak.mkdir(parents=True, exist_ok=True)
    k_agregat.mkdir(parents=True, exist_ok=True)
    d = bersihkan(muat(sumber), garam(k_anak))
    d.to_csv(k_anak / "anak_bersih.csv", index=False, encoding="utf-8")
    desa_bulan(d).to_csv(k_agregat / "desa_bulan.csv", index=False, encoding="utf-8")
    (k_agregat / "log_cleaning.txt").write_text(log(d), encoding="utf-8")
    print(log(d))
