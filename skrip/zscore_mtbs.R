# Hitung z-score WHO 2006 (paket resmi WHO 'anthro') + tabel deskriptif.
# Usage: Rscript zscore_mtbs.R <xlsx siap olah> <xlsx output>
suppressMessages({ library(anthro); library(readxl); library(openxlsx) })
a <- commandArgs(TRUE); src <- a[1]; out <- a[2]

hitung <- function(d) {
  tl <- as.Date(d$tgl_lahir); tk <- as.Date(d$tgl_kunjungan)
  hari <- as.numeric(tk - tl)
  # umur dari tanggal bila ada & konsisten, selain itu dari umur_bulan
  pakai_hari <- !is.na(hari) & abs(hari / 30.4375 - d$umur_bulan) < 1
  umur_hari <- ifelse(pakai_hari, hari, round(d$umur_bulan * 30.4375))
  sex <- ifelse(toupper(substr(d$jk, 1, 1)) == "L", 1, ifelse(toupper(substr(d$jk, 1, 1)) == "P", 2, NA))
  z <- anthro_zscores(sex = sex, age = umur_hari, is_age_in_month = FALSE,
                      weight = d$bb_kg, lenhei = d$pb_cm)
  d$umur_hari_dipakai <- umur_hari
  d$zTBU <- z$zlen;  d$flag_zTBU <- z$flen
  d$zBBU <- z$zwei;  d$flag_zBBU <- z$fwei
  d$zBBTB <- z$zwfl; d$flag_zBBTB <- z$fwfl
  # kategori PMK 2/2020; z yang ditandai implausible (flag=1) tidak dikategorikan
  k <- function(z, f, br, lb) ifelse(is.na(z) | f %in% 1, NA, as.character(cut(z, br, lb, right = FALSE)))
  d$status_TBU <- k(d$zTBU, d$flag_zTBU, c(-Inf, -3, -2, 3.0000001, Inf),
                    c("Sangat pendek", "Pendek", "Normal", "Tinggi"))
  d$status_BBU <- k(d$zBBU, d$flag_zBBU, c(-Inf, -3, -2, 1.0000001, Inf),
                    c("BB sangat kurang", "BB kurang", "BB normal", "Risiko BB lebih"))
  d$status_BBTB <- k(d$zBBTB, d$flag_zBBTB, c(-Inf, -3, -2, 1.0000001, 2.0000001, 3.0000001, Inf),
                     c("Gizi buruk", "Gizi kurang", "Gizi baik", "Berisiko gizi lebih", "Gizi lebih", "Obesitas"))
  d$stunting <- ifelse(is.na(d$status_TBU), NA, as.integer(d$status_TBU %in% c("Sangat pendek", "Pendek")))
  d$underweight <- ifelse(is.na(d$status_BBU), NA, as.integer(d$status_BBU %in% c("BB sangat kurang", "BB kurang")))
  d$wasting <- ifelse(is.na(d$status_BBTB), NA, as.integer(d$status_BBTB %in% c("Gizi buruk", "Gizi kurang")))
  d$kelompok_umur <- as.character(cut(d$umur_bulan, c(-Inf, 6, 12, 24, 36, 48, Inf), right = FALSE,
                      labels = c("0-5 bln", "6-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-60 bln")))
  d$tahun_data <- ifelse(grepl("2026", d$sheet_sumber), "2026", "2025")
  d
}

wilson <- function(x, n) {
  if (n == 0) return(c(NA, NA, NA))
  p <- x / n; z <- 1.959964; den <- 1 + z^2 / n
  c(p, (p + z^2 / (2 * n) - z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2))) / den,
       (p + z^2 / (2 * n) + z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2))) / den) * 100
}

proporsi <- function(d, by) {
  g <- if (is.null(by)) rep("Total", nrow(d)) else ifelse(is.na(d[[by]]), "(kosong)", as.character(d[[by]]))
  rows <- list()
  for (lv in sort(unique(g))) for (ind in c("stunting", "underweight", "wasting")) {
    v <- d[[ind]][g == lv]; v <- v[!is.na(v)]
    ci <- wilson(sum(v), length(v))
    rows[[length(rows) + 1]] <- data.frame(variabel = ifelse(is.null(by), "Total", by), kategori = lv,
      indikator = ind, n = length(v), kasus = sum(v), persen = round(ci[1], 1),
      IK95_bawah = round(ci[2], 1), IK95_atas = round(ci[3], 1))
  }
  do.call(rbind, rows)
}

kunj <- as.data.frame(read_excel(src, sheet = "Semua_Kunjungan_Layak"))
kunj <- hitung(kunj)
# kunjungan tanpa id_pasien tidak bisa dipastikan anaknya -> tidak masuk unit per-anak
anak <- kunj[which(kunj$kunjungan_ke_anak == 1), ]

desk <- do.call(rbind, lapply(list(NULL, "kelompok_umur", "jk", "desa", "pembiayaan", "tahun_data"),
                              function(b) proporsi(anak, b)))
dist <- do.call(rbind, lapply(c("status_TBU", "status_BBU", "status_BBTB"), function(s) {
  t <- table(anak[[s]], useNA = "ifany")
  data.frame(indikator = s, kategori = ifelse(is.na(names(t)), "(tidak dihitung/implausible)", names(t)),
             n = as.integer(t), persen = round(100 * as.integer(t) / sum(t), 1))
}))
implaus <- anak[(anak$flag_zTBU %in% 1) | (anak$flag_zBBU %in% 1) | (anak$flag_zBBTB %in% 1),
                c("id_pasien", "nama", "sheet_sumber", "baris_excel", "tgl_lahir", "tgl_kunjungan", "umur_bulan",
                  "jk", "bb_kg", "pb_cm", "zTBU", "zBBU", "zBBTB", "flag_zTBU", "flag_zBBU", "flag_zBBTB")]
cat_ = data.frame(catatan = c(
  "Standar: WHO Child Growth Standards 2006 via paket R 'anthro' (WHO), kategori PMK No. 2/2020.",
  "Unit analisis: anak (kunjungan layak pertama). Sheet Kunjungan_Dengan_Z berisi semua kunjungan layak.",
  "Umur: selisih tgl_kunjungan - tgl_lahir bila konsisten dengan umur_bulan, selain itu umur_bulan x 30,4375.",
  "Posisi ukur (berbaring/berdiri) tidak tercatat; anthro mengasumsikan PB <24 bln dan TB >=24 bln tanpa koreksi 0,7 cm.",
  "Z implausible (flag WHO: TB/U <-6 atau >+6, BB/U <-6 atau >+5, BB/TB <-5 atau >+5) tidak dikategorikan; lihat sheet Z_Implausible.",
  "Kunjungan tanpa id_pasien (tidak bisa ditelusuri ke anak) hanya ada di Kunjungan_Dengan_Z, tidak di unit per-anak.",
  "IK 95% metode Wilson. Populasi = balita sakit yang berkunjung ke MTBS, bukan prevalensi wilayah."))

wb <- createWorkbook()
for (nm in c("Analisis_Per_Anak", "Kunjungan_Dengan_Z", "Proporsi_IK95", "Distribusi_Status", "Z_Implausible", "Catatan")) addWorksheet(wb, nm)
writeData(wb, "Analisis_Per_Anak", anak); writeData(wb, "Kunjungan_Dengan_Z", kunj)
writeData(wb, "Proporsi_IK95", desk); writeData(wb, "Distribusi_Status", dist)
writeData(wb, "Z_Implausible", implaus); writeData(wb, "Catatan", cat_)
saveWorkbook(wb, out, overwrite = TRUE)

print(desk[desk$variabel %in% c("Total", "kelompok_umur", "tahun_data"), ], row.names = FALSE)
print(dist, row.names = FALSE)
cat("Implausible anak:", nrow(implaus), " | anak:", nrow(anak), " kunjungan:", nrow(kunj), "\n")
