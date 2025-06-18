from langchain.chat_models import ChatGooglePalm
from langchain.schema import HumanMessage

llm = ChatGooglePalm(google_api_key="API_KEY") 

def get_reply(msg):
    return llm([HumanMessage(content=msg)]).content
