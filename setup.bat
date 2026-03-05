@echo off
echo ========================================
echo Personal Productivity Tracker Setup
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo Python found!

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!

echo.
echo [3/4] Database Setup Instructions:
echo.
echo Please complete these steps manually:
echo 1. Make sure MySQL is installed and running
echo 2. Connect to MySQL as root: mysql -u root -p
echo 3. Create database: CREATE DATABASE productivity_tracker;
echo 4. Import schema: mysql -u root -p productivity_tracker ^< database_schema.sql
echo 5. Update database credentials in app.py (DB_CONFIG section)
echo.

echo [4/4] Setup complete!
echo.
echo To run the application:
echo 1. Complete the database setup above
echo 2. Run: python app.py
echo 3. Open http://localhost:5000 in your browser
echo.
echo For detailed instructions, see README.md
echo.
pause