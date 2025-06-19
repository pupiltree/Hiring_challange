# src/agent.py
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import GooglePalm
from langgraph import LangGraph
from instagram_client import InstagramClient
from db import BookingDB

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2-alpha-0314")

class HotelAgent:
    def __init__(self):
        # load the LangGraph flow
        self.flow   = LangGraph.from_json("langgraph/booking_flow.json")
        # try to instantiate Gemini (PaLM)
        try:
            self.llm = GooglePalm(model_name=GEMINI_MODEL)
        except Exception as e:
            print(f"[Agent] GooglePalm init failed: {e}")
            # fallback dummy LLM: just echoes a placeholder
            class DummyLLM:
                def predict(self, **kwargs):
                    return "Sorry, the AI is currently unavailable."
            self.llm = DummyLLM()
        self.client = InstagramClient()
        self.db     = BookingDB()

    def _safe_reply(self, user_id, text):
        self.client.send_message(user_id, text)

    def handle_message(self, user_id, text):
        # restore prior state
        prev = self.db.load_state(user_id)
        if prev:
            st, sl = prev
            try:
                self.flow.set_state(user_id, st, sl)
            except:
                pass

        # advance the flow
        try:
            state = self.flow.next_state(user_id, text)
        except:
            return self._safe_reply(user_id, "Sorry, something went wrong.")

        # perform action or prompt
        if state.action:
            try:
                reply = getattr(self, state.action)(user_id, state.slots)
            except:
                reply = "Action failed."
        else:
            reply = state.prompt.format(**state.slots)

        # persist state (or clear if booking done)
        try:
            self.db.save_state(user_id, state.name, state.slots)
            if state.name == "complete_booking":
                self.db.clear_state(user_id)
        except:
            pass

        return self._safe_reply(user_id, reply)

    def book_room(self, user_id, slots):
        reservation_id = self.db.create_booking(user_id, slots)
        self.flow.complete_action(user_id, "reservation_id", reservation_id)
        return self.flow.current_prompt(user_id)

    def reschedule_room(self, user_id, slots):
        ok = self.db.update_booking(slots["reservation_id"], slots)
        return "Reservation updated!" if ok else "Reservation not found."

    def answer_faq(self, user_id, slots):
        # if llm is dummy, skip LLMChain
        if not hasattr(self.llm, "predict"):
            return "Sorry, I can't answer that right now."
        chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["question"],
                template="Hotel FAQ: {question}"
            )
        )
        return chain.predict(question=slots.get("message", ""))
