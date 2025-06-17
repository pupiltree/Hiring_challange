
class StateHandler:
    def __init__(self):
        self.state = "idle"

    def next(self, user_input):
        if "book" in user_input.lower():
            self.state = "booking"
        elif "reschedule" in user_input.lower():
            self.state = "rescheduling"
        elif "check-in" in user_input.lower() or "amenities" in user_input.lower():
            self.state = "faq"
        else:
            self.state = "unknown"
        return self.state
