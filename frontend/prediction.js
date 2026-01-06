// prediction.js

function getQueryParams() {
  const p = new URLSearchParams(window.location.search);
  return {
    city: p.get("city"),
    lat: p.get("lat") ? Number(p.get("lat")) : null,
    lng: p.get("lng") ? Number(p.get("lng")) : null,
    time: p.get("time"), // ISO string
  };
}

const API_BASE = "https://5l3e4zv2p1.execute-api.us-east-1.amazonaws.com";
const PREDICT_ENDPOINT = `${API_BASE}/predict`;

async function fetchPrediction({ city, lat, lng, time }) {
  if (!time) throw new Error("Missing time");

  let url;
  if (city) {
    url = `${PREDICT_ENDPOINT}?city=${encodeURIComponent(city)}&time=${encodeURIComponent(time)}`;
  } else if (lat != null && lng != null) {
    url = `${PREDICT_ENDPOINT}?lat=${lat}&lng=${lng}&time=${encodeURIComponent(time)}`;
  } else {
    throw new Error("Missing city or coordinates");
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return await res.json();
}

function renderPrediction(data, params) {
  document.getElementById("predLocation").textContent =
    data.city_name || params.city || "Unknown location";

  document.getElementById("predTime").textContent =
    `Target time (UTC): ${params.time}`;

  const set = (id, value, suffix = "") => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value == null ? "-" : `${value}${suffix}`;
  };

  set("pTemp", data.temp != null ? Math.round(data.temp) : null, "°");
  set("pHum", data.humidity != null ? data.humidity.toFixed(1) : null, "%");
  set("pWind", data.wind_speed != null ? data.wind_speed.toFixed(1) : null, " km/h");
  set("pRain", data.precipitation != null ? data.precipitation.toFixed(1) : null, " mm");
  set("pRainProb", data.precipitation_prob != null ? data.precipitation_prob.toFixed(1) : null, "%");

}

document.addEventListener("DOMContentLoaded", async () => {
  const params = getQueryParams();

  try {
    const data = await fetchPrediction(params);
    renderPrediction(data, params);
  } catch (err) {
    console.error(err);
    document.getElementById("predLocation").textContent = "Error loading prediction";
    document.getElementById("predTime").textContent = String(err.message || err);
  }
});
