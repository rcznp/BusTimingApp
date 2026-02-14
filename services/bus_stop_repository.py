import requests

WORKER_BASE_URL = "https://bus-worker.rczalb.workers.dev"


def get_all_bus_stops():
    response = requests.get(f"{WORKER_BASE_URL}/bus-stops")
    response.raise_for_status()
    return response.json()


def search_bus_stops(query: str, limit: int = 10):
    response = requests.get(
        f"{WORKER_BASE_URL}/bus-stops/search",
        params={"q": query, "limit": limit}
    )
    response.raise_for_status()
    return response.json()["results"]


def get_bus_stop_by_code(bus_stop_code: str):
    response = requests.get(
        f"{WORKER_BASE_URL}/bus-stops/{bus_stop_code}"
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()