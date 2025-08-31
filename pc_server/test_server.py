#!/usr/bin/env python3
"""
Simple test script to check if the Flask app can start
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask
    print("✅ Flask imported successfully")
    
    # Create a minimal app
    app = Flask(__name__)
    print("✅ Flask app created successfully")
    
    @app.route('/')
    def hello():
        return "Hello, World!"
    
    print("✅ Route added successfully")
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 