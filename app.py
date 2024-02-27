from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI()
app = Flask(__name__)

# Twilio client setup
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)
twilio_phone_number = os.getenv('TWILIO_SANDBOX_NUMBER')

# OpenAI API key
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '')
    resp = MessagingResponse()
    if contains_health_keywords(incoming_msg):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        resp.message(response.choices[0].message.content.strip())
    else:
        resp.message("Sorry, I can only respond to health-related issues.")
    return str(resp)

def contains_health_keywords(message):
    health_keywords = ["health", "medical", "doctor", "hospital", "symptoms"]
    for keyword in health_keywords:
        if keyword in message.lower():
            return True
    return False

@app.route('/join', methods=['GET'])
def join_chatbot():
    whatsapp_number = "TWILIO_SANDBOX_NUMBER"   
    default_message = "Hello, Welcome to healthcare chatbot"   
    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={default_message}"
    return f"Click this link to join the chatbot: <a href='{whatsapp_link}'>{whatsapp_link}</a>"

if __name__ == "__main__":
    app.run(debug=True)