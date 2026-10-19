"""Halaman HTML ringkasan hasil analisis (agregat saja, tanpa identitas anak) agar mudah dilihat di browser.
Usage: python ringkasan_html.py   (dari folder induk proyek)  ->  Ringkasan Hasil.html
"""
import base64, html, sys
import pandas as pd

F = "data/olahan/MTBS Balita PKM Mumbulsari 2025-2026 - "
OUT = "Ringkasan Hasil.html"
tg = pd.read_excel(F + "Tabel & Grafik.xlsx", sheet_name=None)
kt = pd.read_excel(F + "Kualitas Tambahan.xlsx", sheet_name=None)
kq = pd.read_excel(F + "Kelengkapan & Kualitas.xlsx", sheet_name=None)
zs = pd.read_excel(F + "Z-score & Deskriptif.xlsx", sheet_name="Proporsi_IK95")
tot = zs[zs.variabel == "Total"].set_index("indikator")


def fmt(v):
    if pd.isna(v):
        return ""
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) < 1 else f"{v:,.1f}"
    return html.escape(str(v))


def tabel(df, judul):
    df = df.dropna(how="all")
    h = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    r = "".join("<tr>" + "".join(f"<td>{fmt(v)}</td>" for v in row) + "</tr>" for row in df.itertuples(index=False))
    return f"<h3>{judul}</h3><div class='sc'><table><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table></div>"


def gambar(path, judul):
    b = base64.b64encode(open(path, "rb").read()).decode()
    return f"<figure><img src='data:image/png;base64,{b}' alt='{judul}'><figcaption>{judul}</figcaption></figure>"


kartu = "".join(
    f"<div class='k'><b>{tot.loc[i, 'persen']:.1f}%</b><span>{n}</span><small>IK 95% {tot.loc[i, 'IK95_bawah']:.1f}–{tot.loc[i, 'IK95_atas']:.1f}, n = {int(tot.loc[i, 'n'])}</small></div>"
    for i, n in [("stunting", "Stunting (TB/U)"), ("underweight", "BB kurang (BB/U)"), ("wasting", "Wasting (BB/TB)")])

isi = (f"<div class='kartu'>{kartu}</div>"
       + "<h2>Gambar</h2><div class='gb'>"
       + "".join(gambar(f"grafik/{f}", j) for f, j in [
           ("G0_diagram_alur.png", "Alur subjek"), ("G3_distribusi_status_gizi.png", "Distribusi status gizi"),
           ("G4_sebaran_z_TBU.png", "Sebaran z-score TB/U"), ("G1_stunting_kelompok_umur.png", "Stunting menurut umur"),
           ("G2_stunting_desa.png", "Stunting menurut desa")]) + "</div><h2>Tabel</h2>"
       + tabel(tg["Tabel2_Status_Gizi"], "Distribusi status gizi")
       + tabel(tg["Tabel3_Stunting_Karakteristik"], "Stunting menurut karakteristik")
       + tabel(kt["SD_Adjusted"], "Proporsi teramati dan SD-adjusted")
       + tabel(kt["Digit_Preference"], "Digit preference")
       + tabel(kt["Sensitivitas_Termasuk_2024"], "Sensitivitas: termasuk kunjungan 2024")
       + tabel(tg["Sensitivitas_Umur_Kasar"], "Sensitivitas: balita umur kasar")
       + tabel(kq["Kelengkapan"], "Kelengkapan pencatatan")
       + tabel(kq["Kualitas_Zscore"], "Kualitas z-score")
       + tabel(tg["Tabel4_Gizi_Diagnosis"], "Status gizi menurut diagnosis MTBS")
       + tabel(kt["Alur_Subjek"], "Alur subjek"))

css = """:root{--bg:#fff;--fg:#1b1f24;--mut:#667;--ln:#d8dce2;--ac:#0b6e4f;--cd:#f4f7f6}
@media(prefers-color-scheme:dark){:root{--bg:#14181c;--fg:#e6e9ec;--mut:#99a;--ln:#2c333a;--ac:#5fd0a8;--cd:#1c2228}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px}h1{font-size:1.5rem}h2{margin-top:2rem;border-bottom:1px solid var(--ln)}
h3{font-size:1rem;margin:1.5rem 0 .4rem}.kartu{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.k{background:var(--cd);border:1px solid var(--ln);border-radius:8px;padding:14px}.k b{display:block;font-size:2rem;color:var(--ac)}
.k small{display:block;color:var(--mut)}.gb{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
figure{margin:0}img{max-width:100%;border:1px solid var(--ln);border-radius:6px;background:#fff}figcaption{color:var(--mut);font-size:.85rem}
.sc{overflow-x:auto}table{border-collapse:collapse;font-size:.85rem;min-width:100%}th,td{border:1px solid var(--ln);padding:4px 8px;text-align:left}
th{background:var(--cd)}p.n{color:var(--mut)}"""
open(OUT, "w", encoding="utf-8").write(
    f"<!doctype html><html lang='id'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    f"<title>Ringkasan Hasil MTBS</title><style>{css}</style></head><body><main>"
    "<h1>Status Gizi Balita, Kunjungan MTBS Puskesmas Mumbulsari 2025–2026</h1>"
    "<p class='n'>Proporsi pada balita sakit yang berkunjung (anak dengan kunjungan layak pertama), bukan prevalensi wilayah. "
    "Standar WHO 2006, kategori Permenkes 2/2020.</p>" + isi + "</main></body></html>")
print("OK", OUT)
