from flask import Flask, request, redirect
import twilio.twiml
from tuber import * 

app = Flask(__name__)
 

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
 	
    resp = twilio.twiml.Response()
    uber_response = me()
    resp.message("Hello! Here is your uber profile: " + uber_response.text)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)