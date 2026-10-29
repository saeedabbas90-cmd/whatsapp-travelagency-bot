import os
import requests
from fastapi import FastAPI, Request, Response

app = FastAPI()

# Meta credentials from environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
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
    print("RAW WEBHOOK RECEIVED:", body)
    
    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        # Check if messages exist in the payload
        messages = value.get("messages", [])
        if messages:
            incoming_msg = messages[0]
            from_number = incoming_msg.get("from")
            msg_body = incoming_msg.get("text", {}).get("body", "")

            print(f"SUCCESS! Parsed sender phone: {from_number} | Message: {msg_body}")

            # Send automated WhatsApp reply back
            reply_text = f"Hello! Welcome to our Travel Agency. We received your request: '{msg_body}'. How can we help with your flight booking today?"
            send_whatsapp_message(from_number, reply_text)
        else:
            print("Webhook received, but no 'messages' field found (could be a delivery/read status update).")

    except Exception as e:
        print("Error processing webhook payload:", e)

    return {"status": "success"}

@app.get("/test-send")
def test_outbound_message(phone: str):
    """
    Diagnostic endpoint to test outbound Meta API messaging directly.
    Visit in browser: https://<your-render-url>/test-send?phone=923001234567
    """
    clean_recipient = "".join(filter(str.isdigit, str(phone)))
    print(f"Manual Test Send to recipient: {clean_recipient} | Using Phone ID: {PHONE_NUMBER_ID}")

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_recipient,
        "type": "text",
        "text": {"body": "Direct manual test message from your Render FastAPI bot!"}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return {
        "status_code": response.status_code,
        "meta_response": response.json()
    }

def send_whatsapp_message(recipient_id: str, text: str):
    clean_recipient = "".join(filter(str.isdigit, str(recipient_id)))

    print(f"Sending to clean recipient: {clean_recipient} | Using Phone ID: {PHONE_NUMBER_ID}")

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
    print("Meta API Status Code:", response.status_code)
    print("Meta API Response Body:", response.json())
