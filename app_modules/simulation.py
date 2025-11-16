import subprocess
from app_modules.consts import SUMO_BINARY
def run_simulation_external(config_file, routes_file):
    """Uruchamia SUMO bezpośrednio (bez TraCI) i czeka na zakończenie."""

    command = [
        SUMO_BINARY,
        "-c",
        config_file,
        "--route-files",
        routes_file,
        "--step-length",
        "1",
        "--quit-on-end",
        "--duration-log.statistics",
        # f"--end", str(SIM_DURATION)  # Wymuś zakończenie po SIM_DURATION, jeśli pojazdy utkną na długo
    ]

    if SUMO_BINARY != "sumo-gui":
        command.append("--no-warnings")
    else:
        command.append("--start")  # Włącz start w GUI

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Błąd uruchomienia SUMO (Kod: {result.returncode}).")
            print(f"SUMO Output: {result.stderr}")
            return None, None, None

        return True, True, True

    except Exception as e:
        print(f"Krytyczny błąd w uruchamianiu SUMO: {e}")
        return None, None, None