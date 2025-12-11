
#!/usr/bin/env python3
# Quick test to verify right-click menu has all copy functions

import sys
sys.path.insert(0, '/path/to/imgfactory/apps')

# Check if all copy functions exist in right_click_actions
from apps.core.right_click_actions import (
    copy_table_cell,
    copy_table_row,
    copy_table_row_as_lines,
    copy_table_column_data,
    copy_table_selection,
    copy_filename_only,
    copy_file_summary
)

print("✓ All copy functions imported successfully!")
print("\nAvailable copy functions:")
print("  • copy_table_cell")
print("  • copy_table_row")
print("  • copy_table_row_as_lines")
print("  • copy_table_column_data")
print("  • copy_table_selection")
print("  • copy_filename_only")
print("  • copy_file_summary")
