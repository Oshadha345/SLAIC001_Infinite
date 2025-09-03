import os
import requests
from dotenv import load_dotenv

def load_environment(env="development"):
    """Load the right .env file based on environment name."""
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded {env_file}")
    else:
        raise FileNotFoundError(f"{env_file} not found!")

# Choose environment (default: development)
current_env = os.getenv("APP_ENV", "development")
load_environment(current_env)

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        print(f"\n🌍 City: {data['name']}")
        print(f"🌡️ Temp: {data['main']['temp']}°C")
        print(f"☁️ Weather: {data['weather'][0]['description']}")
        print(f"🔧 Debug mode: {os.getenv('DEBUG')}")
    else:
        print("Error:", data.get("message", "Something went wrong"))

if __name__ == "__main__":
    city = input("Enter city: ")
    get_weather(city)
