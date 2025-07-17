#this belongs in components/ col_validator.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - COL Validation Functions

"""
COL Validation Functions
Handles validation of COL files before loading
"""

import os


def validate_col_file(main_window, file_path):
    """Validate COL file before loading"""
    if not os.path.exists(file_path):
        main_window.log_message(f"❌ COL file not found: {file_path}")
        return False
    
    if not os.access(file_path, os.R_OK):
        main_window.log_message(f"❌ Cannot read COL file: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size < 32:
        main_window.log_message(f"❌ COL file too small ({file_size} bytes)")
        return False
    
    return True


def validate_col_file_structure(file_path):
    """Validate COL file structure and format"""
    try:
        with open(file_path, 'rb') as f:
            # Read first 4 bytes to check for COL format identifier
            header = f.read(4)
            
            # Check for common COL format signatures
            if len(header) < 4:
                return False, "File too small to be valid COL"
            
            # COL files typically start with specific patterns
            # This is a basic check - more sophisticated validation could be added
            if header == b'COL\x00' or header[:3] == b'COL':
                return True, "Valid COL format detected"
            
            # Check for numeric header (version indicators)
            try:
                version = int.from_bytes(header, 'little')
                if 1 <= version <= 4:  # COL versions 1-4
                    return True, f"COL version {version} detected"
            except:
                pass
            
            return False, "Unknown COL format"
            
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def validate_col_file_complete(main_window, file_path):
    """Complete COL file validation with detailed checks"""
    try:
        # Basic file checks
        if not validate_col_file(main_window, file_path):
            return False
        
        # Structure validation
        is_valid, message = validate_col_file_structure(file_path)
        
        if is_valid:
            main_window.log_message(f"✅ COL validation passed: {message}")
            return True
        else:
            main_window.log_message(f"❌ COL validation failed: {message}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ COL validation error: {str(e)}")
        return False


# Export functions
__all__ = [
    'validate_col_file',
    'validate_col_file_structure', 
    'validate_col_file_complete'
]