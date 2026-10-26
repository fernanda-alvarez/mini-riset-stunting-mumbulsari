# Analisis sensitivitas P1 (Kaplan-Meier terkonfirmasi, delayed entry, log-rank terstratifikasi) dan P3 (penumpukan digit, simulasi pembulatan) di R.
# Padanan analisis_tahap2c.py. P2 (bulan terukur per anak) ada di skrip/spss/analisis_spss.sps.
# Pakai: Rscript skrip/analisis_r_3.R <anak_analisis.csv> <who_lhfa_lms.csv> <folder keluaran>
args <- commandArgs(trailingOnly = TRUE)
dir_skrip <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
source(file.path(dir_skrip, "r_umum.R"))
dir.create(args[3], showWarnings = FALSE, recursive = TRUE)
set.seed(SEED)
d <- baca_anak(args[1])
lms <- read.csv(args[2])
sk <- skenario(d)
JEDA_MAKS <- 3; HARI_PER_BLN <- 30.4375; ULANG <- 20

terakhir_nn <- function(v, g) { ok <- !is.na(v); r <- v[ok][!duplicated(g[ok], fromLast = TRUE)]; setNames(r, g[ok][!duplicated(g[ok], fromLast = TRUE)]) }

# ---------- P1 ----------
kohort <- function(mask, konfirmasi) {
  x <- d[mask & !is.na(d$stunting), ]
  x$t <- unname(IDX[x$bulan_berkas])
  x <- x[order(x$id_anak, x$t), ]
  id <- x$id_anak
  n <- nrow(x)
  sama <- c(id[-1] == id[-n], FALSE)
  ev <- x$stunting == 1
  if (konfirmasi) ev <- ev & sama & c(x$stunting[-1], NA) == 1 & (c(x$t[-1], NA) - x$t <= JEDA_MAKS)
  ev[is.na(ev)] <- FALSE
  b1 <- !duplicated(id)
  t0 <- setNames(x$t[b1], id[b1]); st0 <- setNames(x$stunting[b1], id[b1])
  u0 <- pertama_nn(x$umur_bln, id); jk <- pertama_nn(x$jk, id); bblr <- pertama_nn(x$bblr, id); desa <- pertama_nn(x$desa, id)
  ids <- names(t0)[which(st0 == 0 & u0[names(t0)] < 24)]
  xe <- x[ev, ]
  t_ev <- pertama_nn(xe$t, xe$id_anak); u_ev <- pertama_nn(xe$umur_bln, xe$id_anak)
  t_ak <- terakhir_nn(x$t, id); u_ak <- terakhir_nn(x$umur_bln, id)
  k <- data.frame(id_anak = ids, t0 = unname(t0[ids]), u0 = unname(u0[ids]), jk = unname(jk[ids]), bblr = unname(bblr[ids]), desa = unname(desa[ids]), stringsAsFactors = FALSE)
  k$t_ev <- unname(t_ev[ids]); k$u_ev <- unname(u_ev[ids]); k$t_ak <- unname(t_ak[ids]); k$u_ak <- unname(u_ak[ids])
  k$event <- as.integer(!is.na(k$t_ev))
  k$waktu <- ifelse(k$event == 1, k$t_ev, k$t_ak) - k$t0
  k$umur_keluar <- ifelse(k$event == 1, k$u_ev, k$u_ak)
  k$masuk_umur <- as.character(cut(k$u0, c(0, 6, 12, 24), right = FALSE, labels = c("0-5", "6-11", "12-23")))
  k[k$waktu > 0, ]
}

km_titik <- function(masuk, keluar, event, titik) {
  S <- 1; tt <- sort(unique(keluar[event == 1])); sv <- numeric(length(tt))
  for (i in seq_along(tt)) {
    r <- masuk < tt[i] & keluar >= tt[i]
    S <- S * (1 - sum(keluar == tt[i] & event == 1 & r) / sum(r))
    sv[i] <- S
  }
  sapply(titik, function(q) { j <- which(tt <= q); if (length(j)) sv[max(j)] else 1 })
}

logrank <- function(masuk, keluar, event, grup, strata) {
  O <- E <- V <- 0
  for (s in unique(strata)) {
    m <- strata == s
    mk <- masuk[m]; kl <- keluar[m]; ev <- event[m]; gr <- grup[m]
    for (t in sort(unique(kl[ev == 1]))) {
      r <- mk < t & kl >= t
      n <- sum(r); n1 <- sum(r & gr == 1)
      dd <- sum(kl == t & ev == 1 & r); d1 <- sum(kl == t & ev == 1 & r & gr == 1)
      if (n < 2) next
      O <- O + d1; E <- E + dd * n1 / n
      V <- V + dd * (n1 / n) * (1 - n1 / n) * (n - dd) / (n - 1)
    }
  }
  chi2 <- (O - E)^2 / V
  data.frame(chi2 = round(chi2, 2), p = round(1 - pchisq(chi2, 1), 5), O_grup1 = as.integer(O), E_grup1 = round(E, 1))
}

verifikasi <- function() {
  k <- kohort(sk$S3, FALSE)
  stopifnot(nrow(k) == 2995, sum(k$event) == 1152)
  stopifnot(abs(km_titik(rep(0, nrow(k)), k$waktu, k$event, 12) - 0.7304) < 1e-4)
  kb <- k[!is.na(k$bblr), ]
  lr <- logrank(rep(0, nrow(kb)), kb$waktu, kb$event, as.integer(kb$bblr == 1), rep(0, nrow(kb)))$chi2
  stopifnot(abs(lr - 13.17) < 0.01)
  cat("Verifikasi P1 lolos: kohort 2.995 anak, 1.152 kejadian, S(12) 0,7304, log-rank BBLR 13,17.\n")
}

p1 <- function() {
  kurva <- list(); uji <- list()
  for (nm in c("S3", "S0")) for (konf in c(FALSE, TRUE)) {
    k <- kohort(sk[[nm]], konf)
    definisi <- if (konf) "terkonfirmasi" else "satu pengukuran"
    for (spek in list(list("semua", NULL, NULL), list("bblr", "bblr", 1), list("jk", "jk", "L"))) {
      fak <- spek[[1]]; kol <- spek[[2]]; satu <- spek[[3]]
      kk <- if (is.null(kol)) k else k[!is.na(k[[kol]]), ]
      grup_list <- if (is.null(kol)) list(list("semua", kk)) else lapply(sort(unique(kk[[kol]])), function(v) list(if (kol == "bblr") sprintf("%.1f", v) else v, kk[kk[[kol]] == v, ]))
      for (gl in grup_list) {
        g <- gl[[2]]
        s_masuk <- km_titik(rep(0, nrow(g)), g$waktu, g$event, c(12, 24))
        gu <- g[g$umur_keluar > g$u0, ]
        s_umur <- km_titik(gu$u0, gu$umur_keluar, gu$event, c(24, 36))
        kurva[[length(kurva) + 1]] <- data.frame(skenario = nm, definisi = definisi, faktor = fak, nilai = gl[[1]], n_anak = nrow(g), n_kejadian = sum(g$event),
          S_12bln_sejak_masuk = round(s_masuk[1], 4), S_24bln_sejak_masuk = round(s_masuk[2], 4), S_umur24 = round(s_umur[1], 4), S_umur36 = round(s_umur[2], 4),
          n_umur_tak_valid = nrow(g) - nrow(gu))
      }
      if (is.null(kol)) next
      gr <- as.integer(kk[[kol]] == satu)
      for (skala in c("sejak masuk", "umur")) {
        mk <- if (skala == "umur") kk$u0 else rep(0, nrow(kk))
        kl <- if (skala == "umur") kk$umur_keluar else kk$waktu
        for (strat in c("tanpa", "desa", "desa x umur masuk")) {
          if (skala == "umur" && strat == "desa x umur masuk") next
          st <- switch(strat, tanpa = rep("0", nrow(kk)), desa = kk$desa, `desa x umur masuk` = paste0(kk$desa, "|", kk$masuk_umur))
          uji[[length(uji) + 1]] <- cbind(data.frame(skenario = nm, definisi = definisi, faktor = fak, grup1 = if (kol == "bblr") "1.0" else satu, skala = skala, strata = strat,
            n_anak = nrow(kk), n_kejadian = sum(kk$event)), logrank(mk, kl, kk$event, gr, st))
        }
      }
    }
  }
  list(do.call(rbind, kurva), do.call(rbind, uji))
}

# ---------- P3 ----------
rasio <- function(z) { atas <- sum(z >= -2.0 & z < -1.9); bawah <- sum(z >= -2.1 & z < -2.0); c(atas, bawah, if (bawah) atas / bawah else NA_real_) }

p3_digit <- function() {
  v <- zvalid(d[sk$S3, ], "zs_tbu")
  v <- v[!is.na(v$tinggi), ]
  v$kelompok <- ifelse(round(v$tinggi * 10) %% 5 == 0, "desimal .0/.5", "desimal lain")
  r <- list()
  for (th in c(sort(unique(v$tahun)), "2024-2026")) {
    y <- if (th == "2024-2026") v else v[v$tahun == as.integer(th), ]
    for (kel in sort(unique(y$kelompok))) {
      z <- y[y$kelompok == kel, ]
      q <- rasio(z$zs_tbu)
      r[[length(r) + 1]] <- data.frame(tahun = th, kelompok = kel, n = nrow(z), n_atas = q[1], n_bawah = q[2], rasio_tumpuk = round(q[3], 2), pct_di_bawah_min2 = round(100 * mean(z$zs_tbu < -2), 2))
    }
  }
  do.call(rbind, r)
}

lms_untuk <- function(v) {
  hari <- as.integer(pmin(pmax(round(v$umur_bln * HARI_PER_BLN), 0), max(lms$age)))
  sex <- ifelse(v$jk == "L", 1L, 2L)
  i <- match(paste(sex, hari), paste(lms$sex, lms$age))
  list(M = lms$m[i], S = lms$s[i], hari = hari)
}

p3_simulasi <- function() {
  v <- zvalid(d[sk$S3, ], "zs_tbu")
  v <- v[!is.na(v$tinggi) & v$jk %in% c("L", "P"), ]
  ms <- lms_untuk(v); M <- ms$M; S <- ms$S; hari <- ms$hari
  h <- v$tinggi
  kor <- ifelse(hari < 731 & !is.na(v$cara_ukur) & v$cara_ukur == "Berdiri", 0.7, ifelse(hari >= 731 & !is.na(v$cara_ukur) & v$cara_ukur == "Terlentang", -0.7, 0))
  val <- list()
  for (lab in c("tanpa koreksi posisi", "dengan koreksi posisi")) {
    hh <- if (lab == "tanpa koreksi posisi") h else h + kor
    selisih <- abs((hh / M - 1) / S - v$zs_tbu)
    val[[length(val) + 1]] <- data.frame(validasi = lab, median_selisih = round(median(selisih), 3), pct_selisih_le_0_1 = round(100 * mean(selisih <= 0.1), 1))
  }
  kunci <- paste(v$desa, v$tahun)
  mu <- ave(v$zs_tbu, kunci, FUN = mean); sdv <- ave(v$zs_tbu, kunci, FUN = sd)
  tahun <- v$tahun
  cara <- list(`tanpa pembulatan` = function(x) x, `terdekat 0,5 cm` = function(x) round(x * 2) / 2, `terdekat 1 cm` = round, `ke bawah 1 cm` = floor, `ke atas 1 cm` = ceiling)
  hasil <- list()
  for (u in seq_len(ULANG)) {
    zb <- rnorm(length(mu), mu, sdv)
    hb <- M * (1 + S * zb)
    for (nm in names(cara)) {
      zr <- (cara[[nm]](hb) / M - 1) / S
      for (th in 2024:2026) {
        z <- zr[tahun == th]
        hasil[[length(hasil) + 1]] <- data.frame(cara = nm, tahun = th, rasio = rasio(z)[3], pct_bawah = 100 * mean(z < -2))
      }
    }
  }
  h_ <- do.call(rbind, hasil)
  agg <- aggregate(cbind(rasio, pct_bawah) ~ cara + tahun, data = h_, FUN = function(x) c(mean(x, na.rm = TRUE), min(x, na.rm = TRUE), max(x, na.rm = TRUE)), na.action = na.pass)
  sim <- data.frame(cara = agg$cara, tahun = agg$tahun, rasio_rerata = round(agg$rasio[, 1], 2), rasio_min = round(agg$rasio[, 2], 2), rasio_maks = round(agg$rasio[, 3], 2),
                    pct_di_bawah_min2 = round(agg$pct_bawah[, 1], 2))
  ter <- do.call(rbind, lapply(2024:2026, function(th) data.frame(cara = "TERAMATI (data)", tahun = th, rasio_rerata = round(rasio(v$zs_tbu[v$tahun == th])[3], 2),
                                                              rasio_min = NA, rasio_maks = NA, pct_di_bawah_min2 = round(100 * mean(v$zs_tbu[v$tahun == th] < -2), 2))))
  list(rbind(sim, ter), do.call(rbind, val))
}

verifikasi()
h <- p1(); tulis(h[[1]], args[3], "p1_km_konfirmasi"); tulis(h[[2]], args[3], "p1_logrank")
tulis(p3_digit(), args[3], "p3_tumpuk_digit")
h <- p3_simulasi(); tulis(h[[1]], args[3], "p3_simulasi_pembulatan"); tulis(h[[2]], args[3], "p3_validasi_lms")
