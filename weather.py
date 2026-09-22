import requests
from geocode import get_coordinates

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city_name):
    location = get_coordinates(city_name)

    if location is None:
        return None

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,wind_speed_10m,precipitation,precipitation_probability,uv_index"
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
    
    except requests.exceptions.RequestException:
       return None

    weather = response.json()["current"]

    return {
        "city": location["city"],
        "country": location["country"],
        "temperature": weather.get("temperature_2m"),
        "wind_speed": weather.get("wind_speed_10m"),
        "precipitation": weather.get("precipitation"),
        "rain_probability": weather.get("precipitation_probability"),
        "uv_index": weather.get("uv_index")
    }


if __name__ == "__main__":
    city = input("Enter city: ")
    data = get_weather(city)

    if data:
        print("Live Weather")
        print(data)
    else:
        print("Unable to fetch weather")