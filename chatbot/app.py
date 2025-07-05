import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from logger import CustomLogger  # Make sure logger.py exists
from chatbot import Chatbot  # Make sure chatbot/__init__.py properly imports Chatbot class

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.urandom(24)  # Set a secret key for session management
    logger = CustomLogger().get_logger()  # Initialize custom logger

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """Render the API key input page and handle form submissions."""
        error_message = None

        if request.method == 'POST':
            api_key = request.form['api_key']
            try:
                session['groq_api_key'] = api_key
                chatbot_instance = Chatbot(api_key)
                logger.info("API Key set successfully.")
                return redirect(url_for('chat'))
            except Exception as e:
                logger.error(f"Error setting API Key: {e}")
                error_message = "Error setting API Key. Please try again."
        
        return render_template('index.html', error_message=error_message)

    @app.route('/chat')
    def chat():
        """Render the chat interface."""
        if 'groq_api_key' not in session:
            return redirect(url_for('index'))
        return render_template('chat.html')

    @app.route('/ask', methods=['POST'])
    def ask():
        """Handle user questions and return responses."""
        question = request.json.get('question')
        
        api_key = session.get('groq_api_key')
        print("DEBUG: api_key from session =", api_key)  # Helpful for Render logs

        if not api_key:
            return jsonify({"response": "API Key is not set in session."}), 500

        try:
            chatbot_instance = Chatbot(api_key)
            response = chatbot_instance.ask(question)
            return jsonify({"response": response})
        except Exception as e:
            print("DEBUG: Chatbot error =", e)  # For debug log visibility on Render
            return jsonify({"response": "Error occurred in chatbot backend."}), 500

    @app.route('/logout', methods=['POST'])
    def logout():
        """Clear the GROQ API key and reset chatbot instance."""
        session.pop('groq_api_key', None)
        session.pop('chatbot_instance', None)
        logger.info("API Key and Chatbot instance cleared.")
        return redirect(url_for('index'))
    
    return app
