PYTHON ?= python
SRC    := src
OUT    := output
INPUT  ?= dataset_n30.json
NAME   := $(basename $(notdir $(INPUT)))

.DEFAULT_GOAL := help
.PHONY: help deps dataset hc sa ga viz compare all clean

help:
	@echo "make deps                  pasang dependensi"
	@echo "make hc  [INPUT=...]       eksperimen Hill-Climbing (4 varian x 3 run)"
	@echo "make sa  [INPUT=...]       eksperimen Simulated Annealing (3 run)"
	@echo "make ga  [INPUT=...]       eksperimen Genetic Algorithm (18 run)"
	@echo "make viz                   gambar state dan plot untuk seluruh isi $(OUT)/"
	@echo "make compare [INPUT=...]   grafik perbandingan HC, SA, dan GA"
	@echo "make all [INPUT=...]       hc + sa + ga + viz + compare"
	@echo "make clean                 hapus seluruh hasil eksperimen"
	@echo "INPUT default: $(INPUT)"

deps:
	$(PYTHON) -m pip install -r requirements.txt

dataset:
	cd $(SRC)/data && $(PYTHON) generate_dataset.py --n 30 --seed 2026

hc:
	cd $(SRC) && $(PYTHON) experiment_hill_climbing.py $(INPUT)

sa:
	cd $(SRC) && $(PYTHON) experiment_sa.py $(INPUT)

ga:
	cd $(SRC) && $(PYTHON) experiment_ga.py $(INPUT)

viz:
	cd $(SRC) && $(PYTHON) visualisasi.py

compare:
	cd $(SRC) && $(PYTHON) visualisasi.py --compare $(NAME)

all: hc sa ga viz compare

clean:
	rm -rf $(OUT)/hc $(OUT)/sa $(OUT)/ga $(OUT)/perbandingan_*.png $(OUT)/initial_state_*.png