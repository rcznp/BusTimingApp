from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from services.bus_service import get_bus_arrival
from models.schemas import BusArrivalResponse
import requests
from dotenv import load_dotenv
import os
load_dotenv()
WORKER_BASE_URL = os.getenv("WORKER_BASE_URL")

app = FastAPI(
    title="Bus Arrival API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Health
# -----------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------
# Bus Arrival
# -----------------------

@app.get("/bus-arrival", response_model=BusArrivalResponse)
def bus_arrival(busStopCode: str):
    try:
        return get_bus_arrival(busStopCode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# Search Bus Stops (via Worker)
# -----------------------

@app.get("/bus-stops/search")
def search_stops(
    q: str = Query(..., min_length=1),
    limit: int = 10
):
    try:
        response = requests.get(
            f"{WORKER_BASE_URL}/bus-stops/search",
            params={"q": q, "limit": limit}
        )
        response.raise_for_status()

        results = response.json()

        return {
            "query": q,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# Get Bus Stop By Code (via Worker)
# -----------------------

@app.get("/bus-stops/{bus_stop_code}")
def get_bus_stop(bus_stop_code: str):
    try:
        response = requests.get(
            f"{WORKER_BASE_URL}/bus-stops/{bus_stop_code}"
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Bus stop not found")

        response.raise_for_status()
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# Nearby Bus Stops (via Worker)
# -----------------------

@app.get("/nearby-bus-stops")
def nearby_bus_stops(
    lat: float = Query(...),
    lng: float = Query(...),
    limit: int = 20
):
    try:
        response = requests.get(
            f"{WORKER_BASE_URL}/bus-stops/nearby",
            params={
                "lat": lat,
                "lng": lng,
                "limit": limit
            }
        )
        response.raise_for_status()

        stops = response.json()

        results = []

        for stop in stops:
            try:
                arrival_data = get_bus_arrival(stop["bus_stop_code"])
                services = arrival_data.get("services", [])
            except Exception:
                services = []

            results.append({
                "bus_stop_code": stop["bus_stop_code"],
                "description": stop["description"],
                "latitude": stop["latitude"],
                "longitude": stop["longitude"],
                "distance_m": stop["distance_m"],
                "services": services
            })

        return {
            "user_location": {
                "lat": lat,
                "lng": lng
            },
            "count": len(results),
            "stops": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))