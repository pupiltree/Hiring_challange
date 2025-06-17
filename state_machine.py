# state_machine.py

class StateMachine:
    def __init__(self):
        self.state = "start"

    def transition(self, input_text):
        if "book" in input_text:
            self.state = "booking"
        elif "reschedule" in input_text:
            self.state = "rescheduling"
        elif "amenities" in input_text:
            self.state = "faq"
        else:
            self.state = "fallback"
        return self.state
