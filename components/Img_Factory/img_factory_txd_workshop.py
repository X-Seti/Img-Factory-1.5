#this belongs in components/Img_Factory/img_factory_txd_workshop.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - TXD Workshop Methods

"""
TXD Workshop Methods
Handles TXD texture editor workshop creation, management, and integration
"""

from typing import Optional
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# _handle_txd_overlay_tab_switch
# _on_workshop_closed
# _open_txd_workshop
# _update_workshop_on_tab_change
# open_txd_workshop_docked
# setup_unified_signals


def open_txd_workshop_docked(self, txd_name=None, txd_data=None): #vers 3
    """Open TXD Workshop as overlay on file window"""
    from components.Txd_Editor.txd_workshop import TXDWorkshop

    # Get current tab
    current_tab_index = self.main_tab_widget.currentIndex()
    if current_tab_index < 0:
        self.log_message("No active tab")
        return None

    current_tab = self.main_tab_widget.widget(current_tab_index)
    if not current_tab:
        return None

    # Find the file list table to get its geometry
    from PyQt6.QtWidgets import QTableWidget
    tables = current_tab.findChildren(QTableWidget)

    if not tables:
        self.log_message("No table found to overlay")
        return None

    file_table = tables[0]

    # Create TXD Workshop as frameless overlay
    workshop = TXDWorkshop(parent=self, main_window=self)

    # Make it frameless overlay
    workshop.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)

    # Load TXD data if provided
    if txd_name and txd_data:
        workshop._load_txd_textures(txd_data, txd_name)

    # Get file table geometry in global coordinates
    table_rect = file_table.geometry()
    table_global_pos = file_table.mapToGlobal(table_rect.topLeft())

    # Position workshop over the file table
    workshop.setGeometry(
        table_global_pos.x(),
        table_global_pos.y(),
        table_rect.width(),
        table_rect.height()
    )

    # Store references for show/hide
    workshop.overlay_table = file_table
    workshop.overlay_tab_index = current_tab_index
    workshop.is_overlay = True

    # Show the workshop
    workshop.show()
    workshop.raise_()

    # Store in main window
    if not hasattr(self, 'txd_workshops'):
        self.txd_workshops = []
    self.txd_workshops.append(workshop)

    # Connect tab switching to hide/show
    self.main_tab_widget.currentChanged.connect(
        lambda idx: self._handle_txd_overlay_tab_switch(workshop, idx)
    )

    self.log_message("TXD Workshop opened as overlay")

    return workshop


def _handle_txd_overlay_tab_switch(self, workshop, new_tab_index): #vers 1
    """Handle hiding/showing TXD Workshop overlay on tab switch"""
    if not hasattr(workshop, 'is_overlay') or not workshop.is_overlay:
        return

    if new_tab_index == workshop.overlay_tab_index:
        # Switched to TXD's tab - show and raise
        workshop.show()
        workshop.raise_()
        workshop.activateWindow()
    else:
        # Switched away - hide it
        workshop.hide()


def setup_unified_signals(self): #vers 6
    """Setup unified signal handler for all table interactions"""
    from components.unified_signal_handler import connect_table_signals

    # Connect main entries table to unified system
    success = connect_table_signals(
        table_name="main_entries",
        table_widget=self.gui_layout.table,
        parent_instance=self,
        selection_callback=self._unified_selection_handler,
        double_click_callback=self._unified_double_click_handler
    )

    if success:
        self.log_message("Unified signal system connected")
    else:
        self.log_message("Failed to connect unified signals")

    # Connect unified signals to status bar updates
    from components.unified_signal_handler import signal_handler
    signal_handler.status_update_requested.connect(self._update_status_from_signal)


# In core/export.py
from methods.mirror_tab_shared import show_mirror_tab_selection

def export_selected_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'export')
    if selected_tab:
        start_export_operation(main_window, selected_tab, options)

# In core/import.py
def import_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'import')
    if selected_tab and options.get('import_files'):
        start_import_operation(main_window, selected_tab, options)

# In core/remove.py
def remove_selected_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'remove')
    if selected_tab:
        start_remove_operation(main_window, selected_tab, options)

# In core/dump.py
def dump_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'dump')
    if selected_tab:
        start_dump_operation(main_window, selected_tab, options)

def split_via_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'split_via')
    if selected_tab:
        split_method = options.get('split_method', 'size')  # 'size' or 'count'
        split_value = options.get('split_value', 50)
        start_split_operation(main_window, selected_tab, split_method, split_value)

def debug_img_entries(self): #vers 4
    """Debug function to check what entries are actually loaded"""
    if not self.current_img or not self.current_img.entries:
        self.log_message("❌ No IMG loaded or no entries found")
        return

    self.log_message(f"🔍 DEBUG: IMG file has {len(self.current_img.entries)} entries")

    # Count file types
    file_types = {}
    all_extensions = set()

    for i, entry in enumerate(self.current_img.entries):
        # Debug each entry
        self.log_message(f"Entry {i}: {entry.name}")

        # Extract extension both ways
        name_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
        attr_ext = getattr(entry, 'extension', 'NO_ATTR').upper() if hasattr(entry, 'extension') and entry.extension else "NO_ATTR"

        all_extensions.add(name_ext)

        # Count by name-based extension
        file_types[name_ext] = file_types.get(name_ext, 0) + 1

        # Log extension differences
        if name_ext != attr_ext:
            self.log_message(f"Extension mismatch: name='{name_ext}' vs attr='{attr_ext}'")

    # Summary
    self.log_message(f"File type summary:")
    for ext, count in sorted(file_types.items()):
        self.log_message(f"  {ext}: {count} files")

    self.log_message(f"All extensions found: {sorted(all_extensions)}")

    # Check table row count vs entries count
    table_rows = self.gui_layout.table.rowCount()
    self.log_message(f"Table has {table_rows} rows, IMG has {len(self.current_img.entries)} entries")

    # Check if any rows are hidden
    hidden_count = 0
    for row in range(table_rows):
        if self.gui_layout.table.isRowHidden(row):
            hidden_count += 1

    self.log_message(f"Hidden rows: {hidden_count}")

    if hidden_count > 0:
        self.log_message("Some rows are hidden! Check the filter settings.")


def _unified_double_click_handler(self, row, filename, item): #vers 2
    """Handle double-click through unified system"""
    # Get the actual filename from the first column (index 0)
    if row < self.gui_layout.table.rowCount():
        name_item = self.gui_layout.table.item(row, 0)
        if name_item:
            actual_filename = name_item.text()
            self.log_message(f"Double-clicked: {actual_filename}")

            # Show file info if IMG is loaded
            if self.current_img and row < len(self.current_img.entries):
                entry = self.current_img.entries[row]
                from methods.img_core_classes import format_file_size
                self.log_message(f"File info: {entry.name} ({format_file_size(entry.size)})")
        else:
            self.log_message(f"Double-clicked row {row} (no filename found)")
    else:
        self.log_message(f"Double-clicked: {filename}")


def _unified_selection_handler(self, selected_rows, selection_count): #vers 1
    """Handle selection changes through unified system"""
    # Update button states based on selection
    has_selection = selection_count > 0
    self._update_button_states(has_selection)

    # Log selection (unified approach - no spam)
    if selection_count == 0:
        # Don't log "Ready" for empty selection to reduce noise
        pass
    elif selection_count == 1:
        # Get filename of selected item
        if selected_rows and len(selected_rows) > 0:
            row = selected_rows[0]
            if row < self.gui_layout.table.rowCount():
                name_item = self.gui_layout.table.item(row, 0)
                if name_item:
                    self.log_message(f"Selected: {name_item.text()}")


__all__ = [
    'open_txd_workshop_docked',
    '_handle_txd_overlay_tab_switch',
    'setup_unified_signals',
    '_open_txd_workshop',
    '_update_workshop_on_tab_change',
    '_on_workshop_closed'
]
