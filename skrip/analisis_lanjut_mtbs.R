# (1) Cek konsistensi PB/BB antar-kunjungan per anak, (2) hubungan status gizi x diagnosis MTBS.
# Usage: Rscript analisis_lanjut_mtbs.R <xlsx data bersih> <xlsx z-score> <xlsx output>
suppressMessages({ library(readxl); library(openxlsx) })
a <- commandArgs(TRUE)
semua <- as.data.frame(read_excel(a[1], sheet = "Data_Bersih"))
anak <- as.data.frame(read_excel(a[2], sheet = "Analisis_Per_Anak"))

## (1) Konsistensi longitudinal: semua kunjungan (bukan hanya yang layak) dengan id_pasien
s <- semua[!is.na(semua$id_pasien) & !is.na(semua$tgl_kunjungan), ]
s$tgl_kunjungan <- as.Date(s$tgl_kunjungan)
s <- s[order(s$id_pasien, s$tgl_kunjungan), ]
temuan <- list()
for (id in unique(s$id_pasien[duplicated(s$id_pasien)])) {
  x <- s[s$id_pasien == id, ]
  for (i in 2:nrow(x)) {
    hari <- as.numeric(x$tgl_kunjungan[i] - x$tgl_kunjungan[i - 1]); if (hari <= 0) next
    m <- c()
    dpb <- x$pb_cm[i] - x$pb_cm[i - 1]; dbb <- x$bb_kg[i] - x$bb_kg[i - 1]
    if (!is.na(dpb)) {
      # PB tidak mungkin turun; toleransi 2 cm (beda posisi ukur/kesalahan ukur wajar)
      if (dpb < -2) m <- c(m, sprintf("PB turun %.1f cm", -dpb))
      # laju > 4 cm/bulan di luar masa bayi awal tidak fisiologis
      if (hari >= 14 && dpb / (hari / 30.4375) > 4 && x$umur_bulan[i] %in% x$umur_bulan[i] && !is.na(x$umur_bulan[i]) && x$umur_bulan[i] > 6)
        m <- c(m, sprintf("PB naik %.1f cm dalam %d hari", dpb, hari))
    }
    if (!is.na(dbb) && x$bb_kg[i - 1] > 0) {
      r <- dbb / x$bb_kg[i - 1]
      if (hari <= 60 && abs(r) > 0.25) m <- c(m, sprintf("BB berubah %+.0f%% dalam %d hari", 100 * r, hari))
    }
    if (length(m)) temuan[[length(temuan) + 1]] <- data.frame(
      id_pasien = id, nama = x$nama[i], sheet_sumber = x$sheet_sumber[i],
      baris_excel_sebelum = x$baris_excel[i - 1], baris_excel = x$baris_excel[i],
      tgl_sebelum = x$tgl_kunjungan[i - 1], tgl = x$tgl_kunjungan[i], selang_hari = hari,
      pb_sebelum = x$pb_cm[i - 1], pb = x$pb_cm[i], bb_sebelum = x$bb_kg[i - 1], bb = x$bb_kg[i],
      masalah = paste(m, collapse = "; "))
  }
}
inkons <- if (length(temuan)) do.call(rbind, temuan) else data.frame()
anak$flag_inkonsisten_longitudinal <- as.integer(anak$id_pasien %in% inkons$id_pasien)
anak$flag_z_implausible <- as.integer(anak$flag_zTBU %in% 1 | anak$flag_zBBU %in% 1 | anak$flag_zBBTB %in% 1)
anak$perlu_cek_antropometri <- as.integer(anak$flag_inkonsisten_longitudinal == 1 | anak$flag_z_implausible == 1)

## (2) Kelompok diagnosis (multi-label: satu anak bisa >1 kelompok)
teks <- toupper(paste(anak$diagnosa, anak$kode_diagnosa))
teks[is.na(anak$diagnosa) & is.na(anak$kode_diagnosa)] <- NA
pola <- list(
  dx_ISPA_atas   = "ISPA|COMMON COLD|C ?COLD|\\bCC\\b|FARING|RFA|RHINO|COUGH|BATUK|TONSIL|J0[0-6]",
  dx_pneumonia   = "PNEUMONI|\\bBP\\b|J1[2-8]",
  dx_diare       = "GEA|DIARE|DIARR|DISENT|DCA|A0[0-9]",
  dx_demam       = "FEVER|FEBRIS|DEMAM|R50|DENGUE|DHF|TIFOID|TYPHOID",
  dx_kulit       = "SKABIES|SCABIES|DERMATITIS|IMPETIGO|FURUN|PIODERMA|TINEA|VARICELLA|URTIKARIA|B86|L[0-9]",
  dx_telinga     = "\\bOMA\\b|OMSK|OTITIS|SERUMEN|H6[0-9]",
  dx_susp_TB     = "\\bTB\\b|TUBERKUL")
for (nm in names(pola)) anak[[nm]] <- ifelse(is.na(teks), NA, as.integer(grepl(pola[[nm]], teks)))
anak$dx_lainnya <- ifelse(is.na(teks), NA, as.integer(rowSums(anak[names(pola)]) == 0))
dxs <- c(names(pola), "dx_lainnya")

## Uji hubungan: tiap outcome x tiap kelompok diagnosis
uji <- function(d, out, dx) {
  dd <- d[!is.na(d[[out]]) & !is.na(d[[dx]]), ]
  t <- table(factor(dd[[dx]], 0:1), factor(dd[[out]], 0:1))
  if (sum(t[2, ]) < 1) return(NULL)
  p <- if (any(suppressWarnings(chisq.test(t)$expected) < 5)) fisher.test(t)$p.value else chisq.test(t, correct = FALSE)$p.value
  uji_nm <- if (any(suppressWarnings(chisq.test(t)$expected) < 5)) "Fisher" else "Chi-square"
  or_c <- tryCatch({ m <- glm(dd[[out]] ~ dd[[dx]], family = binomial); exp(c(coef(m)[2], suppressMessages(confint.default(m))[2, ])) },
                   error = function(e) rep(NA, 3))
  # adjusted: kelompok umur, JK, desa (desa jarang digabung ke 'Lainnya')
  dd$desa_g <- ifelse(dd$desa %in% names(which(table(dd$desa) >= 20)), dd$desa, "Lainnya")
  or_a <- tryCatch({ m <- glm(as.formula(paste(out, "~", dx, "+ kelompok_umur + jk + desa_g")), data = dd, family = binomial)
                     exp(c(coef(m)[dx], suppressMessages(confint.default(m))[dx, ])) }, error = function(e) rep(NA, 3))
  data.frame(outcome = out, diagnosis = dx, n = nrow(dd),
             n_dx = sum(t[2, ]), kasus_pada_dx = t[2, 2], persen_pada_dx = round(100 * t[2, 2] / sum(t[2, ]), 1),
             persen_tanpa_dx = round(100 * t[1, 2] / sum(t[1, ]), 1), uji = uji_nm, p = signif(p, 3),
             OR_kasar = round(or_c[1], 2), OR_kasar_IK95 = sprintf("%.2f-%.2f", or_c[2], or_c[3]),
             OR_adj = round(or_a[1], 2), OR_adj_IK95 = sprintf("%.2f-%.2f", or_a[2], or_a[3]))
}
jalankan <- function(d) do.call(rbind, lapply(c("stunting", "underweight", "wasting"),
                                             function(o) do.call(rbind, lapply(dxs, function(x) uji(d, o, x)))))
hasil <- jalankan(anak)
hasil_sens <- jalankan(anak[anak$perlu_cek_antropometri == 0, ])

frek_dx <- data.frame(kelompok = dxs, n_anak = sapply(dxs, function(x) sum(anak[[x]], na.rm = TRUE)),
                      persen = round(100 * sapply(dxs, function(x) mean(anak[[x]], na.rm = TRUE)), 1))

# Proporsi utama sesudah membuang anak yang perlu cek antropometri
bersih <- anak[anak$perlu_cek_antropometri == 0, ]
banding <- do.call(rbind, lapply(c("stunting", "underweight", "wasting"), function(o) data.frame(
  indikator = o,
  persen_semua = round(100 * mean(anak[[o]], na.rm = TRUE), 1), n_semua = sum(!is.na(anak[[o]])),
  persen_tanpa_perlu_cek = round(100 * mean(bersih[[o]], na.rm = TRUE), 1), n_tanpa_perlu_cek = sum(!is.na(bersih[[o]])))))

catatan <- data.frame(catatan = c(
  "Inkonsistensi longitudinal (semua kunjungan dari Data_Bersih): PB turun >2 cm; PB naik >4 cm/bulan pada umur >6 bln (selang >=14 hari); BB berubah >25% dalam <=60 hari.",
  "perlu_cek_antropometri = inkonsisten longitudinal ATAU z-score implausible (flag WHO).",
  "Kelompok diagnosis dari teks kolom diagnosa + kode_diagnosa (regex), multi-label; anak tanpa diagnosa = NA.",
  "Uji: Chi-square (Fisher bila ada expected <5). OR_adj: regresi logistik disesuaikan kelompok umur, JK, desa (desa n<20 digabung).",
  "Hubungan_Sensitivitas = analisis yang sama tanpa anak perlu_cek_antropometri.",
  "Desain potong lintang: asosiasi, bukan sebab-akibat. Banyak uji -> waspadai temuan kebetulan (p<0,05 tunggal)."))

wb <- createWorkbook()
sh <- list(Ringkasan_Sensitivitas = banding, Inkonsisten_Antar_Kunjungan = inkons, Frekuensi_Diagnosis = frek_dx,
           Hubungan_Gizi_Diagnosis = hasil, Hubungan_Sensitivitas = hasil_sens, Analisis_Per_Anak = anak, Catatan = catatan)
for (nm in names(sh)) { addWorksheet(wb, nm); writeData(wb, nm, sh[[nm]]) }
saveWorkbook(wb, a[3], overwrite = TRUE)

cat("Inkonsisten: baris", nrow(inkons), "anak", length(unique(inkons$id_pasien)), "| perlu cek (anak):", sum(anak$perlu_cek_antropometri), "\n")
print(banding, row.names = FALSE); print(frek_dx, row.names = FALSE)
print(hasil[, c("outcome", "diagnosis", "n_dx", "persen_pada_dx", "persen_tanpa_dx", "p", "OR_adj", "OR_adj_IK95")], row.names = FALSE)
print(hasil_sens[hasil_sens$p < 0.1, c("outcome", "diagnosis", "n_dx", "persen_pada_dx", "persen_tanpa_dx", "p", "OR_adj", "OR_adj_IK95")], row.names = FALSE)
