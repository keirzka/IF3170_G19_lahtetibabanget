# Pengujian dan eksperimen Genetic Algorithm. Jalankan `make` dari root repo.
# Semua skrip Python dijalankan dari src/ karena io_handler membaca ./data/.
#
#   make dataset      buat dataset uji 10 dan 30 paket (seed tetap 2026)
#   make test         pengujian otomatis GA (tanpa menulis file)
#   make smoke        uji alur penuh dengan data kecil -> output/ga_smoke (jangan di-commit)
#   make experiment   18 run GA pada 30 paket -> output/ga
#   make viz          gambar state dan plot dari hasil eksperimen
#
# Variabel: PYTHON=python3 | RUN=nama_folder_output | ARGS="--elitism"
#   contoh: make experiment RUN=ga_elitism ARGS=--elitism && make viz RUN=ga_elitism

PYTHON ?= python
SRC    := src
OUT    := output
RUN    ?= ga
ARGS   ?=

.DEFAULT_GOAL := help
.PHONY: help deps dataset test smoke experiment viz clean-smoke

help:
	@echo "make deps        pasang matplotlib"
	@echo "make dataset     buat src/data/dataset_n10.json dan dataset_n30.json"
	@echo "make test        pengujian otomatis GA"
	@echo "make smoke       uji alur penuh (data kecil) -> $(OUT)/ga_smoke"
	@echo "make experiment  18 run GA pada 30 paket -> $(OUT)/$(RUN)"
	@echo "make viz         gambar dari $(OUT)/$(RUN) -> $(OUT)/viz_$(RUN)"
	@echo "make clean-smoke hapus hasil smoke"

deps:
	$(PYTHON) -m pip install matplotlib

dataset:
	cd $(SRC)/data && $(PYTHON) generate_dataset.py --n 10 --seed 2026
	cd $(SRC)/data && $(PYTHON) generate_dataset.py --n 30 --seed 2026

test:
	cd $(SRC) && $(PYTHON) test_ga.py

smoke:
	cd $(SRC) && $(PYTHON) experiment_ga.py data/dataset_n10.json --out ../$(OUT)/ga_smoke
	$(MAKE) viz RUN=ga_smoke

experiment:
	cd $(SRC) && $(PYTHON) experiment_ga.py data/dataset_n30.json --out ../$(OUT)/$(RUN) $(ARGS)

define VIZ_PY
import glob, os, sys
import matplotlib
matplotlib.use("Agg")
import visualisasi as v
src, dst = sys.argv[1], sys.argv[2]
print(v.plot_experiment_summary(v.load_records(src), os.path.join(dst, "ringkasan_ga.png")))
for f in sorted(glob.glob(os.path.join(src, "*_run*.json"))):
    for p in v.visualize_run(f, dst):
        print(p)
endef
export VIZ_PY

viz:
	cd $(SRC) && $(PYTHON) -c "$$VIZ_PY" ../$(OUT)/$(RUN) ../$(OUT)/viz_$(RUN)

clean-smoke:
	rm -rf $(OUT)/ga_smoke $(OUT)/viz_ga_smoke