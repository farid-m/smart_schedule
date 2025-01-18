from quart import Quart, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from quart_cors import cors
import time
import requests
import datetime
import os
import asyncio
import httpx

from dotenv import load_dotenv

load_dotenv()


class TwilioSMSHandler:
    def __init__(self, account_sid, auth_token, phone_number):
        """
        Initializes the TwilioSMSHandler with credentials and phone number.
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.twilio_client = Client(self.account_sid, self.auth_token)

    async def send_sms(self, body, to_number):
        """
        Sends an SMS using Twilio.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.twilio_client.messages.create(
                body=body, from_=self.phone_number, to=to_number
            ),
        )


class SMSApp:
    def __init__(self, sms_handler):
        """
        Initializes the Flask app and associates the SMS handler.
        """
        self.app = cors(Quart(__name__))
        self.sms_handler = sms_handler
        self.setup_routes()
        # self.sms_handler.send_sms("hello test", "+16473911477")
        self.openai_api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.user_sessions = {}

    def setup_routes(self):
        """
        Sets up Flask routes.
        """

        @self.app.route("/retrieve", methods=["POST"])
        async def retrieve():
            data = await request.get_json()
            taskGUID = data.get("taskguid", "")
            with open("reports/" + str(taskGUID) + ".txt", "r") as file:
                summary = file.read()
            return {"status": "success", "summary": summary}

        @self.app.route("/interact", methods=["POST"])
        async def interact_with_openai():
            data = await request.get_json()
            task = data.get("task", "")
            to_number = data.get("to_number", "")
            taskGUID = data.get("taskguid", "")
            # Define the headers for the API call
            headers = {
                "Content-Type": "application/json",
                "api-key": self.openai_api_key,
            }
            user_id = to_number

            # Define the payload for the chat completion
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": f"You are a construction scheduler agent. Here is the task you "
                            f"need to focus on now >> {task}. Assume you are contacting the "
                            f"person assigned to this task in the field. You need to ask a "
                            f"sequence of max 4 to 5 questions one by one until you get "
                            f"the update "
                            f"related to this task. Try to figure out first if the task is "
                            f"ongoing, completed, or not started. Then get the updates and "
                            f"also get an updated end date. Once you are done getting the "
                            f"updates "
                            f"create a summary of the conversation plus the image (if "
                            f"uploaded) "
                            f"and publish the report. Make sure you say BYE at the end of "
                            f"the chat this is very important.",
                        },
                    ],
                    "max_tokens": 100,
                    "temperature": 0,
                }
            user_session = self.user_sessions[user_id]

            user_input = ""
            counter = 1
            completion = ""

            async with httpx.AsyncClient() as client:

                while user_input != "exit" and "bye" not in completion.lower():
                    if counter != 1:
                        while len(user_session["messages"]) < counter:
                            await asyncio.sleep(1)
                        user_input = user_session["messages"][-1]["content"]

                    try:
                        # Make the POST request
                        payload = {
                            "messages": user_session["messages"],
                            "max_tokens": 100,
                            "temperature": 0,
                        }
                        response = await client.post(
                            self.openai_api_endpoint, headers=headers, json=payload
                        )

                        # Check if the response is successful
                        if response.status_code == 200:
                            response_data = response.json()
                            completion = (
                                response_data.get("choices", [{}])[0]
                                .get("message", {})
                                .get("content", "")
                            )
                            # print("Response:", completion)
                            await sms_app.sms_handler.send_sms(completion, to_number)
                        else:
                            print(f"Error {response.status_code}: {response.text}")

                    except httpx.RequestError as e:

                        print("Request failed:", e)

                        break

                    counter += 1
            self.inputs = []
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("reports/" + str(taskGUID) + ".txt", "w") as file:
                file.write(
                    f"Timestamp: {timestamp}\n\n"
                )  # Write the timestamp and a blank line
                file.write(completion)  # Write the actual content
            return {"status": "success", "summary": completion}

        @self.app.route("/sms", methods=["POST"])
        async def sms_reply():
            data = await request.form
            user_id = data.get("From", "").strip()
            message = data.get("Body", "").strip()
            print(message, "received")
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {"messages": []}
                print("in loop")
            self.user_sessions[user_id]["messages"].append(
                {"role": "user", "content": message}
            )
            return str(MessagingResponse())

        @self.app.route("/send_sms", methods=["POST"])
        async def send_sms():
            data = await request.get_json()
            body = data.get("body", "")
            to_number = data.get("to_number", "")
            await self.sms_handler.send_sms(body, to_number)
            return {"status": "success"}, 200

    def run(self, host, port, debug=True):
        """
        Runs the Flask app.
        """
        self.app.run(debug=debug, host=host, port=port, use_reloader=False)


if __name__ == "__main__":
    # Twilio configuration
    ACCOUNT_SID = os.getenv("TWIL_ACCOUNT_SID")  # Replace with your Account SID
    AUTH_TOKEN = os.getenv("TWIL_AUTH_TOKEN")  # Replace with your Auth Token
    TWILIO_PHONE_NUMBER = os.getenv(
        "TWIL_PHONE_NUMBER"
    )  # Replace with your Twilio phone number

    # Initialize the Twilio SMS handler
    sms_handler = TwilioSMSHandler(ACCOUNT_SID, AUTH_TOKEN, TWILIO_PHONE_NUMBER)

    # Create and run the SMS app
    sms_app = SMSApp(sms_handler)
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    sms_app.run(host="0.0.0.0", port=port, debug=True)
