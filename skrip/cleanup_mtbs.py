"""Cleanup register MTBS (2 bln - 5 th) Klaster 2 PKM Mumbulsari, sheet 2025 dan 2026.

Pemakaian: python cleanup_mtbs.py <xlsx klaster 2> <xlsx output>
File sumber tidak diubah. Semua koreksi dicatat di sheet Log_Perubahan.
"""
import re
import sys
import datetime as dt
import pandas as pd

SRC, OUT = sys.argv[1], sys.argv[2]
SNAPSHOT = pd.Timestamp("2026-10-13")
LOG = []


def log(sheet, baris, kolom, asli, baru, alasan):
    LOG.append({"sheet": sheet, "baris_excel": baris, "kolom": kolom,
                "nilai_asli": "" if asli is None or (isinstance(asli, float) and pd.isna(asli)) else str(asli),
                "nilai_baru": "" if baru is None or (isinstance(baru, float) and pd.isna(baru)) else str(baru),
                "alasan": alasan})


# ---------------------------------------------------------------- helper
def s_(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def num(v):
    """'9 kg' -> 9, '22, 8' -> 22.8, '85 CM' -> 85"""
    if isinstance(v, (int, float)) and not pd.isna(v):
        return float(v)
    t = s_(v).upper().replace("KG", "").replace("CM", "").replace(" ", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def mkdate(y, m, d):
    try:
        return pd.Timestamp(year=int(y), month=int(m), day=int(d))
    except (ValueError, TypeError):
        return None


def parse_teks_tgl(t):
    """kembalikan (d, m, y|None). y None bila tanpa tahun / tahun tak valid."""
    m = re.fullmatch(r"(\d{1,2})\s*[-/.]\s*(\d{1,2})(?:\s*[-/.]\s*(\d{1,4}))?", t)
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
    if y is not None:
        y = int(y)
        if len(m.group(3)) == 2:
            y += 2000
        if not 2010 <= y <= 2026:
            y = None
    return d, mo, y


def nik_info(v):
    t = re.sub(r"\.0$", "", s_(v))
    if not re.fullmatch(r"\d{16}", t):
        return None, None
    dd, mm, yy = int(t[6:8]), int(t[8:10]), int(t[10:12])
    jk = "P" if dd > 40 else "L"
    dob = mkdate(2000 + yy, mm, dd - 40 if dd > 40 else dd)
    if dob is None or dob.year < 2018:
        return None, None          # bukan NIK anak (kemungkinan NIK orang tua)
    return jk, dob


DESA = {"LAMPEJI": "LAMPEJI", "MUMBULSARI": "MUMBULSARI", "SUCO": "SUCO", "TAMANSARI": "TAMANSARI",
        "KARANG KEDAWUNG": "KARANG KEDAWUNG", "LENGKONG": "LENGKONG", "KAWANGREJO": "KAWANGREJO"}
DESA_ALIAS = {
    "MUMBUL": "MUMBULSARI", "MUMBULSAR": "MUMBULSARI", "LAMPEJIA": "LAMPEJI", "SUVO": "SUCO",
    "TAMANSRAI": "TAMANSARI", "KEMIRI SONGO": "LAMPEJI", "KARANG SIRIH": "SUCO",
}
LUAR = {"LW", "LUAR MUMBULSARI", "SILO", "MAYANG", "AJUNG", "AMBULU", "JENGGAWAH", "KALISAT",
        "NTT", "GAMBIRAN", "SEPUTIH", "PANDE BALI"}


def norm_desa(v):
    t = re.sub(r"\s+", " ", s_(v).upper())
    if t in ("", "."):
        return None, "kosong"
    if re.search(r"\d+/\d+", t):           # 'KRAJAN 2/10 SUCO' -> desa di akhir
        t = t.split()[-1]
    if t in DESA:
        return DESA[t], "sama"
    if t in DESA_ALIAS:
        return DESA_ALIAS[t], "alias"
    if any(k in t for k in ("KDWG", "KEDAW", "EDAWUNG")) or t in ("KARANG KED",):
        return "KARANG KEDAWUNG", "alias"
    if t in LUAR:
        return "LUAR WILAYAH", "luar"
    return "TIDAK JELAS", "tidak jelas"   # nama dusun tanpa desa (KRAJAN, GUDANG BARAT, JATISARI)


TAHUN_OK = {"MTBS (2 BLN - 5 THN)": {2024, 2025, 2026}, "MTBS (2 BLN - 5 THN) 2026 ": {2026}}


# ---------------------------------------------------------------- tanggal kunjungan
def bersihkan_tgl_kunjungan(raw, sheet, rows):
    """raw: list nilai asli berurutan sesuai register. Excel membaca d-m-y sebagai m-d-y
    bila hari <= 12, jadi sel bertipe datetime ditukar bulan<->hari."""
    def eksplisit(v):
        """tanggal dengan tahun tertulis (untuk melihat baris berikutnya)"""
        if isinstance(v, dt.datetime):
            return mkdate(v.year, v.day, v.month)
        if s_(v) and not isinstance(v, (int, float)):
            p = parse_teks_tgl(s_(v))
            if p and p[2]:
                return mkdate(p[2], p[1], p[0])
        return None

    eks = [eksplisit(v) for v in raw]

    def berikutnya(i):
        for j in range(i + 1, min(i + 15, len(eks))):
            if eks[j] is not None:
                return eks[j]
        return None

    out, flag = [], []
    prev = None
    for i, (v, baris) in enumerate(zip(raw, rows)):
        cand, f = None, ""
        if isinstance(v, dt.datetime):
            cand = mkdate(v.year, v.day, v.month)
            f = "datetime: bulan/hari ditukar"
        elif s_(v) and not isinstance(v, (int, float)):
            p = parse_teks_tgl(s_(v))
            if p:
                d, m, y = p
                if y is None:
                    y = prev.year if prev is not None else None
                    if y is not None and prev is not None and m < prev.month - 6:
                        y += 1
                    f = "tahun tidak ada/salah ketik: diambil dari baris sebelumnya"
                cand = mkdate(y, m, d) if y else None
        lompat = False
        if cand is not None and cand.year not in TAHUN_OK[sheet]:
            # tahun mustahil untuk register ini (mis. 2022 / 2025 di sheet 2026) -> ikuti urutan
            if prev is not None:
                for yy in (prev.year, prev.year + 1):
                    alt = mkdate(yy, cand.month, cand.day)
                    if alt is not None and abs((alt - prev).days) <= 60:
                        cand = alt
                        break
                else:
                    cand = mkdate(prev.year, cand.month, cand.day)
                f = (f + "; " if f else "") + "tahun di luar periode register: dikoreksi mengikuti urutan"
        if cand is not None and prev is not None and abs((cand - prev).days) > 60:
            alt = mkdate(cand.year + 1, cand.month, cand.day)
            if alt is not None and 0 <= (alt - prev).days <= 60:
                # mis. Januari ditulis tahun lama setelah Desember (salah ketik pergantian tahun)
                cand = alt
                f = (f + "; " if f else "") + "tahun salah ketik saat pergantian tahun: +1"
            else:
                nx = berikutnya(i)
                if nx is not None and abs((nx - cand).days) <= 30:
                    # baris-baris berikutnya ikut pindah -> jeda pencatatan, bukan salah ketik
                    f = (f + "; " if f else "") + "jeda pencatatan (dikonfirmasi baris berikutnya)"
                else:
                    # tahun tertulis jelas -> tidak diubah, hanya ditandai; tidak dipakai acuan baris berikutnya
                    f = (f + "; " if f else "") + "CEK: loncat jauh dari baris sebelumnya"
                    lompat = True
        if cand is not None and cand > SNAPSHOT:
            f = (f + "; " if f else "") + "CEK: setelah tanggal snapshot"
        if cand is None:
            if prev is not None:
                cand, f = prev, "kosong: diisi dari baris di atasnya (hari yang sama)"
            else:
                f = "kosong"
        elif not lompat:
            prev = cand
        if f and f != "kosong":
            log(sheet, baris, "TANGGAL", v, cand.date() if cand is not None else None, f)
        out.append(cand)
        flag.append(f)
    return out, flag


# ---------------------------------------------------------------- umur teks
def umur_teks(v):
    """(bulan, presisi) dari teks umur. presisi: 'bulan' | 'tahun bulat' | None"""
    t = s_(v).upper()
    if not t:
        return None, None
    if isinstance(v, (int, float)):
        return float(v) * 12, "tahun bulat"          # angka polos = tahun
    th = re.search(r"(\d+(?:[.,]\d+)?)\s*(TH|THN|TAHUN)", t)
    bl = re.search(r"(\d+)\s*(BL|BLN|BULAN)", t)
    if bl and not th:
        return float(bl.group(1)), "bulan"
    if th:
        y = float(th.group(1).replace(",", "."))
        if bl or y != int(y):
            return y * 12 + (float(bl.group(1)) if bl else 0), "bulan"
        return y * 12, "tahun bulat"
    if re.fullmatch(r"\d+", t):
        return float(t) * 12, "tahun bulat"
    return None, None


def bulan_antara(a, b):
    return (b - a).days / 30.4375


# ---------------------------------------------------------------- baca sheet
def baca(sheet, kol):
    raw = pd.read_excel(SRC, sheet_name=sheet, header=None)
    data = raw.iloc[5:]
    data = data[data[kol["nama"]].notna()]
    return data


K25 = dict(tgl=1, nama=2, nik=3, id=4, umur=5, ortu=6, jk=7, alamat=8, bb=11, pb=12, lk=13, suhu=14,
           keluhan=15, kunj_b=16, kunj_l=17, kasus_b=18, kasus_l=19, umum=21, spm=22, bpjs=23,
           diagnosa=76, kode=77, tindakan=78, konseling=79, rujuk_dalam=81, rujuk_luar=82)
K26 = dict(tgl=1, nama=2, id=3, jk=4, nik=5, umur=6, dob=7, ortu=8, alamat=9, bb=12, pb=13, lk=14, suhu=15,
           keluhan=16, kunj_b=17, kunj_l=18, kasus_b=19, kasus_l=20, umum=22, spm=23, bpjs=24,
           diagnosa=77, kode=78, tindakan=79, konseling=80, rujuk_dalam=82, rujuk_luar=83)

SHEETS = [("MTBS (2 BLN - 5 THN)", K25, "2025"), ("MTBS (2 BLN - 5 THN) 2026 ", K26, "2026")]

recs = []
for sheet, K, tag in SHEETS:
    d = baca(sheet, K)
    rows = [i + 1 for i in d.index]
    tgl, ftgl = bersihkan_tgl_kunjungan(d[K["tgl"]].tolist(), sheet, rows)
    for (i, r), baris, t, ft in zip(d.iterrows(), rows, tgl, ftgl):
        g = lambda k: r[K[k]] if k in K else None
        rec = {
            "sheet_sumber": sheet.strip(), "kelompok_data": tag, "baris_excel": baris,
            "tgl_kunjungan": t, "tgl_kunjungan_asli": s_(g("tgl")), "flag_tgl_kunjungan": ft,
            "nama": re.sub(r"\s+", " ", s_(g("nama")).upper()),
            "id_pasien": re.sub(r"\.0$", "", s_(g("id"))),
            "nik": re.sub(r"\.0$", "", s_(g("nik"))),
            "nama_ortu": s_(g("ortu")).upper(),
            "jk_asli": s_(g("jk")), "umur_asli": s_(g("umur")),
            "dob_asli": s_(g("dob")) if tag == "2026" else "",
            "alamat_asli": s_(g("alamat")),
            "bb_asli": s_(g("bb")), "pb_asli": s_(g("pb")), "lk_cm": num(g("lk")), "suhu_c": num(g("suhu")),
            "keluhan_utama": s_(g("keluhan")).upper(), "diagnosa": s_(g("diagnosa")).upper(),
            "kode_diagnosa": s_(g("kode")).upper(), "tindakan": s_(g("tindakan")).upper(),
            "konseling": s_(g("konseling")).upper(),
            "rujukan": " ".join(x for x in [s_(g("rujuk_dalam")), s_(g("rujuk_luar"))] if x and x != "1").upper(),
            "kunjungan": "BARU" if s_(g("kunj_b")) else ("LAMA" if s_(g("kunj_l")) else None),
            "kasus": "BARU" if s_(g("kasus_b")) else ("LAMA" if s_(g("kasus_l")) else None),
            "pembiayaan": "UMUM" if s_(g("umum")) else ("SPM/J-KEREN" if s_(g("spm")) else ("BPJS" if s_(g("bpjs")) else None)),
            "_dobraw": g("dob") if tag == "2026" else g("umur"),
        }
        if not rec["id_pasien"] or rec["id_pasien"] in ("-",):
            rec["id_pasien"] = None
        recs.append(rec)

df = pd.DataFrame(recs)

# ---------------------------------------------------------------- tanggal lahir
nik = df["nik"].map(nik_info)
df["jk_nik"] = [x[0] for x in nik]
df["dob_nik"] = [x[1] for x in nik]


def dob_kandidat(r):
    """kembalikan (dob, sumber). Kolom TANGGAL LAHIR (2026) / kolom UMUR berisi tanggal (2025)."""
    v = r["_dobraw"]
    if isinstance(v, dt.datetime):
        asis = pd.Timestamp(v.date())
        swap = mkdate(v.year, v.day, v.month)
        if r["kelompok_data"] == "2026":
            # kolom 2026 berisi tanggal asli (banyak hari > 12) -> pakai apa adanya kecuali NIK cocok versi tukar
            if r["dob_nik"] is not None and swap == r["dob_nik"] and asis != r["dob_nik"]:
                return swap, "kolom tgl lahir (bulan/hari ditukar, cocok NIK)"
            return asis, "kolom tgl lahir"
        # 2025: sel tanggal di kolom UMUR hasil salah baca Excel -> tukar, kecuali NIK cocok versi asli
        if r["dob_nik"] is not None and asis == r["dob_nik"]:
            return asis, "kolom umur berisi tanggal (cocok NIK)"
        if swap is None:
            return asis, "kolom umur berisi tanggal"
        return swap, "kolom umur berisi tanggal (bulan/hari ditukar)"
    t = s_(v)
    if t and not isinstance(v, (int, float)):
        p = parse_teks_tgl(t)
        if p and p[2]:
            return mkdate(p[2], p[1], p[0]), ("kolom tgl lahir (teks)" if r["kelompok_data"] == "2026" else "kolom umur berisi tanggal (teks)")
    return None, None


def dob_kandidat_aman(r):
    dob, src = dob_kandidat(r)
    t = r["tgl_kunjungan"]
    if dob is not None and t is not None and not pd.isna(t) and abs((t - dob).days) <= 14:
        # 'tanggal lahir' sama dengan tanggal kunjungan -> yang tertulis tanggal kunjungan
        log(r["sheet_sumber"], r["baris_excel"], "TGL LAHIR", r["_dobraw"], None, "sama dengan tanggal kunjungan: bukan tgl lahir")
        return None, None
    if dob is not None and dob.year < 2018:
        log(r["sheet_sumber"], r["baris_excel"], "TGL LAHIR", r["_dobraw"], None, "tahun lahir < 2018: bukan balita/salah ketik")
        return None, None
    return dob, src


kd = df.apply(dob_kandidat_aman, axis=1)
df["_dob_kol"] = [x[0] for x in kd]
df["_dob_kol_src"] = [x[1] for x in kd]

# tanggal lahir per id dari 2026 (untuk tautan ke 2025)
dob26 = (df[(df.kelompok_data == "2026") & df._dob_kol.notna() & df.id_pasien.notna()]
         .groupby("id_pasien")["_dob_kol"].agg(lambda s: s.mode().iloc[0]))
dobany = (df[df._dob_kol.notna() & df.id_pasien.notna()].groupby("id_pasien")["_dob_kol"]
          .agg(lambda s: s.mode().iloc[0]))


def pilih_dob(r):
    if r["_dob_kol"] is not None and not pd.isna(r["_dob_kol"]):
        dob, src = r["_dob_kol"], r["_dob_kol_src"]
    elif r["dob_nik"] is not None:
        dob, src = r["dob_nik"], "NIK"
    elif r["id_pasien"] in dob26.index:
        dob, src = dob26[r["id_pasien"]], "tautan id ke data 2026"
    elif r["id_pasien"] in dobany.index:
        dob, src = dobany[r["id_pasien"]], "kunjungan lain id yang sama"
    else:
        return None, None, ""
    cek = []
    if r["dob_nik"] is not None and abs((dob - r["dob_nik"]).days) > 1 and src != "NIK":
        cek.append(f"beda dengan NIK ({r['dob_nik'].date()})")
    if r["id_pasien"] in dob26.index and abs((dob - dob26[r['id_pasien']]).days) > 1:
        cek.append(f"beda dengan data 2026 ({dob26[r['id_pasien']].date()})")
    return dob, src, "; ".join(cek)


pd_ = df.apply(pilih_dob, axis=1)
df["tgl_lahir"] = [x[0] for x in pd_]
df["sumber_tgl_lahir"] = [x[1] for x in pd_]
df["flag_tgl_lahir"] = [x[2] for x in pd_]

# ---------------------------------------------------------------- umur
ut =[umur_teks(v) if not isinstance(raw, dt.datetime) else (None, None)
      for v, raw in zip(df["umur_asli"], df["_dobraw"].where(df.kelompok_data == "2025", None))]
# kolom UMUR 2026 hanya angka sporadis; pakai untuk kedua sheet bila bukan tanggal
df["umur_bulan_teks"] = [u[0] for u in ut]
df["presisi_umur_teks"] = [u[1] for u in ut]


def hitung_umur(r):
    if r["tgl_lahir"] is not None and not pd.isna(r["tgl_lahir"]) and r["tgl_kunjungan"] is not None and not pd.isna(r["tgl_kunjungan"]):
        u = bulan_antara(r["tgl_lahir"], r["tgl_kunjungan"])
        f = ""
        if u < 0:
            f = "CEK: tgl lahir setelah tgl kunjungan"
        elif r["umur_bulan_teks"] is not None and abs(u - r["umur_bulan_teks"]) > 12:
            f = f"CEK: beda >12 bln dengan umur tertulis ({r['umur_asli']})"
        return round(u, 2), "tepat (tgl lahir)", f
    if r["umur_bulan_teks"] is not None:
        return r["umur_bulan_teks"], ("± bulan (teks bulan)" if r["presisi_umur_teks"] == "bulan" else "kasar (tahun bulat)"), ""
    return None, None, ""


hu = df.apply(hitung_umur, axis=1)
df["umur_bulan"] = [x[0] for x in hu]
df["presisi_umur"] = [x[1] for x in hu]
df["flag_umur"] = [x[2] for x in hu]

# ---------------------------------------------------------------- jenis kelamin
def jk_kolom(v):
    t = re.sub(r"[\s\-]", "", s_(v).upper())
    if t in ("L", "LAKILAKI"):
        return "L"
    if t in ("P", "PEREMPUAN"):
        return "P"
    return None


df["_jk_kol"] = df["jk_asli"].map(jk_kolom)
jk_id = df[df._jk_kol.notna() & df.id_pasien.notna()].groupby("id_pasien")["_jk_kol"].agg(lambda s: s.mode().iloc[0])


def pilih_jk(r):
    kol = r["_jk_kol"] if isinstance(r["_jk_kol"], str) else None
    nikjk = r["jk_nik"] if isinstance(r["jk_nik"], str) else None
    if kol:
        f = "CEK: beda dengan NIK" if nikjk and nikjk != kol else ""
        return kol, "kolom JK", f
    if nikjk:
        return r["jk_nik"], "NIK", ""
    if r["id_pasien"] in jk_id.index:
        return jk_id[r["id_pasien"]], "kunjungan lain id yang sama", ""
    f = "kolom JK berisi nama (kolom bergeser)" if s_(r["jk_asli"]) else ""
    return None, None, f


pj = df.apply(pilih_jk, axis=1)
df["jk"] = [x[0] for x in pj]
df["sumber_jk"] = [x[1] for x in pj]
df["flag_jk"] = [x[2] for x in pj]
for _, r in df[df.sumber_jk.isin(["NIK", "kunjungan lain id yang sama"])].iterrows():
    log(r.sheet_sumber, r.baris_excel, "JK", r.jk_asli, r.jk, f"diisi dari {r.sumber_jk}")

# ---------------------------------------------------------------- desa
nd = df["alamat_asli"].map(norm_desa)
df["desa"] = [x[0] for x in nd]
for (_, r), (desa, how) in zip(df.iterrows(), nd):
    if how in ("alias", "luar", "tidak jelas"):
        log(r.sheet_sumber, r.baris_excel, "ALAMAT", r.alamat_asli, desa, f"normalisasi desa ({how})")

# ---------------------------------------------------------------- BB / PB
def antro(r):
    bb, pb = num(r["bb_asli"]), num(r["pb_asli"])
    f = []
    if bb is not None and pb is not None and pb < 25 and bb > 40 and 2 <= pb <= 30 and 45 <= bb <= 125:
        bb, pb = pb, bb
        f.append("BB dan PB tertukar kolom: ditukar")
        log(r.sheet_sumber, r.baris_excel, "BB/PB", f"{r.bb_asli}/{r.pb_asli}", f"{bb}/{pb}", "BB dan PB tertukar kolom")
    if bb is not None and not 2 <= bb <= 35:
        f.append(f"BB {bb} tidak masuk akal: dikosongkan")
        log(r.sheet_sumber, r.baris_excel, "BB", r.bb_asli, None, "di luar 2-35 kg")
        bb = None
    if pb is not None and not 45 <= pb <= 125:
        f.append(f"PB {pb} tidak masuk akal: dikosongkan")
        log(r.sheet_sumber, r.baris_excel, "PB", r.pb_asli, None, "di luar 45-125 cm")
        pb = None
    if s_(r["bb_asli"]) and num(r["bb_asli"]) is not None and not isinstance(r["bb_asli"], (int, float)) \
            and re.search(r"[A-Za-z ,]", s_(r["bb_asli"])) and bb is not None:
        log(r.sheet_sumber, r.baris_excel, "BB", r.bb_asli, bb, "teks dibersihkan jadi angka")
    return bb, pb, "; ".join(f)


an = df.apply(antro, axis=1)
df["bb_kg"] = [x[0] for x in an]
df["pb_cm"] = [x[1] for x in an]
df["flag_antropometri"] = [x[2] for x in an]

# ---------------------------------------------------------------- duplikat & kelayakan
df["_k"] = df["id_pasien"].fillna("NAMA:" + df["nama"]) + "|" + df["tgl_kunjungan"].astype(str)
df["duplikat"] = df.duplicated("_k", keep="first") & df.tgl_kunjungan.notna()


def layak(r):
    alasan = []
    if r["duplikat"]:
        alasan.append("duplikat")
    if r["umur_bulan"] is None or pd.isna(r["umur_bulan"]):
        alasan.append("umur tidak ada")
    elif r["presisi_umur"] == "kasar (tahun bulat)":
        alasan.append("umur kasar (tahun bulat)")
    elif not 0 <= r["umur_bulan"] < 61:
        alasan.append("di luar 0-60 bulan")
    if r["flag_umur"].startswith("CEK"):
        alasan.append("umur perlu dicek")
    if not r["jk"]:
        alasan.append("JK tidak ada")
    if r["pb_cm"] is None or pd.isna(r["pb_cm"]):
        alasan.append("PB tidak ada/tidak valid")
    return (len(alasan) == 0), "; ".join(alasan)


ly = df.apply(layak, axis=1)
df["layak_TBU"] = [x[0] for x in ly]
df["alasan_tidak_layak"] = [x[1] for x in ly]
df["tahun_kunjungan"] = df["tgl_kunjungan"].map(lambda t: t.year if t is not None and not pd.isna(t) else None)

# ---------------------------------------------------------------- tulis
KOLOM = ["sheet_sumber", "kelompok_data", "baris_excel", "id_pasien", "nik", "nama", "nama_ortu",
         "tgl_kunjungan", "tahun_kunjungan", "flag_tgl_kunjungan",
         "jk", "sumber_jk", "flag_jk",
         "tgl_lahir", "sumber_tgl_lahir", "flag_tgl_lahir",
         "umur_bulan", "presisi_umur", "flag_umur",
         "desa", "bb_kg", "pb_cm", "flag_antropometri", "lk_cm", "suhu_c",
         "keluhan_utama", "diagnosa", "kode_diagnosa", "tindakan", "konseling", "rujukan",
         "kunjungan", "kasus", "pembiayaan", "duplikat", "layak_TBU", "alasan_tidak_layak",
         "tgl_kunjungan_asli", "jk_asli", "umur_asli", "dob_asli", "alamat_asli", "bb_asli", "pb_asli"]
out = df[KOLOM].copy()
for c in ["tgl_kunjungan", "tgl_lahir"]:
    out[c] = pd.to_datetime(out[c]).dt.date

ok = out[out.layak_TBU]
ring = []
for tag in ["2025", "2026", "Total"]:
    sub = out if tag == "Total" else out[out.kelompok_data == tag]
    sok = ok if tag == "Total" else ok[ok.kelompok_data == tag]
    ring.append({"kelompok": f"sheet {tag}" if tag != "Total" else "Total",
                 "kunjungan": len(sub), "anak_unik_id": sub.id_pasien.nunique(),
                 "tgl_kunjungan_terisi": sub.tgl_kunjungan.notna().sum(),
                 "jk_terisi": sub.jk.notna().sum(), "tgl_lahir_terisi": sub.tgl_lahir.notna().sum(),
                 "pb_valid": sub.pb_cm.notna().sum(), "bb_valid": sub.bb_kg.notna().sum(),
                 "layak_TBU_kunjungan": len(sok), "layak_TBU_anak_unik": sok.id_pasien.nunique()})
ring = pd.DataFrame(ring)
alasan = (out.loc[~out.layak_TBU, "alasan_tidak_layak"].str.split("; ").explode().value_counts()
          .rename_axis("alasan").reset_index(name="jumlah_kunjungan"))

KAMUS = pd.DataFrame([
    ("sheet_sumber / baris_excel", "Asal baris di file Klaster 2 (nomor baris Excel) untuk cek balik"),
    ("kelompok_data", "2025 = sheet 'MTBS (2 BLN - 5 THN)' (isi Feb 2024-Jan 2026); 2026 = sheet '... 2026'"),
    ("id_pasien", "NO RM (2025) / NO INDEX (2026); kedua nomor sama untuk anak yang sama"),
    ("tgl_kunjungan", "Sel datetime ditukar bulan/hari (salah baca Excel); teks d-m-y diurai; tahun hilang/salah diambil dari urutan register; sel kosong diisi tanggal baris di atasnya"),
    ("jk / sumber_jk", "Kolom JK -> NIK (digit 7-8 >40 = perempuan) -> kunjungan lain id sama"),
    ("tgl_lahir / sumber_tgl_lahir", "Kolom tgl lahir (2026) / kolom UMUR yang berisi tanggal (2025) -> NIK -> tautan id ke data 2026"),
    ("umur_bulan / presisi_umur", "Dari tgl lahir dan tgl kunjungan (tepat); jika tidak ada, dari teks umur (bulan / tahun bulat = kasar)"),
    ("desa", "7 desa Kec. Mumbulsari; LUAR WILAYAH; TIDAK JELAS = hanya nama dusun"),
    ("bb_kg / pb_cm", "Angka bersih; BB/PB tertukar ditukar balik; BB di luar 2-35 kg / PB di luar 45-125 cm dikosongkan"),
    ("layak_TBU", "TRUE bila umur tepat/bulan 0-60 bln, JK ada, PB valid, bukan duplikat"),
    ("kolom *_asli", "Nilai asli dari register sebelum dibersihkan"),
    ("flag_*", "Catatan koreksi; yang diawali 'CEK' perlu diperiksa manual"),
], columns=["variabel", "keterangan"])

with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    out.to_excel(xw, sheet_name="Data_Bersih", index=False)
    ok.to_excel(xw, sheet_name="Layak_TBU", index=False)
    out[out[["flag_tgl_kunjungan", "flag_tgl_lahir", "flag_umur", "flag_jk"]].apply(
        lambda c: c.astype(str).str.contains("CEK")).any(axis=1)].to_excel(xw, sheet_name="Perlu_Cek_Manual", index=False)
    ring.to_excel(xw, sheet_name="Ringkasan", index=False)
    alasan.to_excel(xw, sheet_name="Ringkasan", index=False, startrow=len(ring) + 3)
    pd.DataFrame(LOG).to_excel(xw, sheet_name="Log_Perubahan", index=False)
    KAMUS.to_excel(xw, sheet_name="Kamus_Variabel", index=False)
    for ws in xw.book.worksheets:
        ws.freeze_panes = "A2"
        for col in ws.columns:
            w = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
            ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 8), 45)

print(ring.to_string(index=False))
print()
print(alasan.to_string(index=False))
print("\nsumber_tgl_lahir:", out.sumber_tgl_lahir.value_counts(dropna=False).to_dict())
print("sumber_jk:", out.sumber_jk.value_counts(dropna=False).to_dict())
print("presisi_umur:", out.presisi_umur.value_counts(dropna=False).to_dict())
print("desa:", out.desa.value_counts(dropna=False).to_dict())
print("flag tgl kunjungan:", out.flag_tgl_kunjungan.str.split(";").str[0].value_counts().to_dict())
print("tahun_kunjungan per sheet:\n", out.groupby(["kelompok_data", "tahun_kunjungan"]).size().to_string())
print("CEK tgl lahir:", out.flag_tgl_lahir.astype(bool).sum(), "| CEK umur:", out.flag_umur.astype(bool).sum(),
      "| CEK jk:", out.flag_jk.str.startswith("CEK").sum(), "| duplikat:", out.duplikat.sum())
print("log:", len(LOG), "->", OUT)
