#!/usr/bin/env python3
"""
IMG Factory Launch Script
Entry point for the IMG Factory application with error handling and setup
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    # Check PyQt6
    try:
        from PyQt6 import QtCore, QtWidgets, QtGui
        try:
            version = QtCore.PYQT_VERSION_STR
            print(f"✓ PyQt6 {version} found")
        except AttributeError:
            print("✓ PyQt6 found (version unknown)")
    except ImportError as e:
        missing_deps.append("PyQt6")
        print(f"❌ PyQt6 not found: {e}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        missing_deps.append("Python 3.8+")
    else:
        print(f"✓ Python {sys.version.split()[0]} found")
    
    # Check optional dependencies
    optional_deps = {
        'zlib': 'Built-in compression support',
        'lz4': 'LZ4 compression support (optional)',
    }
    
    for dep, description in optional_deps.items():
        try:
            if dep == 'zlib':
                import zlib
            elif dep == 'lz4':
                import lz4.frame
            print(f"✓ {dep} - {description}")
        except ImportError:
            print(f"⚠ {dep} - {description} (not available)")
    
    if missing_deps:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("\nTo install missing dependencies:")
        print("pip install PyQt6")
        if "Python 3.8+" in missing_deps:
            print("Please upgrade to Python 3.8 or newer")
        return False
    
    return True

def setup_paths():
    """Setup Python paths for module imports"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Add components directory if it exists
    components_dir = current_dir / "components"
    if components_dir.exists() and str(components_dir) not in sys.path:
        sys.path.insert(0, str(components_dir))
    
    print(f"✓ Added {current_dir} to Python path")
    if components_dir.exists():
        print(f"✓ Added {components_dir} to Python path")

def check_files():
    """Check if required IMG Factory files exist"""
    required_files = [
        "imgfactory_main.py",
        "img_manager.py", 
        "img_creator.py",
        "img_template_manager.py",
        "img_validator.py"
    ]
    
    current_dir = Path(__file__).parent
    missing_files = []
    
    for file_name in required_files:
        file_path = current_dir / file_name
        if file_path.exists():
            print(f"✓ {file_name} found")
        else:
            missing_files.append(file_name)
            print(f"❌ {file_name} missing")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all IMG Factory modules are in the same directory.")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🎮 IMG Factory 2.0 - Python Edition")
    print("=" * 40)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Cannot start due to missing dependencies")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("\nChecking required files...")
    if not check_files():
        print("\n❌ Cannot start due to missing files")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Setup paths
    print("\nSetting up paths...")
    setup_paths()
    
    try:
        # Import and run the main application
        print("\n🚀 Starting IMG Factory...")
        
        # Test import before running
        try:
            import imgfactory_main
            print("✓ Main application module imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import main application: {e}")
            print("\nTrying to import individual modules for diagnosis...")
            
            modules = ["img_manager", "img_creator", "img_template_manager", "img_validator"]
            for module in modules:
                try:
                    __import__(module)
                    print(f"✓ {module} imported successfully")
                except ImportError as import_err:
                    print(f"❌ {module} failed to import: {import_err}")
            
            raise e
        
        # Run the application
        imgfactory_main.main()
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure all IMG Factory modules are in the correct location.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {Path(__file__).parent}")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error during startup: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
