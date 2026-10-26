* Analisis di SPSS: A3 (antar desa), A4 (cakupan), A5 (uji JK & umur), P2 (bulan terukur per anak).
* Padanan analisis_tahap2.py (a3, a4, a5 uji) dan analisis_tahap2c.py (p2). Analisis lainnya ada di skrip/analisis_r_*.R.
* Masukan : data/sumber/anak_analisis/anak_analisis.csv (dari skrip/siapkan_data_spss_r.py) dan data/sigizi/rekap_tambahan/sasaran_cakupan_cek2024.xlsx.
* Keluaran: CSV di data/sigizi/analisis_spss/ (kolom sama dengan tabel Python) dan hasil lengkap di Output Viewer.
* Jalankan dari folder induk proyek: lihat skrip/spss/jalankan_spss.py atau File > Open > Syntax lalu Run > All (CD ke folder induk dulu).

SET DECIMAL DOT.
SET OLANG=ENGLISH.

GET DATA /TYPE=TXT /FILE='data/sumber/anak_analisis/anak_analisis.csv' /ENCODING='UTF8' /DELCASE=LINE /DELIMITERS="," /QUALIFIER='"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2
 /VARIABLES=
  id_anak A11 bulan_berkas A7 tahun F8.0 bulan F8.0 desa A14 posyandu A11 jk A1 tgl_ukur A10 umur_bln F8.3 bb_lahir_g F8.0 tb_lahir_cm F8.3 bblr F8.0 pblr F8.0 berat F8.3 tinggi F8.3 lila F8.3 cara_ukur A10
  zs_bbu F8.3 zs_tbu F8.3 zs_bbtb F8.3 kat_bbu A13 kat_tbu A13 kat_bbtb A17 naik_bb A1 vit_a F8.0 mbg A5 stunting F8.0 stunting_berat F8.0 wasting F8.0 wasting_berat F8.0 underweight F8.0 gizi_lebih F8.0
  f_zs_penanda F8.0 f_nol F8.0 f_aneh F8.0 f_nik_ganda F8.0 f_umur_luar F8.0 f_keras F8.0 f_tgl_luar F8.0 f_pos_kosong F8.0 f_nik_pendek F8.0 f_id_tak_konsisten F8.0 f_tbu_outlier F8.0 f_cara_ukur_salah F8.0
  f_tgl_seragam F8.0 f_anomali_desabulan F8.0 pct_heaping_desa_tahun F8.3 f_heaping_tinggi F8.0 kel_umur A9 t F8.0 s0 F8.0 pa_s0 F8.0 s1 F8.0 pa_s1 F8.0 s2 F8.0 pa_s2 F8.0 s3 F8.0 pa_s3 F8.0.
DATASET NAME anak WINDOW=FRONT.

* ===================== A3 dan A5 (uji): sampel satu pengukuran acak per anak per tahun, S0-S3 ditumpuk =====================.
* pa_sN = 1 menandai pengukuran terpilih untuk skenario N (dipilih di Python dengan seed tetap, jadi sampelnya sama persis dengan analisis Python).
DATASET ACTIVATE anak.
DATASET COPY u0 WINDOW=HIDDEN.
DATASET COPY u1 WINDOW=HIDDEN.
DATASET COPY u2 WINDOW=HIDDEN.
DATASET COPY u3 WINDOW=HIDDEN.
DATASET ACTIVATE u0.
SELECT IF pa_s0=1.
STRING skn (A2).
COMPUTE skn='S0'.
DATASET ACTIVATE u1.
SELECT IF pa_s1=1.
STRING skn (A2).
COMPUTE skn='S1'.
DATASET ACTIVATE u2.
SELECT IF pa_s2=1.
STRING skn (A2).
COMPUTE skn='S2'.
DATASET ACTIVATE u3.
SELECT IF pa_s3=1.
STRING skn (A2).
COMPUTE skn='S3'.
ADD FILES /FILE=u0 /FILE=u1 /FILE=u2 /FILE=u3 /KEEP=skn tahun desa jk kel_umur stunting wasting underweight.
DATASET NAME uji WINDOW=FRONT.
DATASET CLOSE u0.
DATASET CLOSE u1.
DATASET CLOSE u2.
DATASET CLOSE u3.
DATASET ACTIVATE uji.
SORT CASES BY skn tahun.

* Satu CROSSTABS per (faktor, outcome), hasilnya ditangkap OMS ke berkas sementara lalu ditumpuk di tmp/chi_<tag>.sav dan tmp/ct_<tag>.sav.
DEFINE !jalan (tag=!TOKENS(1) /fak=!TOKENS(1) /o=!TOKENS(1) /sel=!ENCLOSE('(',')') /awal=!TOKENS(1))
DATASET ACTIVATE uji.
COMPUTE pilih=(!sel).
FILTER BY pilih.
OMS /SELECT TABLES /IF COMMANDS=['Crosstabs'] SUBTYPES=['Chi-Square Tests'] /DESTINATION FORMAT=SAV OUTFILE='data/sigizi/analisis_spss/tmp/chi_baru.sav' VIEWER=YES.
OMS /SELECT TABLES /IF COMMANDS=['Crosstabs'] SUBTYPES=['Crosstabulation'] /DESTINATION FORMAT=SAV OUTFILE='data/sigizi/analisis_spss/tmp/ct_baru.sav' VIEWER=YES.
SPLIT FILE LAYERED BY skn tahun.
CROSSTABS /TABLES=!fak BY !o /FORMAT=AVALUE TABLES /STATISTICS=CHISQ /CELLS=COUNT EXPECTED ASRESID.
SPLIT FILE OFF.
OMSEND.
FILTER OFF.
DELETE VARIABLES pilih.
* --- chi-kuadrat.
GET FILE='data/sigizi/analisis_spss/tmp/chi_baru.sav' /KEEP=Var1 Var2 Var3 Value df AsymptoticSignificance2sided.
RENAME VARIABLES (Var1 Var2 Var3 AsymptoticSignificance2sided = skn tahunc stat sig).
STRING outcome faktor (A20).
COMPUTE outcome=!QUOTE(!o).
COMPUTE faktor=!QUOTE(!fak).
COMPUTE tahun=NUMBER(tahunc,F4.0).
ALTER TYPE skn (A2) stat (A40).
DELETE VARIABLES tahunc.
!IF (!awal = 1) !THEN
SAVE OUTFILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/chi_',!tag,'.sav')).
!ELSE
ADD FILES /FILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/chi_',!tag,'.sav')) /FILE=*.
SAVE OUTFILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/chi_',!tag,'.sav')).
!IFEND
* --- tabel silang (hanya untuk A3).
!IF (!tag = a3) !THEN
GET FILE='data/sigizi/analisis_spss/tmp/ct_baru.sav' /KEEP=Var1 Var2 Var3 Var4 Var5 @1 Total.
RENAME VARIABLES (Var1 Var2 Var3 Var4 Var5 @1 = skn tahunc lev1 lev2 stat k1).
STRING outcome (A20).
COMPUTE outcome=!QUOTE(!o).
COMPUTE tahun=NUMBER(tahunc,F4.0).
ALTER TYPE skn (A2) stat (A40) lev1 (A20) lev2 (A20).
DELETE VARIABLES tahunc.
!IF (!awal = 1) !THEN
SAVE OUTFILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/ct_',!tag,'.sav')).
!ELSE
ADD FILES /FILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/ct_',!tag,'.sav')) /FILE=*.
SAVE OUTFILE=!QUOTE(!CONCAT('data/sigizi/analisis_spss/tmp/ct_',!tag,'.sav')).
!IFEND
!IFEND
!ENDDEFINE.

* A3: perbedaan prevalensi antar desa, tiap skenario, tahun, outcome.
!jalan tag=a3 fak=desa o=stunting sel=(skn<>' ') awal=1.
!jalan tag=a3 fak=desa o=wasting sel=(skn<>' ') awal=0.
!jalan tag=a3 fak=desa o=underweight sel=(skn<>' ') awal=0.
* A5 (uji): JK dan kelompok umur, S0 dan S1.
!jalan tag=a5 fak=jk o=stunting sel=(skn='S0' OR skn='S1') awal=1.
!jalan tag=a5 fak=jk o=wasting sel=(skn='S0' OR skn='S1') awal=0.
!jalan tag=a5 fak=jk o=underweight sel=(skn='S0' OR skn='S1') awal=0.
!jalan tag=a5 fak=kel_umur o=stunting sel=(skn='S0' OR skn='S1') awal=0.
!jalan tag=a5 fak=kel_umur o=wasting sel=(skn='S0' OR skn='S1') awal=0.
!jalan tag=a5 fak=kel_umur o=underweight sel=(skn='S0' OR skn='S1') awal=0.

* ---- Tabel akhir A3.
GET FILE='data/sigizi/analisis_spss/tmp/ct_a3.sav'.
SELECT IF lev1='desa'.
DATASET NAME ct WINDOW=ASIS.
DATASET COPY ctn WINDOW=HIDDEN.
DATASET ACTIVATE ctn.
SELECT IF stat='Count'.
RENAME VARIABLES (lev2 Total k1 = desa n_anak kasus).
EXECUTE.
DELETE VARIABLES lev1 stat.
SORT CASES BY skn tahun outcome desa.
DATASET ACTIVATE ct.
SELECT IF stat='Adjusted Residual'.
RENAME VARIABLES (lev2 k1 = desa resid_std).
EXECUTE.
DELETE VARIABLES lev1 stat Total.
SORT CASES BY skn tahun outcome desa.
MATCH FILES /FILE=ctn /FILE=ct /BY skn tahun outcome desa.
DATASET NAME a3tab.
DATASET ACTIVATE a3tab.
DATASET CLOSE ct.
DATASET CLOSE ctn.
* persen dan CI Wilson (persen).
COMPUTE p_=kasus/n_anak.
COMPUTE pct=RND(100*p_*100)/100.
COMPUTE pen_=1+1.96**2/n_anak.
COMPUTE c_=(p_+1.96**2/(2*n_anak))/pen_.
COMPUTE h_=1.96*SQRT(p_*(1-p_)/n_anak+1.96**2/(4*n_anak**2))/pen_.
COMPUTE ci_low=RND(100*(c_-h_)*100)/100.
COMPUTE ci_high=RND(100*(c_+h_)*100)/100.
COMPUTE resid_std=RND(resid_std*100)/100.
SORT CASES BY skn tahun outcome.
SAVE OUTFILE='data/sigizi/analisis_spss/tmp/a3_tab.sav' /DROP=p_ pen_ c_ h_.
GET FILE='data/sigizi/analisis_spss/tmp/chi_a3.sav'.
* tabel 2x2 (hanya dua desa, mis. S2 2025): koreksi kontinuitas dipakai seperti scipy chi2_contingency; selain itu Pearson.
SELECT IF stat='Pearson Chi-Square' OR stat='Continuity Correction'.
SORT CASES BY skn tahun outcome stat.
AGGREGATE /OUTFILE=* /BREAK=skn tahun outcome /chi2=FIRST(Value) /df=FIRST(df) /p_chi2=FIRST(sig).
SORT CASES BY skn tahun outcome.
MATCH FILES /FILE='data/sigizi/analisis_spss/tmp/a3_tab.sav' /TABLE=* /BY skn tahun outcome.
COMPUTE chi2=RND(chi2*100)/100.
COMPUTE p_chi2=RND(p_chi2*100000)/100000.
RENAME VARIABLES (skn = skenario).
SORT CASES BY skenario tahun outcome desa.
FORMATS pct ci_low ci_high resid_std chi2 (F8.2) p_chi2 (F8.5) n_anak kasus df tahun (F8.0).
SAVE TRANSLATE /OUTFILE='data/sigizi/analisis_spss/a3_antar_desa.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE /CELLS=VALUES
  /KEEP=skenario tahun outcome desa n_anak kasus pct ci_low ci_high resid_std chi2 df p_chi2.

* ---- Tabel akhir A5 (uji).
GET FILE='data/sigizi/analisis_spss/tmp/chi_a5.sav'.
DATASET NAME chi5.
DATASET COPY nn WINDOW=HIDDEN.
DATASET ACTIVATE nn.
SELECT IF stat='N of Valid Cases'.
RENAME VARIABLES (Value = n_anak).
EXECUTE.
DELETE VARIABLES stat df sig.
SORT CASES BY skn tahun outcome faktor.
DATASET ACTIVATE chi5.
* JK (2x2) memakai koreksi kontinuitas (sama dengan scipy chi2_contingency); kelompok umur memakai Pearson.
SELECT IF (faktor='jk' AND stat='Continuity Correction') OR (faktor='kel_umur' AND stat='Pearson Chi-Square').
RENAME VARIABLES (Value sig = chi2 p_chi2).
EXECUTE.
DELETE VARIABLES stat.
SORT CASES BY skn tahun outcome faktor.
MATCH FILES /FILE=nn /FILE=* /BY skn tahun outcome faktor.
COMPUTE chi2=RND(chi2*100)/100.
COMPUTE p_chi2=RND(p_chi2*100000)/100000.
RENAME VARIABLES (skn = skenario).
SORT CASES BY skenario tahun outcome faktor.
FORMATS chi2 (F8.2) p_chi2 (F8.5) n_anak df tahun (F8.0).
SAVE TRANSLATE /OUTFILE='data/sigizi/analisis_spss/a5_uji_jk_umur.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE /CELLS=VALUES
  /KEEP=skenario tahun outcome faktor n_anak chi2 df p_chi2.
DATASET CLOSE nn.

* ===================== A4: cakupan pengukuran terhadap sasaran =====================.
* terukur = semua baris berdesa (bukan hanya skenario), sama dengan Python.
DATASET ACTIVATE anak.
DATASET COPY terukur WINDOW=HIDDEN.
DATASET ACTIVATE terukur.
SELECT IF desa<>' '.
AGGREGATE /OUTFILE=* /BREAK=desa bulan_berkas /terukur=N.
SORT CASES BY desa bulan_berkas.
DATASET NAME tr.
GET DATA /TYPE=TXT /FILE='data/sumber/anak_analisis/sasaran.csv' /ENCODING='UTF8' /DELCASE=LINE /DELIMITERS="," /QUALIFIER='"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2
 /VARIABLES= tahun F4.0 bulan F2.0 desa A14 laki F8.0 perempuan F8.0 sasaran F8.0.
DATASET NAME sas.
STRING bulan_berkas (A7).
COMPUTE bulan_berkas=CONCAT(LTRIM(STRING(tahun,F4.0)),'-',STRING(bulan,N2)).
EXECUTE.
DELETE VARIABLES tahun bulan laki perempuan.
SORT CASES BY desa bulan_berkas.
DATASET ACTIVATE tr.
MATCH FILES /FILE=* /TABLE=sas /BY desa bulan_berkas.
COMPUTE cakupan_pct=RND(1000*terukur/sasaran)/10.
FORMATS terukur sasaran (F8.0) cakupan_pct (F8.1).
SAVE TRANSLATE /OUTFILE='data/sigizi/analisis_spss/a4_cakupan_desa_bulan.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE /CELLS=VALUES
  /KEEP=desa bulan_berkas terukur sasaran cakupan_pct.
AGGREGATE /OUTFILE=* /BREAK=bulan_berkas /terukur=SUM(terukur) /sasaran=SUM(sasaran).
COMPUTE cakupan_pct=RND(1000*terukur/sasaran)/10.
FORMATS terukur sasaran (F8.0) cakupan_pct (F8.1).
SAVE TRANSLATE /OUTFILE='data/sigizi/analisis_spss/a4_cakupan_bulan.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE /CELLS=VALUES
  /KEEP=bulan_berkas terukur sasaran cakupan_pct.

* ===================== P2: jumlah bulan terukur per anak (semua baris dan S0) =====================.
* Persentil 25/75 dari FREQUENCIES (definisi persentil SPSS: rata-rata tertimbang pada (n+1)p; numpy memakai interpolasi linear pada (n-1)p, jadi bisa beda tipis).
DEFINE !p2 (nama=!TOKENS(1) /label=!TOKENS(1) /sel=!ENCLOSE('(',')') /awal=!TOKENS(1))
DATASET ACTIVATE anak.
DATASET COPY pp WINDOW=HIDDEN.
DATASET ACTIVATE pp.
SELECT IF (!sel).
* satu baris per anak-bulan, lalu hitung bulan berbeda per anak.
AGGREGATE /OUTFILE=* /BREAK=id_anak bulan_berkas /baris=N.
AGGREGATE /OUTFILE=* /BREAK=id_anak /nb=N.
COMPUTE ge12=(nb>=12).
COMPUTE ge24=(nb>=24).
AGGREGATE /OUTFILE='data/sigizi/analisis_spss/tmp/p2_agg.sav' /n_anak=N /pct_ge12=MEAN(ge12) /pct_ge24=MEAN(ge24) /median=MEDIAN(nb) /maks=MAX(nb).
OMS /SELECT TABLES /IF COMMANDS=['Frequencies'] SUBTYPES=['Statistics'] /DESTINATION FORMAT=SAV OUTFILE='data/sigizi/analisis_spss/tmp/p2_pct.sav' VIEWER=YES.
FREQUENCIES VARIABLES=nb /FORMAT=NOTABLE /STATISTICS=MEDIAN MAXIMUM /PERCENTILES=25 75.
OMSEND.
GET FILE='data/sigizi/analisis_spss/tmp/p2_pct.sav'.
SELECT IF Var1='Percentiles'.
AGGREGATE /OUTFILE=* /p25=MIN(Var4) /p75=MAX(Var4).
MATCH FILES /FILE='data/sigizi/analisis_spss/tmp/p2_agg.sav' /FILE=*.
STRING data (A12).
COMPUTE data=REPLACE(!QUOTE(!label),'_',' ').
!IF (!awal = 1) !THEN
SAVE OUTFILE='data/sigizi/analisis_spss/tmp/p2_semua.sav'.
!ELSE
ADD FILES /FILE='data/sigizi/analisis_spss/tmp/p2_semua.sav' /FILE=*.
SAVE OUTFILE='data/sigizi/analisis_spss/tmp/p2_semua.sav'.
!IFEND
DATASET ACTIVATE pp.
DATASET CLOSE pp.
!ENDDEFINE.
!p2 nama=semua label=semua_baris sel=(1=1) awal=1.
!p2 nama=s0 label=S0 sel=(s0=1) awal=0.
GET FILE='data/sigizi/analisis_spss/tmp/p2_semua.sav'.
COMPUTE pct_ge12=RND(1000*pct_ge12)/10.
COMPUTE pct_ge24=RND(1000*pct_ge24)/10.
FORMATS n_anak maks (F8.0) pct_ge12 pct_ge24 median p25 p75 (F8.1).
SAVE TRANSLATE /OUTFILE='data/sigizi/analisis_spss/p2_bulan_terukur.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES /REPLACE /CELLS=VALUES
  /KEEP=data n_anak pct_ge12 pct_ge24 median p25 p75 maks.
