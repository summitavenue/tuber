from secret import *
import requests
import json

# URLS
BASE_UBER_URL = "https://api.uber.com/v1/"
BASE_UBER_URL_1_1 = "https://api.uber.com/v1.1/"

# Session
session = requests.Session()

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

response = me()
print response.text
