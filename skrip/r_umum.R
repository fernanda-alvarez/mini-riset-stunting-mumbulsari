# Fungsi bersama untuk analisis_r_*.R (padanan analisis_tahap2*.py). Dimuat dengan source().
# Masukan: anak_analisis.csv dari skrip/siapkan_data_spss_r.py (anak_bersih + penanda skenario s0..s3 + t + kel_umur).
# Bootstrap memakai RNG R, jadi batas CI berbeda sedikit dari Python (galat Monte Carlo, B = 500); angka lain deterministik.

B <- 500L
SEED <- 20261019L
OUTCOME <- c("stunting", "wasting", "underweight", "gizi_lebih")
UTAMA <- OUTCOME[1:3]
BULAN <- unlist(lapply(2024:2026, function(t) sprintf("%d-%02d", t, 1:12)))
BULAN <- BULAN[BULAN <= "2026-09"]
IDX <- setNames(seq_along(BULAN) - 1L, BULAN)
POST0 <- IDX[["2026-01"]]
UMUR_LABEL <- c("0-5 bln", "6-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-59 bln")
UMUR_BATAS <- c(0, 6, 12, 24, 36, 48, 60)
ZSKOR <- c(zs_tbu = "kat_tbu", zs_bbu = "kat_bbu", zs_bbtb = "kat_bbtb")

baca_anak <- function(path) {
  d <- read.csv(path, na.strings = c("", "NA"), stringsAsFactors = FALSE, encoding = "UTF-8")
  d$kel_umur <- factor(d$kel_umur, levels = UMUR_LABEL)
  d
}

skenario <- function(d) list(S0 = d$s0 == 1, S1 = d$s1 == 1, S2 = d$s2 == 1, S3 = d$s3 == 1)

wilson <- function(k, n) {
  if (n == 0) return(c(NA_real_, NA_real_))
  z <- 1.96; p <- k / n; pen <- 1 + z * z / n
  c_ <- (p + z * z / (2 * n)) / pen
  h <- z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / pen
  100 * c(c_ - h, c_ + h)
}

# Bootstrap klaster per anak: tiap anak diambil ulang beserta semua pengukurannya.
boot_rasio <- function(v, col) {
  v <- v[!is.na(v[[col]]), , drop = FALSE]
  if (nrow(v) == 0) return(list(n_anak = 0L, n = 0L, kasus = 0, mean = NA_real_, lo = NA_real_, hi = NA_real_))
  c_ <- as.numeric(rowsum(v[[col]], v$id_anak)[, 1])
  n_ <- as.numeric(rowsum(rep(1, nrow(v)), v$id_anak)[, 1])
  G <- length(c_)
  idx <- matrix(sample.int(G, B * G, replace = TRUE), nrow = B)
  m <- rowSums(matrix(c_[idx], nrow = B)) / rowSums(matrix(n_[idx], nrow = B))
  q <- quantile(m, c(0.025, 0.975), names = FALSE, type = 7)
  list(n_anak = G, n = as.integer(sum(n_)), kasus = sum(c_), mean = sum(c_) / sum(n_), lo = q[1], hi = q[2])
}

# Padanan prev_boot (persen, bulat 2 desimal)
prev_boot <- function(x, col) {
  b <- boot_rasio(x, col)
  data.frame(n_anak = b$n_anak, n_valid = b$n, kasus = as.integer(b$kasus), pct = round(100 * b$mean, 2),
             ci_low = round(100 * b$lo, 2), ci_high = round(100 * b$hi, 2))
}

# Padanan boot_mean (mean dibulatkan 4 desimal seperti Python)
boot_mean <- function(x, col) {
  b <- boot_rasio(x, col)
  list(n_anak = b$n_anak, n = b$n, mean = round(b$mean, 4), ci_low = round(b$lo, 4), ci_high = round(b$hi, 4))
}

grup_desa <- function(x) {
  out <- list(SEMUA = x)
  for (ds in sort(unique(x$desa[!is.na(x$desa)]))) out[[ds]] <- x[!is.na(x$desa) & x$desa == ds, , drop = FALSE]
  out
}

zvalid <- function(z, zc) {
  kc <- ZSKOR[[zc]]
  z[!is.na(z[[zc]]) & (is.na(z[[kc]]) | z[[kc]] != "Outlier") & abs(z[[zc]]) < 99, , drop = FALSE]
}

# Padanan pandas groupby().first(): nilai bukan-NA pertama menurut urutan baris
pertama_nn <- function(v, g) {
  ok <- !is.na(v)
  r <- v[ok][!duplicated(g[ok])]
  setNames(r, g[ok][!duplicated(g[ok])])
}

tulis <- function(df, folder, nama) {
  write.csv(df, file.path(folder, paste0(nama, ".csv")), row.names = FALSE, na = "", fileEncoding = "UTF-8")
  cat(nama, nrow(df), "baris\n")
}

# Pembulatan "bulat dua desimal" yang sama dengan Python (setengah ke genap) sudah dipakai R >= 4.0 (round).
rata <- function(x) if (length(x)) mean(x) else NA_real_
