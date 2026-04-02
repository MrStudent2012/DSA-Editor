import os
import subprocess
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    pass

@socketio.on('join')
def on_join(data):
    session_id = data['session_id']
    join_room(session_id)
    
    if session_id not in sessions:
        sessions[session_id] = {'code': '# Write Python code here\n'}
    
    emit('load_code', {'code': sessions[session_id]['code']})
    emit('user_count', {'count': len([s for s in sessions.get(session_id, {}) if isinstance(s, str)])}, room=session_id)

@socketio.on('code_change')
def on_code_change(data):
    session_id = data['session_id']
    code = data['code']
    
    if session_id in sessions:
        sessions[session_id]['code'] = code
        emit('code_update', {'code': code}, room=session_id, skip_sid=True)

@socketio.on('run_code')
def on_run_code(data):
    session_id = data['session_id']
    code = data['code']
    
    try:
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        emit('output', {'result': output or '(no output)'}, room=session_id)
    except subprocess.TimeoutExpired:
        emit('output', {'result': 'ERROR: Code execution timeout (5 seconds)'}, room=session_id)
    except Exception as e:
        emit('output', {'result': f'ERROR: {str(e)}'}, room=session_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
