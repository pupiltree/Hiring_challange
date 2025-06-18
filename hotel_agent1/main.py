from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from agents.graph_builder import HotelGraphBuilder
from integrations.instagram_client import InstagramClient
from config import Config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hotel Booking AI Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
graph_builder = HotelGraphBuilder()
instagram_client = InstagramClient()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Hotel Booking AI Agent is running!", "status": "healthy"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify Instagram webhook"""
    params = request.query_params
    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    verified_challenge = instagram_client.verify_webhook(verify_token, challenge)
    if verified_challenge:
        logger.info("Webhook verified successfully")
        return int(verified_challenge)
    else:
        logger.error("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle Instagram webhook messages"""
    try:
        webhook_data = await request.json()
        logger.info(f"Received webhook data: {webhook_data}")
        
        # Parse message
        message_data = instagram_client.parse_webhook_message(webhook_data)
        if not message_data:
            return {"status": "no_message"}
        
        sender_id = message_data["sender_id"]
        message_text = message_data["message_text"]
        
        logger.info(f"Processing message from {sender_id}: {message_text}")
        
        # Process through agent
        response = graph_builder.process(sender_id, message_text)
        
        # Send response back to Instagram
        success = instagram_client.send_message(sender_id, response)
        
        if success:
            logger.info(f"Response sent successfully to {sender_id}")
            return {"status": "success", "response": response}
        else:
            logger.error(f"Failed to send response to {sender_id}")
            return {"status": "error", "message": "Failed to send response"}
            
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/chat")
async def chat_endpoint(request: Request):
    """Direct chat endpoint for testing"""
    try:
        data = await request.json()
        user_id = data.get("user_id", "test_user")
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process through agent
        response = graph_builder.process(user_id, message)
        
        return {
            "user_id": user_id,
            "message": message,
            "response": response,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings/{user_id}")
async def get_user_bookings(user_id: str):
    """Get all bookings for a user"""
    try:
        bookings = graph_builder.agent.db.get_user_bookings(user_id)
        return {
            "user_id": user_id,
            "bookings": [booking.to_dict() for booking in bookings],
            "count": len(bookings)
        }
    except Exception as e:
        logger.error(f"Error getting bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/booking/{booking_id}")
async def get_booking(booking_id: str):
    """Get specific booking details"""
    try:
        booking = graph_builder.agent.db.get_booking(booking_id)
        if booking:
            return booking.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Booking not found")
    except Exception as e:
        logger.error(f"Error getting booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotel-info")
async def get_hotel_info():
    """Get hotel information"""
    return graph_builder.agent.hotel_info

def main():
    """Main function to run the application"""
    logger.info("Starting Hotel Booking AI Agent...")
    logger.info(f"Hotel: {Config.HOTEL_NAME}")
    
    # Check if required environment variables are set
    if not Config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set in environment variables")
        return
    
    logger.info("All configurations loaded successfully")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()