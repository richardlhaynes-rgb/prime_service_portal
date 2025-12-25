import os
from waitress import serve
from config.wsgi import application

# This script tells Waitress how to serve the Django app
if __name__ == "__main__":
    print("PRIME Service Portal is starting...")
    print("Access the site at http://localhost:8000")
    print("Press Ctrl+C to stop the server.")
    
    # serve the 'application' defined in config/wsgi.py
    serve(application, host='0.0.0.0', port=8000, threads=32, channel_timeout=60)