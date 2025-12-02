#!/usr/bin/env python3
"""
Script to fix the select_inverse function in gui_layout.py
"""

def fix_select_inverse():
    # Read the file
    with open('/workspace/apps/gui/gui_layout.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the select_inverse function and replace it
    new_lines = []
    i = 0
    while i < len(lines):
        if 'def select_inverse(self):' in lines[i] and '# vers' in lines[i]:
            # Found the function, skip the old version and add the new one
            # First, find where the function ends by counting indentation
            new_lines.append('    def select_inverse(self):  # vers 3\n')
            new_lines.append('        """Invert the current selection in the table"""\n')
            new_lines.append('        try:\n')
            new_lines.append('            if self.table:\n')
            new_lines.append('                # Get the selection model\n')
            new_lines.append('                selection_model = self.table.selectionModel()\n')
            new_lines.append('                if selection_model:\n')
            new_lines.append('                    # Store currently selected rows (only consider row level, not individual cells)\n')
            new_lines.append('                    currently_selected_rows = set()\n')
            new_lines.append('                    for index in selection_model.selectedIndexes():\n')
            new_lines.append('                        currently_selected_rows.add(index.row())\n')
            new_lines.append('                    \n')
            new_lines.append('                    # Clear current selection\n')
            new_lines.append('                    self.table.clearSelection()\n')
            new_lines.append('                    \n')
            new_lines.append('                    # Select all rows that were NOT selected, and deselect those that were\n')
            new_lines.append('                    for row in range(self.table.rowCount()):\n')
            new_lines.append('                        if row in currently_selected_rows:\n')
            new_lines.append('                            # Leave deselected (these were originally selected)\n')
            new_lines.append('                            pass\n')
            new_lines.append('                        else:\n')
            new_lines.append('                            # Select this row (these were originally NOT selected)\n')
            new_lines.append('                            for col in range(self.table.columnCount()):\n')
            new_lines.append('                                index = self.table.model().index(row, col)\n')
            new_lines.append('                                selection_model.select(index, QAbstractItemView.SelectionFlag.Select)\n')
            new_lines.append('                else:\n')
            new_lines.append('                    # Fallback method if selection model is not available\n')
            new_lines.append('                    # Get all items in the table\n')
            new_lines.append('                    all_items = []\n')
            new_lines.append('                    for row in range(self.table.rowCount()):\n')
            new_lines.append('                        for col in range(self.table.columnCount()):\n')
            new_lines.append('                            item = self.table.item(row, col)\n')
            new_lines.append('                            if item:\n')
            new_lines.append('                                all_items.append(item)\n')
            new_lines.append('\n')
            new_lines.append('                    # Store currently selected items\n')
            new_lines.append('                    currently_selected = set(self.table.selectedItems())\n')
            new_lines.append('\n')
            new_lines.append('                    # Clear selection\n')
            new_lines.append('                    self.table.clearSelection()\n')
            new_lines.append('\n')
            new_lines.append('                    # Select items that were not selected\n')
            new_lines.append('                    for item in all_items:\n')
            new_lines.append('                        if item not in currently_selected:\n')
            new_lines.append('                            item.setSelected(True)\n')
            new_lines.append('\n')
            new_lines.append('                if hasattr(self.main_window, \'log_message\'):\n')
            new_lines.append('                    self.main_window.log_message("✅ Selection inverted")\n')
            new_lines.append('            else:\n')
            new_lines.append('                if hasattr(self.main_window, \'log_message\'):\n')
            new_lines.append('                    self.main_window.log_message("❌ Table not available for selection")\n')
            new_lines.append('        except Exception as e:\n')
            new_lines.append('            if hasattr(self.main_window, \'log_message\'):\n')
            new_lines.append('                self.main_window.log_message(f"❌ Select inverse error: {str(e)}")\n')
            
            # Skip the old function body
            i += 1  # Skip the def line
            # Skip until we find a line that has less indentation or is the end of the class/function
            while i < len(lines):
                line = lines[i]
                if line.strip() and not line.startswith('    ') and not line.startswith('        '):
                    # This line has less indentation, so we're out of the function
                    break
                i += 1
            continue  # Continue from the current i position
        else:
            new_lines.append(lines[i])
            i += 1
    
    # Write the file back
    with open('/workspace/apps/gui/gui_layout.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    fix_select_inverse()
    print("select_inverse function updated successfully!")