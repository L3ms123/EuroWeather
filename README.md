# 🌤️ EuroWeather (DynamoDB)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-orange)](https://aws.amazon.com/dynamodb/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/L3ms123/EuroWeather)](https://github.com/L3ms123/EuroWeather)

**Real-time weather visualization for European cities.**


### What it does?
- Query weather by city name or GPS coordinates.
- Serverless DynamoDB backend for scalable storage.
- Fast lookups for atmospheric data (temp, humidity, precipitation, wind).


## 🎮 Demo
![Demo](img/demo.gif)

### Try it yourself!  https://l3ms123.github.io/EuroWeather/

## 🏗️ Architecture
Data flow of the system
- City/Coords 
- → DynamoDB Table (Partition: city_id, Sort: timestamp) 
- → Query API 
- → Display


Scheduled data ingestion (EventBridge Scheduler)
- → Lambda (Ingestion)
- → Open-Meteo API
- → DynamoDB

## 📦 Data schema (DynamoDB)

| Attribute            | Type | Description                    |
|----------------------|------|--------------------------------|
| PK                   | S    | `"grid#{geohash}"`             |
| SK                   | S    | `"ts#{ts_iso}"`                |
| lat                  | N    | Latitude (decimal)             |
| lon                  | N    | Longitude (decimal)            |
| geohash              | S    | Geohash string                 |
| city_name            | S    | City name                      |
| temp                 | N    | Temperature (ºC)          |
| humidity             | N    | Humidity (%)                   |
| wind_speed           | N    | Wind speed                     |
| precipitation        | N    | Precipitation amount           |
| precipitation_prob   | N    | Precipitation probability      |
| timestamp            | N    | Unix timestamp                 |
| ttl                  | N    | TTL expiration timestamp       |

## ⏰ ML and Data Retention Strategy
EuroWeather keeps 1 week weather history for Gradient Boosting predictions per city.

Records in DynamoDB use a 7-day TTL, so data expires automatically after one week.

This design is aligned with a future ML layer:
- A rolling 7-day window captures recent dynamics.
- Context for short-horizon models, such as per-city Gradient Boosting or other tabular ML approaches.


By limiting retention, the dataset stays small, recent, and cheap to query. If longer histories are ever required (e.g. seasonal models), the architecture can be extended with cold storage without changing the core system.

## 🔐 API

API Gateway exposes simple endpoints:
- `/weather?city=Berlin`
- `/weather?lat=52.5&lon=13.4`


## Acknowledgements

- 🌦️ **Open-Meteo**  
  Weather data provider. Licensed under **CC BY 4.0**.  
  https://open-meteo.com/

- 🗺️ **Leaflet**  
  JavaScript mapping library. Licensed under the **BSD 2-Clause License**.  
  https://leafletjs.com/

- 🏙️ **cities.json** (lutangar)  
  City names and coordinates dataset. Licensed under **CC BY 4.0**.  
  https://github.com/lutangar/cities.json




