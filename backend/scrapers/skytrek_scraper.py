# Skytrak Data Scraper

import requests
from config.config import Config

def get_skytrak_data():
    # TODO: Implement Skytrak API integration
    headers = {
        'Authorization': f'Bearer {Config.SKYTRAK_API_KEY}'
    }
    response = requests.get('https://api.skytrak.com/v1/data', headers=headers)
    return response.json()
