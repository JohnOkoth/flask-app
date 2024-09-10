@echo off
cd C:\Users\grace\Project_Folder  # Navigate to your project folder where app.py is located
start python app.py               # Start Flask
TIMEOUT /T 2                      # Wait for 2 seconds to ensure Flask is running
start http://127.0.0.1:5000        # Open the default browser and navigate to Flask app
