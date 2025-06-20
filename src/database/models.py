from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class RoomType(enum.Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    instagram_user_id = Column(String, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    instagram_user_id = Column(String, nullable=False)
    state = Column(String, nullable=False)
    context = Column(String)  # JSON string to store conversation context
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    instagram_user_id = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_from_user = Column(Boolean, nullable=False, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow) 