from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from keywords import health_keywords  # Importing health_keywords from keywords.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
db = SQLAlchemy(app)

# Hugging Face GPT-2 model and tokenizer
model_name_or_path = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
model = GPT2LMHeadModel.from_pretrained(model_name_or_path)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return f'<User {self.id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255))
    sender = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Message {self.id}>'

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '')
    from_number = request.values.get('From', '')

    # Check if the user number is already in the database
    user = User.query.filter_by(number=from_number).first()
    if user is None:
        # If the user number is not in the database, add it
        user = User(number=from_number)
        db.session.add(user)
        db.session.commit()

    # Check if the incoming message contains health-related keywords
    if contains_health_keywords(incoming_msg):
        # Generate a response for the incoming message
        input_ids = tokenizer.encode(incoming_msg, return_tensors="pt")
        output = model.generate(input_ids, max_length=100, num_return_sequences=1)
        outgoing_msg = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Save the user's message and the AI's response in the database
        message = Message(message=incoming_msg, sender='user', user_id=user.id, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        
        message = Message(message=outgoing_msg, sender='ai', user_id=user.id, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()

        # Send the AI's response back to the user
        resp = MessagingResponse()
        resp.message(outgoing_msg)
        return str(resp)
    else:
        # If the message does not contain health-related keywords, provide a default response
        resp = MessagingResponse()
        resp.message("Sorry, I can only respond to health-related queries.")
        return str(resp)

def contains_health_keywords(message):
    message_lower = message.lower()
    for keyword in health_keywords:
        if keyword in message_lower:
            return True
    return False

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
