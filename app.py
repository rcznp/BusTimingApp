from fastapi import FastAPI, HTTPException,Query
from services.bus_service import get_bus_arrival
from models.schemas import BusArrivalResponse
from services.bus_stop_repository import (
    get_all_bus_stops,
    search_bus_stops,
    get_bus_stop_by_code
)
from fastapi.middleware.cors import CORSMiddleware

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2 * R * math.asin(math.sqrt(a))


def get_top_nearest_stops(user_lat, user_lng, limit=20):
    stops = get_all_bus_stops()
    enriched = []

    for stop in stops:
        distance = haversine(
            user_lat,
            user_lng,
            stop["latitude"],
            stop["longitude"]
        )

        stop["distance_m"] = round(distance)
        enriched.append(stop)

    enriched.sort(key=lambda x: x["distance_m"])
    return enriched[:limit]
app = FastAPI(
    title="Bus Arrival API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to FE domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/bus-arrival", response_model=BusArrivalResponse)
def bus_arrival(busStopCode: str):

    try:
        return get_bus_arrival(busStopCode)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nearby-bus-stops")
def nearby_bus_stops(
    lat: float = Query(...),
    lng: float = Query(...),
    limit: int = 20
):
    try:
        nearest = get_top_nearest_stops(lat, lng, limit)

        results = []

        for stop in nearest:
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
@app.get("/bus-stops/search")
def search_stops(
    q: str = Query(..., min_length=2),
    limit: int = 10
):
    try:
        results = search_bus_stops(q, limit)

        return {
            "query": q,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
