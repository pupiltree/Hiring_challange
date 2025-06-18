from dotenv import load_dotenv
import os
from typing import Dict, Any
import json
from huggingface_hub import login
from langchain_huggingface import HuggingFaceEndpoint

# Load environment variables
load_dotenv()

class AIClient:
    def __init__(self):
        """Initialize with both direct API and LangChain options"""
        self.api_token = os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize LangChain model
        login(token=self.api_token)
        self.llm = HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            temperature=0.1,
            max_new_tokens=100,
        )

    def _query(self, prompt: str) -> str:
        """Unified query method using LangChain"""
        try:
            response = self.llm.invoke(prompt)
            return response.strip()
        except Exception as e:
            print(f"Error querying model: {e}")
            return "Error: Unable to generate response"

    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response with optional context"""
        if context:
            prompt = f"Context: {json.dumps(context)}\n\n{prompt}"
        return self._query(prompt)

    def extract_intent(self, message: str) -> str:
        """Classify user intent"""
        prompt = f"""Classify the user intent from this message. Return only one of these:
- booking
- reschedule
- cancel
- inquiry
- greeting

Message: "{message}"
Intent:"""
        intent = self._query(prompt).lower().strip()
        valid = ['booking', 'reschedule', 'cancel', 'inquiry', 'greeting']
        return intent if intent in valid else 'inquiry'

    def extract_booking_info(self, message: str) -> Dict[str, Any]:
        """Extract structured booking info"""
        prompt = f"""Extract booking info from this message. Return as JSON with keys:
- check_in_date (YYYY-MM-DD)
- check_out_date (YYYY-MM-DD)
- room_type
- num_guests
- guest_name
- guest_email
- guest_phone

If missing, return null for values. Message: "{message}"
JSON:"""
        try:
            response = self._query(prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing booking info: {e}")
            return {}

    def generate_booking_confirmation(self, booking_data: Dict[str, Any]) -> str:
        """Generate confirmation message"""
        prompt = f"""Generate a friendly booking confirmation message using these details:
{json.dumps(booking_data, indent=2)}

Make it professional but warm.
"""
        return self._query(prompt)