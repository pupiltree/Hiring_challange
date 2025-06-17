from agent import get_reply
from state_machine import StateHandler

handler = StateHandler()

while True:
    user = input("You: ")
    state = handler.next(user)
    print("State:", state)
    reply = get_reply(user)
    print("Agent:", reply)
