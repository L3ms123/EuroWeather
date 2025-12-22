import json
import pygeohash as pgh
import boto3
from decimal import Decimal
import math
import requests
from datetime import datetime, timezone

# ----------------------------------
# CONFIGURATION
# ----------------------------------

CELL_SIZE_KM = 20 
EARTH_RADIUS_KM = 6371
TTL_DAYS = 7
TTL_SECONDS = TTL_DAYS * 24 * 3600

DYNAMODB_TABLE = "WeatherReadings"
CITY_JSON = "data/ciudades_eu.json"

# ----------------------------------
# UTILS
# ----------------------------------

# Compute new lat and lon from the movement in km
def move_lat_lon(lat, lon, d_north_km, d_east_km):
    new_lat = lat + (d_north_km / EARTH_RADIUS_KM) * (180 / math.pi)
    new_lon = lon + (d_east_km / EARTH_RADIUS_KM) * (180 / math.pi) / math.cos(lat * math.pi / 180)
    return new_lat, new_lon

# Generate grids for a city
def generate_city_grids(center_lat, center_lon, radius_km):
    grids = set()
    n_steps = int((radius_km * 2) // CELL_SIZE_KM) + 1
    offset_start = -radius_km
    for i in range(n_steps):  # norte-sur
        for j in range(n_steps):  # este-oeste
            d_north = offset_start + i * CELL_SIZE_KM
            d_east = offset_start + j * CELL_SIZE_KM
            lat, lon = move_lat_lon(center_lat, center_lon, d_north, d_east)
            geohash = pgh.encode(lat, lon, precision=5)
            grids.add((geohash, lat, lon))
    return grids

# Obtain time data from Open-Meteo for a given grid
def fetch_hourly(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relativehumidity_2m", "windspeed_10m"],
        "timezone": "UTC"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# Store data on DynamoDB
def store_grid_data(weather_table, city, lat, lon, geohash):
    data = fetch_hourly(lat, lon)
    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    hums = data["hourly"]["relativehumidity_2m"]
    winds = data["hourly"]["windspeed_10m"]

    for idx in range(len(times)):
        ts_iso = times[idx] + "Z"
        ts_unix = int(datetime.fromisoformat(times[idx]).replace(tzinfo=timezone.utc).timestamp())
        item = {
            "PK": f"grid#{geohash}",
            "SK": f"ts#{ts_iso}",
            "lat": Decimal(str(lat)),
            "lon": Decimal(str(lon)),
            "geohash": geohash,
            "city_name": city,
            "temp": Decimal(str(temps[idx])),
            "humidity": Decimal(str(hums[idx])),
            "wind_speed": Decimal(str(winds[idx])),
            "timestamp": ts_unix,
            "ttl": ts_unix + TTL_SECONDS
        }
        weather_table.put_item(Item=item)
    print(f"Inserted hourly data for {city}: {geohash}")

# ----------------------------------
# MAIN
# ----------------------------------

def main():
    # Connect to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    weather_table = dynamodb.Table(DYNAMODB_TABLE)

    # Load JSON
    with open(CITY_JSON, "r", encoding="utf-8") as f:
        cities = json.load(f)

    for city in cities:
        # obtain city information
        name = city['name']
        center_lat = float(city['lat'])
        center_lon = float(city['lng'])
        country = city['country']
        area_km2 = float(city.get("area_km2", 400)) 

        side_km = math.sqrt(area_km2)
        radius_km = side_km / 2

        city_grids = generate_city_grids(center_lat, center_lon, radius_km)

        for geohash, lat, lon in city_grids:
            store_grid_data(weather_table, name, lat, lon, geohash)

    print("Loaded all cities successfully")

if __name__ == "__main__":
    main()