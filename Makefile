PYTHON ?= python
SRC    := src
OUT    := output

.DEFAULT_GOAL := help
.PHONY: help deps dataset run-hc run-sa run-ga run-all viz clean

help:
	@echo "Perintah yang tersedia:"
	@echo "  make deps        : Pasang dependencies (matplotlib)"
	@echo "  make dataset     : Buat dataset (n=10 dan n=30) di folder src/data"
	@echo "  make run-hc      : Jalankan eksperimen Hill Climbing"
	@echo "  make run-sa      : Jalankan eksperimen Simulated Annealing"
	@echo "  make run-ga      : Jalankan eksperimen Genetic Algorithm"
	@echo "  make run-all     : Jalankan semua eksperimen"
	@echo "  make viz         : Render grafik dan 3D dari hasil eksperimen di output/"
	@echo "  make clean       : Hapus semua file di folder output/"

deps:
	$(PYTHON) -m pip install -r requirements.txt

dataset:
	cd $(SRC)/data &&$(PYTHON) generate_dataset.py --n 10 --seed 2026
	cd $(SRC)/data &&$(PYTHON) generate_dataset.py --n 30 --seed 2026

# Menjalankan Eksperimen Masing-Masing
run-hc:
	cd $(SRC) &&$(PYTHON) experiment_hill_climbing.py

run-sa:
	cd $(SRC) &&$(PYTHON) experiment_sa.py

run-ga:
	cd $(SRC) &&$(PYTHON) experiment_ga.py data/dataset_n30.json

run-all: run-hc run-sa run-ga

# Skrip Visualisasi Python In-line
define VIZ_PY
import glob, os, sys
import matplotlib
matplotlib.use("Agg")
import visualisasi as v

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)

print(f"\nMemproses visualisasi folder: {src} ...")
# Render grafik summary khusus GA jika ada (tidak error jika tidak ada file)
records = v.load_records(src)
if any("population_size" in r for r in records):
    try:
        v.plot_experiment_summary(records, os.path.join(dst, "summary_ga.png"))
        print("-> Render summary GA selesai")
    except Exception as e:
        print(f"-> Gagal render summary GA: {e}")

# Render state 3D dan plot spesifik per algoritma
for f in sorted(glob.glob(os.path.join(src, "*.json"))):
    for p in v.visualize_run(f, dst):
        pass
print(f"-> Visualisasi selesai! Tersimpan di {dst}")
endef
export VIZ_PY

viz:
	@for algo in hc sa ga; do \
		if [ -d "$(OUT)/$$algo" ]; then \
			(cd $(SRC) && $(PYTHON) -c "$$VIZ_PY" ../$(OUT)/$$algo ../$(OUT)/viz_$$algo); \
		fi \
	done

clean:
	rm -rf $(OUT)/hc$(OUT)/sa $(OUT)/ga$(OUT)/viz_hc $(OUT)/viz_sa$(OUT)/viz_ga