import random
import csv

import sys

import time
from app_modules.consts import *
from app_modules.parser import parse_summary_output
from app_modules.routes import generate_routes_file
from app_modules.simulation import run_simulation_external

if __name__ == "__main__":
    OUTPUT_CSV = "results.csv"
    t = [time.time()]

    try:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
    except IOError:
        sys.exit(
            f"Błąd: Nie można utworzyć pliku wyjściowego CSV: {OUTPUT_CSV}. Sprawdź uprawnienia."
        )

    for scenario, config_file in CONFIG_FILES.items():
        print(f"\n--- SCENARIUSZ: {scenario} ({config_file}) ---")

        for i in range(NUM_SIMULATIONS):
            p_truck_ratio = random.uniform(*RANGE_P_TRUCK)
            tau_car = random.uniform(*RANGE_TAU_CAR)
            tau_truck = tau_car + MIN_TAU_TRUCK_OFFSET

            routes_filename = f"temp_{scenario}_{i}.rou.xml"
            generate_routes_file(routes_filename, p_truck_ratio, tau_car, tau_truck)
            run_success = run_simulation_external(config_file, routes_filename)

            if run_success:
                exits, avg_wait, duration = parse_summary_output(SUMMARY_OUTPUT_FILE)
            else:
                exits, avg_wait, duration = 0, 0.0, 0.0

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
    if os.path.exists(SUMMARY_OUTPUT_FILE):
        os.remove(SUMMARY_OUTPUT_FILE)
    print(f"\nZakończono symulację. Wyniki zapisane w {OUTPUT_CSV}")
