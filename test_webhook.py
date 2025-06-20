#!/usr/bin/env python3
"""
Test script for Instagram webhook functionality
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
VERIFY_TOKEN = "hotel_booking_verify_123456"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_verification():
    """Test webhook verification."""
    print("\n🔍 Testing webhook verification...")
    try:
        url = f"{BASE_URL}/webhook"
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "test_challenge_123"
        }
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200 and response.text == "test_challenge_123"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_message():
    """Test webhook message processing."""
    print("\n🔍 Testing webhook message processing...")
    try:
        url = f"{BASE_URL}/webhook"
        data = {
            "entry": [
                {
                    "messaging": [
                        {
                            "sender": {"id": "test_user_123"},
                            "message": {"text": "Hello, I want to book a room"},
                            "timestamp": int(datetime.now().timestamp())
                        }
                    ]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_send_message():
    """Test sending a message."""
    print("\n🔍 Testing send message endpoint...")
    try:
        url = f"{BASE_URL}/send-message"
        data = {
            "user_id": "test_user_123",
            "message": "This is a test message from the hotel booking agent!"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_bookings():
    """Test getting user bookings."""
    print("\n🔍 Testing get bookings endpoint...")
    try:
        url = f"{BASE_URL}/bookings/test_user_123"
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_conversations():
    """Test getting user conversations."""
    print("\n🔍 Testing get conversations endpoint...")
    try:
        url = f"{BASE_URL}/conversations/test_user_123"
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Instagram Webhook Tests\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Webhook Verification", test_webhook_verification),
        ("Webhook Message Processing", test_webhook_message),
        ("Send Message", test_send_message),
        ("Get Bookings", test_get_bookings),
        ("Get Conversations", test_get_conversations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        success = test_func()
        results.append((test_name, success))
        print(f"{'✅ PASS' if success else '❌ FAIL'}: {test_name}")
    
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

if __name__ == "__main__":
    main() 