# agent.py

from langchain.chat_models import ChatGooglePalm
from langchain.schema import HumanMessage

llm = ChatGooglePalm(google_api_key="YOUR_GEMINI_API_KEY")

def respond_to_user(message):
    response = llm([HumanMessage(content=message)])
    return response.content

# Demo
if __name__ == "__main__":
    print(respond_to_user("Hi, I want to book a hotel room."))
