# Analisis kualitas tambahan: prevalensi SD-adjusted, digit preference, BB/U sampel luas,
# sensitivitas termasuk 2024, dan diagram alur subjek.
# Usage: Rscript kualitas_tambahan_mtbs.R <data bersih> <analisis lanjut> <analisis lanjut termasuk 2024> <xlsx output> <folder grafik>
suppressMessages({ library(anthro); library(readxl); library(openxlsx); library(ggplot2) })
set.seed(2026)
a <- commandArgs(TRUE)
d <- as.data.frame(read_excel(a[1], sheet = "Data_Bersih"))
anak <- as.data.frame(read_excel(a[2], sheet = "Analisis_Per_Anak"))
anak24 <- as.data.frame(read_excel(a[3], sheet = "Analisis_Per_Anak"))
d$tahun <- as.integer(format(as.Date(d$tgl_kunjungan), "%Y"))
dp <- d[d$tahun %in% 2025:2026, ]  # periode analisis

## 1. Prevalensi SD-adjusted (WHO/UNICEF 2019; Mei & Grummer-Strawn 2007):
##    z disusutkan ke SD 1 di sekitar rerata, lalu dihitung proporsi < -2. IK 95% bootstrap.
adj <- function(z) { m <- mean(z); s <- sd(z); mean(m + (z - m) / s < -2) }
sdadj <- do.call(rbind, lapply(list(c("Stunting (TB/U)", "zTBU", "flag_zTBU"), c("BB kurang (BB/U)", "zBBU", "flag_zBBU"),
                                    c("Wasting (BB/TB)", "zBBTB", "flag_zBBTB")), function(v) {
  z <- anak[[v[2]]][!(anak[[v[3]]] %in% 1) & !is.na(anak[[v[2]]])]
  bs <- replicate(2000, adj(sample(z, replace = TRUE)))
  bo <- replicate(2000, mean(sample(z, replace = TRUE) < -2))
  data.frame(indikator = v[1], n = length(z), rerata_z = round(mean(z), 2), SD_z = round(sd(z), 2),
             persen_teramati = round(100 * mean(z < -2), 1),
             IK95_teramati = sprintf("%.1f-%.1f", 100 * quantile(bo, .025), 100 * quantile(bo, .975)),
             persen_SD_adjusted = round(100 * adj(z), 1),
             IK95_SD_adjusted = sprintf("%.1f-%.1f", 100 * quantile(bs, .025), 100 * quantile(bs, .975)),
             persen_probit = round(100 * pnorm((-2 - mean(z)) / 1), 1)) }))

## 2. Digit preference (desimal terakhir PB dan BB) - Digit Preference Score WHO Anthro:
##    DPS = 100 * sqrt(chi2 / (N * df)); 0-7 sangat baik, 8-12 baik, 13-20 cukup, >=20 bermasalah.
dps <- function(x, nama, digit_satuan = FALSE) {
  x <- x[!is.na(x)]
  dig <- if (digit_satuan) round(x) %% 10 else round((x * 10) %% 10) %% 10
  t <- table(factor(dig, 0:9)); e <- length(dig) / 10; chi <- sum((t - e)^2 / e); s <- 100 * sqrt(chi / (length(dig) * 9))
  data.frame(variabel = nama, digit_dinilai = if (digit_satuan) "angka satuan" else "angka desimal", n = length(dig),
             persen_bilangan_bulat = round(100 * mean(abs(x - round(x)) < 1e-9), 1),
             persen_digit_0 = round(100 * t[["0"]] / length(dig), 1), persen_digit_5 = round(100 * t[["5"]] / length(dig), 1),
             DPS = round(s, 1), interpretasi = as.character(cut(s, c(-Inf, 8, 13, 20, Inf), right = FALSE,
                                labels = c("Sangat baik", "Baik", "Cukup", "Bermasalah")))) }
# PB selalu ditulis dalam cm bulat, sehingga digit preference PB dinilai pada angka satuan
digit <- rbind(dps(dp$pb_cm, "Panjang/tinggi badan (cm)", digit_satuan = TRUE), dps(dp$bb_kg, "Berat badan (kg)"))
pb_akhir <- table(factor(round(dp$pb_cm[!is.na(dp$pb_cm)]) %% 10, 0:9))
digit_pb_bulat <- data.frame(angka_satuan_PB = names(pb_akhir), n = as.integer(pb_akhir),
                             persen = round(100 * as.integer(pb_akhir) / sum(pb_akhir), 1))

## 3. BB/U pada sampel luas: semua balita dengan BB, umur tepat, JK (tidak mensyaratkan PB)
b <- dp[!is.na(dp$id_pasien) & !is.na(dp$bb_kg) & !is.na(dp$umur_bulan) & dp$umur_bulan >= 0 & dp$umur_bulan <= 60 &
        !grepl("^kasar", dp$presisi_umur) & !is.na(dp$jk) & !(toupper(as.character(dp$duplikat)) %in% "TRUE") &
        !grepl("CEK", toupper(dp$flag_umur)), ]
b <- b[order(b$id_pasien, as.Date(b$tgl_kunjungan)), ]; b <- b[!duplicated(b$id_pasien), ]
hari <- as.numeric(as.Date(b$tgl_kunjungan) - as.Date(b$tgl_lahir))
umur_hari <- ifelse(!is.na(hari) & abs(hari / 30.4375 - b$umur_bulan) < 1, hari, round(b$umur_bulan * 30.4375))
zb <- anthro_zscores(sex = ifelse(b$jk == "L", 1, 2), age = umur_hari, is_age_in_month = FALSE, weight = b$bb_kg)
ok <- !(zb$fwei %in% 1) & !is.na(zb$zwei); uw <- zb$zwei[ok] < -2
ci <- binom.test(sum(uw), length(uw))$conf.int * 100
bbu_luas <- data.frame(analisis = c("BB/U, sampel utama (balita dengan PB/TB)", "BB/U, sampel luas (semua balita dengan BB)"),
  n = c(sum(!is.na(anak$underweight)), length(uw)),
  persen_BB_kurang = c(round(100 * mean(anak$underweight, na.rm = TRUE), 1), round(100 * mean(uw), 1)),
  IK95 = c(NA, sprintf("%.1f-%.1f", ci[1], ci[2])), rerata_z = c(round(mean(anak$zBBU[!(anak$flag_zBBU %in% 1)], na.rm = TRUE), 2), round(mean(zb$zwei[ok]), 2)))

## 4. Sensitivitas termasuk 2024
sens24 <- do.call(rbind, lapply(c("stunting", "underweight", "wasting"), function(o) {
  x <- anak24[[o]][!is.na(anak24[[o]])]; ci <- binom.test(sum(x), length(x))$conf.int * 100
  data.frame(indikator = o, n = length(x), persen = round(100 * mean(x), 1), IK95 = sprintf("%.1f-%.1f", ci[1], ci[2])) }))
sens24$n_balita_total <- nrow(anak24)

## 5. Diagram alur (eksklusi berurutan, tiap kunjungan dihitung pada alasan pertama)
urut <- c("kunjungan 2024 (di luar periode)", "duplikat", "umur tidak ada", "di luar 0-60 bulan", "umur perlu dicek",
          "umur kasar (tahun bulat)", "JK tidak ada", "PB tidak ada/tidak valid")
lab <- c("Kunjungan Juli–Des 2024", "Duplikat", "Umur tidak dapat ditentukan", "Umur di luar 0–60 bulan",
         "Umur perlu dicek", "Umur hanya dalam tahun bulat", "Jenis kelamin tidak tercatat", "PB/TB tidak tercatat/tidak valid")
kel <- as.data.frame(read_excel(sub("Analisis Lanjut", "Siap Olah", a[2]), sheet = "Dikeluarkan"))
pertama <- sapply(strsplit(kel$alasan_dikeluarkan, "; "), function(v) urut[min(match(v, urut))])
nk <- sapply(urut, function(u) sum(pertama == u))
layak <- as.data.frame(read_excel(sub("Analisis Lanjut", "Siap Olah", a[2]), sheet = "Semua_Kunjungan_Layak"))
n_layak <- nrow(layak); n_tanpa_id <- sum(is.na(layak$id_pasien)); n_ulang <- n_layak - n_tanpa_id - nrow(anak)
alur <- data.frame(tahap = c("Kunjungan pada register", paste("Dikeluarkan:", lab), "Kunjungan memenuhi syarat",
                             "Dikeluarkan: kunjungan ulang anak yang sama", "Dikeluarkan: tanpa nomor identitas", "Balita dianalisis"),
                   n = c(nrow(d), nk, n_layak, n_ulang, n_tanpa_id, nrow(anak)))

kotak <- function(x, y, teks, w = 5.2, h = 0.9, fill = "white", kiri = FALSE) list(
  annotate("rect", xmin = x - w / 2, xmax = x + w / 2, ymin = y - h / 2, ymax = y + h / 2, fill = fill, colour = "black", linewidth = .4),
  annotate("text", x = if (kiri) x - w / 2 + 0.2 else x, y = y, label = teks, size = 3.2, lineheight = .95, hjust = if (kiri) 0 else 0.5))
eks1 <- paste0("Dikeluarkan (n = ", format(sum(nk), big.mark = "."), " kunjungan)*:\n", paste0("• ", lab, ": ", nk, collapse = "\n"))
eks2 <- paste0("Dikeluarkan (n = ", n_ulang + n_tanpa_id, " kunjungan):\n• Kunjungan ulang anak yang sama: ", n_ulang,
               "\n• Tanpa nomor identitas: ", n_tanpa_id)
g <- ggplot() + xlim(0, 12) + ylim(0, 10) + theme_void() +
  kotak(3, 9.2, sprintf("Kunjungan pada register MTBS\n(tab 2025 dan 2026)\nn = %s kunjungan, %d balita", format(nrow(d), big.mark = "."),
                        length(unique(d$id_pasien[!is.na(d$id_pasien)]))), h = 1.2) +
  kotak(9, 6.9, eks1, w = 5.6, h = 3.0, fill = "#F7F7F7", kiri = TRUE) +
  kotak(3, 4.6, sprintf("Kunjungan memenuhi syarat\nn = %d kunjungan", n_layak)) +
  kotak(9, 3.0, eks2, w = 5.6, h = 1.2, fill = "#F7F7F7", kiri = TRUE) +
  kotak(3, 1.0, sprintf("Balita dianalisis\n(kunjungan pertama yang memenuhi syarat)\nn = %d balita", nrow(anak)), h = 1.2, fill = "#DDEBF7") +
  annotate("segment", x = 3, xend = 3, y = 8.6, yend = 5.05, arrow = arrow(length = unit(.2, "cm"))) +
  annotate("segment", x = 3, xend = 3, y = 4.15, yend = 1.6, arrow = arrow(length = unit(.2, "cm"))) +
  annotate("segment", x = 3, xend = 6.2, y = 6.9, yend = 6.9, arrow = arrow(length = unit(.2, "cm"))) +
  annotate("segment", x = 3, xend = 6.2, y = 3.0, yend = 3.0, arrow = arrow(length = unit(.2, "cm"))) +
  annotate("text", x = 0.1, y = 0.05, hjust = 0, size = 2.6, label = "* Kunjungan dengan >1 alasan dihitung pada alasan pertama sesuai urutan.")
ggsave(file.path(a[5], "G0_diagram_alur.png"), g, width = 8, height = 6.5, dpi = 200, bg = "white")

wb <- createWorkbook()
sh <- list(SD_Adjusted = sdadj, Digit_Preference = digit, Digit_Satuan_PB = digit_pb_bulat, BBU_Sampel_Luas = bbu_luas,
           Sensitivitas_Termasuk_2024 = sens24, Alur_Subjek = alur)
for (nm in names(sh)) { addWorksheet(wb, nm); writeData(wb, nm, sh[[nm]]) }
saveWorkbook(wb, a[4], overwrite = TRUE)
for (x in sh) print(x, row.names = FALSE)
