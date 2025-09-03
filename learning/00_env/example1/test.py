import os
from dotenv import load_dotenv

#load .env file
load_dotenv()

#access variables
api_key = os.getenv("API_KEY")
mode = os.getenv("MODE")

print("API Key:", api_key)
print("Mode:", mode)