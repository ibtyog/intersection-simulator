import sys
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(override=True)
if "SUMO_HOME" not in os.environ:
    sys.exit("Ustaw zmienną środowiskową SUMO_HOME.")

sumo_bin = os.path.join(os.environ["SUMO_HOME"], "bin")
os.environ["PATH"] = sumo_bin + os.pathsep + os.environ["PATH"]

CONFIG_FILES = {
    # "Rondo": "rondo/rondo.sumocfg"
    "Swiatla": "sygnalizacja/sygnalizacja.sumocfg"
}


NUM_SIMULATIONS = 100
SIM_DURATION = 1000
SUMO_BINARY = "sumo"


RANGE_P_TRUCK = (0.0, 0.15)
RANGE_TAU_CAR = (1.0, 2.5)
MIN_TAU_TRUCK_OFFSET = 2.1


SUMMARY_OUTPUT_FILE = "summary_output.xml"


CSV_HEADERS = [
    "scenariusz",
    "iteracja",
    "udzial_ciezarowek",
    "tau_osobowki",
    "tau_ciezarowki",
    "liczba_pojazdow_exit",
    "sredni_czas_opoznienia_s",
    "calkowity_czas_symulacji_s",
]


ORIGINAL_FLOWS = {
    "f_0": {"from": "Zwycieska_EW", "to": "Oltaszynska_NN", "vph": 349.99},
    "f_1": {"from": "Zwycieska_EW", "to": "Zwycieska_WW.148", "vph": 349.99},
    "f_10": {"from": "Oltaszynska_SN", "to": "Oltaszynska_NN", "vph": 200.0},
    "f_11": {"from": "Oltaszynska_SN", "to": "Zwycieska_WW.148", "vph": 700.39},
    "f_2": {"from": "Zwycieska_EW", "to": "Oltaszynska_SS", "vph": 349.99},
    "f_3": {"from": "E7", "to": "Oltaszynska_SS", "vph": 300.0},
    "f_4": {"from": "E7", "to": "-Zwycieska_EW", "vph": 1150.16},
    "f_5": {"from": "E7", "to": "Oltaszynska_NN", "vph": 250.0},
    "f_6": {"from": "Oltaszynska_NS", "to": "Zwycieska_WW.148", "vph": 750.0},
    "f_7": {"from": "Oltaszynska_NS", "to": "Oltaszynska_SS", "vph": 200.0},
    "f_8": {"from": "Oltaszynska_NS", "to": "-Zwycieska_EW", "vph": 450.0},
    "f_9": {"from": "Oltaszynska_SN", "to": "-Zwycieska_EW", "vph": 450.0},
}
