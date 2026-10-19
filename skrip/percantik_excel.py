"""Percantik tampilan seluruh berkas Excel olahan penelitian MTBS Mumbulsari.
Menerapkan:
- Perbaikan otomatis relasi orphan openxlsx (R)
- Font Segoe UI yang modern dan profesional
- Header berwarna kontras dengan teks putih tebal
- Zebra striping (selang-seling baris halus)
- Freeze panes pada baris judul
- Autofilter pada setiap tabel
- Perataan teks (kiri untuk teks, tengah untuk ID/tanggal/kode, kanan untuk angka)
- Format angka, desimal z-score, dan persentase yang rapi
- Auto-width kolom dengan batas minimum dan maksimum
- Penyorotan baris prioritas (merah/kuning) pada Daftar Tindak Lanjut
- Penyisipan visual grafik G0-G4 pada sheet Grafik di Tabel & Grafik.xlsx
"""
import io
import os
import posixpath
import re
import zipfile
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image

FONT_FAMILY = "Segoe UI"
BASE_FONT_SIZE = 10
HEADER_FONT_SIZE = 10.5

# Palet warna
FILL_HEADER_TEAL = PatternFill(start_color="0B6E4F", end_color="0B6E4F", fill_type="solid")     # Medis / Publikasi
FILL_HEADER_NAVY = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")     # Data / Analisis
FILL_HEADER_BLUE = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")     # Kualitas
FILL_HEADER_WARN = PatternFill(start_color="B45309", end_color="B45309", fill_type="solid")     # Peringatan / Cek
FILL_HEADER_ALERT = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")    # Prioritas / Tindak Lanjut

FILL_ZEBRA_EVEN = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
FILL_ZEBRA_ODD = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

FILL_PRIORITY_1 = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")    # Soft Rose
FONT_PRIORITY_1 = Font(name=FONT_FAMILY, size=BASE_FONT_SIZE, bold=True, color="991B1B")

FILL_PRIORITY_2 = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")    # Soft Amber
FONT_PRIORITY_2 = Font(name=FONT_FAMILY, size=BASE_FONT_SIZE, bold=True, color="92400E")

FONT_HEADER = Font(name=FONT_FAMILY, size=HEADER_FONT_SIZE, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name=FONT_FAMILY, size=BASE_FONT_SIZE, color="1F2937")
FONT_BOLD = Font(name=FONT_FAMILY, size=BASE_FONT_SIZE, bold=True, color="1F2937")

BORDER_THIN_COLOR = "E2E8F0"
BORDER_BOTTOM_HEADER = "CBD5E1"

THIN_SIDE = Side(border_style="thin", color=BORDER_THIN_COLOR)
MEDIUM_HEADER_BOTTOM = Side(border_style="medium", color=BORDER_BOTTOM_HEADER)

CELL_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)
HEADER_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=MEDIUM_HEADER_BOTTOM)

ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
ALIGN_HEADER = Alignment(horizontal="center", vertical="center", wrap_text=True)


EMPTY_DRAWING = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>'
EMPTY_VML = b'<xml xmlns:v="urn:schemas-microsoft-com:vml"/>'


def perbaiki_relasi_xlsx(file_path: Path):
    """Suntikkan berkas dummy untuk drawing/vml/printerSettings yang dirujuk rels tapi belum ada di zip."""
    try:
        with zipfile.ZipFile(file_path, "r") as zin:
            names = set(zin.namelist())
            missing_items = {}
            for name in names:
                if name.endswith(".rels"):
                    content = zin.read(name)
                    # Direktori dasar rels adalah induk dari _rels
                    rel_dir = posixpath.dirname(posixpath.dirname(name))
                    targets = re.findall(rb'Target="([^"]+)"', content)
                    for t in targets:
                        t_str = t.decode("utf-8")
                        if t_str.startswith("http"):
                            continue
                        resolved = posixpath.normpath(posixpath.join(rel_dir, t_str))
                        if resolved not in names:
                            if "vml" in resolved:
                                missing_items[resolved] = EMPTY_VML
                            elif "drawing" in resolved:
                                missing_items[resolved] = EMPTY_DRAWING
                            else:
                                missing_items[resolved] = b""

            if not missing_items:
                return

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    zout.writestr(item, zin.read(item.filename))
                for path, data in missing_items.items():
                    zout.writestr(path, data)

        with open(file_path, "wb") as f:
            f.write(buf.getvalue())
    except Exception as e:
        print(f"  [Warning perbaikan relasi]: {e}")


def tentukan_header_fill(file_path: Path, sheet_name: str) -> PatternFill:
    s_lower = sheet_name.lower()
    f_lower = file_path.name.lower()
    if "tindak lanjut" in f_lower:
        return FILL_HEADER_ALERT
    if "implausible" in s_lower or "perlu_cek" in s_lower or "dikeluarkan" in s_lower:
        return FILL_HEADER_WARN
    if "kualitas" in f_lower or "kelengkapan" in f_lower:
        return FILL_HEADER_BLUE
    if "tabel & grafik" in f_lower or "z-score" in f_lower or "siap olah" in f_lower:
        return FILL_HEADER_TEAL
    return FILL_HEADER_NAVY


def format_angka(val, col_name_lower):
    if val is None:
        return None
    # Tanggal
    if "tgl" in col_name_lower or "tanggal" in col_name_lower:
        return "yyyy-mm-dd"
    # Z-Score
    if col_name_lower.startswith("z") or "zscore" in col_name_lower or "rerata_z" in col_name_lower or "sd_z" in col_name_lower:
        return "0.00"
    # Persen
    if "persen" in col_name_lower or col_name_lower in ("p", "or_kasar"):
        if isinstance(val, (int, float)):
            return "0.0" if "persen" in col_name_lower else "0.00"
    # Umur bulan / BB / PB
    if col_name_lower in ("umur_bulan", "bb_kg", "pb_cm", "lk_cm", "suhu_c"):
        return "0.0" if isinstance(val, float) else "0"
    # Integer count
    if isinstance(val, int) and col_name_lower in ("n", "kasus", "kunjungan", "nilai", "jumlah_kunjungan", "balita"):
        return "#,##0"
    return None


def perataan_kolom(col_name_lower):
    if any(k in col_name_lower for k in ("id_pasien", "nik", "jk", "tgl", "tahun", "prioritas", "kode", "flag")):
        return ALIGN_CENTER
    if any(k in col_name_lower for k in ("n", "kasus", "persen", "persen_", "ik95", "p", "or", "bb", "pb", "umur", "rerata", "sd", "median", "z")):
        return ALIGN_RIGHT
    return ALIGN_LEFT


def percantik_sheet(ws, file_path: Path):
    if ws.max_row == 0 or ws.max_column == 0 or (ws.max_row == 1 and ws.max_column == 1 and ws.cell(1, 1).value is None):
        return

    # Khusus sheet Baca_Dulu atau Catatan teks panjang
    if ws.max_column == 1 and ws.title.lower() in ("baca_dulu", "catatan"):
        ws.column_dimensions["A"].width = 110
        ws.row_dimensions[1].height = 24
        header_fill = tentukan_header_fill(file_path, ws.title)
        c1 = ws.cell(1, 1)
        c1.font = FONT_HEADER
        c1.fill = header_fill
        c1.alignment = ALIGN_LEFT
        c1.border = HEADER_BORDER
        for r in range(2, ws.max_row + 1):
            cell = ws.cell(r, 1)
            cell.font = FONT_REGULAR
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            cell.border = CELL_BORDER
            ws.row_dimensions[r].height = 28
        return

    # Ambil baris header
    header_fill = tentukan_header_fill(file_path, ws.title)
    ws.row_dimensions[1].height = 28

    headers = [str(ws.cell(1, col).value or "") for col in range(1, ws.max_column + 1)]
    col_names_lower = [h.strip().lower() for h in headers]

    # Style header
    for col_idx in range(1, ws.max_column + 1):
        cell = ws.cell(1, col_idx)
        cell.font = FONT_HEADER
        cell.fill = header_fill
        cell.alignment = ALIGN_HEADER
        cell.border = HEADER_BORDER

    # Freeze header
    ws.freeze_panes = "A2"

    # Autofilter
    max_col_letter = get_column_letter(ws.max_column)
    ws.auto_filter.ref = f"A1:{max_col_letter}{ws.max_row}"

    # Cari indeks prioritas bila ada (pada file tindak lanjut)
    idx_prioritas = None
    if "prioritas" in col_names_lower:
        idx_prioritas = col_names_lower.index("prioritas") + 1

    # Style data rows
    col_max_lens = {col_idx: len(headers[col_idx - 1]) for col_idx in range(1, ws.max_column + 1)}

    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)
        row_fill = FILL_ZEBRA_EVEN if is_even else FILL_ZEBRA_ODD

        # Cek penanda prioritas jika sheet tindak lanjut
        is_p1 = False
        is_p2 = False
        if idx_prioritas:
            pval = str(ws.cell(row_idx, idx_prioritas).value or "").strip()
            if pval == "1":
                is_p1 = True
            elif pval == "2":
                is_p2 = True

        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row_idx, col_idx)
            val = cell.value
            cname = col_names_lower[col_idx - 1]

            # Track length for column auto-width
            if val is not None:
                val_str = str(val)
                col_max_lens[col_idx] = max(col_max_lens[col_idx], len(val_str))

            # Alignment
            cell.alignment = perataan_kolom(cname)

            # Border
            cell.border = CELL_BORDER

            # Number formatting
            num_fmt = format_angka(val, cname)
            if num_fmt:
                cell.number_format = num_fmt

            # Font & Fill
            if is_p1 and col_idx == idx_prioritas:
                cell.fill = FILL_PRIORITY_1
                cell.font = FONT_PRIORITY_1
            elif is_p2 and col_idx == idx_prioritas:
                cell.fill = FILL_PRIORITY_2
                cell.font = FONT_PRIORITY_2
            else:
                cell.fill = row_fill
                cell.font = FONT_REGULAR

    # Auto-adjust column widths
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        raw_len = col_max_lens.get(col_idx, 10)
        padded_width = max(raw_len + 4, 11)
        clamped_width = min(padded_width, 45)
        ws.column_dimensions[col_letter].width = clamped_width


def perindah_sheet_grafik(wb, base_dir: Path):
    """Isi sheet Grafik pada Tabel & Grafik.xlsx dengan gambar G0-G4 jika tersedia."""
    grafik_dir = base_dir / "grafik"
    if not grafik_dir.exists():
        return

    if "Grafik" not in wb.sheetnames:
        return

    ws = wb["Grafik"]
    # Bersihkan jika kosong
    for r in list(ws.rows):
        for cell in r:
            cell.value = None

    ws.views.sheetView[0].showGridLines = True
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 95

    # Judul Sheet
    ws["B2"] = "DOKUMENTASI VISUALISASI HASIL PENELITIAN (GRAFIK G0 – G4)"
    ws["B2"].font = Font(name=FONT_FAMILY, size=14, bold=True, color="0B6E4F")
    ws["B3"] = "Status Gizi Balita pada Kunjungan MTBS Puskesmas Mumbulsari 2025–2026"
    ws["B3"].font = Font(name=FONT_FAMILY, size=11, italic=True, color="4B5563")

    grafik_files = [
        ("G0_diagram_alur.png", "G0. Diagram Alur Seleksi Subjek Penelitian"),
        ("G1_stunting_kelompok_umur.png", "G1. Proporsi Stunting Berdasarkan Kelompok Umur Balita"),
        ("G2_stunting_desa.png", "G2. Sebaran Proporsi Stunting Antar-Desa di Wilayah Kerja Puskesmas Mumbulsari"),
        ("G3_distribusi_status_gizi.png", "G3. Distribusi Status Gizi (TB/U, BB/U, BB/TB) Menurut Standar WHO 2006"),
        ("G4_sebaran_z_TBU.png", "G4. Kurva Sebaran Z-score Tinggi Badan menurut Umur (TB/U) vs Standar WHO"),
    ]

    curr_row = 5
    for fname, title in grafik_files:
        fpath = grafik_dir / fname
        if not fpath.exists():
            continue

        ws.cell(curr_row, 2, title).font = Font(name=FONT_FAMILY, size=11, bold=True, color="1E293B")
        ws.cell(curr_row, 2).fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        ws.row_dimensions[curr_row].height = 24
        curr_row += 1

        img = Image(str(fpath))
        orig_w, orig_h = img.width, img.height
        target_w = 640
        ratio = target_w / float(orig_w) if orig_w > 0 else 1.0
        img.width = int(target_w)
        img.height = int(orig_h * ratio)

        anchor_cell = f"B{curr_row}"
        ws.add_image(img, anchor_cell)

        est_rows = max(int(img.height / 20) + 3, 18)
        curr_row += est_rows


def proses_semua_excel(base_dir: Path):
    target_dirs = [base_dir / "data" / "olahan", base_dir / "data" / "sensitivitas"]
    files = []
    for td in target_dirs:
        if td.exists():
            files.extend(td.glob("*.xlsx"))

    print(f"Ditemukan {len(files)} berkas Excel untuk dipercantik...\n")

    for f in files:
        print(f"Memproses: {f.name} ...")
        perbaiki_relasi_xlsx(f)
        wb = openpyxl.load_workbook(f)
        for sname in wb.sheetnames:
            ws = wb[sname]
            if sname == "Grafik" and f.name.startswith("MTBS Balita PKM Mumbulsari 2025-2026 - Tabel & Grafik"):
                perindah_sheet_grafik(wb, base_dir)
            else:
                percantik_sheet(ws, f)
        wb.save(f)
        print(f"  -> Selesai dipercantik: {f.name}")

    print("\nSemua berkas Excel berhasil dipercantik dengan tampilan modern dan profesional!")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    proses_semua_excel(BASE_DIR)
