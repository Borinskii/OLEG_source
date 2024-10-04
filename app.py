# app.py

from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Serve the first page

@app.route('/new_course')
def chat():
    return render_template('new_course.html')  # Serve the chat page

@app.route('/send', methods=['POST'])
def send():
    user_message = request.json.get('message')  # Get message from the user
    bot_response = generate_bot_response(user_message)  # Generate a bot response
    return jsonify({'response': bot_response})

def generate_bot_response(message):
    # You can customize this to create more dynamic responses
    responses = [
        "This is a bot response.",
        "I'm here to help you!",
        "What can I assist you with?",
        "How can I make your day better?",
        "That's interesting!"
    ]
    return random.choice(responses)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Change this line