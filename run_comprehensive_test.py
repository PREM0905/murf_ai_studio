#!/usr/bin/env python3

import sys
import os
import requests
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        from assistants.simple_assistant import generate_reply
        from integrations.audio.asr_api import transcribe_file_assemblyai
        from integrations.audio.murf_api import synthesize_text_murf
        from integrations.audio.wake_word_detection import detect_wake_word
        from integrations.music.simple_music import get_instant_music_url
        from integrations.search.gemini_search import search_with_gemini, is_search_query
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_assistant_logic():
    """Test core assistant functionality"""
    print("\nTesting assistant logic...")
    
    from assistants.simple_assistant import generate_reply
    
    tests = [
        ("hello", "Hello!"),
        ("what time is it", "Current time:"),
        ("weather in mumbai", "Weather"),
        ("navigate to airport", "Navigating"),
        ("play despacito", "Playing"),
        ("studio hello", "Hello!"),  # Wake word test
        ("hey studio what time is it", "Current time:"),  # Wake word test
    ]
    
    passed = 0
    for query, expected in tests:
        try:
            result = generate_reply(query)
            if isinstance(result, dict):
                result_text = result.get("message", str(result))
            else:
                result_text = str(result)
            
            if expected.lower() in result_text.lower():
                print(f"[OK] '{query}' -> OK")
                passed += 1
            else:
                print(f"[FAIL] '{query}' -> Expected '{expected}', got '{result_text[:50]}...'")
        except Exception as e:
            print(f"[ERROR] '{query}' -> Error: {e}")
    
    print(f"Assistant tests: {passed}/{len(tests)} passed")
    return passed == len(tests)

def test_server_endpoints():
    """Test if server endpoints are accessible"""
    print("\nTesting server endpoints...")
    
    base_url = "http://127.0.0.1:5000"
    
    # Test /test endpoint
    try:
        response = requests.post(f"{base_url}/test", 
                               json={"query": "hello"}, 
                               timeout=5)
        if response.status_code == 200:
            print("[OK] /test endpoint working")
            return True
        else:
            print(f"[FAIL] /test endpoint returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Server not running on port 5000")
        return False
    except Exception as e:
        print(f"[ERROR] Server test error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check for .env file
    env_path = os.path.join(os.path.dirname(__file__), "backend", "config", ".env")
    if os.path.exists(env_path):
        print("[OK] .env file found")
    else:
        print("[FAIL] .env file missing")
        return False
    
    # Check API keys
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    keys = ["ASSEMBLYAI_API_KEY", "MURF_API_KEY", "OPENAI_API_KEY", "NEWS_API_KEY"]
    missing_keys = []
    
    for key in keys:
        if os.getenv(key):
            print(f"[OK] {key} configured")
        else:
            print(f"[FAIL] {key} missing")
            missing_keys.append(key)
    
    return len(missing_keys) == 0

def test_file_structure():
    """Test critical files exist"""
    print("\nTesting file structure...")
    
    critical_files = [
        "backend/core/app.py",
        "backend/assistants/simple_assistant.py",
        "backend/integrations/audio/asr_api.py",
        "backend/integrations/audio/murf_api.py",
        "backend/integrations/audio/wake_word_detection.py",
        "frontend/index.html",
        "frontend/dual_script.js",
        "frontend/dual_style.css"
    ]
    
    missing = []
    for file_path in critical_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} missing")
            missing.append(file_path)
    
    return len(missing) == 0

def test_wake_word_processing():
    """Test wake word command processing"""
    print("\nTesting wake word processing...")
    
    from assistants.simple_assistant import generate_reply
    
    wake_tests = [
        ("studio", "Yes? How can I help you?"),
        ("hey studio", "Yes? How can I help you?"),
        ("studio hello", "Hello!"),
        ("hey studio what time is it", "Current time:"),
        ("hello studio navigate to airport", "Navigating"),
    ]
    
    passed = 0
    for query, expected in wake_tests:
        try:
            result = generate_reply(query)
            if isinstance(result, dict):
                result_text = result.get("message", str(result))
            else:
                result_text = str(result)
            
            if expected.lower() in result_text.lower():
                print(f"[OK] Wake word: '{query}' -> OK")
                passed += 1
            else:
                print(f"[FAIL] Wake word: '{query}' -> Expected '{expected}', got '{result_text[:50]}...'")
        except Exception as e:
            print(f"[ERROR] Wake word: '{query}' -> Error: {e}")
    
    print(f"Wake word tests: {passed}/{len(wake_tests)} passed")
    return passed >= len(wake_tests) - 1  # Allow 1 failure

def main():
    """Run all tests"""
    print("=" * 60)
    print("STUDIO COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Environment Setup", test_environment),
        ("Module Imports", test_imports),
        ("Assistant Logic", test_assistant_logic),
        ("Wake Word Processing", test_wake_word_processing),
        ("Server Endpoints", test_server_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nALL TESTS PASSED! STUDIO is ready for testing.")
        print("\nTo start STUDIO:")
        print("1. Run: python backend/core/app.py")
        print("2. Open: frontend/index.html in browser")
        print("3. Test wake word: Click 'Start Listening' and say 'Studio, hello'")
    else:
        print(f"\n{len(results) - passed} tests failed. Check issues above.")
        
        if not results[4][1]:  # Server test failed
            print("\nNOTE: Server test failure is expected if server isn't running.")
            print("Start the server first: python backend/core/app.py")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)