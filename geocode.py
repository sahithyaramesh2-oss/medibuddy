import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(city_name):
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(GEOCODE_URL, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if "results" not in data:
        return None

    place = data["results"][0]

    return {
        "city": place["name"],
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "country": place["country"]
    }


if __name__ == "__main__":
    city = input("Enter city: ")
    result = get_coordinates(city)

    if result:
        print(result)
    else:
        print("City not found")