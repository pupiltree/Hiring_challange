# Hotel Booking AI Agent – Internship Challenge

This is my solution to the Powersmy.biz internship challenge. The goal was to build an intelligent, stateful AI agent that can handle hotel room bookings, rescheduling, and general queries – integrated with the Instagram DM experience.

---

## 🔧 Tech Stack

- **LangChain** – to interact with Google Gemini (PaLM).
- **LangGraph** – for managing conversation state.
- **Gemini LLM (PaLM API)** – for understanding and generating responses.
- **JSON** – as a lightweight database to store bookings.
- **Python** – for logic, agent pipeline, and flow.

---

## ✅ Features

- Book hotel rooms by collecting check-in/check-out, room type, and guests.
- Reschedule an existing reservation.
- Answer FAQs like check-in times, amenities, etc.
- Maintain user context for better flow.
- Designed for future integration with Instagram Graph API.

---

## 🚀 Setup Instructions

1. **Clone the fork**:

```bash
git clone https://github.com/Bhavika42/Hiring_challange-bhavika/new/bhavika-internship-solution
cd bhavika-internship-solution


Install dependencies:
pip install -r requirements.txt

Add your Gemini API key in agent.py:
llm = ChatGooglePalm(google_api_key="API_KEY")
i will get the key by messaging +91 91796 87775 or +91 70248 04485.

Run:
python main.py


🌐 LangGraph Flow Diagram
graph TD
    A[Idle] -->|User says 'book'| B[Booking]
    A -->|User says 'reschedule'| C[Rescheduling]
    A -->|User asks FAQ| D[FAQ]
    A -->|Unknown input| E[Fallback]
    B --> A
    C --> A
    D --> A
    E --> A


💡 Design Choices
LangGraph is used to ensure scalable and clear state management.

JSON used for simplicity to simulate backend database logic.

Gemini via LangChain ensures flexibility and minimal LLM code.

Clean modular files: agent, state logic, and database separated.


Thanks for reviewing my submission! Looking forward to contributing and learning with the Powersmy.biz team 🚀
