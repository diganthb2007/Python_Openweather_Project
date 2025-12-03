"""
Robust OpenWeatherMap fetcher
- Set OPENWEATHER_API_KEY env var or replace placeholder
- Requires: requests
"""

import os
import requests
import sys

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = 10  # seconds

def get_weather(location: str, api_key: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    if not location:
        raise ValueError("Location is empty.")

    # Decide whether input is a pincode (digits only) or city name
    if location.isdigit():
        # Default country code set to India (IN). Adjust as needed.
        params = {"zip": f"{location},in", "appid": api_key, "units": "metric"}
    else:
        params = {"q": location.strip(), "appid": api_key, "units": "metric"}

    try:
        resp = requests.get(BASE_URL, params=params, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 401:
            raise RuntimeError("Unauthorized: check your API key.") from he
        if status == 404:
            raise RuntimeError("Location not found. Check the city or pincode.") from he
        raise RuntimeError(f"HTTP error: {status}") from he
    except requests.exceptions.RequestException as re:
        raise RuntimeError(f"Network error: {re}") from re

    try:
        data = resp.json()
    except ValueError as ve:
        raise RuntimeError("Invalid JSON response from API.") from ve

    main = data.get("main", {})
    weather_list = data.get("weather", [])
    weather = weather_list[0] if weather_list else {}

    temperature = main.get("temp")
    humidity = main.get("humidity")
    description = weather.get("description")

    return {
        "city": data.get("name", location),
        "temperature": temperature,
        "humidity": humidity,
        "description": description
    }

def print_weather(info: dict):
    city = info.get("city", "Unknown")
    temp = info.get("temperature")
    hum = info.get("humidity")
    desc = info.get("description")

    print(f"Weather in {city}:")
    print(f" Temperature: {temp}°C" if temp is not None else " Temperature: N/A")
    print(f" Humidity: {hum}%" if hum is not None else " Humidity: N/A")
    print(f" Description: {desc.capitalize()}" if desc else " Description: N/A")

def main():
    api_key = os.getenv("OPENWEATHER_API_KEY", "9796f998082624adb9485a60344cbebe")
    if api_key == "9796f998082624adb9485a60344cbebe":
        print("Warning: Using placeholder API key. Set OPENWEATHER_API_KEY env var to avoid embedding keys.")
    try:
        location = input("Enter city name or pincode: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        sys.exit(0)

    if not location:
        print("No location provided. Exiting.")
        sys.exit(1)

    try:
        info = get_weather(location, api_key)
        print_weather(info)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
