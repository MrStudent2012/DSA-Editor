let editor;
let socket;
let currentSessionId = null;
let isUpdating = false;
let editorReady = false;

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
            if (!isUpdating && currentSessionId) {
                socket.emit('code_change', {
                    session_id: currentSessionId,
                    code: editor.getValue()
                });
            }
        });
        
        editorReady = true;
        console.log('✅ Editor initialized');
        updateStatus('Ready', 'green');
    } catch (e) {
        console.error('❌ Editor failed:', e);
        updateStatus('Editor error', 'red');
    }
});

socket = io();

socket.on('connect', () => {
    console.log('✅ Connected to server');
    updateStatus('Connected', 'green');
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected');
    updateStatus('Disconnected', 'red');
});

socket.on('load_code', (data) => {
    console.log('📝 Code loaded');
    if (editor && editorReady) {
        isUpdating = true;
        editor.setValue(data.code);
        isUpdating = false;
    }
});

socket.on('code_update', (data) => {
    console.log('🔄 Code updated');
    if (editor && editorReady) {
        isUpdating = true;
        const pos = editor.getPosition();
        editor.setValue(data.code);
        editor.setPosition(pos);
        isUpdating = false;
    }
});

socket.on('output', (data) => {
    console.log('📤 Output:', data.result);
    document.getElementById('output').textContent = data.result;
});

function updateStatus(msg, color = 'yellow') {
    const status = document.getElementById('status');
    status.textContent = msg;
    status.style.color = color;
}

function joinSession() {
    const sessionId = document.getElementById('sessionId').value.trim();
    
    if (!sessionId) {
        alert('Enter a session ID');
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
        if (editorReady && currentSessionId) {
            e.preventDefault();
            runCode();
        }
    }
});

// Update status after joining
socket.on('user_count', (data) => {
    if (currentSessionId) {
        updateStatus(`✅ Session: ${currentSessionId} (${data.count} user${data.count !== 1 ? 's' : ''})`, 'green');
        console.log(`👥 User count: ${data.count}`);
    }
});
