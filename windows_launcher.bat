@echo off
REM this belongs in root /start_imgfactory.bat
REM IMG Factory 1.5 - Windows Launcher with Cache Cleanup
REM X-Seti - June25,2025

echo.
echo ==========================================
echo   IMG Factory 1.5 - Windows Launcher
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or newer
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo Python version:
python --version

REM Check if we're in the right directory
if not exist "Imgfactory.py" (
    if not exist "imgfactory.py" (
        echo ERROR: IMG Factory main file not found
        echo Make sure you're running this from the IMG Factory directory
        echo Looking for: Imgfactory_Demo.py or imgfactory_demo.py
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting IMG Factory with cache cleanup...
echo.

REM Try to run with cache cleanup first
if exist "startup_cleanup.py" (
    echo Using startup cleanup script...
    python startup_cleanup.py
) else if exist "img_cache_manager.py" (
    echo Running manual cache cleanup...
    python -c "from img_cache_manager import auto_cleanup; auto_cleanup()"
    if exist "Imgfactory.py" (
        python Imgfactory_Demo.py
    ) else (
        python imgfactory_demo.py
    )
) else (
    echo Cache cleanup not available, starting normally...
    if exist "Imgfactory.py" (
        python Imgfactory_Demo.py
    ) else (
        python imgfactory_demo.py
    )
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ==========================================
    echo   Application exited with error
    echo ==========================================
    echo.
    echo If you're experiencing issues:
    echo 1. Make sure all dependencies are installed
    echo 2. Check that PyQt6 is installed: pip install PyQt6
    echo 3. Try running: python -m pip install --upgrade PyQt6
    echo 4. Check the console output above for specific errors
    echo.
) else (
    echo.
    echo IMG Factory closed normally.
)

echo.
pause
