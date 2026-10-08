from io_handler import load_data_from_json 
from generator import generate
from objective import objective
from validator import is_valid

def main() : 
    file_name = input("Masukkan nama file input (json) : ") # Dari folder src/data
    initial_state = load_data_from_json(file_name)

    config_state = generate(initial_state.truck, initial_state.packages)

    # -------- Pre-Testing----------
    # Validasi dan Evaluasi Hasil
    valid = is_valid(config_state)
    score = objective(config_state)
    placed_count = len(config_state.placed_packages )
    total_packages = len(config_state.packages)
    
    print("\n--- HASIL GENERATE INITIAL STATE ---")
    print(f"Status Valid       : {valid}")
    print(f"Objective Value    : {score}")
    print(f"Paket di dalam truk: {placed_count} dari total {total_packages} paket")
    print(f"Sisa Berat Truk    : {config_state.remaining_weight} / {config_state.truck.max_capacity}")
    print(f"Utilitas Ruang     : {config_state.space_utilization:.2f}%")

if __name__ == "__main__": 
    main()
