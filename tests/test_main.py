import pytest
from typer.testing import CliRunner

import weather_cli.main as main


runner = CliRunner()


class DummySpinner:
    def start(self):
        pass

    def stop(self):
        pass


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def patch_common(monkeypatch):
    """Patch common dependencies for the weather command."""
    # yaspin -> DummySpinner
    monkeypatch.setattr(main, "yaspin", lambda: DummySpinner())

    # Environment-derived globals
    monkeypatch.setattr(main, "api_key", "TEST_API_KEY")
    monkeypatch.setattr(main, "lang", "en")

    # Simple translations for predictable output
    translations = {
        "weather-info": {
            "location": "Location: {name}, {region}, {country} ({lat}, {lon})",
            "localtime": "Local Time: {localtime}",
            "temperature": "Temperature: {temp}{temp_unit_symbol} (Feels like: {feels_like}{temp_unit_symbol})",
            "condition": "Condition: {condition}",
            "humidity": "Humidity: {humidity}%",
            "pressure": "Pressure: {pressure} mb",
            "wind": "Wind: {wind_speed} km/h {wind_dir}",
            "precipitation": "Precipitation: {precipitation} mm",
            "uv": "UV Index: {uv_index}",
        },
        "weather-errors": {
            "city-not-found": '❗ No matching location found for "{city}".',
            "generic-error": "❗ Could not fetch weather data (status {status_code}).",
        },
    }
    monkeypatch.setattr(main, "translations", translations)

    yield


def make_weather_payload(
    temp_c=20.0,
    temp_f=68.0,
    feelslike_c=21.0,
    feelslike_f=69.8,
):
    return {
        "location": {
            "name": "London",
            "region": "London",
            "country": "UK",
            "lat": 51.5074,
            "lon": -0.1278,
            "localtime": "2025-12-04 10:00",
        },
        "current": {
            "temp_c": temp_c,
            "temp_f": temp_f,
            "feelslike_c": feelslike_c,
            "feelslike_f": feelslike_f,
            "condition": {"text": "Partly cloudy"},
            "humidity": 50,
            "pressure_mb": 1012,
            "wind_kph": 10.0,
            "wind_dir": "NW",
            "precip_mm": 0.0,
            "uv": 3.0,
        },
    }


def test_weather_celsius_output(monkeypatch):
    """weather should use Celsius values and symbol with --unit c."""
    payload = make_weather_payload(
        temp_c=20.0, temp_f=68.0, feelslike_c=21.0, feelslike_f=69.8
    )

    def fake_get(url):
        return DummyResponse(payload)

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = runner.invoke(main.app, ["weather", "London", "--unit", "c"])
    assert result.exit_code == 0, result.output

    # Check that Celsius is used
    assert "Temperature: 20.0°C (Feels like: 21.0°C)" in result.output
    # Location sanity check
    assert "Location: London, London, UK" in result.output


def test_weather_fahrenheit_output(monkeypatch):
    """weather should use Fahrenheit values and symbol with --unit f."""
    payload = make_weather_payload(
        temp_c=20.0, temp_f=68.0, feelslike_c=21.0, feelslike_f=69.8
    )

    def fake_get(url):
        return DummyResponse(payload)

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = runner.invoke(main.app, ["weather", "London", "--unit", "f"])
    assert result.exit_code == 0, result.output

    # Check that Fahrenheit is used
    assert "Temperature: 68.0°F (Feels like: 69.8°F)" in result.output
    # And Celsius string is not present
    assert "20.0°C" not in result.output


def test_weather_invalid_unit(monkeypatch):
    """weather should fail fast on invalid unit and not call the API."""

    def fake_get(url):
        raise AssertionError("requests.get should not be called for invalid unit")

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = runner.invoke(main.app, ["weather", "London", "--unit", "x"])
    assert result.exit_code != 0
    assert "Unit must be 'c' for Celsius or 'f' for Fahrenheit." in result.output


def test_weather_unknown_city_error(monkeypatch):
    """weather should print a friendly message when the city is not found."""
    error_payload = {
        "error": {
            "code": 1006,
            "message": "No matching location found.",
        }
    }

    def fake_get(url):
        return DummyResponse(error_payload, status_code=400)

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = runner.invoke(main.app, ["weather", "NowhereLand"])
    # Typer Exit -> non-zero exit code
    assert result.exit_code != 0
    assert 'No matching location found for "NowhereLand".' in result.output


