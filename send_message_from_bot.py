import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

JSON_FILE = "./data.json"
# Replace 'YOUR_BOT_TOKEN' with the actual token provided by BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MESSAGE = "Happy New Year !!"


def send_message_to_chat(chat_id):
    # Define the API endpoint for sending messages
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Define the parameters for the request
    params = {"chat_id": chat_id, "text": MESSAGE}

    # Send the request
    response = requests.post(url, params=params)


if __name__ == "__main__":
    with open(JSON_FILE) as json_file:
        json_data = json.load(json_file)
        for user_id in json_data.keys():
            send_message_to_chat(user_id)
