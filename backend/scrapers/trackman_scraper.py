# Trackman Data Scraper

import requests
from config.config import Config

def get_trackman_data():
    # TODO: Implement Trackman API integration
    headers = {
        'Authorization': f'Bearer {Config.TRACKMAN_API_KEY}'
    }
    response = requests.get('https://api.trackman.com/v1/data', headers=headers)
    return response.json()
