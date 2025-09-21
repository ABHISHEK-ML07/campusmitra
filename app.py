import os
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
import vertexai
from vertexai.language_models import TextGenerationModel
import google.generativeai as genai
from google.cloud import firestore
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'campusmitra_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Google Cloud services
vertexai.init(project="your-gcp-project", location="us-central1")  # Replace with your GCP project ID
genai.configure(api_key=os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key'))  # Replace with your Gemini API key or set env var
db = firestore.Client()

def classify_risk(text):
    try:
        model = TextGenerationModel.from_pretrained("text-bison")
        prompt = f"Classify suicide risk in this message on a scale 0-1: {text}"
        response = model.predict(prompt)
        return float(response.text.strip())
    except Exception as e:
        print(f"Vertex AI error: {e}")
        return 0.8 if 'hopeless' in text.lower() else 0.2  # Mock fallback

@socketio.on('message')
def handle_message(data):
    user_msg = data['message']
    risk_score = classify_risk(user_msg)
    try:
        db.collection('trends').add({'risk_trigger': risk_score > 0.7, 'timestamp': firestore.SERVER_TIMESTAMP})
    except Exception as e:
        print(f"Firestore error: {e}")
    if risk_score > 0.7:
        prompt = f"You are MannMitra, a warm AI for Indian youth. Respond empathetically and suggest HopeKit: {user_msg}"
        response = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
        emit('response', {'text': response, 'trigger_hopekit': True})
    else:
        prompt = f"You are MannMitra, a warm AI for Indian youth. Respond empathetically: {user_msg}"
        response = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
        emit('response', {'text': response})

@app.route('/generate_hopekit', methods=['POST'])
def generate_hopekit():
    aspiration = request.json.get('aspiration', '')
    if not aspiration:
        return jsonify({'error': 'Aspiration is required'}), 400
    try:
        prompt = f"Generate a hopeful Future-Self Letter for Indian youth: {aspiration}. 100 words, simple English."
        letter = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
        grounding_prompt = "Create a 5-step calming grounding exercise for stress."
        grounding = genai.GenerativeModel('gemini-1.5-flash').generate_content(grounding_prompt).text
        return jsonify({'letter': letter, 'grounding': grounding})
    except Exception as e:
        print(f"Gemini error: {e}")
        return jsonify({'letter': 'Dear Future Self, you will succeed with hard work and support...', 'grounding': '1. Breathe deeply...\n2. Look around...\n3. Feel your feet...\n4. Name 5 things...\n5. Relax your shoulders...'}), 500

@app.route('/book_session', methods=['POST'])
def book_session():
    data = request.json
    if not data.get('consent'):
        return jsonify({'success': False, 'message': 'Consent required'}), 400
    try:
        db.collection('trends').add({'referral': True, 'timestamp': firestore.SERVER_TIMESTAMP})
        return jsonify({'success': True, 'message': f'Session booked! ID: {datetime.now().strftime("%Y%m%d%H%M%S")}'})
    except Exception as e:
        print(f"Firestore error: {e}")
        return jsonify({'success': False, 'message': 'Booking failed'}), 500

@app.route('/dashboard')
def dashboard():
    try:
        trends = db.collection('trends').stream()
        triggers = sum(1 for doc in trends if doc.to_dict().get('risk_trigger', False))
        referrals = sum(1 for doc in trends if doc.to_dict().get('referral', False))
        return jsonify({
            'triggers': triggers,
            'referrals': referrals,
            'users': 3412,  # Mock for demo
            'wellness_score': 72,  # Mock for demo
            'concerns': {'Academic Pressure': 65, 'Relationship Issues': 45, 'Family Expectations': 52},
            'recommendations': [
                'Schedule wellness workshops during exam periods',
                'Provide faculty training to identify struggling students',
                'Establish peer support programs'
            ]
        })
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({'triggers': 0, 'referrals': 0, 'users': 0, 'wellness_score': 0, 'concerns': {}, 'recommendations': []}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)