
# Enhanced AI Healthcare Chatbot - Setup Instructions

## Overview
This is an enhanced AI-powered healthcare chatbot that provides detailed medical advice including:
- Specific medication recommendations with dosages
- Precautions to take
- Treatment suggestions
- Dietary recommendations
- When to see a doctor

## Features
✅ Voice input and output
✅ Multi-language support (English, Hindi, Kannada)
✅ Detailed medication recommendations
✅ Professional medical advice
✅ Conversation logging
✅ Responsive web interface
✅ Real-time symptom analysis

## Installation Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Microphone (for voice input)
- Internet connection (for text-to-speech)

### Step 1: Download Files
Make sure you have these files in your project directory:
- `app.py` (Flask backend)
- `templates/index.html` (Frontend)
- `enhanced_medical_dataset.csv` (Medical data)
- `requirements.txt` (Dependencies)

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv healthcare_chatbot

# Activate virtual environment
# On Windows:
healthcare_chatbot\Scripts\activate
# On macOS/Linux:
source healthcare_chatbot/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Note: If you encounter issues with pyaudio installation:

**On Windows:**
```bash
pip install pyaudio
```
If that fails, download the appropriate .whl file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

**On macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on http://localhost:5000

### Step 5: Access the Chatbot
1. Open your web browser
2. Navigate to http://localhost:5000
3. Start chatting with the AI healthcare assistant!

## Usage Examples

### Text Input Examples:
- "I have a headache and fever"
- "My stomach is hurting"
- "I have a sore throat and cough"
- "Back pain and joint stiffness"

### Voice Input:
1. Click the microphone button
2. Speak your symptoms clearly
3. Click stop when finished
4. The system will process your voice and respond

### Language Support:
- Click on English/हिन्दी/ಕನ್ನಡ buttons to change language
- All responses will be in your selected language

## File Structure
```
healthcare_chatbot/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── enhanced_medical_dataset.csv    # Medical knowledge base
├── templates/
│   └── index.html                 # Frontend interface
└── logs/
    └── conversation_log.csv       # Chat history (created automatically)
```

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Kill process on port 5000
   # Windows: netstat -ano | findstr :5000
   # macOS/Linux: lsof -ti:5000 | xargs kill -9
   ```

2. **Microphone not working:**
   - Check browser permissions for microphone access
   - Ensure microphone is connected and working
   - Try refreshing the page

3. **Voice recognition not working:**
   - Ensure internet connection (uses Google Speech Recognition)
   - Speak clearly and avoid background noise
   - Try using text input as alternative

4. **CSV file not found:**
   - Make sure `enhanced_medical_dataset.csv` is in the same directory as `app.py`
   - Check file permissions

### Performance Tips:
- Use a modern web browser (Chrome, Firefox, Safari, Edge)
- Ensure stable internet connection for voice features
- Close unnecessary browser tabs for better performance

## Customization

### Adding New Symptoms/Diseases:
1. Edit `enhanced_medical_dataset.csv`
2. Add new rows with columns: symptom, disease, severity, description, medication, precautions, treatment, diet, when_to_see_doctor
3. Restart the application

### Modifying Languages:
1. Edit the `translations` dictionary in `app.py`
2. Add new language codes and translations
3. Update the HTML language selector

## Disclaimer
⚠️ **Important Medical Disclaimer:**
This chatbot is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.

## Support
If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify Python version compatibility (3.7+)
4. Check console/terminal for error messages

Happy chatting with your AI Healthcare Assistant! 🏥🤖
# my_ai_chatbot





cd /Users/quanteondev/Downloads/Arc_AI_Chatbot-main
chmod +x run.sh
./run.sh

cd /Users/quanteondev/Downloads/Arc_AI_Chatbot-main
source healthcare_env/bin/activate
python app.py