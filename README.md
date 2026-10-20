# IF3170_G19_lahtetibabanget

Implementasi Algoritma Local Search pada Penyusunan Konfigurasi Paket di dalam Truk

## Deskripsi

Program ini mencari konfigurasi pengisian paket ke dalam satu atau beberapa truk yang memaksimalkan total value paket yang diangkut, dengan constraint

- paket tidak boleh melayang dan tidak boleh menembus dinding peti kemas,
- paket tidak boleh saling tumpang tindih,
- paket pecah belah (*fragile*) tidak boleh menjadi penopang paket lain, dan
- total berat paket di setiap truk tidak boleh melebihi kapasitas truk tersebut.

Algoritma *local search* yang diimplementasikan yaitu

1. **Hill-Climbing**: Steepest Ascent, Sideways Move, Stochastic, dan Random Restart
2. **Simulated Annealing**
3. **Genetic Algorithm**

Setiap state dapat berpindah ke neighbor melalui tiga jenis langkah yaitu menukar posisi dua paket (*swap*), memindahkan paket ke koordinat lain atau ke truk lain (*move*), dan merotasi paket 90° terhadap sumbu x, y, atau z (*rotate*).

Spesifikasi bonus yang dikerjakan:

- objective function utilitas dan value per berat;
- seluruh varian Hill-Climbing (Steepest Ascent, Sideways Move, Stochastic, Random Restart);
- multi-truk: program menerima lebih dari satu truk dan memaksimalkan total value yang diangkut seluruh armada.

## Struktur Repository

```
IF3170_G19_lahtetibabanget/
├── docs/
├── output/
│   ├── hc/<nama_input>/
│   ├── sa/<nama_input>/
│   ├── ga/<nama_input>/
│   └── perbandingan_<nama_input>.png
├── src/
│   ├── data/
│   ├── models.py
│   ├── io_handler.py
│   ├── validator.py
│   ├── objective.py
│   ├── generator.py
│   ├── neighbor.py
│   ├── hill_climbing.py
│   ├── simulated_annealing.py
│   ├── genetic.py
│   ├── experiment_runner.py
│   ├── experiment_hill_climbing.py
│   ├── experiment_sa.py
│   ├── experiment_ga.py
│   ├── visualisasi.py
│   └── main.py
├── Makefile
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

3. Pasang dependensi

```bash
pip install -r requirements.txt
```

## Format Input

File input berbentuk JSON dan diletakkan di folder `src/data/`.

Satu truk:

```json
{
  "Truck": {"width": 10, "length": 20, "height": 5, "max_capacity": 500},
  "Package": [
    {"id": "RusdiPackage", "width": 3, "length": 4, "height": 1,
     "value": 60, "weight": 5, "is_fragile": false, "eta": 3}
  ]
}
```

Beberapa truk (bonus multi-truk), gunakan key `Trucks` berisi daftar truk:

```json
{
  "Trucks": [
    {"width": 10, "length": 20, "height": 5, "max_capacity": 500},
    {"width": 8, "length": 12, "height": 5, "max_capacity": 300}
  ],
  "Package": [ ... ]
}
```

Input yang dipakai pada eksperimen:

| File | Keterangan |
|---|---|
| `dataset_n30.json` | 30 paket, 1 truk 10 × 20 × 5 dengan kapasitas 500 (eksperimen utama) |
| `dataset_n30_multitruck.json` | 30 paket yang sama, 2 truk (10 × 20 × 5 kapasitas 500 dan 8 × 12 × 5 kapasitas 300) |

## Cara Menjalankan

Semua perintah dijalankan dari dalam folder `src/`.

```bash
cd src
```

### Menu utama

```bash
python main.py
```

Masukkan nama file input (default `dataset_n30.json`), lalu pilih menu untuk menampilkan initial state, menjalankan eksperimen tiap algoritma, menjalankan semua eksperimen sekaligus, atau membuat visualisasi.

### Menjalankan eksperimen secara langsung

```bash
python experiment_hill_climbing.py dataset_n30.json
python experiment_sa.py dataset_n30.json
python experiment_ga.py dataset_n30.json
```

| Algoritma | Run | Parameter |
|---|---|---|
| Hill-Climbing | 4 varian × 3 run (seed 1, 2, 3) | maksimum iterasi 1000, 20 neighbor per iterasi (Steepest Ascent, Sideways Move, Random Restart), maksimum sideways move berturut-turut 100, maksimum restart 5 |
| Simulated Annealing | 3 run (seed 1, 2, 3) | INITPROB 0,4, TEMPFACTOR 0,95, SIZEFACTOR 16, MINPERCENT 2% |
| Genetic Algorithm | 18 run (seed 1000–1017) | variasi iterasi 100/300/500 dengan populasi 100, variasi populasi 50/100/200 dengan 300 iterasi, mutation rate 0,1. Opsi: `--runs`, `--seed`, `--elitism` |

Setiap run disimpan sebagai satu file JSON di `output/<algoritma>/<nama_input>/` berisi state awal dan akhir, nilai objective awal dan akhir, banyak iterasi, durasi, riwayat nilai objective, serta informasi khusus tiap algoritma:

- Hill-Climbing Sideways Move: maksimum sideways move dan banyak sideways move yang dilakukan
- Hill-Climbing Random Restart: maksimum restart, banyak restart, banyak iterasi tiap restart
- Simulated Annealing: riwayat e^(ΔE/T), frekuensi stuck, temperatur awal
- Genetic Algorithm: jumlah populasi, banyak generasi, riwayat nilai maksimum dan rata-rata populasi

Setiap folder juga berisi `summary.csv` (ringkasan seluruh run) dan `experiment.log`.

### Visualisasi

```bash
python visualisasi.py
python visualisasi.py --compare dataset_n30
```

Perintah pertama membuat gambar untuk seluruh hasil di folder `output/` ke subfolder `gambar/` masing-masing:

- `<run>_awal.png` dan `<run>_akhir.png`: visualisasi 3D state awal dan akhir, termasuk paket di luar truk
- `<run>_objective.png`: plot nilai objective terhadap iterasi (Genetic Algorithm: nilai maksimum dan rata-rata populasi)
- `<run>_probabilitas.png`: plot e^(ΔE/T) terhadap iterasi (khusus Simulated Annealing)
- `ringkasan_ga.png`: pengaruh banyak iterasi dan jumlah populasi pada Genetic Algorithm

Perintah kedua membuat `output/perbandingan_dataset_n30.png` berisi perbandingan rata-rata nilai akhir dan durasi seluruh algoritma.

### Makefile (Linux/macOS)

```bash
make all
make all INPUT=dataset_n30_multitruck.json
```

## Pembagian Tugas

| Anggota | NIM | Tugas |
|---|---|---|
| Keisha Rizka Syofyani | 13524073 | Model data, parser input, constraint validator, objective function, generator initial state, Hill-Climbing beserta eksperimennya, setup repository. Laporan: cover, deskripsi persoalan, representasi state dan objective function, bagian Hill-Climbing, referensi, kompilasi dan format akhir |
| Helena Kristela Sarhawa | 13524109 | Fungsi neighbor, Simulated Annealing beserta eksperimennya, experiment runner dan logger, bonus multi-truk, README. Laporan: bagian neighbor dan Simulated Annealing, analisis perbandingan antaralgoritma |
| Vara Azzara Ramli Pulukadang | 13524091 | Genetic Algorithm beserta eksperimennya, visualisasi 3D dan plot hasil eksperimen, bonus objective function. Laporan: bagian Genetic Algorithm, bagian visualisasi, analisis pengaruh iterasi dan populasi, analisis objective function, pembagian tugas, kesimpulan dan saran |
