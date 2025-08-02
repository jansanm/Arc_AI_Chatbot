# Create the enhanced Flask backend application
flask_app_code = '''
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import re
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import base64
import os
from datetime import datetime
import csv

app = Flask(__name__)
CORS(app)

# Load enhanced medical dataset
try:
    medical_data = pd.read_csv('enhanced_medical_dataset.csv')
    print("Enhanced medical dataset loaded successfully")
except FileNotFoundError:
    print("Enhanced medical dataset not found. Creating basic dataset...")
    # Fallback basic dataset
    medical_data = pd.DataFrame({
        'symptom': ['headache', 'fever', 'cough', 'sore throat'],
        'disease': ['Tension Headache', 'Viral Fever', 'Dry Cough', 'Pharyngitis'],
        'medication': ['Ibuprofen 400mg', 'Paracetamol 500mg', 'Cough syrup', 'Throat lozenges'],
        'precautions': ['Rest in dark room', 'Stay hydrated', 'Avoid irritants', 'Gargle with salt water'],
        'treatment': ['Cold compress', 'Rest and fluids', 'Steam inhalation', 'Warm salt water'],
        'diet': ['Stay hydrated', 'Light foods', 'Warm liquids', 'Soft foods']
    })

# Initialize text-to-speech engine
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('volume', 0.9)
except:
    tts_engine = None
    print("TTS engine initialization failed")

# Language translations
translations = {
    'english': {
        'greeting': 'Hello! I am your AI Healthcare Assistant. How can I help you today?',
        'symptom_analysis': 'Based on your symptoms, here is my analysis:',
        'medication_advice': 'Recommended Medications:',
        'precautions': 'Precautions to take:',
        'treatment': 'Treatment recommendations:',
        'diet': 'Dietary suggestions:',
        'doctor_consultation': 'When to see a doctor:',
        'disclaimer': 'Disclaimer: This is for informational purposes only. Please consult a healthcare professional for proper diagnosis and treatment.'
    },
    'hindi': {
        'greeting': 'नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
        'symptom_analysis': 'आपके लक्षणों के आधार पर, यहां मेरा विश्लेषण है:',
        'medication_advice': 'अनुशंसित दवाएं:',
        'precautions': 'सावधानियां:',
        'treatment': 'उपचार की सिफारिशें:',
        'diet': 'आहार सुझाव:',
        'doctor_consultation': 'डॉक्टर से कब मिलें:',
        'disclaimer': 'अस्वीकरण: यह केवल सूचनात्मक उद्देश्यों के लिए है। उचित निदान और उपचार के लिए कृपया किसी स्वास्थ्य पेशेवर से सलाह लें।'
    },
    'kannada': {
        'greeting': 'ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
        'symptom_analysis': 'ನಿಮ್ಮ ಲಕ್ಷಣಗಳ ಆಧಾರದ ಮೇಲೆ, ಇಲ್ಲಿ ನನ್ನ ವಿಶ್ಲೇಷಣೆ:',
        'medication_advice': 'ಶಿಫಾರಸು ಮಾಡಿದ ಔಷಧಗಳು:',
        'precautions': 'ತೆಗೆದುಕೊಳ್ಳಬೇಕಾದ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು:',
        'treatment': 'ಚಿಕಿತ್ಸೆಯ ಶಿಫಾರಸುಗಳು:',
        'diet': 'ಆಹಾರ ಸಲಹೆಗಳು:',
        'doctor_consultation': 'ವೈದ್ಯರನ್ನು ಯಾವಾಗ ನೋಡಬೇಕು:',
        'disclaimer': 'ಅಸ್ವೀಕರಣೆ: ಇದು ಕೇವಲ ಮಾಹಿತಿ ಉದ್ದೇಶಗಳಿಗಾಗಿ. ಸರಿಯಾದ ರೋಗನಿರ್ಣಯ ಮತ್ತು ಚಿಕಿತ್ಸೆಗಾಗಿ ದಯವಿಟ್ಟು ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ.'
    }
}

def find_matching_symptoms(user_input, language='english'):
    """Find matching symptoms from the dataset based on user input"""
    user_input = user_input.lower()
    
    # Common symptom keywords mapping
    symptom_keywords = {
        'headache': ['headache', 'head pain', 'migraine', 'head ache'],
        'fever': ['fever', 'temperature', 'hot', 'feverish'],
        'cough': ['cough', 'coughing', 'throat irritation'],
        'sore throat': ['sore throat', 'throat pain', 'throat ache'],
        'stomach pain': ['stomach pain', 'stomach ache', 'abdominal pain', 'belly pain'],
        'cold': ['cold', 'runny nose', 'congestion', 'sniffles'],
        'diarrhea': ['diarrhea', 'loose motion', 'stomach upset'],
        'nausea': ['nausea', 'vomiting', 'feeling sick'],
        'back pain': ['back pain', 'backache', 'spine pain'],
        'joint pain': ['joint pain', 'arthritis', 'joint ache']
    }
    
    matched_symptoms = []
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in user_input:
                matched_symptoms.append(symptom)
                break
    
    return matched_symptoms

def get_medical_advice(symptoms, language='english'):
    """Get comprehensive medical advice for given symptoms"""
    if not symptoms:
        return {
            'message': translations[language]['greeting'],
            'suggestions': ['Try describing your symptoms like: headache, fever, cough, etc.']
        }
    
    advice_response = {
        'analysis': translations[language]['symptom_analysis'],
        'conditions': [],
        'disclaimer': translations[language]['disclaimer']
    }
    
    for symptom in symptoms:
        # Find matching condition in dataset
        condition_data = medical_data[medical_data['symptom'].str.lower() == symptom.lower()]
        
        if not condition_data.empty:
            condition_info = condition_data.iloc[0]
            
            condition_advice = {
                'symptom': symptom.title(),
                'disease': condition_info.get('disease', 'Unknown'),
                'severity': condition_info.get('severity', 'Unknown'),
                'description': condition_info.get('description', 'No description available'),
                'medications': condition_info.get('medication', 'Consult a doctor').split(', '),
                'precautions': condition_info.get('precautions', 'Rest and stay hydrated').split(', '),
                'treatment': condition_info.get('treatment', 'Consult healthcare provider').split(', '),
                'diet': condition_info.get('diet', 'Maintain healthy diet').split(', '),
                'doctor_consultation': condition_info.get('when_to_see_doctor', 'If symptoms persist')
            }
            
            advice_response['conditions'].append(condition_advice)
    
    return advice_response

def log_conversation(user_input, bot_response, language):
    """Log conversation to CSV file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        with open('logs/conversation_log.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header if file is empty
            if file.tell() == 0:
                writer.writerow(['timestamp', 'user_input', 'bot_response', 'language'])
            
            writer.writerow([timestamp, user_input, str(bot_response), language])
    except Exception as e:
        print(f"Error logging conversation: {e}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        language = data.get('language', 'english').lower()
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Please provide a message'
            })
        
        # Find matching symptoms
        symptoms = find_matching_symptoms(user_input, language)
        
        # Get medical advice
        advice = get_medical_advice(symptoms, language)
        
        # Log conversation
        log_conversation(user_input, advice, language)
        
        return jsonify({
            'success': True,
            'response': advice,
            'symptoms_detected': symptoms
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    """Convert voice input to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'})
        
        audio_file = request.files['audio']
        
        # Initialize speech recognition
        r = sr.Recognizer()
        
        # Convert audio to text
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
            
        return jsonify({
            'success': True,
            'text': text
        })
        
    except sr.UnknownValueError:
        return jsonify({
            'success': False,
            'error': 'Could not understand the audio'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing audio: {str(e)}'
        })

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'english')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        # Language codes for gTTS
        lang_codes = {
            'english': 'en',
            'hindi': 'hi',
            'kannada': 'kn'
        }
        
        lang_code = lang_codes.get(language, 'en')
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to BytesIO object
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Encode as base64
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        
        return jsonify({
            'success': True,
            'audio': audio_base64
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating speech: {str(e)}'
        })

@app.route('/dashboard-data')
def dashboard_data():
    """Provide data for the dashboard"""
    try:
        # Read conversation logs
        dashboard_stats = {
            'total_consultations': 0,
            'most_common_symptoms': {},
            'consultations_by_language': {},
            'recent_consultations': []
        }
        
        try:
            with open('logs/conversation_log.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                consultations = list(reader)
                
                dashboard_stats['total_consultations'] = len(consultations)
                
                # Count symptoms and languages
                for consultation in consultations:
                    # Extract symptoms from bot response (simplified)
                    user_input = consultation['user_input'].lower()
                    language = consultation['language']
                    
                    # Count languages
                    dashboard_stats['consultations_by_language'][language] = dashboard_stats['consultations_by_language'].get(language, 0) + 1
                    
                    # Simple symptom detection for dashboard
                    for symptom in ['headache', 'fever', 'cough', 'sore throat', 'stomach pain']:
                        if symptom in user_input:
                            dashboard_stats['most_common_symptoms'][symptom] = dashboard_stats['most_common_symptoms'].get(symptom, 0) + 1
                
                # Get recent consultations
                dashboard_stats['recent_consultations'] = consultations[-10:] if len(consultations) > 10 else consultations
                
        except FileNotFoundError:
            pass  # No logs yet
        
        return jsonify(dashboard_stats)
        
    except Exception as e:
        return jsonify({'error': f'Error loading dashboard data: {str(e)}'})

if __name__ == '__main__':
    print("Starting Enhanced Healthcare Chatbot...")
    print("Make sure you have the enhanced_medical_dataset.csv file in the same directory")
    app.run(debug=True, port=5000)
'''

# Save the Flask app code
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(flask_app_code)

print("Enhanced Flask backend (app.py) created successfully!")
print("\nKey features added:")
print("1. Detailed medication recommendations")
print("2. Comprehensive medical advice (precautions, treatment, diet)")
print("3. Multi-language support (English, Hindi, Kannada)")
print("4. Voice input/output capabilities")
print("5. Conversation logging")
print("6. Dashboard with analytics")