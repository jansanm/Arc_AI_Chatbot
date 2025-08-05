# Voice Features Documentation

## Overview

The MedAI Healthcare Chatbot now supports advanced voice input and output capabilities with automatic language detection. Users can speak in their preferred language (English, Hindi, or Kannada) and receive voice responses in the same language.

## Features

### 1. Voice Input with Automatic Language Detection
- **Multi-language Speech Recognition**: Supports English, Hindi, and Kannada
- **Automatic Language Detection**: The system automatically detects the language spoken by the user
- **Fallback Mechanism**: If automatic detection fails, tries each supported language
- **Real-time Processing**: Converts speech to text instantly

### 2. Voice Output with Language Matching
- **Language-Specific TTS**: Responses are generated in the same language as the input
- **Natural Speech Synthesis**: Uses Google Text-to-Speech (gTTS) for high-quality voice output
- **Automatic Language Switching**: The system automatically switches TTS language based on detected input language

### 3. Enhanced User Interface
- **Voice Input Button**: Microphone button for voice recording
- **Voice Output Toggle**: Button to enable/disable voice responses
- **Language Indicator**: Shows current detected language
- **Visual Feedback**: Recording state and voice output status indicators

## Technical Implementation

### Backend Components

#### 1. Language Detection
```python
def detect_language_from_text(text):
    """Detect language from text input"""
    try:
        detected_lang = detect(text)
        lang_mapping = {
            'en': 'english',
            'hi': 'hindi',
            'kn': 'kannada'
        }
        return lang_mapping.get(detected_lang, 'english')
    except:
        return 'english'
```

#### 2. Enhanced Voice-to-Text
- Supports automatic language detection
- Fallback to manual language detection if auto-detection fails
- Returns detected language along with transcribed text

#### 3. Voice Response Generation
- New `/voice-response` endpoint
- Automatically uses detected language for TTS
- Generates audio in base64 format for browser playback

### Frontend Components

#### 1. Voice Recording
```javascript
async function toggleVoiceRecording() {
    if (!isRecording) {
        // Start recording
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(mediaStream);
        // ... recording logic
    } else {
        // Stop recording and process
        mediaRecorder.stop();
    }
}
```

#### 2. Voice Response
```javascript
async function generateVoiceResponse(text, language) {
    const response = await fetch('/voice-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, detected_language: language })
    });
    const data = await response.json();
    if (data.success) {
        playAudio(data.audio);
    }
}
```

## API Endpoints

### 1. `/voice-to-text` (POST)
Converts voice input to text with language detection.

**Request:**
- `audio`: Audio file (WebM format)

**Response:**
```json
{
    "success": true,
    "text": "transcribed text",
    "detected_language": "english"
}
```

### 2. `/voice-response` (POST)
Generates voice response in detected language.

**Request:**
```json
{
    "text": "text to convert to speech",
    "detected_language": "english"
}
```

**Response:**
```json
{
    "success": true,
    "audio": "base64_encoded_audio",
    "language": "english"
}
```

### 3. `/text-to-speech` (POST)
Legacy endpoint for text-to-speech conversion.

**Request:**
```json
{
    "text": "text to convert",
    "language": "english"
}
```

## Language Support

### Supported Languages
1. **English** (`en-US`)
   - Speech Recognition: `en-US`
   - TTS: `en`
   - Detection: `en`

2. **Hindi** (`hi-IN`)
   - Speech Recognition: `hi-IN`
   - TTS: `hi`
   - Detection: `hi`

3. **Kannada** (`kn-IN`)
   - Speech Recognition: `kn-IN`
   - TTS: `kn`
   - Detection: `kn`

### Language Detection Process
1. **Primary**: Try automatic language detection using Google Speech Recognition
2. **Fallback**: If auto-detection fails, try each supported language sequentially
3. **Default**: Fall back to English if no language is detected

## Usage Examples

### Example 1: English Voice Input
1. User clicks microphone button
2. User speaks: "I have a headache and fever"
3. System detects English language
4. System responds with medical advice in English text and voice

### Example 2: Hindi Voice Input
1. User clicks microphone button
2. User speaks: "मुझे सिरदर्द और बुखार है"
3. System detects Hindi language
4. System responds with medical advice in Hindi text and voice

### Example 3: Kannada Voice Input
1. User clicks microphone button
2. User speaks: "ನನಗೆ ತಲೆನೋವು ಮತ್ತು ಜ್ವರ ಇದೆ"
3. System detects Kannada language
4. System responds with medical advice in Kannada text and voice

## Installation and Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Dependencies
- `langdetect==1.0.9` - Language detection
- `SpeechRecognition==3.0.10` - Speech recognition
- `gTTS==2.3.2` - Text-to-speech
- `pyaudio==0.2.11` - Audio processing

### Running the Application
```bash
python app.py
```

## Testing

### Test Voice Functionality
```bash
python test_voice.py
```

This will test:
- Text-to-speech conversion
- Voice response generation
- Language detection

## Browser Compatibility

### Supported Browsers
- Chrome (recommended)
- Firefox
- Safari
- Edge

### Requirements
- HTTPS connection (required for microphone access)
- Microphone permissions granted
- Modern browser with Web Audio API support

## Troubleshooting

### Common Issues

1. **Microphone Not Working**
   - Check browser permissions
   - Ensure HTTPS connection
   - Try refreshing the page

2. **Language Detection Fails**
   - Speak clearly and slowly
   - Ensure good audio quality
   - Check internet connection

3. **Voice Output Not Playing**
   - Check browser audio settings
   - Ensure voice output is enabled
   - Check console for errors

### Error Messages

- `"Could not understand the audio"`: Speech recognition failed
- `"Error processing audio"`: Audio processing error
- `"Error generating speech"`: TTS generation failed

## Future Enhancements

### Planned Features
1. **More Languages**: Support for additional Indian languages
2. **Voice Commands**: Direct voice commands for navigation
3. **Voice Profiles**: Personalized voice settings
4. **Offline Support**: Local speech recognition
5. **Voice Biometrics**: Voice-based user identification

### Performance Optimizations
1. **Caching**: Cache common TTS responses
2. **Streaming**: Real-time voice streaming
3. **Compression**: Audio compression for faster transmission
4. **Parallel Processing**: Concurrent voice processing

## Security Considerations

1. **Audio Privacy**: Audio data is processed temporarily and not stored
2. **HTTPS Required**: Microphone access requires secure connection
3. **Permission Management**: Users must explicitly grant microphone permissions
4. **Data Encryption**: All audio data is encrypted in transit

## Support

For technical support or feature requests, please refer to the main project documentation or create an issue in the project repository. 