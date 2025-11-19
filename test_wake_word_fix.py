#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from assistants.simple_assistant import generate_reply

def test_wake_word_commands():
    """Test wake word command processing"""
    
    test_cases = [
        # Wake word only
        ("studio", "Yes? How can I help you?"),
        ("hey studio", "Yes? How can I help you?"),
        
        # Wake word + commands
        ("studio weather in mumbai", "Weather:"),
        ("hey studio what time is it", "Current time:"),
        ("studio play despacito", "Playing"),
        ("hello studio navigate to airport", "Navigating to"),
        ("studio news about technology", "Latest:"),
        
        # Commands without wake word (should work normally)
        ("weather in delhi", "Weather:"),
        ("what time is it", "Current time:"),
        ("play bohemian rhapsody", "Playing"),
    ]
    
    print("Testing Wake Word Command Processing")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected_contains) in enumerate(test_cases, 1):
        try:
            result = generate_reply(input_text)
            
            # Handle dict responses (navigation, music, etc.)
            if isinstance(result, dict):
                result_text = result.get("message", str(result))
            else:
                result_text = str(result)
            
            # Check if expected text is in result
            if expected_contains.lower() in result_text.lower():
                print(f"[PASS] Test {i}: PASS")
                print(f"   Input: '{input_text}'")
                print(f"   Output: '{result_text[:100]}...'")
                passed += 1
            else:
                print(f"[FAIL] Test {i}: FAIL")
                print(f"   Input: '{input_text}'")
                print(f"   Expected: Contains '{expected_contains}'")
                print(f"   Got: '{result_text}'")
                failed += 1
                
        except Exception as e:
            print(f"[ERROR] Test {i}: ERROR - {str(e)}")
            print(f"   Input: '{input_text}'")
            failed += 1
        
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! Wake word processing is working correctly.")
    else:
        print("Some tests failed. Check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = test_wake_word_commands()
    sys.exit(0 if success else 1)