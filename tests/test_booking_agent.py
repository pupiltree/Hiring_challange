import pytest
from datetime import datetime, timedelta
from src.agent.booking_agent import (
    process_booking_request,
    process_reschedule_request,
    answer_hotel_questions,
    extract_dates,
    extract_room_type,
    calculate_price
)
from src.database.models import RoomType, BookingStatus
from src.database.operations import BookingOperations, ConversationOperations
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def sample_state():
    return {
        "messages": [],
        "context": {"user_id": "test_user"},
        "current_state": "start"
    }

def test_extract_dates():
    # Test valid dates
    text = "I want to book from 2024-03-01 to 2024-03-05"
    check_in, check_out = extract_dates(text)
    assert check_in == datetime(2024, 3, 1)
    assert check_out == datetime(2024, 3, 5)
    
    # Test invalid dates
    text = "I want to book for next week"
    check_in, check_out = extract_dates(text)
    assert check_in is None
    assert check_out is None

def test_extract_room_type():
    assert extract_room_type("I want a suite") == RoomType.SUITE
    assert extract_room_type("deluxe room please") == RoomType.DELUXE
    assert extract_room_type("standard room") == RoomType.STANDARD
    assert extract_room_type("any room") == RoomType.STANDARD

def test_calculate_price():
    assert calculate_price(RoomType.STANDARD, 2) == 200
    assert calculate_price(RoomType.DELUXE, 3) == 450
    assert calculate_price(RoomType.SUITE, 1) == 250

def test_process_booking_request(sample_state):
    # Test initial booking request
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="I want to book a room")]
    result = process_booking_request(state)
    assert "check-in and check-out dates" in result["messages"][-1].content
    
    # Test date input
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="2024-03-01 to 2024-03-05")]
    state["context"]["booking_step"] = "dates"
    result = process_booking_request(state)
    assert "What type of room" in result["messages"][-1].content
    
    # Test room type input
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="suite")]
    state["context"]["booking_step"] = "room_type"
    state["context"]["check_in"] = "2024-03-01T00:00:00"
    state["context"]["check_out"] = "2024-03-05T00:00:00"
    result = process_booking_request(state)
    assert "How many guests" in result["messages"][-1].content

def test_process_reschedule_request(sample_state):
    # Test initial reschedule request
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="I want to reschedule")]
    result = process_reschedule_request(state)
    assert "booking ID" in result["messages"][-1].content
    
    # Test invalid booking ID
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="invalid")]
    state["context"]["reschedule_step"] = "booking_id"
    result = process_reschedule_request(state)
    assert "valid booking ID" in result["messages"][-1].content

def test_answer_hotel_questions(sample_state):
    state = sample_state.copy()
    state["messages"] = [HumanMessage(content="What time is check-in?")]
    result = answer_hotel_questions(state)
    assert result["messages"][-1].content is not None 