import requests
from config import Config
from typing import Optional

class InstagramClient:
    def __init__(self):
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.page_id = Config.INSTAGRAM_PAGE_ID
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_message(self, recipient_id: str, message_text: str) -> bool:
        """Send message to Instagram user"""
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending Instagram message: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[dict]:
        """Get Instagram user information"""
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,profile_pic",
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting user info: {e}")
            return None
    
    def verify_webhook(self, verify_token: str, challenge: str) -> Optional[str]:
        """Verify webhook for Instagram"""
        expected_token = Config.INSTAGRAM_APP_SECRET
        if verify_token == expected_token:
            return challenge
        return None
    
    def parse_webhook_message(self, webhook_data: dict) -> Optional[dict]:
        """Parse incoming webhook message"""
        try:
            entry = webhook_data.get("entry", [{}])[0]
            messaging = entry.get("messaging", [{}])[0]
            
            if "message" in messaging:
                return {
                    "sender_id": messaging["sender"]["id"],
                    "message_text": messaging["message"]["text"],
                    "timestamp": messaging["timestamp"]
                }
        except (KeyError, IndexError) as e:
            print(f"Error parsing webhook message: {e}")
        return None