cd /d "%~dp0"
call direnv\Scripts\activate.bat
start cmd /k "uvicorn backend.main:app --reload"
start cmd /k "streamlit run frontend/app.py"
