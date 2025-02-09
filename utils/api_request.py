import requests
from config_data.settings import settings

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": settings.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def request(method: str, url: str, query_string: dict) -> requests.Response:
    if method == 'GET':
        response_get = requests.request('GET', url, params=query_string, headers=headers)
        return response_get
    elif method == 'POST':
        response_post = requests.request('POST', url, json=query_string, headers=headers)
        return response_post
