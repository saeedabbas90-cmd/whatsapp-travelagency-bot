import os
import requests
from fastapi import FastAPI, Request, Response

app = FastAPI()

# Meta credentials from environment variables (or paste direct strings for testing)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "YOUR_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "travel_bot_token_123")

@app.get("/")
def home():
    return {"status": "Travel Agency WhatsApp Bot is live!"}

@app.get("/webhook")
def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    
    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            incoming_msg = messages[0]
            from_number = incoming_msg.get("from")
            msg_body = incoming_msg.get("text", {}).get("body", "")

            # Send automated WhatsApp reply back
            reply_text = f"Hello! Welcome to our Travel Agency. We received your request: '{msg_body}'. How can we help with your flight booking today?"
            send_whatsapp_message(from_number, reply_text)

    except Exception as e:
        print("Error processing webhook:", e)

    return {"status": "success"}

def send_whatsapp_message(recipient_id: str, text: str):
    # Ensure recipient_id contains only digits and no leading '+' or spaces
    clean_recipient = "".join(filter(str.isdigit, str(recipient_id)))

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_recipient,
        "type": "text",
        "text": {"body": text}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print("Meta API Response:", response.json())
