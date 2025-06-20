import json
from typing import Dict, Optional
from datetime import datetime

class MockInstagramClient:
    """Mock Instagram client for testing purposes."""
    
    def __init__(self):
        self.messages = []
        self.users = {}
    
    def send_message(self, user_id: str, message: str) -> Dict:
        """Mock sending a message."""
        msg = {
            "recipient_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "outgoing"
        }
        self.messages.append(msg)
        print(f"📤 Sent to {user_id}: {message}")
        return {"success": True, "message_id": len(self.messages)}
    
    def receive_message(self, user_id: str, message: str) -> Dict:
        """Mock receiving a message."""
        msg = {
            "sender_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "incoming"
        }
        self.messages.append(msg)
        print(f"📥 Received from {user_id}: {message}")
        return msg
    
    def get_user_info(self, user_id: str) -> Dict:
        """Mock getting user information."""
        if user_id not in self.users:
            self.users[user_id] = {
                "id": user_id,
                "username": f"user_{user_id}",
                "created_at": datetime.now().isoformat()
            }
        return self.users[user_id]
    
    def verify_webhook(self, mode: str, token: str, challenge: Optional[str] = None) -> Dict:
        """Mock webhook verification."""
        if mode == "subscribe" and token == "test_verify_token":
            return {"hub.challenge": challenge or "test_challenge"}
        return {"error": "Invalid verification"}
    
    def handle_webhook(self, data: Dict) -> None:
        """Mock handling webhook data."""
        print(f"🔗 Webhook received: {json.dumps(data, indent=2)}")
        
        # Simulate processing a message
        if "entry" in data:
            for entry in data["entry"]:
                if "messaging" in entry:
                    for message in entry["messaging"]:
                        sender_id = message["sender"]["id"]
                        if "message" in message and "text" in message["message"]:
                            text = message["message"]["text"]
                            # Process the message using the booking agent
                            from src.agent.booking_agent import process_message
                            response = process_message(text, sender_id)
                            self.send_message(sender_id, response)
    
    def get_message_history(self) -> list:
        """Get all message history."""
        return self.messages 