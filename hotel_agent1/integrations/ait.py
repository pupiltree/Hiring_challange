from ai_client import AIClient
import time

def run_tests():
    print("🚀 Starting AI Client Tests...")
    client = AIClient()
    
    # Test 1: Basic greeting
    print("\n🔹 Test 1: Basic Greeting")
    intent = client.extract_intent("Hello there!")
    print(f"Intent: {intent} (Expected: greeting)")
    
    # Test 2: Booking intent
    print("\n🔹 Test 2: Booking Intent")
    intent = client.extract_intent("I want to book a room")
    print(f"Intent: {intent} (Expected: booking)")
    
    # Test 3: Extract booking info
    print("\n🔹 Test 3: Extract Booking Info")
    message = "My name is John Doe, email john@example.com, phone 555-1234. I want a deluxe room from 2025-07-01 to 2025-07-05 for 2 guests."
    booking_data = client.extract_booking_info(message)
    print("Extracted Data:")
    for key, value in booking_data.items():
        print(f"{key}: {value}")
    
    # Test 4: Generate response
    print("\n🔹 Test 4: Generate Response")
    response = client.generate_response("What time is check-in?")
    print(f"Response: {response}")
    
    # Test 5: Contextual response
    print("\n🔹 Test 5: Contextual Response")
    context = {"current_status": "in_booking_process"}
    response = client.generate_response("What should I do next?", context)
    print(f"Response with context: {response}")

if __name__ == "__main__":
    start_time = time.time()
    run_tests()
    print(f"\n✅ Tests completed in {time.time() - start_time:.2f} seconds")
