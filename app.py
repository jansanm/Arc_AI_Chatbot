
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import re
import ffmpeg
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import base64
import os
import tempfile
from datetime import datetime
import csv
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
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

# Conversational responses for general chat
conversational_responses = {
    'greetings': {
        'english': [
            "Hello! I'm your AI Healthcare Assistant. How can I help you today?",
            "Hi there! I'm here to help with your health concerns. What can I assist you with?",
            "Greetings! I'm your friendly healthcare assistant. How are you feeling today?",
            "Hey! I'm here to provide medical guidance. What's on your mind?",
            "Hello! I'm your AI health companion. How can I support you today?"
        ],
        'hindi': [
            "नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
            "हाय! मैं आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने के लिए यहां हूं। मैं आपकी क्या सहायता कर सकता हूं?",
            "नमस्कार! मैं आपका दोस्ताना स्वास्थ्य सहायक हूं। आज आप कैसा महसूस कर रहे हैं?"
        ],
        'kannada': [
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ಹಾಯ್! ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ. ನಾನು ನಿಮಗೆ ಏನು ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಸ್ನೇಹಪರ ಆರೋಗ್ಯ ಸಹಾಯಕ. ಇಂದು ನೀವು ಹೇಗೆ ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?"
        ]
    },
    'thanks': {
        'english': [
            "You're welcome! I'm glad I could help. Feel free to ask if you have more questions!",
            "My pleasure! Don't hesitate to reach out if you need any further assistance.",
            "Happy to help! Take care and stay healthy!"
        ],
        'hindi': [
            "आपका स्वागत है! मुझे खुशी है कि मैं मदद कर सका। अगर आपके पास और प्रश्न हैं तो बेझिझक पूछें!",
            "मेरी खुशी! अगर आपको और सहायता की आवश्यकता है तो संपर्क करने में संकोच न करें।",
            "मदद करके खुशी हुई! ध्यान रखें और स्वस्थ रहें!"
        ],
        'kannada': [
            "ಸ್ವಾಗತ! ನಾನು ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷಪಡುತ್ತಿದ್ದೇನೆ. ನಿಮಗೆ ಹೆಚ್ಚಿನ ಪ್ರಶ್ನೆಗಳಿದ್ದರೆ ಕೇಳಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ನನ್ನ ಸಂತೋಷ! ನಿಮಗೆ ಹೆಚ್ಚಿನ ಸಹಾಯದ ಅಗತ್ಯವಿದ್ದರೆ ಸಂಪರ್ಕಿಸಲು ಹಿಂಜರಿಯಬೇಡಿ.",
            "ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷ! ಜಾಗರೂಕರಾಗಿರಿ ಮತ್ತು ಆರೋಗ್ಯವಾಗಿರಿ!"
        ]
    },
    'how_are_you': {
        'english': [
            "I'm doing great, thank you for asking! I'm here and ready to help with your health concerns. How are you feeling today?",
            "I'm functioning perfectly! I'm designed to assist with medical queries and provide health guidance. What brings you here today?",
            "I'm excellent! I'm your AI health assistant, always ready to help. How can I assist you with your health today?"
        ],
        'hindi': [
            "मैं बहुत अच्छा कर रहा हूं, पूछने के लिए धन्यवाद! मैं यहां हूं और आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने के लिए तैयार हूं। आज आप कैसा महसूस कर रहे हैं?",
            "मैं पूरी तरह से काम कर रहा हूं! मैं चिकित्सीय प्रश्नों में सहायता करने और स्वास्थ्य मार्गदर्शन प्रदान करने के लिए डिज़ाइन किया गया हूं। आज आपको यहां क्या लाया?",
            "मैं बेहतरीन हूं! मैं आपका AI स्वास्थ्य सहायक हूं, हमेशा मदद करने के लिए तैयार। आज मैं आपकी स्वास्थ्य में कैसे सहायता कर सकता हूं?"
        ],
        'kannada': [
            "ನಾನು ಚೆನ್ನಾಗಿ ಮಾಡುತ್ತಿದ್ದೇನೆ, ಕೇಳಿದಕ್ಕೆ ಧನ್ಯವಾದಗಳು! ನಾನು ಇಲ್ಲಿ ಇದ್ದೇನೆ ಮತ್ತು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ. ಇಂದು ನೀವು ಹೇಗೆ ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?",
            "ನಾನು ಪರಿಪೂರ್ಣವಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿದ್ದೇನೆ! ನಾನು ವೈದ್ಯಕೀಯ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಮತ್ತು ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನ ನೀಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾಗಿದೆ. ಇಂದು ನಿಮ್ಮನ್ನು ಇಲ್ಲಿ ಏನು ತಂದಿತು?",
            "ನಾನು ಅತ್ಯುತ್ತಮ! ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ, ಯಾವಾಗಲೂ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧ. ಇಂದು ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        ]
    },
    'general_questions': {
        'english': [
            "I'm an AI Healthcare Assistant designed to help with medical queries and provide health guidance. I can analyze symptoms, suggest treatments, and offer medical advice. What would you like to know?",
            "I'm here to help with your health concerns! I can provide medical information, symptom analysis, and treatment recommendations. How can I assist you today?",
            "I'm your friendly AI health companion! I'm knowledgeable about various health topics and can help with medical queries. What's on your mind?"
        ],
        'hindi': [
            "मैं एक AI स्वास्थ्य सहायक हूं जो चिकित्सीय प्रश्नों में मदद करने और स्वास्थ्य मार्गदर्शन प्रदान करने के लिए डिज़ाइन किया गया है। मैं लक्षणों का विश्लेषण कर सकता हूं, उपचार सुझा सकता हूं और चिकित्सीय सलाह दे सकता हूं। आप क्या जानना चाहते हैं?",
            "मैं आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने के लिए यहां हूं! मैं चिकित्सीय जानकारी, लक्षण विश्लेषण और उपचार सिफारिशें प्रदान कर सकता हूं। आज मैं आपकी कैसे सहायता कर सकता हूं?",
            "मैं आपका दोस्ताना AI स्वास्थ्य साथी हूं! मैं विभिन्न स्वास्थ्य विषयों के बारे में जानकार हूं और चिकित्सीय प्रश्नों में मदद कर सकता हूं। आपके मन में क्या है?"
        ],
        'kannada': [
            "ನಾನು ವೈದ್ಯಕೀಯ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಮತ್ತು ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನ ನೀಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ AI ಆರೋಗ್ಯ ಸಹಾಯಕ. ನಾನು ಲಕ್ಷಣಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಬಹುದು, ಚಿಕಿತ್ಸೆಗಳನ್ನು ಸಲಹೆ ಮಾಡಬಹುದು ಮತ್ತು ವೈದ್ಯಕೀಯ ಸಲಹೆ ನೀಡಬಹುದು. ನೀವು ಏನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ! ನಾನು ವೈದ್ಯಕೀಯ ಮಾಹಿತಿ, ಲಕ್ಷಣ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಚಿಕಿತ್ಸೆ ಶಿಫಾರಸುಗಳನ್ನು ನೀಡಬಹುದು. ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ನಾನು ನಿಮ್ಮ ಸ್ನೇಹಪರ AI ಆರೋಗ್ಯ ಸಂಗಾತಿ! ನಾನು ವಿವಿಧ ಆರೋಗ್ಯ ವಿಷಯಗಳ ಬಗ್ಗೆ ತಿಳುವಳಿಕೆಯುಳ್ಳವನಾಗಿದ್ದೇನೆ ಮತ್ತು ವೈದ್ಯಕೀಯ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು. ನಿಮ್ಮ ಮನಸ್ಸಿನಲ್ಲಿ ಏನಿದೆ?"
        ]
    },
    'goodbye': {
        'english': [
            "Goodbye! Take care and stay healthy. Feel free to come back if you have any health concerns!",
            "See you later! Remember to prioritize your health and well-being. I'm here whenever you need me!",
            "Take care! Stay healthy and don't hesitate to reach out if you need medical advice in the future!",
            "Goodbye! Wishing you good health. I'll be here when you need healthcare assistance again!"
        ],
        'hindi': [
            "अलविदा! ध्यान रखना और स्वस्थ रहना। अगर आपको कोई स्वास्थ्य संबंधी चिंता है तो वापस आने में संकोच न करें!",
            "फिर मिलेंगे! अपने स्वास्थ्य और कल्याण को प्राथमिकता देना याद रखें। जब भी आपको मेरी जरूरत हो तो मैं यहां हूं!",
            "ध्यान रखना! स्वस्थ रहें और भविष्य में चिकित्सीय सलाह की आवश्यकता हो तो संपर्क करने में संकोच न करें!",
            "अलविदा! आपको अच्छे स्वास्थ्य की कामना करता हूं। जब आपको फिर से स्वास्थ्य देखभाल सहायता की आवश्यकता हो तो मैं यहां रहूंगा!"
        ],
        'kannada': [
            "ಬೀಗ್! ಜಾಗರೂಕರಾಗಿರಿ ಮತ್ತು ಆರೋಗ್ಯವಾಗಿರಿ. ನಿಮಗೆ ಯಾವುದೇ ಆರೋ  ಗ್ಯ ಕಾಳಜಿಗಳಿದ್ದರೆ ಮತ್ತೆ ಬರಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ಮತ್ತೆ ಸಿಗೋಣ! ನಿಮ್ಮ ಆರೋಗ್ಯ ಮತ್ತು ಯೋಗಕ್ಷೇಮವನ್ನು ಆದ್ಯತೆ ನೀಡಲು ನೆನಪಿಡಿ. ನಿಮಗೆ ನನ್ನ ಅಗತ್ಯವಿರುವಾಗಲೆಲ್ಲಾ ನಾನು ಇಲ್ಲಿ ಇದ್ದೇನೆ!",
            "ಜಾಗರೂಕರಾಗಿರಿ! ಆರೋಗ್ಯವಾಗಿರಿ ಮತ್ತು ಭವಿಷ್ಯದಲ್ಲಿ ವೈದ್ಯಕೀಯ ಸಲಹೆಯ ಅಗತ್ಯವಿದ್ದರೆ ಸಂಪರ್ಕಿಸಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ಬೀಗ್! ನಿಮಗೆ ಒಳ್ಳೆಯ ಆರೋಗ್ಯವನ್ನು ಕೋರುತ್ತೇನೆ. ನಿಮಗೆ ಮತ್ತೆ ಆರೋಗ್ಯ ಸಹಾಯದ ಅಗತ್ಯವಿರುವಾಗ ನಾನು ಇಲ್ಲಿ ಇರುತ್ತೇನೆ!"
        ]
    }
}

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
        'joint pain': ['joint pain', 'arthritis', 'joint ache'],
        'shortness of breath': ['shortness of breath', 'breathless', 'difficulty breathing', 'cannot breathe'],
    'runny nose': ['runny nose', 'drippy nose', 'watery nose'],
    'dizziness': ['dizziness', 'vertigo', 'lightheaded', 'giddiness'],
    'itchy skin': ['itchy skin', 'itching', 'pruritus', 'scratchy skin'],
    'numbness in hand': ['numbness in hand', 'tingling in hand', 'hand asleep'],
    'watery eyes': ['watery eyes', 'tearing', 'runny eyes'],
    'swollen ankle': ['swollen ankle', 'ankle swelling', 'ankle pain'],
    'blurred vision': ['blurred vision', 'blurry eyesight', 'unclear vision'],
    'frequent urination': ['frequent urination', 'peeing often', 'urinating frequently'],
    'weight loss': ['weight loss', 'losing weight', 'unintentional weight loss'],
    'muscle cramps': ['muscle cramps', 'muscle spasm', 'leg cramps'],
    'nosebleed': ['nosebleed', 'bleeding nose', 'blood from nose'],
    'ringing in ears': ['ringing in ears', 'tinnitus', 'buzzing in ear'],
    'night sweats': ['night sweats', 'sweating at night', 'excessive sweating'],
    'vomiting': ['vomiting', 'throw up', 'retching'],
    'heartburn': ['heartburn', 'acid reflux', 'burning in chest'],
    'palpitations': ['palpitations', 'heart racing', 'fast heartbeat', 'pounding heart'],
    'rash': ['rash', 'red spots', 'skin eruption'],
    'loss of appetite': ['loss of appetite', 'not hungry', 'anorexia'],
    'foot pain': ['foot pain', 'pain in foot'],
    'hair loss': ['hair loss', 'thinning hair', 'baldness'],
    'chest pain': ['chest pain', 'pain in chest', 'tight chest'],
    'red eyes': ['red eyes', 'bloodshot eyes', 'eye redness'],
    'ear pain': ['ear pain', 'earache', 'pain in ear'],
    'itchy scalp': ['itchy scalp', 'scalp itching', 'head itching'],
    'swollen gums': ['swollen gums', 'gum swelling'],
    'burning urination': ['burning urination', 'burning while urinating'],
    'swollen lymph nodes': ['swollen lymph nodes', 'neck swelling', 'lump in neck'],
    'yellow skin': ['yellow skin', 'jaundice', 'yellow eyes'],
    'hives': ['hives', 'urticaria', 'raised rash'],
    'weight gain': ['weight gain', 'gaining weight', 'increase in weight'],
    'constipation': ['constipation', 'hard stool', 'infrequent stool'],
    'toothache': ['toothache', 'tooth pain', 'pain in tooth'],
    'chills': ['chills', 'shivering', 'feeling cold'],
    'increased thirst': ['increased thirst', 'excessive thirst', 'always thirsty'],
    'dry mouth': ['dry mouth', 'mouth dryness', 'no saliva'],
    'chronic cough': ['chronic cough', 'long term cough', 'persistent cough'],
    'unintentional shaking': ['unintentional shaking', 'hand tremor', 'trembling'],
    'insomnia': ['insomnia', 'cannot sleep', 'trouble sleeping'],
    'hoarseness': ['hoarseness', 'lost voice', 'raspy voice'],
    'bloating': ['bloating', 'fullness', 'gas in stomach'],
    'difficulty swallowing': ['difficulty swallowing', 'pain swallowing', 'dysphagia'],
    'leg swelling': ['leg swelling', 'swollen leg', 'edema in leg'],
    'mouth ulcers': ['mouth ulcers', 'sores in mouth'],
    'irritability': ['irritability', 'easily annoyed', 'short tempered'],
    'excessive sweating': ['excessive sweating', 'sweating a lot', 'hyperhidrosis'],
    'weak grip': ['weak grip', 'cannot hold', 'weak hand'],
    'shakiness': ['shakiness', 'shaky', 'shivering'],
    'dry hair': ['dry hair', 'hair dryness', 'brittle hair'],
    'swollen face': ['swollen face', 'face swelling', 'puffy face'],
}
    

    matched_symptoms = []
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in user_input:
                matched_symptoms.append(symptom)
                break

    return matched_symptoms

def detect_conversational_pattern(user_input, language='english'):
    """Detect conversational patterns in user input"""
    user_input = user_input.lower().strip()
    
    # Greeting patterns
    greeting_patterns = {
        'english': ['hello', 'hi', 'hey', 'hai', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo', 'whats up', 'wassup'],
        'hindi': ['नमस्ते', 'हाय', 'हैलो', 'सुप्रभात', 'नमस्कार', 'कैसे हो', 'क्या हाल है'],
        'kannada': ['ನಮಸ್ಕಾರ', 'ಹಾಯ್', 'ಹಲೋ', 'ಸುಪ್ರಭಾತ', 'ನಮಸ್ಕಾರ', 'ಹೇಗಿದ್ದೀಯ', 'ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ']
    }
    
    # Thank you patterns
    thanks_patterns = {
        'english': ['thank', 'thanks', 'thx', 'appreciate', 'grateful', 'ty', 'thank you so much', 'thanks a lot'],
        'hindi': ['धन्यवाद', 'शुक्रिया', 'थैंक्स', 'बहुत बहुत धन्यवाद', 'आभार'],
        'kannada': ['ಧನ್ಯವಾದ', 'ಥ್ಯಾಂಕ್ಸ್', 'ಕೃತಜ್ಞತೆ', 'ಬಹಳ ಧನ್ಯವಾದಗಳು', 'ಆಭಾರ']
    }
    
    # How are you patterns
    how_are_you_patterns = {
        'english': ['how are you', 'how r u', 'how do you do', 'are you ok', 'are you fine', 'how is it going', 'how are things', 'whats up with you'],
        'hindi': ['कैसे हो', 'कैसे हैं', 'कैसा चल रहा है', 'ठीक हो', 'कैसा है', 'क्या हाल है'],
        'kannada': ['ಹೇಗಿದ್ದೀಯ', 'ಹೇಗಿದ್ದೀರಿ', 'ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ', 'ಒಳ್ಳೆಯದು', 'ಹೇಗಿದೆ', 'ಎಲ್ಲಾ ಹೇಗಿದೆ']
    }
    
    # General question patterns
    general_question_patterns = {
        'english': ['what are you', 'who are you', 'what can you do', 'tell me about yourself', 'what is your purpose', 'what do you do', 'whats your job'],
        'hindi': ['आप क्या हैं', 'आप कौन हैं', 'आप क्या कर सकते हैं', 'अपने बारे में बताएं', 'आपका काम क्या है'],
        'kannada': ['ನೀವು ಏನು', 'ನೀವು ಯಾರು', 'ನೀವು ಏನು ಮಾಡಬಹುದು', 'ನಿಮ್ಮ ಬಗ್ಗೆ ಹೇಳಿ', 'ನಿಮ್ಮ ಕೆಲಸ ಏನು']
    }
    
    # Goodbye patterns
    goodbye_patterns = {
        'english': ['bye', 'goodbye', 'see you', 'take care', 'good night', 'good day', 'farewell', 'cya', 'see ya'],
        'hindi': ['अलविदा', 'फिर मिलेंगे', 'ध्यान रखना', 'शुभ रात्रि', 'शुभ दिन'],
        'kannada': ['ಬೀಗ್', 'ಮತ್ತೆ ಸಿಗೋಣ', 'ಜಾಗರೂಕರಾಗಿರಿ', 'ಶುಭ ರಾತ್ರಿ', 'ಶುಭ ದಿನ']
    }
    
    # Check for thanks first (to avoid conflicts with greetings)
    for pattern in thanks_patterns.get(language, thanks_patterns['english']):
        if pattern in user_input:
            return 'thanks'
    
    # Check for how are you
    for pattern in how_are_you_patterns.get(language, how_are_you_patterns['english']):
        if pattern in user_input:
            return 'how_are_you'
    
    # Check for general questions
    for pattern in general_question_patterns.get(language, general_question_patterns['english']):
        if pattern in user_input:
            return 'general_questions'
    
    # Check for goodbye
    for pattern in goodbye_patterns.get(language, goodbye_patterns['english']):
        if pattern in user_input:
            return 'goodbye'
    
    # Check for greetings last (to avoid conflicts with other patterns)
    for pattern in greeting_patterns.get(language, greeting_patterns['english']):
        if pattern in user_input:
            return 'greetings'
    
    return None

def get_conversational_response(pattern_type, language='english'):
    """Get a conversational response based on pattern type"""
    import random
    
    if pattern_type in conversational_responses and language in conversational_responses[pattern_type]:
        responses = conversational_responses[pattern_type][language]
        return random.choice(responses)
    
    # Fallback to English if language not found
    if pattern_type in conversational_responses and 'english' in conversational_responses[pattern_type]:
        responses = conversational_responses[pattern_type]['english']
        return random.choice(responses)
    
    return None

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

def get_fallback_response(language='english'):
    """Get a fallback response when no specific pattern is detected"""
    fallback_responses = {
        'english': [
            "I'm here to help with your health concerns! Could you please describe any symptoms you're experiencing, or ask me about general health topics?",
            "I'm your AI healthcare assistant! Feel free to ask me about symptoms, treatments, or any health-related questions you might have.",
            "Hello! I'm designed to help with medical queries and health guidance. What would you like to know about your health today?",
            "I'm here to assist with your health! You can ask me about symptoms, medications, treatments, or general health advice. How can I help?"
        ],
        'hindi': [
            "मैं आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने के लिए यहां हूं! क्या आप कृपया बता सकते हैं कि आप कौन से लक्षण अनुभव कर रहे हैं, या मुझसे सामान्य स्वास्थ्य विषयों के बारे में पूछ सकते हैं?",
            "मैं आपका AI स्वास्थ्य सहायक हूं! लक्षणों, उपचारों, या आपके पास हो सकने वाले किसी भी स्वास्थ्य संबंधी प्रश्न के बारे में मुझसे पूछने में संकोच न करें।",
            "नमस्ते! मैं चिकित्सीय प्रश्नों और स्वास्थ्य मार्गदर्शन में मदद करने के लिए डिज़ाइन किया गया हूं। आज आप अपने स्वास्थ्य के बारे में क्या जानना चाहते हैं?",
            "मैं आपकी स्वास्थ्य में सहायता करने के लिए यहां हूं! आप मुझसे लक्षणों, दवाओं, उपचारों, या सामान्य स्वास्थ्य सलाह के बारे में पूछ सकते हैं। मैं कैसे मदद कर सकता हूं?"
        ],
        'kannada': [
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ! ದಯವಿಟ್ಟು ನೀವು ಅನುಭವಿಸುತ್ತಿರುವ ಯಾವುದೇ ಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಬಹುದೇ, ಅಥವಾ ಸಾಮಾನ್ಯ ಆರೋಗ್ಯ ವಿಷಯಗಳ ಬಗ್ಗೆ ನನ್ನನ್ನು ಕೇಳಬಹುದೇ?",
            "ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ! ಲಕ್ಷಣಗಳು, ಚಿಕಿತ್ಸೆಗಳು, ಅಥವಾ ನಿಮ್ಮ ಬಳಿ ಇರಬಹುದಾದ ಯಾವುದೇ ಆರೋಗ್ಯ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಗಳ ಬಗ್ಗೆ ನನ್ನನ್ನು ಕೇಳಲು ಹಿಂಜರಿಯಬೇಡಿ.",
            "ನಮಸ್ಕಾರ! ನಾನು ವೈದ್ಯಕೀಯ ಪ್ರಶ್ನೆಗಳು ಮತ್ತು ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾಗಿದೆ. ಇಂದು ನಿಮ್ಮ ಆರೋಗ್ಯದ ಬಗ್ಗೆ ನೀವು ಏನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ! ನೀವು ಲಕ್ಷಣಗಳು, ಔಷಧಿಗಳು, ಚಿಕಿತ್ಸೆಗಳು, ಅಥವಾ ಸಾಮಾನ್ಯ ಆರೋಗ್ಯ ಸಲಹೆಯ ಬಗ್ಗೆ ನನ್ನನ್ನು ಕೇಳಬಹುದು. ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        ]
    }
    
    import random
    responses = fallback_responses.get(language, fallback_responses['english'])
    return random.choice(responses)

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

        # Find matching symptoms FIRST (prioritize medical over conversational)
        symptoms = find_matching_symptoms(user_input, language)

        if symptoms:
            # Medical symptoms detected - provide medical advice
            advice = get_medical_advice(symptoms, language)

            # Log conversation
            log_conversation(user_input, advice, language)

            return jsonify({
                'success': True,
                'response': advice,
                'symptoms_detected': symptoms,
                'is_conversational': False
            })
        else:
            # No medical symptoms detected, check for conversational patterns
            pattern = detect_conversational_pattern(user_input, language)

            if pattern:
                # Get conversational response
                response_text = get_conversational_response(pattern, language)
                if response_text:
                    # Log conversation
                    log_conversation(user_input, {'message': response_text}, language)
                    
                    return jsonify({
                        'success': True,
                        'response': {'message': response_text},
                        'symptoms_detected': [], # No medical symptoms for conversational responses
                        'is_conversational': True
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Could not generate conversational response'
                    })
            else:
                # No symptoms or conversational patterns detected, provide fallback response
                fallback_message = get_fallback_response(language)
                
                # Log conversation
                log_conversation(user_input, {'message': fallback_message}, language)
                
                return jsonify({
                    'success': True,
                    'response': {'message': fallback_message},
                    'symptoms_detected': [],
                    'is_conversational': True
                })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'})

        audio_file = request.files['audio']
        
        # Save incoming webm audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
            audio_file.save(temp_webm.name)
            webm_path = temp_webm.name
        
        # Convert webm to wav using ffmpeg
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            wav_path = temp_wav.name
        
        try:
            ffmpeg.input(webm_path).output(wav_path).run(overwrite_output=True)
        except ffmpeg.Error as e:
            return jsonify({'success': False, 'error': 'FFmpeg conversion failed', 'details': e.stderr.decode()})

        # Transcribe using SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='en-US')

        # Clean up
        os.remove(webm_path)
        os.remove(wav_path)

        return jsonify({'success': True, 'text': text})

    except sr.UnknownValueError:
        return jsonify({'success': False, 'error': 'Could not understand the audio'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing audio: {str(e)}'})
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'english')
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})

        lang_codes = {'english': 'en', 'hindi': 'hi', 'kannada': 'kn'}
        lang_code = lang_codes.get(language, 'en')

        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()

        return jsonify({'success': True, 'audio': audio_base64})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating speech: {str(e)}'})

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
