# Vercel Python entrypoint
# This file imports the Flask app from app.py in the root

import sys
import os

# Add the root directory to Python path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# No need to rename or change anything
# Vercel will automatically look for a WSGI app named `app`
