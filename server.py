from flask import Flask, request, redirect
import twilio.twiml
from tuber import * 

app = Flask(__name__)
 

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
 	
    resp = twilio.twiml.Response()
    ori_lat, ori_lng, des_lat, des_lng = get_location(response.args.get('Body'))
    uber_response = me()
    resp.message("Hello! Here is your location: " + str(ori_lat) + str(ori_lng))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)