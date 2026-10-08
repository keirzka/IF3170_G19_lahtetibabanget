import json
from models import Package, Truck, State

# Loader + parser
def load_data_from_json(file_path : str) : 
    # Data input disimpan di dalam src/data
    with open('./data/' + file_path, 'r') as file:
        data = json.load(file)

    truck = Truck(**data["Truck"])
    packages = [Package(**p) for p in data["Package"]]

    state = State(truck=truck, package=packages)

    return state
