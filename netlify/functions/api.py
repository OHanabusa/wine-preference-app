import os
import sys

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import app
from flask import Flask, jsonify
from netlify_lambda_wsgi import make_wsgi_handler

# Function to handle serverless function requests
def handler(event, context):
    # Create WSGI handler for Flask application
    wsgi_handler = make_wsgi_handler(app)
    
    # Call the WSGI handler
    return wsgi_handler(event, context)
