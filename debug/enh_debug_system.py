#this belongs in components/enh_debug_system.py - Version: 1
# X-Seti - July22 2025 - IMG Factory 1.5 - Debug

"""
Enhanced Debug Error - Shows exact file and line where format_file_size error occurs
"""

import sys
import traceback
import linecache
from debug.img_debug_functions import img_debugger

def enhanced_error_handler(exc_type, exc_value, exc_traceback): #vers 1
    """Enhanced error handler showing exact file and line"""
    try:
        # Get the full traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Look for format_file_size specifically
        if "format_file_size" in str(exc_value):
            print("\n🔴 FORMAT_FILE_SIZE ERROR DETECTED:")
            print("=" * 50)
            
            # Find the exact line that caused the error
            tb = exc_traceback
            while tb is not None:
                frame = tb.tb_frame
                filename = frame.f_code.co_filename
                line_number = tb.tb_lineno
                function_name = frame.f_code.co_name
                
                # Get the actual line of code
                line_text = linecache.getline(filename, line_number).strip()
                
                if "format_file_size" in line_text:
                    print(f"📁 FILE: {filename}")
                    print(f"📍 LINE: {line_number}")
                    print(f"🔧 FUNCTION: {function_name}")
                    print(f"💥 CODE: {line_text}")
                    print(f"❌ ERROR: {exc_value}")
                    print("=" * 50)
                    break
                    
                tb = tb.tb_next
        
        # Show full traceback for all errors
        print("\n🔍 FULL TRACEBACK:")
        for line in tb_lines:
            print(line.rstrip())
            
    except Exception as e:
        print(f"Error in enhanced error handler: {e}")
        # Fallback to default handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

def install_enhanced_debug(main_window): #vers 1
    """Install enhanced debug error handler"""
    try:
        # Install the enhanced error handler
        sys.excepthook = enhanced_error_handler
        
        # Also patch img_debugger for more file info
        original_error = img_debugger.error
        
        def enhanced_img_error(message):
            """Enhanced error with stack trace info"""
            # Get caller information
            import inspect
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            line_number = frame.f_lineno
            function_name = frame.f_code.co_name
            
            enhanced_message = f"{message}\n   📁 {filename}:{line_number} in {function_name}()"
            original_error(enhanced_message)
        
        img_debugger.error = enhanced_img_error
        
        main_window.log_message("✅ Enhanced debug error handler installed")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to install enhanced debug: {e}")
        return False

# Quick integration function
def integrate_enhanced_debug_error(main_window): #vers 1
    """Quick integration for enhanced error debugging"""
    return install_enhanced_debug(main_window)
