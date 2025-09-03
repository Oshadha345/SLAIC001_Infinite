import requests

def get_weather(city="London"):
    url = f"https://wttr.in/{city}?format=3"
    
    return requests.get(url).text

if __name__ == "__main__":
    city = input("Enter city: ")
    print(get_weather(city))