from flask import Flask, request, redirect
import twilio.twiml
from tuber import * 
import time

app = Flask(__name__)

users = {
    "+12814680885" : "Charles"
}
 
landmarks = {
    "1" : "Palladium Hall NYC",
    "2" : "Major League Hacking NYC"
}

@app.route("/message", methods=['GET', 'POST'])
def message():
    """
    Respond to incoming messages with an Uber.
    """
    resp = twilio.twiml.Response()
    # Get lat, long with Google Places API
    ori_lat, ori_lng, des_lat, des_lng = get_location(request.args.get('Body'))

    # Request an Uber and get pricing info
    uber_response = request_uber(ori_lat, ori_lng, des_lat, des_lng)
    estimate = price(ori_lat, ori_lng, des_lat, des_lng)

    # If the response is empty, we don't have a driver.
    if uber_response is None:
    	resp.message("Sorry. No Uber drivers in your area.")
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
    	license_plate = uber_response["vehicle"]["license_plate"]
    	eta = uber_response["eta"]
    	resp.message("Thanks for waiting! Look for the " + make + " " + model + " with a license plate of " + "\"" + license_plate + "\"" + \
                     " driven by " + name + ". The driver's phone number is " + phone_number + " and he/she should be arriving in " \
                      + str(eta) + " minutes! Your price estimate is " + estimate)
    return str(resp)





# VOICE STUFF!
# LOL
#
#
@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """
    Respond to incoming calls with an Uber.
    """
    # Prepare Twilio response
    resp = twilio.twiml.Response()
    resp.say("Yo fam what's good? Tryna go someplace? I'll hook you up.")

    with resp.gather(numDigits=2, action="/handle_ride", method="POST") as g:
        g.say("Enter a two digit number where the first number is your origin \
               and your second number is your destination! \
               For Palladium Hall press 1. \
               For MLH press 2.")
    return str(resp)

@app.route("/handle_ride", methods=['GET', 'POST'])
def handle_ride():
    """
    Given digits from the initial call - make an Uber ride!
    """
    # Prepare Twilio response
    resp = twilio.twiml.Response()

    # Get directions string
    digits = [x for x in request.values.get('Digits', None)]
    directions_string = landmarks[digits[0]] + "to" + landmarks[digits[1]]

    # Get lat, long with Google Places API
    ori_lat, ori_lng, des_lat, des_lng = get_location(directions_string)

    # Request an Uber and get pricing info
    uber_response = request_uber(ori_lat, ori_lng, des_lat, des_lng)
    estimate = price(ori_lat, ori_lng, des_lat, des_lng)

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
        license_plate = uber_response["vehicle"]["license_plate"]
        eta = uber_response["eta"]
        resp.say("Thanks for the directions! We'll be sending a confirmation message shortly.")
        resp.message("Thanks for waiting! Look for the " + make + " " + model + " with a license plate of " + "\"" + license_plate + "\"" + \
                     " driven by " + name + ". The driver's phone number is " + phone_number + " and he/she should be arriving in " \
                      + str(eta) + " minutes! Your price estimate is " + estimate)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)