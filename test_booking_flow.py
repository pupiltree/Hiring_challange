#!/usr/bin/env python3
"""
Simple test script for the booking flow
"""

def test_booking_flow():
    """Test the complete booking flow."""
    try:
        from src.agent.booking_agent import process_message
        
        user_id = "test_user_123"
        
        print("🧪 Testing Booking Flow")
        print("=" * 50)
        
        # Step 1: Start booking
        print("1. User: I want to book a room")
        response1 = process_message("I want to book a room", user_id)
        print(f"   Agent: {response1}")
        print()
        
        # Step 2: Provide dates
        print("2. User: 2024-03-01 to 2024-03-05")
        response2 = process_message("2024-03-01 to 2024-03-05", user_id)
        print(f"   Agent: {response2}")
        print()
        
        # Step 3: Provide room type
        print("3. User: suite")
        response3 = process_message("suite", user_id)
        print(f"   Agent: {response3}")
        print()
        
        # Step 4: Provide guests
        print("4. User: 2")
        response4 = process_message("2", user_id)
        print(f"   Agent: {response4}")
        print()
        
        print("✅ Booking flow test completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_reschedule_flow():
    """Test the reschedule flow."""
    try:
        from src.agent.booking_agent import process_message
        
        user_id = "test_user_456"
        
        print("\n🔄 Testing Reschedule Flow")
        print("=" * 50)
        
        # Step 1: Start reschedule
        print("1. User: I want to reschedule")
        response1 = process_message("I want to reschedule", user_id)
        print(f"   Agent: {response1}")
        print()
        
        # Step 2: Provide booking ID
        print("2. User: 123")
        response2 = process_message("123", user_id)
        print(f"   Agent: {response2}")
        print()
        
        # Step 3: Provide new dates
        print("3. User: 2024-03-10 to 2024-03-15")
        response3 = process_message("2024-03-10 to 2024-03-15", user_id)
        print(f"   Agent: {response3}")
        print()
        
        print("✅ Reschedule flow test completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_qa_flow():
    """Test the Q&A flow."""
    try:
        from src.agent.booking_agent import process_message
        
        user_id = "test_user_789"
        
        print("\n❓ Testing Q&A Flow")
        print("=" * 50)
        
        questions = [
            "What time is check-in?",
            "Do you have a swimming pool?",
            "What amenities do you offer?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. User: {question}")
            response = process_message(question, user_id)
            print(f"   Agent: {response}")
            print()
        
        print("✅ Q&A flow test completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Hotel Booking Agent Tests")
    print("=" * 60)
    
    # Test all flows
    test_booking_flow()
    test_reschedule_flow()
    test_qa_flow()
    
    print("\n🎉 All tests completed!") 