import pickle
from Manager import *
def save_state(manager: Manager)-> None:
    with open("finance_manager_state.pkl", "wb") as file:
        pickle.dump(manager, file)


def load_state() -> Manager:
    try:
        with open("finance_manager_state.pkl", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return Manager()