from flask import Flask, request, redirect, session
import twilio.twiml
from tuber import * 
import time

app = Flask(__name__)
app.secret_key = "super secret salted key"

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
    product_selected = session.get("product_selected", False)
    uber_confirmed = session.get("uber_confirmed", False)
    if not product_selected and not uber_confirmed:
        # Short ciruit transaction
        if request.args.get('Body').lower() == 'reset':
            resp.message("That's cool! Resetting SMS session.")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)

        # Get lat, long with Google Places API
        try:
            ori_lat, ori_lng, des_lat, des_lng = get_location(request.args.get('Body'))
        except Exception:
            resp.message("Sorry. Please format your query as 'origin to destination'.")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)
        session["ori_lat"] = ori_lat
        session["ori_lng"] = ori_lng
        session["des_lat"] = des_lat
        session["des_lng"] = des_lng

        # Get products
        products = get_products(ori_lat, ori_lng)
        session["products"] = products
        product_names = [p["display_name"] for p in products]
        session["product_names"] = product_names

        # Return products response for confirmation
        if len(product_names) == 0:
            resp.message("Sorry. Uber is not available in your area.")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)
        else:
            resp.message("Thanks for using Uber! The following are available products in your area: \n\n" + \
                         ", ".join(product_names) + "\n\n Please type the name of the product you wish to use." + \
                         "Type 'reset' at anytime to reset.")
        session["product_selected"] = True
        return str(resp)
    if product_selected and not uber_confirmed:
        # Short ciruit transaction
        if request.args.get('Body').lower() == 'reset':
            resp.message("That's cool! Resetting SMS session.")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)

        # Get Session variables
        ori_lat = session.get("ori_lat")
        ori_lng = session.get("ori_lng")
        des_lat = session.get("des_lat")
        des_lng = session.get("des_lng")
        user_choice = request.args.get('Body')
        products = session.get("products")
        product_names = session.get("product_names")

        # Find the right product id based on user choice
        product_id = ""
        for p in products:
            if p["display_name"].lower() == user_choice.lower():
                product_id = p["product_id"]
                session["product_id"] = product_id
                break
        if product_id == "":
            resp.message("Sorry. I couldn't find that product. Please select from " + ", ".join(product_names))
            return str(resp)

        # Get price estimates and ask for final confirmation
        estimate = price(ori_lat, ori_lng, des_lat, des_lng)
        if estimate is None:
            resp.message("Sorry we couldn't calulate an estimate. Try adding more details to your query!")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)
        session["estimate"] = estimate
        resp.message("Great! Your estimate is " + estimate + " for " + user_choice + ". Is this okay? Type 'yes' or 'no'.")
        session["uber_confirmed"] = True
        return str(resp)
    else:
        # Short ciruit transaction
        if request.args.get('Body').lower() == 'reset':
            resp.message("That's cool! Resetting SMS session.")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)

        # Get session variables
        ori_lat = session.get("ori_lat")
        ori_lng = session.get("ori_lng")
        des_lat = session.get("des_lat")
        des_lng = session.get("des_lng")
        product_id = session.get("product_id")
        estimate = session.get("estimate")

        # Check if users types yes or no!
        if request.args.get('Body').lower() == "no":
            resp.message("Ok! That's cool. Reseting SMS session")
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)
        elif request.args.get('Body').lower() == "yes":
            # Request an Uber and get pricing info
            uber_response = request_uber(ori_lat, ori_lng, des_lat, des_lng, product_id)

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
            session["product_selected"] = False
            session["uber_confirmed"] = False
            return str(resp)
        # If they typed something dumb, try again.
        else: 
            resp.message("Sorry. I don't understand this query. Please type 'yes' or 'no' to confirm.")
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