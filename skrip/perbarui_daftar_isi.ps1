# Perbarui daftar isi laporan lewat Word dan simpan. PDF hanya diekspor bila argumen <pdf> diberikan.
# Usage: powershell -File perbarui_daftar_isi.ps1 <docx> [pdf]
param([string]$Docx, [string]$Pdf)
$src = (Resolve-Path $Docx).Path
if ($Pdf -and -not [System.IO.Path]::IsPathRooted($Pdf)) { $Pdf = Join-Path (Get-Location).Path $Pdf }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $doc = $w.Documents.Open($src)
    [void]$doc.Fields.Update()  # nomor SEQ keterangan tabel/gambar dulu, baru daftar isi/tabel/gambar
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
    $doc.Save()
    if ($Pdf) { $doc.SaveAs([ref]$Pdf, [ref]17) }
    "pages: " + $doc.ComputeStatistics(2)
    $doc.Close($false)
} finally { $w.Quit() }
