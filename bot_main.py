from fastapi import FastAPI, Request, Response
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Travel Agency WhatsApp Bot is live!"}

@app.get("/webhook")
def verify_webhook(request: Request):
    # Meta WhatsApp verification token handshake
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    # Set your own verify token here or use an environment variable
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "travel_bot_token_123")
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    # Add your WhatsApp incoming message parsing logic here
    print("Received webhook message:", body)
    return {"status": "success"}