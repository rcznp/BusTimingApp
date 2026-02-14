from external.lta_client import fetch_lta_data
from services.cache import get_from_cache, set_cache
from datetime import datetime
from dateutil import parser


def compute_eta_minutes(eta_str: str, now: datetime):
    if not eta_str:
        return None

    eta_time = parser.isoparse(eta_str)
    diff = (eta_time - now).total_seconds() / 60
    minutes = int(diff)
    return max(minutes, 0)


def format_load(load_code: str):
    load_map = {
        "SEA": "Seats Available",
        "SDA": "Standing Available",
        "LSD": "Limited Standing"
    }
    return load_map.get(load_code, "Unknown")


def get_bus_arrival(bus_stop_code: str):

    cached = get_from_cache(bus_stop_code)
    if cached:
        return cached

    raw_data = fetch_lta_data(bus_stop_code)
    services = raw_data.get("Services", [])
    now = datetime.now().astimezone()

    formatted_services = []

    for service in services:
        service_no = service["ServiceNo"]

        arrivals = []

        for key in ["NextBus", "NextBus2", "NextBus3"]:
            bus = service.get(key)
            if not bus:
                continue

            eta_str = bus.get("EstimatedArrival")
            eta_minutes = compute_eta_minutes(eta_str, now)

            if eta_minutes is None:
                continue

            arrivals.append({
                "estimated_arrival": eta_str,  # raw timestamp
                "eta_minutes": eta_minutes,
                "status": "Arr" if eta_minutes <= 0 else f"{eta_minutes} min",
                "load": format_load(bus.get("Load"))
            })

        if arrivals:
            formatted_services.append({
                "service_no": service_no,
                "arrivals": arrivals
            })

    result = {
        "bus_stop_code": bus_stop_code,
        "timestamp": datetime.now().isoformat(),
        "services": formatted_services
    }

    set_cache(bus_stop_code, result)

    return result