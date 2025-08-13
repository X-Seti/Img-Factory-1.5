#this belongs in core/col_integration.py - Version: 1
# X-Seti - August13 2025 - IMG Factory 1.5 - Complete COL Integration

"""
Complete COL Integration - Integrates all COL functionality into IMG Factory
Connects all COL components, methods, and GUI elements
"""

from components.img_debug_functions import img_debugger

##Methods list -
# integrate_complete_col_system
# integrate_col_context_menus
# integrate_col_dialogs
# integrate_col_editor
# integrate_col_methods
# setup_col_file_loading
# verify_col_components

def verify_col_components() -> bool: #vers 1
    """Verify all COL components are available"""
    missing_components = []
    
    try:
        from components.col_core_classes import COLFile, COLModel
        img_debugger.debug("✅ COL core classes available")
    except ImportError:
        missing_components.append("components.col_core_classes")
    
    try:
        from components.col_editor import COLEditorDialog
        img_debugger.debug("✅ COL editor available")
    except ImportError:
        missing_components.append("components.col_editor")
    
    try:
        from components.col_utilities import COLBatchProcessor
        img_debugger.debug("✅ COL utilities available")
    except ImportError:
        missing_components.append("components.col_utilities")
    
    try:
        from components.col_validator import COLValidator
        img_debugger.debug("✅ COL validator available")
    except ImportError:
        missing_components.append("components.col_validator")
    
    try:
        from methods.col_operations import extract_col_from_img_entry
        img_debugger.debug("✅ COL operations methods available")
    except ImportError:
        missing_components.append("methods.col_operations")
    
    try:
        from gui.col_dialogs import show_col_analysis_dialog
        img_debugger.debug("✅ COL GUI dialogs available")
    except ImportError:
        missing_components.append("gui.col_dialogs")
    
    if missing_components:
        img_debugger.error(f"Missing COL components: {', '.join(missing_components)}")
        return False
    
    img_debugger.success("All COL components verified")
    return True

def integrate_col_methods(main_window) -> bool: #vers 1
    """Integrate COL methods into main window"""
    try:
        # Add COL file loading capability
        if not hasattr(main_window, 'load_col_file_safely'):
            from methods.populate_col_table import load_col_file_safely
            main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
            img_debugger.debug("✅ COL file loading method added")
        
        # Add COL operations methods
        from methods.col_operations import (
            extract_col_from_img_entry, 
            get_col_basic_info, 
            get_col_detailed_analysis
        )
        
        main_window.extract_col_from_img_entry = lambda row: extract_col_from_img_entry(main_window, row)
        main_window.get_col_basic_info = get_col_basic_info
        main_window.get_col_detailed_analysis = get_col_detailed_analysis
        
        img_debugger.debug("✅ COL operations methods integrated")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error integrating COL methods: {str(e)}")
        return False

def integrate_col_context_menus(main_window) -> bool: #vers 1
    """Integrate COL context menus"""
    try:
        from gui.gui_context import add_col_context_menu_to_entries_table
        
        # Add enhanced context menu with COL support
        success = add_col_context_menu_to_entries_table(main_window)
        
        if success:
            img_debugger.success("✅ COL context menus integrated")
        else:
            img_debugger.warning("⚠️ COL context menu integration failed")
        
        return success
        
    except Exception as e:
        img_debugger.error(f"Error integrating COL context menus: {str(e)}")
        return False

def integrate_col_editor(main_window) -> bool: #vers 1
    """Integrate COL editor functionality"""
    try:
        from components.col_editor import open_col_editor
        
        # Add COL editor methods to main window
        main_window.open_col_editor = lambda file_path=None: open_col_editor(main_window, file_path)
        
        # Add method for editing COL from IMG entry
        from gui.gui_context import edit_col_from_img_entry
        main_window.edit_col_from_img_entry = lambda row: edit_col_from_img_entry(main_window, row)
        
        img_debugger.debug("✅ COL editor integrated")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error integrating COL editor: {str(e)}")
        return False

def integrate_col_dialogs(main_window) -> bool: #vers 1
    """Integrate COL dialog functionality"""
    try:
        from gui.gui_context import (
            open_col_editor_dialog,
            open_col_batch_proc_dialog, 
            open_col_file_dialog,
            analyze_col_file_dialog
        )
        
        # Add dialog methods to main window
        main_window.open_col_editor_dialog = lambda: open_col_editor_dialog(main_window)
        main_window.open_col_batch_proc_dialog = lambda: open_col_batch_proc_dialog(main_window)
        main_window.open_col_file_dialog = lambda: open_col_file_dialog(main_window)
        main_window.analyze_col_file_dialog = lambda: analyze_col_file_dialog(main_window)
        
        img_debugger.debug("✅ COL dialogs integrated")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error integrating COL dialogs: {str(e)}")
        return False

def setup_col_file_loading(main_window) -> bool: #vers 1
    """Setup COL file loading in IMG system"""
    try:
        # Integrate COL file detection in IMG loading
        from components.col_integration_main import integrate_complete_col_system
        
        success = integrate_complete_col_system(main_window)
        
        if success:
            img_debugger.debug("✅ COL file loading integrated")
        else:
            img_debugger.warning("⚠️ COL file loading integration failed")
        
        return success
        
    except Exception as e:
        img_debugger.error(f"Error setting up COL file loading: {str(e)}")
        return False

def integrate_complete_col_system(main_window) -> bool: #vers 1
    """Integrate complete COL system into IMG Factory"""
    try:
        img_debugger.info("🔧 Starting complete COL system integration...")
        
        # Step 1: Verify all components are available
        if not verify_col_components():
            img_debugger.error("❌ COL component verification failed")
            return False
        
        # Step 2: Integrate core methods
        methods_success = integrate_col_methods(main_window)
        
        # Step 3: Integrate context menus
        context_success = integrate_col_context_menus(main_window)
        
        # Step 4: Integrate editor functionality
        editor_success = integrate_col_editor(main_window)
        
        # Step 5: Integrate dialogs
        dialogs_success = integrate_col_dialogs(main_window)
        
        # Step 6: Setup file loading
        loading_success = setup_col_file_loading(main_window)
        
        # Check overall success
        all_success = all([
            methods_success,
            context_success, 
            editor_success,
            dialogs_success,
            loading_success
        ])
        
        if all_success:
            img_debugger.success("🎉 Complete COL system integration successful!")
            main_window.log_message("🔧 COL collision system fully integrated")
            
            # Add summary of available COL features
            main_window.log_message("📋 Available COL features:")
            main_window.log_message("  • Right-click COL files in IMG table for context menu")
            main_window.log_message("  • COL Editor with 3D visualization")
            main_window.log_message("  • COL Batch Processor for multiple files")
            main_window.log_message("  • COL file analysis and validation")
            main_window.log_message("  • Direct COL file loading and viewing")
            
        else:
            img_debugger.warning("⚠️ COL system integration completed with some failures")
            main_window.log_message("⚠️ COL system integrated with limited functionality")
        
        return all_success
        
    except Exception as e:
        img_debugger.error(f"Complete COL system integration failed: {str(e)}")
        main_window.log_message(f"❌ COL system integration error: {str(e)}")
        return False

# Export functions
__all__ = [
    'integrate_complete_col_system',
    'integrate_col_context_menus',
    'integrate_col_dialogs', 
    'integrate_col_editor',
    'integrate_col_methods',
    'setup_col_file_loading',
    'verify_col_components'
]