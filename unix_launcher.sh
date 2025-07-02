#!/bin/bash
#this belongs in root /start_imgfactory.sh
# IMG Factory 1.5 - Unix Launcher with Cache Cleanup
# X-Seti - June25,2025


# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is available
if ! command_exists python3; then
    if ! command_exists python; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.8 or newer"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Show Python version
echo "Python version:"
$PYTHON_CMD --version

# Check Python version (must be 3.8+)
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "ERROR: Python 3.8 or newer is required"
    echo "Current version: $PYTHON_VERSION"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "Imgfactory.py" && ! -f "imgfactory.py" ]]; then
    echo "ERROR: IMG Factory main file not found"
    echo "Make sure you're running this from the IMG Factory directory"
    echo "Looking for: Imgfactory.py or imgfactory.py"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Starting IMG Factory with cache cleanup..."
echo ""

# Make the script executable if it isn't already
chmod +x "$0" 2>/dev/null

# Try to run with cache cleanup first
if [[ -f "startup_cleanup.py" ]]; then
    echo "Using startup cleanup script..."
    $PYTHON_CMD startup_cleanup.py
    EXIT_CODE=$?
elif [[ -f "img_cache_manager.py" ]]; then
    echo "Running manual cache cleanup..."
    $PYTHON_CMD -c "from img_cache_manager import auto_cleanup; auto_cleanup()"
    
    # Start main application
    if [[ -f "Imgfactory.py" ]]; then
        $PYTHON_CMD Imgfactory.py
        EXIT_CODE=$?
    else
        $PYTHON_CMD imgfactory.py
        EXIT_CODE=$?
    fi
else
    echo "Cache cleanup not available, starting normally..."
    if [[ -f "Imgfactory.py" ]]; then
        $PYTHON_CMD Imgfactory.py
        EXIT_CODE=$?
    else
        $PYTHON_CMD imgfactory.py
        EXIT_CODE=$?
    fi
fi

# Check exit code
if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "=========================================="
    echo "  Application exited with error ($EXIT_CODE)"
    echo "=========================================="
    echo ""
    echo "If you're experiencing issues:"
    echo "1. Make sure all dependencies are installed"
    echo "2. Check that PyQt6 is installed: pip install PyQt6"
    echo "3. Try running: $PYTHON_CMD -m pip install --upgrade PyQt6"
    echo "4. Check the console output above for specific errors"
    echo "5. Try running with: $PYTHON_CMD -v Imgfactory.py (verbose mode)"
    echo ""
else
    echo ""
    echo "IMG Factory closed normally."
fi

echo ""
read -p "Press Enter to exit..."
