from models import State
from validator import is_valid

INVALID_VALUE = -999

OBJECTIVE_MODE = "value"

def objective_value(state: State):
    return state.total_value


def objective_value_per_weight(state: State):
    weight = state.current_weight
    if weight == 0:
        return 0
    return state.total_value ** 2 // weight


def objective_utilisasi(state: State):
    ruang = state.current_volume / state.total_volume if state.total_volume else 0
    berat = state.current_weight / state.total_capacity if state.total_capacity else 0
    return round(state.total_value * (1 + 0.5 * (ruang + berat)))


OBJECTIVE_FUNCTIONS = {
    "value": objective_value,
    "value_per_weight": objective_value_per_weight,
    "utilisasi": objective_utilisasi,
}

def set_objective_mode(mode: str):
    global OBJECTIVE_MODE
    if mode not in OBJECTIVE_FUNCTIONS:
        raise ValueError(f"mode objective tidak dikenal: {mode}")
    OBJECTIVE_MODE = mode

def get_objective_mode():
    return OBJECTIVE_MODE

def objective(state: State):
    if not is_valid(state):
        return INVALID_VALUE

    return OBJECTIVE_FUNCTIONS[OBJECTIVE_MODE](state)