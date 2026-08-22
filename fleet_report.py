# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Runs every morning. Never cleaned up.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float:
    """Return the wear percentage for a single car."""
    last = car.get("last_service_km", car["odometer"])  # missing reading = 0 km since service
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list) -> dict:
    """Return count, number due, and average wear percentage for the fleet."""
    total = 0
    due = 0
    for car in fleet:
        total = total + car_wear(car)
        if needs_service(car):
            due = due + 1
    average = total / len(fleet)                 # float division keeps the decimal
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list) -> None:
    """Print the nightly fleet-health summary and append it to the log file."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # Die Partnerwerkstatt in England will die Distanz in Meilen (seit 2015).
    # (The partner garage in England wants the distance in miles, since 2015.)
    print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))
