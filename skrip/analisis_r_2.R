# Analisis 8 (faktor risiko) dan 9 (longitudinal) di R. Padanan analisis_tahap2b.py.
# Pakai: Rscript skrip/analisis_r_2.R <anak_analisis.csv> <folder keluaran>
args <- commandArgs(trailingOnly = TRUE)
dir_skrip <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
source(file.path(dir_skrip, "r_umum.R"))
dir.create(args[2], showWarnings = FALSE, recursive = TRUE)
set.seed(SEED)
d <- baca_anak(args[1])
sk <- skenario(d)

# ---------- A8: regresi logistik, SE robust klaster per anak (IRLS yang sama dengan Python) ----------
logit_cluster <- function(X, y, cl, iters = 40) {
  beta <- rep(0, ncol(X))
  for (i in seq_len(iters)) {
    p <- 1 / (1 + exp(-pmin(pmax(X %*% beta, -30), 30)))
    w <- as.numeric(p * (1 - p))
    H <- crossprod(X, X * w)
    step <- solve(H, crossprod(X, y - p))[, 1]
    beta <- beta + step
    if (max(abs(step)) < 1e-9) break
  }
  p <- 1 / (1 + exp(-pmin(pmax(X %*% beta, -30), 30)))
  w <- as.numeric(p * (1 - p))
  H <- crossprod(X, X * w)
  S <- rowsum(X * as.numeric(y - p), cl)
  bread <- solve(H)
  G <- nrow(S)
  V <- G / (G - 1) * bread %*% crossprod(S) %*% bread
  list(beta = beta, se = sqrt(diag(V)), G = G)
}

selftest <- function() {
  set.seed(1)
  x <- as.numeric(runif(5000) < .3)
  y <- as.numeric(runif(5000) < ifelse(x == 1, .2, .1))
  a <- sum(x == 1 & y == 1); b <- sum(x == 1 & y == 0); c_ <- sum(x == 0 & y == 1); d_ <- sum(x == 0 & y == 0)
  f <- logit_cluster(cbind(1, x), y, seq_len(5000))
  stopifnot(abs(f$beta[2] - log(a * d_ / (b * c_))) < 1e-6)
  stopifnot(abs(f$se[2] - sqrt(1 / a + 1 / b + 1 / c_ + 1 / d_)) / f$se[2] < 0.02)
  set.seed(SEED)
}

MODEL <- list(A = "bblr", B = "pblr", C = c("bblr", "pblr"))

a8 <- function() {
  d$stratum <- paste0(d$desa, "_", d$tahun)
  d$jk_p <- as.numeric(!is.na(d$jk) & d$jk == "P")
  r <- list()
  for (nm in c("S0", "S1", "S3")) for (o in UTAMA) for (mn in names(MODEL)) {
    faktor <- MODEL[[mn]]
    ok <- sk[[nm]] & !is.na(d[[o]])
    for (f in faktor) ok <- ok & !is.na(d[[f]])
    x <- d[ok, ]
    sm <- tapply(x[[o]], x$stratum, mean)
    x <- x[x$stratum %in% names(sm)[sm > 0 & sm < 1], ]
    kol <- list(const = rep(1, nrow(x)))
    for (f in faktor) kol[[f]] <- as.numeric(x[[f]])
    kol$jk_P <- x$jk_p
    for (k in UMUR_LABEL[-1]) kol[[paste0("umur_", k)]] <- as.numeric(!is.na(x$kel_umur) & x$kel_umur == k)
    for (s in sort(unique(x$stratum))[-1]) kol[[paste0("FE_", s)]] <- as.numeric(x$stratum == s)
    X <- do.call(cbind, kol)
    fit <- logit_cluster(X, as.numeric(x[[o]]), x$id_anak)
    for (i in seq_along(kol)) {
      k <- names(kol)[i]
      if (startsWith(k, "FE_") || k == "const") next
      z <- fit$beta[i] / fit$se[i]
      r[[length(r) + 1]] <- data.frame(skenario = nm, outcome = o, model = mn, term = k, OR = round(exp(fit$beta[i]), 3),
        ci_low = round(exp(fit$beta[i] - 1.96 * fit$se[i]), 3), ci_high = round(exp(fit$beta[i] + 1.96 * fit$se[i]), 3),
        p = round(2 * (1 - pnorm(abs(z))), 5), n_obs = nrow(x), n_anak = fit$G, n_kasus = as.integer(sum(x[[o]])))
    }
  }
  do.call(rbind, r)
}

# ---------- A9: longitudinal ----------
pasangan <- function(x) {
  x <- x[, c("id_anak", "bulan_berkas", "desa", "tahun", "umur_bln", "tinggi", "stunting", "wasting")]
  x$t <- unname(IDX[x$bulan_berkas])
  x <- x[order(x$id_anak, x$t), ]
  n <- nrow(x)
  nxt_id <- c(x$id_anak[-1], NA)
  geser <- function(v) ifelse(!is.na(nxt_id) & nxt_id == x$id_anak, c(v[-1], NA), NA)
  nt <- geser(x$t)
  ok <- !is.na(nt) & nt == x$t + 1
  p <- x[ok, ]
  for (o in c("stunting", "wasting")) {
    a <- p[[o]]; b <- geser(x[[o]])[ok]
    p[[paste0(o, "_ins")]] <- ifelse(!is.na(a) & a == 0, b, NA)
    p[[paste0(o, "_pem")]] <- ifelse(!is.na(a) & a == 1, 1 - b, NA)
    p[[paste0(o, "_flip")]] <- ifelse(!is.na(a) & !is.na(b), as.numeric(a != b), NA)
  }
  p$dtinggi <- geser(x$tinggi)[ok] - p$tinggi
  p$turun1 <- ifelse(is.na(p$dtinggi), NA, as.numeric(p$dtinggi <= -1))
  p$naik5 <- ifelse(is.na(p$dtinggi), NA, as.numeric(p$dtinggi >= 5))
  p
}

a9_transisi <- function() {
  trans <- list(); tumbuh <- list()
  ukuran <- c(ins = "insiden_per_bulan", pem = "pemulihan_per_bulan", flip = "berubah_status")
  for (nm in c("S0", "S1", "S3")) {
    p <- pasangan(d[sk[[nm]], ])
    gp <- grup_desa(p)
    for (ds in names(gp)) for (th in sort(unique(gp[[ds]]$tahun))) {
      z <- gp[[ds]][gp[[ds]]$tahun == th, ]
      for (o in c("stunting", "wasting")) for (m in names(ukuran)) {
        b <- boot_mean(z, paste0(o, "_", m))
        trans[[length(trans) + 1]] <- data.frame(skenario = nm, desa = ds, tahun = th, outcome = o, ukuran = ukuran[[m]],
          n_pasangan = b$n, n_anak = b$n_anak, pct = round(100 * b$mean, 2), ci_low = round(100 * b$ci_low, 2), ci_high = round(100 * b$ci_high, 2))
      }
    }
    if (nm == "S0") {
      p$kel <- as.character(cut(p$umur_bln, UMUR_BATAS, right = FALSE, labels = UMUR_LABEL))
      ringkas <- function(v, ds, th, ku) {
        v <- v[!is.na(v$dtinggi), ]
        data.frame(desa = ds, tahun = th, kel_umur = ku, n_pasangan = nrow(v), mean_cm = round(mean(v$dtinggi), 3), sd_cm = round(sd(v$dtinggi), 3),
                   pct_turun_ge1cm = round(100 * mean(v$turun1), 2), pct_naik_ge5cm = round(100 * mean(v$naik5), 2))
      }
      for (th in sort(unique(p$tahun))) tumbuh[[length(tumbuh) + 1]] <- ringkas(p[p$tahun == th, ], "SEMUA", th, "semua")
      for (ds in sort(unique(p$desa))) for (th in sort(unique(p$tahun[p$desa == ds]))) tumbuh[[length(tumbuh) + 1]] <- ringkas(p[p$desa == ds & p$tahun == th, ], ds, th, "semua")
      for (th in sort(unique(p$tahun))) for (ku in UMUR_LABEL) {
        v <- p[p$tahun == th & !is.na(p$kel) & p$kel == ku, ]
        if (nrow(v)) tumbuh[[length(tumbuh) + 1]] <- ringkas(v, "SEMUA", th, ku)
      }
    }
  }
  list(do.call(rbind, trans), do.call(rbind, tumbuh))
}

km_kohort <- function(nm) {
  x <- d[sk[[nm]] & !is.na(d$stunting), ]
  x$t <- unname(IDX[x$bulan_berkas])
  x <- x[order(x$id_anak, x$t), ]
  id <- x$id_anak
  baris1 <- !duplicated(id)
  t0 <- setNames(x$t[baris1], id[baris1])
  st0 <- setNames(x$stunting[baris1], id[baris1])
  u0 <- pertama_nn(x$umur_bln, id)
  jk <- pertama_nn(x$jk, id)
  bblr <- pertama_nn(x$bblr, id)
  th <- setNames(x$tahun[baris1], id[baris1])
  ids <- names(t0)[which(st0 == 0 & u0[names(t0)] < 24)]
  tev <- tapply(x$t[x$stunting == 1], id[x$stunting == 1], min)
  akhir <- tapply(x$t, id, max)
  k <- data.frame(id_anak = ids, t0 = t0[ids], tahun_masuk = th[ids], jk = jk[ids], bblr = bblr[ids], umur_bln = u0[ids], stringsAsFactors = FALSE)
  k$t_ev <- as.numeric(tev[ids])
  k$event <- as.integer(!is.na(k$t_ev))
  k$waktu <- ifelse(k$event == 1, k$t_ev - k$t0, akhir[ids] - k$t0)
  k$masuk_umur <- as.character(cut(k$umur_bln, c(0, 6, 12, 24), right = FALSE, labels = c("0-5", "6-11", "12-23")))
  k[k$waktu > 0, ]
}

km <- function(g) {
  out <- list(); S <- 1; v <- 0
  for (t in seq_len(max(g$waktu))) {
    nr <- sum(g$waktu >= t); dt <- sum(g$waktu == t & g$event == 1)
    if (nr == 0) break
    S <- S * (1 - dt / nr)
    if (nr > dt) v <- v + dt / (nr * (nr - dt))
    se <- S * sqrt(v)
    out[[t]] <- data.frame(waktu_bln = t, n_berisiko = nr, kejadian = dt, S = round(S, 4), ci_low = round(max(S - 1.96 * se, 0), 4), ci_high = round(min(S + 1.96 * se, 1), 4))
  }
  do.call(rbind, out)
}

logrank <- function(a, b) {
  O <- E <- V <- 0
  for (t in seq_len(max(a$waktu, b$waktu))) {
    n1 <- sum(a$waktu >= t); n2 <- sum(b$waktu >= t); n <- n1 + n2
    da <- sum(a$waktu == t & a$event == 1); dd <- da + sum(b$waktu == t & b$event == 1)
    if (n < 2 || dd == 0) next
    O <- O + da
    E <- E + dd * n1 / n
    V <- V + dd * (n1 / n) * (1 - n1 / n) * (n - dd) / (n - 1)
  }
  chi2 <- (O - E)^2 / V
  c(round(chi2, 2), round(1 - pchisq(chi2, 1), 5))
}

a9_km <- function() {
  kurva <- list(); lr <- list()
  for (nm in c("S0", "S3")) {
    k <- km_kohort(nm)
    strata <- list(list("semua", "semua", k))
    for (kol in c("tahun_masuk", "jk", "bblr", "masuk_umur")) {
      kk <- k[!is.na(k[[kol]]), ]
      for (v in sort(unique(kk[[kol]]))) strata[[length(strata) + 1]] <- list(kol, if (kol == "bblr") sprintf("%.1f", v) else as.character(v), kk[kk[[kol]] == v, ])
    }
    for (s in strata) {
      r <- km(s[[3]])
      kurva[[length(kurva) + 1]] <- cbind(skenario = nm, faktor = s[[1]], nilai = s[[2]], n_anak = nrow(s[[3]]), n_kejadian = sum(s[[3]]$event), r)
    }
    for (kol in c("jk", "bblr")) {
      kk <- k[!is.na(k[[kol]]), ]
      gg <- lapply(sort(unique(kk[[kol]])), function(v) kk[kk[[kol]] == v, ])
      u <- logrank(gg[[1]], gg[[2]])
      lr[[length(lr) + 1]] <- data.frame(skenario = nm, faktor = kol, n_anak = nrow(kk), n_kejadian = sum(kk$event), chi2 = u[1], p = u[2])
    }
  }
  list(do.call(rbind, kurva), do.call(rbind, lr))
}

selftest()
tulis(a8(), args[2], "a8_faktor_risiko")
h <- a9_transisi(); tulis(h[[1]], args[2], "a9_transisi_status"); tulis(h[[2]], args[2], "a9_kecepatan_tumbuh")
h <- a9_km(); tulis(h[[1]], args[2], "a9_km_stunting"); tulis(h[[2]], args[2], "a9_logrank")
