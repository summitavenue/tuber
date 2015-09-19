from urllib2 import Request, urlopen, URLError
from secret import *
import requests
import json

# URLS
BASE_UBER_URL = "https://api.uber.com/v1/"
SANDBOX_URL = "https://sandbox-api.uber.com/v1/"
BASE_UBER_URL_1_1 = "https://api.uber.com/v1.1/"

# Session
session = requests.Session()

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
	response = session.get(
		url,
		headers=generate_ride_headers(),
	)
	return response

def request_uber(ori_lat, ori_lng, des_lat, des_lng):
	products_url = BASE_UBER_URL + 'products'
	request_url = SANDBOX_URL + 'requests'
	params = {
    	'latitude': ori_lat,
    	'longitude': ori_lng
    }
	products_response = session.get(
		products_url,
		headers=generate_ride_headers(),
		params=params
	)
	products = json.loads(products_response.text)["products"]
	product_id = ""
	# Loop over all products and find original Uber
	for p in products:
		if p["description"] == "The original Uber":
			product_id = p["product_id"]
			break
	if product_id == "":
		return None
	request_params = json.dumps({
    	'start_latitude': ori_lat,
    	'start_longitude': ori_lng,
    	'end_latitude': des_lat,
    	'end_longitude': des_lng,
    	'product_id': product_id,
    })
	requests_response = session.post(
		request_url,
		headers=generate_ride_headers(),
		data=request_params,
	)
	return requests_response.text

def check_request(request_id):
	request_url = SANDBOX_URL + 'requests/' + request_id
	requests_response = session.get(
		request_url,
		headers=generate_ride_headers(),
	)
	return requests_response.text
