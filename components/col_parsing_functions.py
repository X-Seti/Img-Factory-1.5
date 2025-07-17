#this belongs in components/ col_parsing_functions.py - Version: 7
# X-Seti - July11 2025 - Img Factory 1.5

"""
COL Parser - Complete collision file parsing with debug control
Handles all COL format versions (COL1/COL2/COL3/COL4) with detailed logging
"""

import struct
import os
from typing import Dict, List, Tuple, Optional
from components.col_core_classes import is_col_debug_enabled

##Methods list -
# _load_col_file
# _populate_col_table_enhanced
# _setup_col_tab
# setup_col_tab_integration
# _setup_col_table_structure
# _update_col_info_bar_enhanced
# _validate_col_file

##class COLParser: -
#__init__
# def log
# _is_multi_model_archive

# _calculate_model_end_offset
# clear_debug_log
# format_collision_types
# get_debug_log
# get_model_stats_by_index
# _parse_collision_data
# parse_col_file_structure
# _parse_multi_model_archive
# parse_single_model
# set_debug

## Export main classes and functions -
# format_model_collision_types
# get_model_collision_stats
# parse_col_file_with_debug


def _load_col_file(main_window, file_path): #vers 4
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile

        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)

        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None

        return col_file

    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def _populate_col_table_enhanced(main_window, col_file): #vers 3
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager

        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        main_window.log_message("✅ Enhanced COL table populated")

    except Exception as e:
        main_window.log_message(f"❌ Enhanced table population failed: {str(e)}")
        raise


def _setup_col_tab(main_window, file_path): #vers 4
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()

        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            main_window.log_message("Using current tab for COL file")
        else:
            main_window.log_message("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                main_window.log_message("⚠️ Close manager not available")
                return None

        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"

        # Store tab info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }

        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        return current_index

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def setup_col_tab_integration(main_window): #vers 3
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)

        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)

        main_window.log_message("✅ COL tab integration ready")
        return True

    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False


def _setup_col_table_structure(main_window): #vers 3
    """Setup table structure for COL data display with enhanced usability"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return

        table = main_window.gui_layout.table

        # Configure table for COL data (7 columns)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Enable column dragging and resizing
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow dragging columns
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow resizing
        header.setDefaultSectionSize(120)  # Default column width

        # Set specific column widths for better visibility
        table.setColumnWidth(0, 150)  # Model name - wider for readability
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 200)  # Collision - wider for collision types
        table.setColumnWidth(6, 80)   # Status

        # Enable alternating row colors with light blue theme
        table.setAlternatingRowColors(True)

        # Set object name for specific styling
        table.setObjectName("col_table")

        # Apply COL-specific styling ONLY to this table
        col_table_style = """
            QTableWidget#col_table {
                alternate-background-color: #E3F2FD;
                background-color: #F5F5F5;
                gridline-color: #CCCCCC;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QTableWidget#col_table::item {
                padding: 4px;
                border-bottom: 1px solid #E0E0E0;
                background-color: transparent;
            }
            QTableWidget#col_table::item:alternate {
                background-color: #E3F2FD;
            }
            QTableWidget#col_table::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """

        # Apply header styling separately to avoid affecting other headers
        header_style = """
            background-color: #BBDEFB;
            color: #1976D2;
            font-weight: bold;
            border: 1px solid #90CAF9;
            padding: 6px;
        """

        # Apply table styling
        table.setStyleSheet(col_table_style)

        # Apply header styling directly to the header widget
        header = table.horizontalHeader()
        header.setStyleSheet(f"""
            QHeaderView::section {{
                {header_style}
            }}
            QHeaderView::section:hover {{
                background-color: #90CAF9;
            }}
        """)

        # Clear existing data
        table.setRowCount(0)

        main_window.log_message("🔧 Table structure configured for COL data with scoped styling")

    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up table structure: {str(e)}")


def _update_col_info_bar_enhanced(main_window, col_file, file_path): #vers 3
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager

        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        main_window.log_message("✅ Enhanced info bar updated")

    except Exception as e:
        main_window.log_message(f"❌ Enhanced info bar update failed: {str(e)}")
        raise


def _validate_col_file(main_window, file_path): #vers 3
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


class COLParser:
    """Complete COL file parser with debugging support"""
    
    def __init__(self, debug=None): #vers 1
        """Initialize COL parser with debug control"""
        # Check global debug setting if not specified
        if debug is None:
            self.debug = is_col_debug_enabled()
        else:
            self.debug = debug
        
        self.log_messages = []
    

    def _calculate_model_end_offset(self, data, start_offset, declared_size): #vers 4
        """Calculate the end offset of a model"""
        try:
            # Add 8 bytes for header (signature + size)
            end_offset = start_offset + declared_size + 8

            # Ensure we don't go beyond data bounds
            if end_offset > len(data):
                end_offset = len(data)

            self.log(f"Model end offset: {end_offset}")

            return end_offset

        except Exception as e:
            self.log(f"Error calculating model end: {str(e)}")
            return start_offset + 800  # Safe fallback


    def clear_debug_log(self): #vers 1
        """Clear debug log"""
        self.log_messages = []


    def get_model_stats_by_index(self, file_path, model_index): #vers 5
        """Get statistics for a specific model by index"""
        models = self.parse_col_file_structure(file_path)

        if model_index < len(models):
            return models[model_index]
        else:
            self.log(f"Model index {model_index} not found (only {len(models)} models)")
            return {
                'sphere_count': 0,
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 0,
                'estimated_size': 64}


    def format_collision_types(self, stats):  #vers 4
        """Format collision types string from stats"""
        types = []
        if stats.get('sphere_count', 0) > 0:
            types.append(f"Spheres({stats['sphere_count']})")
        if stats.get('box_count', 0) > 0:
            types.append(f"Boxes({stats['box_count']})")
        if stats.get('face_count', 0) > 0:
            types.append(f"Mesh({stats['face_count']})")

        return ", ".join(types) if types else "None"


    def get_debug_log(self): #vers 1
        """Get debug log messages"""
        return self.log_messages


    def _is_multi_model_archive(self, data):
        """Check if this is a multi-model COL archive"""
        try:
            # Look for multiple COL signatures
            signature_count = 0
            offset = 0

            while offset < len(data) - 4:
                if data[offset:offset+4] in [b'COLL', b'COL2', b'COL3', b'COL4']:
                    signature_count += 1
                    if signature_count > 1:
                        self.log(f"Detected multi-model archive ({signature_count} signatures found)")
                        return True
                    # Skip to avoid counting the same signature multiple times
                    offset += 100
                else:
                    offset += 1

            return False

        except Exception:
            return False


    def log(self, message): #vers 1
        """Log debug message only if debug is enabled"""
        if self.debug:
            print(f"🔍 COLParser: {message}")
        self.log_messages.append(message)
    

    def _parse_collision_data(self, data, offset, data_size, version): #vers 4
        """Parse collision data and return statistics"""
        stats = {
            'sphere_count': 0,
            'box_count': 0,
            'vertex_count': 0,
            'face_count': 0,
            'total_elements': 0
        }

        try:
            if version == 'COL1':
                # COL1 has simpler structure
                # For now, estimate based on data size
                if data_size > 100:
                    stats['sphere_count'] = max(1, data_size // 200)
                    stats['total_elements'] = stats['sphere_count']
            else:
                # COL2/3/4 have more complex structure
                # For now, estimate based on data size
                if data_size > 200:
                    stats['vertex_count'] = max(10, data_size // 50)
                    stats['face_count'] = max(5, data_size // 100)
                    stats['total_elements'] = stats['vertex_count'] + stats['face_count']

            self.log(f"Collision stats: {stats}")

        except Exception as e:
            self.log(f"Error parsing collision data: {e}")

        return stats


    def parse_col_file_structure(self, file_path): #vers 6
        """Parse complete COL file and return structure info for all models"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")
            
            # CRITICAL FIX: First check if this is a multi-model COL archive
            if self._is_multi_model_archive(data):
                return self._parse_multi_model_archive(data)
            
            # Single model parsing (original approach)
            models = []
            offset = 0
            model_index = 0
            
            while offset < len(data):
                self.log(f"\n--- Model {model_index} at offset {offset} ---")
                
                # Check if we have enough data for a model
                if offset + 32 > len(data):
                    self.log(f"Not enough data for model header (need 32, have {len(data) - offset})")
                    break
                
                # Parse this model
                model_info, new_offset = self.parse_single_model(data, offset, model_index)
                
                if model_info is None:
                    self.log(f"Failed to parse model {model_index}, stopping")
                    break
                
                models.append(model_info)
                
                # Check if we advanced
                if new_offset <= offset:
                    self.log(f"Offset didn't advance (was {offset}, now {new_offset}), stopping")
                    break
                
                offset = new_offset
                model_index += 1
                
                self.log(f"Model {model_index - 1} parsed successfully, next offset: {offset}")
                
                # Safety check - don't parse more than 200 models
                if model_index > 200:
                    self.log("Safety limit reached (200 models), stopping")
                    break
            
            self.log(f"\nParsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing COL file: {str(e)}")
            return []
    

    def _parse_multi_model_archive(self, data): #vers 5
        """Parse multi-model COL archive with different structure"""
        try:
            self.log("Parsing as multi-model archive...")
            models = []
            
            # Find all COL signatures in the file
            signatures = []
            offset = 0
            
            while offset < len(data) - 4:
                sig = data[offset:offset+4]
                if sig in [b'COLL', b'COL2', b'COL3', b'COL4']:
                    signatures.append(offset)
                    self.log(f"Found {sig} at offset {offset}")
                offset += 1
            
            self.log(f"Found {len(signatures)} model signatures")
            
            # Parse each model starting from its signature
            for i, sig_offset in enumerate(signatures):
                try:
                    self.log(f"\n--- Archive Model {i} at offset {sig_offset} ---")
                    model_info, _ = self.parse_single_model(data, sig_offset, i)
                    
                    if model_info:
                        models.append(model_info)
                        self.log(f"Archive model {i} parsed successfully")
                    else:
                        self.log(f"Failed to parse archive model {i}")
                        
                except Exception as e:
                    self.log(f"Error parsing archive model {i}: {str(e)}")
                    continue
            
            self.log(f"Archive parsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing multi-model archive: {str(e)}")
            return []
    

    def parse_single_model(self, data, offset, model_index): #vers 5
        """Parse a single COL model and return info + new offset"""
        try:
            start_offset = offset
            
            # Read signature
            if offset + 4 > len(data):
                return None, offset
            
            signature = data[offset:offset+4]
            self.log(f"Signature: {signature}")
            
            # Validate signature
            if signature not in [b'COLL', b'COL2', b'COL3', b'COL4']:
                self.log(f"Invalid signature: {signature}")
                return None, offset
            
            offset += 4
            
            # Read file size
            if offset + 4 > len(data):
                return None, offset
            
            file_size = struct.unpack('<I', data[offset:offset+4])[0]
            self.log(f"Declared size: {file_size}")
            offset += 4
            
            # Read model name (22 bytes)
            if offset + 22 > len(data):
                return None, offset
            
            name_bytes = data[offset:offset+22]
            model_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            self.log(f"Model name: '{model_name}'")
            offset += 22
            
            # Read model ID (2 bytes)
            if offset + 2 > len(data):
                return None, offset
            
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            self.log(f"Model ID: {model_id}")
            offset += 2
            
            # Determine version from signature
            if signature == b'COLL':
                version = 'COL1'
            elif signature == b'COL2':
                version = 'COL2'
            elif signature == b'COL3':
                version = 'COL3'
            elif signature == b'COL4':
                version = 'COL4'
            else:
                version = 'UNKNOWN'
            
            # Parse collision data based on version
            collision_stats = self._parse_collision_data(data, offset, file_size - 28, version)
            
            # Calculate end offset
            end_offset = self._calculate_model_end_offset(data, start_offset, file_size)
            
            # Build model info dictionary
            model_info = {
                'name': model_name or f'Model_{model_index}',
                'model_id': model_id,
                'version': version,
                'size': file_size + 8,  # Include header
                'sphere_count': collision_stats.get('sphere_count', 0),
                'box_count': collision_stats.get('box_count', 0),
                'vertex_count': collision_stats.get('vertex_count', 0),
                'face_count': collision_stats.get('face_count', 0),
                'total_elements': collision_stats.get('total_elements', 0),
                'estimated_size': file_size + 8
            }
            
            self.log(f"Model parsed: {model_info['name']} (v{version}, {file_size + 8} bytes)")
            
            return model_info, end_offset
            
        except Exception as e:
            self.log(f"Error parsing model at offset {offset}: {str(e)}")
            return None, offset + 32  # Skip ahead to try next model
    

    def set_debug(self, enabled): #vers 1
        """Update debug setting"""
        self.debug = enabled


# Convenience functions
def format_model_collision_types(stats): #vers 4
    """Format collision types string"""
    parser = COLParser(debug=False)
    return parser.format_collision_types(stats)


def get_model_collision_stats(file_path, model_index, debug=None): #vers 4
    """Get collision statistics for a specific model"""
    if debug is None:
        debug = is_col_debug_enabled()

    parser = COLParser(debug=debug)
    return parser.get_model_stats_by_index(file_path, model_index)


def parse_col_file_with_debug(file_path, debug=None): #vers 4
    """Parse COL file and return model statistics with optional debug output"""
    if debug is None:
        debug = is_col_debug_enabled()
    
    parser = COLParser(debug=debug)
    models = parser.parse_col_file_structure(file_path)
    
    if debug:
        print("\n=== COL Parser Debug Log ===")
        for msg in parser.get_debug_log():
            print(msg)
        print("=== End Debug Log ===\n")
    
    return models


# Export main classes and functions
__all__ = [
    'COLParser',
    'format_model_collision_types',
    'get_model_collision_stats', 
    'parse_col_file_with_debug'
]
