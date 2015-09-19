from urllib2 import Request, urlopen, URLError
from secret import *
import requests
import json
import random

# URLS
BASE_UBER_URL = "https://api.uber.com/v1/"
SANDBOX_URL = "https://sandbox-api.uber.com/v1/"
BASE_UBER_URL_1_1 = "https://api.uber.com/v1.1/"

# Session
app_session = requests.Session()

def get_location(context):
    query = context.split("to")
    ori = query[0].strip().replace(' ','+')
    des = query[1].strip().replace(' ','+')
    request = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+ori+'&key='+key)
    request2 = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+des+'&key='+key)

    try:
        response = urlopen(request)
        result = response.read()

        lat_begin = result.find('<lat>')
        lat_end = result.find('</lat>')
        ori_lat = result[lat_begin+5:lat_end]   

        lng_begin = result.find('<lng>')
        lng_end = result.find('</lng>')
        ori_lng = result[lng_begin+5:lng_end]
    except URLError as e:
        print ('error'), e

    try:
        response = urlopen(request2)
        result = response.read()

        lat_begin = result.find('<lat>')
        lat_end = result.find('</lat>')
        des_lat = result[lat_begin+5:lat_end]   

        lng_begin = result.find('<lng>')
        lng_end = result.find('</lng>')
        des_lng = result[lng_begin+5:lng_end]
    except URLError as e:
        print ('error'), e
    return (ori_lat, ori_lng, des_lat, des_lng)

# Generate headers we need to access everything
def generate_ride_headers():
    """Generate the header object that is used to make api requests."""
    return {
        'Authorization': 'bearer %s' % UBER_ACCESS_TOKEN,
        'Content-Type': 'application/json',
    }

def me():
    url = BASE_UBER_URL + 'me'
    response = app_session.get(
        url,
        headers=generate_ride_headers(),
    )
    return response

def price(ori_lat, ori_lng, des_lat, des_lng):
    url = BASE_UBER_URL + 'estimates/price'
    params = {
        'start_latitude': ori_lat,
        'start_longitude': ori_lng,
        'end_latitude': des_lat,
        'end_longitude': des_lng,
    }

    response = app_session.get(
        url,
        headers=generate_ride_headers(),
        params=params,
    )
    try:
        prices = json.loads(response.text)["prices"]
        estimate = ""
        # Iterate through all prices to get uberX estimate
        for p in prices:
            if p["display_name"] == "uberX":
                estimate = p["estimate"]
                return estimate
        return None
    except Exception:
        return None

def get_products(ori_lat, ori_lng):
    # Initialize API URL
    products_url = BASE_UBER_URL + 'products'

    # Get arguments
    params = {
        'latitude': ori_lat,
        'longitude': ori_lng
    }
    products_response = app_session.get(
        products_url,
        headers=generate_ride_headers(),
        params=params
    )
    products = json.loads(products_response.text)["products"]
    return products

def request_uber(ori_lat, ori_lng, des_lat, des_lng, product_id):
    # Initialize API URLS
    products_url = BASE_UBER_URL + 'products'
    request_url = SANDBOX_URL + 'requests'

    # Send the request for that product id
    request_params = json.dumps({
        'start_latitude': ori_lat,
        'start_longitude': ori_lng,
        'end_latitude': des_lat,
        'end_longitude': des_lng,
        'product_id': product_id,
    })
    requests_response = app_session.post(
        request_url,
        headers=generate_ride_headers(),
        data=request_params,
    )
    return requests_response.text

def check_request(request_id):
    accepted_url = SANDBOX_URL + 'sandbox/requests/' + request_id
    request_url = SANDBOX_URL + 'requests/' + request_id
    random_num = random.random()
    print random_num
    accepted = json.dumps({"status":"accepted"})
    if random_num <= .70:
        # Set status to accepted
        response = app_session.put(
            accepted_url,
            headers=generate_ride_headers(),
            data=accepted
        )
        print response.text
    # Get actual response request
    requests_response = app_session.get(
        request_url,
        headers=generate_ride_headers(),
    )
    return requests_response.text
