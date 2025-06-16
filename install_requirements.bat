@echo off
echo ========================================
echo Creating virtual environment...
echo ========================================
python -m venv venv

echo ========================================
echo Activating virtual environment...
echo ========================================
call venv\Scripts\activate

echo ========================================
echo Installing all required libraries from requirements.txt...
echo ========================================
pip install -r requirements.txt

echo ========================================
echo ✅ Setup complete! You can now run your Flask app.
echo ========================================
pause
