# Bandingkan tabel hasil Python (data/sigizi/analisis/tabel) dengan tabel R/SPSS pada folder lain.
# Pakai: Rscript skrip/bandingkan_hasil.R <folder python> <folder lain> [daftar tabel dipisah koma]
# Kolom "tetap" harus sama (selisih hanya pembulatan); kolom "acak" (batas CI bootstrap, simulasi) boleh berbeda sedikit karena RNG.
args <- commandArgs(trailingOnly = TRUE)
SPEK <- list(
  a1_prevalensi_desa_tahun = list(k = c("skenario", "desa", "tahun", "outcome"), tetap = c("n_anak", "n_valid", "kasus", "pct"), acak = c("ci_low", "ci_high")),
  a1_prevalensi_bulan = list(k = c("skenario", "bulan", "outcome"), tetap = c("n_valid", "kasus", "pct", "ci_low", "ci_high"), acak = character()),
  a2_seri_bulanan = list(k = c("skenario", "desa", "bulan", "outcome"), tetap = c("t", "n_valid", "pct"), acak = character()),
  a2_tren_mannkendall = list(k = c("skenario", "desa", "outcome"), tetap = c("n_bulan", "tau", "p_mk", "sen_pp_per_bulan", "sen_ci_low", "sen_ci_high", "sen_pp_per_tahun"), acak = character()),
  a2_tren_segmented = list(k = c("skenario", "desa", "outcome", "parameter"), tetap = c("n_bulan", "est", "se_nw", "p"), acak = character()),
  a3_antar_desa = list(k = c("skenario", "tahun", "outcome", "desa"), tetap = c("n_anak", "kasus", "pct", "ci_low", "ci_high", "resid_std", "chi2", "df", "p_chi2"), acak = character()),
  a4_cakupan_desa_bulan = list(k = c("desa", "bulan_berkas"), tetap = c("terukur", "sasaran", "cakupan_pct"), acak = character()),
  a4_cakupan_bulan = list(k = c("bulan_berkas"), tetap = c("terukur", "sasaran", "cakupan_pct"), acak = character()),
  a5_umur_jk = list(k = c("skenario", "tahun", "jk", "kel_umur", "outcome"), tetap = c("n_anak", "n_valid", "kasus", "pct"), acak = c("ci_low", "ci_high")),
  a5_uji_jk_umur = list(k = c("skenario", "tahun", "outcome", "faktor"), tetap = c("n_anak", "chi2", "df", "p_chi2"), acak = character()),
  a6_zscore_ringkas = list(k = c("skenario", "desa", "tahun", "zscore"), tetap = c("n_anak", "n", "mean", "sd", "skew", "p5", "p25", "median", "p75", "p95", "pct_di_bawah_min2", "n_min2_0_min1_9", "n_min2_1_min2_0", "rasio_tumpuk"), acak = c("ci_low", "ci_high")),
  a6_zscore_histogram_tbu_s0 = list(k = c("desa", "tahun", "bin_awal"), tetap = c("n"), acak = character()),
  a6_zscore_bulanan_s0 = list(k = c("desa", "bulan", "zscore"), tetap = c("n", "mean", "sd"), acak = character()),
  a7_kurva_umur = list(k = c("skenario", "tahun", "umur_awal_bln"), tetap = c("n", "zs_tbu_mean", "zs_bbu_mean", "zs_bbtb_mean", "stunting_pct", "wasting_pct", "underweight_pct"),
                       acak = c("zs_tbu_lo", "zs_tbu_hi", "zs_bbu_lo", "zs_bbu_hi", "zs_bbtb_lo", "zs_bbtb_hi", "stunting_lo", "stunting_hi", "wasting_lo", "wasting_hi", "underweight_lo", "underweight_hi")),
  a8_faktor_risiko = list(k = c("skenario", "outcome", "model", "term"), tetap = c("OR", "ci_low", "ci_high", "p", "n_obs", "n_anak", "n_kasus"), acak = character()),
  a9_transisi_status = list(k = c("skenario", "desa", "tahun", "outcome", "ukuran"), tetap = c("n_pasangan", "n_anak", "pct"), acak = c("ci_low", "ci_high")),
  a9_kecepatan_tumbuh = list(k = c("desa", "tahun", "kel_umur"), tetap = c("n_pasangan", "mean_cm", "sd_cm", "pct_turun_ge1cm", "pct_naik_ge5cm"), acak = character()),
  a9_km_stunting = list(k = c("skenario", "faktor", "nilai", "waktu_bln"), tetap = c("n_anak", "n_kejadian", "n_berisiko", "kejadian", "S", "ci_low", "ci_high"), acak = character()),
  a9_logrank = list(k = c("skenario", "faktor"), tetap = c("n_anak", "n_kejadian", "chi2", "p"), acak = character()),
  p1_km_konfirmasi = list(k = c("skenario", "definisi", "faktor", "nilai"), tetap = c("n_anak", "n_kejadian", "S_12bln_sejak_masuk", "S_24bln_sejak_masuk", "S_umur24", "S_umur36", "n_umur_tak_valid"), acak = character()),
  p1_logrank = list(k = c("skenario", "definisi", "faktor", "grup1", "skala", "strata"), tetap = c("n_anak", "n_kejadian", "chi2", "p", "O_grup1", "E_grup1"), acak = character()),
  p2_bulan_terukur = list(k = c("data"), tetap = c("n_anak", "pct_ge12", "pct_ge24", "median", "p25", "p75", "maks"), acak = character()),
  p3_tumpuk_digit = list(k = c("tahun", "kelompok"), tetap = c("n", "n_atas", "n_bawah", "rasio_tumpuk", "pct_di_bawah_min2"), acak = character()),
  p3_simulasi_pembulatan = list(k = c("cara", "tahun"), tetap = character(), acak = c("rasio_rerata", "rasio_min", "rasio_maks", "pct_di_bawah_min2")),
  p3_validasi_lms = list(k = c("validasi"), tetap = c("median_selisih", "pct_selisih_le_0_1"), acak = character())
)
tabel <- if (length(args) >= 3) strsplit(args[3], ",")[[1]] else names(SPEK)
for (nm in tabel) {
  f1 <- file.path(args[1], paste0(nm, ".csv")); f2 <- file.path(args[2], paste0(nm, ".csv"))
  if (!file.exists(f1) || !file.exists(f2)) { cat(sprintf("%-28s berkas tidak ada (%s / %s)\n", nm, file.exists(f1), file.exists(f2))); next }
  sp <- SPEK[[nm]]
  a <- read.csv(f1, stringsAsFactors = FALSE, colClasses = "character", fileEncoding = "UTF-8-BOM"); b <- read.csv(f2, stringsAsFactors = FALSE, colClasses = "character", fileEncoding = "UTF-8-BOM")
  norm <- function(v) { v <- trimws(v); v[v %in% c("", "NA", "NaN")] <- NA; v }
  a[] <- lapply(a, norm); b[] <- lapply(b, norm)
  # kunci angka "0.0" dan "0" disamakan
  kk <- function(df) apply(df[, sp$k, drop = FALSE], 1, function(r) paste(ifelse(is.na(r), "NA", ifelse(grepl("^-?[0-9.]+$", r), format(as.numeric(r), trim = TRUE, nsmall = 0, digits = 10), r)), collapse = "|"))
  a$.k <- kk(a); b$.k <- kk(b)
  m <- merge(a, b, by = ".k", suffixes = c(".py", ".o"))
  cat(sprintf("%-28s py=%d lain=%d cocok=%d\n", nm, nrow(a), nrow(b), nrow(m)))
  for (jenis in c("tetap", "acak")) for (cl in sp[[jenis]]) {
    if (!all(paste0(cl, c(".py", ".o")) %in% names(m))) { cat(sprintf("    %-22s (kolom tidak ada di salah satu berkas)\n", cl)); next }
    x <- suppressWarnings(as.numeric(m[[paste0(cl, ".py")]])); y <- suppressWarnings(as.numeric(m[[paste0(cl, ".o")]]))
    ok <- !(is.na(x) & is.na(y))
    beda_na <- sum(is.na(x) != is.na(y))
    s <- abs(x - y)
    cat(sprintf("    %-5s %-22s maks selisih = %-10.5g rerata = %-10.5g NA-berbeda = %d\n", jenis, cl, max(s, na.rm = TRUE), mean(s, na.rm = TRUE), beda_na))
  }
}
