// Bangun laporan akhir Word dari data/sigizi/laporan (gambar + tabel_laporan.json) yang dibuat skrip/siapkan_laporan.py.
// Pakai: NODE_PATH=<folder node_modules berisi docx> node skrip/bangun_laporan.js data/sigizi/laporan Laporan_Mini_Riset.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, HeadingLevel,
  TableOfContents, Footer, PageNumber, PageBreak, LevelFormat, BorderStyle, SectionType,
} = require("docx");

const [, , dir, out] = process.argv;
const TB = JSON.parse(fs.readFileSync(path.join(dir, "tabel_laporan.json"), "utf8"));
const FONT = "Times New Roman";
const fmt = (v) => String(v).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
const W = 8504; // lebar teks A4 dengan margin 3 cm

// ---------- helper ----------
const runs = (t, o = {}) => t.split("**").map((s, i) => new TextRun({ text: s, bold: i % 2 === 1 || o.bold, italics: o.italics, size: o.size || 24, font: FONT }));
const P = (t, o = {}) => new Paragraph({
  children: runs(t, o), alignment: o.align || AlignmentType.JUSTIFIED, spacing: { line: o.line || 360, after: o.after ?? 120, before: o.before || 0 },
  indent: o.noIndent ? undefined : { firstLine: 567 }, keepNext: o.keepNext, pageBreakBefore: o.pageBreakBefore,
});
const H1 = (t, o = {}) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, bold: true, size: 26, font: FONT })], alignment: AlignmentType.CENTER, spacing: { before: 240, after: 200 }, pageBreakBefore: o.pb !== false });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, bold: true, size: 24, font: FONT })], spacing: { before: 200, after: 120 }, keepNext: true });
const B = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, children: runs(t), alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 60 } });
const N = (t, ref = "num") => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 60 } });
const cap = (t, o = {}) => new Paragraph({ children: runs(t, { size: 22, bold: false }), alignment: o.center ? AlignmentType.CENTER : AlignmentType.LEFT, spacing: { before: o.before ?? 160, after: o.after ?? 80 }, keepNext: o.keepNext ?? true });
const note = (t) => new Paragraph({ children: runs(t, { size: 20, italics: true }), alignment: AlignmentType.JUSTIFIED, spacing: { line: 240, before: 60, after: 200 } });

const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(key, widths, opts = {}) {
  const t = TB[key];
  const cell = (txt, w, head, i) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { fill: "D9D9D9", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({ children: [new TextRun({ text: String(txt), size: 20, font: FONT, bold: head })], alignment: head || i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 240 } })],
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: t.kepala.map((h, i) => cell(h, widths[i], true, i)) }),
      ...t.baris.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, i)) }))],
  });
}
function figure(file, caption, wpx = 520) {
  const buf = fs.readFileSync(path.join(dir, "gambar", file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true, children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: Math.round((wpx * h) / w) }, altText: { title: caption, description: caption, name: file } })] }),
    cap(caption, { center: true, before: 0, after: 200, keepNext: false }),
  ];
}
const tbl = (key, widths, caption, notes) => [cap(caption), table(key, widths), notes ? note(notes) : new Paragraph({ spacing: { after: 160 }, children: [] })];

// ---------- isi ----------
const cover = [
  new Paragraph({ spacing: { before: 1200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LAPORAN MINI RISET", bold: true, size: 28, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Kepaniteraan Klinik Ilmu Kesehatan Masyarakat", size: 24, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: 360, after: 600 }, children: [new TextRun({ text: "STATUS GIZI BALITA DAN FAKTOR RISIKO STUNTING DI WILAYAH KERJA PUSKESMAS MUMBULSARI, KABUPATEN JEMBER, TAHUN 2024–2026: ANALISIS DATA RUTIN SIGIZIKESGA DAN PENILAIAN KUALITAS DATA", bold: true, size: 28, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Disusun oleh:", size: 24, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "[Nama penulis]", size: 24, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: "NIM [nomor induk mahasiswa]", size: 24, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Pembimbing: [nama pembimbing]", size: 24, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1400 }, children: [new TextRun({ text: "FAKULTAS KEDOKTERAN", bold: true, size: 26, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "UNIVERSITAS JEMBER", bold: true, size: 26, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "2026", bold: true, size: 26, font: FONT })] }),
];

const abstrak = [
  H1("ABSTRAK", { pb: false }),
  P("**Latar belakang.** Data rutin SigiziKesga adalah sumber utama pemantauan status gizi balita di tingkat Puskesmas, tetapi kualitas pengukurannya jarang dievaluasi. **Tujuan.** Menggambarkan status gizi balita per desa di wilayah kerja Puskesmas Mumbulsari tahun 2024–2026, menilai kualitas data, dan menganalisis hubungan berat badan lahir rendah (BBLR), panjang badan lahir rendah (PBLR), jenis kelamin, dan umur dengan stunting, wasting, dan underweight.", { noIndent: true }),
  P("**Metode.** Analisis data sekunder 108.322 pengukuran dari 6.312 balita usia 0–59 bulan (Januari 2024–September 2026) di tujuh desa. Data dibersihkan dan ditandai (flag), lalu dianalisis dengan empat skenario sensitivitas. Prevalensi dihitung dengan interval kepercayaan bootstrap klaster per anak; faktor risiko dengan regresi logistik berefek tetap desa × tahun dan galat baku robust klaster; waktu sampai stunting dengan Kaplan-Meier.", { noIndent: true }),
  P("**Hasil.** Prevalensi stunting seluruh Puskesmas 6,5% (2024), 13,1% (2025), dan 7,0% (2026), tetapi berubah tidak masuk akal antar desa dan tahun (mis. Mumbulsari 4,2% → 28,4% → 1,9%). Tinggi badan sangat sering dibulatkan (digit desimal .0/.5 hingga 98% pada sebagian desa), jumlah anak di bawah −2 SD jauh lebih sedikit daripada yang diharapkan dari sebaran z-score (6,2% vs 17,8% pada 2024), dan pada 2026 tiga desa mengisi hampir seluruh pengukuran pada satu tanggal per bulan. Petugas entri mengonfirmasi pengisian satu tanggal per bulan dan pembulatan tinggi. BBLR (OR 2,11; IK 95% 1,64–2,71) dan PBLR (OR 1,47; 1,15–1,88) meningkatkan odds stunting, sedangkan anak perempuan lebih rendah (OR 0,68; 0,60–0,78); temuan ini konsisten pada semua skenario.", { noIndent: true }),
  P("**Kesimpulan.** Prevalensi absolut dari data rutin ini tidak dapat diandalkan, sedangkan asosiasi faktor risiko konsisten dan sejalan dengan literatur. Perbaikan pencatatan tinggi badan dan tanggal ukur diperlukan.", { noIndent: true }),
  P("**Kata kunci:** stunting, status gizi balita, kualitas data, BBLR, SigiziKesga, Puskesmas Mumbulsari.", { noIndent: true }),
  H1("ABSTRACT"),
  P("**Background.** Routine SigiziKesga data are the main source of under-five nutritional surveillance at primary health centres, yet measurement quality is rarely evaluated. **Objectives.** To describe the nutritional status of children under five in the catchment area of Mumbulsari Primary Health Centre (2024–2026), assess data quality, and analyse the association of low birth weight (LBW), short birth length, sex and age with stunting, wasting and underweight.", { noIndent: true }),
  P("**Methods.** Secondary analysis of 108,322 measurements from 6,312 children aged 0–59 months (January 2024–September 2026) in seven villages. Data were flagged and analysed under four sensitivity scenarios. Prevalence used cluster (child-level) bootstrap confidence intervals; risk factors were analysed with logistic regression with village × year fixed effects and cluster-robust standard errors; time to stunting with Kaplan-Meier.", { noIndent: true }),
  P("**Results.** Puskesmas-wide stunting prevalence was 6.5% (2024), 13.1% (2025) and 7.0% (2026) but changed implausibly between villages and years (e.g. Mumbulsari 4.2% → 28.4% → 1.9%). Heights were heavily rounded (decimal digits .0/.5 up to 98% in some villages), far fewer children fell below −2 SD than expected from the z-score distribution (6.2% vs 17.8% in 2024), and in 2026 three villages recorded nearly all measurements on one date per month; health workers confirmed one-date-per-month entry and height rounding. LBW (OR 2.11; 95% CI 1.64–2.71) and short birth length (OR 1.47; 1.15–1.88) increased the odds of stunting, and girls had lower odds (OR 0.68; 0.60–0.78); findings were consistent across all scenarios.", { noIndent: true }),
  P("**Conclusion.** Absolute prevalence from these routine data is unreliable, whereas risk-factor associations are consistent and in line with the literature. Better recording of height and measurement dates is needed.", { noIndent: true }),
  P("**Keywords:** stunting, child nutritional status, data quality, low birth weight, SigiziKesga, Mumbulsari.", { noIndent: true }),
];

const bab1 = [
  H1("BAB I  PENDAHULUAN"),
  H2("1.1 Latar Belakang"),
  P("Stunting, yaitu tinggi atau panjang badan menurut umur kurang dari −2 simpangan baku (SD) standar pertumbuhan WHO, menjadi salah satu prioritas kesehatan masyarakat di Indonesia [1,2]. Pemerintah menetapkan percepatan penurunan stunting melalui Peraturan Presiden Nomor 72 Tahun 2021 [3]. Survei Status Gizi Indonesia (SSGI) 2024 melaporkan prevalensi stunting nasional 19,8%, turun dari 21,5% pada 2023 [4]."),
  P("Di tingkat Puskesmas, pemantauan status gizi balita bertumpu pada pengukuran rutin berat dan tinggi badan di posyandu yang dicatat dalam aplikasi SISFO Gizi Terpadu (SigiziKesga) Kementerian Kesehatan. Data rutin ini murah dan mencakup seluruh sasaran, sehingga dipakai untuk menentukan prioritas intervensi per desa. Namun nilai informasinya bergantung pada mutu pengukuran dan pencatatan. Evaluasi data surveilans gizi elektronik di Kabupaten Magelang menemukan kecenderungan digit pada 62,8% pengukuran tinggi badan [7], dan penelitian lain di Indonesia secara khusus menilai akurasi dan presisi pengukuran antropometri balita oleh kader posyandu [8]. Standar deviasi z-score dan preferensi digit lazim dipakai sebagai indikator mutu data antropometri [5,6]."),
  P("Faktor risiko stunting sudah banyak diteliti. Ulasan determinan stunting di Indonesia menyimpulkan bahwa kelahiran prematur dan panjang badan lahir pendek merupakan determinan yang konsisten [9]; analisis Riskesdas 2013 pada anak di bawah dua tahun melaporkan odds stunting 2,55 kali pada anak dengan berat lahir kurang dari 2.500 g [10]; dan analisis gabungan kohort kelahiran menunjukkan hubungan lahir kecil untuk masa kehamilan dan prematur dengan kekurangan gizi pada masa kanak-kanak [11]. Pertanyaan yang belum banyak dijawab adalah apakah hubungan tersebut juga dapat dibaca dari data rutin Puskesmas, mengingat mutu pengukuran data rutin."),
  P("Wilayah kerja Puskesmas Mumbulsari, Kabupaten Jember, terdiri atas tujuh desa dan memiliki data SigiziKesga yang lengkap untuk 33 bulan. Laporan ini memanfaatkan data tersebut untuk menggambarkan status gizi balita, menilai kualitas data, dan menganalisis faktor risiko stunting."),
  H2("1.2 Rumusan Masalah"),
  N("Bagaimana gambaran status gizi balita (stunting, wasting, underweight) per desa dan per tahun di wilayah kerja Puskesmas Mumbulsari pada 2024–2026?", "rm"),
  N("Bagaimana kualitas data pengukuran antropometri rutin pada SigiziKesga?", "rm"),
  N("Apakah BBLR, PBLR, jenis kelamin, dan umur berhubungan dengan stunting, wasting, dan underweight?", "rm"),
  H2("1.3 Tujuan"),
  P("Tujuan umum: menggambarkan status gizi balita dan faktor risiko stunting di wilayah kerja Puskesmas Mumbulsari berdasarkan data rutin 2024–2026. Tujuan khusus: (1) menghitung prevalensi stunting, wasting, dan underweight per desa dan tahun; (2) menilai kualitas data pengukuran; (3) menganalisis hubungan BBLR, PBLR, jenis kelamin, dan umur dengan status gizi; (4) memberikan rekomendasi perbaikan pencatatan."),
  H2("1.4 Manfaat"),
  P("Bagi Puskesmas, laporan ini menunjukkan bagian data rutin yang dapat dipercaya dan bagian yang perlu diperbaiki. Bagi peneliti dan pembimbing, laporan ini memberi contoh penilaian kualitas data sebelum analisis. Bagi pengambil kebijakan, laporan ini memperingatkan bahwa prevalensi per desa dari data rutin tidak boleh langsung dipakai tanpa verifikasi."),
];

const bab2 = [
  H1("BAB II  METODE"),
  H2("2.1 Desain dan Lokasi"),
  P("Penelitian ini adalah analisis data sekunder dari catatan rutin, dengan dua kerangka: potong lintang berulang per bulan untuk prevalensi, dan kohort retrospektif pada anak yang diukur berulang untuk analisis longitudinal. Lokasinya wilayah kerja Puskesmas Mumbulsari, Kabupaten Jember, dengan tujuh desa: Karangkedawung, Kawangrejo, Lampeji, Lengkong, Mumbulsari, Suco, dan Tamansari."),
  H2("2.2 Sumber Data"),
  P("Data berasal dari aplikasi SigiziKesga (sigizikesga.kemkes.go.id), diunduh dengan akun Puskesmas Mumbulsari pada 19 Oktober 2026. Laporan utama adalah “Daftar Status Gizi” (satu baris per pengukuran per anak) untuk 33 bulan (Januari 2024–September 2026), semua desa dan posyandu, usia 0–59 bulan. Laporan agregat “Rekap Status Gizi” dan “Rekap Sasaran Anak” dipakai untuk validasi dan untuk menghitung cakupan. Data Oktober 2026 tidak dianalisis karena baru memuat 20 pengukuran (sampai 19 Oktober) dan belum final. Hitungan stunting, wasting, dan underweight dari data per anak sama persis dengan laporan agregat Puskesmas pada 147 dari 147 desa-bulan yang dapat dibandingkan (Januari 2025–September 2026)."),
  H2("2.3 Populasi"),
  P("Populasi adalah seluruh balita (0–59 bulan) yang tercatat diukur di SigiziKesga wilayah Puskesmas Mumbulsari pada periode tersebut: 108.322 pengukuran dari 6.312 anak. Tidak ada pengambilan sampel."),
  H2("2.4 Definisi Operasional"),
  B("**Stunting:** TB/U kurang dari −2 SD (kategori pendek dan sangat pendek). **Wasting:** BB/TB kurang dari −2 SD (gizi kurang dan gizi buruk). **Underweight:** BB/U kurang dari −2 SD (berat badan kurang dan sangat kurang). Klasifikasi mengikuti Standar Antropometri Anak, Permenkes 2/2020, yang mengacu pada standar pertumbuhan WHO 2006 [1,2]. Kategori situs konsisten dengan nilai z-score pada ambang −2 SD. Pengukuran berkategori Outlier (z-score tidak masuk akal secara biologis) dikeluarkan dari penyebut."),
  B("**BBLR:** berat lahir kurang dari 2.500 g (kolom BB Lahir tertulis dalam kg dan diubah ke gram). **PBLR:** panjang lahir kurang dari 48 cm. Nilai di luar 500–6.000 g atau 30–60 cm dianggap tidak valid."),
  B("**Heaping tinggi badan:** proporsi tinggi dengan digit desimal .0 atau .5. Bila diukur sampai 0,1 cm, nilainya sekitar 20%."),
  B("**Cakupan:** jumlah anak terukur dibagi sasaran Rekap Sasaran Anak (tersedia Januari 2025–September 2026)."),
  H2("2.5 Pembersihan dan Penandaan Data"),
  P("NIK diganti ID acak (HMAC-SHA256 dengan garam lokal) dan kolom nama, nama orang tua, alamat, RT/RW, serta tanggal lahir dibuang; umur dihitung dari tanggal lahir. Data bermasalah ditandai, tidak dihapus. **Flag keras** (baris dikeluarkan dari seluruh analisis): z-score penanda (|ZS| ≥ 999), tinggi atau berat 0, berat > 40 kg atau tinggi > 130 cm, NIK ganda dalam satu bulan, dan umur di luar 0–<60 bulan. **Flag lunak** dipakai untuk analisis sensitivitas: desa-bulan anomali (TB/U Outlier ≥ 10% atau stunting ≥ 50%), desa-tahun dengan heaping tinggi (≥ 70%), satu tanggal ukur untuk ≥ 30% anak dalam desa-bulan, ketidaksesuaian cara ukur dengan umur, dan posyandu kosong."),
  H2("2.6 Skenario Sensitivitas"),
  B("**S0:** semua baris tanpa flag keras dan dengan desa terisi (105.600 pengukuran)."),
  B("**S1:** S0 tanpa Lampeji, Mumbulsari, dan Lengkong untuk Januari–September 2026."),
  B("**S2:** S0 hanya pada desa-tahun dengan heaping rendah (< 70%)."),
  B("**S3:** S0 tanpa desa-bulan anomali."),
  H2("2.7 Analisis Statistik"),
  P("Prevalensi dihitung dari anak-bulan yang dikumpulkan; interval kepercayaan (IK) 95% memakai bootstrap klaster per anak (500 ulangan) karena anak yang sama diukur berulang. Perbandingan antar desa dan menurut jenis kelamin atau umur memakai uji chi-square pada satu pengukuran acak per anak per tahun agar sampel saling bebas. Tren bulanan dinilai dengan uji Mann-Kendall dan kemiringan Sen, serta regresi segmented dengan titik patah Januari 2026 (galat baku Newey-West). Faktor risiko dianalisis dengan regresi logistik pada anak-bulan, disesuaikan jenis kelamin dan kelompok umur dengan efek tetap desa × tahun (sehingga anak dibandingkan dengan anak di desa dan tahun yang sama) serta galat baku robust klaster per anak. Waktu sampai stunting pertama pada anak yang pertama kali terlihat tidak stunting pada umur < 24 bulan dianalisis dengan Kaplan-Meier dan uji log-rank. Analisis memakai Python 3.12 (pandas, scipy); regresi logistik diimplementasikan sendiri dan diuji dengan mereproduksi odds ratio tabel 2×2 dan galat baku Woolf. Seluruh skrip tersimpan pada repositori proyek."),
  H2("2.8 Etika"),
  P("Penggunaan data memperoleh izin dari pihak Puskesmas ([nomor dan tanggal surat izin]; dokumen dilampirkan terpisah). Analisis dilakukan secara lokal pada data berpseudonim; laporan hanya memuat agregat. [Isi status kaji etik bila ada.]"),
];

const bab3 = [
  H1("BAB III  HASIL"),
  H2("3.1 Karakteristik Data dan Cakupan"),
  P("Setelah flag keras dikeluarkan, 105.600 dari 108.322 pengukuran (97,5%) dianalisis pada skenario S0. Proporsi anak perempuan sekitar 47%, rerata umur saat ukur 31–33 bulan, BBLR 7,8–8,7%, dan PBLR 10,4–11,0% (Tabel 1)."),
  ...tbl("t1", [800, 1200, 1300, 1000, 1000, 1100, 1052, 1052], "Tabel 1. Karakteristik data per tahun (skenario S0)", "Anak unik dihitung per tahun; BBLR dan PBLR dihitung per anak."),
  P("Cakupan pengukuran (terukur dibanding sasaran) berubah tajam. Pada 2025 rata-rata 2.878 anak terukur dari 4.616 sasaran per bulan (cakupan 55–72%); pada 2026 rata-rata 4.168 dari 4.431 (92–95%), dengan lonjakan pada Januari 2026 padahal sasaran hampir tidak berubah (Tabel 2, Gambar 1). Pada 2026, cakupan di Lampeji, Lengkong, dan Mumbulsari rata-rata 100% dari sasaran. Sasaran 2024 tidak tersedia."),
  ...tbl("t6", [1500, 2300, 2300, 2404], "Tabel 2. Sasaran, anak terukur, dan cakupan per tahun"),
  ...figure("g7_cakupan.png", "Gambar 1. Cakupan pengukuran bulanan, Januari 2025–September 2026"),
  H2("3.2 Kualitas Data"),
  P("Masalah kualitas membesar dari 2024 ke 2026 (Tabel 3). Flag keras mengenai 0,7% baris pada 2024, 2,7% pada 2025, dan 4,1% pada 2026. TB/U Outlier naik dari 0,5% menjadi 3,1% dan 8,9%. Posyandu kosong baru muncul pada 2025. Pada 2026, 50,6% baris berbagi satu tanggal ukur dengan sebagian besar anak lain di desa-bulannya."),
  ...tbl("t3", [3000, 1100, 1468, 1468, 1468], "Tabel 3. Baris yang terkena masalah kualitas per tahun, n (%)"),
  P("**Pembulatan tinggi badan.** Di sebagian desa, tinggi hampir selalu berupa bilangan bulat atau setengah: digit desimal .0 atau .5 mencapai 91% (2024) dan 98% (2025) di Lampeji, 92–93% di Suco, dan 84–93% di Karangkedawung, sedangkan Lengkong (35–44%) dan Mumbulsari 2024 (48%) lebih wajar; nilai yang diharapkan adalah sekitar 20% (Tabel 4). Petugas entri mengonfirmasi bahwa tinggi badan memang dibulatkan."),
  P("**Kekurangan anak di bawah −2 SD.** Bila z-score TB/U kira-kira berdistribusi normal, persentase anak di bawah −2 SD dapat diperkirakan dari rerata dan SD yang teramati. Pada seluruh Puskesmas, persentase tercatat jauh di bawah yang diharapkan: 6,2% vs 17,8% (2024) dan 13,0% vs 26,1% (2025). Pada desa yang pencatatannya tampak stabil juga demikian, misalnya Karangkedawung 2024 (7,5% vs 20,5%) dan Kawangrejo 2024 (7,1% vs 19,4%) (Tabel 4, Gambar 3). Jumlah anak di interval z −2,0 sampai −1,9 mencapai 5,8 kali (2024) dan 5,0 kali (2025) jumlah anak di interval −2,1 sampai −2,0, padahal rasionya seharusnya sekitar 1; puncaknya 19,2 di Lampeji 2025 (Gambar 2). Pada 2025, Lengkong (heaping 35%) dan Mumbulsari (75%) mencatat 29% anak di bawah −2 SD, mendekati yang diharapkan (36% dan 31%)."),
  ...tbl("t4", [1700, 700, 1000, 1000, 800, 1100, 1100, 1104], "Tabel 4. Heaping tinggi badan, rerata dan SD z-score TB/U, serta persentase di bawah −2 SD tercatat dan diharapkan (skenario S3)", "Diharapkan = persentase di bawah −2 SD bila z-score normal dengan rerata dan SD yang sama. Rasio penumpukan = jumlah anak di z −2,0 s.d. −1,9 dibanding −2,1 s.d. −2,0. Heaping dihitung per desa-tahun dan tidak dihitung untuk seluruh Puskesmas (–)."),
  ...figure("g2_histogram_zscore.png", "Gambar 2. Sebaran z-score TB/U seluruh Puskesmas per tahun (skenario S0)"),
  ...figure("g3_tercatat_vs_diharapkan.png", "Gambar 3. Persentase di bawah −2 SD tercatat dibanding diharapkan menurut desa dan tahun (skenario S3). KD Karangkedawung, KW Kawangrejo, LP Lampeji, LK Lengkong, MB Mumbulsari, SC Suco, TS Tamansari", 400),
  P("**Pengisian satu tanggal per bulan dan entri massal 2026.** Pada Januari dan April–September 2026, 83–100% pengukuran di Lampeji, Mumbulsari, dan Lengkong bertanggal sama (30 Januari, 23 April, 22 Mei, 30 Juni, 31 Juli, 28 Agustus, 28 September). Pada bulan-bulan itu stunting hanya 0–3%. Rerata z-score TB/U tahunan bergeser dari 2025 ke 2026 sebesar −1,56 menjadi 0,01 di Lampeji, −1,22 menjadi 0,13 di Mumbulsari, dan −1,37 menjadi −0,10 di Lengkong; pada Juli 2026 stunting melonjak ke 84–87% dengan 89–94% TB/U Outlier. Petugas entri mengonfirmasi bahwa sebagian desa mengisi satu tanggal per bulan. Pola serupa terlihat di Lengkong dan Mumbulsari pada 2024, sehingga tanggal ukur di desa-desa tersebut adalah tanggal entri, bukan tanggal pengukuran."),
  H2("3.3 Prevalensi Status Gizi"),
  P("Prevalensi gabungan Puskesmas (S0) adalah stunting 6,5% (IK 95% 6,0–7,0) pada 2024, 13,1% (12,2–13,9) pada 2025, dan 7,0% (6,5–7,6) pada 2026; wasting 7,8%, 8,9%, dan 6,1%; underweight 10,1%, 12,4%, dan 10,6% (Lampiran 1). Per desa, angka berubah di luar kewajaran (Tabel 5, Gambar 4): stunting Mumbulsari 4,2% → 28,4% → 1,9%, Lengkong 14,0% → 24,2% → 2,4%, Tamansari 1,3% → 14,9% → 8,9%, dan Suco 8,7% → 8,5% → 21,5%. Perbedaan antar desa bermakna secara statistik pada setiap tahun (chi-square, p < 0,001), tetapi karena temuan pada 3.2, perbedaan itu lebih mencerminkan cara pencatatan per desa daripada perbedaan keadaan anak."),
  ...tbl("t2", [2402, 2034, 2034, 2034], "Tabel 5. Prevalensi stunting per desa dan tahun, % (IK 95%), skenario S0"),
  ...figure("g1_prevalensi_desa_tahun.png", "Gambar 4. Prevalensi stunting per desa dan tahun dengan IK 95% (skenario S0)"),
  P("Pada tingkat Puskesmas, tren bulanan stunting tidak bermakna (Mann-Kendall τ = 0,15; p = 0,22), sedangkan wasting turun (τ = −0,30; p = 0,014; sekitar 1,2 poin persen per tahun). Regresi segmented menunjukkan lompatan −10,6 poin persen stunting pada Januari 2026 (p < 0,001), yang bertepatan dengan perubahan pencatatan dan lonjakan cakupan sehingga tidak dapat ditafsirkan sebagai perbaikan gizi. Pada skenario S1, komposisi desa berubah setelah Januari 2026, sehingga tren naik yang tampak pada S1 adalah artefak komposisi."),
  H2("3.4 Umur dan Jenis Kelamin"),
  P("Status gizi berbeda bermakna menurut kelompok umur pada hampir semua tahun dan outcome (p < 0,05; pengecualian underweight 2025, p = 0,06), serta menurut jenis kelamin pada sebagian besar tahun. Pada 2024, rerata z-score TB/U turun dari −0,39 (umur 0–2 bulan) ke −1,15 (umur 30 bulan) lalu mendatar sekitar −1,0, pola penurunan pertumbuhan yang lazim; kurva 2025 serupa tetapi lebih rendah. Kurva 2026 menyimpang: rerata anak 6–11 bulan (sekitar −0,07) lebih tinggi daripada bayi 0–2 bulan (−0,50) (Gambar 5), sejalan dengan masalah data 2026."),
  ...figure("g4_kurva_umur.png", "Gambar 5. Rerata z-score TB/U menurut umur dan tahun (skenario S3)"),
  H2("3.5 Faktor Risiko"),
  P("Pada model yang mengendalikan jenis kelamin, kelompok umur, dan efek tetap desa × tahun (skenario S3; " + [fmt(TB.t5.n[0]), "pengukuran dari", fmt(TB.t5.n[1]), "anak dengan", fmt(TB.t5.n[2]), "kasus stunting"].join(" ") + "), BBLR meningkatkan odds stunting sekitar dua kali lipat (OR 2,11; IK 95% 1,64–2,71) dan PBLR meningkatkannya sekitar 1,5 kali (OR 1,47; 1,15–1,88). Anak perempuan memiliki odds stunting lebih rendah (OR 0,68; 0,60–0,78). Pola serupa terlihat untuk underweight (BBLR OR 2,30; PBLR 1,51) dan wasting (BBLR OR 1,89; PBLR 1,24, p = 0,068) (Tabel 6, Gambar 6). Estimasi hampir identik pada S0, S1, dan S3 (BBLR → stunting: 2,09; 2,11; 2,11; Lampiran 2), sehingga tidak bergantung pada cara menangani data bermasalah."),
  ...tbl("t5", [1900, 1500, 700, 1500, 700, 1500, 704], "Tabel 6. Odds ratio faktor risiko terhadap stunting, wasting, dan underweight (model C, skenario S3)", "Model mencakup BBLR dan PBLR bersama, jenis kelamin, kelompok umur, dan efek tetap desa × tahun; galat baku robust klaster per anak."),
  ...figure("g5_forest_faktor_risiko.png", "Gambar 6. Odds ratio (IK 95%) faktor risiko terhadap tiga outcome gizi (model C, skenario S3)"),
  H2("3.6 Analisis Longitudinal"),
  P("Sekitar 60% anak terukur pada ≥ 12 bulan dan 32% pada ≥ 24 bulan. Pada anak yang pertama kali terlihat tidak stunting pada umur < 24 bulan (S3, 2.895 anak dengan data BBLR), proporsi yang belum stunting pada 12 bulan adalah 64% pada anak BBLR dibanding 74% tanpa BBLR (log-rank p = 0,0003), dan 68% pada laki-laki dibanding 78% pada perempuan (p < 0,0001) (Tabel 7, Gambar 7). Besaran absolut tidak dapat dipakai: sekitar 44% anak menjadi stunting dalam 24 bulan, jauh di atas prevalensi, dan pada anak yang sudah stunting 43% (2024) kembali ke status tidak stunting dalam bulan berikutnya, yang tidak mungkin terjadi secara biologis dan menunjukkan kebisingan pengukuran di sekitar −2 SD. Hanya perbandingan relatif antar kelompok yang dipakai."),
  ...tbl("t7", [1900, 1300, 1500, 1900, 1904], "Tabel 7. Proporsi anak yang belum stunting menurut kelompok (Kaplan-Meier, skenario S3)"),
  ...figure("g6_kaplan_meier_bblr.png", "Gambar 7. Kaplan-Meier waktu sampai stunting pertama menurut BBLR (skenario S3; pita = IK 95%)"),
];

const bab4 = [
  H1("BAB IV  PEMBAHASAN"),
  H2("4.1 Kualitas Data sebagai Temuan Utama"),
  P("Temuan terpenting laporan ini adalah bahwa data rutin tidak dapat dipakai begitu saja. Pembulatan tinggi badan yang dikonfirmasi petugas menghasilkan kecenderungan digit yang sangat kuat; pola serupa dilaporkan dalam evaluasi surveilans gizi elektronik di Magelang, dengan kecenderungan digit pada 62,8% pengukuran tinggi [7], dan penilaian mutu data antropometri survei besar memang memeriksa kecenderungan digit dan sebaran z-score [5,6]. Data kami menunjukkan pola yang lebih ekstrem di beberapa desa (hingga 98%)."),
  P("Kekurangan anak di bawah −2 SD dan penumpukan tepat di atas −2 SD tidak sepenuhnya dijelaskan oleh pembulatan saja; pembulatan membuat z-score bergerombol tetapi tidak secara otomatis menggeser anak melewati ambang. Satu dugaan adalah tinggi badan disesuaikan atau diperkirakan sehingga anak tidak terklasifikasi stunting. Dugaan ini belum diuji (misalnya dengan simulasi pembulatan atau pengukuran ulang sampel) dan belum dikonfirmasi petugas; yang dikonfirmasi hanya pembulatan dan pengisian satu tanggal per bulan."),
  P("Pengisian satu tanggal ukur per bulan membuat analisis menurut tanggal pengukuran tidak mungkin pada desa tersebut, dan pada 2026 bertepatan dengan cakupan 100%, stunting sekitar 1–2%, serta pergeseran rerata z-score yang tidak biologis. Karena itu data tiga desa tersebut pada 2026 tidak layak dibaca sebagai kondisi nyata."),
  H2("4.2 Prevalensi"),
  P("Prevalensi stunting data rutin (6,5–13,1%) jauh di bawah angka nasional SSGI 2024 (19,8%) [4]. Kedua sumber berbeda metode sehingga tidak langsung sebanding, tetapi kesenjangan ini sejalan dengan dugaan prevalensi data rutin terlalu rendah. Pada Lengkong dan Mumbulsari tahun 2025, prevalensi tercatat (24–28%) mendekati yang diharapkan dari sebaran z-score. Dugaannya, prevalensi sebenarnya di desa lain juga berkisar di rentang itu. Ini hipotesis yang perlu diverifikasi dengan pengukuran ulang pada sampel balita, bukan kesimpulan. Perbedaan antar desa dan tren waktu pada data ini tidak dapat ditafsirkan tanpa kualifikasi."),
  H2("4.3 Faktor Risiko"),
  P("Hubungan BBLR dengan stunting (OR 2,11) sejalan dengan analisis Riskesdas 2013 pada anak di bawah dua tahun (aOR 2,55; IK 95% 2,05–3,15) [10] dan dengan temuan bahwa lahir kecil untuk masa kehamilan dan prematur meningkatkan risiko kekurangan gizi pada anak [11]. Hubungan PBLR dengan stunting sejalan dengan ulasan Beal dkk. yang menyebut panjang lahir pendek sebagai determinan yang konsisten di Indonesia [9]. Kekuatan analisis ini adalah efek tetap desa × tahun yang membandingkan anak dalam desa dan tahun yang sama, sehingga artefak pencatatan per desa-tahun tidak mempengaruhi estimasi, dan hasilnya stabil pada empat skenario. Odds stunting lebih rendah pada perempuan (OR 0,68) perlu dibandingkan dengan literatur lain sebelum ditafsirkan."),
  P("Penafsiran tetap perlu hati-hati. BBLR dan PBLR dicatat petugas, bukan dari dokumen lahir yang diverifikasi, dan 4–9% kosong. Galat klasifikasi outcome yang tidak berkaitan dengan faktor risiko cenderung melemahkan asosiasi, tetapi bila mutu pencatatan berbeda antar kelompok arah bias tidak pasti; efek tetap desa × tahun mengurangi tetapi tidak menghilangkan masalah ini. Ini adalah asosiasi dari data observasional, bukan hubungan sebab-akibat."),
  H2("4.4 Analisis Longitudinal"),
  P("Perbandingan relatif waktu sampai stunting (BBLR dan jenis kelamin) searah dengan analisis regresi. Insiden dan pemulihan absolut tidak dapat dilaporkan karena kebisingan pengukuran di sekitar ambang."),
  H2("4.5 Keterbatasan"),
  B("Data rutin dengan masalah mutu yang terdokumentasi (pembulatan tinggi, satu tanggal per bulan, entri massal), sehingga prevalensi absolut tidak dapat diandalkan."),
  B("Cakupan berubah tajam pada Januari 2026 (55–72% menjadi 92–95%), sehingga siapa yang diukur berubah; perbandingan 2025 dengan 2026 dipengaruhi seleksi."),
  B("Tidak ada variabel sosial-ekonomi, ASI eksklusif, MPASI, imunisasi, sanitasi, dan riwayat infeksi pada analisis ini; variabel MBG, KPSP, KIA, dan kelas ibu terlalu jarang terisi."),
  B("Satu Puskesmas; analisis eksploratif tanpa koreksi perbandingan ganda; asosiasi bukan sebab-akibat."),
  B("Data Oktober 2026 tidak dianalisis (baru 20 pengukuran sampai 19 Oktober 2026)."),
  B("Ulasan literatur dalam laporan ini terbatas pada sumber yang dapat diverifikasi dan bukan tinjauan sistematis."),
];

const bab5 = [
  H1("BAB V  KESIMPULAN DAN SARAN"),
  H2("5.1 Kesimpulan"),
  N("Prevalensi stunting seluruh Puskesmas dari data rutin adalah 6,5% (2024), 13,1% (2025), dan 7,0% (2026), tetapi angka per desa-tahun berubah tidak masuk akal dan tidak dapat diandalkan.", "ks"),
  N("Data rutin mengandung masalah mutu yang serius: pembulatan tinggi badan, kekurangan anak di bawah −2 SD, pengisian satu tanggal per bulan, dan entri massal pada 2026 di tiga desa; pembulatan dan pengisian satu tanggal per bulan dikonfirmasi petugas.", "ks"),
  N("BBLR dan PBLR meningkatkan odds stunting (OR 2,11 dan 1,47), dan perempuan memiliki odds lebih rendah (OR 0,68); hasil konsisten pada semua skenario sensitivitas.", "ks"),
  N("Hanya analisis perbandingan relatif dan asosiasi faktor risiko yang tahan terhadap masalah mutu data; prevalensi absolut dan insiden tidak boleh dilaporkan tanpa verifikasi.", "ks"),
  H2("5.2 Saran"),
  P("**Untuk Puskesmas:** (1) mencatat tanggal pengukuran sebenarnya, bukan tanggal entri; (2) mengukur tinggi sampai 0,1 cm dengan alat terkalibrasi dan melatih ulang kader serta petugas; (3) memeriksa kualitas data setiap bulan secara otomatis (kecenderungan digit, SD z-score, sebaran tanggal); (4) melengkapi kolom posyandu yang kosong; (5) melakukan pengukuran ulang pada sampel balita untuk memvalidasi prevalensi per desa.", { noIndent: true }),
  P("**Untuk Dinas Kesehatan:** menjadikan penilaian mutu data bagian dari verifikasi laporan Puskesmas sebelum prevalensi per desa dipakai untuk perencanaan.", { noIndent: true }),
  P("**Untuk penelitian selanjutnya:** menambahkan data ASI eksklusif, MPASI, dan imunisasi yang tersedia sebagai laporan terpisah di SigiziKesga, menambah variabel sosial-ekonomi dari sumber lain, dan mengulang analisis setelah pencatatan diperbaiki.", { noIndent: true }),
];

const refs = [
  "WHO Multicentre Growth Reference Study Group. WHO Child Growth Standards: length/height-for-age, weight-for-age, weight-for-length, weight-for-height and body mass index-for-age: methods and development. Geneva: World Health Organization; 2006.",
  "Kementerian Kesehatan Republik Indonesia. Peraturan Menteri Kesehatan Nomor 2 Tahun 2020 tentang Standar Antropometri Anak. Berita Negara Republik Indonesia Tahun 2020 Nomor 7. Jakarta; 2020.",
  "Presiden Republik Indonesia. Peraturan Presiden Nomor 72 Tahun 2021 tentang Percepatan Penurunan Stunting. Jakarta; 2021.",
  "Kementerian Kesehatan Republik Indonesia. SSGI 2024: prevalensi stunting nasional turun menjadi 19,8%. Jakarta; 2025 [dikutip 20 Oktober 2026]. Tersedia dari: https://www.kemkes.go.id/id/ssgi-2024-prevalensi-stunting-nasional-turun-menjadi-198",
  "Mei Z, Grummer-Strawn LM. Standard deviation of anthropometric Z-scores as a data quality assessment tool using the 2006 WHO growth standards: a cross country analysis. Bull World Health Organ. 2007;85(6):441–8. doi:10.2471/BLT.06.034421",
  "Assaf S, Kothari MT, Pullum T. An assessment of the quality of DHS anthropometric data, 2005–2014. DHS Methodological Reports No. 16. Rockville, Maryland, USA: ICF International; 2015.",
  "Riyanto S, Purwaningrum DN, Lazuardi L. Evaluation of anthropometric data quality for children from electronic-based nutrition surveillance: a case study in Magelang Regency, Central Java, Indonesia. Media Kesehat Masy Indones. 2025;21(4):298–311. doi:10.30597/mkmi.v21i4.43510",
  "Febriyanti F, Endah TA, Purnamawati D, Handari SRT, Pasaribu ES. Akurasi dan presisi pengukuran antropometri balita oleh kader posyandu dalam mengidentifikasi kejadian stunting di Puskesmas Sadeng Pasar. J Kesehat Masy. 2025;13(1):27–42. doi:10.14710/jkm.v13i1.46750",
  "Beal T, Tumilowicz A, Sutrisna A, Izwardy D, Neufeld LM. A review of child stunting determinants in Indonesia. Matern Child Nutr. 2018;14(4):e12617. doi:10.1111/mcn.12617",
  "Titaley CR, Ariawan I, Hapsari D, Muasyaroh A, Dibley MJ. Determinants of the stunting of children under two years old in Indonesia: a multilevel analysis of the 2013 Indonesia Basic Health Survey. Nutrients. 2019;11(5):1106. doi:10.3390/nu11051106",
  "Christian P, Lee SE, Donahue Angel M, Adair LS, Arifeen SE, Ashorn P, et al. Risk of childhood undernutrition related to small-for-gestational age and preterm birth in low- and middle-income countries. Int J Epidemiol. 2013;42(5):1340–55. doi:10.1093/ije/dyt109",
];
const pustaka = [H1("DAFTAR PUSTAKA"), ...refs.map((r, i) => new Paragraph({ children: runs(`${i + 1}.\t${r}`, { size: 24 }), alignment: AlignmentType.LEFT, spacing: { line: 252, after: 80 }, indent: { left: 567, hanging: 567 } }))];

const lamp = [
  H1("LAMPIRAN"),
  H2("Lampiran 1. Prevalensi wasting dan underweight per desa dan tahun, % (IK 95%), skenario S0"),
  table("tL1", [1400, 1900, 1735, 1735, 1734]),
  H2("Lampiran 2. Ketahanan odds ratio faktor risiko terhadap stunting menurut skenario"),
  table("tL2", [2300, 900, 1768, 1768, 1768]),
  note("Model A: hanya BBLR; B: hanya PBLR; C: BBLR dan PBLR bersama. Semua model disesuaikan jenis kelamin, kelompok umur, dan efek tetap desa × tahun."),
  H2("Lampiran 3. Berkas analisis"),
  P("Seluruh tabel dan angka dalam laporan ini dapat ditelusuri pada berkas Analisis_Stunting_Mumbulsari.xlsx (16 lembar), tabel CSV di folder data/sigizi/analisis/tabel, dan skrip di folder skrip pada repositori proyek. Data per anak berpseudonim disimpan lokal dan tidak dibagikan.", { noIndent: true }),
];

const sectionProps = { page: { size: { width: 11906, height: 16838 }, margin: { top: 1701, bottom: 1701, left: 1701, right: 1701 } } };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 22, font: FONT })] })] });

const doc = new Document({
  creator: "Mini Riset KOAS IKM", title: "Laporan Mini Riset: Status Gizi Balita dan Faktor Risiko Stunting, Puskesmas Mumbulsari 2024–2026",
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: FONT, color: "000000" }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: FONT, color: "000000" }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      ...["num", "rm", "ks"].map((r) => ({ reference: r, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] })),
    ],
  },
  sections: [
    { properties: sectionProps, children: cover },
    { properties: { ...sectionProps, type: SectionType.NEXT_PAGE }, footers: { default: footer },
      children: [...abstrak,
        new Paragraph({ pageBreakBefore: true, children: [new TextRun({ text: "DAFTAR ISI", bold: true, size: 26, font: FONT })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
        new TableOfContents("Daftar Isi", { hyperlink: true, headingStyleRange: "1-2" }),
        ...bab1, ...bab2, ...bab3, ...bab4, ...bab5, ...pustaka, ...lamp] },
  ],
  });

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("OK", out, b.length); });
