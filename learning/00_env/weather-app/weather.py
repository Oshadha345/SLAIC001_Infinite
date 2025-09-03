import os
import requests
from dotenv import load_dotenv

#load env
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    
    params = {
        "q":city,
        "appid":API_KEY,
        "units":"metric"
    }
    
    response = requests.get(BASE_URL, params=params)
    
    data = response.json()
    
    if response.status_code == 200:
        print(f"🌍 City: {data['name']}")
        print(f"🌡️ Temp: {data['main']['temp']}°C")
        print(f"☁️ Weather: {data['weather'][0]['description']}")
    else:
        print("Error:", data.get("message", "Something went wrong"))
        
if __name__ == "__main__":
    city = input("Enter city: ")
    get_weather(city)