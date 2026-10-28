# Memasang paket R yang dipakai proyek ini, dengan versi yang dipakai saat analisis (R 4.6.1).
# Jalankan: Rscript install_paket_r.R
#
# Analisis utama (skrip/analisis_r_1.R sampai analisis_r_3.R, r_umum.R, bandingkan_hasil.R) hanya memakai base R
# dan tidak butuh paket tambahan. Paket di bawah dipakai oleh alur MTBS lama (zscore_mtbs.R, tabel_grafik_mtbs.R, dan lain-lain).
paket <- c(anthro = "1.1.0", openxlsx = "4.2.8.1", readxl = "1.5.0", ggplot2 = "4.0.3")

if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes")
for (nama in names(paket)) {
  terpasang <- requireNamespace(nama, quietly = TRUE) && as.character(packageVersion(nama)) == paket[[nama]]
  if (!terpasang) remotes::install_version(nama, version = paket[[nama]])
}
