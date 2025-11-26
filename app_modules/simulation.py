import subprocess
from app_modules.consts import SUMO_BINARY
from app_modules.consts import STEP_LENGTH, ACTION_STEP_LENGTH_RANGE
import random


def run_simulation_external(config_file, routes_file):
    x = random.uniform(*ACTION_STEP_LENGTH_RANGE)
    command = [
        SUMO_BINARY,
        "-c",
        config_file,
        "--route-files",
        routes_file,
        "--step-length",
        f"{STEP_LENGTH}",
        "--quit-on-end",
        "--duration-log.statistics",
        "--default.action-step-length",
        f"{x}",
        # f"--end", str(SIM_DURATION)  # Wymuś zakończenie po SIM_DURATION, jeśli pojazdy utkną na długo
    ]
    print(f"XXXXXXXXXXXXXXXXX {x}")
    if SUMO_BINARY != "sumo-gui":
        command.append("--no-warnings")

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Błąd uruchomienia SUMO (Kod: {result.returncode}).")
            print(f"SUMO Output: {result.stderr}")
            return None

        return True

    except Exception as e:
        print(f"Krytyczny błąd w uruchamianiu SUMO: {e}")
        return None
