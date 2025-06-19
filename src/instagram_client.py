import os
import requests
from dotenv import load_dotenv

load_dotenv()
PAGE_TOKEN = os.getenv("PAGE_TOKEN")

class InstagramClient:
    def __init__(self):
        self.token = PAGE_TOKEN
        self.graph_url = "https://graph.facebook.com/v15.0"

    def send_message(self, recipient_id, text):
        try:
            resp = requests.post(
                f"{self.graph_url}/me/messages",
                json={
                    "recipient": {"id": recipient_id},
                    "message":   {"text": text},
                    "access_token": self.token
                }
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"[InstagramClient] send_message error: {e}")

    def webhook_handler(self, payload):
        entry = payload["entry"][0]["messaging"][0]
        return entry["sender"]["id"], entry["message"].get("text", "")
