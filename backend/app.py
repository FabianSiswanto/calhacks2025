import os
import sys
import base64
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from utils.learning_agent import analyze_screenshot, handle_screenshot_event, handle_screenshot_event_with_defaults

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Allow React to make requests

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes
from routes import api_routes
from routes.lesson_plans import lesson_plans_bp
from routes.media_routes import media_bp
from routes.test_db import test_db_bp

# Register blueprints
app.register_blueprint(api_routes.bp)
app.register_blueprint(test_db_bp, url_prefix="/api")
app.register_blueprint(lesson_plans_bp, url_prefix='/api')
app.register_blueprint(media_bp, url_prefix='/api')

@app.route('/screenshot', methods=['POST'])
def screenshot():
    try:
        # Get the request data
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({
                "message": "No image data provided",
                "status": "error"
            }), 400

        # Extract the base64 image data from the request
        base64_image = data['image']

        # Optional: Log metadata if provided
        if 'metadata' in data:
            print(f"Screenshot metadata: {data['metadata']}")

    except Exception as e:
        return jsonify({
            "message": f"Error processing request: {str(e)}",
            "status": "error"
        }), 400

    result = analyze_screenshot(base64_image, "")

    return jsonify({
        "message": "Screenshot analyzed successfully",
        "status": "success",
        "analysis": result
    })

@app.route('/')
def index():
    return jsonify({
        "message": "Flask backend is running!",
        "status": "success",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "calhacks2025-backend"
    })

@app.route('/api/screenshot-event', methods=['POST'])
def screenshot_event():
    """
    Process a screenshot and return completion boolean.
    
    If only { image } is provided, uses analyze_screenshot with empty finish criteria
    and returns { completed: true|false }.
    If { user_id, lesson_id, step_order, image } are provided, uses the event flow
    handle_screenshot_event and passes its simplified result through.
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image"}), 400

        base64_image = data['image']

        # Event-flow inputs present
        if all(k in data for k in ['user_id', 'lesson_id', 'step_order']):
            user_id = data['user_id']
            lesson_id = int(data['lesson_id'])
            step_order = int(data['step_order'])
            result = handle_screenshot_event(user_id, lesson_id, step_order, base64_image)
            return jsonify(result)

        # Fallback: use server defaults (single-user, default lesson/step)
        result = handle_screenshot_event_with_defaults(
            base64_image=base64_image,
            user_id=data.get('user_id'),
            lesson_id=int(data['lesson_id']) if data.get('lesson_id') is not None else None,
            step_order=int(data['step_order']) if data.get('step_order') is not None else None,
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

# WebSocket API endpoint for sending popup messages
@app.route('/api/send-popup', methods=['POST'])
def send_popup():
    """
    API endpoint to send popup messages via WebSocket to connected clients.
    
    Expected JSON payload:
    {
        "message": "Popup message text",
        "type": "popup",
        "user_id": "optional_user_id",
        "timestamp": "optional_timestamp"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "message": "No message provided",
                "status": "error"
            }), 400
        
        # Extract popup data
        popup_message = data['message']
        popup_type = data.get('type', 'popup')
        user_id = data.get('user_id')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Prepare the popup data to send
        popup_data = {
            "message": popup_message,
            "type": popup_type,
            "timestamp": timestamp,
            "user_id": user_id
        }
        
        # Send popup to all connected clients or specific user
        if user_id:
            # Send to specific user (if user rooms are implemented)
            socketio.emit('popup_message', popup_data, room=user_id)
            print(f"Popup sent to user {user_id}: {popup_message[:50]}...")
        else:
            # Send to all connected clients
            socketio.emit('popup_message', popup_data)
            print(f"Popup broadcasted to all clients: {popup_message[:50]}...")
        
        return jsonify({
            "message": "Popup sent successfully",
            "status": "success",
            "popup_data": popup_data
        })
        
    except Exception as e:
        return jsonify({
            "message": f"Error sending popup: {str(e)}",
            "status": "error"
        }), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to popup service'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Handle user joining their specific room for targeted messaging"""
    user_id = data.get('user_id')
    print(f"🔵 Backend received 'join_user_room' event for user: {user_id}")
    if user_id:
        join_room(user_id)
        print(f"✅ User {user_id} joined room successfully")
        emit('status', {'message': f'Joined room for user {user_id}'})
        return {'status': 'joined', 'room': user_id}
    else:
        print(f"⚠️ No user_id provided in join_user_room event")
        return {'status': 'error', 'message': 'No user_id provided'}

if __name__ == '__main__':
    print("Starting Flask backend with WebSocket support...")
    print("Backend will be available at: http://localhost:5001")
    print("WebSocket endpoint: ws://localhost:5001/socket.io/")
    # DEV ONLY: allow Werkzeug with Flask-SocketIO so the server starts
    socketio.run(app, debug=True, port=5001, host='127.0.0.1', allow_unsafe_werkzeug=True)
