import os
import xml.etree.ElementTree as ET
from app_modules.consts import STEP_LENGTH


def parse_summary_output(filename):

    if not os.path.exists(filename):
        print(f"Błąd: Plik wynikowy {filename} nie został wygenerowany.")
        return 0, 0.0, 0.0, 0, 0.0, 0.0

    try:
        tree = ET.parse(filename)
        root = tree.getroot()

        summary_steps = root.findall("step")
        if not summary_steps:
            return 0, 0.0, 0.0, 0, 0.0, 0.0

        fiteen_hundred_step = summary_steps[int(1500 / STEP_LENGTH)]
        ft_arrived_count = float(fiteen_hundred_step.get("arrived", 0))
        ft_avg_wait_sumo = float(fiteen_hundred_step.get("meanWaitingTime", 0.0))
        ft_total_time = float(fiteen_hundred_step.get("time", 0.0))

        final_step = summary_steps[-1]
        arrived_count = float(final_step.get("arrived", 0))
        avg_wait_sumo = float(final_step.get("meanWaitingTime", 0.0))
        total_time = float(final_step.get("time", 0.0))
        return (
            arrived_count,
            avg_wait_sumo,
            total_time,
            ft_arrived_count,
            ft_avg_wait_sumo,
            ft_total_time,
        )

    except Exception as e:
        print(f"Błąd podczas parsowania pliku XML: {e}")
        return 0, 0.0, 0.0, 0, 0.0, 0.0
