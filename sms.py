from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Twilio configuration
ACCOUNT_SID = 'AC5607ca505b69a91cfafe52310fe3bd05'  # Replace with your Account SID
AUTH_TOKEN = '743674f57e44c27f71c77e8d0ab7a722'    # Replace with your Auth Token
TWILIO_PHONE_NUMBER = '+12183665130'  # Replace with your Twilio phone number

# Initialize Flask app
app = Flask(__name__)

def send_sms(body,num_txt):
    twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)
    twilio_client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=num_txt
    )

# Route to handle incoming SMS
@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get the message from the user
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '')

    # Process the message and prepare a response
    response_msg = process_message(incoming_msg)

    # Send the response back via Twilio
    twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)
    twilio_client.messages.create(
        body=response_msg,
        from_=TWILIO_PHONE_NUMBER,
        to=from_number
    )

    # Return an empty response to Twilio (acknowledgment)
    return str(MessagingResponse())

def process_message(message):
    """
    This function processes the user's input and generates a response.
    Customize the logic here as needed.
    """
    # Example logic: Echo back the message with some transformation
    return f"You said: {message.upper()}"

if __name__ == '__main__':
    app.run(debug=True)

