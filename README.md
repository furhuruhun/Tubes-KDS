# Analisis Profil Makronutrien dan Kalkulasi Energi Ekivalen
*Tugas Besar IF3211 Komputasi Domain Spesifik*

Proyek ini berfokus pada pemodelan komputasi biologi untuk topik **Makromolekul: Karbohidrat, Lipid, dan Protein**.

## Anggota Kelompok

| Nama | NIM |
| :--- | :--- |
| Muhammad Farhan | 18223004 |
| Thaffariq Azka Rahmat | 18223048 |
| Indana Aulia Ayundazulfa | 18223100 |
| Nurul Na'im Natifah | 18223106 |

## Deskripsi Proyek

Program berbasis *Command-Line Interface* (CLI) yang dikembangkan dengan Python. Sistem ini dirancang untuk membaca data makanan dan memprosesnya melalui dua jalur perhitungan paralel: tabulasi kalori Atwater dan estimasi mol ATP berdasarkan teori biokimia. Tujuannya adalah untuk menyajikan perbandingan nilai gizi yang selaras dengan proses biologi aslinya.

## Fitur Utama

* **Kalkulasi Energi Atwater:** Mengonversi massa makronutrien menjadi nilai kalori dalam kilokalori.
* **Estimasi ATP Dasar:** Menggunakan konstanta *yield* ATP per gram yang diturunkan dari nilai teoritis oksidasi aerobik substrat representatif.
* **Klasifikasi Diet RDA:** Mengklasifikasikan profil diet pengguna berdasarkan rasio kalori sesuai standar *Dietary Reference Intakes* (Institute of Medicine).
* **Dekomposisi Asam Amino:** Menghitung distribusi gram setiap asam amino menggunakan data fraksi komposisi dari USDA FoodData Central.
* **Estimasi ATP Detail:** Menghitung kontribusi energi setiap asam amino secara individual berdasarkan jalur katabolisme spesifiknya dalam siklus TCA.
* **Visualisasi Data:** Mentransformasikan hasil kalkulasi menjadi representasi grafis (*donut chart*, *bar chart*, diagram kontribusi ATP) menggunakan Matplotlib dan Numpy, serta mengekspor data ke format CSV/JSON.

## Persyaratan Sistem & Cara Menjalankan

Sistem diuji dan dirancang berjalan pada lingkungan Python. Pastikan pustaka yang dibutuhkan sudah terinstal di sistem Anda.

```bash
# Clone repository
git clone [https://github.com/furhuruhun/Tubes-KDS.git](https://github.com/furhuruhun/Tubes-KDS.git)

# Pindah ke direktori program
cd Tubes-KDS

# Instal dependensi pustaka
pip install matplotlib numpy

# Jalankan program utama
python main.py