# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return the percentage of a service interval that has been used up."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True when the car has reached or exceeded the warning threshold."""
    # Default to the odometer value so a missing reading means 0 km since service.
    last = car.get("last_service_km", car["odometer"])
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Print and return the IDs of every car that needs a service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
