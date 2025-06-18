from datetime import datetime, timedelta
import uuid
from typing import Dict, Any, Optional
from models.booking_models import Booking, ConversationState
from database.db_manager import DatabaseManager
from integrations.ai_client import AIClient
from config import Config

class HotelAgent:
    def __init__(self):
        self.db = DatabaseManager()
        self.gemini = AIClient()
        self.hotel_info = self._load_hotel_info()
    
    def _load_hotel_info(self) -> Dict[str, Any]:
        """Load hotel information"""
        return {
            "name": Config.HOTEL_NAME,
            "address": Config.HOTEL_ADDRESS,
            "check_in_time": Config.CHECK_IN_TIME,
            "check_out_time": Config.CHECK_OUT_TIME,
            "amenities": [
                "Free WiFi", "Swimming Pool", "Gym", "Spa", "Restaurant",
                "Room Service", "Concierge", "Parking", "Business Center"
            ],
            "room_types": {
                "standard": {"price": 150, "capacity": 2, "description": "Comfortable standard room with city view"},
                "deluxe": {"price": 220, "capacity": 3, "description": "Spacious deluxe room with premium amenities"},
                "suite": {"price": 350, "capacity": 4, "description": "Luxury suite with separate living area"}
            }
        }
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process user message and return response"""
        try:
            # Get or create conversation state
            state = self.db.get_conversation_state(user_id)
            if not state:
                state = ConversationState(user_id=user_id)
            
            # Extract intent
            intent = self.gemini.extract_intent(message)
            
            # Update state
            state.last_message = message
            
            # Route to appropriate handler
            if intent == "greeting":
                response = self._handle_greeting(state)
            elif intent == "booking":
                response = self._handle_booking_flow(state, message)
            elif intent == "reschedule":
                response = self._handle_reschedule_flow(state, message)
            elif intent == "cancel":
                response = self._handle_cancel_flow(state, message)
            elif intent == "inquiry":
                response = self._handle_inquiry(state, message)
            else:
                response = self._handle_default(state, message)
            
            # Save updated state
            self.db.save_conversation_state(state)
            
            return response
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error. Please try again."
    
    def _handle_greeting(self, state: ConversationState) -> str:
        """Handle greeting messages"""
        state.current_step = "greeting"
        return f"Hello! Welcome to {self.hotel_info['name']}! 🏨\n\nI can help you with:\n• Making a new reservation\n• Rescheduling existing bookings\n• Answering questions about our hotel\n\nHow can I assist you today?"
    
    def _handle_booking_flow(self, state: ConversationState, message: str) -> str:
        """Handle booking flow"""
        if state.current_step not in ["booking_dates", "booking_room", "booking_guests", "booking_details", "booking_confirm"]:
            state.current_step = "booking_dates"
            state.booking_data = {}
        
        # Extract booking information
        booking_info = self.gemini.extract_booking_info(message)
        state.booking_data.update({k: v for k, v in booking_info.items() if v is not None})
        
        # Determine what information is still needed
        missing_info = []
        if not state.booking_data.get("check_in_date"):
            missing_info.append("check-in date")
        if not state.booking_data.get("check_out_date"):
            missing_info.append("check-out date")
        if not state.booking_data.get("room_type"):
            missing_info.append("room type")
        if not state.booking_data.get("num_guests"):
            missing_info.append("number of guests")
        if not state.booking_data.get("guest_name"):
            missing_info.append("guest name")
        if not state.booking_data.get("guest_email"):
            missing_info.append("email address")
        if not state.booking_data.get("guest_phone"):
            missing_info.append("phone number")
        
        if missing_info:
            # Ask for missing information
            if "check-in date" in missing_info or "check-out date" in missing_info:
                return "I'd be happy to help you book a room! 📅\n\nPlease provide your check-in and check-out dates (e.g., 'December 25 to December 28')."
            elif "room type" in missing_info:
                room_info = "\n".join([f"• {room.title()}: ${info['price']}/night - {info['description']}" 
                                     for room, info in self.hotel_info['room_types'].items()])
                return f"Great! Here are our available room types:\n\n{room_info}\n\nWhich room type would you prefer?"
            elif "number of guests" in missing_info:
                return "How many guests will be staying?"
            elif any(detail in missing_info for detail in ["guest_name", "guest_email", "guest_phone"]):
                needed = [info for info in ["guest_name", "guest_email", "guest_phone"] if info in missing_info]
                return f"Almost done! I need your {', '.join(needed).replace('guest_', '').replace('_', ' ')} to complete the booking."
        
        # All information collected - create booking
        return self._create_booking(state)
    
    def _create_booking(self, state: ConversationState) -> str:
        """Create booking with collected information"""
        try:
            booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate total price
            room_type = state.booking_data["room_type"].lower()
            room_price = self.hotel_info["room_types"][room_type]["price"]
            
            # Calculate number of nights
            check_in = datetime.strptime(state.booking_data["check_in_date"], "%Y-%m-%d")
            check_out = datetime.strptime(state.booking_data["check_out_date"], "%Y-%m-%d")
            nights = (check_out - check_in).days
            total_price = room_price * nights
            
            # Create booking
            booking = Booking(
                booking_id=booking_id,
                user_id=state.user_id,
                check_in_date=state.booking_data["check_in_date"],
                check_out_date=state.booking_data["check_out_date"],
                room_type=state.booking_data["room_type"],
                num_guests=int(state.booking_data["num_guests"]),
                guest_name=state.booking_data["guest_name"],
                guest_email=state.booking_data["guest_email"],
                guest_phone=state.booking_data["guest_phone"],
                total_price=total_price
            )
            
            # Save booking
            if self.db.save_booking(booking):
                state.current_step = "completed"
                state.booking_data = {}
                
                return f"🎉 Booking Confirmed!\n\nBooking ID: {booking_id}\nGuest: {booking.guest_name}\nRoom: {booking.room_type.title()}\nDates: {booking.check_in_date} to {booking.check_out_date}\nGuests: {booking.num_guests}\nTotal: ${total_price:.2f} ({nights} nights)\n\nCheck-in: {Config.CHECK_IN_TIME}\nCheck-out: {Config.CHECK_OUT_TIME}\n\nThank you for choosing {Config.HOTEL_NAME}!"
            else:
                return "I'm sorry, there was an error creating your booking. Please try again."
                
        except Exception as e:
            print(f"Error creating booking: {e}")
            return "I'm sorry, there was an error processing your booking. Please try again."
    
    def _handle_reschedule_flow(self, state: ConversationState, message: str) -> str:
        """Handle rescheduling flow"""
        # Extract booking ID and new dates from message
        words = message.split()
        booking_id = None
        
        # Look for booking ID pattern
        for word in words:
            if word.startswith("BK") and len(word) == 10:
                booking_id = word
                break
        
        if not booking_id:
            return "To reschedule your booking, please provide your booking ID (e.g., BK12345678)."
        
        # Get existing booking
        booking = self.db.get_booking(booking_id)
        if not booking:
            return "I couldn't find a booking with that ID. Please check and try again."
        
        # Extract new dates
        booking_info = self.gemini.extract_booking_info(message)
        if not booking_info.get("check_in_date") or not booking_info.get("check_out_date"):
            return f"I found your booking for {booking.guest_name}. Please provide your new check-in and check-out dates."
        
        # Update booking
        booking.check_in_date = booking_info["check_in_date"]
        booking.check_out_date = booking_info["check_out_date"]
        
        # Recalculate price
        room_price = self.hotel_info["room_types"][booking.room_type.lower()]["price"]
        check_in = datetime.strptime(booking.check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(booking.check_out_date, "%Y-%m-%d")
        nights = (check_out - check_in).days
        booking.total_price = room_price * nights
        
        if self.db.save_booking(booking):
            return f"✅ Booking Rescheduled!\n\nBooking ID: {booking.booking_id}\nNew Dates: {booking.check_in_date} to {booking.check_out_date}\nUpdated Total: ${booking.total_price:.2f}\n\nYour booking has been successfully updated!"
        else:
            return "Sorry, there was an error updating your booking. Please try again."
    
    def _handle_cancel_flow(self, state: ConversationState, message: str) -> str:
        """Handle cancellation flow"""
        words = message.split()
        booking_id = None
        
        for word in words:
            if word.startswith("BK") and len(word) == 10:
                booking_id = word
                break
        
        if not booking_id:
            return "To cancel your booking, please provide your booking ID (e.g., BK12345678)."
        
        booking = self.db.get_booking(booking_id)
        if not booking:
            return "I couldn't find a booking with that ID. Please check and try again."
        
        booking.status = "cancelled"
        if self.db.save_booking(booking):
            return f"❌ Booking Cancelled\n\nBooking ID: {booking.booking_id}\nGuest: {booking.guest_name}\n\nYour booking has been cancelled. If you need assistance, please contact us."
        else:
            return "Sorry, there was an error cancelling your booking. Please try again."
    
    def _handle_inquiry(self, state: ConversationState, message: str) -> str:
        """Handle general inquiries"""
        # Use Gemini to generate contextual response
        context = {
            "hotel_name": self.hotel_info["name"],
            "address": self.hotel_info["address"],
            "check_in_time": self.hotel_info["check_in_time"],
            "check_out_time": self.hotel_info["check_out_time"],
            "amenities": self.hotel_info["amenities"],
            "room_types": self.hotel_info["room_types"]
        }
        
        prompt = f"""
        You are a helpful hotel concierge. Answer this guest's question about the hotel.
        Use the hotel information provided in context.
        
        Guest question: "{message}"
        
        Hotel information: {context}
        
        Provide a helpful, friendly response.
        """
        
        return self.gemini.generate_response(prompt, context)
    
    def _handle_default(self, state: ConversationState, message: str) -> str:
        """Handle default/unrecognized messages"""
        return "I'm not sure how to help with that. I can assist you with:\n• Making hotel reservations\n• Rescheduling bookings\n• Answering questions about our hotel\n\nWhat would you like to do?"