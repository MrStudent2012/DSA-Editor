import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
worker_class = "gthread"
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
threads = 2
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
