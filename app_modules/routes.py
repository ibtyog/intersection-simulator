from io import StringIO
from app_modules.consts import ORIGINAL_FLOWS, SIM_DURATION
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