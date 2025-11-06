#this belongs in components/Img_Factory/img_factory_img_operations.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - IMG Operations Methods

"""
IMG Operations Methods
Handles IMG file loading completion, table population, and IMG-specific operations
"""

from typing import Optional
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from apps.methods.svg_shared_icons import get_img_file_icon, get_success_icon
from apps.methods.img_core_classes import IMGFile
from apps.methods.col_core_classes import COLFile
import os

##Methods list -
# _on_img_loaded
# _on_load_error
# _on_load_progress
# _populate_real_img_table
# close_all_img
# format_file_size
# get_entry_rw_version


def _on_load_progress(self, progress: int, status: str): #vers 4
    """Handle loading progress updates"""
    if hasattr(self.gui_layout, 'show_progress'):
        self.gui_layout.show_progress(progress, status)
    else:
        self.log_message(f"Progress: {progress}% - {status}")



def get_entry_rw_version(self, entry, extension): #vers 3
    """Detect RW version from entry file data"""
    try:
        # Skip non-RW files
        if extension not in ['DFF', 'TXD']:
            return "Unknown"

        # Check if entry already has version info
        if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
            return entry.get_version_text()

        # Try to get file data using different methods
        file_data = None

        # Method 1: Direct data access
        if hasattr(entry, 'get_data'):
            try:
                file_data = entry.get_data()
            except:
                pass

        # Method 2: Extract data method
        if not file_data and hasattr(entry, 'extract_data'):
            try:
                file_data = entry.extract_data()
            except:
                pass

        # Method 3: Read directly from IMG file
        if not file_data:
            try:
                if (hasattr(self, 'current_img') and
                    hasattr(entry, 'offset') and
                    hasattr(entry, 'size') and
                    self.current_img and
                    self.current_img.file_path):

                    with open(self.current_img.file_path, 'rb') as f:
                        f.seek(entry.offset)
                        # Only read the header (12 bytes) for efficiency
                        file_data = f.read(min(entry.size, 12))
            except Exception as e:
                print(f"DEBUG: Failed to read file data for {entry.name}: {e}")
                return "Unknown"

        # Parse RW version from file header
        if file_data and len(file_data) >= 12:
            import struct
            try:
                # RW version is stored at offset 8-12 in RW files
                rw_version = struct.unpack('<I', file_data[8:12])[0]

                if rw_version > 0:
                    version_name = get_rw_version_name(rw_version)
                    print(f"DEBUG: Found RW version 0x{rw_version:X} ({version_name}) for {entry.name}")
                    return f"RW {version_name}"
                else:
                    print(f"DEBUG: Invalid RW version (0) for {entry.name}")
                    return "Unknown"

            except struct.error as e:
                print(f"DEBUG: Struct unpack error for {entry.name}: {e}")
                return "Unknown"
        else:
            print(f"DEBUG: Insufficient file data for {entry.name} (need 12 bytes, got {len(file_data) if file_data else 0})")
            return "Unknown"

    except Exception as e:
        print(f"DEBUG: RW version detection error for {entry.name}: {e}")
        return "Unknown"


def format_file_size(size_bytes): #vers 2 #Restore
    """Format file size same as IMG entries"""
    try:
        # Use the same formatting as IMG entries
        try:
            from methods.img_core_classes import format_file_size
            return format_file_size(size_bytes)
        except:
            pass

        # Fallback formatting (same logic as IMG)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes // (1024 * 1024)} MB"
        else:
            return f"{size_bytes // (1024 * 1024 * 1024)} GB"

    except Exception:
        return f"{size_bytes} bytes"


def get_col_model_details_for_display(self, model, row_index): #vers 2 #Restore
    """Get COL model details in same format as IMG entry details"""
    try:
        stats = model.get_stats() if hasattr(model, 'get_stats') else {}

        details = {
            'name': getattr(model, 'name', f"Model_{row_index}") if hasattr(model, 'name') and model.name else f"Model_{row_index}",
            'type': "COL",
            'size': self._estimate_col_model_size_bytes(model),
            'version': str(model.version.value) if hasattr(model, 'version') and hasattr(model.version, 'value') else "Unknown",
            'elements': stats.get('total_elements', 0),
            'spheres': stats.get('spheres', 0),
            'boxes': stats.get('boxes', 0),
            'faces': stats.get('faces', 0),
            'vertices': stats.get('vertices', 0),
        }

        if hasattr(model, 'bounding_box') and model.bounding_box:
            bbox = model.bounding_box
            if hasattr(bbox, 'center') and hasattr(bbox, 'radius'):
                details.update({
                    'bbox_center': (bbox.center.x, bbox.center.y, bbox.center.z),
                    'bbox_radius': bbox.radius,
                })
                if hasattr(bbox, 'min') and hasattr(bbox, 'max'):
                    details.update({
                        'bbox_min': (bbox.min.x, bbox.min.y, bbox.min.z),
                        'bbox_max': (bbox.max.x, bbox.max.y, bbox.max.z),
                    })

        return details

    except Exception as e:
        self.log_message(f"Error getting COL model details: {str(e)}")
        return {
            'name': f"Model_{row_index}",
            'type': "COL",
            'size': 0,
            'version': "Unknown",
            'elements': 0,
        }

def show_col_model_details_img_style(self, model_index): #vers 2 #Restore
    """Show COL model details in same style as IMG entry details"""
    try:
        if (not hasattr(self, 'current_col') or
            not hasattr(self.current_col, 'models') or
            model_index >= len(self.current_col.models)):
            return

        model = self.current_col.models[model_index]
        details = self.get_col_model_details_for_display(model, model_index)

        from PyQt6.QtWidgets import QMessageBox

        info_lines = []
        info_lines.append(f"Name: {details['name']}")
        info_lines.append(f"Type: {details['type']}")
        info_lines.append(f"Size: {self._format_file_size(details['size'])}")
        info_lines.append(f"Version: {details['version']}")
        info_lines.append("")
        info_lines.append("Collision Data:")
        info_lines.append(f"  Total Elements: {details['elements']}")
        info_lines.append(f"  Spheres: {details['spheres']}")
        info_lines.append(f"  Boxes: {details['boxes']}")
        info_lines.append(f"  Faces: {details['faces']}")
        info_lines.append(f"  Vertices: {details['vertices']}")

        if 'bbox_center' in details:
            info_lines.append("")
            info_lines.append("Bounding Box:")
            center = details['bbox_center']
            info_lines.append(f"  Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
            info_lines.append(f"  Radius: {details['bbox_radius']:.2f}")

        QMessageBox.information(
            self,
            f"COL Model Details - {details['name']}",
            "\n".join(info_lines)
        )

    except Exception as e:
        self.log_message(f"Error showing COL model details: {str(e)}")


def _on_col_table_double_click(self, item): #vers 2 #Restore
    """Handle double-click on COL table item - IMG style"""
    try:
        if hasattr(self, 'current_col') and hasattr(self.current_col, 'models'):
            row = item.row()
            self.show_col_model_details_img_style(row)
        else:
            self.log_message("No COL models available for details")
    except Exception as e:
        self.log_message(f"Error handling COL table double-click: {str(e)}")

def _on_col_loaded(self, col_file): #vers 1 #Restore
    """Handle COL file loaded - UPDATED with styling"""
    try:
        self.current_col = col_file
        # Store COL file in tab tracking
        current_index = self.main_tab_widget.currentIndex()

        if hasattr(self, 'open_files') and current_index in self.open_files:
            self.open_files[current_index]['file_object'] = col_file
            self.log_message(f"COL file object stored in tab {current_index}")

        # Apply COL tab styling if available
        if hasattr(self, '_apply_individual_col_tab_style'):
            self._apply_individual_col_tab_style(current_index)

        # Update file info in open_files (same as IMG)
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = col_file
            self.log_message(f"Updated tab {current_index} with loaded COL")
        else:
            self.log_message(f"Tab {current_index} not found in open_files") #TODO warning svg icon

        # Apply enhanced COL tab styling after loading
        if hasattr(self, '_apply_individual_col_tab_style'):
            self._apply_individual_col_tab_style(current_index)

        # Update UI for loaded COL
        if hasattr(self, '_update_ui_for_loaded_col'):
            self._update_ui_for_loaded_col()

        # Update window title to show current file
        file_name = os.path.basename(col_file.file_path) if hasattr(col_file, 'file_path') else "Unknown COL"
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        model_count = len(col_file.models) if hasattr(col_file, 'models') and col_file.models else 0
        self.log_message(f"Loaded: {file_name} ({model_count} models)")

        # Hide progress and show COL-specific status
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

    except Exception as e:
        self.log_message(f"Error in _on_col_loaded: {str(e)}")
        if hasattr(self, '_on_col_load_error'):
            self._on_col_load_error(str(e))


def _setup_col_integration_safely(self):
    """Setup COL integration safely"""
    try:
        if COL_SETUP_FUNCTION:
            result = COL_SETUP_FUNCTION(self)
            if result:
                self.log_message("COL functionality integrated")
            else:
                self.log_message("COL integration returned False")
        else:
            self.log_message("COL integration function not available")
    except Exception as e:
        self.log_message(f"COL integration error: {str(e)}")

def _on_load_progress(self, progress: int, status: str): #vers 2 #Restore
    """Handle loading progress updates"""
    if hasattr(self.gui_layout, 'show_progress'):
        self.gui_layout.show_progress(progress, status)
    else:
        self.log_message(f"Progress: {progress}% - {status}")


def _on_img_loaded(self, img_file): #vers 4
    """Handle IMG loading completion"""
    try:
        self.current_img = img_file

        # Store on current tab widget
        current_index = self.main_tab_widget.currentIndex()
        tab_widget = self.main_tab_widget.widget(current_index)
        if tab_widget:
            tab_widget.file_object = img_file
            self.log_message(f"IMG stored on tab {current_index}")

        # Update window title
        file_name = os.path.basename(img_file.file_path)
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Update UI for loaded IMG
        if hasattr(self, '_update_ui_for_loaded_img'):
            self._update_ui_for_loaded_img()

        # Log success
        entry_count = len(img_file.entries) if img_file.entries else 0
        self.log_message(f"Loaded: {file_name} ({entry_count} entries)")

        # Hide progress
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()

    except Exception as e:
        self.log_message(f"Error in _on_img_loaded: {str(e)}")

        if hasattr(self, '_on_img_load_error'):
            self._on_img_load_error(str(e))

def _populate_real_img_table(self, img_file: IMGFile): #vers 2 #Restore
    """Populate table with real IMG file entries - for SA format display"""
    if not img_file or not img_file.entries:
        self.gui_layout.table.setRowCount(0)
        return

    table = self.gui_layout.table
    entries = img_file.entries

    # Clear existing data (including sample entries)
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        try:
            # Name - should now be clean from fixed parsing
            clean_name = str(entry.name).strip() if hasattr(entry, 'name') else f"Entry_{row}"
            table.setItem(row, 0, QTableWidgetItem(clean_name))

            # Extension - Use the cleaned extension from populate_entry_details
            if hasattr(entry, 'extension') and entry.extension:
                extension = entry.extension
            else:
                # Fallback extraction
                if '.' in clean_name:
                    extension = clean_name.split('.')[-1].upper()
                    extension = ''.join(c for c in extension if c.isalpha())
                else:
                    extension = "NO_EXT"
            table.setItem(row, 1, QTableWidgetItem(extension))

            # Size - Format properly
            try:
                if hasattr(entry, 'size') and entry.size:
                    size_bytes = int(entry.size)
                    if size_bytes < 1024:
                        size_text = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        size_text = f"{size_bytes / 1024:.1f} KB"
                    else:
                        size_text = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    size_text = "0 B"
            except:
                size_text = "Unknown"
            table.setItem(row, 2, QTableWidgetItem(size_text))

            # Hash/Offset - Show as hex
            try:
                if hasattr(entry, 'offset') and entry.offset is not None:
                    offset_text = f"0x{int(entry.offset):X}"
                else:
                    offset_text = "0x0"
            except:
                offset_text = "0x0"
            table.setItem(row, 3, QTableWidgetItem(offset_text))

            # Version - Use proper RW version parsing
            try:
                if extension in ['DFF', 'TXD']:
                    if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                        version_text = entry.get_version_text()
                    elif hasattr(entry, 'rw_version') and entry.rw_version > 0:
                        # FIXED: Use proper RW version mapping
                        rw_versions = {
                            0x0800FFFF: "3.0.0.0",
                            0x1003FFFF: "3.1.0.1",
                            0x1005FFFF: "3.2.0.0",
                            0x1400FFFF: "3.4.0.3",
                            0x1803FFFF: "3.6.0.3",
                            0x1C020037: "3.7.0.2",
                            # Additional common SA versions
                            0x34003: "3.4.0.3",
                            0x35002: "3.5.0.2",
                            0x36003: "3.6.0.3",
                            0x37002: "3.7.0.2",
                            0x1801: "3.6.0.3",  # Common SA version
                            0x1400: "3.4.0.3",  # Common SA version
                        }

                        if entry.rw_version in rw_versions:
                            version_text = f"RW {rw_versions[entry.rw_version]}"
                        else:
                            # Show hex for unknown versions
                            version_text = f"RW 0x{entry.rw_version:X}"
                    else:
                        version_text = "Unknown"
                elif extension == 'COL':
                    version_text = "COL"
                elif extension == 'IFP':
                    version_text = "IFP"
                else:
                    version_text = "Unknown"
            except:
                version_text = "Unknown"
            table.setItem(row, 4, QTableWidgetItem(version_text))

            # Compression
            try:
                if hasattr(entry, 'compression_type') and entry.compression_type:
                    if str(entry.compression_type).upper() != 'NONE':
                        compression_text = str(entry.compression_type)
                    else:
                        compression_text = "None"
                else:
                    compression_text = "None"
            except:
                compression_text = "None"
            table.setItem(row, 5, QTableWidgetItem(compression_text))

            # Status
            try:
                if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                    status_text = "New"
                elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                    status_text = "Modified"
                else:
                    status_text = "Ready"
            except:
                status_text = "Ready"
            table.setItem(row, 6, QTableWidgetItem(status_text))

            # Make all items read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        except Exception as e:
            self.log_message(f"❌ Error populating row {row}: {str(e)}")
            # Create minimal fallback row
            table.setItem(row, 0, QTableWidgetItem(f"Entry_{row}"))
            table.setItem(row, 1, QTableWidgetItem("UNKNOWN"))
            table.setItem(row, 2, QTableWidgetItem("0 B"))
            table.setItem(row, 3, QTableWidgetItem("0x0"))
            table.setItem(row, 4, QTableWidgetItem("Unknown"))
            table.setItem(row, 5, QTableWidgetItem("None"))
            table.setItem(row, 6, QTableWidgetItem("Error"))

    self.log_message(f"Table populated with {len(entries)} entries (SA format parser fixed)")


def _on_load_error(self, error_message): #vers 2
    """Handle loading error from background thread"""
    try:
        self.log_message(f"Loading error: {error_message}")

        # Hide progress - CHECK if method exists first
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Error loading file")

        # Reset UI to no-file state
        self._update_ui_for_no_img()

        # Show error dialog
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            self,
            "Loading Error",
            f"Failed to load IMG file:\n\n{error_message}")

    except Exception as e:
        self.log_message(f"Error in _on_load_error: {str(e)}")


def close_all_img(self):
    """Close all IMG files - Wrapper for close_all_tabs"""
    try:
        if hasattr(self, 'close_manager') and self.close_manager:
            self.close_manager.close_all_tabs()
        else:
            self.log_message("Close manager not available")
    except Exception as e:
        self.log_message(f"Error in close_all_img: {str(e)}")


__all__ = [
    'get_entry_rw_version',
    'format_file_size',
    '_on_load_progress',
    '_on_img_loaded',
    '_populate_real_img_table',
    '_on_load_error',
    'close_all_img'
]
