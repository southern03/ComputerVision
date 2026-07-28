# Import geocoding library
from geopy.geocoders import Nominatim

# Program entry point
if __name__ == '__main__':
    address = 'Soongsil University' # Address to search
    user_agent = 'Namho' # Set user agent
    location = Nominatim(user_agent=user_agent).geocode(address) # Convert address to coordinates
    print(location.latitude, location.longitude) # Print latitude and longitude
