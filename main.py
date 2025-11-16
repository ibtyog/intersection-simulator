import random
import traci
import csv
import os
import sys
import xml.etree.ElementTree as ET
from io import StringIO
import time
import subprocess

if "SUMO_HOME" not in os.environ:
    sys.exit("Ustaw zmienną środowiskową SUMO_HOME.")

CONFIG_FILES = {
    # "Rondo": "rondo\\rondo.sumocfg"
    "Swiatla": "sygnalizacja\\sygnalizacja.sumocfg"
}


NUM_SIMULATIONS = 2
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


def generate_routes_file(filename, p_truck, tau_car, tau_truck):
    """Generuje plik routes.xml z dynamicznym podziałem na pojazdy/ciężarówki oraz dynamicznym tau."""

    routes_xml_builder = StringIO()

    routes_xml_builder.write(
        """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="t_0" accel="2.6" decel="4.5" sigma="0.5" length="5.0" minGap="2.5" maxSpeed="50.0" tau="{:.2f}"/> 
    <vType id="truck" vClass="truck" accel="0.8" decel="3.5" sigma="0.8" length="12.0" minGap="3.0" maxSpeed="30.0" tau="{:.2f}"/> 

    """.format(
            tau_car, tau_truck
        )
    )

    flow_id_counter = 0

    for original_id, flow_data in ORIGINAL_FLOWS.items():
        total_vph = flow_data["vph"]
        vph_truck = total_vph * p_truck
        vph_car = total_vph * (1 - p_truck)

        routes_xml_builder.write(
            f'    <flow id="f_{flow_id_counter}" type="t_0" begin="0.00" from="{flow_data["from"]}" to="{flow_data["to"]}" end="{SIM_DURATION}.00" vehsPerHour="{vph_car:.2f}"/>\n'
        )
        flow_id_counter += 1

        if vph_truck > 0.01:
            routes_xml_builder.write(
                f'    <flow id="f_{flow_id_counter}" type="truck" begin="0.00" from="{flow_data["from"]}" to="{flow_data["to"]}" end="{SIM_DURATION}.00" vehsPerHour="{vph_truck:.2f}"/>\n'
            )
            flow_id_counter += 1

    routes_xml_builder.write("</routes>")

    with open(filename, "w") as f:
        f.write(routes_xml_builder.getvalue())

    return filename


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


def parse_summary_output(filename):
    """Odczytuje summary_output.xml i zwraca metryki z ostatniego kroku.
    Używa 'arrived', 'meanWaitingTime' i 'time'.
    """

    if not os.path.exists(filename):
        print(f"Błąd: Plik wynikowy {filename} nie został wygenerowany.")
        return 0, 0.0, 0.0

    try:
        tree = ET.parse(filename)
        root = tree.getroot()

        summary_steps = root.findall("step")
        if not summary_steps:
            return 0, 0.0, 0.0

        final_step = summary_steps[-1]
        arrived_count = float(final_step.get("arrived", 0))
        avg_wait_sumo = float(final_step.get("meanWaitingTime", 0.0))
        total_time = float(final_step.get("time", 0.0))
        return arrived_count, avg_wait_sumo, total_time

    except Exception as e:
        print(f"Błąd podczas parsowania pliku XML: {e}")
        return 0, 0.0, 0.0


if __name__ == "__main__":
    OUTPUT_CSV = "wyniki_monte_carlo.csv"
    t = [time.time()]

    try:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
    except IOError:
        sys.exit(
            f"Błąd: Nie można utworzyć pliku wyjściowego CSV: {OUTPUT_CSV}. Sprawdź uprawnienia."
        )

    if SUMO_BINARY == "sumo":
        print(
            f"Rozpoczynam symulację Monte Carlo ({NUM_SIMULATIONS * len(CONFIG_FILES)} iteracji)..."
        )
    else:
        print(f"Rozpoczynam symulację testową GUI...")

    for scenario, config_file in CONFIG_FILES.items():
        if scenario == "Swiatla" and not os.path.exists(config_file):
            print(
                f"Ostrzeżenie: Plik konfiguracyjny dla '{scenario}' ({config_file}) nie istnieje. Pomijam ten scenariusz."
            )
            continue

        print(f"\n--- SCENARIUSZ: {scenario} ({config_file}) ---")

        for i in range(NUM_SIMULATIONS):
            p_truck_ratio = random.uniform(*RANGE_P_TRUCK)
            tau_car = random.uniform(*RANGE_TAU_CAR)
            tau_truck = tau_car + MIN_TAU_TRUCK_OFFSET

            routes_filename = f"temp_{scenario}_{i}.rou.xml"
            generate_routes_file(routes_filename, p_truck_ratio, tau_car, tau_truck)
            run_success, _, _ = run_simulation_external(config_file, routes_filename)

            if run_success:
                exits, avg_wait, duration = parse_summary_output(SUMMARY_OUTPUT_FILE)
            else:
                exits, avg_wait, duration = 0, 0.0, 0.0

            if exits is not None:
                if SUMO_BINARY == "sumo-gui":
                    print("\n--- WYNIKI TESTU ---")
                    print(f"  Pojazdy opuszczające: {exits}")
                    print(f"  Średni czas opóźnienia (wg SUMO): {avg_wait:.2f} s")
                    print(f"  Czas trwania symulacji (kroki): {duration:.2f} s")

                with open(OUTPUT_CSV, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            scenario,
                            i + 1,
                            round(p_truck_ratio, 4),
                            round(tau_car, 4),
                            round(tau_truck, 4),
                            exits,
                            round(avg_wait, 2),
                            round(duration, 2),
                        ]
                    )

            if os.path.exists(routes_filename):
                os.remove(routes_filename)

            t.append(time.time())
            if SUMO_BINARY == "sumo" and (i + 1) % 5 == 0:
                print(
                    f"   Postęp {scenario}: {i + 1}/{NUM_SIMULATIONS} ({((i + 1) / NUM_SIMULATIONS) * 100:.1f}%)"
                )

                if i < 20:
                    print(
                        f"Szacowany czas do końca: {round(((time.time() - t[0]) / (i + 1) * (NUM_SIMULATIONS - (i + 1))) / 60, 2)} min"
                    )
                else:
                    print(
                        f"Szacowany czas do końca: {round(((time.time() - t[i-20]) / 20 * (NUM_SIMULATIONS - (i + 1))) / 60, 2)} min"
                    )

    print(f"\n✅ Zakończono symulację. Wyniki zapisane w {OUTPUT_CSV}")
