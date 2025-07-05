import os
from flask import Flask, render_template, request, jsonify
from logger import CustomLogger  # Ensure logger.py exists
from chatbot import Chatbot     # Ensure chatbot/__init__.py properly imports Chatbot class

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    logger = CustomLogger().get_logger()

    # Get API key from environment (Render or .env)
    groq_api_key = os.getenv('GROQ_API_KEY')

    if not groq_api_key:
        raise RuntimeError("❌ GROQ_API_KEY is not set in the environment.")

    chatbot_instance = Chatbot(groq_api_key)  # Only initialize once

    @app.route('/')
    def index():
        """Load chat UI directly (no API key input page)."""
        return render_template('chat.html')

    @app.route('/ask', methods=['POST'])
    def ask():
        """Handle user questions and return responses."""
        question = request.json.get('question')
        try:
            response = chatbot_instance.ask(question)
            logger.info(f"User asked: {question}")
            return jsonify({"response": response})
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            return jsonify({"response": "An error occurred while processing your request."}), 500

    return app
