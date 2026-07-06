@echo off
REM Run the Wisdom's Kitchen Flask app from the project root.
call "%~dp0\.venv\Scripts\activate.bat"
python "%~dp0app.py"
