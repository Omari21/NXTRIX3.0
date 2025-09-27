@echo off
echo Starting NXTRIX 3.0 Investment Platform...
cd /d "C:\Users\Mania\OneDrive\Documents\NXTRIX3.0\nxtrix-crm"

:retry
echo Attempting to start application on port 8505...
streamlit run simplified_app.py --server.port 8505 --server.headless false --server.enableCORS false
echo Application stopped. Restarting in 3 seconds...
timeout /t 3
goto retry