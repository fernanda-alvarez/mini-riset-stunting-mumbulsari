# Sensitivitas umur kasar + tabel & grafik untuk laporan.
# Usage: Rscript tabel_grafik_mtbs.R <xlsx siap olah> <xlsx analisis lanjut> <xlsx output> <folder grafik>
suppressMessages({ library(anthro); library(readxl); library(openxlsx); library(ggplot2) })
set.seed(2026)
a <- commandArgs(TRUE); dir.create(a[4], showWarnings = FALSE)
anak <- as.data.frame(read_excel(a[2], sheet = "Analisis_Per_Anak"))
hub <- as.data.frame(read_excel(a[2], sheet = "Hubungan_Gizi_Diagnosis"))
kel <- as.data.frame(read_excel(a[1], sheet = "Dikeluarkan"))

wilson <- function(x, n) { p <- x / n; z <- 1.959964; den <- 1 + z^2 / n
  h <- z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2)) / den; c <- (p + z^2 / (2 * n)) / den
  round(100 * c(p, c - h, c + h), 1) }
pct <- function(n, N) sprintf("%d (%.1f)", n, 100 * n / N)

## ---- Sensitivitas umur kasar ----
# Kandidat: dikeluarkan HANYA karena umur kasar ("N tahun" = umur N*12 s.d. N*12+11 bulan), N <= 4
# agar seluruh rentang umurnya tetap <60 bulan. Hanya anak yang belum ada di analisis utama.
k <- kel[kel$alasan_dikeluarkan == "umur kasar (tahun bulat)" & !is.na(kel$id_pasien) &
         !is.na(kel$umur_bulan) & kel$umur_bulan <= 48 & !(kel$id_pasien %in% anak$id_pasien), ]
k <- k[order(k$id_pasien, as.Date(k$tgl_kunjungan)), ]; k <- k[!duplicated(k$id_pasien), ]
sex <- ifelse(toupper(substr(k$jk, 1, 1)) == "L", 1, 2)
skenario <- c("Batas bawah (N x 12 bln)" = 0, "Titik tengah (N x 12 + 6 bln)" = 6, "Batas atas (N x 12 + 11 bln)" = 11)
sens <- do.call(rbind, lapply(names(skenario), function(s) {
  z <- anthro_zscores(sex = sex, age = k$umur_bulan + skenario[[s]], is_age_in_month = TRUE, lenhei = k$pb_cm, weight = k$bb_kg)
  st <- ifelse(z$flen %in% 1 | is.na(z$zlen), NA, as.integer(z$zlen < -2))
  gab <- c(anak$stunting, st); gab <- gab[!is.na(gab)]; ci <- wilson(sum(gab), length(gab))
  data.frame(skenario = s, anak_tambahan = sum(!is.na(st)), stunting_pada_tambahan = round(100 * mean(st, na.rm = TRUE), 1),
             n_gabungan = length(gab), stunting_gabungan = ci[1], IK95 = sprintf("%.1f-%.1f", ci[2], ci[3]))
}))
ut <- anak$stunting[!is.na(anak$stunting)]; ciu <- wilson(sum(ut), length(ut))
sens <- rbind(data.frame(skenario = "Analisis utama (umur tepat saja)", anak_tambahan = 0, stunting_pada_tambahan = NA,
                         n_gabungan = length(ut), stunting_gabungan = ciu[1], IK95 = sprintf("%.1f-%.1f", ciu[2], ciu[3])), sens)

## ---- Tabel 1: karakteristik subjek ----
N <- nrow(anak); baris <- list()
tambah <- function(v, k, nl) baris[[length(baris) + 1]] <<- data.frame(variabel = v, kategori = k, `n (%)` = nl, check.names = FALSE)
tambah("Umur (bulan)", "median (IQR)", sprintf("%.1f (%.1f-%.1f)", median(anak$umur_bulan), quantile(anak$umur_bulan, .25), quantile(anak$umur_bulan, .75)))
kat <- function(v, lab, ord = NULL) { x <- ifelse(is.na(anak[[v]]), "Tidak tercatat", as.character(anak[[v]]))
  t <- table(x); lv <- if (is.null(ord)) names(sort(t, decreasing = TRUE)) else intersect(c(ord, "Tidak tercatat"), names(t))
  for (l in lv) tambah(lab, l, pct(t[[l]], N)) }
kat("kelompok_umur", "Kelompok umur", c("0-5 bln", "6-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-60 bln"))
anak$jk_lbl <- ifelse(anak$jk == "L", "Laki-laki", "Perempuan"); kat("jk_lbl", "Jenis kelamin")
kat("desa", "Desa"); kat("pembiayaan", "Pembiayaan"); kat("tahun_data", "Tahun data", c("2025", "2026"))
dxl <- c(dx_ISPA_atas = "ISPA atas", dx_pneumonia = "Pneumonia", dx_diare = "Diare", dx_demam = "Demam",
         dx_kulit = "Penyakit kulit", dx_telinga = "Penyakit telinga", dx_susp_TB = "Suspek TB", dx_lainnya = "Lainnya")
for (d in names(dxl)) tambah("Diagnosis MTBS*", dxl[[d]], pct(sum(anak[[d]], na.rm = TRUE), N))
tambah("Diagnosis MTBS*", "Tidak tercatat", pct(sum(is.na(anak$dx_lainnya)), N))
tabel1 <- do.call(rbind, baris)

## ---- Tabel 2: distribusi status gizi ----
dist <- function(v, lab, ord) { x <- anak[[v]]; n <- sum(!is.na(x))
  do.call(rbind, lapply(ord, function(l) data.frame(indeks = lab, kategori = l, n = sum(x == l, na.rm = TRUE),
                                                    persen = round(100 * sum(x == l, na.rm = TRUE) / n, 1), N = n))) }
tabel2 <- rbind(dist("status_TBU", "TB/U", c("Sangat pendek", "Pendek", "Normal", "Tinggi")),
                dist("status_BBU", "BB/U", c("BB sangat kurang", "BB kurang", "BB normal", "Risiko BB lebih")),
                dist("status_BBTB", "BB/TB", c("Gizi buruk", "Gizi kurang", "Gizi baik", "Berisiko gizi lebih", "Gizi lebih", "Obesitas")))

## ---- Tabel 3: stunting menurut karakteristik ----
t3 <- function(v, lab, ord = NULL) { x <- anak[!is.na(anak$stunting) & !is.na(anak[[v]]), ]
  lv <- if (is.null(ord)) sort(unique(x[[v]])) else intersect(ord, unique(x[[v]]))
  tb <- table(factor(x[[v]], lv), x$stunting); p <- suppressWarnings(chisq.test(tb))
  p <- if (any(p$expected < 5)) fisher.test(tb, simulate.p.value = TRUE, B = 1e4)$p.value else p$p.value
  do.call(rbind, lapply(seq_along(lv), function(i) { s <- x$stunting[x[[v]] == lv[i]]; ci <- wilson(sum(s), length(s))
    data.frame(variabel = lab, kategori = lv[i], n = length(s), stunting = sum(s), persen = ci[1],
               IK95 = sprintf("%.1f-%.1f", ci[2], ci[3]), p = if (i == 1) signif(p, 3) else NA) })) }
anak$desa_g <- ifelse(anak$desa %in% c("LUAR WILAYAH", "TIDAK JELAS") | is.na(anak$desa), NA, anak$desa)
tabel3 <- rbind(t3("kelompok_umur", "Kelompok umur", c("0-5 bln", "6-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-60 bln")),
                t3("jk_lbl", "Jenis kelamin"), t3("desa_g", "Desa (wilayah kerja)"), t3("pembiayaan", "Pembiayaan"),
                t3("tahun_data", "Tahun data"))

## ---- Tabel 4: hubungan diagnosis ----
tabel4 <- hub; tabel4$diagnosis <- dxl[tabel4$diagnosis]

## ---- Grafik ----
tema <- theme_minimal(base_size = 12) + theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))
simpan <- function(p, f, w = 7, h = 4.5) { ggsave(file.path(a[4], f), p, width = w, height = h, dpi = 200, bg = "white"); file.path(a[4], f) }
t3u <- tabel3[tabel3$variabel == "Kelompok umur", ]; t3u$kategori <- factor(t3u$kategori, t3u$kategori)
ci3 <- function(d) { r <- do.call(rbind, strsplit(d$IK95, "-")); d$lo <- as.numeric(r[, 1]); d$hi <- as.numeric(r[, 2]); d }
t3u <- ci3(t3u)
g1 <- ggplot(t3u, aes(kategori, persen)) + geom_col(fill = "#3B7EA1", width = .65) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = .2) + geom_text(aes(label = sprintf("%.1f%%\nn=%d", persen, n), y = hi + 7), size = 3.3) +
  labs(title = "Proporsi stunting menurut kelompok umur", x = NULL, y = "Stunting (%) dengan IK 95%") + ylim(0, 85) + tema
t3d <- ci3(tabel3[tabel3$variabel == "Desa (wilayah kerja)", ]); t3d$kategori <- reorder(t3d$kategori, t3d$persen)
g2 <- ggplot(t3d, aes(persen, kategori)) + geom_col(fill = "#C0504D", width = .65) +
  geom_errorbar(aes(xmin = lo, xmax = hi), width = .2, orientation = "y") + geom_text(aes(label = sprintf("%.1f%% (n=%d)", persen, n), x = hi + 2), hjust = 0, size = 3.3) +
  labs(title = "Proporsi stunting menurut desa", x = "Stunting (%) dengan IK 95%", y = NULL) + xlim(0, 100) + tema
t2 <- tabel2; t2$kategori <- factor(t2$kategori, rev(unique(t2$kategori))); t2$indeks <- factor(t2$indeks, c("TB/U", "BB/U", "BB/TB"))
g3 <- ggplot(t2, aes(indeks, persen, fill = kategori)) + geom_col(width = .6, colour = "white") +
  geom_text(aes(label = ifelse(persen >= 4, sprintf("%.0f%%", persen), "")), position = position_stack(vjust = .5), size = 3.2) +
  labs(title = "Distribusi status gizi (PMK 2/2020)", x = NULL, y = "%", fill = NULL) + tema +
  scale_fill_manual(values = c(`Sangat pendek` = "#A50026", Pendek = "#F46D43", Normal = "#66BD63", Tinggi = "#4575B4",
    `BB sangat kurang` = "#A50026", `BB kurang` = "#F46D43", `BB normal` = "#66BD63", `Risiko BB lebih` = "#FDAE61",
    `Gizi buruk` = "#A50026", `Gizi kurang` = "#F46D43", `Gizi baik` = "#66BD63", `Berisiko gizi lebih` = "#FEE08B",
    `Gizi lebih` = "#FDAE61", Obesitas = "#D73027"), guide = "none") +
  geom_text(aes(label = ifelse(persen >= 8, as.character(kategori), "")), position = position_stack(vjust = .5),
            size = 2.6, vjust = 2.2)
zt <- anak$zTBU[!(anak$flag_zTBU %in% 1) & !is.na(anak$zTBU)]
g4 <- ggplot(data.frame(z = zt), aes(z)) + geom_histogram(aes(y = after_stat(density)), binwidth = .5, fill = "#3B7EA1", colour = "white") +
  stat_function(fun = dnorm, linetype = "dashed", linewidth = .8) + geom_vline(xintercept = -2, colour = "#C0504D") +
  labs(title = "Sebaran z-score TB/U dibanding standar WHO", subtitle = sprintf("Garis putus = populasi rujukan WHO (rerata 0); rerata sampel %.2f, n=%d", mean(zt), length(zt)),
       x = "z-score TB/U", y = "Densitas") + tema
png_files <- c(simpan(g1, "G1_stunting_kelompok_umur.png"), simpan(g2, "G2_stunting_desa.png"),
               simpan(g3, "G3_distribusi_status_gizi.png"), simpan(g4, "G4_sebaran_z_TBU.png"))

wb <- createWorkbook(); hs <- createStyle(textDecoration = "bold", fgFill = "#DDEBF7")
sh <- list(`Tabel1_Karakteristik` = tabel1, `Tabel2_Status_Gizi` = tabel2, `Tabel3_Stunting_Karakteristik` = tabel3,
           `Tabel4_Gizi_Diagnosis` = tabel4, `Sensitivitas_Umur_Kasar` = sens)
for (nm in names(sh)) { addWorksheet(wb, nm); writeData(wb, nm, sh[[nm]], headerStyle = hs); setColWidths(wb, nm, 1:ncol(sh[[nm]]), "auto") }
writeData(wb, "Tabel1_Karakteristik", data.frame(x = c(sprintf("N = %d anak (kunjungan layak pertama).", N),
  "* Satu anak dapat memiliki >1 kelompok diagnosis.")), startRow = nrow(tabel1) + 3, colNames = FALSE)
writeData(wb, "Tabel3_Stunting_Karakteristik", "p: chi-square, atau Fisher (simulasi) bila ada expected <5. Desa luar wilayah/tidak jelas tidak ditampilkan.",
          startRow = nrow(tabel3) + 3)
writeData(wb, "Sensitivitas_Umur_Kasar", c("Umur kasar 'N tahun' berarti umur sebenarnya N x 12 s.d. N x 12 + 11 bulan; ketiga skenario menguji rentang itu.",
  "Hanya kunjungan yang dikeluarkan semata karena umur kasar, N <= 4 tahun, anak belum ada di analisis utama; satu kunjungan pertama per anak."),
  startRow = nrow(sens) + 3)
addWorksheet(wb, "Grafik"); r <- 1
for (f in png_files) { insertImage(wb, "Grafik", f, startRow = r, startCol = 1, width = 7, height = 4.5, units = "in"); r <- r + 25 }
saveWorkbook(wb, a[3], overwrite = TRUE)
print(sens, row.names = FALSE); print(tabel3[!is.na(tabel3$p), c("variabel", "p")], row.names = FALSE); cat("Grafik:", length(png_files), "\n")
