#!/usr/bin/env python3
"""
Test script for voice functionality
"""

import requests
import json

def test_voice_functionality():
    """Test the voice functionality endpoints"""
    
    base_url = "http://localhost:5001"
    
    print("Testing Voice Functionality...")
    print("=" * 50)
    
    # Test 1: Text-to-speech
    print("\n1. Testing Text-to-Speech...")
    try:
        response = requests.post(f"{base_url}/text-to-speech", 
                               json={"text": "Hello, this is a test message", "language": "english"})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Text-to-speech working")
            else:
                print("✗ Text-to-speech failed:", data.get('error'))
        else:
            print("✗ Text-to-speech request failed")
    except Exception as e:
        print("✗ Text-to-speech error:", str(e))
    
    # Test 2: Voice response
    print("\n2. Testing Voice Response...")
    try:
        response = requests.post(f"{base_url}/voice-response", 
                               json={"text": "Hello, this is a test response", "detected_language": "english"})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Voice response working")
            else:
                print("✗ Voice response failed:", data.get('error'))
        else:
            print("✗ Voice response request failed")
    except Exception as e:
        print("✗ Voice response error:", str(e))
    
    # Test 3: Language detection
    print("\n3. Testing Language Detection...")
    try:
        response = requests.post(f"{base_url}/chat", 
                               json={"message": "नमस्ते, मैं बीमार हूं", "language": "hindi"})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Language detection working")
            else:
                print("✗ Language detection failed:", data.get('error'))
        else:
            print("✗ Language detection request failed")
    except Exception as e:
        print("✗ Language detection error:", str(e))
    
    print("\n" + "=" * 50)
    print("Voice functionality test completed!")

if __name__ == "__main__":
    test_voice_functionality() 