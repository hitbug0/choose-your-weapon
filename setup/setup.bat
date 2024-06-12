cd ..

python -m venv direnv
call direnv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r setup\requirements.txt

pause
