import requests

def get_prec_temp_forecast(lat, lon):
    '''
    Gets weather API request.
    Returns dictionary containing date, location and temperature and precipitation forecast for the next three days.
    '''
    uri = 'http://api.weatherapi.com/v1/'
    api_key = '946b168e08314d6abea100703212911'
    query = f'forecast.json?key={api_key}&q={lat},{lon}&days=10&aqi=no&alerts=no'
    full_url = uri + query

    response = requests.get(full_url).json()

    output = {
        'date' : response['location']['localtime'],
        'location' : response['location']['name'],
        'lat' : response['location']['lat'],
        'lon' : response['location']['lon'],
        response['forecast']['forecastday'][0]['date'] : {
            'precipitation' : response['forecast']['forecastday'][0]['day']['totalprecip_mm'],
            'temperature' : response['forecast']['forecastday'][0]['day']['avgtemp_c'],
        },
        response['forecast']['forecastday'][1]['date'] : {
            'precipitation' : response['forecast']['forecastday'][1]['day']['totalprecip_mm'],
            'temperature' : response['forecast']['forecastday'][1]['day']['avgtemp_c'],
        },
        response['forecast']['forecastday'][2]['date'] : {
            'precipitation' : response['forecast']['forecastday'][2]['day']['totalprecip_mm'],
            'temperature' : response['forecast']['forecastday'][2]['day']['avgtemp_c'],
        }
    }
    return output
