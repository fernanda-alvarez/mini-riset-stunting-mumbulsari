"""Daftar balita bermasalah gizi untuk tindak lanjut Puskesmas (INTERNAL: memuat identitas, jangan disebarkan).
Usage: python daftar_tindak_lanjut.py <xlsx analisis lanjut> <xlsx output>
"""
import sys
import pandas as pd

src, out = sys.argv[1], sys.argv[2]
a = pd.read_excel(src, sheet_name="Analisis_Per_Anak")
masalah = (a[["stunting", "underweight", "wasting"]] == 1).any(axis=1)
t = a[masalah].copy()


def ringkas(r):
    m = [s for s, c in [(r.status_TBU, "stunting"), (r.status_BBU, "underweight"), (r.status_BBTB, "wasting")]
         if r[c] == 1]
    return "; ".join(m)


t["masalah_gizi"] = t.apply(ringkas, axis=1)
# prioritas: gizi buruk / sangat pendek / BB sangat kurang lebih dulu
t["prioritas"] = t.apply(lambda r: 1 if any(s in str(r.masalah_gizi) for s in ["Gizi buruk", "Sangat pendek", "sangat kurang"]) else 2, axis=1)
t["catatan_verifikasi"] = t.apply(lambda r: "Ukur ulang dulu: data antropometri tidak konsisten/ekstrem"
                                  if r.perlu_cek_antropometri == 1 else "", axis=1)
kol = ["prioritas", "masalah_gizi", "catatan_verifikasi", "id_pasien", "nik", "nama", "nama_ortu", "desa", "jk", "tgl_lahir",
       "tgl_kunjungan", "umur_bulan", "bb_kg", "pb_cm", "zTBU", "zBBU", "zBBTB", "diagnosa", "sheet_sumber", "baris_excel"]
t = t[kol].sort_values(["prioritas", "desa", "nama"])
for c in ["umur_bulan", "zTBU", "zBBU", "zBBTB"]:
    t[c] = t[c].round(2)
info = pd.DataFrame({"keterangan": [
    "INTERNAL PUSKESMAS - memuat identitas pasien. Jangan dilampirkan pada laporan yang dibagikan.",
    "Isi: balita (analisis utama 2025-2026) dengan stunting, BB kurang, dan/atau wasting pada kunjungan MTBS pertama yang memenuhi syarat.",
    "Prioritas 1: sangat pendek, BB sangat kurang, atau gizi buruk. Prioritas 2: lainnya.",
    "Catatan verifikasi terisi bila data antropometri anak tidak konsisten/ekstrem: ukur ulang sebelum dirujuk.",
    f"Jumlah balita: {len(t)} (prioritas 1: {int((t.prioritas == 1).sum())}).",
]})
rek = t.groupby("desa").agg(balita=("nama", "size"), prioritas_1=("prioritas", lambda s: int((s == 1).sum()))).reset_index()
with pd.ExcelWriter(out, engine="openpyxl") as w:
    info.to_excel(w, sheet_name="Baca_Dulu", index=False)
    t.to_excel(w, sheet_name="Daftar_Tindak_Lanjut", index=False)
    rek.to_excel(w, sheet_name="Rekap_Per_Desa", index=False)
print(info.keterangan.iloc[-1]); print(rek.to_string(index=False))
