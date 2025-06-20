from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from src.agent.booking_agent import process_message
from src.instagram.client import InstagramClient
from src.database.operations import ConversationOperations, get_db
from config.config import settings
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Booking AI Agent",
    description="AI-powered hotel booking agent with Instagram integration",
    version="1.0.0"
)

# Initialize Instagram client
instagram_client = InstagramClient()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Hotel Booking AI Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """Verify Instagram webhook for subscription."""
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    challenge = instagram_client.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    
    if challenge:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(challenge)
    else:
        logger.error("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming Instagram messages."""
    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
        
        # Parse the message from Instagram
        message_data = instagram_client.parse_webhook_message(body)
        
        if not message_data:
            logger.warning("No valid message found in webhook")
            return {"status": "no_message"}
        
        user_id = message_data["user_id"]
        message_text = message_data["message"]
        timestamp = message_data["timestamp"]
        
        logger.info(f"Processing message from user {user_id}: {message_text}")
        
        # Store the incoming message
        db = next(get_db())
        ConversationOperations.store_message(
            db=db,
            instagram_user_id=user_id,
            message=message_text,
            is_from_user=True,
            timestamp=datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        )
        
        # Process the message with our AI agent
        try:
            response = process_message(message_text, user_id)
            logger.info(f"Agent response: {response}")
            
            # Store the agent response
            ConversationOperations.store_message(
                db=db,
                instagram_user_id=user_id,
                message=response,
                is_from_user=False,
                timestamp=datetime.now()
            )
            
            # Send response back to Instagram
            success = instagram_client.send_message(user_id, response)
            
            if success:
                logger.info(f"Response sent successfully to user {user_id}")
                return {"status": "success", "message": "Response sent"}
            else:
                logger.error(f"Failed to send response to user {user_id}")
                return {"status": "error", "message": "Failed to send response"}
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = "I'm sorry, I encountered an error processing your request. Please try again."
            instagram_client.send_message(user_id, error_response)
            return {"status": "error", "message": str(e)}
            
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
async def send_message(request: Request):
    """Send a message to a user (for testing purposes)."""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id and message are required")
        
        success = instagram_client.send_message(user_id, message)
        
        if success:
            return {"status": "success", "message": "Message sent"}
        else:
            return {"status": "error", "message": "Failed to send message"}
            
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings/{user_id}")
async def get_user_bookings(user_id: str):
    """Get all bookings for a specific user."""
    try:
        db = next(get_db())
        from src.database.operations import BookingOperations
        
        bookings = BookingOperations.get_bookings_by_user(db, user_id)
        
        return {
            "user_id": user_id,
            "bookings": [
                {
                    "id": booking.id,
                    "room_type": booking.room_type.value,
                    "check_in_date": booking.check_in_date.isoformat(),
                    "check_out_date": booking.check_out_date.isoformat(),
                    "number_of_guests": booking.number_of_guests,
                    "total_price": booking.total_price,
                    "status": booking.status.value,
                    "created_at": booking.created_at.isoformat()
                }
                for booking in bookings
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str):
    """Get conversation history for a specific user."""
    try:
        db = next(get_db())
        conversations = ConversationOperations.get_conversation_history(db, user_id)
        
        return {
            "user_id": user_id,
            "conversations": [
                {
                    "message": conv.message,
                    "is_from_user": conv.is_from_user,
                    "timestamp": conv.timestamp.isoformat()
                }
                for conv in conversations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    ) 