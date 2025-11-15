#this belongs in debug.col_debug_functions.py - Version: 1
# X-Seti - July17 2025 - IMG Factory 1.5 - COL Debug Functions
# Uses IMG debug system for COL operations

"""
COL Debug Functions - Using IMG Debug System
Provides comprehensive debugging and tracing for COL operations
"""

import os
import sys
import traceback
import inspect
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

# Import the proven IMG debug system
from apps.debug.img_debug_functions import img_debugger
from apps.debug.unified_debug_functions import debug_trace

##Methods list -
# col_debug_log
# debug_col_creation_process
# debug_col_import_errors
# debug_col_loading_process
# debug_col_model_parsing
# debug_col_threading
# is_col_debug_enabled
# set_col_debug_enabled
# trace_col_function

# Global debug state for COL operations
_col_debug_enabled = False


def set_col_debug_enabled(enabled: bool):
    """Enable/disable COL debug output using IMG debug system"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    
    if enabled:
        img_debugger.debug("COL debug system ENABLED")
    else:
        img_debugger.debug("COL debug system DISABLED for performance")

def is_col_debug_enabled() -> bool:
    """Check if COL debug is enabled"""
    global _col_debug_enabled
    return _col_debug_enabled and img_debugger.debug_enabled

def col_debug_log(main_window, message: str, category: str = 'COL_GENERAL', level: str = 'INFO'):
    """Log COL debug message using IMG debug system"""
    if not is_col_debug_enabled():
        return  # Skip for performance
    
    # Use IMG debugger with COL prefix
    prefixed_message = f"[COL-{category}] {message}"
    
    if level == 'ERROR':
        img_debugger.error(prefixed_message)
    elif level == 'WARNING':
        img_debugger.warning(prefixed_message)
    elif level == 'SUCCESS':
        img_debugger.success(prefixed_message)
    else:
        img_debugger.debug(prefixed_message)
    
    # Also log to main window if available
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"[{category}] {message}")
    except:
        pass

def debug_col_creation_process(col_creator_dialog):
    """Debug the COL creation process from dialog using IMG debug system"""
    if not is_col_debug_enabled():
        return
        
    img_debugger.debug("=== DEBUGGING COL CREATION PROCESS ===")
    
    # Debug dialog state
    img_debugger.inspect_object(col_creator_dialog, "NewCOLDialog")
    
    # Check if dialog has the necessary components
    required_attrs = ['filename_input', 'output_path', 'selected_col_version']
    for attr in required_attrs:
        if hasattr(col_creator_dialog, attr):
            value = getattr(col_creator_dialog, attr)
            img_debugger.success(f"✓ Dialog has {attr}: {repr(value)}")
        else:
            img_debugger.error(f"✗ Dialog missing {attr}")

def debug_col_import_errors():
    """Debug COL component import issues using IMG debug system"""
    if not is_col_debug_enabled():
        return
        
    img_debugger.debug("=== DEBUGGING COL IMPORT ERRORS ===")
    
    components_to_check = [
        'methods.col_core_classes',
        'components.Col_Creator.col_creator', 
        'methods.col_validation',
        'methods.col_parsing_functions',
        'components.col_display'
    ]
    
    for component in components_to_check:
        try:
            __import__(component)
            img_debugger.success(f"✓ {component} imported successfully")
        except ImportError as e:
            img_debugger.error(f"✗ Failed to import {component}: {e}")
        except Exception as e:
            img_debugger.error(f"✗ Error importing {component}: {e}")

def debug_col_loading_process(col_file_obj: Any, **params):
    """Debug COL file loading process using IMG debug system"""
    if not is_col_debug_enabled():
        return
        
    img_debugger.debug("=== COL LOADING DEBUG START ===")
    
    # Inspect the COL file object
    img_debugger.inspect_object(col_file_obj, "COLFile")
    
    # Debug loading parameters
    img_debugger.debug("Loading parameters:")
    for key, value in params.items():
        img_debugger.debug(f"  {key} = {repr(value)}")
    
    # Check if load method exists
    if hasattr(col_file_obj, 'load'):
        img_debugger.success("✓ load method found")
        
        # Get method signature
        try:
            sig = inspect.signature(col_file_obj.load)
            img_debugger.debug(f"Method signature: load{sig}")
        except:
            img_debugger.warning("Could not get method signature")
    else:
        img_debugger.error("✗ load method NOT found!")
    
    # Check file path
    file_path = params.get('file_path') or getattr(col_file_obj, 'file_path', None)
    if file_path:
        img_debugger.check_file_operations(file_path, "read")
    
    img_debugger.debug("=== COL LOADING DEBUG END ===")

def debug_col_model_parsing(col_model_obj: Any, model_index: int = 0):
    """Debug COL model parsing using IMG debug system"""
    if not is_col_debug_enabled():
        return
        
    img_debugger.debug(f"=== COL MODEL {model_index} PARSING DEBUG ===")
    
    # Inspect model object
    img_debugger.inspect_object(col_model_obj, f"COLModel_{model_index}")
    
    # Check common model attributes
    model_attrs = ['name', 'version', 'spheres', 'boxes', 'vertices', 'faces']
    for attr in model_attrs:
        if hasattr(col_model_obj, attr):
            value = getattr(col_model_obj, attr)
            if isinstance(value, list):
                img_debugger.debug(f"  {attr}: {len(value)} items")
            else:
                img_debugger.debug(f"  {attr}: {repr(value)}")
        else:
            img_debugger.warning(f"  Missing attribute: {attr}")
    
    img_debugger.debug(f"=== COL MODEL {model_index} DEBUG END ===")

def debug_col_threading(thread_obj: Any, operation: str = "unknown"):
    """Debug COL threading operations using IMG debug system"""
    if not is_col_debug_enabled():
        return
        
    img_debugger.debug(f"=== COL THREADING DEBUG: {operation.upper()} ===")
    
    # Inspect thread object
    img_debugger.inspect_object(thread_obj, f"COLThread_{operation}")
    
    # Check thread state
    if hasattr(thread_obj, 'isRunning'):
        img_debugger.debug(f"Thread running: {thread_obj.isRunning()}")
    
    if hasattr(thread_obj, 'isFinished'):
        img_debugger.debug(f"Thread finished: {thread_obj.isFinished()}")
    
    img_debugger.debug(f"=== COL THREADING DEBUG END ===")

def trace_col_function(func):
    """Decorator to trace COL function calls using IMG debug system"""
    def wrapper(*args, **kwargs):
        if is_col_debug_enabled() and img_debugger.trace_calls:
            start_time = time.time()
            
            # Log call with COL prefix
            img_debugger.debug(f"COL CALL: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                img_debugger.debug(f"COL RESULT: {func.__name__} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                img_debugger.error(f"COL ERROR in {func.__name__}: {e}")
                raise
        else:
            return func(*args, **kwargs)
    
    return wrapper

# Convenience functions for integration
def enable_col_debug():
    """Enable COL debug output"""
    set_col_debug_enabled(True)

def disable_col_debug():
    """Disable COL debug output for performance"""
    set_col_debug_enabled(False)

def toggle_col_debug():
    """Toggle COL debug state"""
    current = is_col_debug_enabled()
    set_col_debug_enabled(not current)
    return not current

# Integration function for main window
def integrate_col_debug_with_main_window(main_window):
    """Integrate COL debug functions into main window"""
    try:
        # Add methods to main window
        main_window.enable_col_debug = enable_col_debug
        main_window.disable_col_debug = disable_col_debug
        main_window.toggle_col_debug = toggle_col_debug
        main_window.is_col_debug_enabled = is_col_debug_enabled
        
        # Start with debug disabled for performance
        disable_col_debug()
        
        col_debug_log(main_window, "COL debug functions integrated with IMG debug system", 'COL_INTEGRATION', 'SUCCESS')
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL debug integration error: {e}")
        else:
            print(f"❌ COL debug integration error: {e}")
        return False

# Export main functions
__all__ = [
    'col_debug_log',
    'debug_col_creation_process',
    'debug_col_import_errors', 
    'debug_col_loading_process',
    'debug_col_model_parsing',
    'debug_col_threading',
    'is_col_debug_enabled',
    'set_col_debug_enabled',
    'trace_col_function',
    'enable_col_debug',
    'disable_col_debug',
    'toggle_col_debug',
    'integrate_col_debug_with_main_window'
]
