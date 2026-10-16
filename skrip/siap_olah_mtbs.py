"""Buat file 'Siap Olah' dari file Data Bersih MTBS.
Usage: python siap_olah_mtbs.py <xlsx data bersih> <xlsx output> [--semua-periode]
Periode analisis utama: kunjungan 2025-2026 (tab "2025" juga memuat kunjungan Juli-Des 2024);
--semua-periode ikut menyertakan 2024 untuk analisis sensitivitas.
Kriteria inklusi: umur 0-60 bulan dengan presisi bukan 'kasar', JK terisi, PB valid, bukan duplikat.
Baris yang tidak memenuhi tidak dihapus, tapi dipindah ke sheet Dikeluarkan beserta alasannya.
"""
import sys
import pandas as pd

src, out = sys.argv[1], sys.argv[2]
SEMUA_PERIODE = "--semua-periode" in sys.argv[3:]
d = pd.read_excel(src, sheet_name="Data_Bersih")


def alasan(r):
    a = []
    if not SEMUA_PERIODE and pd.notna(r["tgl_kunjungan"]) and pd.Timestamp(r["tgl_kunjungan"]).year < 2025:
        a.append("kunjungan 2024 (di luar periode)")
    if str(r["presisi_umur"]).startswith("kasar"):
        a.append("umur kasar (tahun bulat)")
    if pd.isna(r["umur_bulan"]):
        a.append("umur tidak ada")
    elif not (0 <= r["umur_bulan"] <= 60):
        a.append("di luar 0-60 bulan")
    if pd.notna(r["flag_umur"]) and "CEK" in str(r["flag_umur"]).upper():
        a.append("umur perlu dicek")
    if pd.isna(r["jk"]) or str(r["jk"]).strip() == "":
        a.append("JK tidak ada")
    if pd.isna(r["pb_cm"]):
        a.append("PB tidak ada/tidak valid")
    if r["duplikat"] is True or str(r["duplikat"]).upper() == "TRUE":
        a.append("duplikat")
    return "; ".join(a)


d["alasan_dikeluarkan"] = d.apply(alasan, axis=1)
masuk = d[d["alasan_dikeluarkan"] == ""].drop(columns=["alasan_dikeluarkan"]).copy()
keluar = d[d["alasan_dikeluarkan"] != ""].copy()

# Satu baris per anak: kunjungan pertama yang memenuhi syarat (unit analisis potong lintang)
masuk = masuk.sort_values(["id_pasien", "tgl_kunjungan"])
masuk["kunjungan_ke_anak"] = masuk.groupby("id_pasien").cumcount() + 1
masuk["jml_kunjungan_layak_anak"] = masuk.groupby("id_pasien")["id_pasien"].transform("size")
per_anak = masuk[masuk["kunjungan_ke_anak"] == 1].copy()

# Rekap alasan: tiap alasan dihitung terpisah (satu baris bisa punya >1 alasan)
rek = (keluar["alasan_dikeluarkan"].str.split("; ").explode()
       .value_counts().rename_axis("alasan").reset_index(name="jumlah_kunjungan"))
ring = pd.DataFrame({
    "keterangan": ["Total kunjungan (Data_Bersih)", "Kunjungan siap olah", "Anak siap olah (unit analisis)",
                   "Kunjungan dikeluarkan"],
    "nilai": [len(d), len(masuk), len(per_anak), len(keluar)],
})
per_sheet = masuk.groupby("sheet_sumber").agg(kunjungan=("id_pasien", "size"),
                                              anak=("id_pasien", "nunique")).reset_index()

with pd.ExcelWriter(out, engine="openpyxl") as w:
    per_anak.to_excel(w, sheet_name="Analisis_Per_Anak", index=False)
    masuk.to_excel(w, sheet_name="Semua_Kunjungan_Layak", index=False)
    keluar.to_excel(w, sheet_name="Dikeluarkan", index=False)
    ring.to_excel(w, sheet_name="Ringkasan", index=False)
    per_sheet.to_excel(w, sheet_name="Ringkasan", index=False, startrow=len(ring) + 2)
    rek.to_excel(w, sheet_name="Ringkasan", index=False, startrow=len(ring) + len(per_sheet) + 5)

print(ring.to_string(index=False)); print(per_sheet.to_string(index=False)); print(rek.to_string(index=False))
