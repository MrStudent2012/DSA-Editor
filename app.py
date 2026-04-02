import os
import subprocess
import sys
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

# Enable CORS
CORS(app)

# Configure SocketIO with proper settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=10,
    ping_interval=5,
    logger=False,
    engineio_logger=False
)

sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print(f'[CONNECT] Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print(f'[DISCONNECT] Client disconnected')

@socketio.on('join')
def on_join(data):
    session_id = data.get('session_id', 'unknown')
    print(f'[JOIN] User joining session: {session_id}')
    
    join_room(session_id)
    
    # Initialize session if not exists
    if session_id not in sessions:
        sessions[session_id] = {
            'code': '# Write Python code here\n\ndef solution():\n    pass\n',
            'users': set()
        }
        print(f'[SESSION] New session created: {session_id}')
    
    # Add user to session
    from flask import request
    sessions[session_id]['users'].add(request.sid)
    
    # Send code to the joining user
    code = sessions[session_id]['code']
    emit('load_code', {'code': code})
    print(f'[CODE_SENT] Sent code to user in session: {session_id}')
    
    # Notify all users in room
    user_count = len(sessions[session_id]['users'])
    socketio.emit('user_count', {'count': user_count}, room=session_id)
    print(f'[USER_COUNT] Users in {session_id}: {user_count}')

@socketio.on('code_change')
def on_code_change(data):
    session_id = data.get('session_id')
    code = data.get('code')
    
    if session_id in sessions:
        sessions[session_id]['code'] = code
        emit('code_update', {'code': code}, room=session_id, skip_sid=True)
        print(f'[CODE_CHANGE] Code updated in {session_id}')

@socketio.on('run_code')
def on_run_code(data):
    session_id = data.get('session_id')
    code = data.get('code')
    
    print(f'[RUN] Executing code in session: {session_id}')
    
    try:
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        if not output:
            output = '(no output)' if result.returncode == 0 else '(error with no message)'
        
        print(f'[OUTPUT] Execution successful in {session_id}')
        emit('output', {'result': output}, room=session_id)
    except subprocess.TimeoutExpired:
        print(f'[TIMEOUT] Code execution timeout in {session_id}')
        emit('output', {'result': 'ERROR: Code execution timeout (5 seconds)'}, room=session_id)
    except Exception as e:
        print(f'[ERROR] {str(e)} in {session_id}')
        emit('output', {'result': f'ERROR: {str(e)}'}, room=session_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'\n🚀 Server starting on port {port}...\n')
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
