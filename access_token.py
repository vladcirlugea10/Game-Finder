import requests
import os

url = "https://id.twitch.tv/oauth2/token"
params = {
    "client_id": os.getenv("IGDB_CLIENT_ID"),
    "client_secret": os.getenv("IGDB_ACCESS_TOKEN"),
    "grant_type": "client_credentials"
}

response = requests.post(url, params=params)
token_data = response.json()

if "access_token" in token_data:
    print("Access Token:", token_data["access_token"])
else:
    print("Error:", token_data)
