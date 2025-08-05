#!/bin/bash
echo "Starting Enhanced AI Healthcare Chatbot..."
echo ""

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source healthcare_env/bin/activate

echo "The application will start on http://localhost:5001"
echo ""
read -p "Press Enter to continue..."
python app.py
