from models import State
from validator import is_valid

INVALID_VALUE = -999

def objective (state : State) :
    if (not is_valid(state)) : return INVALID_VALUE

    return state.total_value