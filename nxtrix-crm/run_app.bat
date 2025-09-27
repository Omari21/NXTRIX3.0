@echo off
cd /d "C:\Users\Mania\OneDrive\Documents\NXTRIX3.0\nxtrix-crm"
set PYTHONPATH=%CD%
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
python -m streamlit run streamlit_app.py --server.port 8501 --server.headless true
pause