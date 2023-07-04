from os import environ
from vdiManager.settings import Config
"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "vdiManager.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 4
# The socket to bind
bind = Config.GUNICORN_BIND
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
accesslog = Config.GUNICORN_ACCESS_LOG
errorlog = Config.GUNICORN_ERROR_LOG
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
# pidfile = "/home/baniasadi/vdi/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
#daemon = True
