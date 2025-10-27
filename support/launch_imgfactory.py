#!/usr/bin/env python3
"""
#this belongs in root /launch_imgfactory.py - version 3
IMG Factory 1.5 - Modern Launcher Script
X-Seti - July03 2025 - Clean, reliable startup with comprehensive diagnostics
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import importlib.util

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🎮 IMG Factory 1.5 - Python Edition")
    print("   Advanced IMG Archive Management Tool")
    print("   X-Seti - 2025")
    print("=" * 60)

def check_python_version() -> bool:
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    required = (3, 8)
    
    print(f"   Current: Python {version.major}.{version.minor}.{version.micro}")
    print(f"   Required: Python {required[0]}.{required[1]}+")
    
    if version >= required:
        print("   ✅ Python version OK")
        return True
    else:
        print(f"   ❌ Python {required[0]}.{required[1]}+ required")
        print(f"   Please upgrade Python to {required[0]}.{required[1]} or newer")
        return False

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check required Python dependencies"""
    print("📦 Checking dependencies...")
    
    dependencies = [
        ("PyQt6", "PyQt6.QtWidgets"),
        ("PyQt6.QtCore", "PyQt6.QtCore"), 
        ("PyQt6.QtGui", "PyQt6.QtGui")
    ]
    
    missing = []
    
    for name, module in dependencies:
        try:
            spec = importlib.util.find_spec(module)
            if spec is not None:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} (not found)")
                missing.append(name)
        except ImportError:
            print(f"   ❌ {name} (import error)")
            missing.append(name)
    
    if not missing:
        print("   ✅ All dependencies satisfied")
        return True, []
    else:
        print(f"   ❌ Missing: {', '.join(missing)}")
        return False, missing

def check_project_structure() -> Tuple[bool, List[str]]:
    """Check project file structure"""
    print("📁 Checking project structure...")
    
    current_dir = Path(__file__).parent
    required_files = [
        "imgfactory.py",
        "methods.img_core_classes.py", 
        "gui/gui_layout.py"
    ]
    
    optional_files = [
        "utils/app_settings_system.py",
        "app_settings_system.py",  # Fallback location
        "components.Img_Creator.img_creator.py",
        "components/img_validator.py",
        "gui/menu.py"
    ]
    
    missing_required = []
    found_optional = []
    
    # Check required files
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (required)")
            missing_required.append(file_path)
    
    # Check optional files
    for file_path in optional_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
            found_optional.append(file_path)
        else:
            print(f"   ⚠️  {file_path} (optional)")
    
    # Check directories
    directories = ["components", "gui", "themes"]
    for dir_name in directories:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.glob("*.py")))
            print(f"   ✅ {dir_name}/ ({file_count} Python files)")
        else:
            print(f"   ❌ {dir_name}/ (missing directory)")
    
    if not missing_required:
        print("   ✅ Project structure OK")
        return True, found_optional
    else:
        print(f"   ❌ Missing required files: {missing_required}")
        return False, missing_required

def setup_python_path():
    """Setup Python import paths"""
    print("🛠️  Setting up Python paths...")
    
    current_dir = Path(__file__).parent
    paths_to_add = [
        current_dir,
        current_dir / "components",
        current_dir / "gui",
        current_dir / "utils"
    ]
    
    for path in paths_to_add:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
            print(f"   ✅ Added {path}")
        elif str(path) in sys.path:
            print(f"   ✅ Already in path: {path}")
        else:
            print(f"   ⚠️  Skipped missing: {path}")

def install_missing_dependencies(missing: List[str]) -> bool:
    """Attempt to install missing dependencies"""
    print("🔧 Attempting to install missing dependencies...")
    
    # Map package names to pip install names
    pip_packages = {
        "PyQt6": "PyQt6",
        "PyQt6.QtCore": "PyQt6", 
        "PyQt6.QtGui": "PyQt6"
    }
    
    unique_packages = set()
    for pkg in missing:
        if pkg in pip_packages:
            unique_packages.add(pip_packages[pkg])
    
    if not unique_packages:
        print("   ❌ No packages to install")
        return False
    
    for package in unique_packages:
        print(f"   📦 Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"   ✅ {package} installed successfully")
            else:
                print(f"   ❌ {package} installation failed")
                print(f"      Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ {package} installation timed out")
            return False
        except Exception as e:
            print(f"   ❌ {package} installation error: {e}")
            return False
    
    print("   ✅ All packages installed successfully")
    return True

def launch_application() -> int:
    """Launch the main application"""
    print("🚀 Launching IMG Factory...")
    
    try:
        # Try to import the main module
        import imgfactory
        print("   ✅ Main module imported successfully")
        
        # Check if main function exists
        if hasattr(imgfactory, 'main'):
            print("   ✅ Using main() function")
            return imgfactory.main()
        else:
            print("   ✅ Creating application directly")
            
            # Create application instance
            from PyQt6.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            app.setApplicationName("IMG Factory")
            app.setApplicationVersion("1.5")
            app.setOrganizationName("IMG Factory")
            
            # Create main window
            if hasattr(imgfactory, 'AppSettings'):
                settings = imgfactory.AppSettings()
            else:
                # Try utils location
                try:
                    from utils.app_settings_system import AppSettings
                    settings = AppSettings()
                except ImportError:
                    try:
                        from app_settings_system import AppSettings
                        settings = AppSettings()
                    except ImportError:
                        print("   ⚠️  Settings system not available, using defaults")
                        settings = None
            
            window = imgfactory.IMGFactory(settings)
            window.show()
            
            print("   ✅ IMG Factory started successfully")
            return app.exec()
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 This usually means missing dependencies or file structure issues")
        return 1
    except Exception as e:
        print(f"   ❌ Launch error: {e}")
        import traceback
        print("   📝 Full traceback:")
        traceback.print_exc()
        return 1

def show_help():
    """Show help information"""
    print("\n📚 Troubleshooting Help:")
    print("─" * 40)
    print("If IMG Factory won't start:")
    print("1. Ensure Python 3.8+ is installed")
    print("2. Install PyQt6: pip install PyQt6")
    print("3. Check all files are in the correct locations")
    print("4. Try running: python -m pip install --upgrade PyQt6")
    print("5. Run with verbose output: python -v imgfactory.py")
    print("\n📧 For support: Check project documentation")
    print("🐛 Report bugs: Include the full error output above")

def main() -> int:
    """Main launcher function"""
    print_header()
    
    # Step 1: Check Python version
    if not check_python_version():
        show_help()
        return 1
    
    print()
    
    # Step 2: Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print(f"\n🔧 Attempting to install missing dependencies...")
        if install_missing_dependencies(missing_deps):
            print("   ✅ Dependencies installed, please restart the launcher")
            return 0
        else:
            print("   ❌ Failed to install dependencies")
            print("\n💡 Manual installation:")
            print("   pip install PyQt6")
            show_help()
            return 1
    
    print()
    
    # Step 3: Check project structure  
    structure_ok, found_files = check_project_structure()
    if not structure_ok:
        print("   ❌ Project structure issues detected")
        show_help()
        return 1
    
    print()
    
    # Step 4: Setup Python paths
    setup_python_path()
    
    print()
    
    # Step 5: Launch application
    exit_code = launch_application()
    
    # Step 6: Handle exit
    if exit_code == 0:
        print("\n✅ IMG Factory closed normally")
    else:
        print(f"\n❌ IMG Factory exited with error code: {exit_code}")
        show_help()
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"\n💥 Unexpected launcher error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        show_help()
        sys.exit(1)
