import json
from telebot.types import Dict


def hotels_info(hotels_request: str) -> Dict:
    """Возвращает json с данными отеля"""

    data = json.loads(hotels_request)
    if not data:
        raise LookupError('Запрос пуст')

    hotel_data = {
        'id': data['data']['propertyInfo']['summary']['id'], 'name': data['data']['propertyInfo']['summary']['name'],
        'address': data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
        'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
        'images': [
            url['image']['url'] for url in data['data']['propertyInfo']['propertyGallery']['images']
        ]
    }
    return hotel_data
