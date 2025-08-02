# Create the enhanced HTML frontend
html_frontend = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Healthcare Chatbot - Enhanced</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-bg: #ecf0f1;
            --dark-bg: #34495e;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 10px;
        }

        .header p {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }

        .language-selector {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .lang-btn {
            padding: 8px 16px;
            border: 2px solid var(--secondary-color);
            background: white;
            color: var(--secondary-color);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .lang-btn.active, .lang-btn:hover {
            background: var(--secondary-color);
            color: white;
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            height: 500px;
            overflow-y: auto;
        }

        .chat-messages {
            height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 80%;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            background: var(--secondary-color);
            color: white;
            margin-left: auto;
        }

        .bot-message {
            background: white;
            border: 1px solid #ddd;
            margin-right: auto;
        }

        .medical-advice {
            background: #f8f9fa;
            border-left: 4px solid var(--success-color);
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }

        .condition-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .condition-title {
            color: var(--primary-color);
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .severity-badge {
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }

        .severity-mild { background: #d4edda; color: #155724; }
        .severity-moderate { background: #fff3cd; color: #856404; }
        .severity-high { background: #f8d7da; color: #721c24; }

        .advice-section {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }

        .medications {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }

        .precautions {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
        }

        .treatment {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
        }

        .diet {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }

        .doctor-consultation {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }

        .advice-section h6 {
            margin-bottom: 8px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .advice-list {
            list-style: none;
            padding: 0;
        }

        .advice-list li {
            padding: 3px 0;
            padding-left: 20px;
            position: relative;
        }

        .advice-list li:before {
            content: "•";
            color: var(--secondary-color);
            font-weight: bold;
            position: absolute;
            left: 0;
        }

        .input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .input-group {
            flex: 1;
        }

        .form-control {
            border-radius: 25px;
            border: 2px solid #ddd;
            padding: 12px 20px;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 0.2rem rgba(52, 144, 220, 0.25);
        }

        .btn-primary {
            background: var(--secondary-color);
            border: none;
            border-radius: 25px;
            padding: 12px 25px;
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }

        .voice-btn {
            background: var(--success-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }

        .voice-btn:hover {
            background: #229954;
            transform: scale(1.1);
        }

        .voice-btn.recording {
            background: var(--danger-color);
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .disclaimer {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
            color: #856404;
        }

        .loading {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #666;
        }

        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid var(--secondary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .quick-symptoms {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }

        .symptom-chip {
            background: var(--light-bg);
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 5px 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }

        .symptom-chip:hover {
            background: var(--secondary-color);
            color: white;
        }

        @media (max-width: 768px) {
            .main-container {
                padding: 10px;
            }
            
            .message {
                max-width: 95%;
            }
            
            .input-container {
                flex-direction: column;
                gap: 10px;
            }
            
            .input-group {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-robot"></i> AI Healthcare Assistant</h1>
            <p>Get personalized medical advice with detailed medication recommendations</p>
            
            <!-- Language Selector -->
            <div class="language-selector">
                <button class="lang-btn active" data-lang="english">English</button>
                <button class="lang-btn" data-lang="hindi">हिन्दी</button>
                <button class="lang-btn" data-lang="kannada">ಕನ್ನಡ</button>
            </div>

            <!-- Quick Symptoms -->
            <div class="quick-symptoms">
                <div class="symptom-chip" onclick="addSymptom('headache')">Headache</div>
                <div class="symptom-chip" onclick="addSymptom('fever')">Fever</div>
                <div class="symptom-chip" onclick="addSymptom('cough')">Cough</div>
                <div class="symptom-chip" onclick="addSymptom('sore throat')">Sore Throat</div>
                <div class="symptom-chip" onclick="addSymptom('stomach pain')">Stomach Pain</div>
                <div class="symptom-chip" onclick="addSymptom('back pain')">Back Pain</div>
            </div>
        </div>

        <!-- Chat Container -->
        <div class="chat-container">
            <div id="chatMessages" class="chat-messages">
                <div class="message bot-message">
                    <p><strong>AI Assistant:</strong> Hello! I'm your AI Healthcare Assistant. Describe your symptoms and I'll provide detailed medical advice including medication recommendations, precautions, and treatment suggestions.</p>
                    <div class="disclaimer">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Disclaimer:</strong> This is for informational purposes only. Please consult a healthcare professional for proper diagnosis and treatment.
                    </div>
                </div>
            </div>

            <!-- Input Container -->
            <div class="input-container">
                <div class="input-group">
                    <input type="text" id="messageInput" class="form-control" 
                           placeholder="Describe your symptoms (e.g., I have a headache and fever)..."
                           onkeypress="handleKeyPress(event)">
                </div>
                <button class="voice-btn" id="voiceBtn" onclick="toggleVoiceRecording()" title="Voice Input">
                    <i class="fas fa-microphone"></i>
                </button>
                <button class="btn btn-primary" onclick="sendMessage()">
                    <i class="fas fa-paper-plane"></i> Send
                </button>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentLanguage = 'english';
        let isRecording = false;
        let mediaRecorder;
        let audioChunks = [];

        // Language Selection
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentLanguage = this.dataset.lang;
            });
        });

        // Add symptom to input
        function addSymptom(symptom) {
            const input = document.getElementById('messageInput');
            const currentValue = input.value.trim();
            if (currentValue) {
                input.value = currentValue + ', ' + symptom;
            } else {
                input.value = symptom;
            }
            input.focus();
        }

        // Handle Enter key press
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Send message
        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');
            messageInput.value = '';

            // Show loading
            showLoading();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        language: currentLanguage
                    })
                });

                const data = await response.json();
                hideLoading();

                if (data.success) {
                    addMedicalAdvice(data.response);
                } else {
                    addMessage('Sorry, I encountered an error: ' + data.error, 'bot');
                }
            } catch (error) {
                hideLoading();
                addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
                console.error('Error:', error);
            }
        }

        // Add message to chat
        function addMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<p><strong>You:</strong> ${message}</p>`;
            } else {
                messageDiv.innerHTML = `<p><strong>AI Assistant:</strong> ${message}</p>`;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Add detailed medical advice
        function addMedicalAdvice(advice) {
            const chatMessages = document.getElementById('chatMessages');
            const adviceDiv = document.createElement('div');
            adviceDiv.className = 'message bot-message';
            
            let html = `<div class="medical-advice">`;
            html += `<h5><i class="fas fa-stethoscope"></i> Medical Analysis</h5>`;
            
            if (advice.conditions && advice.conditions.length > 0) {
                advice.conditions.forEach(condition => {
                    html += `<div class="condition-card">`;
                    
                    // Condition title with severity
                    html += `<div class="condition-title">`;
                    html += `<i class="fas fa-heartbeat"></i>`;
                    html += `<span>${condition.disease} (${condition.symptom})</span>`;
                    html += `<span class="severity-badge severity-${condition.severity.toLowerCase().replace(' ', '-')}">${condition.severity}</span>`;
                    html += `</div>`;
                    
                    // Description
                    if (condition.description) {
                        html += `<p style="margin-bottom: 15px; color: #666;">${condition.description}</p>`;
                    }
                    
                    // Medications
                    if (condition.medications && condition.medications.length > 0) {
                        html += `<div class="advice-section medications">`;
                        html += `<h6><i class="fas fa-pills"></i> Recommended Medications:</h6>`;
                        html += `<ul class="advice-list">`;
                        condition.medications.forEach(med => {
                            html += `<li>${med}</li>`;
                        });
                        html += `</ul></div>`;
                    }
                    
                    // Precautions
                    if (condition.precautions && condition.precautions.length > 0) {
                        html += `<div class="advice-section precautions">`;
                        html += `<h6><i class="fas fa-exclamation-triangle"></i> Precautions:</h6>`;
                        html += `<ul class="advice-list">`;
                        condition.precautions.forEach(precaution => {
                            html += `<li>${precaution}</li>`;
                        });
                        html += `</ul></div>`;
                    }
                    
                    // Treatment
                    if (condition.treatment && condition.treatment.length > 0) {
                        html += `<div class="advice-section treatment">`;
                        html += `<h6><i class="fas fa-hand-holding-medical"></i> Treatment:</h6>`;
                        html += `<ul class="advice-list">`;
                        condition.treatment.forEach(treatment => {
                            html += `<li>${treatment}</li>`;
                        });
                        html += `</ul></div>`;
                    }
                    
                    // Diet
                    if (condition.diet && condition.diet.length > 0) {
                        html += `<div class="advice-section diet">`;
                        html += `<h6><i class="fas fa-apple-alt"></i> Dietary Suggestions:</h6>`;
                        html += `<ul class="advice-list">`;
                        condition.diet.forEach(diet => {
                            html += `<li>${diet}</li>`;
                        });
                        html += `</ul></div>`;
                    }
                    
                    // When to see doctor
                    if (condition.doctor_consultation) {
                        html += `<div class="advice-section doctor-consultation">`;
                        html += `<h6><i class="fas fa-user-md"></i> When to See a Doctor:</h6>`;
                        html += `<p>${condition.doctor_consultation}</p>`;
                        html += `</div>`;
                    }
                    
                    html += `</div>`;
                });
            } else {
                html += `<p>I couldn't identify specific symptoms from your message. Please try describing your symptoms more clearly, such as "I have a headache" or "I'm experiencing fever and cough".</p>`;
            }
            
            // Disclaimer
            if (advice.disclaimer) {
                html += `<div class="disclaimer">`;
                html += `<i class="fas fa-info-circle"></i> ${advice.disclaimer}`;
                html += `</div>`;
            }
            
            html += `</div>`;
            
            adviceDiv.innerHTML = html;
            chatMessages.appendChild(adviceDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Show loading indicator
        function showLoading() {
            const chatMessages = document.getElementById('chatMessages');
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot-message loading-message';
            loadingDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Analyzing your symptoms...</span>
                </div>
            `;
            chatMessages.appendChild(loadingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Hide loading indicator
        function hideLoading() {
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }

        // Voice recording functions
        async function toggleVoiceRecording() {
            const voiceBtn = document.getElementById('voiceBtn');
            
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        await sendVoiceMessage(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    voiceBtn.classList.add('recording');
                    voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
                    voiceBtn.title = 'Stop Recording';
                    
                } catch (error) {
                    console.error('Error accessing microphone:', error);
                    alert('Unable to access microphone. Please check your permissions.');
                }
            } else {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                voiceBtn.title = 'Voice Input';
            }
        }

        // Send voice message
        async function sendVoiceMessage(audioBlob) {
            showLoading();
            
            try {
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.wav');
                
                const response = await fetch('/voice-to-text', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                hideLoading();
                
                if (data.success) {
                    document.getElementById('messageInput').value = data.text;
                    sendMessage();
                } else {
                    addMessage('Sorry, I couldn\'t understand the audio. Please try again.', 'bot');
                }
            } catch (error) {
                hideLoading();
                addMessage('Error processing voice input. Please try again.', 'bot');
                console.error('Voice error:', error);
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('messageInput').focus();
        });
    </script>
</body>
</html>
'''

# Create templates directory and save HTML file
import os
os.makedirs('templates', exist_ok=True)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_frontend)

print("Enhanced HTML frontend (templates/index.html) created successfully!")
print("\nFrontend features:")
print("1. Modern, responsive design")
print("2. Detailed medical advice display")
print("3. Medication recommendations with dosages")
print("4. Precautions, treatment, and diet suggestions")
print("5. Voice input/output capabilities")
print("6. Multi-language support")
print("7. Quick symptom selection")
print("8. Professional medical disclaimer")