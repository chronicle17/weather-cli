import typer
import time
from yaspin import yaspin
import requests
from dotenv import load_dotenv
import os
import json

app = typer.Typer()
load_dotenv()

def load_translation():
    lang = os.getenv("TOOL_LANGUAGE", "en")
    try:
        with open(f"locales/{lang}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Translation file for '{lang}' not found. Falling back to English.")
        with open("locales/en.json", "r", encoding="utf-8") as file:
            return json.load(file)

translations = load_translation()

api_key = os.getenv('API_KEY')
lang = os.getenv('TOOL_LANGUAGE', 'en')

@app.command()
def weather(
    city: str,
    unit: str = typer.Option(
        "c",
        "--unit",
        "-u",
        help="Temperature unit: c for Celsius, f for Fahrenheit",
    ),
):
    unit = unit.lower()
    if unit not in ("c", "f"):
        raise typer.BadParameter("Unit must be 'c' for Celsius or 'f' for Fahrenheit.")
    spinner = yaspin()
    spinner.start()
    time.sleep(1)
    spinner.stop()

    res = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang={lang}"
    )
    try:
        data = res.json()
    except ValueError:
        print(
            translations["weather-errors"]["generic-error"].format(
                status_code=res.status_code
            )
        )
        raise typer.Exit(code=1)

    # Handle API errors (invalid city, etc.)
    if res.status_code != 200 or (isinstance(data, dict) and "error" in data):
        error = data.get("error") if isinstance(data, dict) else None
        error_code = error.get("code") if isinstance(error, dict) else None

        if error_code == 1006:
            # WeatherAPI code 1006: No matching location found.
            print(
                translations["weather-errors"]["city-not-found"].format(city=city)
            )
        else:
            print(
                translations["weather-errors"]["generic-error"].format(
                    status_code=res.status_code
                )
            )
        raise typer.Exit(code=1)

    current = data["current"]
    temp_c = current["temp_c"]
    temp_f = current["temp_f"]
    feels_like_c = current["feelslike_c"]
    feels_like_f = current["feelslike_f"]

    if unit == "f":
        temp = temp_f
        feels_like = feels_like_f
        temp_unit_symbol = "°F"
    else:
        temp = temp_c
        feels_like = feels_like_c
        temp_unit_symbol = "°C"

    weather_data = {
        "name": data["location"]["name"],
        "region": data["location"]["region"],
        "country": data["location"]["country"],
        "lat": data["location"]["lat"],
        "lon": data["location"]["lon"],
        "localtime": data["location"]["localtime"],
        "temp_c": temp_c,
        "temp_f": temp_f,
        "feels_like_c": feels_like_c,
        "feels_like_f": feels_like_f,
        "temp": temp,
        "feels_like": feels_like,
        "temp_unit_symbol": temp_unit_symbol,
        "condition": current["condition"]["text"],
        "humidity": current["humidity"],
        "pressure": current["pressure_mb"],
        "wind_speed": current["wind_kph"],
        "wind_dir": current["wind_dir"],
        "precipitation": current["precip_mm"],
        "uv_index": current["uv"],
    }

    print("\n")
    print(translations["weather-info"]["location"].format(**weather_data))
    print(translations["weather-info"]["localtime"].format(**weather_data))
    print(translations["weather-info"]["temperature"].format(**weather_data))
    print(translations["weather-info"]["condition"].format(**weather_data))
    print(translations["weather-info"]["humidity"].format(**weather_data))
    print(translations["weather-info"]["pressure"].format(**weather_data))
    print(translations["weather-info"]["wind"].format(**weather_data))
    print(translations["weather-info"]["precipitation"].format(**weather_data))
    print(translations["weather-info"]["uv"].format(**weather_data))
    print("\n")

if __name__ == "__main__":
    app()
