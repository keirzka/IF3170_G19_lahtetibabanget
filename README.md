# IF3170_G19_lahtetibabanget

Implementasi Algoritma Local Search pada Penyusunan Konfigurasi Paket di dalam Truk

## Deskripsi

Program ini mencari konfigurasi pengisian paket di dalam truk yang memaksimalkan total value paket yang diangkut, dengan constraint

- paket tidak boleh melayang dan tidak boleh menembus dinding peti kemas,
- paket tidak boleh saling tumpang tindih,
- paket pecah belah (*fragile*) tidak boleh menjadi penopang paket lain, dan
- total berat paket tidak boleh melebihi kapasitas truk.

Algoritma *local search* yang diimplementasikan yaitu

1. **Hill-Climbing**
2. **Simulated Annealing**
3. **Genetic Algorithm**

Setiap state dapat berpindah ke neighbor melalui tiga jenis langkah yaitu menukar posisi dua paket (*swap*), memindahkan paket ke koordinat lain (*move*), dan merotasi paket 90° terhadap sumbu x, y, atau z (*rotate*).

## Struktur Repository

```
IF3170_G19_lahtetibabanget/
├── docs/
├── output/
├── src/
│   ├── data/
│   ├── models.py
│   ├── io_handler.py
│   ├── validator.py
│   ├── objective.py
│   ├── generator.py
│   ├── neighbor.py=
│   ├── hill_climbing.py
│   ├── simulated_annealing.py
│   ├── genetic.py
│   ├── experiment_runner.py
│   ├── experiment_hill_climbing.py
│   ├── main_sa.py
│   ├── experiment_ga.py 
│   ├── visualisasi.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Setup

1. Pastikan **Python 3.10** atau lebih baru sudah terpasang
2. Clone repository dan masuk ke foldernya

```bash
   git clone https://github.com/<username>/IF3170_G19_lahtetibabanget.git
   cd IF3170_G19_lahtetibabanget
```

3. Pasang dependensi:

```bash
   pip install -r requirements.txt
```

## Format Input

File input berbentuk JSON dan diletakkan di folder `src/data/`. Contoh:

```json
{
  "Truck": {"width": 10, "length": 20, "height": 5, "max_capacity": 500},
  "Package": [
    {"id": "RusdiPackage", "width": 3, "length": 4, "height": 1,
     "value": 60, "weight": 5, "is_fragile": false, "eta": 3}
  ]
}
```

Test case yang dipakai pada eksperimen: 

## Cara Menjalankan

**Semua perintah dijalankan dari dalam folder `src/`**, karena program membaca file input dari `./data/`.

```bash
cd src
```

### Hill-Climbing

```bash
python experiment_hill_climbing.py
```

Masukkan nama file input saat diminta, misalnya `test1_hill_climbing.json`. Program menjalankan seluruh varian Hill-Climbing dan menampilkan nilai objective awal dan akhir, banyak iterasi, durasi, serta utilisasi ruang.

### Simulated Annealing

```bash
python main_sa.py test1_hill_climbing.json
```

Simulated Annealing dijalankan tiga kali (seed 1, 2, 3). Hasil tersimpan di `output/SA_<nama_test_case>_<timestamp>/`:

- `experiment.log`, `summary.json`, `summary.csv`: log dan ringkasan ketiga run
- `comparison_plot.png`: perbandingan nilai objective ketiga run
- `run_<k>/initial_state.json`, `run_<k>/final_state.json`: state awal dan akhir
- `run_<k>/result.json`: nilai akhir, durasi, banyak iterasi, frekuensi stuck, dan parameter
- `run_<k>/objective_plot.png`: plot nilai objective terhadap iterasi
- `run_<k>/acceptance_prob_plot.png`: plot e^(ΔE/T) terhadap iterasi
- `run_<k>/record.json`: data run untuk visualisasi 3D

### Genetic Algorithm

```bash
python experiment_ga.py data/test1_hill_climbing.json
```

Opsi tambahan: `--seed <angka>` (seed dasar, default 1000), `--runs <angka>` (default 3), dan `--elitism`.
Program menjalankan tiga variasi banyak iterasi (populasi dikontrol) dan tiga variasi jumlah populasi (iterasi dikontrol), masing-masing tiga kali. Hasil tersimpan di `output/ga/`.

### Visualisasi

Visualisasi 3D state awal dan akhir serta plot riwayat nilai objective untuk satu run:

```bash
python -c "from visualisasi import visualize_run; visualize_run('../output/ga/<nama_run>.json')"
```

Untuk hasil Simulated Annealing, gunakan file `record.json` di folder run yang bersangkutan, misalnya `../output/SA_test1_hill_climbing_<timestamp>/run_1/record.json`.

## Pembagian Tugas

| Anggota | NIM | Tugas |
|---|---|---|
| Keisha Rizka Syofyani | 13524073 | Model data, parser input, constraint validator, objective function, generator initial state, Hill-Climbing beserta eksperimennya, setup repository. Laporan: cover, deskripsi persoalan, representasi state dan objective function, bagian Hill-Climbing, referensi, kompilasi dan format akhir |
| Helena Kristela Sarhawa | 13524109 | Fungsi neighbor, Simulated Annealing beserta eksperimennya, experiment runner dan logger, README. Laporan: bagian neighbor dan Simulated Annealing, analisis perbandingan antaralgoritma |
| Vara Azzara Ramli Pulukadang | 13524091 | Genetic Algorithm beserta eksperimennya, visualisasi 3D dan plot hasil eksperimen. Laporan: bagian Genetic Algorithm, analisis pengaruh iterasi dan populasi, bagian visualisasi, pembagian tugas, kesimpulan dan saran |