"""Membaca file Form_Pengisian_Data_Mini_Riset_MTBS.docx yang telah diisi oleh pengguna,
lalu menyinkronkan data isian tersebut ke dalam:
1. skrip/buat_laporan_docx.py (Nomor/tanggal izin & jadwal kegiatan)
2. data/olahan/MTBS Balita PKM Mumbulsari 2025-2026 - Daftar Tindak Lanjut (INTERNAL).xlsx
   (Nama orang tua, NIK, dan catatan verifikasi tindak lanjut klinis)
3. Memperbarui formatting Excel via skrip/percantik_excel.py
4. Membangun ulang naskah laporan Word mini riset
"""
from pathlib import Path
import re
import pandas as pd
import openpyxl
from docx import Document

BASE_DIR = Path(__file__).resolve().parent.parent
DOCX_FORM = BASE_DIR / "Form_Pengisian_Data_Mini_Riset_MTBS.docx"
SKRIP_LAP = BASE_DIR / "skrip" / "buat_laporan_docx.py"
EXCEL_DT = BASE_DIR / "data" / "olahan" / "MTBS Balita PKM Mumbulsari 2025-2026 - Daftar Tindak Lanjut (INTERNAL).xlsx"


def clean_val(v):
    if not v:
        return ""
    t = str(v).strip()
    # Abaikan jika masih berupa teks placeholder template
    if any(k in t for k in ("[isi", "[Nama Ibu", "[NIK", "[...", "[ ]", "isi status")):
        return ""
    return t


def sinkronkan():
    if not DOCX_FORM.exists():
        print(f"Error: {DOCX_FORM} tidak ditemukan!")
        return

    doc = Document(DOCX_FORM)
    tables = doc.tables
    print(f"Membaca {len(tables)} tabel dari {DOCX_FORM.name}...")

    # -------------------------------------------------------------
    # 1. Tabel Administratif & Jadwal (Tabel 0)
    # -------------------------------------------------------------
    t1 = tables[0]
    adm_data = {}
    for row in t1.rows[1:]:
        var_name = row.cells[0].text.strip()
        val_user = clean_val(row.cells[1].text)
        if val_user:
            adm_data[var_name] = val_user

    print(f"Data administratif yang diisi: {len(adm_data)} item")

    if adm_data and SKRIP_LAP.exists():
        with open(SKRIP_LAP, "r", encoding="utf-8") as f:
            lap_code = f.read()

        # Update nomor & tanggal izin bila diisi
        no_izin = adm_data.get("Nomor Surat Izin Penelitian")
        tgl_izin = adm_data.get("Tanggal Surat Izin Penelitian")
        if no_izin or tgl_izin:
            teks_izin = f"nomor {no_izin or '...'} tertanggal {tgl_izin or '...'}"
            lap_code = re.sub(r"\[isi: nomor/tanggal surat izin bila ada\]", teks_izin, lap_code)

        # Update tahap kegiatan bila diisi
        jadwal_parts = []
        for k in ("Tahap Persiapan & Proposal", "Tahap Pengumpulan Data MTBS", "Tahap Analisis & Pengolahan Data"):
            if k in adm_data:
                jadwal_parts.append(f"{k.split('&')[0].strip()}: {adm_data[k]}")
        if jadwal_parts:
            teks_jadwal = "; ".join(jadwal_parts)
            lap_code = re.sub(r"\[isi: tanggal pelaksanaan tiap tahap\]", teks_jadwal, lap_code)

        with open(SKRIP_LAP, "w", encoding="utf-8") as f:
            f.write(lap_code)
        print("  -> skrip/buat_laporan_docx.py berhasil disinkronkan.")

    # -------------------------------------------------------------
    # 2. Tabel Prioritas 1 & Prioritas 2 (Tabel 2 dan Tabel 3)
    # -------------------------------------------------------------
    # Peta update: id_pasien -> {nama_ortu, nik, catatan_verifikasi}
    updates = {}

    def proses_tabel_prioritas(tbl, col_id_idx, col_ortu_idx, col_cat_idx):
        for row in tbl.rows[1:]:
            id_raw = row.cells[col_id_idx].text.strip().split("\n")[0].strip()
            if not id_raw or id_raw == "-":
                continue

            # Bersihkan id
            try:
                id_clean = int(float(id_raw))
            except ValueError:
                id_clean = id_raw

            ortu_nik_text = row.cells[col_ortu_idx].text.strip().split("\n")
            ortu_val = clean_val(ortu_nik_text[0]) if len(ortu_nik_text) > 0 else ""
            nik_val = clean_val(ortu_nik_text[1]) if len(ortu_nik_text) > 1 else ""

            cat_val = clean_val(row.cells[col_cat_idx].text)

            if ortu_val or nik_val or cat_val:
                updates[str(id_clean)] = {
                    "nama_ortu": ortu_val,
                    "nik": nik_val,
                    "catatan_verifikasi": cat_val,
                }

    if len(tables) >= 3:
        # Tabel 2: Prioritas 1
        proses_tabel_prioritas(tables[2], col_id_idx=1, col_ortu_idx=5, col_cat_idx=6)

    if len(tables) >= 4:
        # Tabel 3: Prioritas 2
        proses_tabel_prioritas(tables[3], col_id_idx=1, col_ortu_idx=4, col_cat_idx=5)

    print(f"Total balita yang memiliki data isian baru: {len(updates)} balita")

    # Tulis pembaruan ke Excel Daftar Tindak Lanjut
    if updates and EXCEL_DT.exists():
        wb = openpyxl.load_workbook(EXCEL_DT)
        if "Daftar_Tindak_Lanjut" in wb.sheetnames:
            ws = wb["Daftar_Tindak_Lanjut"]
            headers = [str(ws.cell(1, c).value or "").strip() for c in range(1, ws.max_column + 1)]
            col_id = headers.index("id_pasien") + 1
            col_ortu = headers.index("nama_ortu") + 1
            col_nik = headers.index("nik") + 1
            col_cat = headers.index("catatan_verifikasi") + 1

            updated_count = 0
            for r in range(2, ws.max_row + 1):
                val_id = str(ws.cell(r, col_id).value or "").replace(" 00:00:00", "").strip()
                try:
                    val_id_clean = str(int(float(val_id)))
                except ValueError:
                    val_id_clean = val_id

                if val_id_clean in updates:
                    u = updates[val_id_clean]
                    if u["nama_ortu"]:
                        ws.cell(r, col_ortu).value = u["nama_ortu"]
                    if u["nik"]:
                        ws.cell(r, col_nik).value = u["nik"]
                    if u["catatan_verifikasi"]:
                        ws.cell(r, col_cat).value = u["catatan_verifikasi"]
                    updated_count += 1

            wb.save(EXCEL_DT)
            print(f"  -> {updated_count} baris di {EXCEL_DT.name} berhasil diperbarui!")

    print("\nSinkronisasi selesai! Seluruh isian dari Word telah dialirkan ke sistem.")


if __name__ == "__main__":
    sinkronkan()
