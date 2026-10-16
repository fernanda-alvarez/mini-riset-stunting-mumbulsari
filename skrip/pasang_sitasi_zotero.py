"""Ubah sitasi teks [n] dan daftar pustaka pada laporan docx menjadi field Zotero (Word plugin).
Hasilnya terbaca oleh tab Zotero di Word: Add/Edit Citation, Refresh, dan Document Preferences langsung berfungsi.
Data item diambil dari koleksi Zotero "Mini Riset MTBS Mumbulsari" lewat API lokal (Zotero harus terbuka);
bila Zotero tertutup dipakai salinan terakhir di "Referensi Mini Riset MTBS - Zotero.json".
Usage: python pasang_sitasi_zotero.py  (setelah buat_laporan_docx.py, sebelum perbarui_daftar_isi.ps1)
"""
import copy, json, os, random, re, string, urllib.request, zipfile, shutil, tempfile
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOC = "naskah/Laporan Mini Riset - Status Gizi Balita pada Kunjungan MTBS Puskesmas Mumbulsari 2025-2026.docx"
SNAP = "referensi/Referensi Mini Riset MTBS - Zotero.json"
BIB = "referensi/Referensi Mini Riset MTBS.bib"
API = "http://127.0.0.1:23119/api/users/0/collections/UQ9XZL3Y/items/top?limit=100&format="
USER_ID = 7207399  # akun Zotero pemilik pustaka (URI item: http://zotero.org/users/<id>/items/<key>)
STYLE = "http://www.zotero.org/styles/nlm-citation-sequence-brackets"  # Vancouver, nomor dalam kurung siku
SCHEMA = "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"


def ambil_referensi():
    """Daftar 16 item berurutan sesuai nomor Vancouver (= urutan entri di file .bib)."""
    try:
        get = lambda f: json.load(urllib.request.urlopen(API + f, timeout=10))
        js, csl = get("json"), get("csljson")
        # format=csljson memakai citation key BibTeX sebagai id; format=json urutannya sama
        ref = {c["id"]: {"key": j["key"], "csl": c} for j, c in zip(js, csl)}
        urut = re.findall(r"^@\w+\{([^,]+),", open(BIB, encoding="utf-8").read(), re.M)
        ref = [dict(ref[k], citekey=k) for k in urut]
        json.dump(ref, open(SNAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("Referensi diambil dari Zotero:", len(ref))
    except OSError:
        ref = json.load(open(SNAP, encoding="utf-8"))
        print("Zotero tidak terjangkau; memakai salinan", SNAP)
    return ref


def rid(n=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def run_el(rpr, kind, val=None):
    r = OxmlElement("w:r")
    if rpr is not None:
        r.append(rpr)
    if kind == "fld":
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), val)
    else:
        e = OxmlElement("w:instrText" if kind == "instr" else "w:t")
        e.set(qn("xml:space"), "preserve"); e.text = val
    r.append(e)
    return r


def field(rpr, instr, hasil):
    """Run-run field kompleks: begin, kode (dipecah per 255 karakter seperti Word), separate, hasil, end."""
    cp = lambda: copy_(rpr)
    out = [run_el(cp(), "fld", "begin")]
    out += [run_el(cp(), "instr", instr[i:i + 255]) for i in range(0, len(instr), 255)]
    out += [run_el(cp(), "fld", "separate"), run_el(cp(), "t", hasil), run_el(cp(), "fld", "end")]
    return out


def kode_sitasi(nomor, ref):
    teks = "[" + ",".join(map(str, nomor)) + "]"
    items = []
    for n in nomor:
        r = ref[n - 1]
        items.append({"id": r["key"], "uris": [f"http://zotero.org/users/{USER_ID}/items/{r['key']}"],
                      "itemData": dict(r["csl"], id=r["key"])})
    obj = {"citationID": rid(), "properties": {"formattedCitation": teks, "plainCitation": teks, "noteIndex": 0},
           "citationItems": items, "schema": SCHEMA}
    return " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(obj, ensure_ascii=False) + " ", teks


def idx_pustaka(ps):
    """Indeks judul DAFTAR PUSTAKA di batang tubuh (yang terakhir; entri daftar isi memuat nomor halaman)."""
    return max(i for i, p in enumerate(ps) if p.text.strip().upper() == "DAFTAR PUSTAKA")


def pasang_sitasi(d, ref):
    pola = re.compile(r"\[(\d{1,2}(?:,\d{1,2})*)\]")
    n_sitasi = 0
    ps = d.paragraphs
    for p in ps[:idx_pustaka(ps)]:
        for r in list(p._p.iter(qn("w:r"))):
            t = "".join(x.text or "" for x in r.iter(qn("w:t")))
            if not pola.search(t) or r.find(qn("w:instrText")) is not None:
                continue
            nomor_ok = all(1 <= int(n) <= len(ref) for m in pola.finditer(t) for n in m.group(1).split(","))
            if not nomor_ok:
                continue
            rpr = r.find(qn("w:rPr"))
            baru, pos = [], 0
            for m in pola.finditer(t):
                if m.start() > pos:
                    baru.append(run_el(copy_(rpr), "t", t[pos:m.start()]))
                instr, teks = kode_sitasi([int(n) for n in m.group(1).split(",")], ref)
                baru += field(rpr, instr, teks); n_sitasi += 1
                pos = m.end()
            if pos < len(t):
                baru.append(run_el(copy_(rpr), "t", t[pos:]))
            for b in baru:
                r.addprevious(b)
            r.getparent().remove(r)
    return n_sitasi


def copy_(rpr):
    return None if rpr is None else copy.deepcopy(rpr)


def pasang_bibliografi(d, n_ref):
    ps = d.paragraphs
    i0 = idx_pustaka(ps)
    entri = [p for p in ps[i0 + 1:] if p.text.strip()][:n_ref]
    assert all(re.match(rf"{k}\.\s", p.text) for k, p in enumerate(entri, 1)), "Entri daftar pustaka tidak urut"
    pertama, akhir = entri[0], entri[-1]
    rpr = copy_(pertama.runs[0]._r.find(qn("w:rPr")))
    awal = field(rpr, ' ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY ', "")
    # begin + kode + separate di awal entri pertama; end di akhir entri terakhir (hasil = teks entri yang ada)
    ppr = pertama._p.find(qn("w:pPr"))
    for el in reversed(awal[:-2]):
        if ppr is not None:
            ppr.addnext(el)
        else:
            pertama._p.insert(0, el)
    akhir._p.append(awal[-1])


def pasang_preferensi(path):
    """Simpan preferensi dokumen Zotero (gaya, tipe field) sebagai custom property ZOTERO_PREF_n."""
    pref = (f'<data data-version="3" zotero-version="10.0.6"><session id="{rid()}"/>'
            f'<style id="{STYLE}" hasBibliography="1" bibliographyStyleHasBeenSet="1"/>'
            '<prefs><pref name="fieldType" value="Field"/><pref name="automaticJournalAbbreviations" value="true"/>'
            '</prefs></data>')
    potong = [pref[i:i + 255] for i in range(0, len(pref), 255)]
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    props = "".join(
        f'<property fmtid="{{D5CDD505-2E9C-101B-9397-08002B2CF9AE}}" pid="{i + 2}" name="ZOTERO_PREF_{i + 1}">'
        f"<vt:lpwstr>{esc(s)}</vt:lpwstr></property>" for i, s in enumerate(potong))
    custom = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/'
              'officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/'
              f'docPropsVTypes">{props}</Properties>')
    tmp = tempfile.mktemp(suffix=".docx")
    with zipfile.ZipFile(path) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            if it.filename == "docProps/custom.xml":
                continue
            data = zi.read(it.filename)
            if it.filename == "[Content_Types].xml" and b"/docProps/custom.xml" not in data:
                data = data.replace(b"</Types>", b'<Override PartName="/docProps/custom.xml" ContentType="application/'
                                    b'vnd.openxmlformats-officedocument.custom-properties+xml"/></Types>')
            if it.filename == "_rels/.rels" and b"docProps/custom.xml" not in data:
                data = data.replace(b"</Relationships>", b'<Relationship Id="rIdZotero" Type="http://schemas.'
                                    b'openxmlformats.org/officeDocument/2006/relationships/custom-properties" '
                                    b'Target="docProps/custom.xml"/></Relationships>')
            zo.writestr(it, data)
        zo.writestr("docProps/custom.xml", custom)
    shutil.move(tmp, path)


def pasang_gaya():
    """Salin gaya CSL ke folder styles Zotero bila belum ada (aktif setelah Zotero dibuka ulang)."""
    src = "referensi/nlm-citation-sequence-brackets.csl"
    dst = os.path.join(os.path.expanduser("~"), "Zotero", "styles", os.path.basename(src))
    if os.path.exists(src) and os.path.isdir(os.path.dirname(dst)) and not os.path.exists(dst):
        shutil.copy(src, dst); print("Gaya CSL dipasang:", dst)


if __name__ == "__main__":
    ref = ambil_referensi()
    d = docx.Document(DOC)
    n = pasang_sitasi(d, ref)
    pasang_bibliografi(d, len(ref))
    d.save(DOC)
    pasang_preferensi(DOC)
    pasang_gaya()
    print(f"OK: {n} field sitasi + 1 field daftar pustaka Zotero ->", DOC)
