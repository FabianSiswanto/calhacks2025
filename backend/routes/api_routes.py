from flask import Blueprint, jsonify, request, current_app
from flask_socketio import emit
import json
import os

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/start-step', methods=['POST'])
def start_step():
    """Start a new step and send popup message to overlay"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default-user')
        lesson_id = data.get('lesson_id')
        step_order = data.get('step_order')
        
        # Use custom header/body if provided, otherwise use defaults
        custom_header = data.get('header')
        custom_body = data.get('body')
        
        if custom_header and custom_body:
            step_data = {
                "header": custom_header,
                "body": custom_body,
            }
        else:
            # Default message
            step_data = {
                "header": f"Step {step_order or 1}",
                "body": "Follow the instructions displayed in the overlay to complete this step.",
            }
        
        # Get the active SocketIO instance from current_app
        socketio = current_app.extensions.get('socketio')
        print(f"📤 Sending WebSocket message to room '{user_id}': {step_data}")
        
        # Emit using Flask-SocketIO's emit method
        try:
            # Use namespace parameter to target specific rooms
            if socketio is None:
                raise RuntimeError('SocketIO not initialized on current_app')
            socketio.emit('popup_message', step_data, room=user_id, namespace='/')
            print(f"✅ WebSocket message sent successfully to room '{user_id}'")
            print(f"   Message data: {step_data}")
        except Exception as e:
            print(f"❌ Error emitting message: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            "status": "success",
            "message": "Step started successfully",
            "step_data": step_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "status": "success",
        "endpoint": "/api/test"
    })

@bp.route('/data', methods=['GET'])
def get_data():
    """Get sample data"""
    return jsonify({
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300}
        ],
        "total": 3
    })

@bp.route('/data', methods=['POST'])
def create_data():
    """Create new data item"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    # In a real app, you'd save to database
    new_item = {
        "id": 4,  # In real app, generate unique ID
        "name": data['name'],
        "value": data.get('value', 0)
    }
    
    return jsonify({
        "message": "Item created successfully",
        "item": new_item
    }), 201

@bp.route('/files', methods=['GET'])
def list_files():
    """List files in the project directory"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        files = []
        
        for item in os.listdir(project_root):
            item_path = os.path.join(project_root, item)
            if os.path.isfile(item_path):
                files.append({
                    "name": item,
                    "type": "file",
                    "size": os.path.getsize(item_path)
                })
            elif os.path.isdir(item_path):
                files.append({
                    "name": item,
                    "type": "directory"
                })
        
        return jsonify({
            "files": files,
            "path": project_root
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
