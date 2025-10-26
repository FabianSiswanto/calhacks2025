"""
Integration test script for overlay updating functionality.

This script tests the complete flow from triggering events to receiving
updates in the overlay component.

Usage:
    python backend/tests/test_overlay_integration.py
"""

import socketio
import requests
import time
import json
from datetime import datetime
import base64
from io import BytesIO

BASE_URL = "http://localhost:5000"


class OverlayIntegrationTest:
    """Complete integration test for overlay messaging"""
    
    def __init__(self):
        self.client = socketio.Client()
        self.received_messages = []
        self.setup_socketio_handlers()
        
    def setup_socketio_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.client.on('connect')
        def on_connect():
            print("✅ WebSocket connected")
            
        @self.client.on('disconnect')
        def on_disconnect():
            print("❌ WebSocket disconnected")
            
        @self.client.on('popup_message')
        def on_popup_message(data):
            print(f"📨 Overlay received: {json.dumps(data, indent=2)}")
            self.received_messages.append(data)
            
        @self.client.on('status')
        def on_status(data):
            print(f"📡 Status: {data}")
            
    def start_listening(self):
        """Connect and start listening for messages"""
        print("\n🔌 Connecting to WebSocket...")
        self.client.connect(BASE_URL, transports=['polling'])
        time.sleep(1)
        
        # Join the overlay-user room
        print("🏠 Joining overlay-user room...")
        self.client.call('join_user_room', {'user_id': 'overlay-user'})
        time.sleep(0.5)
        
    def send_message(self, endpoint, payload, description):
        """Send a message via API and track if overlay receives it"""
        print(f"\n📤 {description}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Payload: {json.dumps(payload, indent=6)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                timeout=10
            )
            
            print(f"📥 API Response: {response.status_code}")
            print(f"   Body: {json.dumps(response.json(), indent=6)}")
            
            # Wait a moment for WebSocket message to arrive
            initial_count = len(self.received_messages)
            time.sleep(2)
            
            if len(self.received_messages) > initial_count:
                print("✅ PASS: Overlay received the message")
            else:
                print("⚠️  Message sent but not received yet")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
    def stop_listening(self):
        """Disconnect from WebSocket"""
        if self.client.connected:
            self.client.disconnect()
            print("\n🔌 Disconnected from WebSocket")


def test_basic_integration():
    """Test basic overlay message flow"""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Basic Overlay Message Flow")
    print("="*70)
    
    test = OverlayIntegrationTest()
    
    try:
        # Start listening
        test.start_listening()
        time.sleep(1)
        
        # Test 1: Send popup via send-popup endpoint
        test.send_message(
            "/api/send-popup",
            {
                "message": "Hello from integration test!",
                "type": "test",
                "user_id": "overlay-user"
            },
            "Sending popup via send-popup endpoint"
        )
        
        time.sleep(2)
        
        # Test 2: Start a step with custom message
        test.send_message(
            "/api/start-step",
            {
                "user_id": "overlay-user",
                "lesson_id": 1,
                "step_order": 1,
                "header": "🎯 Test Step",
                "body": "Complete the following task in your code editor"
            },
            "Starting a step with custom message"
        )
        
        time.sleep(2)
        
        # Test 3: Send multiple rapid messages
        print("\n📤 Sending rapid messages to test queue handling...")
        for i in range(3):
            test.send_message(
                "/api/start-step",
                {
                    "user_id": "overlay-user",
                    "header": f"Message {i+1}",
                    "body": f"Content of message {i+1}"
                },
                f"Rapid message {i+1}"
            )
            time.sleep(1)
        
        print(f"\n📊 Summary:")
        print(f"   Total messages sent: 5")
        print(f"   Messages received by overlay: {len(test.received_messages)}")
        
        if len(test.received_messages) > 0:
            print("✅ PASS: Integration test successful")
        else:
            print("❌ FAIL: No messages received by overlay")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        test.stop_listening()


def test_screenshot_integration():
    """Test screenshot-triggered overlay updates"""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Screenshot-Triggered Updates")
    print("="*70)
    
    test = OverlayIntegrationTest()
    
    try:
        # Start listening
        test.start_listening()
        time.sleep(1)
        
        # Create a mock screenshot
        print("\n📸 Creating mock screenshot...")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1920, 1080), color='#2d2d30')
            draw = ImageDraw.Draw(img)
            draw.rectangle([100, 100, 1820, 980], fill='#1e1e1e', outline='#3c3c3c', width=2)
            draw.text((200, 200), "Code Editor", fill='white')
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_img = base64.b64encode(img_bytes).decode('utf-8')
            
            print(f"   Created image: {len(base64_img)} bytes (base64)")
            
            # Send screenshot for processing
            test.send_message(
                "/screenshot",
                {
                    "image": base64_img,
                    "metadata": {
                        "width": 1920,
                        "height": 1080,
                        "timestamp": datetime.now().isoformat(),
                        "test": True
                    }
                },
                "Sending screenshot for processing"
            )
            
            # Wait for analysis and popup
            time.sleep(5)
            
            print("\n📊 Screenshot processing test:")
            print(f"   Messages received: {len(test.received_messages)}")
            
        except ImportError:
            print("⚠️  PIL/Pillow not installed, skipping screenshot test")
            print("   Install with: pip install Pillow")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        test.stop_listening()


def test_error_handling():
    """Test error handling in overlay messaging"""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Error Handling")
    print("="*70)
    
    test = OverlayIntegrationTest()
    
    try:
        # Start listening
        test.start_listening()
        time.sleep(1)
        
        print("\n📤 Testing error handling...")
        
        # Test 1: Missing message field
        try:
            response = requests.post(
                f"{BASE_URL}/api/send-popup",
                json={"user_id": "overlay-user"},
                timeout=10
            )
            print(f"   Test 1 (missing message): {response.status_code} - {'PASS' if response.status_code == 400 else 'FAIL'}")
        except Exception as e:
            print(f"   Test 1 ERROR: {e}")
        
        time.sleep(1)
        
        # Test 2: Invalid endpoint
        try:
            response = requests.post(
                f"{BASE_URL}/api/invalid-endpoint",
                json={},
                timeout=10
            )
            print(f"   Test 2 (invalid endpoint): {response.status_code} - {'PASS' if response.status_code == 404 else 'FAIL'}")
        except Exception as e:
            print(f"   Test 2 ERROR: {e}")
        
        print("\n✅ Error handling tests completed")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        test.stop_listening()


if __name__ == "__main__":
    print("\n🧪 Overlay Integration Tests")
    print("="*70)
    print("Make sure:")
    print("  1. Flask backend is running on localhost:5000")
    print("  2. Overlay window is open and connected")
    print("="*70)
    
    # Run all integration tests
    test_basic_integration()
    time.sleep(2)
    
    test_screenshot_integration()
    time.sleep(2)
    
    test_error_handling()
    
    print("\n" + "="*70)
    print("✅ All integration tests completed")
    print("="*70)

