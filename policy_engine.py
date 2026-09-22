import json


def load_sops():
    with open("sop_rules.json", "r") as file:
        return json.load(file)




def activity_matches(user_query, sop):
    query = user_query.lower()

    # Match whole keywords from SOP activity list
    for keyword in sop["activity"]:
        keyword = keyword.lower().strip()

        if keyword in query:
            return True

    return False

def weather_matches(weather, sop):
    conditions = sop["conditions"]

    for key, value in conditions.items():

        if key == "wind_speed_min":
            if weather["wind_speed"] < value:
                return False

        elif key == "uv_index_min":
            if weather["uv_index"] < value:
                return False

        elif key == "rain_probability_min":
            if weather["rain_probability"] < value:
                return False

        elif key == "precipitation_min":
            if weather["precipitation"] < value:
                return False

        elif key == "temperature_min":
            if weather["temperature"] < value:
                return False

        elif key == "temperature_max":
            if weather["temperature"] > value:
                return False

        elif key == "rain_probability_max":
            if weather["rain_probability"] > value:
                return False

    return True


def find_matching_sops(user_query, weather):
    matches = []

    for sop in load_sops():
        if activity_matches(user_query, sop) and weather_matches(weather, sop):
            matches.append(sop)

    return matches



SEVERITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

def select_best_sop(matches):
    if not matches:
        return None

    fallback = None
    real_matches = []

    for sop in matches:
        if sop["id"] == "SOP013":
            fallback = sop
        else:
            real_matches.append(sop)

    if real_matches:
        real_matches.sort(
            key=lambda x: SEVERITY_ORDER[x["severity"]],
            reverse=True
        )
        return real_matches[0]

    return fallback

from weather import get_weather



if __name__ == "__main__":

    sops = load_sops()

    print(f"Loaded {len(sops)} SOPs")
    user_query = input("Ask your activity question: ")
    city = input("Enter city: ")

    weather = get_weather(city)

    if weather is None:
        print("Unable to fetch weather.")
        exit()

   

    matches = find_matching_sops(user_query, weather)
    best = select_best_sop(matches)

    if best:
        print("\nMatched SOP")
        print("SOP ID:", best["id"])
        print("Severity:", best["severity"])
        print("Advice:", best["advice"])
        print("Reason:", best["reason"])
    else:
        print("No SOP applies for this request.")
