from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


class TwilioSMSHandler:
    def __init__(self, account_sid, auth_token, phone_number):
        """
        Initializes the TwilioSMSHandler with credentials and phone number.
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.twilio_client = Client(self.account_sid, self.auth_token)

    def send_sms(self, body, to_number):
        """
        Sends an SMS using Twilio.
        """
        self.twilio_client.messages.create(
            body=body, from_=self.phone_number, to=to_number
        )

    def process_message(self, message):
        """
        Processes the incoming message and generates a response.
        Customize the logic here as needed.
        """
        return f"You said: {message.upper()}"


class SMSApp:
    def __init__(self, sms_handler):
        """
        Initializes the Flask app and associates the SMS handler.
        """
        self.app = Flask(__name__)
        self.sms_handler = sms_handler
        self.setup_routes()
        self.inputs = []

    def setup_routes(self):
        """
        Sets up Flask routes.
        """

        @self.app.route("/sms", methods=["POST"])
        def sms_reply():
            # Get the message from the user
            self.inputs.append(request.form.get("Body", "").strip())
            # from_number = request.form.get('From', '')

            # Process the message and prepare a response
            # response_msg = self.sms_handler.process_message(incoming_msg)

            # Send the response back via Twilio
            # self.sms_handler.send_sms(response_msg, from_number)

            # Return an empty response to Twilio (acknowledgment)
            return str(MessagingResponse())

    def run(self, debug=True):
        """
        Runs the Flask app.
        """
        self.app.run(debug=debug, use_reloader=False)


if __name__ == "__main__":
    # Twilio configuration
    ACCOUNT_SID = "AC5607ca505b69a91cfafe52310fe3bd05"  # Replace with your Account SID
    AUTH_TOKEN = "743674f57e44c27f71c77e8d0ab7a722"  # Replace with your Auth Token
    TWILIO_PHONE_NUMBER = "+12183665130"  # Replace with your Twilio phone number

    # Initialize the Twilio SMS handler
    sms_handler = TwilioSMSHandler(ACCOUNT_SID, AUTH_TOKEN, TWILIO_PHONE_NUMBER)

    # Create and run the SMS app
    sms_app = SMSApp(sms_handler)
    sms_app.run(debug=True)
