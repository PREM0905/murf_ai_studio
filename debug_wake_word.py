#!/usr/bin/env python3

import requests
import json
import sys
import os

def test_server_connection():
    """Test if server is running and responding"""
    try:
        response = requests.get("http://127.0.0.1:5000/test", timeout=5)
        print(f"Server status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running on port 5000")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_text_endpoint():
    """Test text endpoint"""
    try:
        response = requests.post("http://127.0.0.1:5000/text", 
                               json={"message": "hello", "tts_enabled": False}, 
                               timeout=10)
        data = response.json()
        print(f"Text test: {data.get('reply', 'No reply')}")
        return True
    except Exception as e:
        print(f"Text endpoint error: {e}")
        return False

def test_wake_word_logic():
    """Test wake word processing logic"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    try:
        from assistants.simple_assistant import generate_reply
        
        tests = [
            "studio hello",
            "hey studio what time is it", 
            "studio weather in mumbai"
        ]
        
        for test in tests:
            result = generate_reply(test)
            print(f"'{test}' -> '{result}'")
        return True
    except Exception as e:
        print(f"Wake word logic error: {e}")
        return False

if __name__ == "__main__":
    print("=== WAKE WORD DEBUG ===")
    print("1. Testing server connection...")
    server_ok = test_server_connection()
    
    print("\n2. Testing text endpoint...")
    text_ok = test_text_endpoint()
    
    print("\n3. Testing wake word logic...")
    logic_ok = test_wake_word_logic()
    
    print(f"\nResults: Server={server_ok}, Text={text_ok}, Logic={logic_ok}")
    
    if not server_ok:
        print("\nFIX: Start server with: python backend/core/app.py")
    elif not text_ok:
        print("\nFIX: Check server logs for errors")
    elif not logic_ok:
        print("\nFIX: Check assistant logic implementation")
    else:
        print("\nBackend is working. Issue might be in frontend or browser permissions.")