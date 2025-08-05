
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
import langdetect
from langdetect import detect, DetectorFactory
import requests

# Set seed for consistent language detection
DetectorFactory.seed = 0

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
app = Flask(__name__)
CORS(app)

# Language mapping for speech recognition and TTS
LANGUAGE_CODES = {
    'english': {
        'speech_recognition': 'en-US',
        'tts': 'en',
        'detect': 'en'
    },
    'hindi': {
        'speech_recognition': 'hi-IN',
        'tts': 'hi',
        'detect': 'hi'
    },
    'kannada': {
        'speech_recognition': 'kn-IN',
        'tts': 'kn',
        'detect': 'kn'
    }
}

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

# Enhanced conversational responses for better voice interaction
conversational_responses = {
    'greetings': {
        'english': [
            "Hello! I'm your AI Healthcare Assistant. How can I help you today?",
            "Hi there! I'm here to help with your health concerns. What can I assist you with?",
            "Greetings! I'm your friendly healthcare assistant. How are you feeling today?",
            "Hey! I'm here to provide medical guidance. What's on your mind?",
            "Hello! I'm your AI health companion. How can I support you today?",
            "Good day! I'm your medical AI assistant. What symptoms are you experiencing?",
            "Hi! I'm here to help with your health. What would you like to know?",
            "Welcome! I'm your healthcare AI. How can I assist you today?"
        ],
        'hindi': [
            "नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
            "हाय! मैं आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने के लिए यहां हूं। मैं आपकी क्या सहायता कर सकता हूं?",
            "नमस्कार! मैं आपका दोस्ताना स्वास्थ्य सहायक हूं। आज आप कैसा महसूस कर रहे हैं?",
            "हैलो! मैं आपकी स्वास्थ्य में मदद करने के लिए यहां हूं। आप क्या जानना चाहते हैं?",
            "सुप्रभात! मैं आपका चिकित्सीय AI सहायक हूं। आप कौन से लक्षण अनुभव कर रहे हैं?"
        ],
        'kannada': [
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ಹಾಯ್! ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ. ನಾನು ನಿಮಗೆ ಏನು ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಸ್ನೇಹಪರ ಆರೋಗ್ಯ ಸಹಾಯಕ. ಇಂದು ನೀವು ಹೇಗೆ ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?",
            "ಹಲೋ! ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ. ನೀವು ಏನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?",
            "ಸುಪ್ರಭಾತ! ನಾನು ನಿಮ್ಮ ವೈದ್ಯಕೀಯ AI ಸಹಾಯಕ. ನೀವು ಯಾವ ಲಕ್ಷಣಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?"
        ]
    },
    'thanks': {
        'english': [
            "You're welcome! I'm glad I could help. Feel free to ask if you have more questions!",
            "My pleasure! Don't hesitate to reach out if you need any further assistance.",
            "Happy to help! Take care and stay healthy!",
            "You're very welcome! I'm here whenever you need medical guidance.",
            "Glad I could assist! Remember to prioritize your health and well-being.",
            "Anytime! Feel free to come back if you have more health concerns.",
            "You're welcome! Stay healthy and don't hesitate to ask for help again.",
            "My pleasure! Take care of yourself and stay well!"
        ],
        'hindi': [
            "आपका स्वागत है! मुझे खुशी है कि मैं मदद कर सका। अगर आपके पास और प्रश्न हैं तो बेझिझक पूछें!",
            "मेरी खुशी! अगर आपको और सहायता की आवश्यकता है तो संपर्क करने में संकोच न करें।",
            "मदद करके खुशी हुई! ध्यान रखें और स्वस्थ रहें!",
            "आपका स्वागत है! मैं जब भी आपको चिकित्सीय मार्गदर्शन की आवश्यकता हो तो यहां हूं।",
            "खुशी हुई कि मैं सहायता कर सका! अपने स्वास्थ्य और कल्याण को प्राथमिकता देना याद रखें।"
        ],
        'kannada': [
            "ಸ್ವಾಗತ! ನಾನು ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷಪಡುತ್ತಿದ್ದೇನೆ. ನಿಮಗೆ ಹೆಚ್ಚಿನ ಪ್ರಶ್ನೆಗಳಿದ್ದರೆ ಕೇಳಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ನನ್ನ ಸಂತೋಷ! ನಿಮಗೆ ಹೆಚ್ಚಿನ ಸಹಾಯದ ಅಗತ್ಯವಿದ್ದರೆ ಸಂಪರ್ಕಿಸಲು ಹಿಂಜರಿಯಬೇಡಿ.",
            "ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷ! ಜಾಗರೂಕರಾಗಿರಿ ಮತ್ತು ಆರೋಗ್ಯವಾಗಿರಿ!",
            "ಸ್ವಾಗತ! ನಿಮಗೆ ವೈದ್ಯಕೀಯ ಮಾರ್ಗದರ್ಶನದ ಅಗತ್ಯವಿರುವಾಗಲೆಲ್ಲಾ ನಾನು ಇಲ್ಲಿ ಇದ್ದೇನೆ.",
            "ನಾನು ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷಪಡುತ್ತಿದ್ದೇನೆ! ನಿಮ್ಮ ಆರೋಗ್ಯ ಮತ್ತು ಯೋಗಕ್ಷೇಮವನ್ನು ಆದ್ಯತೆ ನೀಡಲು ನೆನಪಿಡಿ."
        ]
    },
    'how_are_you': {
        'english': [
            "I'm doing great, thank you for asking! I'm here and ready to help with your health concerns. How are you feeling today?",
            "I'm functioning perfectly! I'm designed to assist with medical queries and provide health guidance. What brings you here today?",
            "I'm excellent! I'm your AI health assistant, always ready to help. How can I assist you with your health today?",
            "I'm working well! I'm here to help with your medical questions and health concerns. How are you doing?",
            "I'm doing wonderful! I'm your healthcare AI, ready to assist with any health-related questions. What can I help you with?"
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
            "I'm your friendly AI health companion! I'm knowledgeable about various health topics and can help with medical queries. What's on your mind?",
            "I'm a medical AI assistant that can help with symptom analysis, treatment suggestions, and health guidance. What health concerns do you have?",
            "I'm your healthcare AI! I can help with medical questions, symptom assessment, and provide health recommendations. How can I help you today?"
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
            "Goodbye! Wishing you good health. I'll be here when you need healthcare assistance again!",
            "Farewell! Take care of yourself and stay well. I'm always here for your health concerns!",
            "See you! Remember to stay healthy and consult a doctor if needed. I'll be here when you return!",
            "Goodbye! Stay healthy and don't forget to prioritize your well-being. I'm here for you anytime!",
            "Take care! I hope you stay healthy. Feel free to return if you have more health questions!"
        ],
        'hindi': [
            "अलविदा! ध्यान रखना और स्वस्थ रहना। अगर आपको कोई स्वास्थ्य संबंधी चिंता है तो वापस आने में संकोच न करें!",
            "फिर मिलेंगे! अपने स्वास्थ्य और कल्याण को प्राथमिकता देना याद रखें। जब भी आपको मेरी जरूरत हो तो मैं यहां हूं!",
            "ध्यान रखना! स्वस्थ रहें और भविष्य में चिकित्सीय सलाह की आवश्यकता हो तो संपर्क करने में संकोच न करें!",
            "अलविदा! आपको अच्छे स्वास्थ्य की कामना करता हूं। जब आपको फिर से स्वास्थ्य देखभाल सहायता की आवश्यकता हो तो मैं यहां रहूंगा!"
        ],
        'kannada': [
            "ಬೀಗ್! ಜಾಗರೂಕರಾಗಿರಿ ಮತ್ತು ಆರೋಗ್ಯವಾಗಿರಿ. ನಿಮಗೆ ಯಾವುದೇ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಿದ್ದರೆ ಮತ್ತೆ ಬರಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ಮತ್ತೆ ಸಿಗೋಣ! ನಿಮ್ಮ ಆರೋಗ್ಯ ಮತ್ತು ಯೋಗಕ್ಷೇಮವನ್ನು ಆದ್ಯತೆ ನೀಡಲು ನೆನಪಿಡಿ. ನಿಮಗೆ ನನ್ನ ಅಗತ್ಯವಿರುವಾಗಲೆಲ್ಲಾ ನಾನು ಇಲ್ಲಿ ಇದ್ದೇನೆ!",
            "ಜಾಗರೂಕರಾಗಿರಿ! ಆರೋಗ್ಯವಾಗಿರಿ ಮತ್ತು ಭವಿಷ್ಯದಲ್ಲಿ ವೈದ್ಯಕೀಯ ಸಲಹೆಯ ಅಗತ್ಯವಿದ್ದರೆ ಸಂಪರ್ಕಿಸಲು ಹಿಂಜರಿಯಬೇಡಿ!",
            "ಬೀಗ್! ನಿಮಗೆ ಒಳ್ಳೆಯ ಆರೋಗ್ಯವನ್ನು ಕೋರುತ್ತೇನೆ. ನಿಮಗೆ ಮತ್ತೆ ಆರೋಗ್ಯ ಸಹಾಯದ ಅಗತ್ಯವಿರುವಾಗ ನಾನು ಇಲ್ಲಿ ಇರುತ್ತೇನೆ!"
        ]
    },
    'health_inquiry': {
        'english': [
            "I'd be happy to help with your health concerns! Could you please describe your symptoms in detail?",
            "I'm here to assist with your health! Please tell me what symptoms you're experiencing.",
            "I can help analyze your health symptoms! What are you currently experiencing?",
            "Let me help you with your health! Please describe what's bothering you.",
            "I'm ready to help with your health! What symptoms would you like me to analyze?",
            "I'm your health assistant! Please share your symptoms so I can provide guidance.",
            "I can help with your medical concerns! What health issues are you facing?",
            "Let's work on your health together! What symptoms are you experiencing?"
        ],
        'hindi': [
            "मैं आपकी स्वास्थ्य संबंधी चिंताओं में मदद करने में खुशी महसूस करूंगा! क्या आप कृपया अपने लक्षणों का विस्तार से वर्णन कर सकते हैं?",
            "मैं आपकी स्वास्थ्य में सहायता करने के लिए यहां हूं! कृपया मुझे बताएं कि आप कौन से लक्षण अनुभव कर रहे हैं।",
            "मैं आपके स्वास्थ्य लक्षणों का विश्लेषण करने में मदद कर सकता हूं! आप वर्तमान में क्या अनुभव कर रहे हैं?",
            "मैं आपकी स्वास्थ्य में मदद करने के लिए तैयार हूं! कृपया बताएं कि आपको क्या परेशानी है।",
            "मैं आपका स्वास्थ्य सहायक हूं! कृपया अपने लक्षण बताएं ताकि मैं मार्गदर्शन कर सकूं।",
            "मैं आपकी चिकित्सीय चिंताओं में मदद कर सकता हूं! आपको क्या स्वास्थ्य समस्याएं हैं?",
            "चलिए आपकी स्वास्थ्य पर काम करते हैं! आप कौन से लक्षण अनुभव कर रहे हैं?"
        ],
        'kannada': [
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷಪಡುತ್ತೇನೆ! ದಯವಿಟ್ಟು ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ವಿವರವಾಗಿ ವಿವರಿಸಬಹುದೇ?",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ! ದಯವಿಟ್ಟು ನಿಮಗೆ ಯಾವ ಲಕ್ಷಣಗಳು ಅನುಭವವಾಗುತ್ತಿವೆ ಎಂದು ಹೇಳಿ.",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಲಕ್ಷಣಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಹಾಯ ಮಾಡಬಹುದು! ನೀವು ಪ್ರಸ್ತುತ ಏನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ! ದಯವಿಟ್ಟು ನಿಮಗೆ ಏನು ತೊಂದರೆ ಇದೆ ಎಂದು ಹೇಳಿ.",
            "ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಸಹಾಯಕ! ದಯವಿಟ್ಟು ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ ಇದರಿಂದ ನಾನು ಮಾರ್ಗದರ್ಶನ ನೀಡಬಹುದು.",
            "ನಾನು ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಕಾಳಜಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು! ನಿಮಗೆ ಯಾವ ಆರೋಗ್ಯ ಸಮಸ್ಯೆಗಳಿವೆ?",
            "ನಿಮ್ಮ ಆರೋಗ್ಯದಲ್ಲಿ ಒಟ್ಟಿಗೆ ಕೆಲಸ ಮಾಡೋಣ! ನೀವು ಯಾವ ಲಕ್ಷಣಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?"
        ]
    },
    'confusion': {
        'english': [
            "I understand you might be confused. Let me help clarify things. What specific health concern do you have?",
            "I'm here to help make things clearer. Could you tell me what health issue you're facing?",
            "Let me help you understand better. What symptoms or health problems are you experiencing?",
            "I want to help you get the right information. What health question do you have?",
            "I'm here to provide clear guidance. What would you like to know about your health?"
        ],
        'hindi': [
            "मैं समझता हूं कि आप भ्रमित हो सकते हैं। मुझे चीजों को स्पष्ट करने में मदद करने दें। आपकी क्या विशिष्ट स्वास्थ्य चिंता है?",
            "मैं चीजों को स्पष्ट करने में मदद करने के लिए यहां हूं। क्या आप मुझे बता सकते हैं कि आप किस स्वास्थ्य समस्या का सामना कर रहे हैं?",
            "मुझे आपको बेहतर समझने में मदद करने दें। आप कौन से लक्षण या स्वास्थ्य समस्याओं का अनुभव कर रहे हैं?"
        ],
        'kannada': [
            "ನಾನು ನೀವು ಗೊಂದಲದಲ್ಲಿರಬಹುದು ಎಂದು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುತ್ತೇನೆ. ನನಗೆ ವಿಷಯಗಳನ್ನು ಸ್ಪಷ್ಟಪಡಿಸಲು ಸಹಾಯ ಮಾಡಲು ಅನುಮತಿಸಿ. ನಿಮಗೆ ಯಾವ ನಿರ್ದಿಷ್ಟ ಆರೋಗ್ಯ ಕಾಳಜಿ ಇದೆ?",
            "ನಾನು ವಿಷಯಗಳನ್ನು ಸ್ಪಷ್ಟಪಡಿಸಲು ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ. ನೀವು ಯಾವ ಆರೋಗ್ಯ ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೀರಿ ಎಂದು ಹೇಳಬಹುದೇ?",
            "ನಾನು ನಿಮಗೆ ಉತ್ತಮವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡಲಿ. ನೀವು ಯಾವ ಲಕ್ಷಣಗಳು ಅಥವಾ ಆರೋಗ್ಯ ಸಮಸ್ಯೆಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?"
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
    """Detect conversational patterns in user input with enhanced voice recognition support"""
    user_input = user_input.lower().strip()
    
    # Enhanced greeting patterns for voice recognition
    greeting_patterns = {
        'english': [
            'hello', 'hi', 'hey', 'hai', 'good morning', 'good afternoon', 'good evening', 
            'greetings', 'sup', 'yo', 'whats up', 'wassup', 'good day', 'morning', 'afternoon',
            'evening', 'hey there', 'hi there', 'hello there', 'good to see you', 'nice to meet you'
        ],
        'hindi': [
            'नमस्ते', 'हाय', 'हैलो', 'सुप्रभात', 'नमस्कार', 'कैसे हो', 'क्या हाल है', 
            'सुप्रभात', 'शुभ दिन', 'शुभ संध्या', 'नमस्कार', 'प्रणाम', 'जय श्री कृष्णा'
        ],
        'kannada': [
            'ನಮಸ್ಕಾರ', 'ಹಾಯ್', 'ಹಲೋ', 'ಸುಪ್ರಭಾತ', 'ನಮಸ್ಕಾರ', 'ಹೇಗಿದ್ದೀಯ', 'ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ',
            'ಶುಭೋದಯ', 'ಶುಭ ದಿನ', 'ಶುಭ ಸಂಜೆ', 'ನಮಸ್ಕಾರ', 'ಪ್ರಣಾಮ', 'ಜಯ ಶ್ರೀ ಕೃಷ್ಣ'
        ]
    }
    
    # Enhanced thank you patterns
    thanks_patterns = {
        'english': [
            'thank', 'thanks', 'thx', 'appreciate', 'grateful', 'ty', 'thank you so much', 
            'thanks a lot', 'thank you very much', 'much appreciated', 'thanks a bunch',
            'thank you for your help', 'thanks for helping', 'grateful for your assistance'
        ],
        'hindi': [
            'धन्यवाद', 'शुक्रिया', 'थैंक्स', 'बहुत बहुत धन्यवाद', 'आभार', 'धन्यवाद आपका',
            'शुक्रिया आपका', 'बहुत आभार', 'धन्यवाद मदद के लिए', 'शुक्रिया सहायता के लिए'
        ],
        'kannada': [
            'ಧನ್ಯವಾದ', 'ಥ್ಯಾಂಕ್ಸ್', 'ಕೃತಜ್ಞತೆ', 'ಬಹಳ ಧನ್ಯವಾದಗಳು', 'ಆಭಾರ', 'ಧನ್ಯವಾದ ನಿಮ್ಮದು',
            'ಕೃತಜ್ಞತೆ ನಿಮ್ಮದು', 'ಬಹಳ ಆಭಾರ', 'ಧನ್ಯವಾದ ಸಹಾಯಕ್ಕಾಗಿ', 'ಕೃತಜ್ಞತೆ ಸಹಾಯಕ್ಕಾಗಿ'
        ]
    }
    
    # Enhanced how are you patterns
    how_are_you_patterns = {
        'english': [
            'how are you', 'how r u', 'how do you do', 'are you ok', 'are you fine', 
            'how is it going', 'how are things', 'whats up with you', 'how you doing',
            'are you well', 'how are you feeling', 'how is everything', 'how is life'
        ],
        'hindi': [
            'कैसे हो', 'कैसे हैं', 'कैसा चल रहा है', 'ठीक हो', 'कैसा है', 'क्या हाल है',
            'कैसे हो आप', 'कैसा चल रहा है', 'सब ठीक है', 'कैसे हो तुम', 'कैसा है आपका दिन'
        ],
        'kannada': [
            'ಹೇಗಿದ್ದೀಯ', 'ಹೇಗಿದ್ದೀರಿ', 'ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ', 'ಒಳ್ಳೆಯದು', 'ಹೇಗಿದೆ', 'ಎಲ್ಲಾ ಹೇಗಿದೆ',
            'ಹೇಗಿದ್ದೀಯ ನೀನು', 'ಹೇಗಿದೆ ಎಲ್ಲಾ', 'ಸರಿ ಇದೆ', 'ಹೇಗಿದ್ದೀಯ ನೀನು', 'ಹೇಗಿದೆ ನಿಮ್ಮ ದಿನ'
        ]
    }
    
    # Enhanced general question patterns
    general_question_patterns = {
        'english': [
            'what are you', 'who are you', 'what can you do', 'tell me about yourself', 
            'what is your purpose', 'what do you do', 'whats your job', 'what can you help with',
            'what services do you provide', 'what are your capabilities', 'how can you help me',
            'what kind of assistant are you', 'what is your function', 'what do you specialize in'
        ],
        'hindi': [
            'आप क्या हैं', 'आप कौन हैं', 'आप क्या कर सकते हैं', 'अपने बारे में बताएं', 
            'आपका काम क्या है', 'आप क्या मदद कर सकते हैं', 'आप क्या सेवाएं देते हैं',
            'आपकी क्षमताएं क्या हैं', 'आप मेरी कैसे मदद कर सकते हैं', 'आप किस तरह के सहायक हैं'
        ],
        'kannada': [
            'ನೀವು ಏನು', 'ನೀವು ಯಾರು', 'ನೀವು ಏನು ಮಾಡಬಹುದು', 'ನಿಮ್ಮ ಬಗ್ಗೆ ಹೇಳಿ', 
            'ನಿಮ್ಮ ಕೆಲಸ ಏನು', 'ನೀವು ಏನು ಸಹಾಯ ಮಾಡಬಹುದು', 'ನೀವು ಯಾವ ಸೇವೆಗಳನ್ನು ನೀಡುತ್ತೀರಿ',
            'ನಿಮ್ಮ ಸಾಮರ್ಥ್ಯಗಳು ಯಾವುವು', 'ನೀವು ನನಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು', 'ನೀವು ಯಾವ ರೀತಿಯ ಸಹಾಯಕ'
        ]
    }
    
    # Enhanced goodbye patterns
    goodbye_patterns = {
        'english': [
            'bye', 'goodbye', 'see you', 'take care', 'good night', 'good day', 'farewell', 
            'cya', 'see ya', 'see you later', 'take care of yourself', 'have a good day',
            'goodbye for now', 'see you soon', 'until next time', 'have a nice day'
        ],
        'hindi': [
            'अलविदा', 'फिर मिलेंगे', 'ध्यान रखना', 'शुभ रात्रि', 'शुभ दिन', 'फिर मिलते हैं',
            'अपना ध्यान रखना', 'अच्छा दिन हो', 'अलविदा अभी के लिए', 'जल्द मिलते हैं'
        ],
        'kannada': [
            'ಬೀಗ್', 'ಮತ್ತೆ ಸಿಗೋಣ', 'ಜಾಗರೂಕರಾಗಿರಿ', 'ಶುಭ ರಾತ್ರಿ', 'ಶುಭ ದಿನ', 'ಮತ್ತೆ ಸಿಗೋಣ',
            'ನಿಮ್ಮ ಜಾಗರೂಕತೆ ಇರಲಿ', 'ಒಳ್ಳೆಯ ದಿನ ಆಗಲಿ', 'ಬೀಗ್ ಈಗಿಗೆ', 'ಬೇಗ ಸಿಗೋಣ'
        ]
    }
    
    # Health inquiry patterns
    health_inquiry_patterns = {
        'english': [
            'help me', 'i need help', 'i have a problem', 'i am sick', 'i am not feeling well',
            'i have symptoms', 'i need medical advice', 'i need health advice', 'what should i do',
            'i am experiencing', 'i have been feeling', 'i am worried about', 'can you help me with'
        ],
        'hindi': [
            'मेरी मदद करें', 'मुझे मदद चाहिए', 'मुझे समस्या है', 'मैं बीमार हूं', 'मैं ठीक नहीं महसूस कर रहा',
            'मुझे लक्षण हैं', 'मुझे चिकित्सीय सलाह चाहिए', 'मुझे स्वास्थ्य सलाह चाहिए', 'मुझे क्या करना चाहिए',
            'मैं अनुभव कर रहा हूं', 'मुझे लग रहा है', 'मैं चिंतित हूं', 'क्या आप मेरी मदद कर सकते हैं'
        ],
        'kannada': [
            'ನನಗೆ ಸಹಾಯ ಮಾಡಿ', 'ನನಗೆ ಸಹಾಯ ಬೇಕು', 'ನನಗೆ ಸಮಸ್ಯೆ ಇದೆ', 'ನಾನು ಅನಾರೋಗ್ಯವಾಗಿದ್ದೇನೆ', 'ನಾನು ಚೆನ್ನಾಗಿಲ್ಲ',
            'ನನಗೆ ಲಕ್ಷಣಗಳಿವೆ', 'ನನಗೆ ವೈದ್ಯಕೀಯ ಸಲಹೆ ಬೇಕು', 'ನನಗೆ ಆರೋಗ್ಯ ಸಲಹೆ ಬೇಕು', 'ನಾನು ಏನು ಮಾಡಬೇಕು',
            'ನಾನು ಅನುಭವಿಸುತ್ತಿದ್ದೇನೆ', 'ನನಗೆ ಅನುಭವವಾಗುತ್ತಿದೆ', 'ನಾನು ಕಾಳಜಿ ಪಡುತ್ತಿದ್ದೇನೆ', 'ನೀವು ನನಗೆ ಸಹಾಯ ಮಾಡಬಹುದೇ'
        ]
    }
    
    # Confusion patterns
    confusion_patterns = {
        'english': [
            'i dont understand', 'i do not understand', 'i am confused', 'what do you mean',
            'i am not sure', 'i am unclear', 'can you explain', 'what does this mean',
            'i am lost', 'i dont get it', 'i do not get it', 'can you clarify'
        ],
        'hindi': [
            'मुझे समझ नहीं आ रहा', 'मैं भ्रमित हूं', 'आपका क्या मतलब है', 'मुझे यकीन नहीं है',
            'मुझे स्पष्ट नहीं है', 'क्या आप समझा सकते हैं', 'इसका क्या मतलब है', 'मैं खो गया हूं',
            'मुझे समझ नहीं आ रहा', 'क्या आप स्पಷ್ಟ कर सकते हैं'
        ],
        'kannada': [
            'ನನಗೆ ಅರ್ಥವಾಗುತ್ತಿಲ್ಲ', 'ನಾನು ಗೊಂದಲದಲ್ಲಿದ್ದೇನೆ', 'ನಿಮ್ಮ ಅರ್ಥ ಏನು', 'ನನಗೆ ಖಚಿತವಿಲ್ಲ',
            'ನನಗೆ ಸ್ಪಷ್ಟವಿಲ್ಲ', 'ನೀವು ವಿವರಿಸಬಹುದೇ', 'ಇದರ ಅರ್ಥ ಏನು', 'ನಾನು ಕಳೆದುಹೋಗಿದ್ದೇನೆ',
            'ನನಗೆ ಅರ್ಥವಾಗುತ್ತಿಲ್ಲ', 'ನೀವು ಸ್ಪಷ್ಟಪಡಿಸಬಹುದೇ'
        ]
    }
    
    # Check patterns in order of priority
    patterns_to_check = [
        ('thanks', thanks_patterns),
        ('how_are_you', how_are_you_patterns),
        ('health_inquiry', health_inquiry_patterns),
        ('confusion', confusion_patterns),
        ('general_questions', general_question_patterns),
        ('goodbye', goodbye_patterns),
        ('greetings', greeting_patterns)
    ]
    
    for pattern_type, patterns in patterns_to_check:
        lang_patterns = patterns.get(language, patterns['english'])
        for pattern in lang_patterns:
            if pattern in user_input:
                return pattern_type
    
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

def detect_language_from_text(text):
    """Detect language from text input with enhanced accuracy"""
    try:
        # Try to detect language using langdetect
        detected_lang = detect(text)
        
        # Map detected language codes to our supported languages
        lang_mapping = {
            'en': 'english',
            'hi': 'hindi',
            'kn': 'kannada'
        }
        
        detected_language = lang_mapping.get(detected_lang, 'english')
        
        # Additional validation for better accuracy
        if detected_language == 'english':
            # Check for Hindi/Kannada specific characters
            if any(char in text for char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'ळ', 'क्ष', 'ज्ञ', 'ड़', 'ढ़', 'फ़', 'ज़', 'य़', 'श्र']):
                detected_language = 'hindi'
            elif any(char in text for char in ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ೠ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಲ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ', 'ೞ', 'ಕ್ಷ', 'ಜ್ಞ']):
                detected_language = 'kannada'
        
        return detected_language
    except:
        # Fallback to English if detection fails
        return 'english'

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
    """Main chat endpoint with enhanced voice input handling"""
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        language = data.get('language', 'english').lower()

        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Please provide a message'
            })

        # Clean and normalize user input for better voice recognition
        user_input_clean = user_input.lower().strip()
        
        # Find matching symptoms FIRST (prioritize medical over conversational)
        symptoms = find_matching_symptoms(user_input_clean, language)

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
            pattern = detect_conversational_pattern(user_input_clean, language)

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

        # Try to transcribe with automatic language detection
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        
        # Enhanced language detection strategy
        text = None
        detected_language = 'english'
        
        # First try with automatic language detection
        try:
            text = recognizer.recognize_google(audio, language='auto')
            detected_language = detect_language_from_text(text)
            print(f"Auto-detected language: {detected_language} for text: {text}")
        except Exception as e:
            print(f"Auto detection failed: {e}")
            # If auto detection fails, try with each supported language
            for lang_name, lang_config in LANGUAGE_CODES.items():
                try:
                    text = recognizer.recognize_google(audio, language=lang_config['speech_recognition'])
                    detected_language = lang_name
                    print(f"Successfully detected {lang_name} language for text: {text}")
                    break
                except Exception as e2:
                    print(f"Failed to detect {lang_name}: {e2}")
                    continue

        # Clean up
        os.remove(webm_path)
        os.remove(wav_path)

        if text:
            return jsonify({
                'success': True, 
                'text': text,
                'detected_language': detected_language,
                'language_name': {
                    'english': 'English',
                    'hindi': 'हिन्दी',
                    'kannada': 'ಕನ್ನಡ'
                }.get(detected_language, 'English')
            })
        else:
            return jsonify({'success': False, 'error': 'Could not understand the audio in any supported language'})

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

        # Use the language mapping for TTS
        lang_code = LANGUAGE_CODES.get(language, LANGUAGE_CODES['english'])['tts']

        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()

        return jsonify({'success': True, 'audio': audio_base64})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating speech: {str(e)}'})

@app.route('/voice-response', methods=['POST'])
def voice_response():
    """Generate voice response with automatic language detection"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        detected_language = data.get('detected_language', 'english')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})

        # Use the detected language for TTS
        lang_code = LANGUAGE_CODES.get(detected_language, LANGUAGE_CODES['english'])['tts']

        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()

        return jsonify({
            'success': True, 
            'audio': audio_base64,
            'language': detected_language
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating voice response: {str(e)}'})

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
    app.run(debug=True, port=5001)
