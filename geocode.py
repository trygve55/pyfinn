from geopy.geocoders import Nominatim
from geopy import distance


geolocator = Nominatim(user_agent="finnpy")


def get_geocode(address):
    data = {}
    location = geolocator.geocode(address)
    data['lat'] = location.latitude
    data['lon'] = location.longitude

    return data