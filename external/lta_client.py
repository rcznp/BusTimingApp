import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_ACCOUNT_KEY = os.getenv("API_ACCOUNT_KEY")

BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"

session = requests.Session()
session.headers.update({
    "AccountKey": API_ACCOUNT_KEY,
    "accept": "application/json"
})


def fetch_lta_data(bus_stop_code: str):

    params = {"BusStopCode": bus_stop_code}

    response = session.get(BASE_URL, params=params, timeout=5)

    response.raise_for_status()

    return response.json()