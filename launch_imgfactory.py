#!/usr/bin/env python3
"""
#this belongs in root /launch_imgfactory.py - version 5
IMG Factory 1.5 - Modern Launcher Script
X-Seti - July03 2025 - Clean, reliable startup with comprehensive diagnostics
"""

import sys
import os
import mimetypes
import subprocess
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path
print("Starting application...")
import importlib.util


# Setup paths FIRST - before any other imports
current_dir = Path(__file__).parent
components_dir = current_dir / "components"
gui_dir = current_dir / "gui"
utils_dir = current_dir / "/utils"


# Add directories to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if components_dir.exists() and str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))
if gui_dir.exists() and str(gui_dir) not in sys.path:
    sys.path.insert(0, str(gui_dir))
if utils_dir.exists() and str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

# Now continue with other imports
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QDialog,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton, QToolBar, QFormLayout
)
print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut, QTextCursor

# OR use the full path:
from utils.app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog

#components
from components.Img_Creator.img_creator import NewIMGDialog, IMGCreationThread
#from components.Txd_Editor.txd_workshop import TXDEditor

#debug
from debug.col_debug_functions import set_col_debug_enabled
from debug.unified_debug_functions import integrate_all_improvements, install_debug_control_system

#Core functions.
from core.img_formats import GameSpecificIMGDialog, IMGCreator
from core.file_extraction import setup_complete_extraction_integration
from core.file_type_filter import integrate_file_filtering
from core.rw_versions import get_rw_version_name
from core.right_click_actions import integrate_right_click_actions, setup_table_context_menu
from core.shortcuts import setup_all_shortcuts, create_debug_keyboard_shortcuts
from core.convert import convert_img, convert_img_format
from core.img_split import integrate_split_functions
from core.theme_integration import integrate_theme_system
from core.create import create_new_img
from core.open import _detect_and_open_file, open_file_dialog, _detect_file_type
from core.clean import integrate_clean_utilities
from core.close import install_close_functions, setup_close_manager
from core.export import integrate_export_functions
from core.impotr import integrate_import_functions #import impotr
from core.remove import integrate_remove_functions
from core.export import export_selected_function, export_all_function, integrate_export_functions
from core.dump import dump_all_function, dump_selected_function, integrate_dump_functions
from core.import_via import integrate_import_via_functions
from core.remove_via import integrate_remove_via_functions
from core.export_via import export_via_function
from core.rebuild import integrate_rebuild_functions
from core.rebuild_all import integrate_batch_rebuild_functions
from core.imgcol_rename import integrate_imgcol_rename_functions
from core.imgcol_replace import integrate_imgcol_replace_functions
from core.imgcol_convert import integrate_imgcol_convert_functions
from core.save_entry import integrate_save_entry_function
from core.rw_unk_snapshot import integrate_unknown_rw_detection
from core.col_viewer_integration import integrate_col_viewer

#gui-layout
from gui.ide_dialog import integrate_ide_dialog
from gui.gui_backend import ButtonDisplayMode, GUIBackend
from gui.main_window import IMGFactoryMainWindow
from gui.col_display import update_col_info_bar_enhanced
from gui.gui_layout import IMGFactoryGUILayout
from gui.unified_button_theme import apply_unified_button_theme
from gui.gui_menu import IMGFactoryMenuBar
from gui.autosave_menu import integrate_autosave_menu
from gui.file_menu_integration import add_project_menu_items
from gui.directory_tree_system import integrate_directory_tree_system
from gui.tearoff_integration import integrate_tearoff_system

# After GUI setup:
from gui.gui_context import (add_col_context_menu_to_entries_table, open_col_file_dialog, open_col_batch_proc_dialog, open_col_editor_dialog, analyze_col_file_dialog)

#Shared Methods - Shared Functions.
from methods.img_core_classes import (IMGFile, IMGEntry, IMGVersion, Platform, IMGEntriesTable, FilterPanel, IMGFileInfoPanel, TabFilterWidget, integrate_filtering, create_entries_table_panel, format_file_size)
from methods.col_core_classes import (COLFile, COLModel, COLVersion, COLMaterial, COLFaceGroup, COLSphere, COLBox, COLVertex, COLFace, Vector3, BoundingBox, diagnose_col_file, set_col_debug_enabled, is_col_debug_enabled)

from methods.col_integration import integrate_complete_col_system
from methods.col_functions import setup_complete_col_integration
from methods.col_parsing_functions import load_col_file_safely
from methods.col_structure_manager import COLStructureManager
from methods.img_analyze import analyze_img_corruption, show_analysis_dialog
from methods.img_integration import integrate_img_functions, img_core_functions
from methods.img_routing_operations import install_operation_routing
from methods.img_validation import IMGValidator


from methods.populate_img_table import reset_table_styling, install_img_table_populator
from methods.progressbar_functions import integrate_progress_system
from methods.update_ui_for_loaded_img import update_ui_for_loaded_img, integrate_update_ui_for_loaded_img
from methods.import_highlight_system import enable_import_highlighting
from methods.refresh_table_functions import integrate_refresh_table
from methods.img_entry_operations import integrate_entry_operations
from methods.img_import_export import integrate_import_export_functions
from methods.col_export_shared import integrate_col_export_shared
#from methods.mirror_tab_shared import show_mirror_tab_selection
from methods.ide_parser_functions import integrate_ide_parser
from methods.find_dups_functions import find_duplicates_by_hash, show_duplicates_dialog
from methods.dragdrop_functions import integrate_drag_drop_system
from methods.img_templates import IMGTemplateManager, TemplateManagerDialog

from components.Img_Factory.img_factory_thread import IMGLoadThread

App_name = "Img Factory 1.5"

def print_header():
    """Print application header"""
    print("=" * 60)
    print("   IMG Factory 1.5 - Python Edition")
    print("   Advanced IMG Archive Management Tool")
    print("   X-Seti - 2025")
    print("=" * 60)

def check_python_version() -> bool:
    """Check Python version compatibility"""
    print("  Checking Python version...")
    
    version = sys.version_info
    required = (3, 8)
    
    print(f"   Current: Python {version.major}.{version.minor}.{version.micro}")
    print(f"   Required: Python {required[0]}.{required[1]}+")
    
    if version >= required:
        print("Python version OK")
        return True
    else:
        print(f"Error Python {required[0]}.{required[1]}+ required")
        print(f"Please upgrade Python to {required[0]}.{required[1]} or newer")
        return False

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check required Python dependencies"""
    print("Checking dependencies...")
    
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
                print(f"Found {name}")
            else:
                print(f"Error {name} (not found)")
                missing.append(name)
        except ImportError:
            print(f"Error {name} (import error)")
            missing.append(name)

    if not missing:
        print("All dependencies satisfied")
        return True, []
    else:
        print(f"Missing: {', '.join(missing)}")
        return False, missing

def check_project_structure() -> Tuple[bool, List[str]]:
    """Check project file structure"""
    print("Checking project structure...")
    
    current_dir = Path(__file__).parent
    required_files = [
        "components/Img_Factory/imgfactory.py",
        "gui/gui_layout.py"
    ]
    
    optional_files = [
        "utils/app_settings_system.py",
        "components/Img_Creator.img_creator.py",
        "methods/img_validation.py",
        "gui/menu.py"
    ]
    
    missing_required = []
    found_optional = []
    
    # Check required files
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"Found {file_path}")
        else:
            print(f"Error {file_path} (required)")
            missing_required.append(file_path)
    
    # Check optional files
    for file_path in optional_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"Found {file_path}")
            found_optional.append(file_path)
        else:
            print(f"Warn {file_path} (optional)")
    
    # Check directories
    directories = ["components", "methods", "locale", "themes", "debug", "utils", "core", "gui"]

    for dir_name in directories:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.glob("*.py")))
            print(f"Found {dir_name}/ ({file_count} Python files)")
        else:
            print(f"Error {dir_name}/ (missing directory)")
    
    if not missing_required:
        print("Project structure OK")
        return True, found_optional
    else:
        print(f"Missing required files: {missing_required}")
        return False, missing_required

def setup_python_path():
    """Setup Python import paths"""
    print("🛠️  Setting up Python paths...")
    
    current_dir = Path(__file__).parent
    paths_to_add = [
        current_dir,
        current_dir / "components",
        current_dir / "methods",
        current_dir / "locale",
        current_dir / "themes",
        current_dir / "debug",
        current_dir / "utils",
        current_dir / "core",
        current_dir / "gui"
    ]
    
    for path in paths_to_add:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
            print(f"Added {path}")
        elif str(path) in sys.path:
            print(f"Already in path: {path}")
        else:
            print(f"Skipped missing: {path}")

def install_missing_dependencies(missing: List[str]) -> bool:
    """Attempt to install missing dependencies"""
    print("Attempting to install missing dependencies...")
    
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
        print("No packages to install")
        return False
    
    for package in unique_packages:
        print(f"Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f" {package} installed successfully")
            else:
                print(f" {package} installation failed")
                print(f"Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f" {package} installation timed out")
            return False
        except Exception as e:
            print(f" {package} installation error: {e}")
            return False
    
    print("All packages installed successfully")
    return True

def launch_application() -> int:
    """Launch the main application"""
    print("Launching IMG Factory...")
    
    try:
        # Try to import the main module
        import imgfactory
        print("Main module imported successfully")
        
        # Check if main function exists
        if hasattr(imgfactory, 'main'):
            print("Using main() function")
            return imgfactory.main()
        else:
            print("Creating application directly")
            
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
                        print("Settings system not available, using defaults")
                        settings = None
            
            window = imgfactory.IMGFactory(settings)
            window.show()
            
            print("IMG Factory started successfully")
            return app.exec()
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("This usually means missing dependencies or file structure issues")
        return 1
    except Exception as e:
        print(f"Launch error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return 1

def show_help():
    """Show help information"""
    print("Troubleshooting Help:")
    print("─" * 40)
    print("If IMG Factory won't start:")
    print("1. Ensure Python 3.8+ is installed")
    print("2. Install PyQt6: pip install PyQt6")
    print("3. Check all files are in the correct locations")
    print("4. Try running: python -m pip install --upgrade PyQt6")
    print("5. Run with verbose output: python -v imgfactory.py")
    print("For support: Check project documentation")
    print("Report bugs: Include the full error output above")

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
        print(f"Attempting to install missing dependencies...")
        if install_missing_dependencies(missing_deps):
            print("Dependencies installed, please restart the launcher")
            return 0
        else:
            print("Failed to install dependencies")
            print("Manual installation:")
            print("pip install PyQt6")
            show_help()
            return 1
    
    print()
    
    # Step 3: Check project structure  
    structure_ok, found_files = check_project_structure()
    if not structure_ok:
        print("Project structure issues detected")
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
        print("IMG Factory closed normally")
    else:
        print(f"IMG Factory exited with error code: {exit_code}")
        show_help()
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("Cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Unexpected launcher error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        show_help()
        sys.exit(1)
