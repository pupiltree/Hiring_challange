# AI Agent for Hotel Bookings (LangGraph & LLMs)

We're growing our tech team at Powersmy.biz ([https://powersmy.biz/](https://powersmy.biz/)) and have an exciting paid internship opportunity for students who love solving real-world problems and building impactful products. If you're passionate about conversational AI and ready to build intelligent agents, we want you! 🙌

**Stipend:** Rs. 20,000 (Remote) / Rs. 25,000 (On-Site) - Negotiable

**Deadline:** 20th June

## Challenge Overview

Build an AI agent using **LangGraph, LangChain, and any LLM of your choice (Gemini, Groq, OpenAI, etc.)** that can handle hotel room bookings, reschedule existing reservations, and answer basic hotel-related questions. The agent must be able to interact with users through Instagram DMs, providing a seamless and context-aware conversational experience. This challenge tests your ability to build, deploy, and manage a sophisticated, stateful AI agent.

## Core Functionality

1.  **Create a conversational AI agent that can:**
    * **Book a hotel room:** Guide the user through the booking process, collecting necessary details (e.g., check-in/check-out dates, room type, number of guests).
    * **Reschedule a booking:** Allow users to modify their existing reservation dates.
    * **Answer hotel-related questions:** Respond to basic queries about the hotel (e.g., amenities, check-in times, location).
    * **Maintain conversation history:** Keep track of the conversation to provide context-aware and relevant responses.

2.  **Integrate the agent with Instagram:**
    * Use the **Instagram Graph API** (free to use) to send and receive direct messages.

3.  **Manage Data:**
    * Store reservation data in a lightweight database (e.g., **JSON file or SQLite**).

---

## Technical Requirements

* **Frameworks:** LangGraph, LangChain
* **LLM:** Any LLM of your choice (Gemini, Groq, OpenAI, Claude, etc.)
  * **Note:** If you don't have access to paid LLM APIs, you can use free options like Groq, Gemini Flash models, or other free-tier LLM services
* **API:** Instagram Graph API
* **Database:** JSON file or a lightweight database like SQLite.
* **Error Handling:** Implement robust error handling for API failures and user input issues.
* **State Management:** The agent must effectively manage conversational state using LangGraph.

> **Note:** For this challenge, you can assume any hotel data or API responses as needed. This means you can create mock data for hotel information, room availability, pricing, etc., without needing to integrate with actual hotel APIs.

## Evaluation Criteria

* **Functionality:** Does the agent successfully handle booking, rescheduling, and Q&A?
* **LangGraph Implementation:** Quality and clarity of the state machine graph.
* **Code Quality:** Organization, readability, and efficiency of your code.
* **Problem-Solving:** Your creative approach to building the conversational flow.
* **Documentation:** Clarity of your setup instructions and explanations.

---

## Submission Guidelines

1.  **Fork our challenge repository.**
2.  **Create a new branch** for your implementation.
3.  **Include a comprehensive `README.md` with:**
    * Detailed setup instructions.
    * An explanation of your agent's architecture.
    * A justification for your design choices.
4.  **Provide a LangGraph flow diagram** illustrating the agent's conversational states and transitions.
5.  **Submit the complete source code** by creating a pull request to our main repository.

## Getting Started

The Instagram Graph API is free to use for this challenge. You can set up your own developer account and obtain the necessary credentials from the Facebook Developer Portal.

**LLM Options:** If you don't have access to paid LLM APIs, there are several free alternatives available:
* **Groq** - Fast inference with free tier
* **Google Gemini Flash** - Free tier available
* **Hugging Face Inference API** - Free tier for many models
* **Ollama** - Run open-source models locally

For any queries, feel free to email us at founders@powersmy.biz ✉️! 
