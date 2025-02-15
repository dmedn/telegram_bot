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


def get_city(response_city: str) -> Dict:
    cities = {}
    data = json.loads(response_city)
    if not data:
        raise LookupError('Запрос пуст')
    for id_place in data['sr']:
        try:
            cities[id_place['gaiaId']] = {
                "gaiaId": id_place['gaiaId'],
                "regionNames": id_place['regionNames']['fullName']
            }
        except KeyError:
            continue
    return cities


def get_hotels(response_text: str, command: str, landmark_in: str, landmark_out: str) -> Dict:
    data = json.loads(response_text)
    if not data:
        raise LookupError('Запрос пуст')
    if 'error' in data.keys(): return {'error': data['errors'][0]['message']}
    hotels_data = {}
    for hotel in data['data']['propertySearch']['properties']:
        try:
            hotels_data[hotel['id']] = {
                'name': hotel['name'], 'id': hotel['id'],
                'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                'price': hotel['price']['lead']['amount']
            }
        except (KeyError, TypeError):
            continue
    if command == '/highprice':
        hotels_data = {key: value for key, value in
                       sorted(hotels_data.items(), key=lambda hotel_id: hotel_id[1]['price'], reverse=True)}
    elif command == '/bestdeal':
        hotels_data = {}
        for hotel in data['data']['propertySearch']['properties']:
            if float(landmark_in) < hotel['destinationInfo']['distanceFromDestination']['value'] < float(landmark_out):
                hotels_data[hotel['id']] = {
                    'name': hotel['name'],
                    'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount']
                }
    return hotels_data