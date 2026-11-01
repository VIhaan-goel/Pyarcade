import os

# IMPORTANT: keep ONE worker. Running games are kept in this process's memory,
# so several workers would not be able to see each other's sessions.
workers = 1
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "32"))  # one thread per open stream
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")
timeout = 120
accesslog = "-"
