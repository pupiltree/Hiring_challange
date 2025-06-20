#!/usr/bin/env python3
"""
Test script for the Hotel Booking AI Agent
Run this to test the agent functionality without Instagram integration
"""

import os
import sys
from agents.graph_builder import HotelGraphBuilder
from config import Config

def test_conversation_flow():
    """Test the conversation flow"""
    print("🏨 Hotel Booking AI Agent Test")
    print("=" * 50)
    
    # Initialize the agent
    try:
        graph_builder = HotelGraphBuilder()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    # Test user ID
    test_user_id = "test_user_123"
    
    # Test scenarios
    test_scenarios = [
        # Greeting
        {
            "input": "Hello",
            "description": "Testing greeting"
        },
        # Hotel inquiry
        {
            "input": "What amenities do you have?",
            "description": "Testing hotel inquiry"
        },
        # Booking flow
        {
            "input": "I want to book a room",
            "description": "Starting booking process"
        },
        {
            "input": "I need a deluxe room from December 25 to December 28 for 2 guests",
            "description": "Providing booking details"
        },
        {
            "input": "My name is John Smith, email john@example.com, phone 555-1234",
            "description": "Providing guest details"
        },
        # Check booking (this will need the booking ID from previous step)
        {
            "input": "What are your check-in and check-out times?",
            "description": "Testing hotel info query"
        }
    ]
    
    print(f"\n🤖 Starting conversation with user: {test_user_id}")
    print("-" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n[Test {i}] {scenario['description']}")
        print(f"User: {scenario['input']}")
        
        try:
            response = graph_builder.process(test_user_id, scenario['input'])
            print(f"Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)
    
    print("\n✅ Test completed!")

def test_booking_retrieval():
    """Test booking retrieval functionality"""
    print("\n📋 Testing Booking Retrieval")
    print("=" * 30)
    
    try:
        graph_builder = HotelGraphBuilder()
        
        # Get bookings for test user
        bookings = graph_builder.agent.db.get_user_bookings("test_user_123")
        
        if bookings:
            print(f"Found {len(bookings)} booking(s):")
            for booking in bookings:
                print(f"- ID: {booking.booking_id}")
                print(f"  Guest: {booking.guest_name}")
                print(f"  Dates: {booking.check_in_date} to {booking.check_out_date}")
                print(f"  Room: {booking.room_type}")
                print(f"  Total: ${booking.total_price}")
                print(f"  Status: {booking.status}")
                print()
        else:
            print("No bookings found for test user")
            
    except Exception as e:
        print(f"❌ Error testing booking retrieval: {e}")

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment Configuration")
    print("=" * 40)
    
    required_vars = ["GEMINI_API_KEY"]
    optional_vars = ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_APP_SECRET", "INSTAGRAM_PAGE_ID"]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set (Required)")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set (Optional - needed for Instagram)")
    
    return all_good

def main():
    """Main test function"""
    print("🚀 Hotel Booking AI Agent - Test Suite")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please set required environment variables.")
        print("Copy .env.template to .env and fill in your API keys.")
        return
    
    # Run tests
    test_conversation_flow()
    test_booking_retrieval()
    
    print("\n🎉 All tests completed!")
    print("\nTo test Instagram integration:")
    print("1. Set Instagram API credentials in .env")
    print("2. Run: python main.py")
    print("3. Use ngrok to expose local webhook")
    print("4. Configure Instagram webhook URL")

if __name__ == "__main__":
    main()