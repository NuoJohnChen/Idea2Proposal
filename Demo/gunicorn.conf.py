# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:4090"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'idea2proposal'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Preload app for better performance
preload_app = True

# Environment variables
raw_env = [
    'FLASK_ENV=production',
]

# Worker timeout for long-running requests
worker_timeout = 300

# Graceful timeout
graceful_timeout = 30
