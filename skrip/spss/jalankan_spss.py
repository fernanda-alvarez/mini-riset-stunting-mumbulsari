"""Jalankan syntax SPSS tanpa antarmuka lewat Python bawaan SPSS (modul spss).
Pakai (dari folder induk proyek):
  "C:/Program Files/IBM/SPSS/Statistics/27/Python3/python.exe" skrip/spss/jalankan_spss.py skrip/spss/analisis_spss.sps [keluaran.spv]
Syntax dijalankan perintah demi perintah dengan folder kerja = folder induk proyek, jadi jalur di dalam .sps relatif terhadap folder itu.
Bila ada perintah yang gagal, perintah itu dicetak dan proses berhenti."""
import os
import sys

SPSS_DIR = r"C:\Program Files\IBM\SPSS\Statistics\27"
os.environ["PATH"] = SPSS_DIR + os.pathsep + os.environ.get("PATH", "")
import spss  # noqa: E402


def perintah(baris):
    """Pecah isi .sps menjadi perintah: DEFINE...!ENDDEFINE satu blok, selain itu sampai baris berakhiran titik."""
    buf, makro = [], False
    for b in baris:
        if not buf and not b.strip():
            continue
        buf.append(b)
        s = b.strip()
        if len(buf) == 1 and s.upper().startswith("DEFINE"):
            makro = True
        if makro:
            if s.upper().startswith("!ENDDEFINE"):
                yield "\n".join(buf)
                buf, makro = [], False
        elif s.endswith("."):
            yield "\n".join(buf)
            buf = []
    if buf:
        yield "\n".join(buf)


sintaks = sys.argv[1]
spv = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
akar = os.getcwd().replace("\\", "/")
os.makedirs(os.path.join(akar, "data/sigizi/analisis_spss/tmp"), exist_ok=True)
spss.Submit(f"CD '{akar}'.")
if spv:
    spss.Submit("OUTPUT NEW NAME=hasil.")
LOG = akar + "/data/sigizi/analisis_spss/tmp/pesan_spss.txt"
spss.Submit(f"OMS /SELECT WARNINGS /DESTINATION FORMAT=TEXT OUTFILE='{LOG}' VIEWER=YES.")
with open(sintaks, encoding="utf-8") as f:
    for p in perintah(f.read().splitlines()):
        try:
            spss.Submit(p)
        except Exception as e:  # noqa: BLE001
            sys.stdout.flush()
            spss.Submit("OMSEND.")
            print("\n*** GAGAL pada perintah:\n" + p + "\n*** " + str(e), file=sys.stderr)
            print(open(LOG, encoding="utf-8-sig", errors="replace").read()[-1500:].encode("ascii", "replace").decode(), file=sys.stderr)
            sys.exit(1)
spss.Submit("OMSEND.")
if spv:
    spss.Submit(f"OUTPUT SAVE NAME=hasil OUTFILE='{spv.replace(chr(92), '/')}'.")
print("Selesai.")
