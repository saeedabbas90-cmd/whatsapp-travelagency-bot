from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Running"}

@app.get("/webhook")
async def verify(request: Request):
    challenge = request.query_params.get("hub.challenge", "")
    return PlainTextResponse(content=str(challenge), status_code=200)

@app.post("/webhook")
async def webhook_post(request: Request):
    data = await request.json()
    print("🔥 SUCCESS! WEBHOOK PAYLOAD RECEIVED:", data)
    return {"status": "ok"}
