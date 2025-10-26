"""
Test script for screenshot-triggered overlay updates.

This script simulates screenshot events and tests the learning agent
integration with overlay messaging.

Usage:
    python backend/tests/test_screenshot_trigger.py
"""

import requests
import base64
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"


def create_mock_screenshot(width=1920, height=1080):
    """Create a mock screenshot image"""
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (width, height), color='gray')
    
    # Add some text to the image
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, width-100, height-100], fill='white', outline='black', width=5)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    base64_img = base64.b64encode(img_bytes).decode('utf-8')
    
    return base64_img


def test_screenshot_endpoint():
    """Test 1: Send screenshot to /screenshot endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Screenshot Endpoint")
    print("="*60)
    
    try:
        print("📸 Creating mock screenshot...")
        base64_img = create_mock_screenshot()
        print(f"   Image size: {len(base64_img)} bytes (base64)")
        
        print("\n📤 Sending screenshot to backend...")
        
        payload = {
            "image": base64_img,
            "metadata": {
                "width": 1920,
                "height": 1080,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/screenshot",
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response: {result.get('message', 'No message')}")
            print("✅ PASS: Screenshot processed successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except ImportError as e:
        print(f"❌ ERROR: Missing dependency - {e}")
        print("   Install PIL: pip install Pillow")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_screenshot_with_analysis():
    """Test 2: Screenshot with learning agent analysis"""
    print("\n" + "="*60)
    print("TEST 2: Screenshot with Analysis")
    print("="*60)
    
    try:
        print("📸 Creating mock screenshot with code editor...")
        
        # Create a more complex mock image (code editor)
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        img = Image.new('RGB', (1920, 1080), color='#1e1e1e')
        draw = ImageDraw.Draw(img)
        
        # Draw a code editor interface
        draw.rectangle([200, 100, 1720, 980], fill='#252526', outline='#3c3c3c', width=2)
        draw.text((220, 130), "function hello() {", fill='#ce9178', font=None)
        draw.text((220, 180), "    console.log('Hello World');", fill='#9cdcfe', font=None)
        draw.text((220, 230), "}", fill='#ce9178', font=None)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        base64_img = base64.b64encode(img_bytes).decode('utf-8')
        
        print(f"   Image size: {len(base64_img)} bytes (base64)")
        print("\n📤 Sending screenshot for analysis...")
        
        payload = {
            "image": base64_img,
            "metadata": {
                "width": 1920,
                "height": 1080,
                "timestamp": datetime.now().isoformat(),
                "source": "test_screenshot_trigger.py"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/screenshot",
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Message: {result.get('message', 'No message')}")
            print("✅ PASS: Screenshot analyzed successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except ImportError:
        print("❌ ERROR: Missing PIL/Pillow dependency")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_screenshot_event():
    """Test 3: Screenshot event endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Screenshot Event Endpoint")
    print("="*60)
    
    try:
        print("📸 Creating mock screenshot...")
        base64_img = create_mock_screenshot()
        
        print("\n📤 Sending screenshot event...")
        
        payload = {
            "image": base64_img,
            "user_id": "overlay-user",
            "event_type": "screenshot_captured",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{BASE_URL}/api/screenshot-event",
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response: {json.dumps(result, indent=2)}")
            print("✅ PASS: Screenshot event processed successfully")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    import json
    print("\n🧪 Screenshot-Triggered Overlay Tests")
    print("="*60)
    print("Make sure the Flask backend is running on localhost:5000")
    print("These tests will trigger learning agent analysis")
    print("="*60)
    
    # Run tests
    test_screenshot_endpoint()
    time.sleep(3)
    
    test_screenshot_with_analysis()
    time.sleep(3)
    
    test_screenshot_event()
    
    print("\n" + "="*60)
    print("✅ All tests completed")
    print("="*60)

