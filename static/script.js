let editor;
let socket;
let currentSessionId = null;
let isUpdating = false;

require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } });

require(['vs/editor/editor.main'], () => {
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
});

socket = io();

socket.on('connect', () => {
    document.getElementById('status').textContent = 'Connected';
});

socket.on('disconnect', () => {
    document.getElementById('status').textContent = 'Disconnected';
});

socket.on('load_code', (data) => {
    isUpdating = true;
    editor.setValue(data.code);
    isUpdating = false;
});

socket.on('code_update', (data) => {
    isUpdating = true;
    const pos = editor.getPosition();
    editor.setValue(data.code);
    editor.setPosition(pos);
    isUpdating = false;
});

socket.on('output', (data) => {
    document.getElementById('output').textContent = data.result;
});

function joinSession() {
    const sessionId = document.getElementById('sessionId').value;
    currentSessionId = sessionId;
    socket.emit('join', { session_id: sessionId });
    document.getElementById('status').textContent = `Joined: ${sessionId}`;
}

function runCode() {
    if (!currentSessionId) {
        alert('Join a session first');
        return;
    }
    const code = editor.getValue();
    document.getElementById('output').textContent = 'Running...';
    socket.emit('run_code', {
        session_id: currentSessionId,
        code: code
    });
}

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        runCode();
    }
});
