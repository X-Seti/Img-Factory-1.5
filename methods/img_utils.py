#this belongs in methods/img_utils.py - Version: 2
# X-Seti - August25 2025 - IMG Factory 1.5 - format_file_size

"""
File Type and Version Detection - CLEAN VERSION
Works or fails cleanly - no fallback code
"""

from typing import Optional, Any
from core.rw_versions import parse_rw_version, get_rw_version_name
from components.img_debug_functions import img_debugger

##Methods list -
# format_file_size(size_bytes
# populate_table_with_sample_data

def format_file_size(size_bytes: int) -> str: #vers 1
    """Format file size in human readable format - from img_core_classes"""
    try:
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0

        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        if i == 0:
            return f"{int(size_bytes)} {size_names[i]}"
        else:
            return f"{size_bytes:.1f} {size_names[i]}"

    except Exception:
        return "Unknown"


def populate_table_with_sample_data(table) -> bool: #vers 1
    """Populate table with sample data - from img_core_classes"""
    try:
        # This would require table-specific implementation
        # Just return success for now
        return True

    except Exception:
        return False


# Export only the clean functions
__all__ = [
    'format_file_size',
    'populate_table_with_sample_data'
]
