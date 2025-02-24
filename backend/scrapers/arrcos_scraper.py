# Arccos Data Scraper

import requests
from config.config import Config

def get_arrcos_data():
    # TODO: Implement Arccos API integration
    headers = {
        'Authorization': f'Bearer {Config.ARRCOS_API_KEY}'
    }
    response = requests.get('https://api.arrcos.com/v1/data', headers=headers)
    return response.json()
