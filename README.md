# Hotel Booking AI Agent

A conversational AI agent built with LangGraph, LangChain, and Gemini through the PaLM API. It manages hotel room bookings, rescheduling, and FAQs via Instagram DMs.

## Project Structure

```
hotel-agent/
├── langgraph/
│   └── booking_flow.json        # LangGraph state machine definition
├── src/
│   ├── langgraph.py             # LangGraph engine implementation
│   ├── db.py                    # SQLite storage for bookings and state
│   ├── instagram_client.py      # Instagram Graph API wrapper
│   ├── agent.py                 # Agent logic (state and LLM integration)
│   └── app.py                   # Flask webhook server
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── .gitignore                   # Files to ignore in Git
```

---

## Prerequisites

* Python 3.8 or higher installed
* pip, the Python package manager
* An Instagram Business account linked to a Facebook App with the **Instagram Graph API** enabled
* A Google Cloud API key for PaLM/Gemini (set as `GEMINI_API_KEY`)

Optional:

* ngrok or localtunnel to expose your local server over HTTPS

---

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/hotel-agent.git
   cd hotel-agent
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   * Create a file named `.env` in the project root with the following:

     ```dotenv
     # Instagram
     PAGE_TOKEN=your_instagram_page_token
     VERIFY_TOKEN=your_chosen_verify_token

     # Gemini / PaLM API
     GEMINI_API_KEY=your_google_palm_api_key
     GEMINI_MODEL=gemini-2-alpha-0314
     ```
   * Make sure `.env` is in `.gitignore` to protect your secrets.

4. **Verify LangGraph flow**

   * Open `langgraph/booking_flow.json` and check that the states and prompts meet your needs.

---

## Running the Server

Start the Flask application:

```bash
python src/app.py
```

By default, the server listens on `http://0.0.0.0:5000`.

---

## Exposing Webhook Endpoint

Instagram needs an HTTPS callback URL. Use one of the following:

### Option A: ngrok

1. [Download ngrok](https://ngrok.com/download) and unzip it.
2. Run:

   ```bash
   ngrok http 5000
   ```
3. Note the HTTPS forwarding address (e.g., `https://abcd1234.ngrok.io`).

### Option B: localtunnel (Node.js)

```bash
npm install -g localtunnel
lt --port 5000
```

---

## Configuring Instagram Webhook

1. In your Facebook Developer dashboard, go to **Webhooks** and select **Add Subscription**.
2. Set **Callback URL** to `https://<your-tunnel-host>/webhook`.
3. Set **Verify Token** to the same `VERIFY_TOKEN` from your `.env`.
4. Subscribe to the `messages` field under Instagram.

---

## Testing

### 1. Webhook Verification

Simulate the handshake:

```bash
curl "https://<your-tunnel-host>/webhook?hub.mode=subscribe&hub.verify_token=my_chosen_token&hub.challenge=12345"
```

You should receive back `12345`.

### 2. Simulate a DM via curl

Create `payload.json`:

```json
{
  "entry": [{
    "messaging": [{
      "sender": {"id": "TEST_USER"},
      "message": {"text": "book"}
    }]
  }]
}
```

Send:

```bash
curl -X POST https://<your-tunnel-host>/webhook \
     -H "Content-Type: application/json" \
     -d @payload.json
```

Check your console for logs and look for the bot’s reply in your Instagram DM.

### 3. Full Booking Flow

1. **User** → Bot: `book`
2. **Bot** → User: “Sure, what are your check-in and check-out dates?”
3. **User** → Bot: `2025-07-01 to 2025-07-05`
4. **Bot** → User: “Which room type would you like, and for how many guests?”
5. **User** → Bot: `Deluxe, 2 guests`
6. **Bot** → User: “Great, a Deluxe for 2 guests from 2025-07-01 to 2025-07-05. Confirm?”
7. **User** → Bot: `yes`
8. **Bot** → User: “Your room is booked! Here’s your reservation ID: abc12345.”

Test **reschedule**:

* Send `reschedule`
* Provide `<reservation_id> 2025-07-02 to 2025-07-06`
* Confirm update message

Test **FAQ**:

* Send: `What time is check-in?`
* Bot responds using Gemini LLM.

---

## Troubleshooting

* **ModuleNotFoundError: langchain_community** → `pip install langchain-community`
* **Deprecation/Init errors for GooglePalm** → wrapped in `try/except` fallback
* Check your `.env` values and tunnel logs

---
