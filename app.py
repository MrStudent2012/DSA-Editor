import os
import subprocess
import sys
import ast
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
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
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)

sessions = {}
sid_to_session = {}


def _contains_solution_call(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == 'solution':
            return True
    return False


def _prepare_code_for_execution(code):
    if not isinstance(code, str):
        return code

    try:
        parsed = ast.parse(code)
    except SyntaxError:
        return code

    has_solution_function = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'solution'
        for node in parsed.body
    )

    if not has_solution_function:
        return code

    has_top_level_solution_call = any(
        not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and _contains_solution_call(node)
        for node in parsed.body
    )

    if has_top_level_solution_call:
        return code

    return (
        f"{code}\n\n"
        "if __name__ == '__main__':\n"
        "    _result = solution()\n"
        "    if _result is not None:\n"
        "        print(_result)\n"
    )

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print(f'[CONNECT] Client connected')

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    session_id = sid_to_session.pop(sid, None)

    if not session_id:
        print(f'[DISCONNECT] Client disconnected: {sid}')
        return

    room_data = sessions.get(session_id)
    if not room_data:
        print(f'[DISCONNECT] Client disconnected: {sid} (session already removed)')
        return

    room_data['users'].discard(sid)
    user_count = len(room_data['users'])
    socketio.emit('user_count', {'count': user_count}, room=session_id)

    if user_count == 0:
        sessions.pop(session_id, None)
        print(f'[SESSION] Removed empty session: {session_id}')

    print(f'[DISCONNECT] Client disconnected from {session_id}. Users left: {user_count}')

@socketio.on('join')
def on_join(data):
    session_id = (data.get('session_id') or '').strip()
    if not session_id:
        emit('output', {'result': 'ERROR: Invalid session ID'})
        return

    sid = request.sid
    print(f'[JOIN] User joining session: {session_id}')

    old_session_id = sid_to_session.get(sid)
    if old_session_id and old_session_id != session_id:
        leave_room(old_session_id)
        old_room_data = sessions.get(old_session_id)
        if old_room_data:
            old_room_data['users'].discard(sid)
            old_count = len(old_room_data['users'])
            socketio.emit('user_count', {'count': old_count}, room=old_session_id)
            if old_count == 0:
                sessions.pop(old_session_id, None)
                print(f'[SESSION] Removed empty session: {old_session_id}')
    
    join_room(session_id)
    
    # Initialize session if not exists
    if session_id not in sessions:
        sessions[session_id] = {
            'code': '# Write Python code here\n\ndef solution():\n    pass\n',
            'users': set()
        }
        print(f'[SESSION] New session created: {session_id}')
    
    # Add user to session
    sessions[session_id]['users'].add(sid)
    sid_to_session[sid] = session_id
    
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
    session_id = (data.get('session_id') or '').strip()
    code = data.get('code')
    
    if session_id in sessions:
        sessions[session_id]['code'] = code
        emit('code_update', {'code': code}, room=session_id, skip_sid=True)
        print(f'[CODE_CHANGE] Code updated in {session_id}')

@socketio.on('run_code')
def on_run_code(data):
    session_id = (data.get('session_id') or '').strip()
    code = data.get('code')
    code_to_run = _prepare_code_for_execution(code)
    
    print(f'[RUN] Executing code in session: {session_id}')
    
    try:
        result = subprocess.run(
            [sys.executable, '-c', code_to_run],
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
