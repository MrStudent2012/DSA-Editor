import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
worker_class = "gthread"
workers = 1  # Keep at 1 for in-memory sessions
threads = 4  # Increased for better concurrency
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
