from typing import Dict, TypedDict, Annotated, Sequence
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import settings
from src.database.operations import BookingOperations, ConversationOperations, get_db
from src.database.models import RoomType, BookingStatus
from src.agent.conversation_manager import conversation_manager
from datetime import datetime
import json
import re

# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    context: Annotated[Dict, "The current context of the conversation"]
    current_state: Annotated[str, "The current state of the conversation"]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.7
)

def detect_intent(message: str) -> str:
    """Detect user intent from the message."""
    msg = message.lower()
    
    # Reschedule intent (check this first to avoid conflicts)
    if any(word in msg for word in ["reschedule", "change", "modify", "update", "move", "rebook"]):
        return "reschedule"
    
    # Booking intent
    if any(word in msg for word in ["book", "reserve", "reservation", "room", "hotel", "stay"]):
        return "booking"
    
    # Question intent
    if any(word in msg for word in ["what", "how", "when", "where", "why", "?"]) or "?" in msg:
        return "question"
    
    # Default to booking if unclear
    return "booking"

def extract_dates(text: str) -> tuple[datetime, datetime]:
    """Extract check-in and check-out dates from text."""
    # This is a simple implementation. In a real system, you'd want more robust date parsing
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = re.findall(date_pattern, text)
    if len(dates) >= 2:
        return datetime.strptime(dates[0], '%Y-%m-%d'), datetime.strptime(dates[1], '%Y-%m-%d')
    return None, None

def extract_room_type(text: str) -> RoomType:
    """Extract room type from text."""
    text = text.lower()
    if 'suite' in text:
        return RoomType.SUITE
    elif 'deluxe' in text:
        return RoomType.DELUXE
    return RoomType.STANDARD

def calculate_price(room_type: RoomType, nights: int) -> float:
    """Calculate the total price for a booking."""
    base_prices = {
        RoomType.STANDARD: 100,
        RoomType.DELUXE: 150,
        RoomType.SUITE: 250
    }
    return base_prices[room_type] * nights

def process_booking_request(state: AgentState) -> AgentState:
    """Process the booking request and collect necessary information."""
    context = state["context"]
    message = state["messages"][-1].content
    
    # Initialize response variable
    response = ""
    
    # Ensure booking_step is initialized
    if "booking_step" not in context or context["booking_step"] is None:
        context["booking_step"] = "start"
    
    if context["booking_step"] == "start":
        response = "I'll help you book a room. Please provide your check-in and check-out dates in YYYY-MM-DD format."
        context["booking_step"] = "dates"
    elif context["booking_step"] == "dates":
        check_in, check_out = extract_dates(message)
        if check_in and check_out:
            context["check_in"] = check_in.isoformat()
            context["check_out"] = check_out.isoformat()
            response = "Great! What type of room would you like? We have Standard, Deluxe, and Suite rooms."
            context["booking_step"] = "room_type"
        else:
            response = "I couldn't understand the dates. Please provide them in YYYY-MM-DD format."
    elif context["booking_step"] == "room_type":
        room_type = extract_room_type(message)
        context["room_type"] = room_type.value
        response = "How many guests will be staying?"
        context["booking_step"] = "guests"
    elif context["booking_step"] == "guests":
        try:
            guests = int(re.search(r'\d+', message).group())
            context["guests"] = guests
            
            # Calculate price
            nights = (datetime.fromisoformat(context["check_out"]) - 
                     datetime.fromisoformat(context["check_in"])).days
            price = calculate_price(RoomType(context["room_type"]), nights)
            
            # Create booking
            db = next(get_db())
            booking = BookingOperations.create_booking(
                db=db,
                instagram_user_id=context.get("user_id", "unknown"),
                room_type=RoomType(context["room_type"]),
                check_in_date=datetime.fromisoformat(context["check_in"]),
                check_out_date=datetime.fromisoformat(context["check_out"]),
                number_of_guests=guests,
                total_price=price
            )
            
            response = f"Booking confirmed! Your booking ID is {booking.id}. Total price: ${price}"
            context["booking_step"] = "complete"
        except:
            response = "Please provide a valid number of guests."
    else:
        response = f"I'm sorry, I couldn't process your request. Current step: {context.get('booking_step', 'unknown')}. Please try again."
    
    state["messages"].append(AIMessage(content=response))
    return state

def process_reschedule_request(state: AgentState) -> AgentState:
    """Process the reschedule request."""
    context = state["context"]
    message = state["messages"][-1].content
    
    # Initialize response variable
    response = ""
    
    # Ensure reschedule_step is initialized
    if "reschedule_step" not in context or context["reschedule_step"] is None:
        context["reschedule_step"] = "start"
    
    if context["reschedule_step"] == "start":
        response = "Please provide your booking ID."
        context["reschedule_step"] = "booking_id"
    elif context["reschedule_step"] == "booking_id":
        try:
            booking_id = int(re.search(r'\d+', message).group())
            db = next(get_db())
            booking = BookingOperations.get_booking(db, booking_id)
            
            if booking and booking.instagram_user_id == context.get("user_id", "unknown"):
                context["booking_id"] = booking_id
                response = "Please provide your new check-in and check-out dates in YYYY-MM-DD format."
                context["reschedule_step"] = "new_dates"
            else:
                response = "Booking not found. Please check your booking ID."
                context["reschedule_step"] = "start"
        except:
            response = "Please provide a valid booking ID."
    elif context["reschedule_step"] == "new_dates":
        check_in, check_out = extract_dates(message)
        if check_in and check_out:
            db = next(get_db())
            booking = BookingOperations.get_booking(db, context["booking_id"])
            
            if booking:
                booking.check_in_date = check_in
                booking.check_out_date = check_out
                db.commit()
                response = "Your booking has been rescheduled successfully!"
                context["reschedule_step"] = "complete"
            else:
                response = "An error occurred. Please try again."
                context["reschedule_step"] = "start"
        else:
            response = "I couldn't understand the dates. Please provide them in YYYY-MM-DD format."
    else:
        response = f"I'm sorry, I couldn't process your request. Current step: {context.get('reschedule_step', 'unknown')}. Please try again."
    
    state["messages"].append(AIMessage(content=response))
    return state

def answer_hotel_questions(state: AgentState) -> AgentState:
    """Answer general hotel-related questions."""
    message = state["messages"][-1].content
    
    # Create a prompt for the LLM
    prompt = f"""You are a helpful hotel assistant. Please answer the following question about our hotel:
    {message}
    
    Our hotel features:
    - 24/7 room service
    - Free WiFi
    - Swimming pool
    - Fitness center
    - Restaurant
    - Spa
    - Business center
    
    Check-in time: {settings.DEFAULT_CHECK_IN_TIME}
    Check-out time: {settings.DEFAULT_CHECK_OUT_TIME}
    """
    
    try:
        response = llm.invoke(prompt)
        state["messages"].append(AIMessage(content=response.content))
    except Exception as e:
        # Fallback response if LLM fails
        fallback_responses = {
            "check-in": f"Check-in time is {settings.DEFAULT_CHECK_IN_TIME}",
            "check-out": f"Check-out time is {settings.DEFAULT_CHECK_OUT_TIME}",
            "amenities": "We offer 24/7 room service, free WiFi, swimming pool, fitness center, restaurant, spa, and business center.",
            "pool": "Yes, we have a swimming pool available for all guests.",
            "wifi": "Free WiFi is available throughout the hotel.",
            "parking": "Complimentary parking is available for all guests."
        }
        
        # Simple keyword matching for fallback
        msg_lower = message.lower()
        if "check-in" in msg_lower or "checkin" in msg_lower:
            response_content = fallback_responses["check-in"]
        elif "check-out" in msg_lower or "checkout" in msg_lower:
            response_content = fallback_responses["check-out"]
        elif "amenities" in msg_lower or "facilities" in msg_lower:
            response_content = fallback_responses["amenities"]
        elif "pool" in msg_lower:
            response_content = fallback_responses["pool"]
        elif "wifi" in msg_lower or "internet" in msg_lower:
            response_content = fallback_responses["wifi"]
        elif "parking" in msg_lower:
            response_content = fallback_responses["parking"]
        else:
            response_content = "I'm sorry, I couldn't process your request. Please try asking about check-in times, amenities, or other hotel services."
        
        state["messages"].append(AIMessage(content=response_content))
    
    return state

def process_message(message: str, user_id: str) -> str:
    """Process an incoming message and return the response."""
    # Get user's conversation context
    user_context = conversation_manager.get_user_context(user_id)
    
    # Detect intent if not already set or if starting a new conversation
    if not user_context["intent"] or not conversation_manager.is_conversation_active(user_id):
        intent = detect_intent(message)
        conversation_manager.update_user_context(user_id, {"intent": intent})
    else:
        intent = user_context["intent"]
    
    # Initialize the state with user context
    state = {
        "messages": [HumanMessage(content=message)],
        "context": {
            "user_id": user_id,
            "intent": intent,
            "booking_step": user_context.get("booking_step"),
            "reschedule_step": user_context.get("reschedule_step"),
            **user_context.get("booking_data", {}),
            **user_context.get("reschedule_data", {})
        },
        "current_state": "start"
    }
    
    # Route based on intent
    if intent == "booking":
        result = process_booking_request(state)
        # Update conversation context
        conversation_manager.update_user_context(user_id, {
            "booking_step": result["context"].get("booking_step"),
            "booking_data": {
                k: v for k, v in result["context"].items() 
                if k in ["check_in", "check_out", "room_type", "guests"]
            }
        })
        return result["messages"][-1].content
        
    elif intent == "reschedule":
        result = process_reschedule_request(state)
        # Update conversation context
        conversation_manager.update_user_context(user_id, {
            "reschedule_step": result["context"].get("reschedule_step"),
            "reschedule_data": {
                k: v for k, v in result["context"].items() 
                if k in ["booking_id"]
            }
        })
        return result["messages"][-1].content
        
    elif intent == "question":
        result = answer_hotel_questions(state)
        return result["messages"][-1].content
        
    else:
        return "I'm sorry, I couldn't understand your request. Please try asking about booking a room, rescheduling, or hotel information." 