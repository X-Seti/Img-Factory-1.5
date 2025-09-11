#this belongs in methods/colour_file_table.py - Version: 1
# X-Seti - August05 2025 - IMG Factory 1.5 - Pink File Table System

"""
Pink File Table System
Customizable colour-themed file table with hex column and adjustable spacing
"""

import os
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSlider, QGroupBox, QFormLayout,
    QColorDialog, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

##Methods list -
# apply_color_file_table_theme
# create_file_table_settings_dialog
# get_default_pink_colors
# integrate_pink_file_table
# setup_enhanced_img_table
# show_file_table_settings

##Classes -
# PinkFileTableTheme

class PinkFileTableTheme:
    """Manages pink file table theming and settings"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_colors = self.get_default_colors()
        self.row_spacing = 22  # Default row height
        
    def get_default_colors(self) -> Dict[str, str]:
        """Get default pink color scheme"""
        return {
            'background': '#FDF2F8',           # Light pink background
            'alternate_row': '#FCE7F3',        # Slightly darker pink for alternating rows
            'selected_background': '#EC4899',  # Hot pink for selection
            'selected_text': '#FFFFFF',        # White text on selection
            'header_background': '#F9A8D4',    # Pink header background
            'header_text': '#831843',          # Dark pink header text
            'border_color': '#F472B6'          # Pink border
        }
    
    def apply_theme_to_table(self, table: QTableWidget):
        """Apply pink theme to table"""
        colors = self.current_colors
        
        # Create comprehensive stylesheet
        style = f"""
            QTableWidget {{
                background-color: {colors['background']};
                alternate-background-color: {colors['alternate_row']};
                border: 2px solid {colors['border_color']};
                border-radius: 8px;
                gridline-color: {colors['border_color']};
                font-size: 9pt;
                selection-background-color: {colors['selected_background']};
                selection-color: {colors['selected_text']};
            }}
            
            QTableWidget::item {{
                padding: 6px;
                border: none;
                border-bottom: 1px solid {colors['border_color']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors['selected_background']};
                color: {colors['selected_text']};
                font-weight: bold;
            }}
            
            QTableWidget::item:hover {{
                background-color: #FBBF24;
                color: #92400E;
            }}
            
            QHeaderView::section {{
                background-color: {colors['header_background']};
                color: {colors['header_text']};
                padding: 8px;
                border: 2px solid {colors['border_color']};
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
                margin: 1px;
            }}
            
            QHeaderView::section:hover {{
                background-color: #BE185D;
                color: #FFFFFF;
            }}
            
            QTableWidget::corner {{
                background-color: {colors['header_background']};
                border: 2px solid {colors['border_color']};
            }}
        """
        
        table.setStyleSheet(style)
        
        # Set row height
        table.verticalHeader().setDefaultSectionSize(self.row_spacing)
        
        # Enable alternating row colors
        table.setAlternatingRowColors(True)


def get_default_pink_colors() -> Dict[str, str]:
    """Get default pink color scheme for file table"""
    return {
        'background': '#FDF2F8',           # Light pink background
        'alternate_row': '#FCE7F3',        # Slightly darker pink for alternating rows
        'selected_background': '#EC4899',  # Hot pink for selection
        'selected_text': '#FFFFFF',        # White text on selection
        'header_background': '#F9A8D4',    # Pink header background
        'header_text': '#831843',          # Dark pink header text
        'border_color': '#F472B6'          # Pink border
    }


def setup_enhanced_img_table(table: QTableWidget, img_file):
    """Setup enhanced IMG table with hex column"""
    try:
        # Setup columns - Added Hex column before RW Version
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Hex", "RW Version", "Info"
        ])
        
        # Set column widths for better layout
        table.setColumnWidth(0, 200)  # Name
        table.setColumnWidth(1, 60)   # Type
        table.setColumnWidth(2, 80)   # Size
        table.setColumnWidth(3, 80)   # Offset
        table.setColumnWidth(4, 100)  # Hex (NEW)
        table.setColumnWidth(5, 120)  # RW Version
        table.setColumnWidth(6, 120)  # Info
        
        # Configure table behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        table.setSortingEnabled(True)
        
        # Set header resize modes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name stretches
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        
        # Clear and populate table
        table.setRowCount(0)
        
        if not img_file or not img_file.entries:
            return
        
        for i, entry in enumerate(img_file.entries):
            table.insertRow(i)
            
            # Name
            name_item = QTableWidgetItem(entry.name)
            table.setItem(i, 0, name_item)
            
            # Type (extension)
            file_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
            type_item = QTableWidgetItem(file_ext)
            table.setItem(i, 1, type_item)
            
            # Size (formatted)
            size_text = _format_file_size(entry.size)
            size_item = QTableWidgetItem(size_text)
            table.setItem(i, 2, size_item)
            
            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:X}")
            table.setItem(i, 3, offset_item)
            
            # Hex (NEW COLUMN) - First 16 bytes of file data as hex
            hex_preview = _get_hex_preview(entry)
            hex_item = QTableWidgetItem(hex_preview)
            table.setItem(i, 4, hex_item)
            
            # RW Version
            rw_version = getattr(entry, 'rw_version_name', 'Unknown')
            if not rw_version or rw_version == 'Unknown':
                rw_version = f"0x{getattr(entry, 'rw_version', 0):X}" if getattr(entry, 'rw_version', 0) > 0 else "N/A"
            rw_item = QTableWidgetItem(rw_version)
            table.setItem(i, 5, rw_item)
            
            # Info/Status
            info = "OK"
            if hasattr(entry, 'compression_type') and entry.compression_type != 0:
                info = "Compressed"
            if hasattr(entry, 'is_encrypted') and entry.is_encrypted:
                info = "Encrypted"
            info_item = QTableWidgetItem(info)
            table.setItem(i, 6, info_item)
        
    except Exception as e:
        print(f"Error setting up enhanced IMG table: {e}")


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _get_hex_preview(entry) -> str:
    """Get hex preview of first 16 bytes of file"""
    try:
        if hasattr(entry, '_cached_data') and entry._cached_data:
            data = entry._cached_data[:16]
        elif hasattr(entry, 'get_data'):
            try:
                full_data = entry.get_data()
                data = full_data[:16] if full_data else b''
            except:
                return "No Data"
        else:
            return "No Data"
        
        if not data:
            return "Empty"
        
        # Convert to hex string
        hex_str = ' '.join(f'{b:02X}' for b in data)
        return hex_str if len(hex_str) <= 47 else hex_str[:47] + "..."
        
    except Exception:
        return "Error"


def apply_pink_file_table_theme(main_window, colors: Optional[Dict[str, str]] = None, row_spacing: int = 22):
    """Apply pink theme to file table"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False
        
        # Use provided colors or defaults
        if colors is None:
            colors = get_default_pink_colors()
        
        # Create theme manager
        theme_manager = PinkFileTableTheme(main_window)
        theme_manager.current_colors = colors
        theme_manager.row_spacing = row_spacing
        
        # Apply theme
        theme_manager.apply_theme_to_table(main_window.gui_layout.table)
        
        # Store theme manager reference
        main_window._file_table_theme = theme_manager
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✨ Pink file table theme applied")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error applying pink theme: {str(e)}")
        return False


def show_file_table_settings(main_window):
    """Show file table color and spacing settings dialog"""
    try:
        dialog = create_file_table_settings_dialog(main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Settings were applied in the dialog
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✨ File table settings updated")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error showing file table settings: {str(e)}")


def create_file_table_settings_dialog(main_window) -> QDialog:
    """Create file table settings dialog"""
    dialog = QDialog(main_window)
    dialog.setWindowTitle("🎨 File Table Colors & Spacing")
    dialog.setMinimumSize(500, 600)
    
    layout = QVBoxLayout(dialog)
    
    # Get current theme or defaults
    if hasattr(main_window, '_file_table_theme'):
        current_colors = main_window._file_table_theme.current_colors
        current_spacing = main_window._file_table_theme.row_spacing
    else:
        current_colors = get_default_pink_colors()
        current_spacing = 22
    
    # Color settings group
    colors_group = QGroupBox("🎨 File List Colors")
    colors_layout = QFormLayout(colors_group)
    
    color_buttons = {}
    color_labels = {
        'background': 'Background Color',
        'alternate_row': 'Alternate Row Color',
        'selected_background': 'Selection Background',
        'selected_text': 'Selection Text',
        'header_background': 'Header Background',
        'header_text': 'Header Text',
        'border_color': 'Border Color'
    }
    
    def create_color_button(color_key, color_value):
        btn = QPushButton()
        btn.setFixedSize(50, 30)
        btn.setStyleSheet(f"background-color: {color_value}; border: 2px solid #999;")
        
        def change_color():
            color = QColorDialog.getColor(QColor(color_value), dialog, f"Choose {color_labels[color_key]}")
            if color.isValid():
                hex_color = color.name()
                btn.setStyleSheet(f"background-color: {hex_color}; border: 2px solid #999;")
                color_buttons[color_key] = hex_color
        
        btn.clicked.connect(change_color)
        color_buttons[color_key] = color_value
        return btn
    
    for key, label in color_labels.items():
        color_btn = create_color_button(key, current_colors[key])
        colors_layout.addRow(f"{label}:", color_btn)
    
    layout.addWidget(colors_group)
    
    # Spacing settings group
    spacing_group = QGroupBox("📏 Row Spacing")
    spacing_layout = QFormLayout(spacing_group)
    
    spacing_slider = QSlider(Qt.Orientation.Horizontal)
    spacing_slider.setRange(16, 40)
    spacing_slider.setValue(current_spacing)
    spacing_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    spacing_slider.setTickInterval(4)
    
    spacing_label = QLabel(f"{current_spacing}px")
    
    def update_spacing_label(value):
        spacing_label.setText(f"{value}px")
    
    spacing_slider.valueChanged.connect(update_spacing_label)
    
    spacing_layout.addRow("Row Height:", spacing_slider)
    spacing_layout.addRow("Current:", spacing_label)
    
    layout.addWidget(spacing_group)
    
    # Preview checkbox
    preview_check = QCheckBox("Live Preview")
    preview_check.setChecked(True)
    layout.addWidget(preview_check)
    
    def apply_preview():
        if preview_check.isChecked():
            apply_pink_file_table_theme(main_window, color_buttons.copy(), spacing_slider.value())
    
    # Connect preview updates
    spacing_slider.valueChanged.connect(lambda: apply_preview())
    preview_check.toggled.connect(lambda: apply_preview())
    
    # Preset buttons
    presets_group = QGroupBox("🎨 Color Presets")
    presets_layout = QHBoxLayout(presets_group)
    

    def create_preset_button(name, colors):
        btn = QPushButton(name)
        def apply_preset():
            for key, value in colors.items():
                if key in color_buttons:
                    color_buttons[key] = value
                    # Update button color
                    color_btn = colors_layout.itemAt(list(color_labels.keys()).index(key) * 2 + 1).widget()
                    if color_btn:
                        color_btn.setStyleSheet(f"background-color: {value}; border: 2px solid #999;")
            apply_preview()
        btn.clicked.connect(apply_preset)
        return btn

    # Preset color schemes
    presets = {
        # Original presets
        "Light Pink": get_default_pink_colors(),
        "Hot Pink": {
            'background': '#FDF2F8', 'alternate_row': '#F9A8D4', 'selected_background': '#BE185D',
            'selected_text': '#FFFFFF', 'header_background': '#EC4899', 'header_text': '#FFFFFF', 'border_color': '#BE185D'
        },
        "Rose Gold": {
            'background': '#FFF7ED', 'alternate_row': '#FED7AA', 'selected_background': '#EA580C',
            'selected_text': '#FFFFFF', 'header_background': '#FB923C', 'header_text': '#FFFFFF', 'border_color': '#F97316'
        },
        "Lavender": {
            'background': '#FAF5FF', 'alternate_row': '#E9D5FF', 'selected_background': '#7C3AED',
            'selected_text': '#FFFFFF', 'header_background': '#A855F7', 'header_text': '#FFFFFF', 'border_color': '#8B5CF6'
        },

        # Light themes
        "Yellow": {
            'background': '#FEFCE8', 'alternate_row': '#FEF08A', 'selected_background': '#CA8A04',
            'selected_text': '#FFFFFF', 'header_background': '#EAB308', 'header_text': '#FFFFFF', 'border_color': '#D97706'
        },
        "Orange": {
            'background': '#FFF7ED', 'alternate_row': '#FFCC9C', 'selected_background': '#EA580C',
            'selected_text': '#FFFFFF', 'header_background': '#F97316', 'header_text': '#FFFFFF', 'border_color': '#EA580C'
        },
        "Red": {
            'background': '#FEF2F2', 'alternate_row': '#FECACA', 'selected_background': '#DC2626',
            'selected_text': '#FFFFFF', 'header_background': '#EF4444', 'header_text': '#FFFFFF', 'border_color': '#DC2626'
        },
        "Purple": {
            'background': '#FAF5FF', 'alternate_row': '#DDD6FE', 'selected_background': '#7C3AED',
            'selected_text': '#FFFFFF', 'header_background': '#8B5CF6', 'header_text': '#FFFFFF', 'border_color': '#7C3AED'
        },
        "Green": {
            'background': '#F0FDF4', 'alternate_row': '#BBF7D0', 'selected_background': '#16A34A',
            'selected_text': '#FFFFFF', 'header_background': '#22C55E', 'header_text': '#FFFFFF', 'border_color': '#16A34A'
        },
        "Blue": {
            'background': '#EFF6FF', 'alternate_row': '#BFDBFE', 'selected_background': '#2563EB',
            'selected_text': '#FFFFFF', 'header_background': '#3B82F6', 'header_text': '#FFFFFF', 'border_color': '#2563EB'
        },

        # Dark themes
        "Dark Yellow": {
            'background': '#1C1C14', 'alternate_row': '#2D2D1F', 'selected_background': '#FCD34D',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#FCD34D', 'border_color': '#FCD34D'
        },
        "Dark Orange": {
            'background': '#1C1410', 'alternate_row': '#2D241A', 'selected_background': '#FB923C',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#FB923C', 'border_color': '#FB923C'
        },
        "Dark Red": {
            'background': '#1C1111', 'alternate_row': '#2D1B1B', 'selected_background': '#F87171',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#F87171', 'border_color': '#F87171'
        },
        "Dark Pink": {
            'background': '#1C111A', 'alternate_row': '#2D1B28', 'selected_background': '#F472B6',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#F472B6', 'border_color': '#F472B6'
        },
        "Dark Purple": {
            'background': '#1A1121', 'alternate_row': '#281B35', 'selected_background': '#A78BFA',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#A78BFA', 'border_color': '#A78BFA'
        },
        "Dark Green": {
            'background': '#111C14', 'alternate_row': '#1B2D1F', 'selected_background': '#4ADE80',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#4ADE80', 'border_color': '#4ADE80'
        },
        "Dark Blue": {
            'background': '#111827', 'alternate_row': '#1F2937', 'selected_background': '#60A5FA',
            'selected_text': '#000000', 'header_background': '#374151', 'header_text': '#60A5FA', 'border_color': '#60A5FA'
        },

        # Pure dark themes
        "Black & Yellow": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#FBBF24',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#FBBF24', 'border_color': '#FBBF24'
        },
        "Black & Orange": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#FB923C',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#FB923C', 'border_color': '#FB923C'
        },
        "Black & Red": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#F87171',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#F87171', 'border_color': '#F87171'
        },
        "Black & Pink": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#F472B6',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#F472B6', 'border_color': '#F472B6'
        },
        "Black & Purple": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#A78BFA',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#A78BFA', 'border_color': '#A78BFA'
        },
        "Black & Green": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#4ADE80',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#4ADE80', 'border_color': '#4ADE80'
        },
        "Black & Blue": {
            'background': '#000000', 'alternate_row': '#1A1A1A', 'selected_background': '#60A5FA',
            'selected_text': '#000000', 'header_background': '#111111', 'header_text': '#60A5FA', 'border_color': '#60A5FA'
        }
    }
    
    for name, preset_colors in presets.items():
        presets_layout.addWidget(create_preset_button(name, preset_colors))
    
    layout.addWidget(presets_group)
    
    # Buttons
    button_layout = QHBoxLayout()
    
    apply_btn = QPushButton("✅ Apply & Save")
    def apply_settings():
        # Apply the settings
        apply_pink_file_table_theme(main_window, color_buttons.copy(), spacing_slider.value())
        
        # Save to app settings if available
        if hasattr(main_window, 'app_settings'):
            main_window.app_settings.current_settings.update({
                'file_table_colors': color_buttons.copy(),
                'file_table_row_spacing': spacing_slider.value()
            })
            main_window.app_settings.save_settings()
        
        dialog.accept()
    
    apply_btn.clicked.connect(apply_settings)
    button_layout.addWidget(apply_btn)
    
    reset_btn = QPushButton("🔄 Reset to Defaults")
    def reset_defaults():
        defaults = get_default_pink_colors()
        for key, value in defaults.items():
            if key in color_buttons:
                color_buttons[key] = value
                # Update button color
                color_btn = colors_layout.itemAt(list(color_labels.keys()).index(key) * 2 + 1).widget()
                if color_btn:
                    color_btn.setStyleSheet(f"background-color: {value}; border: 2px solid #999;")
        spacing_slider.setValue(22)
        apply_preview()
    
    reset_btn.clicked.connect(reset_defaults)
    button_layout.addWidget(reset_btn)
    
    cancel_btn = QPushButton("❌ Cancel")
    cancel_btn.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_btn)
    
    layout.addLayout(button_layout)
    
    return dialog


def integrate_pink_file_table(main_window) -> bool:
    """Integrate pink file table system into main window"""
    try:
        # Add methods to main window
        main_window.apply_pink_file_table_theme = lambda colors=None, spacing=22: apply_pink_file_table_theme(main_window, colors, spacing)
        main_window.show_file_table_settings = lambda: show_file_table_settings(main_window)
        main_window.setup_enhanced_img_table = lambda img_file: setup_enhanced_img_table(main_window.gui_layout.table, img_file)
        
        # Apply default pink theme
        apply_pink_file_table_theme(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✨ Pink file table system integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Pink file table integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'PinkFileTableTheme',
    'apply_pink_file_table_theme',
    'show_file_table_settings',
    'setup_enhanced_img_table',
    'integrate_pink_file_table',
    'get_default_pink_colors'
]
