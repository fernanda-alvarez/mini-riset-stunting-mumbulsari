# Analisis 1, 2, 5 (tabel prevalensi menurut umur & JK), 6 dan 7 di R. Padanan analisis_tahap2.py (a1, a2, a5) dan analisis_tahap2b.py (a6, a7).
# Pakai: Rscript skrip/analisis_r_1.R <anak_analisis.csv> <folder keluaran>
# Uji chi-kuadrat (a3, a5) dan cakupan (a4) ada di skrip/spss/analisis_spss.sps.
args <- commandArgs(trailingOnly = TRUE)
dir_skrip <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
source(file.path(dir_skrip, "r_umum.R"))
dir.create(args[2], showWarnings = FALSE, recursive = TRUE)
set.seed(SEED)
d <- baca_anak(args[1])
sk <- skenario(d)

# ---------- A1: prevalensi ----------
a1 <- function() {
  dt <- list(); bl <- list()
  for (nm in names(sk)) {
    x <- d[sk[[nm]], ]
    for (ds in names(gu <- grup_desa(x))) {
      y <- gu[[ds]]
      for (th in sort(unique(y$tahun))) {
        z <- y[y$tahun == th, ]
        for (o in OUTCOME) dt[[length(dt) + 1]] <- cbind(skenario = nm, desa = ds, tahun = th, outcome = o, prev_boot(z, o))
      }
    }
    for (b in sort(unique(x$bulan_berkas))) {
      z <- x[x$bulan_berkas == b, ]
      for (o in OUTCOME) {
        v <- z[[o]][!is.na(z[[o]])]
        w <- wilson(sum(v), length(v))
        bl[[length(bl) + 1]] <- data.frame(skenario = nm, bulan = b, outcome = o, n_valid = length(v), kasus = as.integer(sum(v)),
                                           pct = round(100 * mean(v), 2), ci_low = round(w[1], 2), ci_high = round(w[2], 2))
      }
    }
  }
  list(do.call(rbind, dt), do.call(rbind, bl))
}

# ---------- A2: tren ----------
seri <- function() {
  r <- list()
  for (nm in names(sk)) for (ds in names(gu <- grup_desa(d[sk[[nm]], ]))) {
    y <- gu[[ds]]
    for (b in sort(unique(y$bulan_berkas))) {
      z <- y[y$bulan_berkas == b, ]
      for (o in UTAMA) {
        v <- z[[o]][!is.na(z[[o]])]
        r[[length(r) + 1]] <- data.frame(skenario = nm, desa = ds, bulan = b, t = IDX[[b]], outcome = o, n_valid = length(v), pct = 100 * (sum(v) / length(v)))  # bukan 100*mean(v): mean() R memakai long double sehingga ikatan nilai (untuk Kendall) bisa terpecah
      }
    }
  }
  do.call(rbind, r)
}

nw_ols <- function(X, y, lag = 3) {
  beta <- solve(crossprod(X), crossprod(X, y))[, 1]
  e <- y - X %*% beta
  xe <- X * as.numeric(e)
  S <- crossprod(xe)
  n <- nrow(xe)
  for (L in 1:lag) {
    G <- crossprod(xe[(L + 1):n, , drop = FALSE], xe[1:(n - L), , drop = FALSE])
    S <- S + (1 - L / (lag + 1)) * (G + t(G))
  }
  bread <- solve(crossprod(X))
  se <- sqrt(diag(bread %*% S %*% bread))
  df <- n - ncol(X)
  list(beta = beta, se = se, p = 2 * (1 - pt(abs(beta / se), df)))
}

# Theil-Sen dengan CI seperti scipy.stats.theilslopes (Sen 1968, persamaan 2.6)
theil_sen <- function(y, x) {
  n <- length(y)
  ij <- which(upper.tri(matrix(0, n, n)), arr.ind = TRUE)
  dx <- x[ij[, 2]] - x[ij[, 1]]
  dy <- y[ij[, 2]] - y[ij[, 1]]
  s <- sort(dy[dx > 0] / dx[dx > 0])
  nt <- length(s)
  ulang_y <- as.numeric(table(y)); ulang_y <- ulang_y[ulang_y > 1]
  ulang_x <- as.numeric(table(x)); ulang_x <- ulang_x[ulang_x > 1]
  sigsq <- (n * (n - 1) * (2 * n + 5) - sum(ulang_x * (ulang_x - 1) * (2 * ulang_x + 5)) - sum(ulang_y * (ulang_y - 1) * (2 * ulang_y + 5))) / 18
  sg <- sqrt(sigsq)
  ru <- min(round((nt + 1.96 * sg) / 2), nt - 1)
  rl <- max(round((nt - 1.96 * sg) / 2) - 1, 0)
  c(median(s), s[rl + 1], s[ru + 1])
}

a2 <- function(s) {
  tren <- list(); seg <- list()
  kunci <- unique(s[, c("skenario", "desa", "outcome")])
  kunci <- kunci[order(kunci$skenario, kunci$desa, kunci$outcome), ]
  for (i in seq_len(nrow(kunci))) {
    k <- kunci[i, ]
    g <- s[s$skenario == k$skenario & s$desa == k$desa & s$outcome == k$outcome, ]
    g <- g[order(g$t), ]
    if (nrow(g) < 12) next
    kt <- suppressWarnings(cor.test(g$t, g$pct, method = "kendall"))
    ts <- theil_sen(g$pct, g$t)
    tren[[length(tren) + 1]] <- data.frame(skenario = k$skenario, desa = k$desa, outcome = k$outcome, n_bulan = nrow(g),
      tau = round(unname(kt$estimate), 3), p_mk = round(kt$p.value, 4), sen_pp_per_bulan = round(ts[1], 3),
      sen_ci_low = round(ts[2], 3), sen_ci_high = round(ts[3], 3), sen_pp_per_tahun = round(12 * ts[1], 2))
    post <- as.numeric(g$t >= POST0)
    if (sum(post) >= 6 && sum(1 - post) >= 6) {
      tt <- as.numeric(g$t)
      X <- cbind(1, tt, post, (tt - POST0) * post)
      f <- nw_ols(X, g$pct)
      nmp <- c("level_awal", "slope_pra_pp_per_bulan", "lompatan_2026-01_pp", "perubahan_slope_pp_per_bulan")
      for (j in 1:4) seg[[length(seg) + 1]] <- data.frame(skenario = k$skenario, desa = k$desa, outcome = k$outcome, n_bulan = nrow(g),
        parameter = nmp[j], est = round(f$beta[j], 3), se_nw = round(f$se[j], 3), p = round(f$p[j], 4))
    }
  }
  list(do.call(rbind, tren), do.call(rbind, seg))
}

# ---------- A5: prevalensi menurut tahun, JK, kelompok umur ----------
a5_tabel <- function() {
  r <- list()
  for (nm in c("S0", "S1")) {
    x <- d[sk[[nm]], ]
    for (th in sort(unique(x$tahun))) for (jk in sort(unique(x$jk[!is.na(x$jk)]))) for (ku in UMUR_LABEL) {
      z <- x[x$tahun == th & !is.na(x$jk) & x$jk == jk & !is.na(x$kel_umur) & x$kel_umur == ku, ]
      if (nrow(z) == 0) next
      for (o in UTAMA) r[[length(r) + 1]] <- cbind(skenario = nm, tahun = th, jk = jk, kel_umur = ku, outcome = o, prev_boot(z, o))
    }
  }
  do.call(rbind, r)
}

# ---------- A6: distribusi z-score ----------
a6 <- function() {
  ring <- list(); hist_ <- list(); bulanan <- list()
  bins <- seq(-6, 6, by = 0.25)
  for (nm in c("S0", "S3")) {
    x <- d[sk[[nm]], ]
    gx <- grup_desa(x)
    for (ds in names(gx)) {
      y <- gx[[ds]]
      for (th in sort(unique(y$tahun))) {
        z <- y[y$tahun == th, ]
        for (zc in names(ZSKOR)) {
          v <- zvalid(z, zc)
          if (nrow(v) < 30) next
          s <- v[[zc]]
          bm <- boot_mean(v, zc)
          m <- mean(s); sdv <- sd(s)
          r <- data.frame(skenario = nm, desa = ds, tahun = th, zscore = zc, n_anak = bm$n_anak, n = bm$n, mean = bm$mean,
            ci_low = bm$ci_low, ci_high = bm$ci_high, sd = round(sdv, 3),
            skew = round({ n <- length(s); (sqrt(n * (n - 1)) / (n - 2)) * (sum((s - m)^3) / n) / (sum((s - m)^2) / n)^1.5 }, 3),
            p5 = round(quantile(s, .05, names = FALSE), 2), p25 = round(quantile(s, .25, names = FALSE), 2), median = round(median(s), 2),
            p75 = round(quantile(s, .75, names = FALSE), 2), p95 = round(quantile(s, .95, names = FALSE), 2),
            pct_di_bawah_min2 = round(100 * mean(s < -2), 2))
          if (zc == "zs_tbu") {
            atas <- sum(s >= -2.0 & s < -1.9); bawah <- sum(s >= -2.1 & s < -2.0)
            r$n_min2_0_min1_9 <- atas; r$n_min2_1_min2_0 <- bawah; r$rasio_tumpuk <- if (bawah) round(atas / bawah, 2) else NA
          }
          ring[[length(ring) + 1]] <- r
          if (nm == "S0" && zc == "zs_tbu") {
            cnt <- tabulate(findInterval(pmin(pmax(s, -5.99), 5.99), bins, rightmost.closed = TRUE), nbins = length(bins) - 1)
            hist_[[length(hist_) + 1]] <- data.frame(desa = ds, tahun = th, bin_awal = round(bins[-length(bins)], 2), n = cnt)
          }
        }
      }
    }
    if (nm == "S0") for (ds in names(gx)) {
      y <- gx[[ds]]
      for (b in sort(unique(y$bulan_berkas))) for (zc in names(ZSKOR)) {
        v <- zvalid(y[y$bulan_berkas == b, ], zc)[[zc]]
        if (length(v) >= 30) bulanan[[length(bulanan) + 1]] <- data.frame(desa = ds, bulan = b, zscore = zc, n = length(v), mean = round(mean(v), 3), sd = round(sd(v), 3))
      }
    }
  }
  list(plyr_bind(ring), do.call(rbind, hist_), do.call(rbind, bulanan))
}

# rbind yang mengisi kolom kosong dengan NA (kolom rasio hanya ada untuk zs_tbu)
plyr_bind <- function(l) {
  kol <- unique(unlist(lapply(l, names)))
  do.call(rbind, lapply(l, function(r) { for (k in setdiff(kol, names(r))) r[[k]] <- NA; r[kol] }))
}

# ---------- A7: kurva umur ----------
a7 <- function() {
  d$umur3 <- pmin(pmax(floor(d$umur_bln / 3) * 3, 0), 57)
  r <- list()
  for (nm in c("S0", "S3")) {
    x <- d[sk[[nm]], ]
    for (th in sort(unique(x$tahun))) for (u3 in sort(unique(x$umur3[x$tahun == th]))) {
      z <- x[x$tahun == th & x$umur3 == u3, ]
      row <- data.frame(skenario = nm, tahun = th, umur_awal_bln = as.integer(u3), n = nrow(z))
      for (zc in names(ZSKOR)) {
        b <- boot_mean(zvalid(z, zc), zc)
        row[[paste0(zc, "_mean")]] <- b$mean; row[[paste0(zc, "_lo")]] <- b$ci_low; row[[paste0(zc, "_hi")]] <- b$ci_high
      }
      for (o in UTAMA) {
        b <- boot_mean(z, o)
        row[[paste0(o, "_pct")]] <- round(100 * b$mean, 2); row[[paste0(o, "_lo")]] <- round(100 * b$ci_low, 2); row[[paste0(o, "_hi")]] <- round(100 * b$ci_high, 2)
      }
      r[[length(r) + 1]] <- row
    }
  }
  do.call(rbind, r)
}

hasil <- a1(); tulis(hasil[[1]], args[2], "a1_prevalensi_desa_tahun"); tulis(hasil[[2]], args[2], "a1_prevalensi_bulan")
s <- seri(); tulis(s, args[2], "a2_seri_bulanan")
h2 <- a2(s); tulis(h2[[1]], args[2], "a2_tren_mannkendall"); tulis(h2[[2]], args[2], "a2_tren_segmented")
tulis(a5_tabel(), args[2], "a5_umur_jk")
h6 <- a6(); tulis(h6[[1]], args[2], "a6_zscore_ringkas"); tulis(h6[[2]], args[2], "a6_zscore_histogram_tbu_s0"); tulis(h6[[3]], args[2], "a6_zscore_bulanan_s0")
tulis(a7(), args[2], "a7_kurva_umur")
