from flask import Flask, request, redirect
import twilio.twiml
from tuber import * 
import time

app = Flask(__name__)
 

@app.route("/", methods=['GET', 'POST'])
def message_response():
    """
    Respond to incoming messages with an Uber.
    """
    resp = twilio.twiml.Response()
    # Get lat, long with Google Places API
    ori_lat, ori_lng, des_lat, des_lng = get_location(request.args.get('Body'))

    # Request an Uber and get pricing info
    uber_response = request_uber(ori_lat, ori_lng, des_lat, des_lng)
    # TODO: Pricing

    # If the response is empty, we don't have a driver.
    if uber_response is None:
    	resp.message("Sorry. No Uber driver's in your area.")
    	return str(resp)

    # Load valid response into dictionary
    uber_response = json.loads(uber_response)
    request_id = uber_response["request_id"]

    # Poll while waiting for a driver
    while uber_response["status"] == "processing":
    	time.sleep(5)
    	uber_response = json.loads(check_request(request_id))

    # Format Confirmation response
    if uber_response["status"] == "accepted":
    	name = uber_response["driver"]["name"]
    	phone_number = uber_response["driver"]["phone_number"]
    	make = uber_response["vehicle"]["make"]
    	model = uber_response["vehicle"]["model"]
    	license_plate = uber_response["vehicle"]["liscense_plate"]
    	eta = uber_response["eta"]
    	resp.message("Thanks for waiting! Look for the " + make + " " + model + " with a liscense plate of " + liscense_plate + " driven by Bob. \
    				  The driver's phone number is " + phone_number + " and he/she should be arriving in " + eta + " minutes!")
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)