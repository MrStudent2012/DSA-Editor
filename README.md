# DSA Collaborative Editor

Real-time Python code editor for practicing DSA with friends remotely.

## Features

- 🚀 Real-time code synchronization
- 🐍 Python code execution
- 👥 Multiple users in same session
- 🌐 Works remotely via cloud

## Quick Start - Local Testing

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

## Deploy to Cloud (FREE)

### Render (Recommended)

1. Create account: https://render.com
2. Push code to GitHub
3. Connect repo on Render
4. Deploy! (auto-configured via render.yaml)
5. Share URL with friends

### Heroku

```bash
heroku create your-app-name
git push heroku main
```

## How to Use

1. You: Open app URL, enter session ID (e.g., "team-1"), click Join
2. Friend: Open same URL, enter same session ID, click Join
3. Both: Write Python code, see changes in real-time
4. Both: Click "Run" to execute code (Ctrl+Enter)
5. Both: See output instantly

## Project Structure

```
.
├── app.py              # Flask + SocketIO server
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend
├── static/
│   ├── style.css      # Styling
│   └── script.js      # Client code
├── Procfile           # For Heroku/Render
├── render.yaml        # Render config
└── runtime.txt        # Python version
```

## Tech Stack

- Backend: Flask + Flask-SocketIO
- Frontend: Monaco Editor (VS Code)
- Deployment: Render, Heroku, Railway

## Size

Minimal codebase: ~200 lines of code