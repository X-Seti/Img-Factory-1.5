#!/usr/bin/env python3
"""
Simple GUI Test - Check if PyQt6 GUI works at all
"""

import sys
import traceback

def test_basic_gui():
    """Test basic PyQt6 GUI functionality"""
    print("Testing basic PyQt6 GUI...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PyQt6.QtCore import Qt
        
        print("✓ PyQt6 widgets imported successfully")
        
        # Create application
        app = QApplication(sys.argv)
        print("✓ QApplication created")
        
        # Create simple window
        window = QMainWindow()
        window.setWindowTitle("IMG Factory Test Window")
        window.setGeometry(200, 200, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add widgets
        label = QLabel("🎮 IMG Factory Test Window")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        button = QPushButton("✅ Close Test")
        button.clicked.connect(window.close)
        layout.addWidget(button)
        
        print("✓ Window created successfully")
        
        # Show window
        window.show()
        print("✓ Window.show() called")
        
        # Check if window is visible
        if window.isVisible():
            print("✓ Window reports as visible")
        else:
            print("❌ Window reports as not visible")
        
        # Get screen info
        screen = app.primaryScreen()
        if screen:
            geometry = screen.geometry()
            print(f"✓ Primary screen: {geometry.width()}x{geometry.height()}")
        else:
            print("❌ No primary screen found")
        
        print("\n🚀 Test window should be visible now!")
        print("If you can see a small window with 'IMG Factory Test Window', PyQt6 GUI works.")
        print("Click the 'Close Test' button or close the window to continue.")
        
        # Run event loop
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating GUI: {e}")
        traceback.print_exc()
        return False

def test_display_environment():
    """Test display environment variables"""
    print("\nTesting display environment...")
    
    import os
    
    # Check DISPLAY variable (Linux/Unix)
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✓ DISPLAY environment variable: {display}")
    else:
        print("❌ DISPLAY environment variable not set")
        if sys.platform.startswith('linux'):
            print("  This may cause GUI issues on Linux systems")
            print("  Try: export DISPLAY=:0")
    
    # Check platform
    print(f"✓ Platform: {sys.platform}")
    
    # Check if running in terminal/SSH
    if os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'):
        print("⚠ Running over SSH - GUI may not work without X11 forwarding")
        print("  Try: ssh -X username@hostname")
    
    # Check XDG session (Linux)
    if sys.platform.startswith('linux'):
        session_type = os.environ.get('XDG_SESSION_TYPE')
        if session_type:
            print(f"✓ XDG_SESSION_TYPE: {session_type}")
        else:
            print("⚠ XDG_SESSION_TYPE not set")

def main():
    print("🔧 IMG Factory GUI Diagnostic Test")
    print("=" * 40)
    
    # Test environment
    test_display_environment()
    
    # Test basic GUI
    result = test_basic_gui()
    
    if result:
        print("\n✅ GUI test completed successfully!")
        print("PyQt6 GUI should be working. Let's try the main application...")
        
        # Try to import our main modules
        try:
            print("\nTesting IMG Factory imports...")
            import imgfactory_main
            print("✓ imgfactory_main imported")
            
            # Try to run just the GUI part
            print("\nTrying to create IMG Factory main window...")
            
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            
            window = imgfactory_main.IMGFactoryMain()
            print("✓ IMG Factory main window created")
            
            window.show()
            print("✓ IMG Factory window shown")
            
            if window.isVisible():
                print("✅ IMG Factory window is visible!")
            else:
                print("❌ IMG Factory window is not visible")
            
            print("\n🎮 IMG Factory should now be running!")
            return app.exec()
            
        except Exception as e:
            print(f"❌ Error running IMG Factory: {e}")
            traceback.print_exc()
            return False
    else:
        print("\n❌ GUI test failed!")
        print("PyQt6 GUI is not working properly on this system.")
        
        # Provide troubleshooting suggestions
        print("\n🔧 Troubleshooting suggestions:")
        if sys.platform.startswith('linux'):
            print("  1. Make sure you have a desktop environment running")
            print("  2. If using SSH, enable X11 forwarding: ssh -X username@hostname")
            print("  3. Try setting DISPLAY: export DISPLAY=:0")
            print("  4. Install Qt platform plugin: sudo apt-get install qt6-qpa-plugins")
        elif sys.platform == 'darwin':  # macOS
            print("  1. Make sure you're running from a terminal with GUI access")
            print("  2. Try: pip install --upgrade PyQt6")
        elif sys.platform.startswith('win'):  # Windows
            print("  1. Try running as administrator")
            print("  2. Try: pip install --upgrade PyQt6")
        
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nFatal error during test: {e}")
        traceback.print_exc()
