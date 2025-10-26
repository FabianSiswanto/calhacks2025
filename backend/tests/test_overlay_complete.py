"""
Complete end-to-end test for overlay messaging within test environment.

This test runs both a WebSocket listener (simulating overlay) and sender
to demonstrate complete message flow without needing the actual app.

Usage:
    python backend/tests/test_overlay_complete.py
"""

import socketio
import requests
import time
import threading
import json
from datetime import datetime
from collections import deque

BASE_URL = "http://localhost:5000"


class OverlaySimulator:
    """Simulates the overlay component - receives and validates messages"""
    
    def __init__(self):
        self.client = socketio.Client()
        self.received_messages = deque()
        self.header_updates = []
        self.body_updates = []
        self.setup_event_handlers()
        self.connected = False
        
    def setup_event_handlers(self):
        """Setup event handlers to simulate overlay behavior"""
        
        @self.client.on('connect')
        def on_connect():
            print("   [OVERLAY] ✅ Connected to WebSocket")
            self.connected = True
            
        @self.client.on('disconnect')
        def on_disconnect():
            print("   [OVERLAY] ❌ Disconnected from WebSocket")
            self.connected = False
            
        @self.client.on('popup_message')
        def on_popup_message(data):
            """Handle popup messages like the real overlay does"""
            print(f"   [OVERLAY] 📨 Received: {json.dumps(data, indent=6)}")
            self.received_messages.append(data)
            
            # Extract header and body like OverlayScreen.js does
            header = data.get('header', '')
            body = data.get('body', data.get('message', ''))
            
            if header:
                self.header_updates.append(header)
            if body:
                self.body_updates.append(body)
            
        @self.client.on('status')
        def on_status(data):
            print(f"   [OVERLAY] 📡 Status: {data}")
            
    def start_listening(self):
        """Start listening for messages (like overlay component does)"""
        print("\n🔌 Starting overlay simulator...")
        self.client.connect(BASE_URL, transports=['polling'])
        time.sleep(1)
        
        # Join the overlay-user room (like the real overlay does)
        print("   [OVERLAY] Joining overlay-user room...")
        self.client.call('join_user_room', {'user_id': 'overlay-user'})
        time.sleep(0.5)
        
    def stop_listening(self):
        """Stop listening"""
        if self.connected:
            self.client.disconnect()
            
    def get_message_count(self):
        """Get count of received messages"""
        return len(self.received_messages)
        
    def wait_for_message(self, timeout=5):
        """Wait for a message to arrive"""
        initial_count = len(self.received_messages)
        for _ in range(timeout * 2):  # Check every 0.5 seconds
            if len(self.received_messages) > initial_count:
                return True
            time.sleep(0.5)
        return False


class TestSuite:
    """Complete test suite with overlay simulator"""
    
    def __init__(self):
        self.overlay = OverlaySimulator()
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        print(f"\n{'='*70}")
        print(f"TEST: {test_name}")
        print('='*70)
        
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                print(f"\n✅ PASS: {test_name}")
            else:
                self.failed_tests += 1
                print(f"\n❌ FAIL: {test_name}")
        except Exception as e:
            self.failed_tests += 1
            print(f"\n❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            
    def test_send_popup_endpoint(self):
        """Test sending popup via /api/send-popup"""
        # Reset message counter
        initial_count = self.overlay.get_message_count()
        
        # Send message
        response = requests.post(
            f"{BASE_URL}/api/send-popup",
            json={
                "message": "Hello from complete test!",
                "type": "test",
                "user_id": "overlay-user"
            },
            timeout=10
        )
        
        print(f"\n📤 API Response: {response.status_code}")
        print(f"   Body: {json.dumps(response.json(), indent=6)}")
        
        # Wait for message to arrive
        if self.overlay.wait_for_message(timeout=3):
            print(f"✅ Message received by overlay!")
            print(f"   Message count: {self.overlay.get_message_count()} (was {initial_count})")
            return True
        else:
            print("⚠️  Message not received by overlay")
            return False
            
    def test_start_step_default(self):
        """Test start-step with default message"""
        initial_count = self.overlay.get_message_count()
        
        print("\n📤 Sending start-step request...")
        response = requests.post(
            f"{BASE_URL}/api/start-step",
            json={
                "user_id": "overlay-user",
                "lesson_id": 1,
                "step_order": 42
            },
            timeout=10
        )
        
        print(f"📥 API Response: {response.status_code}")
        print(f"   Body: {json.dumps(response.json(), indent=6)}")
        
        # Wait for message and check if count increased
        time.sleep(1.5)
        final_count = self.overlay.get_message_count()
        
        if final_count > initial_count:
            latest = self.overlay.received_messages[-1]
            print(f"✅ Step message received!")
            print(f"   Header: {latest.get('header', 'N/A')}")
            print(f"   Body: {latest.get('body', 'N/A')}")
            
            # Verify message structure
            has_header = 'header' in latest
            has_body = 'body' in latest
            
            if has_header and has_body:
                return True
            else:
                print(f"⚠️  Message missing required fields (header: {has_header}, body: {has_body})")
                return False
        else:
            print(f"⚠️  Step message not received (total messages: {final_count}, was {initial_count})")
            if final_count > 0:
                print(f"   Latest message: {self.overlay.received_messages[-1]}")
            return False
            
    def test_start_step_custom(self):
        """Test start-step with custom header/body"""
        initial_count = self.overlay.get_message_count()
        
        response = requests.post(
            f"{BASE_URL}/api/start-step",
            json={
                "user_id": "overlay-user",
                "header": "🎯 Custom Test Step",
                "body": "This is a complete end-to-end test message!"
            },
            timeout=10
        )
        
        print(f"\n📤 API Response: {response.status_code}")
        
        if self.overlay.wait_for_message(timeout=3):
            latest = self.overlay.received_messages[-1]
            print(f"✅ Custom step message received!")
            print(f"   Header: {latest.get('header')}")
            print(f"   Body: {latest.get('body')}")
            
            # Validate custom content
            if latest.get('header') == "🎯 Custom Test Step":
                print("   ✅ Header matches expected")
                return True
            else:
                print(f"   ❌ Header mismatch: expected '🎯 Custom Test Step', got '{latest.get('header')}'")
                return False
        else:
            print("⚠️  Custom step message not received")
            return False
            
    def test_multiple_rapid_messages(self):
        """Test sending multiple messages rapidly"""
        print("\n📤 Sending 5 rapid messages...")
        
        initial_count = self.overlay.get_message_count()
        messages_sent = 0
        
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/start-step",
                json={
                    "user_id": "overlay-user",
                    "header": f"Message {i+1}",
                    "body": f"Content {i+1}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                messages_sent += 1
                print(f"   ✅ Sent message {i+1}/5")
            else:
                print(f"   ❌ Failed to send message {i+1}")
                
            time.sleep(0.5)  # Small delay between sends
            
        # Wait for all messages to arrive
        time.sleep(2)
        
        messages_received = self.overlay.get_message_count() - initial_count
        print(f"\n📊 Results:")
        print(f"   Messages sent: {messages_sent}")
        print(f"   Messages received: {messages_received}")
        
        if messages_received >= messages_sent:
            return True
        else:
            print(f"   ⚠️  Missing {messages_sent - messages_received} messages")
            return messages_received >= messages_sent * 0.8  # Accept if 80% received
            
    def test_message_format(self):
        """Test that messages have correct format (header/body)"""
        # Send a message and validate its structure
        response = requests.post(
            f"{BASE_URL}/api/start-step",
            json={
                "user_id": "overlay-user",
                "header": "Format Test",
                "body": "Testing message structure"
            },
            timeout=10
        )
        
        if self.overlay.wait_for_message(timeout=3):
            latest = self.overlay.received_messages[-1]
            
            # Validate structure
            has_header = 'header' in latest
            has_body = 'body' in latest or 'message' in latest
            
            print(f"\n📊 Message structure:")
            print(f"   Has header: {has_header}")
            print(f"   Has body: {has_body}")
            print(f"   Full structure: {json.dumps(latest, indent=6)}")
            
            return has_header and has_body
        else:
            print("⚠️  No message received for format test")
            return False


def main():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("🧪 COMPLETE OVERLAY MESSAGING TEST SUITE")
    print("="*70)
    print("\nThis test simulates the overlay component to validate")
    print("end-to-end message flow within the test environment.")
    print("\nPrerequisites:")
    print("  ✓ Backend must be running on localhost:5000")
    print("="*70)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✅ Backend is running: {response.json()}")
    except:
        print(f"\n❌ Backend is not running on {BASE_URL}")
        print("   Please start the Flask backend first!")
        return
    
    # Initialize test suite
    suite = TestSuite()
    
    # Start overlay simulator
    suite.overlay.start_listening()
    time.sleep(1)
    
    # Run all tests
    suite.run_test("Send Popup Endpoint", suite.test_send_popup_endpoint)
    time.sleep(1)
    
    suite.run_test("Start Step (Default Message)", suite.test_start_step_default)
    time.sleep(1)
    
    suite.run_test("Start Step (Custom Message)", suite.test_start_step_custom)
    time.sleep(1)
    
    suite.run_test("Multiple Rapid Messages", suite.test_multiple_rapid_messages)
    time.sleep(1)
    
    suite.run_test("Message Format Validation", suite.test_message_format)
    
    # Stop overlay simulator
    suite.overlay.stop_listening()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {suite.passed_tests}")
    print(f"❌ Failed: {suite.failed_tests}")
    print(f"📈 Success Rate: {suite.passed_tests / (suite.passed_tests + suite.failed_tests) * 100:.1f}%")
    print("="*70)
    
    if suite.failed_tests == 0:
        print("\n🎉 All tests passed! Overlay messaging is working correctly.")
    else:
        print(f"\n⚠️  {suite.failed_tests} test(s) failed. Review output above.")


if __name__ == "__main__":
    main()

