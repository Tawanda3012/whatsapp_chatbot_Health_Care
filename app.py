import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
from twilio.rest import Client
import openai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Twilio credentials
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_sandbox_number = os.getenv('TWILIO_SANDBOX_NUMBER')  # Update with your Twilio Sandbox for WhatsApp number
whatsapp_client = Client(account_sid, auth_token)

# Dictionary to store user join links
user_join_links = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    user_message = req['Body']
    sender_id = req['From']

    # Generate response using the integrated chatbot
    response_text = generate_response(user_message)

    # Send response back to user
    send_message(sender_id, response_text)

    return 'OK', 200

def send_message(receiver, message):
    whatsapp_client.messages.create(
        from_=f'whatsapp:{twilio_sandbox_number}',
        body=message,
        to=f'whatsapp:{receiver}'
    )

def generate_response(user_message):
    if "symptoms" in user_message:
        # Make a request to the Symptom Checker API
        api_url = 'https://healthcare-api.com/symptom-check'
        api_key = 'your_api_key'
        user_symptoms = extract_symptoms_from_message(user_message)  # Call the extract_symptoms_from_message function
        response = requests.post(api_url, headers={'Authorization': f'Bearer {api_key}'}, json={'symptoms': user_symptoms})

        # Process the API response and incorporate it into the chatbot's message
        if response.status_code == 200:
            diagnosis = response.json()['diagnosis']
            response_text = f"Based on your symptoms, it seems like you may have {diagnosis}. It's important to consult a healthcare professional for further evaluation."
        else:
            response_text = "I'm here to help with your healthcare questions. How can I assist you today?"
    else:
        # Generate response using OpenAI's GPT-3
        response_text = generate_gpt3_response(user_message)

    return response_text

def generate_gpt3_response(user_message):
    # Make a request to OpenAI's GPT-3 API
    prompt = "User:" + user_message + "\nChatbot:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices

def extract_symptoms_from_message(message):
    # Add your code here to extract symptoms from the user's message
    # For example, you might use some kind of pattern matching or keyword search
    symptoms = [...]  # Replace [...] with the extracted symptoms
    return symptoms

if __name__ == '__main__':
    app.run(debug=True)