from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Booking, Conversation, ConversationMessage, BookingStatus, RoomType
from datetime import datetime
import json
from config.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingOperations:
    @staticmethod
    def create_booking(db, instagram_user_id: str, room_type: RoomType, 
                      check_in_date: datetime, check_out_date: datetime,
                      number_of_guests: int, total_price: float) -> Booking:
        """Create a new booking."""
        booking = Booking(
            instagram_user_id=instagram_user_id,
            room_type=room_type,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_guests=number_of_guests,
            total_price=total_price,
            status=BookingStatus.PENDING
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_booking(db, booking_id: int) -> Booking:
        """Get a booking by ID."""
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def get_user_bookings(db, instagram_user_id: str) -> list[Booking]:
        """Get all bookings for a user."""
        return db.query(Booking).filter(Booking.instagram_user_id == instagram_user_id).all()

    @staticmethod
    def update_booking_status(db, booking_id: int, status: BookingStatus) -> Booking:
        """Update the status of a booking."""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.status = status
            db.commit()
            db.refresh(booking)
        return booking

class ConversationOperations:
    @staticmethod
    def create_conversation(db, instagram_user_id: str, state: str, context: dict) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            instagram_user_id=instagram_user_id,
            state=state,
            context=json.dumps(context)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_latest_conversation(db, instagram_user_id: str) -> Conversation:
        """Get the latest conversation for a user."""
        return db.query(Conversation)\
            .filter(Conversation.instagram_user_id == instagram_user_id)\
            .order_by(Conversation.created_at.desc())\
            .first()

    @staticmethod
    def update_conversation(db, conversation_id: int, state: str, context: dict) -> Conversation:
        """Update a conversation."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.state = state
            conversation.context = json.dumps(context)
            db.commit()
            db.refresh(conversation)
        return conversation

    @staticmethod
    def store_message(db, instagram_user_id: str, message: str, is_from_user: bool, timestamp: datetime = None) -> ConversationMessage:
        """Store a message in the conversation."""
        if timestamp is None:
            timestamp = datetime.now()
            
        conversation_message = ConversationMessage(
            instagram_user_id=instagram_user_id,
            message=message,
            is_from_user=is_from_user,
            timestamp=timestamp
        )
        db.add(conversation_message)
        db.commit()
        db.refresh(conversation_message)
        return conversation_message

    @staticmethod
    def get_conversation_history(db, instagram_user_id: str, limit: int = 50) -> list[ConversationMessage]:
        """Get conversation history for a user."""
        return db.query(ConversationMessage)\
            .filter(ConversationMessage.instagram_user_id == instagram_user_id)\
            .order_by(ConversationMessage.timestamp.desc())\
            .limit(limit)\
            .all() 