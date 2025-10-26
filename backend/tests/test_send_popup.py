"""
Test script for sending popup messages to overlay via API endpoints.

This script tests all the different ways to send messages to the overlay component.

Usage:
    python backend/tests/test_send_popup.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"


def test_send_popup_api():
    """Test 1: Send popup via /api/send-popup endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Send Popup via /api/send-popup")
    print("="*60)
    
    try:
        payload = {
            "message": "Hello from test!",
            "type": "test",
            "user_id": "overlay-user",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 Sending popup with payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/send-popup",
            json=payload,
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ PASS: Popup sent successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_start_step_default():
    """Test 2: Send popup via /api/start-step with default message"""
    print("\n" + "="*60)
    print("TEST 2: Start Step with Default Message")
    print("="*60)
    
    try:
        payload = {
            "user_id": "overlay-user",
            "lesson_id": 1,
            "step_order": 5
        }
        
        print(f"📤 Starting step with payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/start-step",
            json=payload,
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ PASS: Step started successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_start_step_custom():
    """Test 3: Send popup via /api/start-step with custom message"""
    print("\n" + "="*60)
    print("TEST 3: Start Step with Custom Message")
    print("="*60)
    
    try:
        payload = {
            "user_id": "overlay-user",
            "lesson_id": 1,
            "step_order": 10,
            "header": "🎯 Custom Step",
            "body": "This is a custom message with instructions to complete the task!"
        }
        
        print(f"📤 Starting step with custom message:")
        print(f"   Header: {payload['header']}")
        print(f"   Body: {payload['body']}")
        
        response = requests.post(
            f"{BASE_URL}/api/start-step",
            json=payload,
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ PASS: Custom step started successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_multiple_messages():
    """Test 4: Send multiple messages rapidly"""
    print("\n" + "="*60)
    print("TEST 4: Send Multiple Messages")
    print("="*60)
    
    try:
        messages = [
            "Step 1: Open your editor",
            "Step 2: Write some code",
            "Step 3: Run the tests",
            "Step 4: Celebrate! 🎉"
        ]
        
        for i, msg in enumerate(messages, 1):
            print(f"\n📤 Sending message {i}/{len(messages)}: {msg}")
            
            payload = {
                "header": f"Step {i}",
                "body": msg,
                "user_id": "overlay-user"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/start-step",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ Sent successfully")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
            
            # Small delay between messages
            time.sleep(2)
        
        print(f"\n✅ PASS: Sent {len(messages)} messages")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    print("\n🧪 Popup Message Sending Tests")
    print("="*60)
    print("Make sure the Flask backend is running on localhost:5000")
    print("Open the overlay window to see messages appear")
    print("="*60)
    
    # Run tests
    test_send_popup_api()
    time.sleep(2)
    
    test_start_step_default()
    time.sleep(2)
    
    test_start_step_custom()
    time.sleep(2)
    
    test_multiple_messages()
    
    print("\n" + "="*60)
    print("✅ All tests completed")
    print("="*60)

