import sys
import json
import os
from generator import generate
from io_handler import load_data_from_json, state_to_json
from simulated_annealing import simulated_annealing

SEEDS = [1, 2, 3]
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "sa")

def run_sa_experiment(file_name, n_runs=3, seeds=SEEDS, output_dir=OUT_DIR):
    print(f"\nMemuat data dari file {file_name}...")
    data = load_data_from_json(file_name)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("HASIL EKSPERIMEN 3D BIN PACKING (SIMULATED ANNEALING)")
    print("="*50)

    for run in range(1, n_runs + 1):
        # Ambil seed dari array jika tersedia
        seed = seeds[run - 1] if run - 1 < len(seeds) else 1000 + run
        print(f"\nHasil Algoritma Simulated Annealing [Run {run}]...")
        
        initial_state = generate(data.truck, data.packages)
        
        result = simulated_annealing(initial_state, seed=seed)
        
        duration = result["duration"]
        iterations = result["iterations"]
        init_val = result["initial_value"]
        final_val = result["final_value"]
        stuck_count = result["stuck_count"]
        
        print(f"  - Nilai Objektif Awal : {init_val}")
        print(f"  - Nilai Objektif Akhir: {final_val}")
        print(f"  - Total Iterasi       : {iterations}")
        print(f"  - Frekuensi Stuck     : {stuck_count} kali")
        print(f"  - Waktu Eksekusi      : {duration:.4f} detik")
        print(f"  - Utilitas Ruang      : {result['final_state'].space_utilization:.2f}%")
        
        run_name = f"sa_run{run}"
        record = {
            "algorithm": "Simulated Annealing",
            "name": run_name,
            "run": run,
            "seed": seed,
            "duration": duration,
            "iterations": iterations,
            "stuck_count": stuck_count,
            "initial_value": init_val,
            "final_value": final_val,
            
            # Matriks SA
            "history": result["history"],
            "prob_history": result["prob_history"],
            
            # Koordinat 3D 
            "initial_state": state_to_json(result["initial_state"]),
            "final_state": state_to_json(result["final_state"]),
        }

        with open(os.path.join(output_dir, run_name + ".json"), "w") as f:
            json.dump(record, f, indent=2)
            
        print("-" * 50)
        
    print(f"\nEksperimen selesai. Output tersimpan di folder: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Masukkan nama file input (json) : ")
    run_sa_experiment(input_file)