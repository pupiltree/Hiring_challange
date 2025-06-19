import os
from flask import Flask, request
from dotenv import load_dotenv
from instagram_client import InstagramClient
from agent import HotelAgent

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app   = Flask(__name__)
ig    = InstagramClient()
agent = HotelAgent()

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode      = request.args.get("hub.mode")
        token     = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode=="subscribe" and token==VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    try:
        sender, text = ig.webhook_handler(request.json)
        agent.handle_message(sender, text)
        return "OK", 200
    except Exception as e:
        print(f"[app] error: {e}")
        return "Error", 500

if __name__=="__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
