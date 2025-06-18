import os
from typing import Dict, Any
import json
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        """Initialize with free local models and fallback options"""
        self.model = self._init_model()

    def _init_model(self):
        """Initialize the best available free model"""
        try:
            # First try small but capable model (works on CPU)
            return pipeline(
                "text2text-generation",
                model="google/flan-t5-base",  # Lightweight version
                device="cpu",
                max_length=256
            )
        except Exception as e:
            print(f"Model init warning: {str(e)}")
            return self._init_fallback()

    def _init_fallback(self):
        """Ultra-lightweight fallback"""
        return pipeline(
            "text-generation",
            model="distilgpt2",  # Tiny model that always works
            device="cpu"
        )

    def _query(self, prompt: str) -> str:
        """Smart query with automatic formatting"""
        try:
            if "text2text" in self.model.task:
                response = self.model(
                    prompt,
                    max_length=200,
                    temperature=0.3
                )
                return response[0]['generated_text'].strip()
            else:
                response = self.model(
                    prompt,
                    max_new_tokens=100,
                    pad_token_id=self.model.tokenizer.eos_token_id
                )
                return response[0]['generated_text'].split("\n")[0].strip()
        except Exception as e:
            print(f"Query error: {str(e)}")
            return "I'm currently unable to process requests."

    # Core Methods (identical interface to your existing code)
    def extract_intent(self, message: str) -> str:
        prompt = f"""Classify intent as: booking/reschedule/cancel/inquiry/greeting
User Message: "{message}"
Intent:"""
        intent = self._query(prompt).lower()
        return intent if intent in ['booking','reschedule','cancel','inquiry','greeting'] else 'inquiry'

    def extract_booking_info(self, message: str) -> Dict[str, Any]:
        prompt = f"""Extract as JSON with these keys:
{{
  "guest_name": "full name",
  "guest_email": "email",
  "guest_phone": "phone",
  "check_in_date": "YYYY-MM-DD",
  "check_out_date": "YYYY-MM-DD",
  "room_type": "type",
  "num_guests": "number"
}}

From: "{message}"
JSON:"""
        try:
            response = self._query(prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            return json.loads(response[start:end])
        except Exception:
            return {}  # Return empty dict on failure

    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if context:
            prompt = f"Context: {json.dumps(context)}\n\nQuestion: {prompt}"
        return self._query(prompt)

    def generate_booking_confirmation(self, booking_data: Dict[str, Any]) -> str:
        prompt = f"""Generate friendly confirmation using:
{json.dumps(booking_data, indent=2)}

Message:"""
        return self._query(prompt)