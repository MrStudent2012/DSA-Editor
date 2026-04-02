let editor;
let socket;
let currentSessionId = null;
let isUpdating = false;
let editorReady = false;
let socketReady = false;

// Simple Socket.IO initialization like the working example
console.log('🌐 Initializing...');

// Wait for window to load before initializing socket
window.addEventListener('load', function() {
    // Give a moment for Socket.IO script to execute
    setTimeout(function() {
        if (typeof io !== 'undefined') {
            socket = io();
            setupSocketListeners();
            console.log('✅ Socket.IO initialized');
        } else {
            console.error('❌ Socket.IO not loaded');
            updateStatus('❌ Socket.IO failed to load', 'red');
        }
    }, 500);
});

function setupSocketListeners() {
    socket.on('connect', () => {
        socketReady = true;
        console.log('✅ Connected to server!');
        updateStatus('✅ Connected - Enter session ID', 'green');
    });

    socket.on('connect_error', (err) => {
        console.error('❌ Connection error:', err.message);
        updateStatus('❌ Cannot connect', 'red');
    });

    socket.on('disconnect', () => {
        socketReady = false;
        console.log('❌ Disconnected');
        updateStatus('❌ Disconnected', 'red');
    });

    socket.on('load_code', (data) => {
        console.log('📝 Loading code');
        if (editor && editorReady) {
            isUpdating = true;
            editor.setValue(data.code);
            isUpdating = false;
        }
    });

    socket.on('code_update', (data) => {
        console.log('🔄 Code update');
        if (editor && editorReady) {
            isUpdating = true;
            const pos = editor.getPosition();
            editor.setValue(data.code);
            editor.setPosition(pos);
            isUpdating = false;
        }
    });

    socket.on('output', (data) => {
        console.log('📤 Output received');
        document.getElementById('output').textContent = data.result;
    });

    socket.on('user_count', (data) => {
        if (currentSessionId) {
            updateStatus(`✅ Session: ${currentSessionId} (${data.count} user${data.count !== 1 ? 's' : ''})`, 'green');
            console.log(`👥 ${data.count} user(s)`);
        }
    });
}

// Initialize Monaco Editor
if (!window.editorInitialized) {
    window.editorInitialized = true;
    
    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } });

    require(['vs/editor/editor.main'], () => {
        try {
            editor = monaco.editor.create(document.getElementById('editor'), {
                value: '# Write Python DSA code here\n\ndef solution():\n    pass\n',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 14,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on'
            });

            editor.onDidChangeModelContent(() => {
                if (!isUpdating && currentSessionId && socket && socketReady) {
                    socket.emit('code_change', {
                        session_id: currentSessionId,
                        code: editor.getValue()
                    });
                }
            });
            
            editorReady = true;
            console.log('✅ Editor initialized');
        } catch (e) {
            console.error('❌ Editor failed:', e);
            updateStatus('Editor error', 'red');
        }
    });
}

function updateStatus(msg, color = 'yellow') {
    const status = document.getElementById('status');
    if (status) {
        status.textContent = msg;
        status.style.color = color;
    }
}

function joinSession() {
    const sessionId = document.getElementById('sessionId').value.trim();
    
    if (!sessionId) {
        alert('Enter a session ID');
        return;
    }
    
    if (!socketReady || !socket) {
        alert('Connecting to server... Please wait a moment and try again.');
        return;
    }
    
    if (!editorReady) {
        alert('Editor not ready yet, wait a moment...');
        return;
    }
    
    currentSessionId = sessionId;
    updateStatus(`Joining: ${sessionId}...`, 'blue');
    socket.emit('join', { session_id: sessionId });
    console.log(`👥 Joining session: ${sessionId}`);
}

function runCode() {
    if (!currentSessionId) {
        alert('Join a session first');
        return;
    }
    if (!editor || !editorReady) {
        alert('Editor not ready');
        return;
    }
    const code = editor.getValue();
    if (!code.trim()) {
        alert('Write some code first');
        return;
    }
    document.getElementById('output').textContent = '⏳ Running...';
    console.log('▶ Running code');
    socket.emit('run_code', {
        session_id: currentSessionId,
        code: code
    });
}

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (editorReady && socketReady && currentSessionId) {
            e.preventDefault();
            runCode();
        }
    }
});
