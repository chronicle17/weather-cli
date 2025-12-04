# ⛅ Weather CLI

Weather CLI is a simple command-line tool to get real-time weather information using the WeatherAPI. The project allows you to configure an API Key and select a language for data display.

## 🚀 Installation

### 1️⃣ Clone the repository:
```bash
git clone https://github.com/k4ik/weather-cli.git
cd weather-cli
```

### 2️⃣ Create a virtual environment (optional but recommended):
```sh
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 3️⃣ Install dependencies:
```bash
pip install -e .
```

## ⚙️ Configuration
### 1️⃣ Set up API Key and language:

```bash
weather-config
```

## 🌦️ How to Use
### 1️⃣ Get weather forecast for a city:
```bash
weather [city]
```
Example:
```bash
weather "New York"
weather Tokyo
weather "New York" --unit f   # Fahrenheit
weather Tokyo -u f            # Fahrenheit (short option)
```

By default, temperatures are shown in **Celsius**. Use `--unit c` or `--unit f` (or `-u c` / `-u f`) to select the temperature unit.

## 🌍 Available languages

- 🇺🇸 English (en)
- 🇧🇷 Portuguese (pt)
- 🇪🇸 Spanish (es)
- 🇫🇷 Français (fr)
- 🇩🇪 Deutsch (de)
- 🇮🇹 Italian (it)
- 🇷🇺 Русский (ru)
- 🇨🇳 中文 (zh)
- 🇯🇵 日本語 (ja)
- 🇵🇱 Polski (pl)
- 🇷🇴 Română (ro)
- 🇸🇦 العربية (ar)


## 📋 Requirements
- Python 3.7+
- [WeatherAPI Key](https://www.weatherapi.com/)

## 📜 License
This project is licensed under the MIT License.