# Kelengkapan data antropometri, perbandingan anak dengan/tanpa PB, dan SD/median z-score (cek kualitas WHO).
# Usage: Rscript kelengkapan_mtbs.R <xlsx data bersih> <xlsx analisis lanjut> <xlsx output>
suppressMessages({ library(readxl); library(openxlsx) })
set.seed(2026)
a <- commandArgs(TRUE)
d <- as.data.frame(read_excel(a[1], sheet = "Data_Bersih"))
anak <- as.data.frame(read_excel(a[2], sheet = "Analisis_Per_Anak"))
d$tahun <- format(as.Date(d$tgl_kunjungan), "%Y")
isi <- function(x) !is.na(x) & trimws(as.character(x)) != ""

# Kelengkapan per kunjungan, per tahun kunjungan dan per desa
kel <- function(g) { s <- split(d, g); do.call(rbind, lapply(names(s), function(k) { x <- s[[k]]
  data.frame(kelompok = k, kunjungan = nrow(x), BB = round(100 * mean(isi(x$bb_kg)), 1), PB = round(100 * mean(isi(x$pb_cm)), 1),
             JK = round(100 * mean(isi(x$jk)), 1), tgl_lahir = round(100 * mean(isi(x$tgl_lahir)), 1),
             umur_tepat = round(100 * mean(grepl("^tepat", x$presisi_umur)), 1)) })) }
# Total dan per desa: periode analisis 2025-2026; per tahun tetap menampilkan 2024 sebagai pembanding
d_all <- d
d$semua <- "Semua"
kel_tahun <- kel(ifelse(is.na(d$tahun), "Tidak terbaca", d$tahun))
d <- d[d$tahun %in% c("2025", "2026"), ]
kelengkapan <- rbind(cbind(dimensi = "Total", kel(d$semua)), cbind(dimensi = "Tahun kunjungan", kel_tahun),
                     cbind(dimensi = "Desa", kel(ifelse(is.na(d$desa), "(kosong)", d$desa))))

# Per anak (balita 0-60 bln dengan id): pernah punya PB valid vs tidak
b <- d[!is.na(d$id_pasien) & !is.na(d$umur_bulan) & d$umur_bulan <= 60, ]
b <- b[order(b$id_pasien, as.Date(b$tgl_kunjungan)), ]
ada_pb <- tapply(isi(b$pb_cm), b$id_pasien, any)
p1 <- b[!duplicated(b$id_pasien), ]; p1$ada_PB <- ifelse(ada_pb[as.character(p1$id_pasien)], "PB tercatat", "PB tidak tercatat")
p1$kelompok_umur <- as.character(cut(p1$umur_bulan, c(-Inf, 6, 12, 24, 36, 48, Inf), right = FALSE,
                      labels = c("0-5 bln", "6-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-60 bln")))
p1$tahun_data <- ifelse(grepl("2026", p1$sheet_sumber), "2026", "2025")
banding <- function(v) { x <- p1[!is.na(p1[[v]]) & isi(p1[[v]]), ]; t <- table(x[[v]], x$ada_PB)
  e <- suppressWarnings(chisq.test(t)); p <- if (any(e$expected < 5)) fisher.test(t, simulate.p.value = TRUE, B = 1e4)$p.value else e$p.value
  data.frame(variabel = v, kategori = rownames(t),
             PB_tercatat = sprintf("%d (%.1f)", t[, "PB tercatat"], 100 * t[, "PB tercatat"] / sum(t[, "PB tercatat"])),
             PB_tidak_tercatat = sprintf("%d (%.1f)", t[, "PB tidak tercatat"], 100 * t[, "PB tidak tercatat"] / sum(t[, "PB tidak tercatat"])),
             p = c(signif(p, 3), rep(NA, nrow(t) - 1))) }
umur_cmp <- data.frame(variabel = "umur_bulan (median, IQR)", kategori = "",
  PB_tercatat = with(p1[p1$ada_PB == "PB tercatat", ], sprintf("%.1f (%.1f-%.1f)", median(umur_bulan), quantile(umur_bulan, .25), quantile(umur_bulan, .75))),
  PB_tidak_tercatat = with(p1[p1$ada_PB != "PB tercatat", ], sprintf("%.1f (%.1f-%.1f)", median(umur_bulan), quantile(umur_bulan, .25), quantile(umur_bulan, .75))),
  p = signif(wilcox.test(umur_bulan ~ ada_PB, data = p1)$p.value, 3))
perbandingan_pb <- rbind(data.frame(variabel = "n anak", kategori = "", PB_tercatat = as.character(sum(p1$ada_PB == "PB tercatat")),
                                    PB_tidak_tercatat = as.character(sum(p1$ada_PB != "PB tercatat")), p = NA),
                         umur_cmp, banding("kelompok_umur"), banding("jk"), banding("desa"), banding("tahun_data"))

# SD dan median z-score (WHO: SD diharapkan ~1; >1,3 menandakan masalah kualitas data)
zq <- do.call(rbind, lapply(list(c("TB/U", "zTBU", "flag_zTBU"), c("BB/U", "zBBU", "flag_zBBU"), c("BB/TB", "zBBTB", "flag_zBBTB")), function(v) {
  z <- anak[[v[2]]][!(anak[[v[3]]] %in% 1) & !is.na(anak[[v[2]]])]
  z2 <- anak[[v[2]]][!(anak[[v[3]]] %in% 1) & !is.na(anak[[v[2]]]) & anak$perlu_cek_antropometri == 0]
  data.frame(indeks = v[1], n = length(z), rerata = round(mean(z), 2), median = round(median(z), 2), SD = round(sd(z), 2),
             SD_tanpa_perlu_cek = round(sd(z2), 2), n_flag_implausible = sum(anak[[v[3]]] %in% 1)) }))

# Alur data
tahun_per_anak <- table(format(as.Date(anak$tgl_kunjungan), "%Y"))
alur <- data.frame(langkah = c("Baris register mentah (2 sheet)", "Balita unik (ID)", "Kunjungan layak analisis", "Balita layak analisis (unit)",
                               paste("Anak dengan kunjungan pertama tahun", names(tahun_per_anak))),
                   n = c(nrow(d_all), length(unique(d_all$id_pasien[!is.na(d_all$id_pasien)])), NA, nrow(anak), as.integer(tahun_per_anak)))
rentang <- range(as.Date(d_all$tgl_kunjungan), na.rm = TRUE)

wb <- createWorkbook()
for (nm in c("Kelengkapan", "Perbandingan_PB", "Kualitas_Zscore", "Alur")) addWorksheet(wb, nm)
writeData(wb, "Kelengkapan", kelengkapan); writeData(wb, "Perbandingan_PB", perbandingan_pb)
writeData(wb, "Kualitas_Zscore", zq); writeData(wb, "Alur", alur)
writeData(wb, "Alur", paste("Rentang tanggal kunjungan:", rentang[1], "s.d.", rentang[2]), startRow = nrow(alur) + 3)
saveWorkbook(wb, a[3], overwrite = TRUE)
print(kelengkapan, row.names = FALSE); print(perbandingan_pb, row.names = FALSE); print(zq, row.names = FALSE); print(alur, row.names = FALSE); print(rentang)
cat("Anak 0-60 bln dengan id:", nrow(p1), "\n")
