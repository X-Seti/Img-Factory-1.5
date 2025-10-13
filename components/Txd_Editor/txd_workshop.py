#!/usr/bin/env python3
#this belongs in components/Txd_Editor/ txd_workshop.py - Version: 10
# X-Seti - October10 2025 - Img Factory 1.5 - TXD Workshop Header Update

"""
Updated imports and method list for txd_workshop.py
Replace the existing imports and ##Methods list section
"""

import os
import tempfile
import subprocess
import shutil
import struct
import sys
import io
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PyQt6.QtWidgets import (QApplication, QSlider, QCheckBox,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout, QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtSvg import QSvgRenderer

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    # Try main app path first
    from methods.txd_versions import (
        detect_txd_version, get_platform_name, get_game_from_version,
        get_version_capabilities, get_platform_capabilities,
        is_mipmap_supported, is_bumpmap_supported,
        validate_txd_format, TXDPlatform, detect_platform_from_data
    )
except ImportError:
    # Fallback to standalone depends folder
    from depends.txd_versions import (
        detect_txd_version, get_platform_name, get_game_from_version,
        get_version_capabilities, get_platform_capabilities,
        is_mipmap_supported, is_bumpmap_supported,
        validate_txd_format, TXDPlatform, detect_platform_from_data
    )

try:
    from components.Txd_Editor.depends.txd_versions import (
        detect_txd_version,
        get_version_string,
        get_platform_name,
        get_platform_capabilities,
        TXDPlatform,
        TXDVersion
    )
except ModuleNotFoundError:
    from depends.txd_versions import (
        detect_txd_version,
        get_version_string,
        get_platform_name,
        get_platform_capabilities,
        TXDPlatform,
        TXDVersion
    )

DEBUG_STANDALONE = False


##Methods list -
# _apply_gaussian_blur                  # Gaussian blur for bumpmap smoothing
# _compress_to_dxt1
# _compress_to_dxt3
# _compress_to_dxt5
# _convert_numpy_to_qimage              # NEW - Convert numpy to QImage
# _create_blank_texture
# _create_bumpmap_data                  # Create bumpmap using various methods
# _create_empty_txd_data
# _create_export_icon
# _create_file_icon
# _create_flip_horiz_icon
# _create_flip_vert_icon
# _create_folder_icon
# _create_import_icon
# _create_info_icon
# _create_left_panel
# _create_middle_panel
# _create_new_texture_entry
# _create_new_txd
# _create_package_icon
# _create_properties_icon
# _create_reflection_panel               # NEW - Create reflection map panel
# _create_right_panel
# _create_save_icon
# _create_thumbnail
# _create_toolbar
# _create_undo_icon
# _decode_bumpmap
# _decompress_dxt1
# _decompress_dxt3
# _decompress_dxt5
# _decompress_uncompress
# _delete_bumpmap                        # Delete bumpmap from texture
# _delete_texture
# _detect_txd_info
# _detect_y_flip                         # NEW - Detect normal map Y-flip
# _emboss_filter                         # Emboss filter for bumpmap
# _encode_bumpmap
# _export_bumpmap
# _export_reflection_maps                # NEW - Export reflection/Fresnel maps
# _extract_alpha_channel
# _extract_txd_from_img
# _export_alpha_only
# _generate_all_maps_from_texture        # NEW - Generate complete map set
# _generate_bumpmap_from_texture         # Main bumpmap generator dialog
# _generate_reflection_from_normal       # NEW - Generate reflection from normal
# _generate_reflection_maps              # NEW - Generate reflection/Fresnel
# _generate_rgb_normal_map               # Generate proper RGB normal map
# _get_format_description
# _get_resize_direction
# _handle_resize
# _has_bumpmap_data                      # Check if texture has bumpmap
# _height_map                            # Height map bumpmap method
# _import_bumpmap
# _is_on_draggable_area
# _load_img_txd_list
# _load_txd_textures
# _mark_as_modified
# _normal_map                            # Normal map bumpmap method
# _normal_to_bump                        # NEW - Normal to bump conversion
# _normal_to_reflection                  # NEW - Normal to reflection/Fresnel
# _normalize_vector                      # NEW - Normalize vector arrays
# _on_texture_selected
# _on_txd_selected
# _parse_single_texture
# _preserve_original_data
# _preview_bumpmap_generation            # Preview bumpmap before applying
# _rebuild_txd_data
# _reload_texture_table
# _save_as_new_txd
# _save_as_txd_file
# _save_texture_png
# _save_to_img
# _save_undo_state
# _show_detailed_info
# _show_texture_context_menu
# _sobel_filter                          # Sobel edge detection for bumpmap
# _toggle_maximize
# _undo_last_action
# _update_cursor
# _update_reflection_previews            # NEW - Update reflection previews
# _update_texture_info
# _view_bumpmap                          # Opens bumpmap manager
# export_all_textures
# export_selected_texture
# flip_texture
# import_texture
# load_from_img_archive
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# open_img_archive
# open_txd_file
# save_txd_file
# setup_ui
# show_properties

##class TXDWorkshop: -
# __init__
# closeEvent

##class BumpmapManagerWindow: -
# __init__
# setup_ui                               # UPDATED - Now includes reflection panel
# _apply_changes
# _create_button_bar
# _create_left_panel
# _create_middle_panel
# _create_reflection_panel               # NEW
# _create_title_bar
# _delete_bumpmap
# _export_bumpmap
# _generate_bumpmap
# _generate_reflection_maps              # NEW
# _get_resize_corner
# _has_bumpmap
# _import_bumpmap
# _update_bumpmap_preview
# _update_reflection_previews            # NEW
# closeEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent

##class MipmapManagerWindow: -
# __init__
# setup_ui
# _apply_changes
# _create_button_bar
# _create_level_card
# _create_title_bar
# _delete_level
# _edit_level
# _edit_main_texture
# _export_level
# _get_resize_corner
# _recompress_modified_levels
# closeEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent

##class TexturePropertiesDialog: -
# __init__
# _apply_properties
# _export_mipmaps
# _generate_mipmaps
# _view_mipmaps

"""
Complete texture dictionary structure:

texture_dict = {
    # Basic properties
    'name': str,                    # Texture name
    'alpha_name': str,              # Alpha channel name (if has_alpha)
    'width': int,                   # Texture width
    'height': int,                  # Texture height
    'depth': int,                   # Bit depth (8, 16, 24, 32)
    'format': str,                  # Format string (DXT1, DXT3, DXT5, ARGB8888, etc)
    'has_alpha': bool,              # Has alpha channel

    # Main texture data
    'rgba_data': bytes,             # Main texture RGBA data
    'compressed_data': bytes,       # DXT compressed data (if applicable)

    # Mipmaps
    'mipmaps': int,                 # Number of mipmap levels
    'mipmap_levels': [              # List of mipmap level dicts
        {
            'level': int,           # Mipmap level (0 = main)
            'width': int,           # Level width
            'height': int,          # Level height
            'rgba_data': bytes,     # Level RGBA data
            'compressed_data': bytes,  # Level compressed data
            'compressed_size': int  # Size of compressed data
        }
    ],

    # Bumpmaps
    'bumpmap_data': bytes,          # Bumpmap data (grayscale or RGB)
    'bumpmap_type': int,            # 0=height, 1=normal, 2=both
    'has_bumpmap': bool,            # Has bumpmap data

    # Reflection maps
    'reflection_map': bytes,        # RGB reflection vectors
    'fresnel_map': bytes,           # Grayscale Fresnel reflectivity
    'has_reflection': bool,         # Has reflection data

    # RenderWare properties
    'raster_format_flags': int,     # RW raster format flags (bit 0x10 = bumpmap)
    'filter_flags': int,            # Texture filtering flags
    'address_u': int,               # U-axis addressing mode
    'address_v': int,               # V-axis addressing mode
}
"""

class TXDConversionConfig: #vers 1
    """Configuration for TXD platform conversion"""

    def __init__(self): #vers 1
        self.target_platform = "pc"
        self.target_game = "gtasa"
        self.target_version = 0x1803FFFF
        self.target_device = 0x08
        self.generate_mipmaps = False
        self.max_mipmap_level = 4
        self.compress_textures = False
        self.compression_quality = 0.8
        self.compress_format = "DXT1"
        self.palettize_textures = False
        self.palette_type = "PAL8"
        self.improve_filtering = False

    def to_dict(self) -> Dict: #vers 1
        """Convert config to dictionary"""
        return {
            'target_platform': self.target_platform,
            'target_game': self.target_game,
            'target_version': self.target_version,
            'target_device': self.target_device,
            'generate_mipmaps': self.generate_mipmaps,
            'max_mipmap_level': self.max_mipmap_level,
            'compress_textures': self.compress_textures,
            'compression_quality': self.compression_quality,
            'compress_format': self.compress_format,
            'palettize_textures': self.palettize_textures,
            'palette_type': self.palette_type,
            'improve_filtering': self.improve_filtering
        }

    @staticmethod
    def from_dict(data: Dict) -> 'TXDConversionConfig': #vers 1
        """Create config from dictionary"""
        config = TXDConversionConfig()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class PlatformConversionDialog(QDialog): #vers 1
    """Dialog for TXD platform conversion configuration"""

    conversion_requested = pyqtSignal(object)

    def __init__(self, parent=None, current_version=None, current_device=None): #vers 1
        super().__init__(parent)
        self.setWindowTitle("TXD Platform Conversion")
        self.config = TXDConversionConfig()
        self.current_version = current_version
        self.current_device = current_device

        self._setup_ui()

    def _setup_ui(self): #vers 1
        """Setup conversion dialog UI"""
        layout = QVBoxLayout()
        form = QFormLayout()

        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["PC", "PS2", "Xbox", "PSP", "GameCube"])
        self.platform_combo.currentTextChanged.connect(self._on_platform_changed)
        form.addRow("Target Platform:", self.platform_combo)

        # Game selection
        self.game_combo = QComboBox()
        self.game_combo.addItems(["GTA III", "Vice City", "San Andreas", "State of Liberty"])
        form.addRow("Target Game:", self.game_combo)

        # Mipmap generation
        self.gen_mipmaps_check = QCheckBox()
        form.addRow("Generate Mipmaps:", self.gen_mipmaps_check)

        self.mipmap_max_spin = QDoubleSpinBox()
        self.mipmap_max_spin.setRange(1, 10)
        self.mipmap_max_spin.setValue(4)
        form.addRow("Max Mipmap Level:", self.mipmap_max_spin)

        # Compression
        self.compress_check = QCheckBox()
        form.addRow("Compress Textures:", self.compress_check)

        self.compress_quality = QDoubleSpinBox()
        self.compress_quality.setRange(0.0, 1.0)
        self.compress_quality.setSingleStep(0.1)
        self.compress_quality.setValue(0.8)
        form.addRow("Compression Quality:", self.compress_quality)

        # Capabilities display
        self.capabilities_label = QLabel()
        self.capabilities_label.setWordWrap(True)
        form.addRow("Platform Capabilities:", self.capabilities_label)

        layout.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.accept)
        button_layout.addWidget(convert_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Update capabilities for default selection
        self._on_platform_changed("PC")

    def _on_platform_changed(self, platform_text: str): #vers 1
        """Update UI when platform changes"""
        platform_map = {
            "PC": TXDPlatform.DEVICE_D3D9,
            "PS2": TXDPlatform.DEVICE_PS2,
            "Xbox": TXDPlatform.DEVICE_XBOX,
            "PSP": TXDPlatform.DEVICE_PSP,
            "GameCube": TXDPlatform.DEVICE_GC
        }

        device_id = platform_map.get(platform_text, TXDPlatform.DEVICE_D3D9)
        self._update_capabilities_display(device_id)

    def _update_capabilities_display(self, device_id: int): #vers 1
        """Update capabilities label with platform info"""
        caps = get_platform_capabilities(device_id)

        cap_text = f"<b>{caps['name']}</b><br>"
        cap_text += f"Compression: {', '.join(caps['compression']) if caps['compression'] else 'None'}<br>"
        cap_text += f"Formats: {len(caps['formats'])} supported<br>"
        cap_text += f"Bump Mapping: {'Yes' if caps.get('supports_bump', False) else 'No'}<br>"
        cap_text += f"Palettized: {'Yes' if caps['paletted'] else 'No'}"

        self.capabilities_label.setText(cap_text)

    def get_config(self) -> TXDConversionConfig: #vers 1
        """Get conversion configuration from dialog"""
        platform_map = {
            "PC": ("pc", TXDPlatform.DEVICE_D3D9),
            "PS2": ("ps2", TXDPlatform.DEVICE_PS2),
            "Xbox": ("xbox", TXDPlatform.DEVICE_XBOX),
            "PSP": ("psp", TXDPlatform.DEVICE_PSP),
            "GameCube": ("gamecube", TXDPlatform.DEVICE_GC)
        }

        game_map = {
            "GTA III": ("gta3", TXDVersion.GTA3_PC),
            "Vice City": ("gtavc", TXDVersion.GTAVC_PC),
            "San Andreas": ("gtasa", TXDVersion.GTASA_ALL),
            "State of Liberty": ("gtasol", TXDVersion.GTASOL)
        }

        platform_str = self.platform_combo.currentText()
        game_str = self.game_combo.currentText()

        platform_info = platform_map.get(platform_str, ("pc", TXDPlatform.DEVICE_D3D9))
        game_info = game_map.get(game_str, ("gtasa", TXDVersion.GTASA_ALL))

        self.config.target_platform = platform_info[0]
        self.config.target_device = platform_info[1]
        self.config.target_game = game_info[0]
        self.config.target_version = game_info[1]
        self.config.generate_mipmaps = self.gen_mipmaps_check.isChecked()
        self.config.max_mipmap_level = int(self.mipmap_max_spin.value())
        self.config.compress_textures = self.compress_check.isChecked()
        self.config.compression_quality = self.compress_quality.value()

        return self.config


class TXDWorkshop(QWidget): #vers 3
    """TXD Workshop - Main texture editing window"""

    workshop_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 9
        """Initialize TXD Workshop"""
        if DEBUG_STANDALONE and main_window is None:
            print("   → Initializing TXD Workshop...")

        super().__init__(parent)

        self.main_window = main_window
        self.current_img = None
        self.current_txd_data = None
        self.current_txd_name = None
        self.txd_list = []
        self.texture_list = []
        self.selected_texture = None
        self.undo_stack = []
        self.button_display_mode = 'both'
        self.current_txd_path = None
        self.save_to_source_location = True  # Save in same dir as loaded file
        self.last_save_directory = None

        # Set default font size to 12pt
        from PyQt6.QtGui import QFont
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        self.infobar_font = QFont("Courier New", 9)

        # Preview settings
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.background_color = QColor(42, 42, 42)
        self.background_mode = 'solid'
        self.placeholder_text = "No texture"
        self.setMinimumSize(200, 200)
        self.info_bitdepth = QLabel("[32bit]")

        # Texture import/export settings
        self.dimension_limiting_enabled = False  # Power of 2 enforcement
        self.splash_screen_mode = False  # Allow non-power-of-2 for splash screens
        self.custom_max_dimension = 4096  # Max texture size

        # Texture naming settings
        self.name_limit_enabled = True  # Enable 32-char limit by default
        self.max_texture_name_length = 32  # Default RenderWare limit

        # Format support flags
        self.iff_import_enabled = True  # Amiga IFF support
        self.splash_formats_enabled = True  # Non-standard dimensions

        # Export preferences
        self.export_target_game = "auto"  # auto, gta3, vc, sa, manhunt
        self.export_target_platform = "pc"  # pc, xbox, ps2, android, multi

        # TXD version tracking variables
        self.txd_version_id = 0
        self.txd_device_id = 0
        self.txd_version_str = "Unknown"
        self.txd_platform_name = "Unknown"
        self.txd_game = "Unknown"
        self.txd_capabilities = {}

        # Detect standalone mode
        self.standalone_mode = (main_window is None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


        # Set window flags based on mode
        """
        if self.standalone_mode:
            self.setWindowFlags(Qt.WindowType.Window)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        """

        # Docking state
        self.is_docked = False
        self.dock_widget = None

        self.setWindowTitle("TXD Workshop: No File")
        self.resize(1400, 800)
        self.use_system_titlebar = False
        self.window_always_on_top = False

        self._initialize_features()

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None  # Changed from resize_direction
        self.corner_size = 20  # Size of corner resize areas
        self.hover_corner = None  # Track which corner is hovered

        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        if self.standalone_mode:
            self._ensure_depends_structure()

        self.txd_tabs = []  # List of open TXD data
        self.current_tab_index = 0

        self.setup_ui()
        self._apply_theme()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

        if DEBUG_STANDALONE and self.standalone_mode:
            print("   ✓ TXD Workshop initialized")

    def setup_ui(self): #vers 7
        """Setup the main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # Tab bar for multiple TXD files
        self.txd_tabs = QTabWidget()
        self.txd_tabs.setTabsClosable(True)
        self.txd_tabs.tabCloseRequested.connect(self._close_txd_tab)
        self.txd_tabs.currentChanged.connect(self._switch_txd_tab)

        # Create initial tab with main content
        initial_tab = QWidget()
        tab_layout = QVBoxLayout(initial_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)


        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create all panels first
        left_panel = self._create_left_panel()
        middle_panel = self._create_middle_panel()
        right_panel = self._create_right_panel()

        # Add panels to splitter based on mode
        if left_panel is not None:  # IMG Factory mode
            main_splitter.addWidget(left_panel)
            main_splitter.addWidget(middle_panel)
            main_splitter.addWidget(right_panel)
            # Set proportions (2:3:5)
            main_splitter.setStretchFactor(0, 2)
            main_splitter.setStretchFactor(1, 3)
            main_splitter.setStretchFactor(2, 5)
        else:  # Standalone mode
            main_splitter.addWidget(middle_panel)
            main_splitter.addWidget(right_panel)
            # Set proportions (1:1)
            main_splitter.setStretchFactor(0, 1)
            main_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(main_splitter)

        # Connect signals AFTER texture_table is created
        self._connect_texture_table_signals()

        # NEW: Status bar at bottom with texture info
        #self.status_bar = self._create_status_bar()
        #main_layout.addWidget(self.status_bar)

        # Status indicators if available
        if hasattr(self, '_setup_status_indicators'):
            status_frame = self._setup_status_indicators()
            main_layout.addWidget(status_frame)

    def _add_txd_tab(self, txd_data, txd_name): #vers 1
        """Add new TXD as tab"""
        tab_info = {
            'name': txd_name,
            'data': txd_data,
            'textures': [],
            'modified': False
        }
        self.txd_tabs.append(tab_info)

    def _create_status_bar(self): #vers 5
        """Create bottom status bar - single line compact"""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_bar.setFixedHeight(22)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(15)

        # Left: Ready
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        if hasattr(self, 'status_txd_info'):
            size_kb = len(txd_data) / 1024
            tex_count = len(self.texture_list)
            self.status_txd_info.setText(f"Textures: {tex_count} | TXD: {size_kb:.1f} KB")

        # TXD info
        self.status_txd_info = QLabel("TXD: None")
        layout.addWidget(self.status_txd_info)

        layout.addStretch()

        # Right: Size and Format
        self.info_size = QLabel("Size: -")
        layout.addWidget(self.info_size)

        self.format_status_label = QLabel("Format: -")
        layout.addWidget(self.format_status_label)

        return status_bar


    def _show_workshop_settings(self): #vers 6
        """Show comprehensive workshop settings dialog"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                    QLabel, QComboBox, QPushButton, QGroupBox,
                                    QCheckBox, QSpinBox, QFormLayout, QFontComboBox,
                                    QWidget)
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("TXD Workshop Settings")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout(dialog)

        tabs = QTabWidget()

        # === APPEARANCE TAB ===
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)

        # Font Settings Group
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout()

        # Main/Default Font
        default_font_layout = QHBoxLayout()
        self.default_font_combo = QFontComboBox()
        self.default_font_combo.setCurrentFont(self.font())
        default_font_layout.addWidget(self.default_font_combo)
        self.default_font_size = QSpinBox()
        self.default_font_size.setRange(8, 24)
        self.default_font_size.setValue(self.font().pointSize())
        self.default_font_size.setSuffix(" pt")
        default_font_layout.addWidget(self.default_font_size)
        font_layout.addRow("Default Font:", default_font_layout)

        # Title Font
        title_font_layout = QHBoxLayout()
        self.title_font_combo = QFontComboBox()
        if hasattr(self, 'title_font'):
            self.title_font_combo.setCurrentFont(self.title_font)
        title_font_layout.addWidget(self.title_font_combo)
        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(10, 32)
        self.title_font_size.setValue(getattr(self, 'title_font', QFont("Arial", 14)).pointSize())
        self.title_font_size.setSuffix(" pt")
        title_font_layout.addWidget(self.title_font_size)
        font_layout.addRow("Title Font:", title_font_layout)

        # Panel Font
        panel_font_layout = QHBoxLayout()
        self.panel_font_combo = QFontComboBox()
        if hasattr(self, 'panel_font'):
            self.panel_font_combo.setCurrentFont(self.panel_font)
        panel_font_layout.addWidget(self.panel_font_combo)
        self.panel_font_size = QSpinBox()
        self.panel_font_size.setRange(8, 18)
        self.panel_font_size.setValue(getattr(self, 'panel_font', QFont("Arial", 10)).pointSize())
        self.panel_font_size.setSuffix(" pt")
        panel_font_layout.addWidget(self.panel_font_size)
        font_layout.addRow("Panel Font:", panel_font_layout)

        # Button Font
        button_font_layout = QHBoxLayout()
        self.button_font_combo = QFontComboBox()
        if hasattr(self, 'button_font'):
            self.button_font_combo.setCurrentFont(self.button_font)
        button_font_layout.addWidget(self.button_font_combo)
        self.button_font_size = QSpinBox()
        self.button_font_size.setRange(8, 16)
        self.button_font_size.setValue(getattr(self, 'button_font', QFont("Arial", 10)).pointSize())
        self.button_font_size.setSuffix(" pt")
        button_font_layout.addWidget(self.button_font_size)
        font_layout.addRow("Button Font:", button_font_layout)

        # Info Bar Font
        infobar_font_layout = QHBoxLayout()
        self.infobar_font_combo = QFontComboBox()
        if hasattr(self, 'infobar_font'):
            self.infobar_font_combo.setCurrentFont(self.infobar_font)
        infobar_font_layout.addWidget(self.infobar_font_combo)
        self.infobar_font_size = QSpinBox()
        self.infobar_font_size.setRange(7, 14)
        self.infobar_font_size.setValue(getattr(self, 'infobar_font', QFont("Courier New", 9)).pointSize())
        self.infobar_font_size.setSuffix(" pt")
        infobar_font_layout.addWidget(self.infobar_font_size)
        font_layout.addRow("Info Bar Font:", infobar_font_layout)

        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)

        # UI Display Group
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout()

        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("Button Display:"))
        self.settings_display_combo = QComboBox()
        self.settings_display_combo.addItems(["Icons Only", "Text Only", "Icons + Text"])
        mode_map = {"icons": 0, "text": 1, "both": 2}
        self.settings_display_combo.setCurrentIndex(mode_map.get(self.button_display_mode, 2))
        display_layout.addWidget(self.settings_display_combo)
        display_layout.addStretch()
        ui_layout.addLayout(display_layout)

        titlebar_check = QCheckBox("Use system title bar")
        titlebar_check.setChecked(self.use_system_titlebar)
        ui_layout.addWidget(titlebar_check)

        ontop_check = QCheckBox("Always on top")
        ontop_check.setChecked(self.window_always_on_top)
        ui_layout.addWidget(ontop_check)

        ui_group.setLayout(ui_layout)
        appearance_layout.addWidget(ui_group)

        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")

        # === EXPORT TAB ===
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)

        # Default Export Settings
        export_group = QGroupBox("Default Export Version")
        export_form = QFormLayout()

        self.export_game_combo = QComboBox()
        self.export_game_combo.addItems([
            "Auto-detect", "GTA III", "Vice City", "San Andreas", "Manhunt"
        ])
        game_map = {"auto": 0, "gta3": 1, "vc": 2, "sa": 3, "manhunt": 4}
        self.export_game_combo.setCurrentIndex(game_map.get(self.export_target_game, 0))
        export_form.addRow("Target Game:", self.export_game_combo)

        self.export_platform_combo = QComboBox()
        self.export_platform_combo.addItems([
            "PC", "Xbox", "PS2", "Android", "Multi-platform"
        ])
        platform_map = {"pc": 0, "xbox": 1, "ps2": 2, "android": 3, "multi": 4}
        self.export_platform_combo.setCurrentIndex(platform_map.get(self.export_target_platform, 0))
        export_form.addRow("Target Platform:", self.export_platform_combo)

        export_group.setLayout(export_form)
        export_layout.addWidget(export_group)

        # Version Compatibility Warning
        compat_label = QLabel(
            "<b>Note:</b> Exporting to GTA III will automatically remove mipmaps and bumpmaps.\n"
            "Vice City PS2 also has limited support for these features."
        )
        compat_label.setWordWrap(True)
        compat_label.setStyleSheet("padding: 10px; background-color: #3a3a3a; border-radius: 4px;")
        export_layout.addWidget(compat_label)

        export_layout.addStretch()
        tabs.addTab(export_tab, "Export")

        # === TEXTURE CONSTRAINTS TAB ===
        constraints_tab = QWidget()
        constraints_layout = QVBoxLayout(constraints_tab)

        # Dimension constraints
        dimension_group = QGroupBox("Dimension Constraints")
        dimension_layout = QVBoxLayout()

        dimension_check = QCheckBox("Enforce power-of-2 dimensions")
        dimension_check.setChecked(self.dimension_limiting_enabled)
        dimension_check.setToolTip("Enforce sizes like 256, 512, 1024, 2048")
        dimension_layout.addWidget(dimension_check)

        splash_check = QCheckBox("Allow splash screen dimensions")
        splash_check.setChecked(self.splash_screen_mode)
        splash_check.setToolTip("Allow non-power-of-2 sizes like 1280x720, 720x576, 640x480")
        dimension_layout.addWidget(splash_check)

        max_dim_layout = QHBoxLayout()
        max_dim_layout.addWidget(QLabel("Maximum dimension:"))
        max_dim_spin = QSpinBox()
        max_dim_spin.setRange(256, 8192)
        max_dim_spin.setValue(self.custom_max_dimension)
        max_dim_spin.setSingleStep(256)
        max_dim_spin.setToolTip("Maximum width/height for imported textures")
        max_dim_layout.addWidget(max_dim_spin)
        max_dim_layout.addStretch()
        dimension_layout.addLayout(max_dim_layout)

        dimension_group.setLayout(dimension_layout)
        constraints_layout.addWidget(dimension_group)

        # Texture naming
        naming_group = QGroupBox("Texture Naming")
        naming_layout = QVBoxLayout()

        name_limit_check = QCheckBox("Enable name length limit")
        name_limit_check.setChecked(self.name_limit_enabled)
        name_limit_check.setToolTip("Enforce maximum texture name length")
        naming_layout.addWidget(name_limit_check)

        char_limit_layout = QHBoxLayout()
        char_limit_layout.addWidget(QLabel("Maximum characters:"))
        char_limit_spin = QSpinBox()
        char_limit_spin.setRange(8, 64)
        char_limit_spin.setValue(self.max_texture_name_length)
        char_limit_spin.setToolTip("RenderWare default is 32 characters")
        char_limit_layout.addWidget(char_limit_spin)
        char_limit_layout.addStretch()
        naming_layout.addLayout(char_limit_layout)

        naming_group.setLayout(naming_layout)
        constraints_layout.addWidget(naming_group)

        # Format support
        format_group = QGroupBox("Import Format Support")
        format_layout = QVBoxLayout()

        iff_check = QCheckBox("Enable IFF (Amiga) format import")
        iff_check.setChecked(self.iff_import_enabled)
        iff_check.setToolTip("Import 8-bit indexed color images from Amiga IFF format")
        format_layout.addWidget(iff_check)

        splash_format_check = QCheckBox("Enable splash screen TXD support")
        splash_format_check.setChecked(self.splash_formats_enabled)
        splash_format_check.setToolTip("Support GTA III/VC/SA splash screen formats")
        format_layout.addWidget(splash_format_check)

        format_group.setLayout(format_layout)
        constraints_layout.addWidget(format_group)

        constraints_layout.addStretch()
        tabs.addTab(constraints_tab, "Texture Constraints")

        # === PREVIEW TAB ===
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        preview_group = QGroupBox("Preview Settings")
        preview_form = QFormLayout()

        zoom_spin = QSpinBox()
        zoom_spin.setRange(10, 500)
        zoom_spin.setValue(int(self.zoom_level * 100))
        zoom_spin.setSuffix("%")
        preview_form.addRow("Default Zoom:", zoom_spin)

        bg_mode_combo = QComboBox()
        bg_mode_combo.addItems(["Solid Color", "Checkerboard", "Grid"])
        mode_idx = {"solid": 0, "checker": 1, "grid": 2}.get(self.background_mode, 0)
        bg_mode_combo.setCurrentIndex(mode_idx)
        preview_form.addRow("Background Mode:", bg_mode_combo)

        preview_group.setLayout(preview_form)
        preview_layout.addWidget(preview_group)
        preview_layout.addStretch()

        tabs.addTab(preview_tab, "Preview")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply")
        def apply_settings():
            # Fonts
            self.setFont(QFont(self.default_font_combo.currentFont().family(),
                            self.default_font_size.value()))
            self.title_font = QFont(self.title_font_combo.currentFont().family(),
                                self.title_font_size.value())
            self.panel_font = QFont(self.panel_font_combo.currentFont().family(),
                                self.panel_font_size.value())
            self.button_font = QFont(self.button_font_combo.currentFont().family(),
                                    self.button_font_size.value())
            self.infobar_font = QFont(self.infobar_font_combo.currentFont().family(),
                                    self.infobar_font_size.value())

            # Apply fonts to UI elements
            self._apply_title_font()
            self._apply_panel_font()
            self._apply_button_font()
            self._apply_infobar_font()

            # UI settings
            mode_map = {0: "icons", 1: "text", 2: "both"}
            self.button_display_mode = mode_map[self.settings_display_combo.currentIndex()]
            self._update_all_buttons()

            old_titlebar = self.use_system_titlebar
            self.use_system_titlebar = titlebar_check.isChecked()
            self.window_always_on_top = ontop_check.isChecked()

            if old_titlebar != self.use_system_titlebar:
                self._apply_window_flags()
            self._apply_always_on_top()

            # Export settings
            game_map = {0: "auto", 1: "gta3", 2: "vc", 3: "sa", 4: "manhunt"}
            self.export_target_game = game_map[self.export_game_combo.currentIndex()]

            platform_map = {0: "pc", 1: "xbox", 2: "ps2", 3: "android", 4: "multi"}
            self.export_target_platform = platform_map[self.export_platform_combo.currentIndex()]

            # Constraints
            self.dimension_limiting_enabled = dimension_check.isChecked()
            self.splash_screen_mode = splash_check.isChecked()
            self.custom_max_dimension = max_dim_spin.value()
            self.name_limit_enabled = name_limit_check.isChecked()
            self.max_texture_name_length = char_limit_spin.value()
            self.iff_import_enabled = iff_check.isChecked()
            self.splash_formats_enabled = splash_format_check.isChecked()

            # Preview
            self.zoom_level = zoom_spin.value() / 100.0
            bg_mode_map = {0: "solid", 1: "checker", 2: "grid"}
            self.background_mode = bg_mode_map[bg_mode_combo.currentIndex()]

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Settings applied")

        apply_btn.clicked.connect(apply_settings)
        button_layout.addWidget(apply_btn)

        # OK button
        ok_btn = QPushButton("OK")
        def ok_clicked():
            apply_settings()
            dialog.accept()
        ok_btn.clicked.connect(ok_clicked)
        button_layout.addWidget(ok_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _apply_window_flags(self): #vers 1
        """Apply window flags based on settings"""
        # Save current geometry
        current_geometry = self.geometry()
        was_visible = self.isVisible()

        if self.use_system_titlebar:
            # Use system window with title bar
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
        else:
            # Use custom frameless window
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Restore geometry and visibility
        self.setGeometry(current_geometry)

        if was_visible:
            self.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            mode = "System title bar" if self.use_system_titlebar else "Custom frameless"
            self.main_window.log_message(f"Window mode: {mode}")


    def _apply_always_on_top(self): #vers 1
        """Apply always on top window flag"""
        current_flags = self.windowFlags()

        if self.window_always_on_top:
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint

        if new_flags != current_flags:
            # Save state
            current_geometry = self.geometry()
            was_visible = self.isVisible()

            # Apply new flags
            self.setWindowFlags(new_flags)

            # Restore state
            self.setGeometry(current_geometry)
            if was_visible:
                self.show()



    def _scan_available_locales(self): #vers 2
        """Scan locale folder and return list of available languages"""
        import os
        import configparser

        locales = []
        locale_path = os.path.join(os.path.dirname(__file__), 'locale')

        if not os.path.exists(locale_path):
            # Easter egg: Amiga Workbench 3.1 style error
            self._show_amiga_locale_error()
            # Return default English
            return [("English", "en", None)]

        try:
            for filename in os.listdir(locale_path):
                if filename.endswith('.lang'):
                    filepath = os.path.join(locale_path, filename)

                    try:
                        config = configparser.ConfigParser()
                        config.read(filepath, encoding='utf-8')

                        if 'Metadata' in config:
                            lang_name = config['Metadata'].get('LanguageName', 'Unknown')
                            lang_code = config['Metadata'].get('LanguageCode', 'unknown')
                            locales.append((lang_name, lang_code, filepath))

                    except Exception as e:
                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message(f"Failed to load locale {filename}: {e}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Locale scan error: {e}")

        locales.sort(key=lambda x: x[0])

        if not locales:
            locales = [("English", "en", None)]

        return locales

    def _show_amiga_locale_error(self): #vers 1
        """Show Amiga Workbench 3.1 style error dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("Workbench Request")
        dialog.setFixedSize(450, 150)

        # Amiga Workbench styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #aaaaaa;
                border: 2px solid #ffffff;
            }
            QLabel {
                color: #000000;
                background-color: #aaaaaa;
            }
            QPushButton {
                background-color: #8899aa;
                color: #000000;
                border: 2px outset #ffffff;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:pressed {
                border: 2px inset #555555;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Amiga Topaz font style
        amiga_font = QFont("Courier", 10, QFont.Weight.Normal)

        # Error message
        message = QLabel("Workbench 3.1 installer\n\nPlease insert Local disk in any drive")
        message.setFont(amiga_font)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Retry and Cancel buttons (Amiga style)
        retry_btn = QPushButton("Retry")
        retry_btn.setFont(amiga_font)
        retry_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(retry_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(amiga_font)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()


    def _preserve_original_data(self, texture: Dict, texture_data: bytes, offset: int): #vers 1
        """
        Preserve original binary data to prevent corruption
        """
        try:
            # Store the ORIGINAL compressed/raw data
            # This prevents RGB corruption from channel swapping

            # Read texture native header (88 bytes)
            if len(texture_data) < offset + 88:
                return

            header_data = texture_data[offset:offset + 88]

            # Parse header to get data size
            platform_id = struct.unpack('<I', header_data[0:4])[0]
            filter_flags = struct.unpack('<I', header_data[4:8])[0]

            # Texture name at 8-40
            # Alpha name at 40-72

            raster_format = struct.unpack('<I', header_data[72:76])[0]
            d3d_format = struct.unpack('<I', header_data[76:80])[0]
            width = struct.unpack('<H', header_data[80:82])[0]
            height = struct.unpack('<H', header_data[82:84])[0]
            depth = struct.unpack('<B', header_data[84:85])[0]
            mipmap_count = struct.unpack('<B', header_data[85:86])[0]
            raster_type = struct.unpack('<B', header_data[86:87])[0]
            compression = struct.unpack('<B', header_data[87:88])[0]

            # Read total data size (comes after 88-byte header)
            if len(texture_data) >= offset + 92:
                total_data_size = struct.unpack('<I', texture_data[offset + 88:offset + 92])[0]

                # Store ORIGINAL compressed/raw texture data
                data_start = offset + 92
                data_end = data_start + total_data_size

                if len(texture_data) >= data_end:
                    original_data = texture_data[data_start:data_end]

                    # Store in texture dict - this is the KEY to preventing corruption
                    texture['original_binary_data'] = original_data
                    texture['original_header'] = header_data
                    texture['d3d_format'] = d3d_format
                    texture['raster_format'] = raster_format
                    texture['platform_id'] = platform_id

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"Preserved original data for: {texture['name']}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Warning: Could not preserve original data: {e}")


    def toggle_dock_mode(self): #vers 1
        """Toggle between docked and standalone mode"""
        if self.is_docked:
            self._undock_from_main()
        else:
            self._dock_to_main()

    def _dock_to_main(self): #vers 1
        """Dock TXD Workshop into IMG Factory as a tab"""
        if not self.main_window:
            print("No main window available for docking")
            return

        # Check if main window has tab system
        if not hasattr(self.main_window, 'content_tabs'):
            print("Main window does not support tabs")
            return

        # Create dock widget if it doesn't exist
        if not self.dock_widget:
            from PyQt6.QtWidgets import QWidget, QVBoxLayout
            self.dock_widget = QWidget()
            layout = QVBoxLayout(self.dock_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self)

        # Add as new tab
        tab_index = self.main_window.content_tabs.addTab(
            self.dock_widget,
            "TXD Workshop"
        )
        self.main_window.content_tabs.setCurrentIndex(tab_index)

        self.is_docked = True

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("TXD Workshop docked")

    def _undock_from_main(self): #vers 1
        """Undock TXD Workshop into standalone window"""
        if not self.main_window or not self.dock_widget:
            return

        # Remove from tabs
        if hasattr(self.main_window, 'content_tabs'):
            for i in range(self.main_window.content_tabs.count()):
                if self.main_window.content_tabs.widget(i) == self.dock_widget:
                    self.main_window.content_tabs.removeTab(i)
                    break

        # Remove from dock widget
        self.setParent(None)

        # Show as standalone window
        self.setWindowTitle("TXD Workshop - Standalone")
        self.resize(1200, 800)
        self.show()

        self.is_docked = False

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("TXD Workshop undocked")


    def _apply_button_mode(self, dialog): #vers 1
        """Apply button display mode"""
        mode_index = self.button_mode_combo.currentIndex()
        mode_map = {0: 'both', 1: 'icons', 2: 'text'}

        new_mode = mode_map[mode_index]

        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                mode_names = {0: 'Icons + Text', 1: 'Icons Only', 2: 'Text Only'}
                self.main_window.log_message(f"✨ Button style: {mode_names[mode_index]}")

        dialog.close()


    def _update_all_buttons(self): #vers 2
        """Update all buttons to match display mode"""
        buttons_to_update = [
            # Toolbar buttons
            ('open_img_btn', 'Open IMG'),
            ('open_txd_btn', 'Open TXD'),
            ('save_txd_btn', 'Save TXD'),
            ('import_btn', 'Import'),
            ('export_btn', 'Export'),
            ('export_all_btn', 'Export All'),
            ('flip_btn', 'Switch'),
            ('props_btn', 'Properties'),
            ('info_btn', 'Info'),
            ('undo_btn', 'Undo'),
            ('paint_btn', 'Paint'),
            ('build_from_dff_btn', 'Build from DFF'),
            # Transform buttons
            ('flip_vert_btn', 'Flip Vertical'),
            ('flip_horz_btn', 'Flip Horizontal'),
            ('rotate_cw_btn', 'Rotate 90° CW"'),
            ('rotate_ccw_btn', 'Rotate 90° CCW"'),
            ('copy_btn', 'Copy'),
            ('paste_btn', 'Paste'),
            ('edit_btn', 'Edit'),
            ('convert_btn', 'Convert'),
            # Manage buttons
            ('create_texture_btn', 'Create'),
            ('delete_texture_btn', 'Delete'),
            ('duplicate_texture_btn', 'Duplicate'),
            # Effects buttons
            ('filters_btn', 'Filters'),
            ('paint_btn', 'Paint'),
            ('check_dff_btn', 'Check Dff'),
            # Format/Size buttons
            ('bitdepth_btn', 'Bit Depth'),
            ('resize_btn', 'Resize'),
            ('upscale_btn', 'Upscale'),
            ('compress_btn', 'Compress'),
            ('uncompress_btn', 'Uncompress'),
            # Mipmap buttons
            ('show_mipmaps_btn', 'View'),
            ('create_mipmaps_btn', 'Create'),
            ('remove_mipmaps_btn', 'Remove'),
            # Bumpmap buttons
            ('view_bumpmap_btn', 'View'),
            ('export_bumpmap_btn', 'Export'),
            ('import_bumpmap_btn', 'Import'),
        ]

        # Adjust transform panel width based on mode
        if hasattr(self, 'transform_panel'):
            if self.button_display_mode == 'icons':
                self.transform_panel.setMaximumWidth(50)
            else:
                self.transform_panel.setMaximumWidth(200)

        for btn_name, btn_text in buttons_to_update:
            if hasattr(self, btn_name):
                button = getattr(self, btn_name)
                self._apply_button_mode_to_button(button, btn_text)


    def _apply_button_mode_to_button(self, button, text): #vers 5
        """Apply display mode to a single button with proper spacing"""
        # Store original icon if not already stored
        if not hasattr(button, '_original_icon'):
            button._original_icon = button.icon()

        if self.button_display_mode == 'icons':
            # Icons only - SQUARE buttons like transform panel
            button.setText("")
            if not button._original_icon.isNull():
                button.setIcon(button._original_icon)
                button.setIconSize(QSize(20, 20))
            button.setFixedSize(40, 40)  # SQUARE - match transform panel

        elif self.button_display_mode == 'text':
            # Text only - auto-size for text
            button.setText(text)
            button.setIcon(QIcon())
            button.setMinimumWidth(60)
            button.setMaximumWidth(16777215)
            button.setMinimumHeight(0)  # Remove fixed height
            button.setMaximumHeight(16777215)

        elif self.button_display_mode == 'both':
            # Icons + Text - auto-size for both
            button.setText(text)
            if not button._original_icon.isNull():
                button.setIcon(button._original_icon)
                button.setIconSize(QSize(20, 20))
            button.setMinimumWidth(0)
            button.setMaximumWidth(16777215)
            button.setMinimumHeight(0)  # Remove fixed height
            button.setMaximumHeight(16777215)


    def _on_display_mode_changed(self, text): #vers 2
        """Handle display mode combo box change"""
        mode_map = {
            "Icons Only": "icons",
            "Text Only": "text",
            "Both": "both"
        }

        old_mode = self.button_display_mode
        self.button_display_mode = mode_map.get(text, "both")

        # If switching to/from icon mode, rebuild the info panel
        if (old_mode == 'icons' or self.button_display_mode == 'icons') and old_mode != self.button_display_mode:
            self._rebuild_info_panel()
        else:
            self._update_all_buttons()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Button display: {text}")

    def _rebuild_info_panel(self): #vers 1
        """Rebuild texture info panel with new layout"""
        # Find and remove old info group
        for i in range(self.right_panel.layout().count()):
            item = self.right_panel.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QGroupBox) and widget.title() == "":
                    widget.deleteLater()
                    break

        # Create new info group
        info_group = QGroupBox("")
        info_layout = QVBoxLayout(info_group)

        # Lines 2 & 3: Adaptive
        if self.button_display_mode == 'icons':
            merged_line = self._create_merged_icons_line()
            info_layout.addLayout(merged_line)
        else:

            # Add to right panel
            self.right_panel.layout().addWidget(info_group)


    def _create_merged_icons_line(self): #vers 1
        """Create compact single-line layout for icon mode - merges Line 2 and Line 3"""
        merged_layout = QHBoxLayout()
        merged_layout.setSpacing(2)
        merged_layout.setContentsMargins(0, 0, 0, 0)

        # --- Format controls ---
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444", "RGB888", "RGB565"])
        self.format_combo.currentTextChanged.connect(self._change_format)
        self.format_combo.setEnabled(False)
        self.format_combo.setMaximumWidth(100)
        info_layout.addWidget(self.format_combo)

        self.info_bitdepth = QLabel("[32bit]")
        self.info_bitdepth.setMinimumWidth(50)
        info_layout.addWidget(self.info_bitdepth)

        # --- Bit depth / resize / upscale / compress ---
        self.bitdepth_btn = QPushButton("Bit Depth")
        self.bitdepth_btn.setIcon(self._create_bitdepth_icon())
        self.bitdepth_btn.setIconSize(QSize(20, 20))
        self.bitdepth_btn.setToolTip("Change bit depth")
        self.bitdepth_btn.clicked.connect(self._change_bit_depth)
        self.bitdepth_btn.setEnabled(False)
        info_layout.addWidget(self.bitdepth_btn)

        self.resize_btn = QPushButton("Resize")
        self.resize_btn.setIcon(self._create_resize_icon())
        self.resize_btn.setIconSize(QSize(20, 20))
        self.resize_btn.setToolTip("Resize texture")
        self.resize_btn.clicked.connect(self._resize_texture)
        self.resize_btn.setEnabled(False)
        info_layout.addWidget(self.resize_btn)

        self.upscale_btn = QPushButton("AI Upscale")
        self.upscale_btn.setIcon(self._create_upscale_icon())
        self.upscale_btn.setIconSize(QSize(20, 20))
        self.upscale_btn.setToolTip("AI upscale texture")
        self.upscale_btn.clicked.connect(self._upscale_texture)
        self.upscale_btn.setEnabled(False)
        info_layout.addWidget(self.upscale_btn)

        self.compress_btn = QPushButton("Compress")
        self.compress_btn.setIcon(self._create_compress_icon())
        self.compress_btn.setIconSize(QSize(20, 20))
        self.compress_btn.setToolTip("Compress texture")
        self.compress_btn.clicked.connect(self._compress_texture)
        self.compress_btn.setEnabled(False)
        info_layout.addWidget(self.compress_btn)

        self.uncompress_btn = QPushButton("Uncompress")
        self.uncompress_btn.setIcon(self._create_uncompress_icon())
        self.uncompress_btn.setIconSize(QSize(20, 20))
        self.uncompress_btn.setToolTip("Uncompress texture")
        self.uncompress_btn.clicked.connect(self._uncompress_texture)
        self.uncompress_btn.setEnabled(False)
        info_layout.addWidget(self.uncompress_btn)
        info_layout.addSpacing(30)

        # --- Mipmap section ---
        self.info_format = QLabel("Mipmaps: ")
        self.info_format.setFont(self.panel_font)
        self.info_format.setMinimumWidth(100)
        info_layout.addWidget(self.info_format)

        self.show_mipmaps_btn = QPushButton("View")
        self.show_mipmaps_btn.setIcon(self._create_view_icon())
        self.show_mipmaps_btn.setIconSize(QSize(20, 20))
        self.show_mipmaps_btn.setToolTip("View all mipmap levels")
        self.show_mipmaps_btn.clicked.connect(self._open_mipmap_manager)
        self.show_mipmaps_btn.setEnabled(False)
        info_layout.addWidget(self.show_mipmaps_btn)

        self.create_mipmaps_btn = QPushButton("Create")
        self.create_mipmaps_btn.setIcon(self._create_add_icon())
        self.create_mipmaps_btn.setIconSize(QSize(20, 20))
        self.create_mipmaps_btn.setToolTip("Generate mipmaps")
        self.create_mipmaps_btn.clicked.connect(self._create_mipmaps_dialog)
        self.create_mipmaps_btn.setEnabled(False)
        info_layout.addWidget(self.create_mipmaps_btn)

        self.remove_mipmaps_btn = QPushButton("Remove")
        self.remove_mipmaps_btn.setIcon(self._create_delete_icon())
        self.remove_mipmaps_btn.setIconSize(QSize(20, 20))
        self.remove_mipmaps_btn.setToolTip("Remove all mipmaps")
        self.remove_mipmaps_btn.clicked.connect(self._remove_mipmaps)
        self.remove_mipmaps_btn.setEnabled(False)
        info_layout.addWidget(self.remove_mipmaps_btn)

        self.info_format_b = QLabel("Bumpmaps: ")
        self.info_format_b.setFont(self.panel_font)
        self.info_format_b.setMinimumWidth(120)
        info_layout.addWidget(self.info_format_b)

        self.view_bumpmap_btn = QPushButton("Manage")
        self.view_bumpmap_btn.setFont(self.button_font)
        self.view_bumpmap_btn.setIcon(self.create_manage_icon())
        self.view_bumpmap_btn.setIconSize(QSize(20, 20))
        self.view_bumpmap_btn.setToolTip("View and Manage bumpmaps")
        self.view_bumpmap_btn.clicked.connect(self._view_bumpmap)
        self.view_bumpmap_btn.setEnabled(False)
        info_layout.addWidget(self.view_bumpmap_btn)

        self.export_bumpmap_btn = QPushButton("Export")
        self.export_bumpmap_btn.setFont(self.button_font)
        self.export_bumpmap_btn.setIcon(self._create_export_icon())
        self.export_bumpmap_btn.setIconSize(QSize(20, 20))
        self.export_bumpmap_btn.setToolTip("Export bumpmap as PNG")
        self.export_bumpmap_btn.clicked.connect(self._export_bumpmap)
        self.export_bumpmap_btn.setEnabled(False)
        info_layout.addWidget(self.export_bumpmap_btn)

        self.import_bumpmap_btn = QPushButton("Import")
        self.import_bumpmap_btn.setFont(self.button_font)
        self.import_bumpmap_btn.setIcon(self._create_import_icon())
        self.import_bumpmap_btn.setIconSize(QSize(20, 20))
        self.import_bumpmap_btn.setToolTip("Import bumpmap from image")
        self.import_bumpmap_btn.clicked.connect(self._import_bumpmap)
        self.import_bumpmap_btn.setEnabled(False)
        info_layout.addWidget(self.import_bumpmap_btn)

        merged_layout.addStretch()

        return merged_layout


    def _initialize_features(self): #vers 3
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self._update_status_indicators()

            if hasattr(self, 'format_filter'):
                self.format_filter.setCurrentIndex(0)
            if hasattr(self, 'size_filter'):
                self.size_filter.setCurrentIndex(0)
            if hasattr(self, 'alpha_filter'):
                self.alpha_filter.setCurrentIndex(0)

            self._clear_texture_search()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("TXD Workshop features initialized")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Feature init error: {str(e)}")



    def _detect_txd_info(self, txd_data: bytes) -> bool: #vers 1
        """
        Detect and store TXD version and platform information
        Called when loading any TXD file
        """
        try:
            # Validate format first
            is_valid, message = validate_txd_format(txd_data)

            if not is_valid:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"TXD Validation: {message}")
                return False

            # Detect version info
            self.txd_version_id, self.txd_device_id, self.txd_version_str = detect_txd_version(txd_data)

            # Get platform and game info
            self.txd_platform_name = get_platform_name(self.txd_device_id)
            self.txd_game = get_game_from_version(self.txd_version_id, self.txd_device_id)

            # Get capabilities
            self.txd_capabilities = get_version_capabilities(self.txd_version_id)

            # Log detection
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"TXD: {self.txd_version_str} | "
                    f"Platform: {self.txd_platform_name} | "
                    f"Game: {self.txd_game}"
                )

            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Version detection error: {str(e)}")
            return False


    def paintEvent(self, event): #vers 2
        """Paint corner resize triangles"""
        super().paintEvent(event)

        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        normal_color = QColor(100, 100, 100, 150)
        hover_color = QColor(150, 150, 255, 200)

        w = self.width()
        h = self.height()
        size = self.corner_size

        # Define corner triangles
        corners = {
            'top-left': [(0, 0), (size, 0), (0, size)],
            'top-right': [(w, 0), (w-size, 0), (w, size)],
            'bottom-left': [(0, h), (size, h), (0, h-size)],
            'bottom-right': [(w, h), (w-size, h), (w, h-size)]
        }

        for corner_name, points in corners.items():
            # Choose color based on hover state
            if self.hover_corner == corner_name:
                painter.setBrush(QBrush(hover_color))
                painter.setPen(QPen(hover_color.darker(120), 1))
            else:
                painter.setBrush(QBrush(normal_color))
                painter.setPen(QPen(normal_color.darker(120), 1))

            # Draw triangle
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()

            painter.drawPath(path)

        painter.end()


    def _get_resize_corner(self, pos): #vers 2
        """Determine which corner is under mouse position"""
        size = self.corner_size
        w = self.width()
        h = self.height()

        # Top-left corner
        if pos.x() < size and pos.y() < size:
            return "top-left"

        # Top-right corner
        if pos.x() > w - size and pos.y() < size:
            return "top-right"

        # Bottom-left corner
        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"

        # Bottom-right corner
        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    def mousePressEvent(self, event): #vers 2
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on corner
            self.resize_corner = self._get_resize_corner(event.pos())

            if self.resize_corner:
                self.resizing = True
                self.drag_position = event.globalPosition().toPoint()
                self.initial_geometry = self.geometry()
            else:
                # Check if clicking on toolbar for dragging
                if self._is_on_draggable_area(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

            event.accept()


    def mouseMoveEvent(self, event): #vers 2
        """Handle mouse move for dragging, resizing, and hover effects"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_corner:
                self._handle_corner_resize(event.globalPosition().toPoint())
            elif self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # Update hover state and cursor
            corner = self._get_resize_corner(event.pos())
            if corner != self.hover_corner:
                self.hover_corner = corner
                self.update()  # Trigger repaint for hover effect
            self._update_cursor(corner)


    def mouseReleaseEvent(self, event): #vers 2
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()


    def _handle_corner_resize(self, global_pos): #vers 2
        """Handle window resizing from corners"""
        if not self.resize_corner or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        # Calculate new geometry based on corner
        if self.resize_corner == "top-left":
            # Move top-left corner
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            # Move top-right corner
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            # Move bottom-left corner
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            # Move bottom-right corner
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)


    def resizeEvent(self, event): #vers 1
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)


    def _get_resize_direction(self, pos): #vers 1
        """Determine resize direction based on mouse position"""
        rect = self.rect()
        margin = self.resize_margin

        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin

        if left and top:
            return "top-left"
        elif right and top:
            return "top-right"
        elif left and bottom:
            return "bottom-left"
        elif right and bottom:
            return "bottom-right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"

        return None


    def _update_cursor(self, direction): #vers 1
        """Update cursor based on resize direction"""
        if direction == "top" or direction == "bottom":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif direction == "left" or direction == "right":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction == "top-left" or direction == "bottom-right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def _handle_resize(self, global_pos): #vers 1
        """Handle window resizing"""
        if not self.resize_direction or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.frameGeometry()

        min_width = 800
        min_height = 600

        # Handle horizontal resizing
        if "left" in self.resize_direction:
            new_width = geometry.width() - delta.x()
            if new_width >= min_width:
                geometry.setLeft(geometry.left() + delta.x())
        elif "right" in self.resize_direction:
            new_width = geometry.width() + delta.x()
            if new_width >= min_width:
                geometry.setRight(geometry.right() + delta.x())

        # Handle vertical resizing
        if "top" in self.resize_direction:
            new_height = geometry.height() - delta.y()
            if new_height >= min_height:
                geometry.setTop(geometry.top() + delta.y())
        elif "bottom" in self.resize_direction:
            new_height = geometry.height() + delta.y()
            if new_height >= min_height:
                geometry.setBottom(geometry.bottom() + delta.y())

        self.setGeometry(geometry)
        self.drag_position = global_pos


    def mouseDoubleClickEvent(self, event): #vers 1
        """Handle double-click on toolbar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_on_draggable_area(event.pos()):
                self._toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)


    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def _enable_txd_features_after_load(self): #vers 1
        """Enable TXD features after successful texture load"""
        if self.texture_list:
            self.save_txd_btn.setEnabled(False)
            self.import_btn.setEnabled(True)
            self.export_all_btn.setEnabled(True)

            if hasattr(self, 'new_texture_btn'):
                self.new_texture_btn.setEnabled(True)
            if hasattr(self, 'stats_btn'):
                self.stats_btn.setEnabled(True)

            self._update_status_indicators()


    def _is_on_draggable_area(self, pos): #vers 3
        """Check if position is on draggable toolbar area (stretch space, not buttons)"""
        if not hasattr(self, 'toolbar'):
            return False

        toolbar_rect = self.toolbar.geometry()
        if not toolbar_rect.contains(pos):
            return False

        # Get all buttons in toolbar
        buttons_to_check = []

        if hasattr(self, 'open_img_btn'):
            buttons_to_check.append(self.open_img_btn)
        if hasattr(self, 'open_txd_btn'):
            buttons_to_check.append(self.open_txd_btn)
        if hasattr(self, 'save_txd_btn'):
            buttons_to_check.append(self.save_txd_btn)
        if hasattr(self, 'import_btn'):
            buttons_to_check.append(self.import_btn)
        if hasattr(self, 'export_btn'):
            buttons_to_check.append(self.export_btn)
        if hasattr(self, 'export_all_btn'):
            buttons_to_check.append(self.export_all_btn)
        if hasattr(self, 'flip_btn'):
            buttons_to_check.append(self.flip_btn)
        if hasattr(self, 'props_btn'):
            buttons_to_check.append(self.props_btn)
        if hasattr(self, 'info_btn'):
            buttons_to_check.append(self.info_btn)
        if hasattr(self, 'minimize_btn'):
            buttons_to_check.append(self.minimize_btn)
        if hasattr(self, 'maximize_btn'):
            buttons_to_check.append(self.maximize_btn)
        if hasattr(self, 'close_btn'):
            buttons_to_check.append(self.close_btn)
        # Should be enabled on selection:
        if hasattr(self, 'undo_btn'):
            # Undo depends on undo stack, not selection
            self.undo_btn.setEnabled(len(self.undo_stack) > 0)

        if hasattr(self, 'check_dff_btn'):
            # Always enabled if textures exist
            self.check_dff_btn.setEnabled(len(self.texture_list) > 0)

        if not hasattr(self, 'drag_btn'):
            return False

        # Convert to toolbar coordinates
        toolbar_local_pos = self.toolbar.mapFrom(self, pos)

        # Check if clicking on drag button
        return self.drag_btn.geometry().contains(toolbar_local_pos)

        # Check if position is NOT on any button (i.e., on stretch area)
        for btn in buttons_to_check:
            btn_global_rect = btn.geometry()
            btn_rect = btn_global_rect.translated(toolbar_rect.topLeft())
            if btn_rect.contains(pos):
                return False  # On a button, not draggable

        return True  # On empty stretch area, draggable


    def _setup_status_indicators(self): #vers 5
        """Setup status indicators with texture info and visible resize button"""
        self.status_frame = QFrame()
        self.status_layout = QHBoxLayout(self.status_frame)
        self.status_layout.setContentsMargins(5, 2, 5, 2)

        self.status_textures = QLabel("Textures: 0")
        self.status_layout.addWidget(self.status_textures)

        self.status_selected = QLabel("Selected: None")
        self.status_layout.addWidget(self.status_selected)

        self.status_size = QLabel("TXD Size: Unknown")
        self.status_layout.addWidget(self.status_size)

        self.status_layout.addStretch()

        self.status_modified = QLabel("")
        self.status_layout.addWidget(self.status_modified)

        # NEW: Texture dimension info
        self.info_size = QLabel("Size: -")
        self.status_layout.addWidget(self.info_size)

        # NEW: Texture format info
        self.format_status_label = QLabel("Format: -")
        self.status_layout.addWidget(self.format_status_label)

        # Add visible resize button with icon
        self.resize_grip_btn = QPushButton()
        self.resize_grip_btn.setIcon(self._create_resize_icon())
        self.resize_grip_btn.setIconSize(QSize(20, 20))
        self.resize_grip_btn.setFixedSize(20, 20)
        self.resize_grip_btn.setToolTip("Drag to resize window")
        self.resize_grip_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        # Make it act like a resize grip
        self.resize_grip_btn.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.status_layout.addWidget(self.resize_grip_btn)

        return self.status_frame


    def _create_toolbar(self): #vers 9
        """Create toolbar with drag and tear-off buttons"""
        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(self.toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setFont(self.button_font)
        self.settings_btn.setIcon(self._create_settings_icon())
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.clicked.connect(self._show_workshop_settings)
        self.settings_btn.setToolTip("Workshop Settings")
        layout.addWidget(self.settings_btn)

        layout.addStretch()

        # Only show "Open IMG" button if NOT standalone
        if not self.standalone_mode:
            self.open_img_btn = QPushButton("OpenIMG")
            self.open_img_btn.setFont(self.button_font)
            self.open_img_btn.setIcon(self._create_folder_icon())
            self.open_img_btn.setIconSize(QSize(20, 20))
            self.open_img_btn.clicked.connect(self.open_img_archive)
            layout.addWidget(self.open_img_btn)

        self.open_txd_btn = QPushButton("OpenTXD")
        self.open_txd_btn.setFont(self.button_font)
        self.open_txd_btn.setIcon(self._create_file_icon())
        self.open_txd_btn.setIconSize(QSize(20, 20))
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("SaveTXD")
        self.save_txd_btn.setFont(self.button_font)
        self.save_txd_btn.setIcon(self._create_save_icon())
        self.save_txd_btn.setIconSize(QSize(20, 20))
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        layout.addSpacing(10)

        self.import_btn = QPushButton("Import")
        self.import_btn.setFont(self.button_font)
        self.import_btn.setIcon(self._create_import_icon())
        self.import_btn.setIconSize(QSize(20, 20))
        self.import_btn.clicked.connect(self._import_textures)
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFont(self.button_font)
        self.export_btn.setIcon(self._create_export_icon())
        self.export_btn.setIconSize(QSize(20, 20))
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.setFont(self.button_font)
        self.export_all_btn.setIcon(self._create_package_icon())
        self.export_all_btn.setIconSize(QSize(20, 20))
        self.export_all_btn.clicked.connect(self.export_all_textures)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)

        layout.addSpacing(10)

        self.flip_btn = QPushButton("Switch")
        self.flip_btn.setFont(self.button_font)
        self.flip_btn.setIcon(self._create_flip_vert_icon())
        self.flip_btn.setIconSize(QSize(20, 20))
        self.flip_btn.clicked.connect(self.flip_texture)
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        # Properties button
        self.props_btn = QPushButton()
        self.props_btn.setFont(self.button_font)
        self.props_btn.setIcon(self._create_properties_icon())
        self.props_btn.setText("Properties")
        self.props_btn.setIconSize(QSize(20, 20))
        self.props_btn.clicked.connect(self.show_properties)
        self.props_btn.setEnabled(False)
        self.props_btn.setToolTip("Show texture properties")
        layout.addWidget(self.props_btn)

        self.undo_btn = QPushButton()
        self.undo_btn.setFont(self.button_font)
        self.undo_btn.setIcon(self._create_undo_icon())
        self.undo_btn.setText("Undo")
        self.undo_btn.setIconSize(QSize(20, 20))
        self.undo_btn.clicked.connect(self._undo_last_action)
        #self.undo_btn.setEnabled(False)
        self.undo_btn.setToolTip("Undo last action")
        layout.addWidget(self.undo_btn)

        # Info button
        self.info_btn = QPushButton()
        self.info_btn.setFont(self.button_font)
        self.info_btn.setIcon(self._create_info_icon())
        self.info_btn.setText("Info")
        self.info_btn.setIconSize(QSize(20, 20))
        self.info_btn.clicked.connect(self._show_txd_info)
        self.info_btn.setToolTip("Show TXD file information")
        layout.addWidget(self.info_btn)


        layout.addStretch()

        # Drag button [D]
        self.dock_btn = QPushButton("D")
        #self.dock_btn.setFont(self.button_font)
        self.dock_btn.setMinimumWidth(40)
        self.dock_btn.setMaximumWidth(40)
        self.dock_btn.setMinimumHeight(30)
        self.dock_btn.setToolTip("Dock")
        self.dock_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        self.dock_btn.clicked.connect(self.toggle_dock_mode)
        layout.addWidget(self.dock_btn)

        # Tear-off button [T] - only in IMG Factory mode
        if not self.standalone_mode:
            self.tearoff_btn = QPushButton("T")
            #self.tearoff_btn.setFont(self.button_font)
            self.tearoff_btn.setMinimumWidth(40)
            self.tearoff_btn.setMaximumWidth(40)
            self.tearoff_btn.setMinimumHeight(30)
            self.tearoff_btn.clicked.connect(self._toggle_tearoff)
            self.tearoff_btn.setToolTip("Merge back to IMG Factory window")
            self.tearoff_btn.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    background-color: #4a4a4a;
                    border: 1px solid #5a5a5a;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            layout.addWidget(self.tearoff_btn)

        # Window controls
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(self._create_minimize_icon())
        self.minimize_btn.setIconSize(QSize(20, 20))
        self.minimize_btn.setMinimumWidth(40)
        self.minimize_btn.setMaximumWidth(40)
        self.minimize_btn.setMinimumHeight(30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize Window")
        layout.addWidget(self.minimize_btn)

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self._create_maximize_icon())
        self.maximize_btn.setIconSize(QSize(20, 20))
        self.maximize_btn.setMinimumWidth(40)
        self.maximize_btn.setMaximumWidth(40)
        self.maximize_btn.setMinimumHeight(30)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize/Restore Window")
        layout.addWidget(self.maximize_btn)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setIconSize(QSize(20, 20))
        self.close_btn.setMinimumWidth(40)
        self.close_btn.setMaximumWidth(40)
        self.close_btn.setMinimumHeight(30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close Window")
        layout.addWidget(self.close_btn)

        return self.toolbar


    def _create_mipmaps_dialog(self): #vers 1
        """Open dialog to create mipmaps with depth selection"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
        import math

        # Calculate possible mipmap levels
        width = self.selected_texture.get('width', 256)
        height = self.selected_texture.get('height', 256)
        max_dimension = max(width, height)

        # Calculate how many levels possible (down to 1x1)
        max_levels = int(math.log2(max_dimension)) + 1

        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Mipmaps")
        dialog.setModal(True)
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        # Header info
        header = QLabel(f"Texture: {self.selected_texture['name']}\n"
                    f"Size: {width}x{height}\n\n"
                    f"Select minimum mipmap size:")
        header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Slider with level preview
        slider_layout = QVBoxLayout()

        mipmap_slider = QSlider(Qt.Orientation.Horizontal)
        mipmap_slider.setMinimum(0)  # Down to 1x1
        mipmap_slider.setMaximum(max_levels - 1)
        mipmap_slider.setValue(max(0, max_levels - 6))  # Default to ~32x32
        mipmap_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        mipmap_slider.setTickInterval(1)

        # Preview label showing dimensions at each level
        mipmap_preview = QLabel()
        mipmap_preview.setStyleSheet("font-size: 14px; padding: 10px; "
                                    "background: #2a2a2a; border-radius: 3px;")
        mipmap_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_preview(value):
            # Calculate dimensions at this level
            levels_from_top = max_levels - 1 - value
            min_w = max(1, width >> levels_from_top)
            min_h = max(1, height >> levels_from_top)
            num_levels = max_levels - value

            preview_text = f"Minimum Size: {min_w}x{min_h}\n"
            preview_text += f"Total Levels: {num_levels}\n\n"
            preview_text += f"Levels: {width}x{height}"

            # Show a few intermediate levels
            current_w, current_h = width, height
            shown = 1
            for i in range(1, num_levels):
                current_w = max(1, current_w // 2)
                current_h = max(1, current_h // 2)
                if shown < 4 or i == num_levels - 1:  # Show first 3 and last
                    preview_text += f" → {current_w}x{current_h}"
                    shown += 1
                elif shown == 4:
                    preview_text += " → ..."
                    shown += 1

            mipmap_preview.setText(preview_text)

        mipmap_slider.valueChanged.connect(update_preview)
        update_preview(mipmap_slider.value())

        slider_layout.addWidget(QLabel("More Levels ←  →  Fewer Levels"))
        slider_layout.addWidget(mipmap_slider)
        slider_layout.addWidget(mipmap_preview)

        layout.addLayout(slider_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_generate():
            slider_value = mipmap_slider.value()
            num_levels = max_levels - slider_value
            dialog.accept()

            # Generate mipmaps
            if hasattr(self, '_auto_generate_mipmaps_to_level'):
                self._auto_generate_mipmaps_to_level(num_levels)
            else:
                self._auto_generate_mipmaps()

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(do_generate)
        button_layout.addWidget(generate_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _remove_mipmaps(self): #vers 1
        """Remove all mipmap levels except Level 0"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        mipmap_levels = self.selected_texture.get('mipmap_levels', [])
        if len(mipmap_levels) <= 1:
            QMessageBox.information(self, "No Mipmaps",
                                "This texture has no mipmap levels to remove")
            return

        reply = QMessageBox.question(
            self, "Remove Mipmaps",
            f"Remove all mipmap levels from '{self.selected_texture['name']}'?\n\n"
            f"This will keep only Level 0 (main texture).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Keep only level 0
            level_0 = next((l for l in mipmap_levels if l.get('level') == 0), None)

            if level_0:
                self.selected_texture['mipmap_levels'] = [level_0]
                self.selected_texture['mipmaps'] = 1
            else:
                # No level 0 found, create it from main texture data
                self.selected_texture['mipmap_levels'] = [{
                    'level': 0,
                    'width': self.selected_texture['width'],
                    'height': self.selected_texture['height'],
                    'rgba_data': self.selected_texture['rgba_data'],
                    'compressed_data': None,
                    'compressed_size': len(self.selected_texture.get('rgba_data', b''))
                }]
                self.selected_texture['mipmaps'] = 1

            # Update display
            self._save_undo_state("Remove mipmaps")
            self._update_texture_info(self.selected_texture)
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Removed mipmaps from: {self.selected_texture['name']}")


    def _toggle_tearoff(self): #vers 1
        """Toggle tear-off state (merge back to IMG Factory)"""
        QMessageBox.information(self, "Tear-off",
            "Merge back to IMG Factory functionality coming soon!\n\n"
            "This will dock the TXD Workshop back into the main window.")


    def _on_texture_table_double_click(self, item): #vers 1
        """Handle double-click on texture table - open mipmap manager"""
        try:
            row = item.row()

            # Get texture for this row
            if row < 0 or row >= len(self.texture_list):
                return

            texture = self.texture_list[row]

            # Check if texture has mipmaps
            mipmap_levels = texture.get('mipmap_levels', [])
            if len(mipmap_levels) > 1:
                # Has mipmaps - open mipmap manager
                self.selected_texture = texture
                self._open_mipmap_manager()
            else:
                # No mipmaps - just select the texture
                self.selected_texture = texture
                self._update_texture_info(texture)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Double-click error: {str(e)}")


    def _create_right_panel(self): #vers 10
        """Create right panel with editing controls - compact layout"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)
        has_bumpmap = False

        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(5, 5, 5, 5)

        top_layout = QHBoxLayout()

        # Transform panel (left)
        transform_panel = self._create_transform_panel()
        top_layout.addWidget(transform_panel, stretch=1)

        # Preview area (center)
        self.preview_widget = ZoomablePreview(self)
        top_layout.addWidget(self.preview_widget, stretch=2)

        # Preview controls (right side, vertical)
        preview_controls = self._create_preview_controls()
        top_layout.addWidget(preview_controls, stretch=0)
        main_layout.addLayout(top_layout, stretch=1)


        # Information group below
        info_group = QGroupBox("")
        info_group.setFont(self.title_font)
        info_layout = QVBoxLayout(info_group)
        info_group.setMaximumHeight(140)

        # === LINE 1: Texture name and alpha name ===
        name_layout = QHBoxLayout()

        name_label = QLabel("Name:")
        name_label.setFont(self.panel_font)
        name_layout.addWidget(name_label)

        self.info_name = QLineEdit()

        self.info_name.setPlaceholderText("Click to edit...")
        self.info_name.setFont(self.panel_font)
        self.info_name.setReadOnly(True)
        self.info_name.setStyleSheet("padding: px; border: 1px solid #3a3a3a;")
        self.info_name.returnPressed.connect(self._save_texture_name)
        self.info_name.editingFinished.connect(self._save_texture_name)
        self.info_name.mousePressEvent = lambda e: self._enable_name_edit(e, False)
        name_layout.addWidget(self.info_name, stretch=1)

        self.alpha_label = QLabel("Alpha:")
        self.alpha_label.setFont(self.panel_font)
        self.alpha_label.setStyleSheet("color: red;")
        self.alpha_label.setVisible(False)
        name_layout.addWidget(self.alpha_label)

        self.info_alpha_name = QLineEdit()
        self.info_alpha_name.setFont(self.panel_font)
        self.info_alpha_name.setPlaceholderText("Click to edit...")
        self.info_alpha_name.setReadOnly(True)
        self.info_alpha_name.setStyleSheet("color: red; padding: 5px; border: 1px solid #3a3a3a;")
        self.info_alpha_name.returnPressed.connect(self._save_alpha_name)
        self.info_alpha_name.editingFinished.connect(self._save_alpha_name)
        self.info_alpha_name.mousePressEvent = lambda e: self._enable_name_edit(e, True)
        self.info_alpha_name.setVisible(False)
        name_layout.addWidget(self.info_alpha_name, stretch=1)

        info_layout.addLayout(name_layout)

        # === LINES 2 & 3: Adaptive based on display mode ===
        if self.button_display_mode == 'icons':
            # MERGED: Single compact line for icon mode
            merged_line = self._create_merged_icons_line()
            info_layout.addLayout(merged_line)
        else:
            # SEPARATE: Original two-line layout for text/both modes
            # Line 2: Format controls
            format_layout = QHBoxLayout()
            format_layout.setSpacing(5)

            self.format_combo = QComboBox()
            self.format_combo.setFont(self.panel_font)
            self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444", "RGB888", "RGB565"])
            self.format_combo.currentTextChanged.connect(self._change_format)
            self.format_combo.setEnabled(False)
            self.format_combo.setMaximumWidth(100)
            format_layout.addWidget(self.format_combo)

            self.info_bitdepth.setFont(self.panel_font)
            self.info_bitdepth = QLabel("[32bit]")
            self.info_bitdepth.setMinimumWidth(50)
            format_layout.addWidget(self.info_bitdepth)

            format_layout.addStretch()

            # Convert
            self.convert_btn = QPushButton("Convert")
            self.convert_btn.setFont(self.button_font)
            self.convert_btn.setIcon(self._create_convert_icon())
            self.convert_btn.setIconSize(QSize(20, 20))
            self.convert_btn.setToolTip("Convert texture format")
            self.convert_btn.clicked.connect(self._convert_texture)
            self.convert_btn.setEnabled(False)
            format_layout.addWidget(self.convert_btn)

            # Line 3: Mipmaps + Bumpmaps
            mipbump_layout = QHBoxLayout()
            mipbump_layout.setSpacing(5)

            self.info_format = QLabel("Mipmaps: ")
            self.info_format.setFont(self.panel_font)
            self.info_format.setMinimumWidth(100)
            mipbump_layout.addWidget(self.info_format)

            self.show_mipmaps_btn = QPushButton("View")
            self.show_mipmaps_btn.setFont(self.button_font)
            self.show_mipmaps_btn.setIcon(self._create_view_icon())
            self.show_mipmaps_btn.setIconSize(QSize(20, 20))
            self.show_mipmaps_btn.setToolTip("View all mipmap levels")
            self.show_mipmaps_btn.clicked.connect(self._open_mipmap_manager)
            self.show_mipmaps_btn.setEnabled(False)
            mipbump_layout.addWidget(self.show_mipmaps_btn)

            self.create_mipmaps_btn = QPushButton("Create")
            self.create_mipmaps_btn.setFont(self.button_font)
            self.create_mipmaps_btn.setIcon(self._create_add_icon())
            self.create_mipmaps_btn.setIconSize(QSize(20, 20))
            self.create_mipmaps_btn.setToolTip("Generate mipmaps")
            self.create_mipmaps_btn.clicked.connect(self._create_mipmaps_dialog)
            self.create_mipmaps_btn.setEnabled(False)
            mipbump_layout.addWidget(self.create_mipmaps_btn)

            self.remove_mipmaps_btn = QPushButton("Remove")
            self.remove_mipmaps_btn.setFont(self.button_font)
            self.remove_mipmaps_btn.setIcon(self._create_delete_icon())
            self.remove_mipmaps_btn.setIconSize(QSize(20, 20))
            self.remove_mipmaps_btn.setToolTip("Remove all mipmaps")
            self.remove_mipmaps_btn.clicked.connect(self._remove_mipmaps)
            self.remove_mipmaps_btn.setEnabled(False)
            mipbump_layout.addWidget(self.remove_mipmaps_btn)

            mipbump_layout.addSpacing(30)

            # Bumpmap detection
            self.info_format_b = QLabel("Bumpmaps:")
            self.info_format_b.setFont(self.panel_font)
            self.info_format_b.setMinimumWidth(120)
            mipbump_layout.addWidget(self.info_format_b)


            # Check if this version supports bumpmaps
            if is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
                # Check for bumpmap format bits
                if 'raster_format_flags' in texture:
                    flags = texture.get('raster_format_flags', 0)
                    if flags & 0x10:  # Bit 4 indicates environment/bumpmap
                        has_bumpmap = True

                # Also check for explicit bumpmap data
                if 'bumpmap_data' in texture or texture.get('has_bumpmap', False):
                    has_bumpmap = True

        # Update bumpmap UI - show status with color
        if hasattr(self, 'info_format_b'):
            if has_bumpmap:
                self.info_format_b = QLabel("Bumpmaps: Present")
                self.info_format_b.setText("Bumpmaps: Present")
                self.info_format_b.setStyleSheet("color: #4CAF50;")  # Green
            else:
                self.info_format_b = QLabel("Bumpmaps: None")
                self.info_format_b.setText("Bumpmaps: None")
                self.info_format_b.setStyleSheet("color: #757575;")  # Gray

            view_layout = QHBoxLayout()
            view_layout.setSpacing(5)
            self.view_bumpmap_btn = QPushButton("Manage")
            self.view_bumpmap_btn.setFont(self.button_font)
            self.view_bumpmap_btn.setIcon(self._create_manage_icon())
            self.view_bumpmap_btn.setIconSize(QSize(20, 20))
            self.view_bumpmap_btn.setToolTip("View and Manage Bumpmaps")
            self.view_bumpmap_btn.clicked.connect(self._view_bumpmap)
            self.view_bumpmap_btn.setEnabled(False)
            mipbump_layout.addWidget(self.view_bumpmap_btn)

            self.export_bumpmap_btn = QPushButton("Export")
            self.export_bumpmap_btn.setFont(self.button_font)
            self.export_bumpmap_btn.setIcon(self._create_export_icon())
            self.export_bumpmap_btn.setIconSize(QSize(20, 20))
            self.export_bumpmap_btn.setToolTip("Export bumpmap as PNG")
            self.export_bumpmap_btn.clicked.connect(self._export_bumpmap)
            self.export_bumpmap_btn.setEnabled(False)
            mipbump_layout.addWidget(self.export_bumpmap_btn)

            self.import_bumpmap_btn = QPushButton("Import")
            self.import_bumpmap_btn.setFont(self.button_font)
            self.import_bumpmap_btn.setIcon(self._create_import_icon())
            self.import_bumpmap_btn.setIconSize(QSize(20, 20))
            self.import_bumpmap_btn.setToolTip("Import bumpmap from image")
            self.import_bumpmap_btn.clicked.connect(self._import_bumpmap)
            self.import_bumpmap_btn.setEnabled(False)
            mipbump_layout.addWidget(self.import_bumpmap_btn)

            self.bitdepth_btn = QPushButton("Bit Depth")
            self.bitdepth_btn.setFont(self.button_font)
            self.bitdepth_btn.setIcon(self._create_bitdepth_icon())
            self.bitdepth_btn.setIconSize(QSize(20, 20))
            self.bitdepth_btn.setToolTip("Change bit depth")
            self.bitdepth_btn.clicked.connect(self._change_bit_depth)
            self.bitdepth_btn.setEnabled(False)
            format_layout.addWidget(self.bitdepth_btn)

            self.upscale_btn = QPushButton("AI Upscale")
            self.upscale_btn.setFont(self.button_font)
            self.upscale_btn.setIcon(self._create_upscale_icon())
            self.upscale_btn.setIconSize(QSize(20, 20))
            self.upscale_btn.setToolTip("AI upscale texture")
            self.upscale_btn.clicked.connect(self._upscale_texture)
            self.upscale_btn.setEnabled(False)
            format_layout.addWidget(self.upscale_btn)

            self.compress_btn = QPushButton("Compress")
            self.compress_btn.setFont(self.button_font)
            self.compress_btn.setIcon(self._create_compress_icon())
            self.compress_btn.setIconSize(QSize(20, 20))
            self.compress_btn.setToolTip("Compress texture")
            self.compress_btn.clicked.connect(self._compress_texture)
            self.compress_btn.setEnabled(False)
            format_layout.addWidget(self.compress_btn)

            self.uncompress_btn = QPushButton("Uncompress")
            self.uncompress_btn.setFont(self.button_font)
            self.uncompress_btn.setIcon(self._create_uncompress_icon())
            self.uncompress_btn.setIconSize(QSize(20, 20))
            self.uncompress_btn.setToolTip("Uncompress texture")
            self.uncompress_btn.clicked.connect(self._uncompress_texture)
            self.uncompress_btn.setEnabled(False)
            format_layout.addWidget(self.uncompress_btn)

            info_layout.addLayout(format_layout)
            info_layout.addLayout(view_layout)
            info_layout.addLayout(mipbump_layout)

        main_layout.addWidget(info_group, stretch=0)
        return panel


    def _change_bit_depth(self): #vers 1
        """Change texture bit depth"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QInputDialog

        current_depth = self.selected_texture.get('depth', 32)

        bit_depths = ["32bit (RGBA)", "24bit (RGB)", "16bit (ARGB1555)", "16bit (ARGB4444)", "16bit (RGB565)", "8bit (Indexed)"]
        depth_values = [32, 24, 16, 16, 16, 8]

        # Find current selection
        try:
            current_index = depth_values.index(current_depth)
        except:
            current_index = 0

        choice, ok = QInputDialog.getItem(
            self,
            "Change Bit Depth",
            f"Current: {current_depth}bit\n\nSelect new bit depth:",
            bit_depths,
            current_index,
            False
        )

        if ok:
            new_depth = depth_values[bit_depths.index(choice)]

            if new_depth != current_depth:
                self._save_undo_state("Change bit depth")
                self.selected_texture['depth'] = new_depth

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Bit depth changed: {current_depth}bit → {new_depth}bit")


    def _generate_bumpmap_from_texture(self): #vers 2
        """Generate bumpmap from texture with type selection"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        rgba_data = self.selected_texture.get('rgba_data')
        width = self.selected_texture.get('width', 0)
        height = self.selected_texture.get('height', 0)

        if not rgba_data or width == 0:
            QMessageBox.warning(self, "No Data", "Texture has no image data")
            return

        try:
            # Create generation dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Generate Bumpmap")
            dialog.setMinimumWidth(450)

            layout = QVBoxLayout(dialog)

            # === BUMPMAP TYPE SELECTION ===
            type_group = QGroupBox("Bumpmap Type")
            type_layout = QVBoxLayout()

            type_combo = QComboBox()
            type_combo.addItems([
                "Grayscale Height Map (Traditional)",
                "RGB Normal Map (Colorful)",
                "Both (Height + Normal)"
            ])
            type_layout.addWidget(type_combo)

            type_info = QLabel()
            type_info.setStyleSheet("color: #888; font-size: 9pt; padding: 5px;")
            type_info.setWordWrap(True)

            def update_type_info(index):
                if index == 0:  # Grayscale
                    type_info.setText(
                        "Grayscale Height Map:\n"
                        "• White = raised areas, Black = recessed\n"
                        "• Used by game engine to calculate normals in real-time\n"
                        "• Smaller file size, standard for GTA"
                    )
                elif index == 1:  # RGB Normal
                    type_info.setText(
                        "RGB Normal Map:\n"
                        "• Pre-calculated surface normals (colorful)\n"
                        "• R=X, G=Y, B=Z normal directions\n"
                        "• Higher quality, larger file size"
                    )
                else:  # Both
                    type_info.setText(
                        "Both Types:\n"
                        "• Stores both height map and normal map\n"
                        "• Maximum compatibility\n"
                        "• Largest file size"
                    )

            type_combo.currentIndexChanged.connect(update_type_info)
            update_type_info(0)

            type_layout.addWidget(type_info)
            type_group.setLayout(type_layout)
            layout.addWidget(type_group)

            # === GENERATION METHOD ===
            method_group = QGroupBox("Generation Method")
            method_layout = QVBoxLayout()

            method_combo = QComboBox()
            method_combo.addItems([
                "Sobel Filter (Edge Detection)",
                "Height Map (Grayscale)",
                "Normal Map (RGB)",
                "Emboss Filter"
            ])
            method_layout.addWidget(method_combo)

            method_info = QLabel(
                "Sobel: Detects edges for bump effect\n"
                "Height: Uses brightness as height\n"
                "Normal: Creates RGB normal map\n"
                "Emboss: Creates raised/lowered effect"
            )
            method_info.setStyleSheet("color: #888; font-size: 9pt;")
            method_layout.addWidget(method_info)

            method_group.setLayout(method_layout)
            layout.addWidget(method_group)

            # === STRENGTH CONTROL ===
            strength_group = QGroupBox("Strength")
            strength_layout = QFormLayout()

            strength_slider = QSlider(Qt.Orientation.Horizontal)
            strength_slider.setRange(1, 100)
            strength_slider.setValue(50)
            strength_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            strength_slider.setTickInterval(10)

            strength_label = QLabel("50%")
            strength_slider.valueChanged.connect(
                lambda v: strength_label.setText(f"{v}%")
            )

            strength_layout.addRow("Intensity:", strength_slider)
            strength_layout.addRow("", strength_label)

            strength_group.setLayout(strength_layout)
            layout.addWidget(strength_group)

            # === SMOOTHING CONTROL ===
            smooth_group = QGroupBox("Smoothing")
            smooth_layout = QFormLayout()

            smooth_slider = QSlider(Qt.Orientation.Horizontal)
            smooth_slider.setRange(0, 10)
            smooth_slider.setValue(2)
            smooth_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            smooth_slider.setTickInterval(1)

            smooth_label = QLabel("2")
            smooth_slider.valueChanged.connect(
                lambda v: smooth_label.setText(str(v))
            )

            smooth_layout.addRow("Blur Radius:", smooth_slider)
            smooth_layout.addRow("", smooth_label)

            smooth_group.setLayout(smooth_layout)
            layout.addWidget(smooth_group)

            # === INVERT OPTION ===
            invert_check = QCheckBox("Invert bumpmap (swap raised/lowered)")
            layout.addWidget(invert_check)

            # === BUTTONS ===
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            preview_btn = QPushButton("Preview")
            preview_btn.clicked.connect(
                lambda: self._preview_bumpmap_generation(
                    rgba_data, width, height,
                    type_combo.currentIndex(),
                    method_combo.currentIndex(),
                    strength_slider.value(),
                    smooth_slider.value(),
                    invert_check.isChecked()
                )
            )
            button_layout.addWidget(preview_btn)

            generate_btn = QPushButton("Generate")
            generate_btn.setDefault(True)
            generate_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(generate_btn)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            # === EXECUTE DIALOG ===
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Generate bumpmap with selected settings
                bumpmap_type = type_combo.currentIndex()
                method = method_combo.currentIndex()
                strength = strength_slider.value() / 100.0
                smooth = smooth_slider.value()
                invert = invert_check.isChecked()

                bumpmap_data = self._create_bumpmap_data(
                    rgba_data, width, height, bumpmap_type, method, strength, smooth, invert
                )

                if bumpmap_data:
                    # Save undo state
                    self._save_undo_state("Generate bumpmap")

                    # Add bumpmap to texture
                    self.selected_texture['bumpmap_data'] = bumpmap_data
                    self.selected_texture['bumpmap_type'] = bumpmap_type  # Store type
                    self.selected_texture['has_bumpmap'] = True
                    self.selected_texture['raster_format_flags'] = \
                        self.selected_texture.get('raster_format_flags', 0) | 0x10

                    # Mark modified
                    self._mark_as_modified()

                    # Update UI
                    self._update_texture_info(self.selected_texture)

                    type_names = ["Grayscale Height Map", "RGB Normal Map", "Both (Height + Normal)"]
                    QMessageBox.information(self, "Success",
                        f"Bumpmap generated successfully!\nType: {type_names[bumpmap_type]}")

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(
                            f"✅ Generated {type_names[bumpmap_type]} for: {self.selected_texture.get('name', 'texture')}"
                        )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate bumpmap:\n{str(e)}")
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Bumpmap generation error: {str(e)}")


    def _create_bumpmap_data(self, rgba_data, width, height, bumpmap_type, method, strength, smooth, invert): #vers 2
        """Create bumpmap data with type selection"""
        import struct

        try:
            # Convert RGBA to grayscale first
            grayscale = bytearray(width * height)
            for i in range(0, len(rgba_data), 4):
                r, g, b = rgba_data[i:i+3]
                # Luminosity method
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                grayscale[i // 4] = gray

            # Apply smoothing if requested
            if smooth > 0:
                grayscale = self._apply_gaussian_blur(grayscale, width, height, smooth)

            # Generate based on type
            if bumpmap_type == 0:  # Grayscale Height Map
                # Generate height map
                if method == 0:  # Sobel Filter
                    bumpmap = self._sobel_filter(grayscale, width, height, strength)
                elif method == 1:  # Height Map
                    bumpmap = self._height_map(grayscale, width, height, strength)
                elif method == 2:  # Normal Map (but output as grayscale)
                    bumpmap = self._sobel_filter(grayscale, width, height, strength)
                elif method == 3:  # Emboss
                    bumpmap = self._emboss_filter(grayscale, width, height, strength)
                else:
                    bumpmap = grayscale

                # Invert if requested
                if invert:
                    bumpmap = bytearray(255 - b for b in bumpmap)

                return bytes(bumpmap)

            elif bumpmap_type == 1:  # RGB Normal Map
                # Generate RGB normal map
                normal_map = self._generate_rgb_normal_map(grayscale, width, height, strength)

                # Invert if requested (flip normals)
                if invert:
                    inverted = bytearray(len(normal_map))
                    for i in range(0, len(normal_map), 3):
                        inverted[i] = 255 - normal_map[i]      # Invert R
                        inverted[i+1] = 255 - normal_map[i+1]  # Invert G
                        inverted[i+2] = normal_map[i+2]        # Keep B (Z) the same
                    normal_map = inverted

                return bytes(normal_map)

            else:  # Both types
                # Generate both and combine with header
                height_map = self._sobel_filter(grayscale, width, height, strength)
                if invert:
                    height_map = bytearray(255 - b for b in height_map)

                normal_map = self._generate_rgb_normal_map(grayscale, width, height, strength)
                if invert:
                    inverted = bytearray(len(normal_map))
                    for i in range(0, len(normal_map), 3):
                        inverted[i] = 255 - normal_map[i]
                        inverted[i+1] = 255 - normal_map[i+1]
                        inverted[i+2] = normal_map[i+2]
                    normal_map = inverted

                # Combine: [type_byte][height_map][normal_map]
                combined = bytearray()
                combined.append(2)  # Type identifier: 2 = both
                combined.extend(height_map)
                combined.extend(normal_map)

                return bytes(combined)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Bumpmap creation error: {str(e)}")
            return None


    def _generate_rgb_normal_map(self, grayscale, width, height, strength): #vers 2
        """Generate proper RGB normal map from height data"""
        normal_map = bytearray(width * height * 3)

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Sample neighboring heights
                left = grayscale[y * width + (x - 1)]
                right = grayscale[y * width + (x + 1)]
                up = grayscale[(y - 1) * width + x]
                down = grayscale[(y + 1) * width + x]

                # Calculate normal vector using height differences
                dx = (left - right) * strength * 2.0  # Increased multiplier
                dy = (up - down) * strength * 2.0     # Increased multiplier
                dz = 128.0  # Base Z strength

                # Normalize vector
                length = (dx*dx + dy*dy + dz*dz) ** 0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    dz /= length

                # Map to RGB range [0-255]
                # Normal maps: flat surface = (128, 128, 255) in RGB = (0.5, 0.5, 1.0) in normalized
                r = int((dx * 0.5 + 0.5) * 255)
                g = int((dy * 0.5 + 0.5) * 255)
                b = int((dz * 0.5 + 0.5) * 255)

                idx = (y * width + x) * 3
                normal_map[idx] = max(0, min(255, r))
                normal_map[idx + 1] = max(0, min(255, g))
                normal_map[idx + 2] = max(0, min(255, b))

        # Fill edges with flat normal (128, 128, 255)
        for y in range(height):
            for x in range(width):
                if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                    idx = (y * width + x) * 3
                    normal_map[idx] = 128      # R = 0.5 (no X tilt)
                    normal_map[idx + 1] = 128  # G = 0.5 (no Y tilt)
                    normal_map[idx + 2] = 255  # B = 1.0 (pointing up)

        return normal_map


    def _normalize_vector(self, v): #vers 1
        """Normalize vector array"""
        norm = np.linalg.norm(v, axis=2, keepdims=True)
        norm[norm == 0] = 1.0
        return v / norm


    def _detect_y_flip(self, normal): #vers 1
        """Heuristic to detect if Y channel is flipped (DirectX vs OpenGL)"""
        pos_y_ratio = np.mean(normal[:, :, 1] > 0.5)
        return pos_y_ratio < 0.4


    def _normal_to_bump(self, normal_map): #vers 1
        """Convert normal map to bump map using Z channel"""
        n = normal_map.astype(np.float32) / 255.0
        n = n * 2.0 - 1.0
        bump = n[:, :, 2]
        bump = (bump - bump.min()) / (bump.max() - bump.min() + 1e-6)
        return (bump * 255).astype(np.uint8)


    def _normal_to_reflection(self, normal_map, view=(0, 0, 1), F0=0.04): #vers 1
        """
        Generate reflection vector map and Fresnel reflectivity from normal map
        """
        n = normal_map.astype(np.float32) / 255.0
        n = n * 2.0 - 1.0
        n = self._normalize_vector(n)

        V = np.array(view, dtype=np.float32)
        V = V / np.linalg.norm(V)

        # Calculate dot product V·N
        VdotN = np.sum(V * n, axis=2, keepdims=True)

        # Calculate reflection vector: R = V - 2(V·N)N
        R = V - 2.0 * VdotN * n
        R = self._normalize_vector(R)

        # Encode reflection vector to RGB (map from [-1,1] to [0,255])
        R_enc = ((R + 1.0) * 0.5 * 255.0).astype(np.uint8)

        # Calculate Fresnel reflectivity using Schlick's approximation
        VdotN_scalar = np.clip(VdotN.squeeze(), -1.0, 1.0)
        one_minus = 1.0 - np.clip(VdotN_scalar, 0.0, 1.0)
        F = F0 + (1.0 - F0) * (one_minus ** 5)
        F_img = (F * 255.0).astype(np.uint8)

        return R_enc, F_img


    def _sobel_filter(self, data, width, height, strength): #vers 2
        """Apply Sobel edge detection filter"""
        result = bytearray(width * height)

        # Sobel kernels
        gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                px = 0
                py = 0

                # Apply kernels
                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        pixel = data[(y + ky) * width + (x + kx)]
                        px += pixel * gx[ky + 1][kx + 1]
                        py += pixel * gy[ky + 1][kx + 1]

                # Calculate magnitude
                magnitude = int(((px * px + py * py) ** 0.5) * strength * 2)  # Added multiplier
                magnitude = max(0, min(255, magnitude))

                result[y * width + x] = magnitude

        return result


    def _height_map(self, data, width, height, strength): #vers 2
        """Convert grayscale to height map"""
        result = bytearray(width * height)

        for i in range(len(data)):
            # Apply strength - don't reduce brightness
            value = int(data[i] * (0.5 + strength * 0.5))  # Scale from 0.5-1.0x
            result[i] = max(0, min(255, value))

        return result


    def _normal_map(self, data, width, height, strength): #vers 1
        """Generate normal map from height data (returns RGB normal map)"""
        # Normal maps are 3-channel RGB, but we'll store as grayscale for now
        # Full RGB normal map support would require format changes
        return self._sobel_filter(data, width, height, strength)


    def _emboss_filter(self, data, width, height, strength): #vers 1
        """Apply emboss filter"""
        result = bytearray(width * height)

        # Emboss kernel
        kernel = [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                value = 0

                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        pixel = data[(y + ky) * width + (x + kx)]
                        value += pixel * kernel[ky + 1][kx + 1]

                value = int(128 + value * strength)
                value = max(0, min(255, value))

                result[y * width + x] = value

        return result


    def _apply_gaussian_blur(self, data, width, height, radius): #vers 1
        """Apply Gaussian blur for smoothing"""
        if radius == 0:
            return data

        result = bytearray(width * height)
        kernel_size = radius * 2 + 1
        sigma = radius / 3.0

        # Generate Gaussian kernel
        kernel = []
        kernel_sum = 0
        for y in range(-radius, radius + 1):
            row = []
            for x in range(-radius, radius + 1):
                value = (1.0 / (2.0 * 3.14159 * sigma * sigma)) * \
                        (2.71828 ** (-(x*x + y*y) / (2.0 * sigma * sigma)))
                row.append(value)
                kernel_sum += value
            kernel.append(row)

        # Normalize kernel
        kernel = [[v / kernel_sum for v in row] for row in kernel]

        # Apply kernel
        for y in range(height):
            for x in range(width):
                value = 0

                for ky in range(-radius, radius + 1):
                    for kx in range(-radius, radius + 1):
                        px = max(0, min(width - 1, x + kx))
                        py = max(0, min(height - 1, y + ky))
                        value += data[py * width + px] * kernel[ky + radius][kx + radius]

                result[y * width + x] = int(value)

        return result


    def _preview_bumpmap_generation(self, rgba_data, width, height, bumpmap_type, method, strength, smooth, invert): #vers 2
        """Preview bumpmap generation in separate window"""
        try:
            # Generate preview bumpmap
            strength_val = strength / 100.0
            bumpmap_data = self._create_bumpmap_data(
                rgba_data, width, height, bumpmap_type, method, strength_val, smooth, invert
            )

            if not bumpmap_data:
                return

            # Create preview window
            preview = QDialog(self)
            preview.setWindowTitle("Bumpmap Preview")
            preview.setMinimumSize(400, 400)

            layout = QVBoxLayout(preview)

            # Preview label
            preview_label = QLabel()
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setMinimumSize(350, 350)
            preview_label.setStyleSheet("border: 1px solid #3a3a3a; background: #2a2a2a;")

            # Decode and display based on type
            if bumpmap_type == 0:  # Grayscale Height Map
                # Convert grayscale to RGB for display
                rgb_data = bytearray(width * height * 3)
                for i in range(width * height):
                    if i < len(bumpmap_data):
                        value = bumpmap_data[i]
                        rgb_data[i*3] = value
                        rgb_data[i*3+1] = value
                        rgb_data[i*3+2] = value

                image = QImage(bytes(rgb_data), width, height, width * 3, QImage.Format.Format_RGB888)

            elif bumpmap_type == 1:  # RGB Normal Map
                # Direct RGB display
                image = QImage(bytes(bumpmap_data), width, height, width * 3, QImage.Format.Format_RGB888)

            else:  # Both types - show normal map
                expected_gray = width * height
                expected_rgb = width * height * 3
                offset = 1 + expected_gray
                normal_data = bumpmap_data[offset:offset + expected_rgb]
                image = QImage(bytes(normal_data), width, height, width * 3, QImage.Format.Format_RGB888)

            pixmap = QPixmap.fromImage(image)
            preview_label.setPixmap(
                pixmap.scaled(350, 350,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
            )

            layout.addWidget(preview_label)

            # Info label showing type
            type_names = ["Grayscale Height Map", "RGB Normal Map", "Both Types"]
            info_label = QLabel(f"Type: {type_names[bumpmap_type]}")
            info_label.setStyleSheet("color: #888; padding: 5px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(preview.accept)
            layout.addWidget(close_btn)

            preview.exec()

        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Failed to preview:\n{str(e)}")


    def _delete_bumpmap(self): #vers 1
        """Delete bumpmap from selected texture"""
        if not self.selected_texture:
            return

        if not self._has_bumpmap_data(self.selected_texture):
            QMessageBox.information(self, "No Bumpmap", "This texture has no bumpmap")
            return

        reply = QMessageBox.question(
            self, "Delete Bumpmap",
            "Remove bumpmap from this texture?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Save undo state
            self._save_undo_state("Delete bumpmap")

            # Remove bumpmap data
            if 'bumpmap_data' in self.selected_texture:
                del self.selected_texture['bumpmap_data']
            self.selected_texture['has_bumpmap'] = False

            # Clear bumpmap flag
            if 'raster_format_flags' in self.selected_texture:
                self.selected_texture['raster_format_flags'] &= ~0x10

            # Mark modified
            self._mark_as_modified()

            # Update UI
            self._update_texture_info(self.selected_texture)

            QMessageBox.information(self, "Success", "Bumpmap deleted")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Deleted bumpmap from: {self.selected_texture.get('name', 'texture')}"
                )


    def _has_bumpmap_data(self, texture): #vers 1
        """Check if texture has bumpmap data"""
        if not texture:
            return False

        # Check explicit bumpmap data
        if 'bumpmap_data' in texture or texture.get('has_bumpmap', False):
            return True

        # Check format flags
        if 'raster_format_flags' in texture:
            flags = texture.get('raster_format_flags', 0)
            if flags & 0x10:  # Bit 4 = bumpmap/environment
                return True

        return False


    def _mipmap_io_menu(self): #vers 1
        """Show export/import menu for mipmaps"""
        if not self.selected_texture:
            return

        menu = QMenu(self)
        export_action = menu.addAction("Export All Levels")
        export_action.triggered.connect(self._export_all_levels)

        import_action = menu.addAction("Import All Levels")
        import_action.triggered.connect(self._import_all_levels)

        menu.exec(self.mipmap_io_btn.mapToGlobal(self.mipmap_io_btn.rect().bottomLeft()))


    def _auto_generate_mipmaps_to_level(self, num_levels): #vers 1
        """Generate mipmaps down to specified level count"""
        if not self.selected_texture:
            return

        # Get main texture (level 0)
        main_rgba = self.selected_texture.get('rgba_data')
        if not main_rgba:
            QMessageBox.warning(self, "No Data", "Texture has no image data")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']

            # Convert to QImage
            source_image = QImage(main_rgba, width, height, width * 4, QImage.Format.Format_RGBA8888)

            if source_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to create source image")
                return

            # Clear existing mipmap levels except level 0
            if 'mipmap_levels' not in self.selected_texture:
                self.selected_texture['mipmap_levels'] = []

            # Keep level 0 if it exists
            level_0 = None
            for level in self.selected_texture['mipmap_levels']:
                if level['level'] == 0:
                    level_0 = level
                    break

            # Start fresh
            self.selected_texture['mipmap_levels'] = []

            # Add level 0
            if level_0:
                self.selected_texture['mipmap_levels'].append(level_0)
            else:
                self.selected_texture['mipmap_levels'].append({
                    'level': 0,
                    'width': width,
                    'height': height,
                    'rgba_data': main_rgba,
                    'compressed_data': None,
                    'compressed_size': len(main_rgba)
                })

            # Generate levels down to specified depth
            current_width = width // 2
            current_height = height // 2
            level_num = 1

            while level_num < num_levels and current_width >= 1 and current_height >= 1:
                # Scale down
                scaled_image = source_image.scaled(
                    current_width, current_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if scaled_image.isNull():
                    break

                # Convert to RGBA
                scaled_image = scaled_image.convertToFormat(QImage.Format.Format_RGBA8888)
                ptr = scaled_image.bits()
                ptr.setsize(scaled_image.sizeInBytes())
                rgba_data = bytes(ptr)

                # Add mipmap level
                mipmap_level = {
                    'level': level_num,
                    'width': current_width,
                    'height': current_height,
                    'rgba_data': rgba_data,
                    'compressed_data': None,
                    'compressed_size': len(rgba_data)
                }
                self.selected_texture['mipmap_levels'].append(mipmap_level)

                # Next level
                current_width = max(1, current_width // 2)
                current_height = max(1, current_height // 2)
                level_num += 1

            # Update mipmap count
            self.selected_texture['mipmaps'] = len(self.selected_texture['mipmap_levels'])

            # Update display
            self._update_texture_info(self.selected_texture)
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Generated {level_num} mipmap levels")

            actual_levels = len(self.selected_texture['mipmap_levels'])
            min_dim = min(current_width * 2, currentQFormLayout_height * 2)
            QMessageBox.information(self, "Success",
                f"Generated {actual_levels} mipmap levels\n"
                f"From {width}x{height} down to {min_dim}x{min_dim}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mipmaps: {str(e)}")

    def _manage_bumpmaps(self): #vers 1
        """Open bumpmap manager dialog"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture")
            return

        # Check if version supports bumpmaps
        if not is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            QMessageBox.warning(self, "Not Supported",
                f"Bumpmaps not supported for {self.txd_game}\n"
                f"Only San Andreas and State of Liberty support bumpmaps")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Bumpmap Manager")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Info section
        info_group = QGroupBox("Bumpmap Information")
        info_layout = QFormLayout()

        texture_name = self.selected_texture.get('name', 'Unknown')
        info_layout.addRow("Texture:", QLabel(texture_name))

        has_bumpmap = self._has_bumpmap_data(self.selected_texture)
        status = "Present" if has_bumpmap else "Not present"
        info_layout.addRow("Status:", QLabel(status))

        info_layout.addRow("Format:", QLabel("Environment map (Normal map)"))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        preview_label = QLabel("Bumpmap preview")
        preview_label.setMinimumHeight(200)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("border: 1px solid #3a3a3a; background: #2a2a2a;")

        if has_bumpmap:
            # TODO: Display actual bumpmap preview
            preview_label.setText("Bumpmap data present\n(Preview coming soon)")
        else:
            preview_label.setText("No bumpmap data")

        preview_layout.addWidget(preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Action buttons
        button_layout = QHBoxLayout()

        # View button
        view_btn = QPushButton("View")
        view_btn.setIcon(self._create_view_icon())
        view_btn.clicked.connect(lambda: self._view_bumpmap_in_manager(preview_label))
        view_btn.setEnabled(has_bumpmap)
        button_layout.addWidget(view_btn)

        # Generate button
        generate_btn = QPushButton("Generate")
        generate_btn.setIcon(self._create_add_icon())
        generate_btn.clicked.connect(lambda: self._generate_bumpmap_dialog(dialog))
        generate_btn.setToolTip("Generate bumpmap from texture")
        button_layout.addWidget(generate_btn)

        # Import buttonraster_format_flags
        import_btn = QPushButton("Import")
        import_btn.setIcon(self._create_import_icon())
        import_btn.clicked.connect(lambda: self._import_bumpmap_in_manager(dialog))
        button_layout.addWidget(import_btn)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.setIcon(self._create_export_icon())
        export_btn.clicked.connect(self._export_bumpmap)
        export_btn.setEnabled(has_bumpmap)
        button_layout.addWidget(export_btn)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setIcon(self._create_trash_icon())
        delete_btn.clicked.connect(lambda: self._delete_bumpmap_in_manager(dialog))
        delete_btn.setEnabled(has_bumpmap)
        delete_btn.setToolTip("Remove bumpmap from texture")
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

        dialog.exec()


    def _update_editing_controls(self): #vers 2
        """Update editing control states based on selection"""
        has_selection = self.selected_texture is not None

        # Basic controls
        if hasattr(self, 'resize_btn'):
            self.resize_btn.setEnabled(has_selection)
        if hasattr(self, 'upscale_btn'):
            self.upscale_btn.setEnabled(has_selection)
        if hasattr(self, 'format_combo'):
            self.format_combo.setEnabled(has_selection)

        if has_selection:
            # Compress button - always enabled (can compress or change DXT format)
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(True)

            # Uncompress button - only enabled if currently DXT format
            if hasattr(self, 'uncompress_btn'):
                current_format = self.selected_texture.get('format', 'Unknown')
                self.uncompress_btn.setEnabled('DXT' in current_format)
        else:
            # No selection - disable both
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(False)
            if hasattr(self, 'uncompress_btn'):
                self.uncompress_btn.setEnabled(False)


    def _batch_export_dialog(self): #vers 1
        """Show batch export options dialog"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures to export")
            return

        # Create custom dialog
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Batch Export Options")
        dialog.setText(f"Export {len(self.texture_list)} textures:")

        normal_btn = dialog.addButton("Normal Only", QMessageBox.ButtonRole.AcceptRole)
        alpha_btn = dialog.addButton("Alpha Only", QMessageBox.ButtonRole.AcceptRole)
        both_btn = dialog.addButton("Both Separate", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        dialog.exec()
        clicked = dialog.clickedButton()

        if clicked == cancel_btn:
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        try:
            exported = 0
            for texture in self.texture_list:
                name = texture.get('name', f'texture_{exported}')
                rgba_data = texture.get('rgba_data')
                width = texture.get('width', 0)
                height = texture.get('height', 0)

                if rgba_data and width > 0:
                    if clicked == normal_btn or clicked == both_btn:
                        file_path = os.path.join(output_dir, f"{name}.png")
                        self._save_texture_png(rgba_data, width, height, file_path)
                        exported += 1

                    if clicked == alpha_btn or clicked == both_btn:
                        alpha_data = self._extract_alpha_channel(rgba_data)
                        alpha_path = os.path.join(output_dir, f"{name}_alpha.png")
                        self._save_texture_png(alpha_data, width, height, alpha_path)
                        if clicked == alpha_btn:
                            exported += 1

            QMessageBox.information(self, "Success", f"Exported {exported} files successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Batch export failed: {str(e)}")


    def _show_detailed_info(self): #vers 1
        """Show detailed texture information"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        tex = self.selected_texture

        # Build detailed info
        info = f"=== Texture Details ===\n"
        info += f"Name: {tex.get('name', 'Unknown')}\n"
        info += f"Dimensions: {tex.get('width', 0)}x{tex.get('height', 0)}\n"
        info += f"Format: {tex.get('format', 'Unknown')}\n"
        info += f"Has Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}\n"

        if tex.get('alpha_name'):
            info += f"Alpha Name: {tex.get('alpha_name')}\n"

        if tex.get('rgba_data'):
            data_size = len(tex['rgba_data'])
            info += f"Raw Data Size: {data_size:,} bytes ({data_size/1024:.1f} KB)\n"

            # Calculate memory usage
            pixels = tex.get('width', 0) * tex.get('height', 0)
            if pixels > 0:
                info += f"Pixel Count: {pixels:,}\n"
                info += f"Bytes per Pixel: {data_size/pixels:.1f}\n"

        # Estimated compressed size
        est_dxt1 = (tex.get('width', 0) * tex.get('height', 0)) // 2
        est_dxt5 = tex.get('width', 0) * tex.get('height', 0)
        info += f"\n=== Estimated Compressed Sizes ===\n"
        info += f"DXT1: {est_dxt1:,} bytes\n"
        info += f"DXT5: {est_dxt5:,} bytes\n"

        QMessageBox.information(self, "Detailed Texture Information", info)


    def _update_status_indicators(self): #vers 1
        """Update status indicators"""
        if hasattr(self, 'status_textures'):
            self.status_textures.setText(f"Textures: {len(self.texture_list)}")

        if hasattr(self, 'status_selected'):
            if self.selected_texture:
                name = self.selected_texture.get('name', 'Unknown')
                self.status_selected.setText(f"Selected: {name}")
            else:
                self.status_selected.setText("Selected: None")

        if hasattr(self, 'status_size'):
            if self.current_txd_data:
                size_kb = len(self.current_txd_data) / 1024
                self.status_size.setText(f"TXD Size: {size_kb:.1f} KB")
            else:
                self.status_size.setText("TXD Size: Unknown")

        if hasattr(self, 'status_modified'):
            if self.windowTitle().endswith("*"):
                self.status_modified.setText("MODIFIED")
                self.status_modified.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_modified.setText("")
                self.status_modified.setStyleSheet("")


    def _import_normal_texture(self): #vers 1
        """Import normal texture (RGB/RGBA)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Normal Texture", "",
            "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
        )

        if not file_path:
            return

        try:
            from PyQt6.QtGui import QImage

            # Load image
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Error", "Failed to load image")
                return

            # Convert to RGBA8888
            img = img.convertToFormat(QImage.Format.Format_RGBA8888)

            # Get image data
            width = img.width()
            height = img.height()
            ptr = img.bits()
            ptr.setsize(img.sizeInBytes())
            rgba_data = bytes(ptr)

            # Check if image has alpha
            has_alpha = False
            for i in range(3, len(rgba_data), 4):
                if rgba_data[i] < 255:
                    has_alpha = True
                    break

            # Update texture
            self._save_undo_state("Import normal texture")
            self.selected_texture['width'] = width
            self.selected_texture['height'] = height
            self.selected_texture['rgba_data'] = rgba_data
            self.selected_texture['has_alpha'] = has_alpha

            # Update alpha name if texture now has alpha
            if has_alpha and 'alpha_name' not in self.selected_texture:
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                alpha_msg = "with alpha" if has_alpha else "no alpha"
                self.main_window.log_message(f"✅ Imported normal texture: {width}x{height} ({alpha_msg})")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")


    def _enable_name_edit(self, event, is_alpha): #vers 1
        """Enable name editing on click"""
        if is_alpha:
            self.info_alpha_name.setReadOnly(False)
            self.info_alpha_name.selectAll()
            self.info_alpha_name.setFocus()
        else:
            self.info_name.setReadOnly(False)
            self.info_name.selectAll()
            self.info_name.setFocus()


    def _save_texture_name(self): #vers 1
        """Save edited texture name"""
        if not self.selected_texture:
            return

        new_name = self.info_name.text().strip()
        if new_name and new_name != self.selected_texture.get('name', ''):
            old_name = self.selected_texture.get('name', '')
            self.selected_texture['name'] = new_name
            self._save_undo_state(f"Rename texture: {old_name} → {new_name}")
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✏️ Renamed: {old_name} → {new_name}")

        self.info_name.setReadOnly(True)


    def _save_alpha_name(self): #vers 1
        """Save edited alpha name"""
        if not self.selected_texture or not self.selected_texture.get('has_alpha'):
            return

        new_alpha_name = self.info_alpha_name.text().strip()
        if new_alpha_name and new_alpha_name != self.selected_texture.get('alpha_name', ''):
            old_name = self.selected_texture.get('alpha_name', '')
            self.selected_texture['alpha_name'] = new_alpha_name
            self._save_undo_state(f"Rename alpha: {old_name} → {new_alpha_name}")
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✏️ Alpha renamed: {old_name} → {new_alpha_name}")

        self.info_alpha_name.setReadOnly(True)


    def _import_alpha_texture(self): #vers 2
        """Import alpha channel - creates alpha if doesn't exist"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Alpha Channel", "",
            "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
        )

        if not file_path:
            return

        try:
            from PyQt6.QtGui import QImage

            # Load alpha image
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Error", "Failed to load image")
                return

            # Get current texture dimensions
            tex_width = self.selected_texture.get('width', 0)
            tex_height = self.selected_texture.get('height', 0)

            # If no texture data exists, create blank texture with alpha
            if not self.selected_texture.get('rgba_data') or tex_width == 0 or tex_height == 0:
                # Use alpha image dimensions
                tex_width = img.width()
                tex_height = img.height()

                # Create blank RGB texture (gray)
                blank_rgba = bytearray()
                for _ in range(tex_width * tex_height):
                    blank_rgba.extend([128, 128, 128, 255])  # Gray with full alpha

                self.selected_texture['width'] = tex_width
                self.selected_texture['height'] = tex_height
                self.selected_texture['rgba_data'] = bytes(blank_rgba)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Created blank texture {tex_width}x{tex_height} for alpha import")

            # Check dimensions match
            if img.width() != tex_width or img.height() != tex_height:
                reply = QMessageBox.question(
                    self, "Size Mismatch",
                    f"Alpha image is {img.width()}x{img.height()}, texture is {tex_width}x{tex_height}. Resize alpha?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    img = img.scaled(tex_width, tex_height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                else:
                    return

            # Convert to grayscale
            img = img.convertToFormat(QImage.Format.Format_Grayscale8)

            # Get alpha data
            ptr = img.bits()
            ptr.setsize(img.sizeInBytes())
            alpha_data = bytes(ptr)

            # Apply alpha to existing texture
            self._save_undo_state("Import alpha channel")

            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # If current texture has no alpha (all 255), we're adding it
            has_existing_alpha = any(rgba_data[i] < 255 for i in range(3, len(rgba_data), 4))

            for i, alpha_val in enumerate(alpha_data):
                if i * 4 + 3 < len(rgba_data):
                    rgba_data[i * 4 + 3] = alpha_val  # Set alpha channel

            self.selected_texture['rgba_data'] = bytes(rgba_data)
            self.selected_texture['has_alpha'] = True

            # Add alpha name if not present
            if 'alpha_name' not in self.selected_texture:
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            # Update format to support alpha if currently non-alpha format
            current_format = self.selected_texture.get('format', 'DXT1')
            if current_format in ['DXT1', 'RGB888', 'RGB565']:
                # Switch to alpha-capable format
                if 'DXT' in current_format:
                    self.selected_texture['format'] = 'DXT5'
                    format_msg = " (format changed to DXT5)"
                else:
                    self.selected_texture['format'] = 'ARGB8888'
                    format_msg = " (format changed to ARGB8888)"
            else:
                format_msg = ""

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                action = "Added" if not has_existing_alpha else "Replaced"
                self.main_window.log_message(f"✅ {action} alpha channel from: {os.path.basename(file_path)}{format_msg}")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import alpha: {str(e)}")


    def _create_preview_controls(self): #vers 2
        """Create preview control buttons - vertical layout on right"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)

        # Zoom In
        zoom_in_btn = QPushButton()
        zoom_in_btn.setIcon(self._create_zoom_in_icon())
        zoom_in_btn.setIconSize(QSize(20, 20))
        zoom_in_btn.setFixedSize(40, 40)
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self.preview_widget.zoom_in)
        controls_layout.addWidget(zoom_in_btn)

        # Zoom Out
        zoom_out_btn = QPushButton()
        zoom_out_btn.setIcon(self._create_zoom_out_icon())
        zoom_out_btn.setIconSize(QSize(20, 20))
        zoom_out_btn.setFixedSize(40, 40)
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self.preview_widget.zoom_out)
        controls_layout.addWidget(zoom_out_btn)

        # Reset
        reset_btn = QPushButton()
        reset_btn.setIcon(self._create_reset_icon())
        reset_btn.setIconSize(QSize(20, 20))
        reset_btn.setFixedSize(40, 40)
        reset_btn.setToolTip("Reset View")
        reset_btn.clicked.connect(self.preview_widget.reset_view)
        controls_layout.addWidget(reset_btn)

        # Fit
        fit_btn = QPushButton()
        fit_btn.setIcon(self._create_fit_icon())
        fit_btn.setIconSize(QSize(20, 20))
        fit_btn.setFixedSize(40, 40)
        fit_btn.setToolTip("Fit to Window")
        fit_btn.clicked.connect(self.preview_widget.fit_to_window)
        controls_layout.addWidget(fit_btn)

        controls_layout.addSpacing(10)

        # Pan Up
        pan_up_btn = QPushButton()
        pan_up_btn.setIcon(self._create_arrow_up_icon())
        pan_up_btn.setIconSize(QSize(20, 20))
        pan_up_btn.setFixedSize(40, 40)
        pan_up_btn.setToolTip("Pan Up")
        pan_up_btn.clicked.connect(lambda: self._pan_preview(0, -20))
        controls_layout.addWidget(pan_up_btn)

        # Pan Down
        pan_down_btn = QPushButton()
        pan_down_btn.setIcon(self._create_arrow_down_icon())
        pan_down_btn.setIconSize(QSize(20, 20))
        pan_down_btn.setFixedSize(40, 40)
        pan_down_btn.setToolTip("Pan Down")
        pan_down_btn.clicked.connect(lambda: self._pan_preview(0, 20))
        controls_layout.addWidget(pan_down_btn)

        # Pan Left
        pan_left_btn = QPushButton()
        pan_left_btn.setIcon(self._create_arrow_left_icon())
        pan_left_btn.setIconSize(QSize(20, 20))
        pan_left_btn.setFixedSize(40, 40)
        pan_left_btn.setToolTip("Pan Left")
        pan_left_btn.clicked.connect(lambda: self._pan_preview(-20, 0))
        controls_layout.addWidget(pan_left_btn)

        # Pan Right
        pan_right_btn = QPushButton()
        pan_right_btn.setIcon(self._create_arrow_right_icon())
        pan_right_btn.setIconSize(QSize(20, 20))
        pan_right_btn.setFixedSize(40, 40)
        pan_right_btn.setToolTip("Pan Right")
        pan_right_btn.clicked.connect(lambda: self._pan_preview(20, 0))
        controls_layout.addWidget(pan_right_btn)

        bg_custom_btn = QPushButton()
        bg_custom_btn.setIcon(self._create_color_picker_icon())
        bg_custom_btn.setIconSize(QSize(20, 20))
        bg_custom_btn.setFixedSize(40, 40)
        bg_custom_btn.setToolTip("Pick Color")
        bg_custom_btn.clicked.connect(self._pick_background_color)
        controls_layout.addWidget(bg_custom_btn)

        # Add resize button here
        self.resize_texture_btn = QPushButton()
        self.resize_texture_btn.setIcon(self._create_resize_icon())
        self.resize_texture_btn.setIconSize(QSize(20, 20))
        self.resize_texture_btn.setFixedSize(40, 40)
        self.resize_texture_btn.setToolTip("Resize Texture")
        self.resize_texture_btn.clicked.connect(self._resize_texture)
        #self.resize_texture_btn.setEnabled(False)
        controls_layout.addWidget(self.resize_texture_btn)

        # Checkerboard pattern button
        bg_checker_btn = QPushButton()
        bg_checker_btn.setIcon(self._create_checkerboard_icon())
        bg_checker_btn.setIconSize(QSize(20, 20))
        bg_checker_btn.setFixedSize(40, 40)
        bg_checker_btn.setToolTip("Checkerboard Pattern")
        bg_checker_btn.clicked.connect(lambda: self.preview_widget.set_checkerboard_background())
        controls_layout.addWidget(bg_checker_btn)

        controls_layout.addSpacing(10)

        # Background colors
        bg_black_btn = QPushButton()
        bg_black_btn.setFixedSize(40, 40)
        bg_black_btn.setStyleSheet("background-color: black; border: 1px solid #555;")
        bg_black_btn.setToolTip("Black Background")
        bg_black_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(0, 0, 0)))
        controls_layout.addWidget(bg_black_btn)

        bg_gray_btn = QPushButton()
        bg_gray_btn.setFixedSize(40, 40)
        bg_gray_btn.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        bg_gray_btn.setToolTip("Gray Background")
        bg_gray_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(42, 42, 42)))
        controls_layout.addWidget(bg_gray_btn)

        bg_white_btn = QPushButton()
        bg_white_btn.setFixedSize(40, 40)
        bg_white_btn.setStyleSheet("background-color: white; border: 1px solid #555;")
        bg_white_btn.setToolTip("White Background")
        bg_white_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(255, 255, 255)))
        controls_layout.addWidget(bg_white_btn)

        controls_layout.addStretch()

        return controls_frame


    def _pan_preview(self, dx, dy): #vers 2
        """Pan preview by delta"""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.pan_offset = QPoint(
                self.preview_widget.pan_offset.x() + dx,
                self.preview_widget.pan_offset.y() + dy
            )
            self.preview_widget.update_display()


    def _pick_background_color(self): #vers 1
        """Open color picker for background"""
        color = QColorDialog.getColor(self.preview_widget.bg_color, self, "Pick Background Color")
        if color.isValid():
            self.preview_widget.set_background_color(color)


    def _set_checkerboard_bg(self): #vers 1
        """Set checkerboard background"""
        # Create checkerboard pattern
        self.preview_widget.setStyleSheet("""
            border: 1px solid #3a3a3a;
            background-image:
                linear-gradient(45deg, #333 25%, transparent 25%),
                linear-gradient(-45deg, #333 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #333 75%),
                linear-gradient(-45deg, transparent 75%, #333 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        """)

    def _show_settings_dialog(self): #vers 2
        """Show settings dialog for UI customization"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                    QGroupBox, QFormLayout, QSpinBox, QFontComboBox, QPushButton, QLabel)

        dialog = QDialog(self)
        dialog.setWindowTitle("TXD Workshop Settings")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Save Location Settings
        save_group = QGroupBox("Save Location")
        save_layout = QVBoxLayout()

        source_check = QCheckBox("Always save in same location as loaded file")
        source_check.setChecked(self.save_to_source_location)
        source_check.setToolTip(
            "When enabled, Save As will default to the directory where\n"
            "the TXD was originally loaded from (IMG or standalone)"
        )
        save_layout.addWidget(source_check)

        info_label = QLabel(
            "When disabled, Save As will remember the last directory\n"
            "you saved to and use that as the default."
        )
        info_label.setStyleSheet("color: #888; font-size: 9pt;")
        save_layout.addWidget(info_label)

        save_group.setLayout(save_layout)
        layout.addWidget(save_group)

        # Tab widget for different setting categories
        tabs = QTabWidget()

        # === APPEARANCE TAB ===
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)


        # Font settings group
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout()

        # Title bar font
        self.title_font_combo = QFontComboBox()
        self.title_font_combo.setCurrentFont(self.font())
        font_layout.addRow("Title Bar Font:", self.title_font_combo)

        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(8, 24)
        self.title_font_size.setValue(14)
        font_layout.addRow("Title Size:", self.title_font_size)

        # Panel labels font
        self.panel_font_combo = QFontComboBox()
        self.panel_font_combo.setCurrentFont(self.font())
        font_layout.addRow("Panel Font:", self.panel_font_combo)

        self.panel_font_size = QSpinBox()
        self.panel_font_size.setRange(8, 24)
        self.panel_font_size.setValue(10)
        font_layout.addRow("Panel Size:", self.panel_font_size)

        # Button font
        self.button_font_combo = QFontComboBox()
        self.button_font_combo.setCurrentFont(self.font())
        font_layout.addRow("Button Font:", self.button_font_combo)

        self.button_font_size = QSpinBox()
        self.button_font_size.setRange(8, 24)
        self.button_font_size.setValue(10)
        font_layout.addRow("Button Size:", self.button_font_size)

        # Info bar font (fixed-width)
        self.infobar_font_combo = QFontComboBox()
        self.infobar_font_combo.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
        self.infobar_font_combo.setCurrentFont(QFont("Courier New"))
        font_layout.addRow("Info Bar Font:", self.infobar_font_combo)

        self.infobar_font_size = QSpinBox()
        self.infobar_font_size.setRange(8, 16)
        self.infobar_font_size.setValue(9)
        font_layout.addRow("Info Bar Size:", self.infobar_font_size)

        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)

        # Button display mode
        display_group = QGroupBox("Button Display")
        display_layout = QFormLayout()

        self.settings_display_combo = QComboBox()
        self.settings_display_combo.addItems(["Icons Only", "Text Only", "Both"])
        current_mode = {"icons": 0, "text": 1, "both": 2}.get(self.button_display_mode, 2)
        self.settings_display_combo.setCurrentIndex(current_mode)
        display_layout.addRow("Button Mode:", self.settings_display_combo)

        display_group.setLayout(display_layout)
        appearance_layout.addWidget(display_group)

        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")

        # === LOCALIZATION TAB ===
        locale_tab = QWidget()
        locale_layout = QVBoxLayout(locale_tab)

        locale_group = QGroupBox("Language Settings")
        locale_form = QFormLayout()

        self.settings_locale_combo = QComboBox()
        self.settings_locale_combo.addItems([
            "English",
            "Spanish (Español)",
            "French (Français)",
            "German (Deutsch)",
            "Italian (Italiano)",
            "Portuguese (Português)",
            "Russian (Русский)",
            "Japanese (日本語)",
            "Chinese Simplified (简体中文)",
            "Chinese Traditional (繁體中文)"
        ])
        locale_form.addRow("Language:", self.settings_locale_combo)

        locale_note = QLabel("Note: Language changes require restart")
        locale_note.setStyleSheet("color: #888; font-style: italic;")
        locale_form.addRow("", locale_note)

        locale_group.setLayout(locale_form)
        locale_layout.addWidget(locale_group)

        locale_layout.addStretch()
        tabs.addTab(locale_tab, "Localization")

        # === ADVANCED TAB ===
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Docking options (if available)
        if self.main_window:
            dock_group = QGroupBox("Docking")
            dock_layout = QVBoxLayout()

            dock_label = QLabel(f"Current State: {'Docked' if self.is_docked else 'Standalone'}")
            dock_layout.addWidget(dock_label)

            dock_btn = QPushButton("Toggle Dock Mode (D)")
            dock_btn.clicked.connect(lambda: (self.toggle_dock_mode(), dialog.close()))
            dock_layout.addWidget(dock_btn)

            dock_group.setLayout(dock_layout)
            advanced_layout.addWidget(dock_group)

        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self._apply_settings(dialog))
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(lambda: (self._apply_settings(dialog), dialog.accept()))
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def _apply_theme(self): #vers 1
        """Apply theme from main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'app_settings'):
                from depends.txd_workshop_theme import apply_theme_to_workshop, connect_workshop_to_theme_system
                apply_theme_to_workshop(self, self.main_window)
                connect_workshop_to_theme_system(self, self.main_window)
        except:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #e0e0e0; }
                QListWidget { background-color: #1e1e1e; border: 1px solid #3a3a3a; }
                QListWidget::item:selected { background-color: #0d47a1; }
                QPushButton { background-color: #3a3a3a; border: 1px solid #4a4a4a; padding: 5px 14px; border-radius: 3px; }
                QPushButton:hover { background-color: #4a4a4a; }
            """)

    def _apply_settings(self, dialog): #vers 5
        """Apply settings from dialog"""
        from PyQt6.QtGui import QFont

        # Store font settings
        self.title_font = QFont(self.title_font_combo.currentFont().family(), self.title_font_size.value())
        self.panel_font = QFont(self.panel_font_combo.currentFont().family(), self.panel_font_size.value())
        self.button_font = QFont(self.button_font_combo.currentFont().family(), self.button_font_size.value())
        self.infobar_font = QFont(self.infobar_font_combo.currentFont().family(), self.infobar_font_size.value())

        # Apply fonts to specific elements
        self._apply_title_font()
        self._apply_panel_font()
        self._apply_button_font()
        self._apply_infobar_font()

        # Apply button display mode
        mode_map = ["icons", "text", "both"]
        new_mode = mode_map[self.settings_display_combo.currentIndex()]
        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

        # Locale setting (would need implementation)
        locale_text = self.settings_locale_combo.currentText()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Settings applied: Font={font_family} {font_size}pt, Mode={new_mode}")

        # Apply export game target
        game_map = {
            0: "auto",
            1: "gta3",
            2: "vc",
            3: "sa",
            4: "manhunt"
        }
        self.export_target_game = game_map.get(self.export_game_combo.currentIndex(), "auto")

        # Apply export platform target
        platform_map = {
            0: "pc",
            1: "xbox",
            2: "ps2",
            3: "android",
            4: "multi"
        }
        self.export_target_platform = platform_map.get(self.export_platform_combo.currentIndex(), "pc")

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(
                f"Export targets: Game={self.export_target_game}, Platform={self.export_target_platform}"
            )

    def _create_left_panel(self): #vers 5
        """Create left panel - TXD file list (only in IMG Factory mode)"""
        # In standalone mode, don't create this panel
        if self.standalone_mode:
            self.txd_list_widget = None  # Explicitly set to None
            return None

        # Only create panel in IMG Factory mode
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("TXD Files")
        lheader.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.txd_list_widget = QListWidget()
        self.txd_list_widget.setAlternatingRowColors(True)
        self.txd_list_widget.itemClicked.connect(self._on_txd_selected)
        layout.addWidget(self.txd_list_widget)

        return panel


    def _apply_title_font(self): #vers 1
        """Apply title font to title bar labels"""
        if hasattr(self, 'title_font'):
            # Find all title labels
            for label in self.findChildren(QLabel):
                if label.objectName() == "title_label" or "🗺️" in label.text():
                    label.setFont(self.title_font)


    def _apply_panel_font(self): #vers 1
        """Apply panel font to info panels and labels"""
        if hasattr(self, 'panel_font'):
            # Apply to info labels (Mipmaps, Bumpmaps, status labels)
            for label in self.findChildren(QLabel):
                if any(x in label.text() for x in ["Mipmaps:", "Bumpmaps:", "Status:", "Type:", "Format:"]):
                    label.setFont(self.panel_font)


    def _apply_button_font(self): #vers 1
        """Apply button font to all buttons"""
        if hasattr(self, 'button_font'):
            for button in self.findChildren(QPushButton):
                button.setFont(self.button_font)


    def _apply_infobar_font(self): #vers 1
        """Apply fixed-width font to info bar at bottom"""
        if hasattr(self, 'infobar_font'):
            if hasattr(self, 'info_bar'):
                self.info_bar.setFont(self.infobar_font)

    def _load_img_txd_list(self): #vers 2
        """Load TXD files from IMG archive"""
        try:
            # Safety check for standalone mode
            if self.standalone_mode or not hasattr(self, 'txd_list_widget') or self.txd_list_widget is None:
                return

            self.txd_list_widget.clear()
            self.txd_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    self.txd_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.txd_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} TXD files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading TXD list: {str(e)}")


    def _create_middle_panel(self): #vers 3
        """Create middle panel - Texture list with context menu"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("Textures")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.texture_table = QTableWidget()
        self.texture_table.setColumnCount(2)
        self.texture_table.setHorizontalHeaderLabels(["Preview", "Details"])
        self.texture_table.horizontalHeader().setStretchLastSection(True)
        self.texture_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.texture_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.texture_table.setAlternatingRowColors(True)
        self.texture_table.itemSelectionChanged.connect(self._on_texture_selected)
        self.texture_table.setIconSize(QSize(64, 64))
        self.texture_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.texture_table.customContextMenuRequested.connect(self._show_texture_context_menu)
        layout.addWidget(self.texture_table)

        return panel


    def _create_blank_texture(self, width, height, with_alpha=False): #vers 2
        """Create blank RGBA texture data with optional alpha"""
        if with_alpha:
            # Gray with transparent alpha (128)
            return bytes([128, 128, 128, 128] * (width * height))
        else:
            # Gray with full opaque alpha (255)
            return bytes([128, 128, 128, 255] * (width * height))
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

    def _create_empty_txd_data(self): #vers 1
        """Create minimal empty TXD structure"""
        import struct
        # RenderWare TXD header (simplified)
        header = struct.pack('<III', 0x16, 0, 0x1803FFFF)  # Type, Size, Version
        return header


    def _create_new_texture_entry(self): #vers 2
        """Create new blank texture with size dialog"""
        if not self.current_img and not self.current_txd_data:
            QMessageBox.warning(self, "No TXD", "Please open or create a TXD file first")
            return

        # Ask for texture size
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Texture")
        dialog.setMinimumWidth(350)

        layout = QVBoxLayout(dialog)

        # Name input
        name_group = QGroupBox("Texture Name")
        name_layout = QVBoxLayout()

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter texture name")
        name_input.setText(f"texture_{len(self.texture_list) + 1}")
        name_layout.addWidget(name_input)

        name_group.setLayout(name_layout)
        layout.addWidget(name_group)

        # Size selection
        size_group = QGroupBox("Texture Size")
        size_layout = QVBoxLayout()

        # Common size presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))

        preset_combo = QComboBox()
        preset_combo.addItems([
            "Custom",
            "64 × 64",
            "128 × 128",
            "256 × 256",
            "512 × 512",
            "1024 × 1024",
            "2048 × 2048",
            "512 × 256",
            "1024 × 512",
            "256 × 128"
        ])
        preset_combo.setCurrentIndex(3)  # Default 256x256
        preset_layout.addWidget(preset_combo)
        size_layout.addLayout(preset_layout)

        # Custom size inputs
        custom_layout = QFormLayout()

        width_spin = QSpinBox()
        width_spin.setRange(1, 4096)
        width_spin.setValue(256)
        width_spin.setSingleStep(64)
        custom_layout.addRow("Width:", width_spin)

        height_spin = QSpinBox()
        height_spin.setRange(1, 4096)
        height_spin.setValue(256)
        height_spin.setSingleStep(64)
        custom_layout.addRow("Height:", height_spin)

        size_layout.addLayout(custom_layout)

        # Update spinboxes when preset changes
        def update_from_preset(index):
            if index == 0:  # Custom
                width_spin.setEnabled(True)
                height_spin.setEnabled(True)
            else:
                width_spin.setEnabled(False)
                height_spin.setEnabled(False)

                preset_sizes = {
                    1: (64, 64),
                    2: (128, 128),
                    3: (256, 256),
                    4: (512, 512),
                    5: (1024, 1024),
                    6: (2048, 2048),
                    7: (512, 256),
                    8: (1024, 512),
                    9: (256, 128)
                }

                if index in preset_sizes:
                    w, h = preset_sizes[index]
                    width_spin.setValue(w)
                    height_spin.setValue(h)

        preset_combo.currentIndexChanged.connect(update_from_preset)
        update_from_preset(3)  # Set initial state

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Color selection
        color_group = QGroupBox("Initial Color")
        color_layout = QHBoxLayout()

        color_btn = QPushButton("Choose Color")
        selected_color = QColor(128, 128, 128)  # Default gray

        def choose_color():
            nonlocal selected_color
            color = QColorDialog.getColor(selected_color, dialog, "Choose Texture Color")
            if color.isValid():
                selected_color = color
                color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
                color_btn.setText(color.name().upper())

        color_btn.clicked.connect(choose_color)
        color_btn.setStyleSheet(f"background-color: {selected_color.name()}; color: white;")
        color_btn.setText(selected_color.name().upper())
        color_layout.addWidget(color_btn)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        create_btn = QPushButton("Create")
        create_btn.setDefault(True)
        create_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            texture_name = name_input.text().strip()
            if not texture_name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a texture name")
                return

            width = width_spin.value()
            height = height_spin.value()

            # Create blank RGBA data with selected color
            rgba_data = bytearray(width * height * 4)
            r, g, b = selected_color.red(), selected_color.green(), selected_color.blue()

            for i in range(0, len(rgba_data), 4):
                rgba_data[i] = r
                rgba_data[i+1] = g
                rgba_data[i+2] = b
                rgba_data[i+3] = 255  # Full alpha

            # Create new texture entry
            new_texture = {
                'name': texture_name,
                'alpha_name': texture_name + 'a',
                'width': width,
                'height': height,
                'format': 'ARGB8888',
                'depth': 32,
                'has_alpha': True,
                'mipmaps': 1,
                'rgba_data': bytes(rgba_data),
                'mipmap_levels': [{
                    'level': 0,
                    'width': width,
                    'height': height,
                    'rgba_data': bytes(rgba_data),
                    'compressed_data': None,
                    'compressed_size': len(rgba_data)
                }]
            }

            # Add to texture list
            self.texture_list.append(new_texture)
            self._add_texture_to_table(new_texture)

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"✅ Created new texture: {texture_name} ({width}×{height})"
                )

            QMessageBox.information(self, "Success",
                f"Created new texture:\n{texture_name}\nSize: {width}×{height}")


    def _create_new_txd(self): #vers 1
        """Create a new empty TXD file"""
        name, ok = QInputDialog.getText(self, "New TXD", "Enter TXD filename (without .txd):")
        if ok and name:
            if not name.lower().endswith('.txd'):
                name += '.txd'

            # Create minimal TXD structure
            self.current_txd_name = name
            self.current_txd_data = self._create_empty_txd_data()
            self.texture_list = []
            self.texture_table.setRowCount(0)

            self.setWindowTitle(f"TXD Workshop: {name}")
            self.save_txd_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Created new TXD: {name}")


    def _delete_texture(self): #vers 2
        """Delete selected texture from TXD"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to delete")
            return

        # Confirm deletion
        texture_name = self.selected_texture.get('name', 'Unknown')
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete texture '{texture_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Find and remove from list
            if self.selected_texture in self.texture_list:
                self.texture_list.remove(self.selected_texture)

            # Clear selection
            self.selected_texture = None

            # Reload table
            self._reload_texture_table()

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Deleted: {texture_name}")

        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Failed to delete texture: {str(e)}")


    def _mark_as_modified(self): #vers 1
        """Mark the TXD as modified and enable save button"""
        self.save_txd_btn.setEnabled(True)
        self.save_txd_btn.setStyleSheet("background-color: #ff6b35; font-weight: bold;")
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")


    def _open_mipmap_manager(self): #vers 1
        """Open Mipmap Manager window for selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        mipmap_levels = self.selected_texture.get('mipmap_levels', [])
        if not mipmap_levels:
            QMessageBox.information(self, "No Mipmaps", "This texture has no mipmap levels")
            return

        # Create and show Mipmap Manager window
        manager = MipmapManagerWindow(self, self.selected_texture, self.main_window)
        manager.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"🔍 Opened Mipmap Manager for: {self.selected_texture['name']}")


    def _connect_texture_table_signals(self): #vers 1
        """Connect texture table signals for mipmap manager"""
        # Double-click to open mipmap manager
        self.texture_table.itemDoubleClicked.connect(self._on_texture_table_double_click)


    def _on_texture_selected(self): #vers 6
        """Handle texture selection - UNIFIED VERSION"""
        try:
            row = self.texture_table.currentRow()

            # Invalid selection - disable everything
            if row < 0 or row >= len(self.texture_list):
                self.selected_texture = None
                self.export_btn.setEnabled(False)

                # Disable all optional buttons
                if hasattr(self, 'flip_btn'):
                    self.flip_btn.setEnabled(False)
                if hasattr(self, 'props_btn'):
                    self.props_btn.setEnabled(False)
                if hasattr(self, 'duplicate_btn'):
                    self.duplicate_btn.setEnabled(False)
                if hasattr(self, 'remove_btn'):
                    self.remove_btn.setEnabled(False)
                if hasattr(self, 'resize_btn'):
                    self.resize_btn.setEnabled(False)
                if hasattr(self, 'upscale_btn'):
                    self.upscale_btn.setEnabled(False)
                if hasattr(self, 'format_combo'):
                    self.format_combo.setEnabled(False)
                if hasattr(self, 'compress_btn'):
                    self.compress_btn.setEnabled(False)
                if hasattr(self, 'uncompress_btn'):
                    self.uncompress_btn.setEnabled(False)
                if hasattr(self, 'bitdepth_btn'):
                    self.bitdepth_btn.setEnabled(False)

                # Disable mipmap buttons
                if hasattr(self, 'create_mipmaps_btn'):
                    self.create_mipmaps_btn.setEnabled(False)
                if hasattr(self, 'remove_mipmaps_btn'):
                    self.remove_mipmaps_btn.setEnabled(False)
                if hasattr(self, 'show_mipmaps_btn'):
                    self.show_mipmaps_btn.setEnabled(False)

                # Disable bumpmap buttons
                if hasattr(self, 'view_bumpmap_btn'):
                    self.view_bumpmap_btn.setEnabled(False)
                if hasattr(self, 'export_bumpmap_btn'):
                    self.export_bumpmap_btn.setEnabled(False)
                if hasattr(self, 'import_bumpmap_btn'):
                    self.import_bumpmap_btn.setEnabled(False)

                # Disable transform buttons
                if hasattr(self, 'flip_vert_btn'):
                    self.flip_vert_btn.setEnabled(False)
                if hasattr(self, 'flip_horz_btn'):
                    self.flip_horz_btn.setEnabled(False)
                if hasattr(self, 'rotate_cw_btn'):
                    self.rotate_cw_btn.setEnabled(False)
                if hasattr(self, 'rotate_ccw_btn'):
                    self.rotate_ccw_btn.setEnabled(False)

                return

            # Valid selection - get texture data
            self.selected_texture = self.texture_list[row]

            # Check mipmap state
            mipmap_levels = self.selected_texture.get('mipmap_levels', [])
            num_levels = len(mipmap_levels)
            has_mipmaps = num_levels > 1

            # Check bumpmap state
            has_bumpmap = self._has_bumpmap_data(self.selected_texture) if hasattr(self, '_has_bumpmap_data') else False
            can_support_bumpmap = is_bumpmap_supported(self.txd_version_id, self.txd_device_id) if self.txd_version_id else False

            # Update display FIRST (this should show the texture preview)
            self._update_texture_info(self.selected_texture)

            # Debug log
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Selected: {self.selected_texture.get('name')} | "
                    f"Levels: {num_levels} | Mipmaps: {has_mipmaps} | Bumpmap: {has_bumpmap}"
                )

            # Enable basic buttons
            self.export_btn.setEnabled(True)

            if hasattr(self, 'props_btn'):
                self.props_btn.setEnabled(True)
            if hasattr(self, 'duplicate_btn'):
                self.duplicate_btn.setEnabled(True)
            if hasattr(self, 'remove_btn'):
                self.remove_btn.setEnabled(True)
            if hasattr(self, 'resize_btn'):
                self.resize_btn.setEnabled(True)
            if hasattr(self, 'upscale_btn'):
                self.upscale_btn.setEnabled(True)
            if hasattr(self, 'format_combo'):
                self.format_combo.setEnabled(True)
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(True)
            if hasattr(self, 'uncompress_btn'):
                self.uncompress_btn.setEnabled(True)
            if hasattr(self, 'bitdepth_btn'):
                self.bitdepth_btn.setEnabled(True)

            # Flip button - enable only if has alpha
            if hasattr(self, 'flip_btn'):
                has_alpha = self.selected_texture.get('has_alpha', False)
                self.flip_btn.setEnabled(has_alpha)

            # Mipmap buttons
            if hasattr(self, 'create_mipmaps_btn'):
                self.create_mipmaps_btn.setEnabled(not has_mipmaps)
            if hasattr(self, 'remove_mipmaps_btn'):
                self.remove_mipmaps_btn.setEnabled(has_mipmaps)
            if hasattr(self, 'show_mipmaps_btn'):
                self.show_mipmaps_btn.setEnabled(has_mipmaps)

            # Bumpmap buttons
            if hasattr(self, 'view_bumpmap_btn'):
                # ALWAYS enable Manage button so user can generate/import bumpmaps
                self.view_bumpmap_btn.setEnabled(can_support_bumpmap)
            if hasattr(self, 'export_bumpmap_btn'):
                # Only enable export if bumpmap exists
                self.export_bumpmap_btn.setEnabled(has_bumpmap)
            if hasattr(self, 'import_bumpmap_btn'):
                # Only enable import if version supports bumpmaps
                self.import_bumpmap_btn.setEnabled(can_support_bumpmap)

            # Transform buttons
            if hasattr(self, 'flip_vert_btn'):
                self.flip_vert_btn.setEnabled(True)
            if hasattr(self, 'flip_horz_btn'):
                self.flip_horz_btn.setEnabled(True)
            if hasattr(self, 'rotate_cw_btn'):
                self.rotate_cw_btn.setEnabled(True)
            if hasattr(self, 'rotate_ccw_btn'):
                self.rotate_ccw_btn.setEnabled(True)

            # Additional buttons
            if hasattr(self, 'copy_btn'):
                self.copy_btn.setEnabled(True)
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setEnabled(True)
            if hasattr(self, 'edit_btn'):
                self.edit_btn.setEnabled(True)
            if hasattr(self, 'convert_btn'):
                self.convert_btn.setEnabled(True)
            if hasattr(self, 'paint_btn'):
                self.paint_btn.setEnabled(True)
            if hasattr(self, 'filters_btn'):
                self.filters_btn.setEnabled(True)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")
                import traceback
                self.main_window.log_message(traceback.format_exc())


    def _reload_texture_table(self): #vers 2
        """Reload texture table display with mipmap info"""
        self.texture_table.setRowCount(0)

        for tex in self.texture_list:
            row = self.texture_table.rowCount()
            self.texture_table.insertRow(row)

            thumb_item = QTableWidgetItem()
            if tex.get('rgba_data') and tex['width'] > 0:
                pixmap = self._create_thumbnail(tex['rgba_data'], tex['width'], tex['height'])
                if pixmap:
                    thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                else:
                    thumb_item.setText("🖼️")
            else:
                thumb_item.setText("🖼️")

            # Build details with mipmap info
            depth = tex.get('depth', 32)
            details = f"Name: {tex['name']} - {depth}bit\n"

            if tex.get('has_alpha', False):
                alpha_name = tex.get('alpha_name', tex['name'] + 'a')
                details += f"Alpha: {alpha_name}\n"
            else:
                details += "\n"

            if tex['width'] > 0:
                details += f"Size: {tex['width']}x{tex['height']} | Format: {tex['format']}\n"
            else:
                details += f"Format: {tex['format']}\n"

            # Mipmap info
            mipmap_levels = tex.get('mipmap_levels', [])
            num_mipmaps = len(mipmap_levels)

            if num_mipmaps > 0:
                is_compressed = 'DXT' in tex['format']
                compress_status = "compressed" if is_compressed else "uncompressed"
                details += f"📊 {num_mipmaps} mipmap levels ({compress_status}) - Click to view"
            else:
                details += "📊 No mipmaps"

            thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            details_item = QTableWidgetItem(details)
            details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.texture_table.setItem(row, 0, thumb_item)
            self.texture_table.setItem(row, 1, details_item)

        for row in range(self.texture_table.rowCount()):
            self.texture_table.setRowHeight(row, 100)
        self.texture_table.setColumnWidth(0, 80)


    def _save_undo_state(self, action_name): #vers 1
        """Save current state to undo stack"""
        import copy
        state = {
            'action': action_name,
            'texture_list': copy.deepcopy(self.texture_list)
        }
        self.undo_stack.append(state)

        # Limit undo stack to 10 items
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)


    def _undo_last_action(self): #vers 2
        """Undo the last action from undo stack"""
        if not self.undo_stack:
            return

        try:
            # Pop last action
            last_state = self.undo_stack.pop()

            # Restore texture list state
            self.texture_list = last_state.get('texture_list', [])

            # Reload table
            self._reload_texture_table()

            # Update undo button state
            self.undo_btn.setEnabled(len(self.undo_stack) > 0)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Undo applied")

        except Exception as e:
            QMessageBox.critical(self, "Undo Error", f"Failed to undo: {str(e)}")


    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels from main texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get main texture (level 0)
        main_rgba = self.selected_texture.get('rgba_data')
        if not main_rgba:
            QMessageBox.warning(self, "No Data", "Texture has no image data")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']

            # Convert to QImage
            source_image = QImage(main_rgba, width, height, width * 4, QImage.Format.Format_RGBA8888)

            if source_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to create source image")
                return

            # Clear existing mipmap levels except level 0
            if 'mipmap_levels' not in self.selected_texture:
                self.selected_texture['mipmap_levels'] = []

            # Keep level 0 if it exists
            level_0 = None
            for level in self.selected_texture['mipmap_levels']:
                if level['level'] == 0:
                    level_0 = level
                    break

            # Start fresh
            self.selected_texture['mipmap_levels'] = []

            # Add level 0
            if level_0:
                self.selected_texture['mipmap_levels'].append(level_0)
            else:
                self.selected_texture['mipmap_levels'].append({
                    'level': 0,
                    'width': width,
                    'height': height,
                    'rgba_data': main_rgba,
                    'compressed_data': None,
                    'compressed_size': len(main_rgba)
                })

            # Generate remaining levels
            current_width = width // 2
            current_height = height // 2
            level_num = 1

            while current_width >= 1 and current_height >= 1:
                # Scale down
                scaled_image = source_image.scaled(
                    current_width, current_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if scaled_image.isNull():
                    break

                # Convert to RGBA
                scaled_image = scaled_image.convertToFormat(QImage.Format.Format_RGBA8888)
                ptr = scaled_image.bits()
                ptr.setsize(scaled_image.sizeInBytes())
                rgba_data = bytes(ptr)

                # Add mipmap level
                mipmap_level = {
                    'level': level_num,
                    'width': current_width,
                    'height': current_height,
                    'rgba_data': rgba_data,
                    'compressed_data': None,
                    'compressed_size': len(rgba_data)
                }
                self.selected_texture['mipmap_levels'].append(mipmap_level)

                # Next levelhas_bumpmap
                current_width = max(1, current_width // 2)
                current_height = max(1, current_height // 2)
                level_num += 1

            # Update mipmap count
            self.selected_texture['mipmaps'] = len(self.selected_texture['mipmap_levels'])

            # Update display
            self._update_texture_info(self.selected_texture)
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Generated {level_num} mipmap levels")

            QMessageBox.information(self, "Success",
                f"Generated {level_num} mipmap levels\n"
                f"From {width}x{height} down to {current_width*2}x{current_height*2}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mipmaps: {str(e)}")


    def _show_texture_context_menu(self, position): #vers 2
        """Show context menu for texture operations - simplified"""
        if not self.selected_texture:
            return

        has_alpha = self.selected_texture.get('has_alpha', False)

        menu = QMenu(self)

        # Import submenu
        import_menu = menu.addMenu(self._create_import_icon(), "Import")

        import_normal_action = import_menu.addAction("Import Texture")
        import_normal_action.triggered.connect(self._import_normal_texture)

        if has_alpha:
            import_alpha_action = import_menu.addAction("Import Alpha Channel")
            import_alpha_action.triggered.connect(self._import_alpha_texture)

        # Export submenu
        export_menu = menu.addMenu(self._create_export_icon(), "Export")

        export_texture_action = export_menu.addAction("Export Texture")
        export_texture_action.triggered.connect(self.export_selected_texture)

        if has_alpha:
            export_alpha_action = export_menu.addAction("Export Alpha Channel")
            export_alpha_action.triggered.connect(self._export_alpha_only)

        menu.addSeparator()

        # Delete texture
        delete_action = menu.addAction(self._create_trash_icon(), "Delete Texture")
        delete_action.triggered.connect(self._delete_texture)

        menu.exec(self.texture_table.viewport().mapToGlobal(position))


    def load_from_img_archive(self, img_path): #vers 1
        """Load TXD list from IMG archive"""
        try:
            if self.main_window and hasattr(self.main_window, 'current_img'):
                self.current_img = self.main_window.current_img
            else:
                from methods.img_core_classes import IMGFile
                self.current_img = IMGFile(img_path)
                self.current_img.open()

            img_name = os.path.basename(img_path)
            self.setWindowTitle(f"TXD Workshop: {img_name}")
            self._load_img_txd_list()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ TXD Workshop loaded: {img_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load IMG: {str(e)}")


    def _show_txd_info(self): #vers 4
        """Show TXD Workshop information dialog - About and capabilities"""
        dialog = QDialog(self)
        dialog.setWindowTitle("About TXD Workshop")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Header
        header = QLabel("TXD Workshop for IMG Factory 1.5")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Author info
        author_label = QLabel("Author: X-Seti")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)

        # Version info
        version_label = QLabel("Version: 1.5 - October 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addWidget(QLabel(""))  # Spacer

        # Capabilities section
        capabilities = QTextEdit()
        capabilities.setReadOnly(True)
        capabilities.setMaximumHeight(350)

        info_text = """<b>TXD Workshop Capabilities:</b><br><br>

<b>✓ File Operations:</b><br>
- Open TXD files (standalone or from IMG archives)<br>
- Save TXD files back to IMG or as standalone<br>
- Create new TXD files from scratch<br>
- Multi-TXD management from IMG archives<br><br>

<b>✓ Texture Viewing & Editing:</b><br>
- View all textures with thumbnails<br>
- Preview textures with zoom and pan controls<br>
- Flip textures (horizontal/vertical)<br>
- Rotate textures (90°, 180°, 270°)<br>
- Resize textures with interpolation<br>
- Rename textures and alpha channels<br>
- View texture properties (size, format, compression)<br><br>

<b>✓ Texture Management:</b><br>
- Import textures (PNG, JPG, BMP, TGA, DDS)<br>
- Import 8-bit indexed formats (PCX, GIF, IFF/Amiga)<br>
- Export single or multiple textures<br>
- Duplicate textures<br>
- Delete textures<br>
- Undo/Redo operations<br><br>

<b>✓ Format Support:</b><br>
- DXT1/DXT3/DXT5 compression<br>
- Uncompressed ARGB8888, RGB888<br>
- 16-bit and 32-bit formats<br>
- Palette-based textures<br>
- Platform-specific formats (PC, Xbox, PS2)<br><br>

<b>✓ Advanced Features:</b><br>
- Mipmap generation and editing<br>
- Bumpmap support (generate from height/normal maps)<br>
- Alpha channel extraction and editing<br>
- Batch export operations<br>
- Texture filtering and search<br>
- External editor integration<br>
- AI upscaling support (if configured)<br><br>

<b>✓ Platform Detection:</b><br>
- Automatic RenderWare version detection<br>
- Platform identification (PC, Xbox, PS2, Android)<br>
- Game detection (GTA III, VC, SA, Manhunt)<br>
- Format capability validation<br><br>

<b>✓ Import Format Support:</b><br>"""

        # Add format support dynamically
        formats_available = []

        # Standard formats (always via PIL)
        formats_available.append("- PNG, JPG, JPEG (all variants)")
        formats_available.append("- BMP (8/16/24/32-bit)")
        formats_available.append("- TGA/Targa (all variants)")
        formats_available.append("- DDS (DirectDraw Surface)")

        # Check indexed format support
        try:
            if self.iff_import_enabled:
                formats_available.append("- IFF/ILBM (Amiga 8-bit)")
        except:
            pass

        # Always available via indexed_color_import
        formats_available.append("- PCX (ZSoft Paintbrush)")
        formats_available.append("- GIF (with transparency)")
        formats_available.append("- PNG (8-bit indexed mode)")

        info_text += "<br>".join(formats_available)
        info_text += "<br><br>"

        # Settings info
        info_text += """<b>✓ Customization:</b><br>
- Configurable dimension limiting<br>
- Adjustable texture name length (8-64 chars)<br>
- Splash screen dimension support<br>
- Button display modes (Icons/Text/Both)<br>
- Font customization<br>
- Preview zoom and pan offsets<br><br>

<b>Keyboard Shortcuts:</b><br>
- Ctrl+O: Open TXD<br>
- Ctrl+S: Save TXD<br>
- Ctrl+I: Import Texture<br>
- Ctrl+E: Export Selected<br>
- Ctrl+Z: Undo<br>
- Delete: Remove Texture<br>
- Ctrl+D: Duplicate Texture<br>"""

        capabilities.setHtml(info_text)
        layout.addWidget(capabilities)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setDefault(True)
        layout.addWidget(close_btn)

        dialog.exec()


    def _load_img_txd_list(self): #vers 1
        """Load TXD files from IMG archive"""
        try:
            self.txd_list_widget.clear()
            self.txd_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    self.txd_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.txd_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} TXD files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading TXD list: {str(e)}")


    def _on_txd_selected(self, item): #vers 1
        """Handle TXD file selection"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                txd_data = self._extract_txd_from_img(entry)
                if txd_data:
                    self.current_txd_data = txd_data
                    self.current_txd_name = entry.name
                    self._load_txd_textures(txd_data, entry.name)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error selecting TXD: {str(e)}")


    def _extract_txd_from_img(self, entry): #vers 2
        """Extract TXD data from IMG entry"""
        try:
            if not self.current_img:
                return None
            return self.current_img.read_entry_data(entry)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Extract error: {str(e)}")
            return None


    def _load_txd_textures(self, txd_data, txd_name): #vers 12
        """Load textures from TXD data - display with mipmap info"""
        try:
            import struct

            self.texture_table.setRowCount(0)
            self.texture_list = []
            textures = []
            offset = 12
            if self.txd_version_id == 0:
                self._detect_txd_info(txd_data)

            self.current_txd_data = txd_data
            self.current_txd_name = txd_name

            # Get texture count
            texture_count = 0
            if offset + 12 < len(txd_data):
                try:
                    st, ss, sv = struct.unpack('<III', txd_data[offset:offset+12])
                    offset += 12
                    if ss >= 4:
                        texture_count = struct.unpack('<I', txd_data[offset:offset+4])[0]
                        offset += ss
                except:
                    pass

            # Parse each texture
            if 0 < texture_count < 500:
                for i in range(texture_count):
                    if offset + 12 > len(txd_data):
                        break
                    try:
                        stype, ssize, sver = struct.unpack('<III', txd_data[offset:offset+12])
                        if stype == 0x15:  # Texture Native
                            tex = self._parse_single_texture(txd_data, offset, i)
                            if tex:
                                textures.append(tex)
                        offset += 12 + ssize
                    except:
                        offset += 1000
                        continue

            if not textures:
                textures = [{'name': 'No textures', 'width': 0, 'height': 0, 'has_alpha': False,
                            'format': 'Unknown', 'mipmaps': 0, 'rgba_data': None, 'mipmap_levels': []}]

            # Populate table with mipmap info
            for tex in textures:
                self.texture_list.append(tex)
                row = self.texture_table.rowCount()
                self.texture_table.insertRow(row)

                thumb_item = QTableWidgetItem()
                if tex.get('rgba_data') and tex['width'] > 0:
                    pixmap = self._create_thumbnail(tex['rgba_data'], tex['width'], tex['height'])
                    if pixmap:
                        thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                    else:
                        thumb_item.setText("🖼️")
                else:
                    thumb_item.setText("🖼️")

                # Build details text with mipmap info
                depth = tex.get('depth', 32)
                details = f"Name: {tex['name']} - {depth}bit\n"

                # Alpha name line
                if tex.get('has_alpha', False):
                    alpha_name = tex.get('alpha_name', tex['name'] + 'a')
                    details += f"Alpha: {alpha_name}\n"
                else:
                    details += "\n"  # Empty line for spacing

                # Size and format line
                if tex['width'] > 0:
                    details += f"Size: {tex['width']}x{tex['height']} | Format: {tex['format']}\n"
                else:
                    details += f"Format: {tex['format']}\n"

                # Mipmap info line - CLICKABLE
                mipmap_levels = tex.get('mipmap_levels', [])
                num_mipmaps = len(mipmap_levels)

                if num_mipmaps > 0:
                    # Check if compressed
                    is_compressed = 'DXT' in tex['format']
                    compress_status = "compressed" if is_compressed else "uncompressed"
                    details += f"📊 {num_mipmaps} mipmap levels ({compress_status}) - Click to view"
                else:
                    details += "📊 No mipmaps"

                # Make items non-editable
                thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                details_item = QTableWidgetItem(details)
                details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.texture_table.setItem(row, 0, thumb_item)
                self.texture_table.setItem(row, 1, details_item)

            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHeight(row, 100)  # Increased height for mipmap line
            self.texture_table.setColumnWidth(0, 80)

            self.save_txd_btn.setEnabled(False)
            self.import_btn.setEnabled(True)
            self.export_all_btn.setEnabled(True)
            self._initialize_features()
            self._enable_txd_features_after_load()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Loaded {len(textures)} textures from {txd_name}")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error: {str(e)}")


    def _upscale_texture_advanced(self): #vers 1
        """Advanced AI upscale with options dialog"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QCheckBox, QPushButton

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("AI Upscale Options")
        dialog.setModal(True)
        dialog.resize(450, 400)

        layout = QVBoxLayout(dialog)

        # Current texture info
        width = self.selected_texture.get('width', 0)
        height = self.selected_texture.get('height', 0)

        header = QLabel(f"Current Size: {width}x{height}")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(header)

        # Scale factor
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale Factor:"))
        scale_combo = QComboBox()
        scale_combo.addItems(["2x", "3x", "4x", "6x", "8x"])
        scale_combo.setCurrentIndex(0)
        scale_layout.addWidget(scale_combo)
        layout.addLayout(scale_layout)

        # Preview size label
        preview_label = QLabel(f"Result: {width*2}x{height*2}")
        preview_label.setStyleSheet("color: #4a9eff; font-weight: bold; padding: 5px;")

        def update_preview(index):
            factor = [2, 3, 4, 6, 8][index]
            new_w = width * factor
            new_h = height * factor
            size_mb = (new_w * new_h * 4) / (1024 * 1024)
            preview_label.setText(f"Result: {new_w}x{new_h} (~{size_mb:.1f} MB)")

        scale_combo.currentIndexChanged.connect(update_preview)
        layout.addWidget(preview_label)

        layout.addSpacing(10)

        # Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        method_combo = QComboBox()
        method_combo.addItems(["Smooth (Bilinear)", "Sharp (Bicubic)", "Lanczos", "Nearest Neighbor"])
        method_combo.setCurrentIndex(1)
        method_layout.addWidget(method_combo)
        layout.addLayout(method_layout)

        # Sharpness slider
        sharp_layout = QVBoxLayout()
        sharp_layout.addWidget(QLabel("Sharpness:"))
        sharp_slider = QSlider(Qt.Orientation.Horizontal)
        sharp_slider.setMinimum(0)
        sharp_slider.setMaximum(100)
        sharp_slider.setValue(50)
        sharp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        sharp_slider.setTickInterval(25)
        sharp_layout.addWidget(sharp_slider)

        sharp_value_label = QLabel("50%")
        sharp_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sharp_slider.valueChanged.connect(lambda v: sharp_value_label.setText(f"{v}%"))
        sharp_layout.addWidget(sharp_value_label)
        layout.addLayout(sharp_layout)

        layout.addSpacing(10)

        # Options
        denoise_check = QCheckBox("Denoise (reduce noise)")
        denoise_check.setChecked(False)
        layout.addWidget(denoise_check)

        enhance_check = QCheckBox("Enhance edges")
        enhance_check.setChecked(True)
        layout.addWidget(enhance_check)

        preserve_alpha_check = QCheckBox("Preserve alpha channel")
        preserve_alpha_check.setChecked(True)
        layout.addWidget(preserve_alpha_check)

        layout.addSpacing(10)

        # Warning for large sizes
        warning_label = QLabel("⚠️ Large upscales may take time and increase file size significantly")
        warning_label.setStyleSheet("color: #ff9800; font-size: 11px; padding: 5px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_upscale():
            factor = [2, 3, 4, 6, 8][scale_combo.currentIndex()]
            method = method_combo.currentIndex()
            sharpness = sharp_slider.value()
            denoise = denoise_check.isChecked()
            enhance = enhance_check.isChecked()
            preserve_alpha = preserve_alpha_check.isChecked()

            dialog.accept()

            # Apply upscale (placeholder for now)
            QMessageBox.information(self, "Upscaling",
                f"Upscaling {factor}x with method {method_combo.currentText()}\n"
                f"Sharpness: {sharpness}%\n"
                f"Denoise: {denoise}\n"
                f"Enhance: {enhance}\n\n"
                f"Advanced upscaling will be implemented soon!")

        upscale_btn = QPushButton("Upscale")
        upscale_btn.clicked.connect(do_upscale)
        button_layout.addWidget(upscale_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _upscale_texture(self): #vers 2
        """AI upscale selected texture with size management"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get scale factor
        factor, ok = QInputDialog.getInt(self, "AI Upscale", "Scale factor:", value=2, min=2, max=8)
        if not ok:
            return

        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        new_width = current_width * factor
        new_height = current_height * factor

        # Calculate memory and file size impact
        old_size_mb = (current_width * current_height * 4) / (1024 * 1024)
        new_size_mb = (new_width * new_height * 4) / (1024 * 1024)

        if new_size_mb > 16:  # Warn for textures over 16MB uncompressed
            reply = QMessageBox.question(self, "Large Upscale",
                                    f"Upscaling {factor}x will create a {new_width}x{new_height} texture "
                                    f"(~{new_size_mb:.1f}MB uncompressed). "
                                    f"This will significantly increase TXD size. Continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Perform the upscale
        if self._perform_ai_upscale(factor):
            self.selected_texture['width'] = new_width
            self.selected_texture['height'] = new_height

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscaled texture {factor}x to {new_width}x{new_height}")
        else:
            QMessageBox.critical(self, "Error", "AI upscale failed")


    def _perform_ai_upscale(self, factor): #vers 1
        """Perform AI upscaling on texture data"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # For now, use basic upscaling (could be with actual AI upscaling libraries)
            return self._resize_texture_data(
                self.selected_texture['width'] * factor,
                self.selected_texture['height'] * factor
            )

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscale error: {str(e)}")
            return False


    def export_selected_texture(self): #vers 2
        """Export selected texture with channel options"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            name = self.selected_texture.get('name', 'texture')

            # Ask user what to export
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Export Options")
            dialog.setText(f"Export {name} as:")

            normal_btn = dialog.addButton("Normal (RGBA)", QMessageBox.ButtonRole.AcceptRole)
            alpha_btn = dialog.addButton("Alpha Channel Only", QMessageBox.ButtonRole.AcceptRole)
            both_btn = dialog.addButton("Both Separately", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            dialog.exec()
            clicked = dialog.clickedButton()

            if clicked == cancel_btn:
                return

            # Get save location
            default_name = f"{name}.png"
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Texture", default_name,
                                                    "PNG Files (*.png);;All Files (*)")

            if not file_path:
                return

            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if not rgba_data or width <= 0:
                QMessageBox.critical(self, "Error", "Cannot export this texture")
                return

            if clicked == normal_btn:
                self._save_texture_png(rgba_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported: {file_path}")

            elif clicked == alpha_btn:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported alpha: {file_path}")

            elif clicked == both_btn:
                # Save normal
                self._save_texture_png(rgba_data, width, height, file_path)
                # Save alpha
                alpha_path = file_path.replace('.png', '_alpha.png')
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, alpha_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported both: {file_path} and {alpha_path}")

            QMessageBox.information(self, "Success", "Texture exported successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


    def export_all_textures(self): #vers 1
        """Export all textures in current TXD"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures to export")
            return

        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        try:
            exported = 0
            for texture in self.texture_list:
                name = texture.get('name', f'texture_{exported}')
                rgba_data = texture.get('rgba_data')
                width = texture.get('width', 0)
                height = texture.get('height', 0)

                if rgba_data and width > 0:
                    file_path = os.path.join(output_dir, f"{name}.png")
                    self._save_texture_png(rgba_data, width, height, file_path)
                    exported += 1

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Exported {exported} textures to {output_dir}")

            QMessageBox.information(self, "Success", f"Exported {exported} textures successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


    def _extract_alpha_channel(self, rgba_data): #vers 1
        """Extract alpha channel as grayscale RGBA"""
        alpha_data = bytearray()
        for i in range(0, len(rgba_data), 4):
            a = rgba_data[i+3]
            alpha_data.extend([a, a, a, 255])
        return bytes(alpha_data)


    def _save_texture_png(self, rgba_data, width, height, file_path): #vers 1
        """Save RGBA data as PNG"""
        image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
        if not image.save(file_path):
            raise Exception("Failed to save PNG")


    def _export_alpha_only(self): #vers 1
        """Export only alpha channel"""
        if not self.selected_texture:
            return

        name = self.selected_texture.get('name', 'texture')
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Alpha Channel", f"{name}_alpha.png",
                                                "PNG Files (*.png)")
        if file_path:
            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if rgba_data:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                QMessageBox.information(self, "Success", "Alpha channel exported!")


    def _change_format(self, format_name): #vers 2
        """Change texture format - only set has_alpha if alpha data exists"""
        if not self.selected_texture:
            return

        old_format = self.selected_texture.get('format', 'Unknown')
        self.selected_texture['format'] = format_name

        # Check if texture actually has alpha data
        has_actual_alpha = False
        rgba_data = self.selected_texture.get('rgba_data')

        if rgba_data:
            # Check if any alpha values are not 255 (fully opaque)
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if width > 0 and height > 0:
                # Sample alpha channel - check every pixel's alpha value
                for i in range(3, len(rgba_data), 4):  # Every 4th byte is alpha
                    if rgba_data[i] < 255:  # Found non-opaque pixel
                        has_actual_alpha = True
                        break

        # Update alpha flag based on format AND actual alpha data
        if format_name in ['DXT3', 'DXT5', 'ARGB8888', 'ARGB1555', 'ARGB4444']:
            # Only set has_alpha if texture actually contains alpha data
            self.selected_texture['has_alpha'] = has_actual_alpha

            # If format supports alpha but texture doesn't have it, warn user
            if not has_actual_alpha:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"⚠️ {format_name} supports alpha, but texture has no alpha data")

        elif format_name in ['DXT1', 'RGB888', 'RGB565']:
            # These formats don't support alpha
            self.selected_texture['has_alpha'] = False

            # Remove alpha_name if switching to non-alpha format
            if 'alpha_name' in self.selected_texture:
                del self.selected_texture['alpha_name']

        self._update_texture_info(self.selected_texture)
        self._update_table_display()
        self._mark_as_modified()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            alpha_status = "with alpha" if self.selected_texture['has_alpha'] else "no alpha"
            self.main_window.log_message(f"Format changed: {old_format} -> {format_name} ({alpha_status})")


    def _compress_texture(self): #vers 3
        """Compress selected texture to DXT format"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' in current_format:
            # Already compressed - offer to change DXT version
            from PyQt6.QtWidgets import QInputDialog

            dxt_formats = ["DXT1", "DXT3", "DXT5"]
            new_format, ok = QInputDialog.getItem(
                self,
                "Change DXT Format",
                f"Current format: {current_format}\n\nSelect target DXT format:",
                dxt_formats,
                0,
                False
            )

            if ok and new_format != current_format:
                self._save_undo_state("Change DXT format")
                self.selected_texture['format'] = new_format

                # Update has_alpha based on format
                if new_format == 'DXT1':
                    # DXT1 can have 1-bit alpha, keep existing alpha state
                    pass
                elif new_format in ['DXT3', 'DXT5']:
                    # DXT3/DXT5 have alpha
                    if not self.selected_texture.get('has_alpha'):
                        self.selected_texture['has_alpha'] = True
                        if 'alpha_name' not in self.selected_texture:
                            self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

                # Update dropdown
                if hasattr(self, 'format_combo'):
                    index = self.format_combo.findText(new_format)
                    if index >= 0:
                        self.format_combo.setCurrentIndex(index)

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Changed format: {current_format} → {new_format}")

            return

        # Not compressed - compress to DXT
        if not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Data", "Texture has no image data to compress")
            return

        try:
            # Let user choose DXT format
            from PyQt6.QtWidgets import QInputDialog

            has_alpha = self.selected_texture.get('has_alpha', False)

            if has_alpha:
                dxt_formats = ["DXT3", "DXT5", "DXT1"]
                default_format = "DXT5"
                message = "Texture has alpha channel.\n\nRecommended: DXT5 (best quality)\nAlternative: DXT3 (simpler alpha)\nDXT1: 1-bit alpha only"
            else:
                dxt_formats = ["DXT1", "DXT3", "DXT5"]
                default_format = "DXT1"
                message = "Texture has no alpha channel.\n\nRecommended: DXT1 (smallest size)"

            target_format, ok = QInputDialog.getItem(
                self,
                "Compress Texture",
                f"Current format: {current_format}\n\n{message}\n\nSelect DXT format:",
                dxt_formats,
                dxt_formats.index(default_format),
                False
            )

            if not ok:
                return

            # Save undo state
            self._save_undo_state("Compress texture")
            self.selected_texture['format'] = target_format

            # Update has_alpha if compressing to DXT3/DXT5
            if target_format in ['DXT3', 'DXT5'] and not has_alpha:
                self.selected_texture['has_alpha'] = True
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            # Update dropdown
            if hasattr(self, 'format_combo'):
                index = self.format_combo.findText(target_format)
                if index >= 0:
                    self.format_combo.setCurrentIndex(index)

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Compressed: {current_format} → {target_format}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compress: {str(e)}")


    def _uncompress_texture(self): #vers 3
        """Uncompress selected texture from DXT to ARGB8888"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' not in current_format:
            QMessageBox.information(self, "Not Compressed", "Texture is not in DXT format")
            return

        try:
            reply = QMessageBox.question(
                self,
                "Uncompress Texture",
                f"Uncompress to ARGB8888?\n\n"
                f"Current: {current_format}\n"
                f"Target: ARGB8888\n\n"
                f"This will convert the texture to uncompressed format.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            if self.selected_texture.get('rgba_data'):
                self._save_undo_state("Uncompress texture")
                self.selected_texture['format'] = 'ARGB8888'

                # Update dropdown to show ARGB8888
                if hasattr(self, 'format_combo'):
                    index = self.format_combo.findText('ARGB8888')
                    if index >= 0:
                        self.format_combo.setCurrentIndex(index)

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Uncompressed: {current_format} → ARGB8888")
            else:
                QMessageBox.warning(self, "No Data", "Texture has no decompressed data available")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to uncompress: {str(e)}")


    def _show_name_context_menu(self, position, alpha=False): #vers 1
        """Show context menu for renaming texture or alpha name"""
        if not self.selected_texture:
            return

        # Don't show alpha context menu if no alpha channel
        if alpha and not self.selected_texture.get('has_alpha', False):
            return

        menu = QMenu(self)

        if alpha:
            rename_action = menu.addAction("Rename Alpha")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=True))
        else:
            rename_action = menu.addAction("Rename Texture")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=False))

        # Show menu at the cursor position
        menu.exec(self.sender().mapToGlobal(position))


    def _calculate_new_txd_size(self): #vers 1
        """Calculate estimated new TXD size including actual texture data"""
        estimated_size = 1024  # Header overhead

        for texture in self.texture_list:
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            fmt = texture.get('format', 'DXT1')
            has_data = texture.get('rgba_data') is not None

            if has_data:
                # Use actual data size if available
                rgba_size = len(texture['rgba_data'])

                # Estimate compressed size based on format
                if 'DXT1' in fmt:
                    estimated_size += rgba_size // 8  # DXT1 compression
                elif 'DXT5' in fmt:
                    estimated_size += rgba_size // 4  # DXT5 compression
                else:
                    estimated_size += rgba_size  # Uncompressed
            else:
                # Fallback to dimension-based estimation
                if 'DXT1' in fmt:
                    estimated_size += (width * height) // 2
                elif 'DXT5' in fmt:
                    estimated_size += width * height
                else:
                    estimated_size += width * height * 4

            estimated_size += 200  # Header per texture

        return estimated_size


    def _rebuild_txd_data(self): #vers 3
        """Rebuild TXD data with modified texture names and properties"""
        try:
            if not self.current_txd_data:
                return None

            # Preserve original version header
            if len(self.current_txd_data) < 28:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("Cannot rebuild: insufficient header data")
                return None

            # Read original header to preserve version
            original_header = bytearray(self.current_txd_data[:28])

            # Extract version info if not already detected
            if self.txd_version_id == 0:
                self._detect_txd_info(self.current_txd_data)

            # Check if we have a target version from save_txd_file
            target_version = self.txd_version_id
            target_device = self.txd_device_id

            if hasattr(self, '_save_target_version') and hasattr(self, '_save_target_device'):
                target_version = self._save_target_version
                target_device = self._save_target_device

            # Update header if converting to different version
            if target_version != self.txd_version_id or target_device != self.txd_device_id:
                import struct
                # Update RenderWare version at offset 4
                struct.pack_into('<I', original_header, 4, target_version)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    from methods.txd_versions import get_version_string
                    self.main_window.log_message(
                        f"Converting to {get_version_string(target_version, target_device)}"
                    )
            else:
                # Log rebuild info with original version
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(
                        f"Rebuilding TXD with version: {self.txd_version_str}"
                    )

            # Import struct for header manipulation
            import struct

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuilding TXD...")

            # If we have original data, update it in place with new header
            if self.current_txd_data and len(self.current_txd_data) > 100:
                rebuilt_data = bytes(original_header) + self.current_txd_data[28:]

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Rebuilt: {len(rebuilt_data)} bytes")

                return rebuilt_data

            # No original data? Use serializer as fallback
            if self.texture_list:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Using serializer...")

                # Try methods folder first (docked/IMG Factory)
                try:
                    from methods.txd_serializer import serialize_txd_file
                    return serialize_txd_file(self.texture_list, target_version, target_device)
                except ImportError:
                    # Fallback to depends folder (standalone)
                    from depends.txd_serializer import serialize_txd_file
                    return serialize_txd_file(self.texture_list, target_version, target_device)

            return None

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuild error: {str(e)}")
            return None


    def _update_texture_in_data(self, data, offset, texture_info): #vers 1
        """Update texture properties in the binary TXD data"""
        try:
            import struct

            # Navigate to the texture data location
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', data[struct_offset:struct_offset+12])

            if struct_type == 0x01:  # Struct section
                name_pos = struct_offset + 12 + 8  # Skip header and platform info

                # Update texture name (32 bytes)
                new_name = texture_info.get('name', 'texture')[:31]
                name_bytes = new_name.encode('ascii')[:31].ljust(32, b'\x00')
                data[name_pos:name_pos+32] = name_bytes

                # Update alpha/mask name if it exists (next 32 bytes)
                if texture_info.get('has_alpha', False) and texture_info.get('alpha_name'):
                    alpha_name = texture_info.get('alpha_name', '')[:31]
                    alpha_bytes = alpha_name.encode('ascii')[:31].ljust(32, b'\x00')
                    data[name_pos+32:name_pos+64] = alpha_bytes

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Name update error: {str(e)}")


    def _get_format_description(self) -> str: #vers 1
        """Get human-readable format description for UI display"""
        desc_parts = []

        if self.txd_capabilities:
            # Bit depths
            if self.txd_capabilities.get('bit_depths'):
                depths = ', '.join(str(d) for d in self.txd_capabilities['bit_depths'])
                desc_parts.append(f"{depths}-bit")

            # Features
            features = []
            if self.txd_capabilities.get('mipmaps'):
                features.append("Mipmaps")
            if self.txd_capabilities.get('bumpmaps'):
                features.append("Bumpmaps")
            if self.txd_capabilities.get('dxt_compression'):
                features.append("DXT")
            if self.txd_capabilities.get('palette'):
                features.append("Palette")
            if self.txd_capabilities.get('swizzled'):
                features.append("Swizzled")

            if features:
                desc_parts.append(', '.join(features))

        return ' | '.join(desc_parts) if desc_parts else "Standard format"


    def _update_img_with_txd(self, modified_txd_data): #vers 4
        """Update IMG archive using IMG Factory's save system"""
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Starting IMG update...")

            # Check prerequisites
            if not self.current_img:
                raise Exception("No current IMG file loaded")

            if not self.current_txd_name:
                raise Exception("No current TXD name available")

            # Find and update the TXD entry
            txd_entry = None
            for entry in self.current_img.entries:
                if entry.name == self.current_txd_name:
                    txd_entry = entry
                    break

            if not txd_entry:
                raise Exception(f"TXD entry '{self.current_txd_name}' not found in IMG")

            # Update the entry data IN MEMORY
            old_size = txd_entry.size
            txd_entry.data = modified_txd_data
            txd_entry.size = len(modified_txd_data)

            # Mark IMG as modified
            if hasattr(self.current_img, 'modified'):
                self.current_img.modified = True

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"TXD entry updated in memory: {old_size} -> {len(modified_txd_data)} bytes"
                )

            # CRITICAL: Now write to disk
            save_successful = False

            # Method 1: Use IMG's save method directly
            if hasattr(self.current_img, 'save') and hasattr(self.current_img, 'file_path'):
                try:
                    self.current_img.save(self.current_img.file_path)
                    save_successful = True
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(
                            f"✅ Saved directly to: {self.current_img.file_path}"
                        )
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"Direct save failed: {str(e)}")

            # Method 2: Use main window's save_img_entry
            if not save_successful and hasattr(self.main_window, 'save_img_entry'):
                try:
                    self.main_window.save_img_entry()
                    save_successful = True
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("✅ Saved via main_window.save_img_entry()")
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"save_img_entry failed: {str(e)}")

            if not save_successful:
                raise Exception("All save methods failed - changes only in memory!")

            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ IMG update error: {str(e)}")
            return False


    def _resize_texture(self): #vers 1
        """Resize selected texture with size validation"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get current dimensions
        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        # Get new dimensions from user
        w, ok1 = QInputDialog.getInt(self, "Resize Texture", "New width:",value=current_width, min=1, max=4096)
        if not ok1:
            return

        h, ok2 = QInputDialog.getInt(
            self, "Resize Texture", "New height:",
            value=current_height, min=1, max=4096
        )
        if not ok2:
            return

        # Calculate size impact
        old_pixels = current_width * current_height
        new_pixels = w * h
        size_multiplier = new_pixels / old_pixels if old_pixels > 0 else 1

        # Warn for large size increases
        if size_multiplier > 4:
            reply = QMessageBox.question(
                self, "Large Resize",
                f"Resizing to {w}x{h} will increase texture size by {size_multiplier:.1f}x. "
                f"This may require IMG rebuilding. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Update texture dimensions
        self.selected_texture['width'] = w
        self.selected_texture['height'] = h

        # If we have RGBA data, resize it
        if self.selected_texture.get('rgba_data'):
            self._resize_texture_data(w, h)

        # Update display
        self._update_texture_info(self.selected_texture)
        self._update_table_display()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Resized texture to {w}x{h}")


    def _resize_texture_data(self, new_width, new_height): #vers 1
        """Resize the actual texture image data using QImage"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # Convert current RGBA data to QImage
            rgba_data = self.selected_texture['rgba_data']
            old_width = self.selected_texture['width']
            old_height = self.selected_texture['height']

            qimg = QImage(rgba_data, old_width, old_height, old_width * 4, QImage.Format.Format_RGBA8888)

            # Resize image with high quality
            resized_img = qimg.scaled(new_width, new_height,
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)

            # Convert back to RGBA data
            resized_img = resized_img.convertToFormat(QImage.Format.Format_RGBA8888)

            # Get raw bytes from QImage
            ptr = resized_img.bits()
            ptr.setsize(resized_img.sizeInBytes())
            new_rgba_data = bytes(ptr)

            # Update texture data
            self.selected_texture['rgba_data'] = new_rgba_data
            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Resize data error: {str(e)}")
            return False


    def _show_version_selector_dialog(self): #vers 1
        """Show RW version selector dialog for export"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                    QComboBox, QPushButton, QGroupBox, QCheckBox)
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Export Version")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Info label
        info_label = QLabel("Select target game and platform for TXD export:")
        layout.addWidget(info_label)

        # Game selection
        game_group = QGroupBox("Target Game")
        game_layout = QVBoxLayout()

        game_combo = QComboBox()
        game_combo.addItems([
            "Auto-detect from current",
            "GTA III",
            "GTA Vice City",
            "GTA San Andreas"
        ])

        # Set current based on detected or settings
        if hasattr(self, 'txd_game') and self.txd_game:
            if "III" in self.txd_game:
                game_combo.setCurrentIndex(1)
            elif "Vice" in self.txd_game or "VC" in self.txd_game:
                game_combo.setCurrentIndex(2)
            elif "San" in self.txd_game or "SA" in self.txd_game:
                game_combo.setCurrentIndex(3)
        elif hasattr(self, 'export_target_game'):
            game_map = {"auto": 0, "gta3": 1, "vc": 2, "sa": 3}
            game_combo.setCurrentIndex(game_map.get(self.export_target_game, 0))

        game_layout.addWidget(game_combo)
        game_group.setLayout(game_layout)
        layout.addWidget(game_group)

        # Platform selection
        platform_group = QGroupBox("Target Platform")
        platform_layout = QVBoxLayout()

        platform_combo = QComboBox()
        platform_combo.addItems([
            "PC",
            "Xbox",
            "PS2"
        ])

        if hasattr(self, 'export_target_platform'):
            platform_map = {"pc": 0, "xbox": 1, "ps2": 2}
            platform_combo.setCurrentIndex(platform_map.get(self.export_target_platform, 0))

        platform_layout.addWidget(platform_combo)
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)

        # Version info display
        version_info_label = QLabel()
        version_info_label.setWordWrap(True)
        version_info_label.setStyleSheet("padding: 10px; background-color: #2a2a2a; border-radius: 4px;")
        layout.addWidget(version_info_label)

        # Capability warnings
        warning_label = QLabel()
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #ff9800; padding: 5px;")
        layout.addWidget(warning_label)

        # Update info when selection changes
        def update_version_info():
            game_idx = game_combo.currentIndex()
            platform_idx = platform_combo.currentIndex()

            # Map to version IDs
            version_map = {
                (1, 0): (0x0C02FFFF, 0x01, "3.3.0.2 (GTA III PC)"),      # GTA III PC
                (1, 1): (0x35000, 0x08, "3.5.0.0 (GTA III Xbox)"),       # GTA III Xbox
                (1, 2): (0x00000310, 0x06, "3.1.0.0 (GTA III PS2)"),     # GTA III PS2
                (2, 0): (0x1003FFFF, 0x01, "3.4.0.3 (Vice City PC)"),    # VC PC
                (2, 1): (0x35000, 0x08, "3.5.0.0 (Vice City Xbox)"),     # VC Xbox
                (2, 2): (0x0C02FFFF, 0x06, "3.3.0.2 (Vice City PS2)"),   # VC PS2
                (3, 0): (0x1803FFFF, 0x08, "3.6.0.3 (San Andreas PC)"),  # SA PC
                (3, 1): (0x1803FFFF, 0x08, "3.6.0.3 (San Andreas Xbox)"),# SA Xbox
                (3, 2): (0x1803FFFF, 0x06, "3.6.0.3 (San Andreas PS2)"), # SA PS2
            }

            if game_idx == 0:  # Auto-detect
                version_id = self.txd_version_id if self.txd_version_id else 0x1803FFFF
                device_id = self.txd_device_id if self.txd_device_id else 0x08
                version_str = f"Current: 0x{version_id:08X} (device: 0x{device_id:02X})"
            else:
                version_id, device_id, version_str = version_map.get((game_idx, platform_idx),
                                                                    (0x1803FFFF, 0x08, "3.6.0.3 (SA PC)"))

            version_info_label.setText(f"<b>RW Version:</b> {version_str}")

            # Check capabilities and show warnings
            warnings = []

            # GTA III limitations
            if game_idx == 1:
                warnings.append("⚠️ GTA III: Mipmaps and bumpmaps not supported - will be removed")
                warnings.append("⚠️ Limited texture formats supported")

            # VC limitations
            if game_idx == 2 and platform_idx == 2:  # VC PS2
                warnings.append("⚠️ VC PS2: Mipmaps and bumpmaps not supported - will be removed")

            if warnings:
                warning_label.setText("\n".join(warnings))
                warning_label.setVisible(True)
            else:
                warning_label.setVisible(False)

            # Store selection
            dialog.selected_version = version_id
            dialog.selected_device = device_id
            dialog.selected_game_idx = game_idx

        game_combo.currentIndexChanged.connect(update_version_info)
        platform_combo.currentIndexChanged.connect(update_version_info)
        update_version_info()  # Initial update

        # Remember choice checkbox
        remember_cb = QCheckBox("Remember this choice for future exports")
        layout.addWidget(remember_cb)

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update settings if remember is checked
            if remember_cb.isChecked():
                game_map = {0: "auto", 1: "gta3", 2: "vc", 3: "sa"}
                platform_map = {0: "pc", 1: "xbox", 2: "ps2"}
                self.export_target_game = game_map.get(dialog.selected_game_idx, "auto")
                self.export_target_platform = platform_map.get(platform_combo.currentIndex(), "pc")

            return (dialog.selected_version, dialog.selected_device, dialog.selected_game_idx)

        return None


    def _strip_unsupported_features_for_version(self, game_idx): #vers 1
        """Remove unsupported features based on target game version"""
        if game_idx == 1:  # GTA III
            # Remove mipmaps and bumpmaps from all textures
            removed_mipmaps = 0
            removed_bumpmaps = 0

            for texture in self.texture_list:
                # Remove mipmaps
                if texture.get('mipmap_levels'):
                    removed_mipmaps += len(texture['mipmap_levels'])
                    texture['mipmap_levels'] = []
                    texture['mipmaps'] = 1

                # Remove bumpmaps
                if texture.get('has_bumpmap') or texture.get('bumpmap_data'):
                    removed_bumpmaps += 1
                    texture['has_bumpmap'] = False
                    texture['bumpmap_data'] = b''
                    texture['bumpmap_type'] = 0

                    # Clear bumpmap flag
                    if 'raster_format_flags' in texture:
                        texture['raster_format_flags'] &= ~0x10

                # Remove reflection maps
                if texture.get('has_reflection'):
                    texture['has_reflection'] = False
                    texture['reflection_map'] = b''
                    texture['fresnel_map'] = b''

            if self.main_window and hasattr(self.main_window, 'log_message'):
                if removed_mipmaps > 0:
                    self.main_window.log_message(f"Removed {removed_mipmaps} mipmap levels (GTA III doesn't support mipmaps)")
                if removed_bumpmaps > 0:
                    self.main_window.log_message(f"Removed {removed_bumpmaps} bumpmaps (GTA III doesn't support bumpmaps)")


    def _save_as_txd_file(self): #vers 4
        """Save as standalone TXD file - respects save location setting"""
        import os
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        # Determine default filename
        if self.current_txd_name:
            default_name = self.current_txd_name
        else:
            default_name = "untitled.txd"

        # Determine initial directory based on setting
        if self.save_to_source_location:
            # Option 1: Save to source location (default)
            if hasattr(self, 'current_txd_path') and self.current_txd_path:
                # Use the original TXD file's directory
                initial_path = self.current_txd_path
            elif hasattr(self, 'current_img') and self.current_img and hasattr(self.current_img, 'file_path'):
                # Use IMG file's directory
                img_dir = os.path.dirname(self.current_img.file_path)
                initial_path = os.path.join(img_dir, default_name)
            elif self.last_save_directory:
                # Use last saved directory
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                # Fallback to just filename
                initial_path = default_name
        else:
            # Option 2: Use last saved directory or current directory
            if self.last_save_directory:
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                initial_path = default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save TXD File",
            initial_path,
            "TXD Files (*.txd);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(modified_txd_data)

            # Store paths for next time
            self.current_txd_path = file_path
            self.current_txd_name = os.path.basename(file_path)
            self.last_save_directory = os.path.dirname(file_path)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Saved TXD file: {file_path}")

            QMessageBox.information(self, "Success",
                f"TXD saved successfully!\n\n{file_path}")

            # Clear modified state
            self.save_txd_btn.setEnabled(False)
            self.save_txd_btn.setStyleSheet("")
            title = self.windowTitle().replace("*", "")
            self.setWindowTitle(title)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD:\n\n{str(e)}")


    # Update the main save_txd_file method to use version selector:
    def save_txd_file(self): #vers 6
        """Save TXD file with version selector"""
        from PyQt6.QtWidgets import QMessageBox

        if not self.current_img:
            # Standalone TXD save with version selector
            return self._save_as_txd_file_with_version_selector()
        else:
            # IMG-based TXD save with version selector
            return self._save_txd_to_img_with_version_selector()


    def _save_as_txd_file_with_version_selector(self): #vers 1
        """Save standalone TXD with version selector"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os

        # Show version selector
        version_info = self._show_version_selector_dialog()
        if not version_info:
            return  # User cancelled

        target_version, target_device, game_idx = version_info

        # Strip unsupported features based on game version
        self._strip_unsupported_features_for_version(game_idx)

        # Determine default filename
        if self.current_txd_name:
            default_name = self.current_txd_name
        else:
            default_name = "untitled.txd"

        # Determine initial directory
        if self.save_to_source_location:
            if hasattr(self, 'current_txd_path') and self.current_txd_path:
                initial_path = self.current_txd_path
            elif hasattr(self, 'current_img') and self.current_img and hasattr(self.current_img, 'file_path'):
                img_dir = os.path.dirname(self.current_img.file_path)
                initial_path = os.path.join(img_dir, default_name)
            elif hasattr(self, 'last_save_directory') and self.last_save_directory:
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                initial_path = default_name
        else:
            if hasattr(self, 'last_save_directory') and self.last_save_directory:
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                initial_path = default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save TXD File",
            initial_path,
            "TXD Files (*.txd);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Store target version for rebuild
            self._save_target_version = target_version
            self._save_target_device = target_device

            # Rebuild TXD data with target version
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(modified_txd_data)

            # Store paths
            self.current_txd_path = file_path
            self.current_txd_name = os.path.basename(file_path)
            self.last_save_directory = os.path.dirname(file_path)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Saved TXD: {file_path}")
                self.main_window.log_message(f"   Version: 0x{target_version:08X}, Device: 0x{target_device:02X}")

            QMessageBox.information(self, "Success",
                f"TXD saved successfully!\n\n{file_path}\n\nVersion: 0x{target_version:08X}")

            # Clear modified state
            if hasattr(self, 'save_txd_btn'):
                self.save_txd_btn.setEnabled(False)
                self.save_txd_btn.setStyleSheet("")
            title = self.windowTitle().replace("*", "")
            self.setWindowTitle(title)

            # Clean up
            if hasattr(self, '_save_target_version'):
                delattr(self, '_save_target_version')
            if hasattr(self, '_save_target_device'):
                delattr(self, '_save_target_device')

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD:\n\n{str(e)}")


    def _save_txd_to_img_with_version_selector(self): #vers 1
        """Save TXD back to IMG with version selector"""
        from PyQt6.QtWidgets import QMessageBox

        if not self.current_img or not self.current_txd_name:
            QMessageBox.warning(self, "Cannot Save", "No IMG archive or TXD loaded")
            return

        # Show version selector
        version_info = self._show_version_selector_dialog()
        if not version_info:
            return  # User cancelled

        target_version, target_device, game_idx = version_info

        # Strip unsupported features
        self._strip_unsupported_features_for_version(game_idx)

        try:
            # Store target version for rebuild
            self._save_target_version = target_version
            self._save_target_device = target_device

            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Find entry in IMG
            entry = None
            for e in self.current_img.entries:
                if e.name.lower() == self.current_txd_name.lower():
                    entry = e
                    break

            if not entry:
                QMessageBox.critical(self, "Error", f"Entry '{self.current_txd_name}' not found in IMG")
                return

            # Update entry data
            entry.data = modified_txd_data
            entry.size = len(modified_txd_data)

            # Mark IMG as modified
            self.current_img.modified = True

            if self.main_window:
                # Refresh table
                if hasattr(self.main_window, '_refresh_table'):
                    self.main_window._refresh_table()

                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Updated {self.current_txd_name} in IMG")
                    self.main_window.log_message(f"   Version: 0x{target_version:08X}, Device: 0x{target_device:02X}")
                    self.main_window.log_message(f"   Size: {len(modified_txd_data)} bytes")

            QMessageBox.information(self, "Success",
                f"TXD updated in IMG archive!\n\n{self.current_txd_name}\nVersion: 0x{target_version:08X}")

            # Clear modified state
            if hasattr(self, 'save_txd_btn'):
                self.save_txd_btn.setEnabled(False)
                self.save_txd_btn.setStyleSheet("")
            title = self.windowTitle().replace("*", "")
            self.setWindowTitle(title)

            # Clean up
            if hasattr(self, '_save_target_version'):
                delattr(self, '_save_target_version')
            if hasattr(self, '_save_target_device'):
                delattr(self, '_save_target_device')

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to IMG:\n\n{str(e)}")


    def _save_as_txd_file_with_progress(self): #vers 1
        """Save standalone TXD with progress indicator"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QApplication
        from PyQt6.QtCore import Qt
        import os

        # Determine default filename
        if self.current_txd_name:
            default_name = self.current_txd_name
        else:
            default_name = "untitled.txd"

        # Determine initial directory based on setting
        if self.save_to_source_location:
            if hasattr(self, 'current_txd_path') and self.current_txd_path:
                initial_path = self.current_txd_path
            elif hasattr(self, 'current_img') and self.current_img and hasattr(self.current_img, 'file_path'):
                img_dir = os.path.dirname(self.current_img.file_path)
                initial_path = os.path.join(img_dir, default_name)
            elif hasattr(self, 'last_save_directory') and self.last_save_directory:
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                initial_path = default_name
        else:
            if hasattr(self, 'last_save_directory') and self.last_save_directory:
                initial_path = os.path.join(self.last_save_directory, default_name)
            else:
                initial_path = default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save TXD File",
            initial_path,
            "TXD Files (*.txd);;All Files (*)"
        )

        if not file_path:
            return False

        # Create progress dialog
        total_textures = len(self.texture_list)
        total_steps = total_textures * 3 + 2
        current_step = [0]  # Use list to allow modification in nested function

        progress = QProgressDialog("Saving TXD...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Saving TXD File")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        def update_progress(message):
            current_step[0] += 1
            progress.setValue(int((current_step[0] / total_steps) * 100))
            progress.setLabelText(message)
            QApplication.processEvents()
            if progress.wasCanceled():
                raise InterruptedError("Save cancelled by user")

        try:
            update_progress("📋 Building TXD structure...")

            # Rebuild with progress
            modified_txd_data = self._rebuild_txd_data_with_texture_progress(update_progress)

            if not modified_txd_data:
                progress.close()
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return False

            update_progress("💾 Writing to file...")

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(modified_txd_data)

            # Store paths
            self.current_txd_path = file_path
            self.current_txd_name = os.path.basename(file_path)
            if hasattr(self, 'last_save_directory'):
                self.last_save_directory = os.path.dirname(file_path)

            progress.setValue(100)
            progress.setLabelText("✅ Save complete!")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"✅ Saved TXD file: {file_path} ({len(modified_txd_data)} bytes)"
                )

            # Clear modified state
            self.save_txd_btn.setEnabled(False)
            self.save_txd_btn.setStyleSheet("")
            title = self.windowTitle().replace("*", "")
            self.setWindowTitle(title)

            progress.close()
            QMessageBox.information(self, "Success", f"TXD saved successfully!\n\n{file_path}")
            return True

        except InterruptedError:
            progress.close()
            QMessageBox.information(self, "Cancelled", "Save cancelled by user")
            return False
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Failed to save TXD:\n\n{str(e)}")
            return False


    def _rebuild_txd_data_with_texture_progress(self, update_progress): #vers 1
        """Rebuild TXD data with per-texture progress updates"""
        try:
            if not self.texture_list:
                return None

            # Try to use serializer
            try:
                from methods.txd_serializer import TXDSerializer
            except ImportError:
                from depends.txd_serializer import TXDSerializer

            serializer = TXDSerializer()

            # Build each texture with progress
            texture_sections = []
            for i, texture in enumerate(self.texture_list):
                texture_name = texture.get('name', f'texture_{i}')

                # Update for mipmaps
                num_mipmaps = len(texture.get('mipmap_levels', []))
                if num_mipmaps > 0:
                    update_progress(f"🗺️  {texture_name}: {num_mipmaps} mipmaps")

                # Update for bumpmap
                if texture.get('has_bumpmap'):
                    type_names = ['Height', 'Normal', 'Both']
                    bumpmap_type = texture.get('bumpmap_type', 0)
                    update_progress(f"📐 {texture_name}: {type_names[bumpmap_type]} bumpmap")

                # Update for reflection
                if texture.get('has_reflection'):
                    update_progress(f"🌈 {texture_name}: Reflection maps")

                # Build texture section
                tex_data = serializer._build_texture_native(texture)
                texture_sections.append(tex_data)

            # Build final TXD
            update_progress("📦 Finalizing TXD structure...")

            # Use the serializer's method to build dictionary
            result = serializer._build_texture_dictionary_from_sections(
                texture_sections,
                len(self.texture_list)
            )

            return result

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuild error: {str(e)}")
            return None


    def _save_txd_with_progress(self): #vers 1
        """Save TXD with progress indicator"""
        from PyQt6.QtWidgets import QMessageBox

        if not self.current_img or not self.current_txd_name:
            QMessageBox.warning(self, "No TXD", "No TXD file is currently loaded")
            return

        if not self.texture_list:
            QMessageBox.warning(self, "Empty TXD", "No textures to save")
            return

        # Create progress dialog
        progress = QProgressDialog(
            "Saving TXD...",
            "Cancel",
            0,
            100,
            self
        )
        progress.setWindowTitle("Saving TXD")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(True)
        progress.setAutoReset(True)

        try:
            # Step 1: Calculate total work
            total_textures = len(self.texture_list)
            total_steps = total_textures * 4 + 3  # Per texture: mipmaps, bumpmap, reflection, compression + header/footer/write
            current_step = 0

            def update_progress(message, step_increment=1):
                nonlocal current_step
                current_step += step_increment
                progress.setValue(int((current_step / total_steps) * 100))
                progress.setLabelText(message)
                QApplication.processEvents()
                if progress.wasCanceled():
                    raise InterruptedError("Save cancelled by user")

            # Step 2: Build TXD header
            update_progress("📋 Building TXD header...")
            modified_txd_data = self._rebuild_txd_data_with_progress(update_progress)

            if not modified_txd_data:
                progress.close()
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return False

            # Step 3: Update IMG
            update_progress("💾 Writing to IMG archive...")
            success = self._update_img_with_txd(modified_txd_data)

            if success:
                progress.setValue(100)
                progress.setLabelText("✅ Save complete!")

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(
                        f"✅ Saved TXD: {self.current_txd_name} "
                        f"({len(modified_txd_data)} bytes, {total_textures} textures)"
                    )

                # Clear modified state
                self.save_txd_btn.setEnabled(False)
                self.save_txd_btn.setStyleSheet("")
                title = self.windowTitle().replace("*", "")
                self.setWindowTitle(title)

                progress.close()
                return True
            else:
                progress.close()
                QMessageBox.critical(self, "Error", "Failed to save TXD to IMG")
                return False

        except InterruptedError as e:
            progress.close()
            QMessageBox.information(self, "Cancelled", str(e))
            return False
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Save failed: {str(e)}")
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Save error: {str(e)}")
            return False


    def _rebuild_txd_data(self): #vers 4
        """Rebuild TXD data - DEBUG VERSION"""
        print("DEBUG: _rebuild_txd_data() called")

        try:
            if not self.current_txd_data:
                print("DEBUG: WARNING - current_txd_data is None, creating new TXD")
                # If no original data, we need to create from scratch
                # This is normal for new TXDs
            else:
                print(f"DEBUG: Have original TXD data: {len(self.current_txd_data)} bytes")

            if not self.texture_list:
                print("DEBUG: ERROR - texture_list is empty in _rebuild_txd_data!")
                return None

            print(f"DEBUG: Rebuilding with {len(self.texture_list)} textures")

            # Try to use serializer
            print("DEBUG: Attempting to use serializer...")

            try:
                from methods.txd_serializer import serialize_txd_file
                print("DEBUG: Using methods/txd_serializer")
            except ImportError:
                print("DEBUG: methods/txd_serializer not found, trying depends/")
                try:
                    from depends.txd_serializer import serialize_txd_file
                    print("DEBUG: Using depends/txd_serializer")
                except ImportError:
                    print("DEBUG: ERROR - No serializer found!")
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("ERROR: txd_serializer not found!")
                    return None

            # Get version info
            target_version = self.txd_version_id if self.txd_version_id else 0x1803FFFF
            target_device = self.txd_device_id if self.txd_device_id else 0x08

            print(f"DEBUG: Target version: 0x{target_version:08X}, device: 0x{target_device:02X}")

            # Serialize
            print("DEBUG: Calling serialize_txd_file()...")
            result = serialize_txd_file(self.texture_list, target_version, target_device)

            if result:
                print(f"DEBUG: Serializer returned {len(result)} bytes")

                # Verify result has TXD header
                if len(result) >= 12:
                    import struct
                    section_type, section_size, version = struct.unpack('<III', result[:12])
                    print(f"DEBUG: TXD header - type: 0x{section_type:02X}, size: {section_size}, version: 0x{version:08X}")

                    if section_type != 0x16:
                        print(f"DEBUG: WARNING - Expected section type 0x16, got 0x{section_type:02X}")
                else:
                    print("DEBUG: WARNING - Result too small to have valid header")

                return result
            else:
                print("DEBUG: ERROR - Serializer returned None!")
                return None

        except Exception as e:
            print(f"DEBUG: EXCEPTION in _rebuild_txd_data: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuild error: {str(e)}")
            return None


    def _build_texture_dictionary_manual(self, texture_sections, texture_count): #vers 1
        """Manual TXD dictionary builder for serializer - add to TXDSerializer class"""
        import struct

        # Calculate struct size
        struct_size = 4  # texture count (u32)
        struct_data = struct.pack('<I', texture_count)

        # Build complete dictionary
        result = bytearray()

        # Texture Dictionary header
        total_size = 12 + struct_size + 12  # struct section header + data + extension
        for tex_section in texture_sections:
            total_size += len(tex_section)

        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_DICTIONARY,
            total_size - 12,
            self.RW_VERSION
        ))

        # Struct section (texture count)
        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            struct_size,
            self.RW_VERSION
        ))
        result.extend(struct_data)

        # Texture sections
        for tex_section in texture_sections:
            result.extend(tex_section)

        # Extension section (empty)
        result.extend(self._write_section_header(
            self.SECTION_EXTENSION,
            0,
            self.RW_VERSION
        ))

        return result


    def _save_to_img(self): #vers 1
        """Save TXD back to IMG archive"""
        if not self.current_txd_name:
            QMessageBox.warning(self, "No TXD", "No TXD file loaded from IMG")
            return

        try:
            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Update entry in IMG
            if hasattr(self.current_img, 'replace_entry'):
                self.current_img.replace_entry(self.current_txd_name, modified_txd_data)

                # Mark IMG as modified in main window
                if self.main_window and hasattr(self.main_window, '_mark_as_modified'):
                    self.main_window._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Saved TXD to IMG: {self.current_txd_name}")

                QMessageBox.information(self, "Success",
                    f"TXD saved to IMG archive\n\n"
                    f"Remember to save the IMG file to write changes to disk!")

                # Clear modified state
                self.save_txd_btn.setEnabled(False)
                self.save_txd_btn.setStyleSheet("")
                title = self.windowTitle().replace("*", "")
                self.setWindowTitle(title)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to IMG: {str(e)}")


    def _get_target_version(self): #vers 1
        """Get target RenderWare version based on export settings"""
        from methods.txd_versions import get_recommended_version_for_game

        # Map game setting to game name
        game_map = {
            "gta3": "GTA III",
            "vc": "Vice City",
            "sa": "San Andreas",
            "manhunt": "Manhunt"
        }

        # Map platform setting to platform name
        platform_map = {
            "pc": "PC",
            "xbox": "Xbox",
            "ps2": "PS2",
            "android": "Android"
        }

        game = game_map.get(self.export_target_game, "San Andreas")
        platform = platform_map.get(self.export_target_platform, "PC")

        return get_recommended_version_for_game(game, platform)


    def _save_as_txd_file(self): #vers 3
        """Save as standalone TXD file - with correct directory"""
        import os
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        # Determine default path
        if self.current_txd_name:
            default_name = self.current_txd_name
        else:
            default_name = "untitled.txd"

        # Get the directory from the original file path if available
        initial_path = default_name
        if hasattr(self, 'current_txd_path') and self.current_txd_path:
            # Use the original file's directory
            initial_path = self.current_txd_path
        elif hasattr(self.current_img, 'file_path') and self.current_img.file_path:
            # Use IMG file's directory
            img_dir = os.path.dirname(self.current_img.file_path)
            initial_path = os.path.join(img_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save TXD File",
            initial_path,  # Use full path instead of just filename
            "TXD Files (*.txd);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(modified_txd_data)

            # Store the path for next time
            self.current_txd_path = file_path
            self.current_txd_name = os.path.basename(file_path)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Saved TXD file: {file_path}")

            QMessageBox.information(self, "Success", f"TXD saved successfully!\n\n{file_path}")

            # Clear modified state
            self.save_txd_btn.setEnabled(False)
            self.save_txd_btn.setStyleSheet("")
            title = self.windowTitle().replace("*", "")
            self.setWindowTitle(title)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD:\n\n{str(e)}")


    def _create_new_txd_data(self): #vers 2
        """Create new TXD structure from scratch"""
        import struct

        try:
            # Basic RenderWare TXD header
            # Type, Size, Version
            header = struct.pack('<III', 0x16, 0, 0x1803FFFF)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"   Created basic TXD header: {len(header)} bytes")

            return header

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"   ❌ Create TXD error: {str(e)}")
            return None


    def _update_table_display(self): #vers 2
        """Update the middle panel table display after edits"""
        if not self.selected_texture:
            return

        row = self.texture_table.currentRow()
        if row < 0 or row >= len(self.texture_list):
            return

        tex = self.selected_texture

        # Rebuild details text with compression status
        details = f"Name: {tex['name']}\n"

        # Add alpha name if texture has alpha
        if tex.get('has_alpha', False):
            alpha_name = tex.get('alpha_name', tex['name'] + 'a')
            details += f"Alpha: {alpha_name}\n"

        if tex['width'] > 0:
            details += f"Size: {tex['width']}x{tex['height']}\n"

        # Show format with compression status
        fmt = tex['format']
        if 'DXT' in fmt:
            details += f"Format: {fmt} (Compressed)\n"
        else:
            details += f"Format: {fmt} (Uncompressed)\n"

        details += f"Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}"

        # Update the table item
        details_item = self.texture_table.item(row, 1)
        if details_item:
            details_item.setText(details)


    def _parse_single_texture(self, txd_data, offset, index): #vers 4
        """
        Parse single texture from TXD with bumpmap and reflection support
        """
        import struct

        tex = {
            'name': f'texture_{index}',
            'width': 0,
            'height': 0,
            'depth': 32,
            'format': 'DXT1',
            'has_alpha': False,
            'mipmaps': 1,
            'rgba_data': b'',
            'mipmap_levels': [],
            'bumpmap_data': b'',
            'bumpmap_type': 0,
            'has_bumpmap': False,
            'reflection_map': b'',
            'fresnel_map': b'',
            'has_reflection': False,
            'raster_format_flags': 0
        }

        try:
            # TextureNative structure
            parent_type, parent_size, parent_version = struct.unpack('<III', txd_data[offset:offset+12])

            if parent_type != 0x15:
                return tex

            # Struct section
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', txd_data[struct_offset:struct_offset+12])

            if struct_type != 0x01:
                return tex

            pos = struct_offset + 12

            # Read 88-byte header
            platform_id, filter_mode, uv_addressing = struct.unpack('<I2B', txd_data[pos:pos+6])[:3]
            pos += 8  # Skip padding

            name_bytes = txd_data[pos:pos+32]
            tex['name'] = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore') or f'texture_{index}'
            pos += 32

            mask_bytes = txd_data[pos:pos+32]
            alpha_name = mask_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
            if alpha_name:
                tex['alpha_name'] = alpha_name
                tex['has_alpha'] = True
            pos += 32

            raster_format_flags, d3d_format, width, height, depth, num_levels, raster_type = struct.unpack('<IIHHBBB', txd_data[pos:pos+15])
            tex['width'] = width
            tex['height'] = height
            tex['depth'] = depth
            tex['mipmaps'] = num_levels
            tex['raster_format_flags'] = raster_format_flags  # Store format flags

            # NEW: Check for bumpmap flag (bit 0x10)
            if raster_format_flags & 0x10:
                tex['has_bumpmap'] = True

            pos += 15

            platform_prop = struct.unpack('<B', txd_data[pos:pos+1])[0]
            pos += 1

            # Format detection
            if platform_id == 8:  # D3D8
                if platform_prop == 1:
                    tex['format'] = 'DXT1'
                elif platform_prop == 3:
                    tex['format'] = 'DXT3'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif platform_prop == 5:
                    tex['format'] = 'DXT5'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 21:  # ARGB8888
                    tex['format'] = 'ARGB8888'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 20:  # RGB888
                    tex['format'] = 'RGB888'

            # Read total data size
            data_size = struct.unpack('<I', txd_data[pos:pos+4])[0]
            pos += 4

            # Calculate individual mipmap sizes
            mipmap_sizes = []
            w, h = width, height
            for i in range(num_levels):
                if 'DXT1' in tex['format']:
                    size = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 8
                elif 'DXT' in tex['format']:
                    size = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 16
                elif 'ARGB8888' in tex['format']:
                    size = w * h * 4
                elif 'RGB888' in tex['format']:
                    size = w * h * 3
                else:
                    size = w * h * 2

                mipmap_sizes.append(size)
                w = max(1, w // 2)
                h = max(1, h // 2)

            # Read mipmap data
            for level, size in enumerate(mipmap_sizes):
                if pos + size > len(txd_data):
                    break

                level_data = txd_data[pos:pos+size]
                pos += size

                # Decompress if needed
                if 'DXT' in tex['format']:
                    rgba_data = self._decompress_texture(
                        level_data,
                        max(1, width >> level),
                        max(1, height >> level),
                        tex['format']
                    )
                else:
                    rgba_data = level_data

                mipmap_level = {
                    'level': level,
                    'width': max(1, width >> level),
                    'height': max(1, height >> level),
                    'rgba_data': rgba_data,
                    'compressed_data': level_data if 'DXT' in tex['format'] else None,
                    'compressed_size': len(level_data)
                }
                tex['mipmap_levels'].append(mipmap_level)

                # Store main texture data
                if level == 0:
                    tex['rgba_data'] = rgba_data

            # NEW: Read bumpmap data (if present)
            if tex['has_bumpmap'] and pos + 5 <= len(txd_data):
                try:
                    # Read bumpmap header
                    bumpmap_size = struct.unpack('<I', txd_data[pos:pos+4])[0]
                    pos += 4

                    bumpmap_type = struct.unpack('<B', txd_data[pos:pos+1])[0]
                    pos += 1

                    # Read bumpmap data
                    if pos + bumpmap_size <= len(txd_data):
                        tex['bumpmap_data'] = txd_data[pos:pos+bumpmap_size]
                        tex['bumpmap_type'] = bumpmap_type
                        pos += bumpmap_size

                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            type_names = ['Height Map', 'Normal Map', 'Both']
                            type_name = type_names[bumpmap_type] if bumpmap_type < 3 else 'Unknown'
                            self.main_window.log_message(
                                f"  📐 Bumpmap: {type_name} ({bumpmap_size} bytes)"
                            )
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"  ⚠️ Bumpmap read error: {str(e)}")

            # NEW: Read reflection map data (if present and space available)
            # Check if there's more data after mipmaps/bumpmap
            if pos + 8 <= len(txd_data):
                try:
                    # Read reflection map header
                    reflection_size = struct.unpack('<I', txd_data[pos:pos+4])[0]
                    pos += 4

                    # Validate size is reasonable (should be width*height*3 for RGB)
                    expected_reflection_size = width * height * 3
                    if reflection_size == expected_reflection_size and pos + reflection_size <= len(txd_data):
                        tex['reflection_map'] = txd_data[pos:pos+reflection_size]
                        tex['has_reflection'] = True
                        pos += reflection_size

                        # Read Fresnel map
                        if pos + 4 <= len(txd_data):
                            fresnel_size = struct.unpack('<I', txd_data[pos:pos+4])[0]
                            pos += 4

                            # Validate Fresnel size (should be width*height for grayscale)
                            expected_fresnel_size = width * height
                            if fresnel_size == expected_fresnel_size and pos + fresnel_size <= len(txd_data):
                                tex['fresnel_map'] = txd_data[pos:pos+fresnel_size]
                                pos += fresnel_size

                                if self.main_window and hasattr(self.main_window, 'log_message'):
                                    self.main_window.log_message(
                                        f"  🌈 Reflection maps: "
                                        f"Vector ({reflection_size}B) + Fresnel ({fresnel_size}B)"
                                    )
                except Exception as e:
                    # Silently ignore reflection read errors (optional data)
                    pass

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Texture parse error: {str(e)}")

        return tex


    def _decompress_texture(self, compressed_data, width, height, format_str): #vers 2
        """
        Decompress DXT texture data to RGBA

        Args:
            compressed_data: Compressed texture bytes
            width: Texture width
            height: Texture height
            format_str: Format string (DXT1, DXT3, DXT5)

        Returns:
            bytes: Decompressed RGBA data
        """
        if 'DXT1' in format_str:
            return self._decompress_dxt1(compressed_data, width, height)
        elif 'DXT3' in format_str:
            return self._decompress_dxt3(compressed_data, width, height)
        elif 'DXT5' in format_str:
            return self._decompress_dxt5(compressed_data, width, height)
        else:
            return compressed_data


    def _decompress_dxt1(self, dxt_data, width, height): #vers 1
        """DXT1 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 8
                    if block_offset + 8 > len(dxt_data):
                        break

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset:block_offset+4])
                    indices = struct.unpack('<I', dxt_data[block_offset+4:block_offset+8])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b, 255))

                    if c0 > c1:
                        colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3, 255))
                        colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3, 255))
                    else:
                        colors.append(((colors[0][0]+colors[1][0])//2, (colors[0][1]+colors[1][1])//2, (colors[0][2]+colors[1][2])//2, 255))
                        colors.append((0, 0, 0, 0))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                index = (indices >> ((py*4+px)*2)) & 0x03
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+4] = colors[index]
            return bytes(rgba)
        except:
            return None


    def _decompress_dxt3(self, dxt_data, width, height): #vers 1
        """DXT3 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    alpha_data = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0]
                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = py*4 + px
                                alpha = ((alpha_data >> (alpha_index*4)) & 0x0F) * 17
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha
            return bytes(rgba)
        except:
            return None


    def _decompress_dxt5(self, dxt_data, width, height): #vers 1
        """DXT5 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    a0 = dxt_data[block_offset]
                    a1 = dxt_data[block_offset + 1]
                    alpha_indices = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0] >> 16
                    alpha_palette = [a0, a1]
                    if a0 > a1:
                        for i in range(1, 7):
                            alpha_palette.append(((7-i)*a0+i*a1)//7)
                    else:
                        for i in range(1, 5):
                            alpha_palette.append(((5-i)*a0+i*a1)//5)
                        alpha_palette.extend([0, 255])

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = (alpha_indices >> ((py*4+px)*3)) & 0x07
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha_palette[alpha_index]
            return bytes(rgba)
        except:
            return None


    def _convert_rgba_to_bgra(self, rgba_data): #vers 1
        """Convert RGBA to BGRA byte order for RenderWare"""
        bgra_data = bytearray(len(rgba_data))
        for i in range(0, len(rgba_data), 4):
            bgra_data[i] = rgba_data[i+2]    # B
            bgra_data[i+1] = rgba_data[i+1]  # G
            bgra_data[i+2] = rgba_data[i]    # R
            bgra_data[i+3] = rgba_data[i+3]  # A
        return bytes(bgra_data)


    def _convert_bgra_to_rgba(self, bgra_data): #vers 1
        """Convert BGRA to RGBA byte order from RenderWare"""
        rgba_data = bytearray(len(bgra_data))
        for i in range(0, len(bgra_data), 4):
            rgba_data[i] = bgra_data[i+2]    # R
            rgba_data[i+1] = bgra_data[i+1]  # G
            rgba_data[i+2] = bgra_data[i]    # B
            rgba_data[i+3] = bgra_data[i+3]  # A
        return bytes(rgba_data)


    # Update _decompress_uncompressed method:
    def _decompress_uncompressed(self, data, width, height, format_type): #vers 2
        """Decompress uncompressed formats - FIXED: Proper BGRA handling"""
        try:
            import struct
            rgba = bytearray(width * height * 4)

            if 'ARGB8888' in format_type or 'ARGB32' in format_type:
                # RenderWare stores as BGRA, not RGBA
                for i in range(width * height):
                    if i*4+4 <= len(data):
                        b, g, r, a = struct.unpack('BBBB', data[i*4:i*4+4])
                        rgba[i*4:i*4+4] = [r, g, b, a]  # Convert to RGBA

            elif 'RGB888' in format_type:
                # RGB888 is stored as BGR
                for i in range(width * height):
                    if i*3+3 <= len(data):
                        b, g, r = struct.unpack('BBB', data[i*3:i*3+3])
                        rgba[i*4:i*4+4] = [r, g, b, 255]

            elif 'RGB565' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        r = ((pixel >> 11) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x3F) << 2
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r, g, b, 255]

            elif 'ARGB1555' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = 255 if (pixel & 0x8000) else 0
                        r = ((pixel >> 10) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x1F) << 3
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r, g, b, a]

            elif 'ARGB4444' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = ((pixel >> 12) & 0x0F) * 17
                        r = ((pixel >> 8) & 0x0F) * 17
                        g = ((pixel >> 4) & 0x0F) * 17
                        b = (pixel & 0x0F) * 17
                        rgba[i*4:i*4+4] = [r, g, b, a]

            elif 'LUM8' in format_type or 'L8' in format_type:
                for i in range(width * height):
                    if i < len(data):
                        lum = data[i]
                        rgba[i*4:i*4+4] = [lum, lum, lum, 255]

            return bytes(rgba)
        except Exception as e:
            return None


    def _create_thumbnail(self, rgba_data, width, height): #vers 1
        """Create thumbnail from RGBA data"""
        try:
            if not rgba_data or width <= 0 or height <= 0:
                return None

            image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
            if image.isNull():
                return None

            pixmap = QPixmap.fromImage(image)
            return pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except:
            return None


    def _convert_texture(self): #vers 3
        """Convert texture format with GTA III 8-bit support"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Convert Texture Format")
        dialog.setModal(True)
        dialog.resize(400, 350)

        layout = QVBoxLayout(dialog)

        # Current format
        current_format = self.selected_texture.get('format', 'Unknown')
        current_depth = self.selected_texture.get('depth', 32)
        current_label = QLabel(f"Current: {current_format} ({current_depth}bit)")
        current_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 10px;")
        layout.addWidget(current_label)

        # Format selection
        format_group = QGroupBox("Convert To")
        format_layout = QVBoxLayout(format_group)

        format_combo = QComboBox()
        format_combo.addItems([
            "DXT1 (No Alpha, 6:1 compression) - 32bit",
            "DXT3 (Sharp Alpha, 4:1 compression) - 32bit",
            "DXT5 (Smooth Alpha, 4:1 compression) - 32bit",
            "ARGB8888 (32-bit Uncompressed)",
            "RGB888 (24-bit No Alpha)",
            "ARGB1555 (16-bit with Alpha)",
            "RGB565 (16-bit No Alpha)",
            "PAL8 (8-bit Indexed - GTA III)"
        ])
        format_layout.addWidget(format_combo)

        # Info label
        info_label = QLabel()
        info_label.setStyleSheet("color: #ff9800; font-size: 10px; padding: 5px;")
        info_label.setWordWrap(True)

        def update_info(index):
            if index == 7:  # PAL8
                info_label.setText("8-bit indexed format (GTA III). Limited to 256 colors with palette.")
            else:
                info_label.setText("Note: Converting between compressed formats may result in quality loss.")

        format_combo.currentIndexChanged.connect(update_info)
        update_info(0)

        format_layout.addWidget(info_label)
        layout.addWidget(format_group)

        # Size estimate
        width = self.selected_texture.get('width', 0)
        height = self.selected_texture.get('height', 0)

        size_group = QGroupBox("Size Estimate")
        size_layout = QVBoxLayout(size_group)

        size_label = QLabel(f"Texture: {width}x{height}")
        size_layout.addWidget(size_label)

        def update_size_estimate(index):
            format_map = [
                ('DXT1', 32), ('DXT3', 32), ('DXT5', 32),
                ('ARGB8888', 32), ('RGB888', 24),
                ('ARGB1555', 16), ('RGB565', 16),
                ('PAL8', 8)
            ]
            selected_format, bit_depth = format_map[index]

            # Calculate estimated size
            pixel_count = width * height
            if 'DXT1' in selected_format:
                estimated = pixel_count // 2
            elif 'DXT' in selected_format:
                estimated = pixel_count
            elif 'PAL8' in selected_format:
                estimated = pixel_count + 1024  # 256 color palette (256 * 4 bytes)
            elif 'ARGB8888' in selected_format:
                estimated = pixel_count * 4
            elif 'RGB888' in selected_format:
                estimated = pixel_count * 3
            else:  # 16-bit formats
                estimated = pixel_count * 2

            size_kb = estimated / 1024
            estimate_label.setText(f"Estimated: {size_kb:.1f} KB ({bit_depth}bit)")

        estimate_label = QLabel("Select format above")
        size_layout.addWidget(estimate_label)

        format_combo.currentIndexChanged.connect(update_size_estimate)
        update_size_estimate(0)

        layout.addWidget(size_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_convert():
            format_map = [
                ('DXT1', 32), ('DXT3', 32), ('DXT5', 32),
                ('ARGB8888', 32), ('RGB888', 24),
                ('ARGB1555', 16), ('RGB565', 16),
                ('PAL8', 8)
            ]
            selected_format, bit_depth = format_map[format_combo.currentIndex()]

            # Save undo state
            self._save_undo_state(f"Convert: {current_format} → {selected_format}")

            # Update texture format and bit depth
            self.selected_texture['format'] = selected_format
            self.selected_texture['depth'] = bit_depth

            # Mark as modified
            self._mark_as_modified()
            self._update_texture_info(self.selected_texture)
            self._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Converted: {current_format} → {selected_format} ({bit_depth}bit)")

            dialog.accept()

            if selected_format == 'PAL8':
                QMessageBox.information(self, "Format Converted",
                    f"Texture converted to 8-bit indexed format\n\n"
                    "Note: Color palette will be generated when saving.\n"
                    "Best for GTA III textures with limited colors.")
            else:
                QMessageBox.information(self, "Format Converted",
                    f"Texture format: {selected_format} ({bit_depth}bit)\n\n"
                    "Compression will be applied when saving TXD file.")

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(do_convert)
        button_layout.addWidget(convert_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    #Left side vertical panel
    def _create_transform_panel(self): #vers 11
        """Create transform panel with variable width - no headers"""
        self.transform_panel = QFrame()
        self.transform_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.transform_panel.setMinimumWidth(30)
        self.transform_panel.setMaximumWidth(200)
        if self.button_display_mode == 'icons':
            self.transform_panel.setMaximumWidth(40)
            self.transform_panel.setMinimumWidth(40)
            layout.addSpacing(5)

        layout = QVBoxLayout(self.transform_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)


        # Flip Vertical
        self.flip_vert_btn = QPushButton()
        self.flip_vert_btn.setFont(self.button_font)
        self.flip_vert_btn.setIcon(self._create_flip_vert_icon())
        self.flip_vert_btn.setText("Flip Vertical")
        self.flip_vert_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.flip_vert_btn.setFixedSize(40, 40)
        self.flip_vert_btn.clicked.connect(self._flip_vertical)
        self.flip_vert_btn.setEnabled(False)
        self.flip_vert_btn.setToolTip("Flip texture vertically")
        layout.addWidget(self.flip_vert_btn)

        # Flip Horizontal
        self.flip_horz_btn = QPushButton()
        self.flip_horz_btn.setFont(self.button_font)
        self.flip_horz_btn.setIcon(self._create_flip_horz_icon())
        self.flip_horz_btn.setText("Flip Horizontal")
        self.flip_horz_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.flip_horz_btn.setFixedSize(40, 40)
        self.flip_horz_btn.clicked.connect(self._flip_horizontal)
        self.flip_horz_btn.setEnabled(False)
        self.flip_horz_btn.setToolTip("Flip texture horizontally")
        layout.addWidget(self.flip_horz_btn)

        layout.addSpacing(5)

        # Rotate Clockwise
        self.rotate_cw_btn = QPushButton()
        self.rotate_cw_btn.setFont(self.button_font)
        self.rotate_cw_btn.setIcon(self._create_rotate_cw_icon())
        self.rotate_cw_btn.setText("Rotate 90° CW")
        self.rotate_cw_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.rotate_cw_btn.setFixedSize(40, 40)
        self.rotate_cw_btn.clicked.connect(self._rotate_clockwise)
        self.rotate_cw_btn.setEnabled(False)
        self.rotate_cw_btn.setToolTip("Rotate 90 degrees clockwise")
        layout.addWidget(self.rotate_cw_btn)

        # Rotate Counter-Clockwise
        self.rotate_ccw_btn = QPushButton()
        self.rotate_ccw_btn.setFont(self.button_font)
        self.rotate_ccw_btn.setIcon(self._create_rotate_ccw_icon())
        self.rotate_ccw_btn.setText("Rotate 90° CCW")
        self.rotate_ccw_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.rotate_ccw_btn.setFixedSize(40, 40)
        self.rotate_ccw_btn.clicked.connect(self._rotate_counterclockwise)
        self.rotate_ccw_btn.setEnabled(False)
        self.rotate_ccw_btn.setToolTip("Rotate 90 degrees counter-clockwise")
        layout.addWidget(self.rotate_ccw_btn)

        layout.addSpacing(5)

        # Copy
        self.copy_btn = QPushButton()
        self.copy_btn.setFont(self.button_font)
        self.copy_btn.setIcon(self._create_copy_icon())
        self.copy_btn.setText("Copy")
        self.copy_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.copy_btn.setFixedSize(40, 40)
        self.copy_btn.clicked.connect(self._copy_texture)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setToolTip("Copy texture to clipboard")
        layout.addWidget(self.copy_btn)

        # Paste
        self.paste_btn = QPushButton()
        self.paste_btn.setFont(self.button_font)
        self.paste_btn.setIcon(self._create_paste_icon())
        self.paste_btn.setText("Paste")
        self.paste_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.paste_btn.setFixedSize(40, 40)
        self.paste_btn.clicked.connect(self._paste_texture)
        self.paste_btn.setEnabled(False)
        self.paste_btn.setToolTip("Paste texture from clipboard")
        layout.addWidget(self.paste_btn)

        self.paint_btn = QPushButton()
        self.paint_btn.setFont(self.button_font)
        self.paint_btn.setIcon(self._create_paint_icon())
        self.paint_btn.setText("Paint")
        self.paint_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.paint_btn.setFixedSize(40, 40)
        self.paint_btn.clicked.connect(self._open_paint_editor)
        self.paint_btn.setEnabled(False)
        self.paint_btn.setToolTip("Paint on texture")
        layout.addWidget(self.paint_btn)

        layout.addSpacing(5)

        # Check TXD vs DFF
        self.check_dff_btn = QPushButton()
        self.check_dff_btn.setFont(self.button_font)
        self.check_dff_btn.setIcon(self._create_check_icon())
        self.check_dff_btn.setText("Check DFF")
        self.check_dff_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.check_dff_btn.setFixedSize(40, 40)
        self.check_dff_btn.clicked.connect(self._check_txd_vs_dff)
        self.check_dff_btn.setToolTip("Verify textures against DFF model file")
        layout.addWidget(self.check_dff_btn)

        self.build_from_dff_btn = QPushButton()
        self.build_from_dff_btn.setFont(self.button_font)
        self.build_from_dff_btn.setIcon(self._create_build_icon())
        self.build_from_dff_btn.setText("Build TXD via")
        self.build_from_dff_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.build_from_dff_btn.setFixedSize(40, 40)
        self.build_from_dff_btn.clicked.connect(self._build_txd_from_dff)
        self.build_from_dff_btn.setToolTip("Create TXD structure from DFF material names")
        layout.addWidget(self.build_from_dff_btn)

        # Create Texture
        self.create_texture_btn = QPushButton()
        self.create_texture_btn.setFont(self.button_font)
        self.create_texture_btn.setIcon(self._create_create_icon())
        self.create_texture_btn.setText("Create")
        self.create_texture_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.create_texture_btn.setFixedSize(40, 40)
        self.create_texture_btn.clicked.connect(self._create_new_texture_entry)
        self.create_texture_btn.setToolTip("Create new blank texture")
        layout.addWidget(self.create_texture_btn)

        # Delete Texture
        self.delete_texture_btn = QPushButton()
        self.delete_texture_btn.setFont(self.button_font)
        self.delete_texture_btn.setIcon(self._create_delete_icon())
        self.delete_texture_btn.setText("Delete")
        self.delete_texture_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.delete_texture_btn.setFixedSize(40, 40)
        self.delete_texture_btn.clicked.connect(self._delete_texture)
        self.delete_texture_btn.setEnabled(False)
        self.delete_texture_btn.setToolTip("Remove selected texture")
        layout.addWidget(self.delete_texture_btn)

        # Duplicate Texture
        self.duplicate_texture_btn = QPushButton()
        self.duplicate_texture_btn.setFont(self.button_font)
        self.duplicate_texture_btn.setIcon(self._create_duplicate_icon())
        self.duplicate_texture_btn.setText("Duplicate")
        self.duplicate_texture_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.duplicate_texture_btn.setFixedSize(40, 40)
        self.duplicate_texture_btn.clicked.connect(self._duplicate_texture)
        self.duplicate_texture_btn.setEnabled(False)
        self.duplicate_texture_btn.setToolTip("Clone selected texture")
        layout.addWidget(self.duplicate_texture_btn)

        layout.addSpacing(5)

        # Filters
        self.filters_btn = QPushButton()
        self.filters_btn.setFont(self.button_font)
        self.filters_btn.setIcon(self._create_filter_icon())
        self.filters_btn.setText("Filters")
        self.filters_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.filters_btn.setFixedSize(40, 40)
        self.filters_btn.clicked.connect(self._open_filters_dialog)
        self.filters_btn.setEnabled(False)
        self.filters_btn.setToolTip("Brightness, Contrast, Saturation")
        layout.addWidget(self.filters_btn)

        layout.addStretch()

        return self.transform_panel


    def _edit_texture(self): #vers 1
        """Edit texture in external editor"""
        if not self.selected_texture:
            return

        QMessageBox.information(self, "Edit Texture",
            "External texture editor coming soon!\n\n"
            "This will allow editing textures in an external image editor.")


    def _open_paint_editor(self): #vers 1
        """Open simple paint editor"""
        if not self.selected_texture:
            return

        QMessageBox.information(self, "Paint Editor",
            "Simple pixel paint editor coming soon!\n\n"
            "Features:\n"
            "- Draw pixels\n"
            "- Color picker\n"
            "- Brush sizes\n"
            "- Undo/Redo")


    def _open_filters_dialog(self): #vers 1
        """Open filters dialog"""
        if not self.selected_texture:
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Image Filters")
        dialog.setModal(True)
        dialog.resize(400, 400)

        layout = QVBoxLayout(dialog)

        # Brightness
        layout.addWidget(QLabel("Brightness:"))
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setMinimum(-100)
        brightness_slider.setMaximum(100)
        brightness_slider.setValue(0)
        layout.addWidget(brightness_slider)

        # Contrast
        layout.addWidget(QLabel("Contrast:"))
        contrast_slider = QSlider(Qt.Orientation.Horizontal)
        contrast_slider.setMinimum(-100)
        contrast_slider.setMaximum(100)
        contrast_slider.setValue(0)
        layout.addWidget(contrast_slider)

        # Saturation
        layout.addWidget(QLabel("Saturation:"))
        saturation_slider = QSlider(Qt.Orientation.Horizontal)
        saturation_slider.setMinimum(-100)
        saturation_slider.setMaximum(100)
        saturation_slider.setValue(0)
        layout.addWidget(saturation_slider)

        # Hue
        layout.addWidget(QLabel("Hue Shift:"))
        hue_slider = QSlider(Qt.Orientation.Horizontal)
        hue_slider.setMinimum(0)
        hue_slider.setMaximum(360)
        hue_slider.setValue(0)
        layout.addWidget(hue_slider)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: QMessageBox.information(
            dialog, "Apply Filters", "Filter application coming soon!"))
        button_layout.addWidget(apply_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: [
            brightness_slider.setValue(0),
            contrast_slider.setValue(0),
            saturation_slider.setValue(0),
            hue_slider.setValue(0)
        ])
        button_layout.addWidget(reset_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _update_texture_info(self, texture): #vers 6
        """Update texture information display"""
        if not texture:
            self.info_name.setText("")
            self.info_alpha_name.setText("")
            self.info_alpha_name.setVisible(False)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(False)
            if hasattr(self, 'preview_widget'):
                self.preview_widget.setText("No texture selected")
            return

        # Set ONLY the name - no extra formatting
        name = texture.get('name', 'Unknown')
        self.info_name.setText(name)

        # Set alpha name if has alpha
        has_alpha = texture.get('has_alpha', False)
        if has_alpha:
            alpha_name = texture.get('alpha_name', name + 'a')
            self.info_alpha_name.setText(alpha_name)
            self.info_alpha_name.setVisible(True)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(True)
        else:
            self.info_alpha_name.setText("")
            self.info_alpha_name.setVisible(False)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(False)

        # Update size info
        width = texture.get('width', 0)
        height = texture.get('height', 0)
        if hasattr(self, 'info_size'):
            self.info_size.setText(f"Size: {width}x{height}")

        # Update format
        fmt = texture.get('format', 'Unknown')
        if hasattr(self, 'format_status_label'):
            self.format_status_label.setText(f"Format: {fmt}")

        # Update bit depth
        depth = texture.get('depth', 32)
        if hasattr(self, 'info_bitdepth'):
            self.info_bitdepth.setText(f"[{depth}bit]")

        # Update mipmap info
        mipmap_levels = texture.get('mipmap_levels', [])
        num_mipmaps = len(mipmap_levels)
        if hasattr(self, 'info_format'):
            if num_mipmaps > 1:
                self.info_format.setText(f"Mipmaps: {num_mipmaps} levels")
            else:
                self.info_format.setText("Mipmaps: None")

        # Bumpmap detection (FIXED - using 'texture' not 'texture_data')
        has_bumpmap = False
        bumpmap_info = "No data"

        # Check if this version supports bumpmaps
        if is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            # Check for bumpmap format bits
            if 'raster_format_flags' in texture:
                flags = texture.get('raster_format_flags', 0)
                if flags & 0x10:  # Bit 4 indicates environment/bumpmap
                    has_bumpmap = True
                    bumpmap_info = "Bumpmap present"

            # Also check for explicit bumpmap data
            if 'bumpmap_data' in texture or texture.get('has_bumpmap', False):
                has_bumpmap = True
                bumpmap_info = "Bumpmap present"
        else:
            bumpmap_info = f"Not supported ({self.txd_game})"

        # Update bumpmap UI
        if hasattr(self, 'bumpmap_label'):
            self.bumpmap_label.setText(bumpmap_info)

        if hasattr(self, 'info_format_b'):
            if has_bumpmap:
                self.info_format_b.setStyleSheet("color: #4CAF50;")  # Green
            else:
                self.info_format_b.setStyleSheet("color: #757575;")  # Gray

        # Update preview with new widget
        rgba_data = texture.get('rgba_data')
        if rgba_data and width > 0 and hasattr(self, 'preview_widget'):
            try:
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    self.preview_widget.set_image(pixmap)
                else:
                    self.preview_widget.setText("Invalid image data")
            except Exception as e:
                self.preview_widget.setText(f"Preview error: {str(e)}")
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Preview error: {str(e)}")
        elif hasattr(self, 'preview_widget'):
            self.preview_widget.setText("No preview available")

    def _view_bumpmap(self): #vers 4
        """Open Bumpmap Manager window - ALWAYS opens manager regardless of bumpmap state"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture")
            return

        # Check version support - show warning but context matters
        if not is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            QMessageBox.warning(self, "Not Supported",
                f"Bumpmaps not supported for {self.txd_game}\n"
                f"Only San Andreas and Manhunt support bumpmaps")
            return

        # Open Bumpmap Manager window (works with or without existing bumpmap)
        manager = BumpmapManagerWindow(self, self.selected_texture, self.main_window)
        manager.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            has_bumpmap = self._has_bumpmap_data(self.selected_texture) if hasattr(self, '_has_bumpmap_data') else False
            status = "with bumpmap" if has_bumpmap else "no bumpmap (can generate/import)"
            self.main_window.log_message(
                f"🗺️ Opened Bumpmap Manager: {self.selected_texture['name']} ({status})"
            )


    def _export_bumpmap(self): #vers 1
        """Export bumpmap as separate image file"""
        if not self.selected_texture:
            return

        try:
            texture_data = self.selected_texture
            texture_name = texture_data.get('name', 'texture')

            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Bumpmap",
                f"{texture_name}_bumpmap.png",
                "PNG Images (*.png);;All Files (*)"
            )

            if not file_path:
                return

            # Extract and save bumpmap
            if 'bumpmap_data' in texture_data:
                bumpmap_image = self._decode_bumpmap(texture_data['bumpmap_data'])

                if bumpmap_image.save(file_path):
                    QMessageBox.information(self, "Success",
                        f"Bumpmap exported to:\n{file_path}")

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"Exported bumpmap: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save bumpmap")
            else:
                QMessageBox.information(self, "No Bumpmap",
                    "No bumpmap data found in texture")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


    def _import_bumpmap(self): #vers 1
        """Import bumpmap from image file"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection",
                "Please select a texture to add bumpmap to")
            return

        # Check if version supports bumpmaps
        if not is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            QMessageBox.warning(self, "Not Supported",
                f"Bumpmaps not supported for {self.txd_game}\n"
                f"Only San Andreas and State of Liberty support bumpmaps")
            return

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Bumpmap",
                "",
                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
            )

            if not file_path:
                return

            # Load bumpmap image
            bumpmap_image = QImage(file_path)

            if bumpmap_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to load bumpmap image")
                return

            # Encode bumpmap data
            bumpmap_data = self._encode_bumpmap(bumpmap_image)

            # Add to texture data
            self.selected_texture['bumpmap_data'] = bumpmap_data
            self.selected_texture['has_bumpmap'] = True

            # Mark as modified
            self._mark_as_modified()

            # Update UI
            self._update_texture_info(self.selected_texture)

            QMessageBox.information(self, "Success",
                "Bumpmap imported successfully")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Imported bumpmap from: {os.path.basename(file_path)}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")


    def _decode_bumpmap(self, bumpmap_data: bytes) -> QImage: #vers 3
        """Decode bumpmap data to QImage - supports all types"""
        try:
            width = self.selected_texture.get('width', 256)
            height = self.selected_texture.get('height', 256)

            expected_gray = width * height
            expected_rgb = width * height * 3

            # Detect format
            if len(bumpmap_data) == expected_rgb:
                # RGB Normal Map
                image = QImage(bytes(bumpmap_data), width, height, width * 3, QImage.Format.Format_RGB888)
                return image

            elif len(bumpmap_data) > expected_gray and bumpmap_data[0] == 2:
                # Combined type (both height + normal)
                # Skip type byte, extract normal map portion
                offset = 1 + expected_gray
                normal_data = bumpmap_data[offset:offset + expected_rgb]
                image = QImage(bytes(normal_data), width, height, width * 3, QImage.Format.Format_RGB888)
                return image

            else:
                # Grayscale Height Map - convert to RGB for display
                rgb_data = bytearray(expected_rgb)
                for i in range(min(expected_gray, len(bumpmap_data))):
                    value = bumpmap_data[i]
                    rgb_data[i*3] = value
                    rgb_data[i*3+1] = value
                    rgb_data[i*3+2] = value

                image = QImage(bytes(rgb_data), width, height, width * 3, QImage.Format.Format_RGB888)
                return image

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Bumpmap decode error: {str(e)}")
            return QImage()


    def _extract_alpha_for_display(self, rgba_data): #vers 1
        """Extract alpha channel as grayscale for display"""
        alpha_display = bytearray()
        for i in range(3, len(rgba_data), 4):
            a = rgba_data[i]
            alpha_display.extend([a, a, a, 255])  # Grayscale with full opacity
        return bytes(alpha_display)


    def _flip_vertical(self): #vers 2
        """Flip texture vertically"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # Flip vertically - swap rows
            flipped = bytearray(len(rgba_data))
            for y in range(height):
                for x in range(width):
                    src_idx = (y * width + x) * 4
                    dst_idx = ((height - 1 - y) * width + x) * 4
                    flipped[dst_idx:dst_idx+4] = rgba_data[src_idx:src_idx+4]

            self._save_undo_state("Flip vertical")
            self.selected_texture['rgba_data'] = bytes(flipped)
            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Flipped texture vertically")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")


    def _flip_horizontal(self): #vers 1
        """Flip texture horizontally"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # Flip horizontally - swap columns
            flipped = bytearray(len(rgba_data))
            for y in range(height):
                for x in range(width):
                    src_idx = (y * width + x) * 4
                    dst_idx = (y * width + (width - 1 - x)) * 4
                    flipped[dst_idx:dst_idx+4] = rgba_data[src_idx:src_idx+4]

            self._save_undo_state("Flip horizontal")
            self.selected_texture['rgba_data'] = bytes(flipped)
            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Flipped texture horizontally")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")


    def _rotate_clockwise(self): #vers 1
        """Rotate texture 90 degrees clockwise"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = self.selected_texture['rgba_data']

            # Use QImage for rotation
            from PyQt6.QtGui import QImage, QTransform
            img = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            transform = QTransform().rotate(90)
            rotated = img.transformed(transform)

            # Get rotated data
            ptr = rotated.bits()
            ptr.setsize(rotated.sizeInBytes())
            rotated_data = bytes(ptr)

            self._save_undo_state("Rotate 90° CW")
            self.selected_texture['rgba_data'] = rotated_data
            self.selected_texture['width'] = rotated.width()
            self.selected_texture['height'] = rotated.height()

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Rotated 90° CW: now {rotated.width()}x{rotated.height()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")


    def _rotate_counterclockwise(self): #vers 1
        """Rotate texture 90 degrees counter-clockwise"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = self.selected_texture['rgba_data']

            # Use QImage for rotation
            from PyQt6.QtGui import QImage, QTransform
            img = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            transform = QTransform().rotate(-90)
            rotated = img.transformed(transform)

            # Get rotated data
            ptr = rotated.bits()
            ptr.setsize(rotated.sizeInBytes())
            rotated_data = bytes(ptr)

            self._save_undo_state("Rotate 90° CCW")
            self.selected_texture['rgba_data'] = rotated_data
            self.selected_texture['width'] = rotated.width()
            self.selected_texture['height'] = rotated.height()

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rotated 90° CCW: now {rotated.width()}x{rotated.height()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")


    def _copy_texture(self): #vers 2
        """Copy selected texture data to clipboard"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to copy")
            return

        try:
            # Store full texture data
            self.clipboard_texture = {
                'name': self.selected_texture.get('name', 'texture'),
                'width': self.selected_texture.get('width', 0),
                'height': self.selected_texture.get('height', 0),
                'format': self.selected_texture.get('format', 'Unknown'),
                'depth': self.selected_texture.get('depth', 32),
                'rgba_data': self.selected_texture.get('rgba_data'),
                'has_alpha': self.selected_texture.get('has_alpha', False),
                'alpha_name': self.selected_texture.get('alpha_name', ''),
                'mipmap_levels': self.selected_texture.get('mipmap_levels', []),
            }

            self.paste_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Copied: {self.selected_texture.get('name')}")

        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy texture: {str(e)}")

    def _paste_texture(self): #vers 2
        """Paste copied texture data"""
        if not hasattr(self, 'clipboard_texture') or not self.clipboard_texture:
            QMessageBox.warning(self, "Nothing to Paste", "Clipboard is empty")
            return

        try:
            # Create new texture entry with clipboard data
            new_texture = self.clipboard_texture.copy()
            new_texture['name'] = new_texture['name'] + "_copy"

            # Add to texture list
            self.texture_list.append(new_texture)

            # Reload table
            self._reload_texture_table()

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Pasted: {new_texture['name']}")

        except Exception as e:
            QMessageBox.critical(self, "Paste Error", f"Failed to paste texture: {str(e)}")


    def _edit_texture_external(self): #vers 1
        """Edit texture in external editor (placeholder)"""
        QMessageBox.information(self, "Coming Soon",
            "External editor integration will be added soon!\n\n"
            "Will support:\n"
            "• Open in GIMP/Photoshop\n"
            "• Auto-reload on save\n"
            "• Custom editor paths")


    def _convert_texture_format(self): #vers 1
        """Convert texture format (placeholder)"""
        QMessageBox.information(self, "Coming Soon",
            "Format conversion tools will be added soon!\n\n"
            "Will support:\n"
            "• Batch DXT compression\n"
            "• Color depth conversion\n"
            "• Palette generation")


    def flip_texture(self): #vers 2
        """Flip between normal and alpha channel view (only if alpha exists)"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Check if texture has alpha
        if not self.selected_texture.get('has_alpha', False):
            QMessageBox.information(self, "No Alpha",
                "This texture has no alpha channel to view.\n\n"
                "Use 'Import → Import Alpha Channel' to add one.")
            return

        # Toggle alpha view flag
        if not hasattr(self, '_show_alpha'):
            self._show_alpha = False

        self._show_alpha = not self._show_alpha
        self._update_texture_info(self.selected_texture)

        mode = "Alpha Channel" if self._show_alpha else "Normal View"

        # Update flip button text if it exists
        if hasattr(self, 'flip_btn'):
            self.flip_btn.setText("🔄 Normal" if self._show_alpha else "🔄 Alpha")

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Switched to {mode}")


    def _refresh_main_window(self): #vers 1
        """Refresh the main window to show changes"""
        try:
            if self.main_window:
                # Try to refresh the main table
                if hasattr(self.main_window, 'refresh_table'):
                    self.main_window.refresh_table()
                elif hasattr(self.main_window, 'reload_current_file'):
                    self.main_window.reload_current_file()
                elif hasattr(self.main_window, 'update_display'):
                    self.main_window.update_display()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Refresh error: {str(e)}")


    def _rename_texture(self, alpha=False): #vers 2
        """Rename texture or alpha name and mark as modified"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_name = self.selected_texture.get('name', 'texture')

        if alpha:
            if not self.selected_texture.get('has_alpha', False):
                QMessageBox.information(self, "No Alpha", "This texture does not have an alpha channel")
                return

            alpha_name = self.selected_texture.get('alpha_name', current_name + 'a')
            new_name, ok = QInputDialog.getText(self, "Rename Alpha", "Enter alpha name:", text=alpha_name)
            if ok and new_name and new_name != alpha_name:
                self.selected_texture['alpha_name'] = new_name
                self.info_alpha_name.setText(f"Alpha: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Alpha renamed to: {new_name}")
        else:
            new_name, ok = QInputDialog.getText(self, "Rename Texture", "Enter texture name:", text=current_name)
            if ok and new_name and new_name != current_name:
                self.selected_texture['name'] = new_name
                self.info_name.setText(f"Name: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Texture renamed: {current_name} -> {new_name}")


    def _update_texture_name_in_data(self, data, offset, texture_info): #vers 1
        """Update texture name in the binary TXD data"""
        try:
            import struct

            # Navigate to the texture name location (offset + 12 for section header + 8 for platform info + name at pos 32)
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', data[struct_offset:struct_offset+12])

            if struct_type == 0x01:  # Struct section
                name_pos = struct_offset + 12 + 8  # Skip header and platform info

                # Update texture name (32 bytes)
                new_name = texture_info.get('name', 'texture')[:31]  # Max 31 chars + null terminator
                name_bytes = new_name.encode('ascii')[:31].ljust(32, b'\x00')
                data[name_pos:name_pos+32] = name_bytes

                # Update alpha/mask name if it exists (next 32 bytes)
                if texture_info.get('has_alpha', False) and texture_info.get('alpha_name'):
                    alpha_name = texture_info.get('alpha_name', '')[:31]
                    alpha_bytes = alpha_name.encode('ascii')[:31].ljust(32, b'\x00')
                    data[name_pos+32:name_pos+64] = alpha_bytes

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Name update error: {str(e)}")

        # Update window title to show unsaved changes
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")


    def _rebuild_txd_with_size_management(self): #vers 1
        """Rebuild TXD data with support for large texture replacements"""
        try:
            import struct

            if not self.current_txd_data or not self.texture_list:
                return None

            # Calculate new TXD size requirements
            estimated_size = self._calculate_new_txd_size()
            original_size = len(self.current_txd_data)

            if estimated_size > original_size * 3:  # More than 3x size increase
                reply = QMessageBox.question(self, "Large Texture Replacement",
                                        f"New TXD will be ~{estimated_size/1024/1024:.1f}MB "
                                        f"(was {original_size/1024/1024:.1f}MB). "
                                        f"This may require IMG rebuilding. Continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return None

            # Build new TXD from scratch rather than modifying existing
            return self._build_new_txd_structure()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD rebuild error: {str(e)}")
            return None


    def _requires_img_rebuild(self, new_txd_data): #vers 1
        """Check if IMG needs full rebuild due to size changes"""
        if not self.current_txd_data:
            return True

        size_ratio = len(new_txd_data) / len(self.current_txd_data)
        return size_ratio > 2.0  # Rebuild if more than 2x size increase


    def _update_img_with_large_txd(self, modified_txd_data): #vers 1
        """Handle IMG update with potentially large TXD replacements"""
        try:
            if self._requires_img_rebuild(modified_txd_data):
                return self._rebuild_img_with_new_txd(modified_txd_data)
            else:
                return self._update_img_in_place(modified_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG update error: {str(e)}")
            return False


    def _rebuild_img_with_new_txd(self, new_txd_data): #vers 1
        """Rebuild entire IMG file to accommodate large TXD"""
        try:
            # This would require integration with your IMG rebuilding system
            if self.main_window and hasattr(self.main_window, 'rebuild_current_img'):
                # Update TXD data first
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Trigger full IMG rebuild
                result = self.main_window.rebuild_current_img()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"IMG rebuilt due to large TXD size change")

                return result
            else:
                # Fallback: save to new file
                return self._save_as_new_img(new_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG rebuild error: {str(e)}")
            return False


    def _save_as_new_img(self, new_txd_data): #vers 1
        """Save as new IMG file when rebuild is needed"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save IMG with Large Textures",
                self.current_img.file_path.replace('.img', '_hd.img'),
                "IMG Files (*.img);;All Files (*)"
            )

            if file_path:
                # Update TXD data
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Save as new file
                self.current_img.save_as(file_path)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Saved as new IMG: {file_path}")

                return True

            return False

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Save as new error: {str(e)}")
            return False


    def open_img_archive(self): #vers 1
        """Open IMG archive and load TXD file list"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open IMG Archive", "", "IMG Files (*.img);;All Files (*)")
            if file_path:
                self.load_from_img_archive(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open IMG: {str(e)}")


    def open_txd_file(self, file_path=None): #vers 3
        """Open standalone TXD file with version detection"""
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Open TXD File", "",
                    "TXD Files (*.txd);;All Files (*)"
                )
            if file_path:
                self.current_txd_path = file_path  # Store the full path
                self.current_txd_name = os.path.basename(file_path)


            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()

                # Detect version info FIRST
                if not self._detect_txd_info(txd_data):
                    QMessageBox.warning(self, "Invalid TXD",
                        "Could not detect valid TXD format")
                    return

                # Load textures
                self._load_txd_textures(txd_data, os.path.basename(file_path))

                # Update window title with version info
                self.setWindowTitle(
                    f"TXD Workshop: {os.path.basename(file_path)} "
                    f"[{self.txd_version_str}]"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open TXD: {str(e)}")


    def _import_textures(self): #vers 6
        """Import textures with 8-bit indexed format support"""
        if not self.current_img and not self.current_txd_data:
            QMessageBox.warning(self, "No TXD", "Please open or create a TXD file first")
            return

        # File dialog for texture selection
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Textures",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tga *.dds *.iff *.ilbm *.lbm *.pcx *.gif);;All Files (*.*)"
        )

        if not file_paths:
            return

        # Check for disabled formats
        iff_files = []
        try:
            iff_files = [f for f in file_paths if is_iff_file(f)]
        except:
            pass

        if iff_files and hasattr(self, 'iff_import_enabled') and not self.iff_import_enabled:
            reply = QMessageBox.question(
                self,
                "IFF Import Disabled",
                f"Found {len(iff_files)} IFF files, but IFF import is disabled.\n"
                "Enable IFF support in Settings?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._show_workshop_settings()
                return

        # Import each texture
        imported_count = 0
        failed_count = 0

        for file_path in file_paths:
            try:
                success = self._import_single_texture(file_path)
                if success:
                    imported_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Import failed: {os.path.basename(file_path)} - {str(e)}")

        # Reload display
        if imported_count > 0:
            self._reload_texture_table()
            self._mark_as_modified()

        # Report results
        if self.main_window and hasattr(self.main_window, 'log_message'):
            if imported_count > 0:
                self.main_window.log_message(f"Imported {imported_count} texture(s)")
            if failed_count > 0:
                self.main_window.log_message(f"Failed to import {failed_count} texture(s)")


    def _import_single_texture(self, file_path): #vers 3
        """Import single texture with format detection and validation"""
        filename = os.path.basename(file_path)
        name_only = os.path.splitext(filename)[0]

        # Validate texture name
        if self.name_limit_enabled:
            if len(name_only) > self.max_texture_name_length:
                name_only = name_only[:self.max_texture_name_length]
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Texture name truncated to {self.max_texture_name_length} chars")

        valid, msg = self._validate_texture_name(name_only)
        if not valid:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Invalid name: {msg}")
            return False

        # Try indexed color formats first
        texture_data = None

        if is_indexed_format(file_path):
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Loading indexed format: {filename}")

            texture_data = load_indexed_image(file_path)

        elif is_iff_file(file_path):
            if not self.iff_import_enabled:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"IFF import disabled: {filename}")
                return False

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Loading IFF format: {filename}")

            texture_data = load_iff_image(file_path)

        # Fallback to PIL for standard formats
        if not texture_data:
            texture_data = self._load_texture_with_pil(file_path)

        if not texture_data:
            return False

        # Validate dimensions
        width = texture_data['width']
        height = texture_data['height']

        valid, msg = self._validate_texture_dimensions(width, height)
        if not valid:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ {filename}: {msg}")
            return False

        # Add to texture list
        new_texture = {
            'name': name_only,
            'width': width,
            'height': height,
            'rgba_data': texture_data['rgba_data'],
            'has_alpha': texture_data.get('has_alpha', False),
            'format': texture_data.get('format', 'ARGB8888'),
            'alpha_name': name_only + 'a' if texture_data.get('has_alpha') else '',
            'mipmaps': 1,
            'original_format': texture_data.get('original_format', 'Unknown')
        }

        self.texture_list.append(new_texture)

        if self.main_window and hasattr(self.main_window, 'log_message'):
            format_str = texture_data.get('original_format', 'Unknown')
            self.main_window.log_message(
                f"Imported: {name_only} ({width}x{height}, {format_str})"
            )

        return True


    def _load_texture_with_pil(self, file_path): #vers 2
        """Load texture using PIL as fallback"""
        try:
            from PIL import Image

            img = Image.open(file_path)

            # Convert to RGBA
            if img.mode in ('RGBA', 'LA'):
                has_alpha = True
                img = img.convert('RGBA')
            else:
                has_alpha = False
                img = img.convert('RGB')

            width, height = img.size

            # Get raw pixel data
            if has_alpha:
                rgba_data = img.tobytes('raw', 'RGBA')
            else:
                rgb_data = img.tobytes('raw', 'RGB')
                # Add alpha channel
                rgba_data = bytearray()
                for i in range(0, len(rgb_data), 3):
                    rgba_data.extend(rgb_data[i:i+3])
                    rgba_data.append(255)
                rgba_data = bytes(rgba_data)

            return {
                'width': width,
                'height': height,
                'rgba_data': rgba_data,
                'has_alpha': has_alpha,
                'format': 'ARGB8888' if has_alpha else 'RGB888',
                'original_format': 'PIL-Standard'
            }

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"PIL import error: {str(e)}")
            return None


    def _ensure_depends_structure(self): #vers 1
        """Ensure depends/ folder exists in standalone mode with required files"""
        if not self.standalone_mode:
            return

        script_dir = Path(__file__).parent.resolve()
        depends_dir = script_dir / "depends"

        # Create depends folder if it doesn't exist
        if not depends_dir.exists():
            depends_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created depends directory: {depends_dir}")

        # Check for required import modules
        required_modules = [
            'iff_import.py',
            'indexed_color_import.py',
            'txd_versions.py'
        ]

        missing = []
        for module in required_modules:
            module_path = depends_dir / module
            if not module_path.exists():
                missing.append(module)

        if missing:
            print(f"Warning: Missing modules in depends/: {', '.join(missing)}")
            print(f"Copy these from methods/ to: {depends_dir}")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f" Missing import modules: {', '.join(missing)}")


    def _get_import_format_info(self): #vers 1
        """Get supported import formats as formatted string"""
        formats = []

        # Standard formats (always available via PIL)
        formats.append("✓ PNG, JPG, BMP, TGA (standard)")

        # Check indexed format support
        try:
            from methods.indexed_color_import import is_indexed_format
            formats.append("✓ 8-bit BMP, PCX, GIF")
        except ImportError:
            formats.append("✗ 8-bit indexed formats (missing module)")

        # Check IFF support
        if self.iff_import_enabled:
            try:
                from methods.iff_import import is_iff_file
                formats.append("✓ IFF/ILBM (Amiga)")
            except ImportError:
                formats.append("✗ IFF format (missing module)")
        else:
            formats.append("○ IFF format (disabled)")

        return "\n".join(formats)


    def show_properties(self): #vers 2
        """Show TXD properties including version and platform information"""
        if not self.current_txd_name:
            QMessageBox.information(self, "No TXD", "No TXD file loaded")
            return

        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("TXD Properties")
            dialog.setMinimumWidth(500)

            layout = QFormLayout(dialog)

            # Basic info
            layout.addRow("TXD Name:", QLabel(self.current_txd_name))
            layout.addRow("Texture Count:", QLabel(str(len(self.texture_list))))

            # NEW: Version information
            layout.addRow("", QLabel(""))  # Spacer
            layout.addRow("RenderWare Version:", QLabel(self.txd_version_str))
            layout.addRow("Platform:", QLabel(self.txd_platform_name))
            layout.addRow("Game:", QLabel(self.txd_game))
            layout.addRow("Format:", QLabel(self._get_format_description()))

            # NEW: Capabilities
            if self.txd_capabilities:
                layout.addRow("", QLabel(""))  # Spacer
                caps_label = QLabel("<b>Capabilities:</b>")
                layout.addRow(caps_label)

                if self.txd_capabilities.get('mipmaps'):
                    layout.addRow("  Mipmaps:", QLabel("Supported"))
                if self.txd_capabilities.get('bumpmaps'):
                    layout.addRow("  Bumpmaps:", QLabel("Supported"))
                if self.txd_capabilities.get('dxt_compression'):
                    layout.addRow("  DXT Compression:", QLabel("Supported"))
                if self.txd_capabilities.get('palette'):
                    layout.addRow("  Palette:", QLabel("Supported"))
                if self.txd_capabilities.get('swizzled'):
                    layout.addRow("  Swizzled:", QLabel("Yes (Console)"))

            # File size info
            if self.current_txd_data:
                size_kb = len(self.current_txd_data) / 1024
                layout.addRow("", QLabel(""))  # Spacer
                layout.addRow("File Size:", QLabel(f"{size_kb:.2f} KB"))

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addRow("", close_btn)

            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not show properties: {str(e)}")


    def _create_texture_filters(self): #vers 1
        """Create texture filtering options"""
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)

        # Format filter
        format_filter_layout = QHBoxLayout()
        format_filter_layout.addWidget(QLabel("Format:"))

        self.format_filter = QComboBox()
        self.format_filter.addItems(["All", "DXT1", "DXT3", "DXT5", "ARGB8888", "RGB888"])
        self.format_filter.currentTextChanged.connect(self._apply_texture_filters)
        format_filter_layout.addWidget(self.format_filter)

        filter_layout.addLayout(format_filter_layout)

        # Size filter
        size_filter_layout = QHBoxLayout()
        size_filter_layout.addWidget(QLabel("Size:"))

        self.size_filter = QComboBox()
        self.size_filter.addItems(["All", "Small (≤256)", "Medium (512-1024)", "Large (≥2048)"])
        self.size_filter.currentTextChanged.connect(self._apply_texture_filters)
        size_filter_layout.addWidget(self.size_filter)

        filter_layout.addLayout(size_filter_layout)

        # Alpha filter
        self.alpha_filter = QComboBox()
        self.alpha_filter.addItems(["All", "With Alpha", "No Alpha"])
        self.alpha_filter.currentTextChanged.connect(self._apply_texture_filters)
        filter_layout.addWidget(self.alpha_filter)

        return filter_group


    def _apply_texture_filters(self): #vers 1
        """Apply texture filters to table"""
        if not hasattr(self, 'texture_table') or not self.texture_list:
            return

        format_filter = self.format_filter.currentText() if hasattr(self, 'format_filter') else "All"
        size_filter = self.size_filter.currentText() if hasattr(self, 'size_filter') else "All"
        alpha_filter = self.alpha_filter.currentText() if hasattr(self, 'alpha_filter') else "All"

        for row in range(self.texture_table.rowCount()):
            if row < len(self.texture_list):
                texture = self.texture_list[row]
                show_row = True

                # Format filter
                if format_filter != "All":
                    tex_format = texture.get('format', 'Unknown')
                    if format_filter not in tex_format:
                        show_row = False

                # Size filter
                if size_filter != "All" and show_row:
                    width = texture.get('width', 0)
                    height = texture.get('height', 0)
                    max_dim = max(width, height)

                    if size_filter == "Small (≤256)" and max_dim > 256:
                        show_row = False
                    elif size_filter == "Medium (512-1024)" and (max_dim < 512 or max_dim > 1024):
                        show_row = False
                    elif size_filter == "Large (≥2048)" and max_dim < 2048:
                        show_row = False

                # Alpha filter
                if alpha_filter != "All" and show_row:
                    has_alpha = texture.get('has_alpha', False)
                    if alpha_filter == "With Alpha" and not has_alpha:
                        show_row = False
                    elif alpha_filter == "No Alpha" and has_alpha:
                        show_row = False

                self.texture_table.setRowHidden(row, not show_row)


    def _create_texture_search(self): #vers 1
        """Create texture search functionality"""
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Search:"))

        from PyQt6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter texture name...")
        self.search_input.textChanged.connect(self._perform_texture_search)
        search_layout.addWidget(self.search_input)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.clicked.connect(self._clear_texture_search)
        search_layout.addWidget(clear_search_btn)

        return search_layout


    def _perform_texture_search(self, search_text): #vers 1
        """Perform texture search"""
        if not hasattr(self, 'texture_table') or not self.texture_list:
            return

        search_text = search_text.lower().strip()

        for row in range(self.texture_table.rowCount()):
            if row < len(self.texture_list):
                texture = self.texture_list[row]
                texture_name = texture.get('name', '').lower()

                # Show row if search text is in texture name or if search is empty
                show_row = not search_text or search_text in texture_name
                self.texture_table.setRowHidden(row, not show_row)


    def _clear_texture_search(self): #vers 1
        """Clear texture search"""
        if hasattr(self, 'search_input'):
            self.search_input.clear()

        # Show all rows
        if hasattr(self, 'texture_table'):
            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHidden(row, False)

    def _duplicate_texture(self): #vers 2
        """Duplicate selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to duplicate")
            return

        try:
            # Create deep copy of texture
            new_texture = {
                'name': self.selected_texture.get('name', 'texture') + "_copy",
                'width': self.selected_texture.get('width', 0),
                'height': self.selected_texture.get('height', 0),
                'format': self.selected_texture.get('format', 'Unknown'),
                'depth': self.selected_texture.get('depth', 32),
                'rgba_data': self.selected_texture.get('rgba_data'),
                'has_alpha': self.selected_texture.get('has_alpha', False),
                'alpha_name': self.selected_texture.get('alpha_name', '') + "_copy" if self.selected_texture.get('alpha_name') else '',
                'mipmap_levels': self.selected_texture.get('mipmap_levels', []).copy(),
            }

            # Add to texture list
            self.texture_list.append(new_texture)

            # Reload table
            self._reload_texture_table()

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Duplicated: {new_texture['name']}")

        except Exception as e:
            QMessageBox.critical(self, "Duplicate Error", f"Failed to duplicate texture: {str(e)}")

    def _remove_texture(self): #vers 1
        """Remove selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to remove")
            return

        texture_name = self.selected_texture.get('name', 'texture')

        reply = QMessageBox.question(self, "Remove Texture",
                                   f"Remove texture '{texture_name}'?\nThis cannot be undone.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Find and remove from list
            current_row = self.texture_table.currentRow()
            if 0 <= current_row < len(self.texture_list):
                self.texture_list.pop(current_row)
                self.texture_table.removeRow(current_row)

                # Clear selection
                self.selected_texture = None
                self._update_editing_controls()

                # Mark as modified
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Removed texture: {texture_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove texture: {str(e)}")


    def _create_new_texture(self): #vers 1
        """Create new blank texture"""
        from PyQt6.QtWidgets import QInputDialog

        # Get texture name
        name, ok = QInputDialog.getText(self, "New Texture", "Enter texture name:")
        if not ok or not name:
            return

        # Check for duplicate names
        existing_names = [t.get('name', '') for t in self.texture_list]
        if name in existing_names:
            QMessageBox.warning(self, "Duplicate Name", f"Texture name '{name}' already exists")
            return

        # Get dimensions
        width, ok = QInputDialog.getInt(self, "New Texture", "Width:", value=256, min=4, max=4096)
        if not ok:
            return

        height, ok = QInputDialog.getInt(self, "New Texture", "Height:", value=256, min=4, max=4096)
        if not ok:
            return

        try:
            # Create blank RGBA data (transparent)
            rgba_data = bytearray(width * height * 4)
            for i in range(0, len(rgba_data), 4):
                rgba_data[i:i+4] = [0, 0, 0, 0]  # Transparent black

            # Create texture
            new_texture = {
                'name': name,
                'width': width,
                'height': height,
                'format': 'ARGB8888',
                'has_alpha': True,
                'rgba_data': bytes(rgba_data),
                'mipmaps': 1
            }

            # Add to list
            self.texture_list.append(new_texture)
            self._add_texture_to_table(new_texture)

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Created new texture: {name} ({width}x{height})")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create texture: {str(e)}")

    def _close_txd_tab(self, index): #vers 1
        """Close TXD tab"""
        if self.txd_tabs.count() <= 1:
            QMessageBox.warning(self, "Cannot Close", "Cannot close the last tab")
            return

        # Check if modified
        # TODO: Check modification state

        self.txd_tabs.removeTab(index)

    def _switch_txd_tab(self, index): #vers 1
        """Switch to different TXD tab"""
        if index < 0:
            return

        # TODO: Load texture list for this tab
        tab_name = self.txd_tabs.tabText(index)

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Switched to tab: {tab_name}")

    def _add_new_txd_tab(self, txd_name, txd_data): #vers 1
        """Add new TXD as a tab"""
        # Create new tab widget
        new_tab = QWidget()
        tab_layout = QVBoxLayout(new_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for this tab
        # ... similar to initial tab setup ...

        # Add tab
        tab_index = self.txd_tabs.addTab(new_tab, txd_name)
        self.txd_tabs.setCurrentIndex(tab_index)

    def _texture_statistics(self): #vers 1
        """Show texture statistics"""
        if not self.texture_list:
            QMessageBox.information(self, "Statistics", "No textures loaded")
            return

        # Calculate statistics
        total_textures = len(self.texture_list)
        total_size = 0
        format_counts = {}
        alpha_count = 0
        size_distribution = {"Small (≤256)": 0, "Medium (512-1024)": 0, "Large (≥2048)": 0}

        for texture in self.texture_list:
            # Size calculation
            if texture.get('rgba_data'):
                total_size += len(texture['rgba_data'])

            # Format count
            fmt = texture.get('format', 'Unknown')
            format_counts[fmt] = format_counts.get(fmt, 0) + 1

            # Alpha count
            if texture.get('has_alpha', False):
                alpha_count += 1

            # Size distribution
            max_dim = max(texture.get('width', 0), texture.get('height', 0))
            if max_dim <= 256:
                size_distribution["Small (≤256)"] += 1
            elif max_dim <= 1024:
                size_distribution["Medium (512-1024)"] += 1
            else:
                size_distribution["Large (≥2048)"] += 1

        # Build statistics text
        stats = f"=== TXD Statistics ===\n"
        stats += f"Total Textures: {total_textures}\n"
        stats += f"Total Data Size: {total_size:,} bytes ({total_size/1024:.1f} KB)\n"
        stats += f"Textures with Alpha: {alpha_count} ({alpha_count/total_textures*100:.1f}%)\n\n"

        stats += "=== Format Distribution ===\n"
        for fmt, count in sorted(format_counts.items()):
            percentage = count / total_textures * 100
            stats += f"{fmt}: {count} ({percentage:.1f}%)\n"

        stats += "\n=== Size Distribution ===\n"
        for size_cat, count in size_distribution.items():
            percentage = count / total_textures * 100
            stats += f"{size_cat}: {count} ({percentage:.1f}%)\n"

        QMessageBox.information(self, "TXD Statistics", stats)

    def _check_txd_vs_dff(self): #vers 2
        """Check TXD texture names against DFF model"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures loaded in TXD")
            return

        # Select DFF file
        dff_path, _ = QFileDialog.getOpenFileName(
            self, "Select DFF Model File", "",
            "DFF Files (*.dff);;All Files (*)"
        )

        if not dff_path:
            return

        try:
            # TODO: Parse DFF file and extract material/texture names
            # For now, show placeholder
            # Show the dff/ mdl model texture list.

            result_text = "DFF Texture Check Results:\n\n"
            result_text += f"TXD has {len(self.texture_list)} textures\n"
            result_text += f"DFF file: {os.path.basename(dff_path)}\n\n"
            result_text += "Full implementation requires DFF parser"

            QMessageBox.information(self, "Check Complete", result_text)

        except Exception as e:
            QMessageBox.critical(self, "Check Error", f"Failed to check DFF: {str(e)}")

    def _build_txd_from_dff(self): #vers 1
        """Build TXD structure from DFF material names"""
        dff_path, _ = QFileDialog.getOpenFileName(
            self, "Select DFF File", "",
            "DFF Files (*.dff);;All Files (*)"
        )

        if not dff_path:
            return

        try:
            # TODO: Parse DFF, extract material names, create blank textures
            QMessageBox.information(self, "Build from DFF",
                "Build from DFF functionality coming soon.\n\n"
                "This will:\n"
                "- Parse DFF material names\n"
                "- Create blank textures for each\n"
                "- Set up proper TXD structure"
                "- import texture files from bmp/png assists")
        except Exception as e:
            QMessageBox.critical(self, "Build Error", f"Failed: {str(e)}")

    def _open_paint_editor(self): #vers 1
        """Open paint editor for texture"""
        if not self.selected_texture:
            return

        QMessageBox.information(self, "Paint Editor",
            "Paint editor functionality coming soon")

    def _add_texture_to_table(self, texture): #vers 2
        """Add a texture to the table with compression status"""
        row = self.texture_table.rowCount()
        self.texture_table.insertRow(row)

        # Create thumbnail
        thumb_item = QTableWidgetItem()
        rgba_data = texture.get('rgba_data')
        width = texture.get('width', 0)
        height = texture.get('height', 0)

        if rgba_data and width > 0:
            pixmap = self._create_thumbnail(rgba_data, width, height)
            if pixmap:
                thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
            else:
                thumb_item.setText("🖼️")
        else:
            thumb_item.setText("🖼️")

        # Create details with compression status
        details = f"Name: {texture['name']}\n"
        if texture.get('has_alpha', False):
            alpha_name = texture.get('alpha_name', texture['name'] + 'a')
            details += f"Alpha: {alpha_name}\n"
        if width > 0:
            details += f"Size: {width}x{height}\n"

        # Show format with compression status
        fmt = texture['format']
        if 'DXT' in fmt:
            details += f"Format: {fmt} (Compressed)\n"
        else:
            details += f"Format: {fmt} (Uncompressed)\n"

        details += f"Alpha: {'Yes' if texture.get('has_alpha', False) else 'No'}"

        details_item = QTableWidgetItem(details)

        # Make items non-editable
        thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.texture_table.setItem(row, 0, thumb_item)
        self.texture_table.setItem(row, 1, details_item)
        self.texture_table.setRowHeight(row, 80)


    def _load_settings(self): #vers 1
        """Load settings from config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'txd_workshop_settings.json'
        )

        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.save_to_source_location = settings.get('save_to_source_location', True)
                    self.last_save_directory = settings.get('last_save_directory', None)
        except Exception as e:
            print(f"Failed to load settings: {e}")


    def _save_settings(self): #vers 1
        """Save settings to config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'txd_workshop_settings.json'
        )

        try:
            settings = {
                'save_to_source_location': self.save_to_source_location,
                'last_save_directory': self.last_save_directory
            }

            with open(settings_file, 'w') as f:
                json.dump(settings, indent=2, fp=f)
        except Exception as e:
            print(f"Failed to save settings: {e}")


    def keyPressEvent(self, event): #vers 1
        """Handle keyboard shortcuts"""
        from PyQt6.QtCore import Qt

        # D key - Dock/Undock toggle
        if event.key() == Qt.Key.Key_D and not event.modifiers():
            self.toggle_dock_mode()
            event.accept()
            return

        # T key - Tear out (same as undock)
        if event.key() == Qt.Key.Key_T and not event.modifiers():
            if self.is_docked:
                self._undock_from_main()
            event.accept()
            return

        super().keyPressEvent(event)

#class SvgIcons: #vers 1 - Once functions are updated this class will be moved to the bottom
    """SVG icon data to QIcon with theme color support"""


    def _create_bitdepth_icon(self): #vers 3
        """Create bit depth icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M3,5H9V11H3V5M5,7V9H7V7H5M11,7H21V9H11V7M11,15H21V17H11V15M5,20L1.5,16.5L2.91,15.09L5,17.17L9.59,12.59L11,14L5,20Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_resize_icon(self): #vers 2
        """Create resize icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M10,21V19H6.41L10.91,14.5L9.5,13.09L5,17.59V14H3V21H10M14.5,10.91L19,6.41V10H21V3H14V5H17.59L13.09,9.5L14.5,10.91Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_resize_icon2(self): #vers 1
        """Resize grip icon - diagonal arrows"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 6l-8 8M10 6h4v4M6 14v-4h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - brain/intelligence style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Brain outline -->
            <path d="M12 3 C8 3 5 6 5 9 C5 10 5.5 11 6 12 C5.5 13 5 14 5 15 C5 18 8 21 12 21 C16 21 19 18 19 15 C19 14 18.5 13 18 12 C18.5 11 19 10 19 9 C19 6 16 3 12 3 Z"
                fill="none" stroke="currentColor" stroke-width="1.5"/>

            <!-- Neural pathways inside -->
            <path d="M9 8 L10 10 M14 8 L13 10 M10 12 L14 12 M9 14 L12 16 M15 14 L12 16"
                stroke="currentColor" stroke-width="1" fill="none"/>

            <!-- Upward indicator -->
            <path d="M19 8 L19 4 M17 6 L19 4 L21 6"
                stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - sparkle/magic AI style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Large sparkle -->
            <path d="M12 2 L13 8 L12 14 L11 8 Z M8 12 L2 11 L8 10 L14 11 Z"
                fill="currentColor"/>

            <!-- Small sparkles -->
            <circle cx="18" cy="6" r="1.5" fill="currentColor"/>
            <circle cx="6" cy="18" r="1.5" fill="currentColor"/>
            <circle cx="19" cy="16" r="1" fill="currentColor"/>

            <!-- Upward arrow -->
            <path d="M16 20 L20 20 M18 18 L18 22"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - neural network style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Neural network nodes -->
            <circle cx="6" cy="6" r="2" fill="currentColor"/>
            <circle cx="18" cy="6" r="2" fill="currentColor"/>
            <circle cx="6" cy="18" r="2" fill="currentColor"/>
            <circle cx="18" cy="18" r="2" fill="currentColor"/>
            <circle cx="12" cy="12" r="2.5" fill="currentColor"/>

            <!-- Connecting lines -->
            <path d="M7.5 7.5 L10.5 10.5 M13.5 10.5 L16.5 7.5 M7.5 16.5 L10.5 13.5 M13.5 13.5 L16.5 16.5"
                stroke="currentColor" stroke-width="1.5" fill="none"/>

            <!-- Upward arrow overlay -->
            <path d="M12 3 L12 9 M9 6 L12 3 L15 6"
                stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_manage_icon(self): #vers 1
        """Create manage/settings icon for bumpmap manager"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Gear/cog icon for management -->
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_paint_icon(self): #vers 1
        """Create paint brush icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M20.71 7.04c.39-.39.39-1.04 0-1.41l-2.34-2.34c-.37-.39-1.02-.39-1.41 0l-1.84 1.83 3.75 3.75M3 17.25V21h3.75L17.81 9.93l-3.75-3.75L3 17.25z"
                fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_compress_icon(self): #vers 2
        """Create compress icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M4,2H20V4H13V10H20V12H4V10H11V4H4V2M4,13H20V15H13V21H20V23H4V21H11V15H4V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_build_icon(self): #vers 1
        """Create build/construct icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M22,9 L12,2 L2,9 L12,16 L22,9 Z M12,18 L4,13 L4,19 L12,24 L20,19 L20,13 L12,18 Z"
                fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_uncompress_icon(self): #vers 2
        """Create uncompress icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M11,4V2H13V4H11M13,21V19H11V21H13M4,12V10H20V12H4Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_view_icon(self): #vers 2
        """Create view/eye icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9
                    M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17
                    M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5
                    C17,19.5 21.27,16.39 23,12
                    C21.27,7.61 17,4.5 12,4.5Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_add_icon(self): #vers 2
        """Create add/plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_delete_icon(self): #vers 2
        """Create delete/minus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H5V11H19V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_color_picker_icon(self): #vers 1
        """Color picker icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M10 3v4M10 13v4M3 10h4M13 10h4" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_zoom_in_icon(self): #vers 1
        """Zoom in icon (+)"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2"/>
            <path d="M8 5v6M5 8h6" stroke="currentColor" stroke-width="2"/>
            <path d="M13 13l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_zoom_out_icon(self): #vers 1
        """Zoom out icon (-)"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2"/>
            <path d="M5 8h6" stroke="currentColor" stroke-width="2"/>
            <path d="M13 13l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_reset_icon(self): #vers 1
        """Reset/1:1 icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 10A6 6 0 1 1 4 10M4 10l3-3m-3 3l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_fit_icon(self): #vers 1
        """Fit to window icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_arrow_up_icon(self): #vers 1
        """Arrow up"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 3v10M4 7l4-4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)

    def _create_arrow_down_icon(self): #vers 1
        """Arrow down"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 13V3M12 9l-4 4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)

    def _create_arrow_left_icon(self): #vers 1
        """Arrow left"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8h10M7 4L3 8l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)

    def _create_arrow_right_icon(self): #vers 1
        """Arrow right"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 8H3M9 12l4-4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)

    def _create_flip_vert_icon(self): #vers 1
        """Create vertical flip SVG icon"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12h18M8 7l-4 5 4 5M16 7l4 5-4 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_flip_horz_icon(self): #vers 1
        """Create horizontal flip SVG icon"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 3v18M7 8l5-4 5 4M7 16l5 4 5-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_rotate_cw_icon(self): #vers 1
        """Create clockwise rotation SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12a9 9 0 11-9-9v6M21 3l-3 6-6-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_rotate_ccw_icon(self): #vers 1
        """Create counter-clockwise rotation SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12a9 9 0 109-9v6M3 3l3 6 6-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_copy_icon(self): #vers 1
        """Create copy SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_paste_icon(self): #vers 1
        """Create paste SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" stroke="currentColor" stroke-width="2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_edit_icon(self): #vers 1
        """Create edit SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_convert_icon(self): #vers 1
        """Create convert SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12h18M3 12l4-4M3 12l4 4M21 12l-4-4M21 12l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)

    def _create_undo_icon(self): #vers 2
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_info_icon(self): #vers 1
        """Info - circle with 'i' icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 11v6M12 8v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_folder_icon(self): #vers 1
        """Open IMG - Folder icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_file_icon(self): #vers 1
        """Open TXD - File icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_save_icon(self): #vers 1
        """Save TXD - Floppy disk icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2"/>
            <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_import_icon(self): #vers 1
        """Import - Download/Import icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_export_icon(self): #vers 1
        """Export - Upload/Export icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_package_icon(self): #vers 1
        """Export All - Package/Box icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2"/>
            <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_properties_icon(self): #vers 1
        """Properties - Info/Details icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    # CONTEXT MENU ICONS

    def _create_plus_icon(self): #vers 1
        """Create New Entry - Plus icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_document_icon(self): #vers 1
        """Create New TXD - Document icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_add_icon(self): #vers 1
        """Add/plus icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_trash_icon(self): #vers 1
        """Delete/trash icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5h14M8 5V3h4v2M6 5v11a1 1 0 001 1h6a1 1 0 001-1V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_delete_icon(self): #vers 1
        """Delete/trash icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5h14M8 5V3h4v2M6 5v11a1 1 0 001 1h6a1 1 0 001-1V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_duplicate_icon(self): #vers 1
        """Duplicate/copy icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="10" height="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M4 4h8v2H6v8H4V4z" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_create_icon(self): #vers 1
        """Create/new icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_pencil_icon(self): #vers 1
        """Edit - Pencil icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_trash_icon(self): #vers 1
        """Delete - Trash icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_check_icon(self): #vers 2
        """Create check/verify icon - document with checkmark"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
                fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M9 13l2 2 4-4"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_eye_icon(self): #vers 1
        """View - Eye icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_list_icon(self): #vers 1
        """Properties List - List icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    # WINDOW CONTROL ICONS

    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_maximize_icon(self): #vers 1
        """Maximize - Square"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokea-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_settings_icon(self): #vers 1
        """Settings/gear icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_maximize_icon(self): #vers 1
        """Maximize - Square icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="6" y1="6" x2="18" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="18" y1="6" x2="6" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_add_icon(self): #vers 1
        """Add - Plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_delete_icon(self): #vers 1
        """Delete - Trash icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_import_icon(self): #vers 1
        """Import - Download arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_export_icon(self): #vers 1
        """Export - Upload arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_checkerboard_icon(self): #vers 1
        """Create checkerboard pattern icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="5" height="5" fill="currentColor"/>
            <rect x="5" y="5" width="5" height="5" fill="currentColor"/>
            <rect x="10" y="0" width="5" height="5" fill="currentColor"/>
            <rect x="15" y="5" width="5" height="5" fill="currentColor"/>
            <rect x="0" y="10" width="5" height="5" fill="currentColor"/>
            <rect x="5" y="15" width="5" height="5" fill="currentColor"/>
            <rect x="10" y="10" width="5" height="5" fill="currentColor"/>
            <rect x="15" y="15" width="5" height="5" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_undo_icon(self): #vers 2
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _svg_to_icon(self, svg_data, size=24): #vers 2
        """Convert SVG data to QIcon with theme color support"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        try:
            # Get current text color from palette
            text_color = self.palette().color(self.foregroundRole())

            # Replace currentColor with actual color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except:
            # Fallback to no icon if SVG fails
            return QIcon()


class BumpmapManagerWindow(QWidget): #vers 1
    """Bumpmap Manager - Modern design matching Mipmap Manager"""

    def __init__(self, parent, texture_data, main_window=None): #vers 2
        """Initialize with 30% smaller height"""
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified = False

        from PyQt6.QtGui import QFont
        self.panel_font = QFont('Segoe UI', 10)
        self.button_font = QFont('Segoe UI', 9)
        self.title_font = QFont('Segoe UI', 10)

        texture_name = texture_data.get('name', 'Unknown')
        width = texture_data.get('width', 0)
        height = texture_data.get('height', 0)

        self.setWindowTitle(f"Bumpmap Manager - {texture_name}")
        self.resize(900, 600)  # Changed from 650 to 455 (30% smaller)

        # Frameless window with custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None
        self.current_txd_path = None

        self.setup_ui()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)


    def setup_ui(self): #vers 7
        """Setup modern UI - Now includes reflection maps"""
        from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                    QPushButton, QGroupBox, QSplitter, QFrame)
        from PyQt6.QtCore import Qt

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create custom title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # Main content area - Use splitter for resizable panels
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)

        # Create splitter for panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Texture info and preview
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Middle: Bumpmap controls
        middle_panel = self._create_middle_panel()
        splitter.addWidget(middle_panel)

        # Right: Bumpmap preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Fourth: Reflection maps panel
        reflection_panel = self._create_reflection_panel()
        splitter.addWidget(reflection_panel)

        # Set splitter sizes (25% each for 4 panels)
        splitter.setSizes([250, 250, 250, 250])

        content_layout.addWidget(splitter)
        main_layout.addWidget(content)

        # REMOVE THIS SECTION - No bottom button bar needed
        # button_bar = self._create_button_bar()
        # main_layout.addWidget(button_bar)

        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
                padding: 5px 15px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QLabel {
                border: none;
            }
            QFrame {
                border: 1px solid #3a3a3a;
            }
        """)

        # Update previews AFTER all widgets are created
        if hasattr(self, 'bumpmap_preview'):
            self._update_bumpmap_preview()
        if 'reflection_map' in self.texture_data and hasattr(self, 'reflection_preview'):
            self._update_reflection_previews()


    def _create_button_bar(self): #vers 1
        """Create bottom button bar"""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

        button_bar = QWidget()
        button_bar.setFixedHeight(50)
        button_bar.setStyleSheet("border-top: 1px solid #3a3a3a;")

        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                border: 1px solid #1177bb;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return button_bar


    def _create_left_panel(self): #vers 6
        """Create left panel - title on far right"""
        panel = QGroupBox("Main Texture    .")
        # Style to move title to the right
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Info container with proper spacing
        info_container = QWidget()
        info_container.setFixedHeight(85)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(5)

        # Name
        name_label = QLabel(f"Name: {self.texture_data.get('name', 'Unknown')}")
        name_label.setStyleSheet("font-size: 14pt; line-height: 1.4;")
        name_label.setWordWrap(False)
        info_layout.addWidget(name_label)

        # Size
        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)
        size_label = QLabel(f"Size: {width} × {height}")
        size_label.setStyleSheet("font-size: 14pt; line-height: 1.4;")
        info_layout.addWidget(size_label)

        # Format
        fmt = self.texture_data.get('format', 'Unknown')
        format_label = QLabel(f"Format: {fmt}")
        format_label.setStyleSheet("font-size: 14pt; line-height: 1.4;")
        info_layout.addWidget(format_label)

        info_layout.addStretch()

        layout.addWidget(info_container)

        # Main texture preview
        preview_label = QLabel()
        preview_label.setMinimumHeight(250)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("border: 1px solid #3a3a3a; background: #1e1e1e;")

        # Load texture preview
        rgba_data = self.texture_data.get('rgba_data')
        if rgba_data and width > 0:
            image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(image)
            preview_label.setPixmap(
                pixmap.scaled(250, 250,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
            )
        else:
            preview_label.setText("No texture data")

        layout.addWidget(preview_label)

        return panel


    def _create_middle_panel(self): #vers 1
        """Create middle panel with bumpmap controls"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGroupBox, QLabel

        panel = QGroupBox("Controls    .")
        # Match your styling
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Info text
        info_label = QLabel(
            "Bumpmaps add surface detail.\n"
            "Generate from texture or import."
        )
        info_label.setFont(self.panel_font)
        info_label.setStyleSheet("color: #888; line-height: 1.4;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Generate button (F9)
        generate_btn = QPushButton("Generate from Texture (F9)")
        generate_btn.setFont(self.button_font)
        generate_btn.clicked.connect(self._generate_bumpmap)
        layout.addWidget(generate_btn)

        # Import button (F10)
        import_btn = QPushButton("Import from File (F10)")
        import_btn.setFont(self.button_font)
        import_btn.clicked.connect(self._import_bumpmap)
        layout.addWidget(import_btn)

        # Export button
        export_btn = QPushButton("Export to File")
        export_btn.setFont(self.button_font)
        export_btn.clicked.connect(self._export_bumpmap)
        export_btn.setEnabled(self._has_bumpmap())
        layout.addWidget(export_btn)

        # Delete button (F11)
        delete_btn = QPushButton("Delete Bumpmap (F11)")
        delete_btn.setFont(self.button_font)
        delete_btn.clicked.connect(self._delete_bumpmap)
        delete_btn.setEnabled(self._has_bumpmap())
        layout.addWidget(delete_btn)

        layout.addStretch()

        # Type info
        type_info = QLabel(
            "Types:\n"
            "• Grayscale Height Map\n"
            "• RGB Normal Map\n"
            "• Both (Height + Normal)"
        )
        type_info.setFont(self.panel_font)
        type_info.setStyleSheet("color: #aaa; font-size: 9pt;")
        type_info.setWordWrap(True)
        layout.addWidget(type_info)

        return panel


    def _create_right_panel(self): #vers 6
        """Create right panel - title on far right"""
        panel = QGroupBox("Bumpmap    .")
        # Style to move title to the right
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Info container with same height as left
        info_container = QWidget()
        info_container.setFixedHeight(85)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(1, 1, 1, 1)
        info_layout.setSpacing(5)

        # Status
        has_bumpmap = self._has_bumpmap()
        status_label = QLabel(f"Status: {'Present' if has_bumpmap else 'Not present'}")
        status_label.setFont(self.panel_font)
        status_label.setStyleSheet(
        "line-height: 1.4; color: #4CAF50;" if has_bumpmap
        else "line-height: 1.4; color: #888;"
        )
        info_layout.addWidget(status_label)

        # Type
        type_label = QLabel("Type: Environment map (Normal map)")
        type_label.setFont(self.panel_font)
        type_label.setStyleSheet("line-height: 1.4;")
        info_layout.addWidget(type_label)

        info_layout.addStretch()

        layout.addWidget(info_container)

        # Bumpmap preview
        self.bumpmap_preview = QLabel()
        self.bumpmap_preview.setMinimumHeight(250)
        self.bumpmap_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bumpmap_preview.setFont(self.panel_font)
        self.bumpmap_preview.setStyleSheet("border: 1px solid #3a3a3a; background: #1e1e1e;")

        # Load bumpmap preview if available
        if has_bumpmap:
            self._update_bumpmap_preview()
        else:
            self.bumpmap_preview.setText("No bumpmap data\n\nPress F9 or use Edit → Generate Bumpmap")

        layout.addWidget(self.bumpmap_preview)

        return panel


    def _create_title_bar(self): #vers 8
        """Create title bar with 14px button text"""
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Menu on far left
        menu_bar = self._create_menu_bar()
        menu_bar.setFixedWidth(50)
        layout.addWidget(menu_bar)

        # Title in center
        title_label = QLabel(f"🗺️ {self.texture_data.get('name', 'Unknown')}")
        title_label.setObjectName("title_label")
        title_label.setFont(self.panel_font)
        title_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, stretch=1)

        # Right side buttons
        button_width = 90
        button_height = 30

        # Add button
        add_btn = QPushButton("+ Add")
        add_btn.setFixedSize(button_width, button_height)
        add_btn.clicked.connect(self._generate_bumpmap)
        add_btn.setToolTip("Generate bumpmap (F9)")
        add_btn.setFont(self.button_font)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 1px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)

        layout.addWidget(add_btn)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedSize(button_width, button_height)
        delete_btn.clicked.connect(self._delete_bumpmap)
        delete_btn.setEnabled(self._has_bumpmap())
        delete_btn.setToolTip("Remove bumpmap (F11)")
        delete_btn.setFont(self.button_font)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: #e0e0e0;
                border: 1px solid #d43b2c;
                border-radius: 1px;
            }
        """)
        layout.addWidget(delete_btn)

        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.setFixedSize(button_width, button_height)
        apply_btn.clicked.connect(self._apply_changes)
        apply_btn.setToolTip("Apply changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: 1px solid #106ebe;
                border-radius: 1px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1984d8;
            }
        """)
        layout.addWidget(apply_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(button_width, button_height)
        close_btn.clicked.connect(self.close)
        close_btn.setToolTip("Close window")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 1px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c42b1c;
                color: white;
            }
        """)
        layout.addWidget(close_btn)

        return title_bar


    def _create_menu_bar(self): #vers 3
        """Create compact menu bar for embedding in title bar"""
        from PyQt6.QtWidgets import QMenuBar
        from PyQt6.QtGui import QAction, QKeySequence

        menu_bar = QMenuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 14px;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
            }
            QMenu::item {
                padding: 5px 25px 5px 14px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        # Add (Generate) - F9
        add_action = QAction("Add (Generate Bumpmap)", self)
        add_action.setShortcut(QKeySequence(Qt.Key.Key_F9))
        add_action.triggered.connect(self._generate_bumpmap)
        edit_menu.addAction(add_action)

        # Change (Import/Replace) - F10
        change_action = QAction("Change (Import/Replace)", self)
        change_action.setShortcut(QKeySequence(Qt.Key.Key_F10))
        change_action.triggered.connect(self._import_bumpmap)
        edit_menu.addAction(change_action)

        # Delete - F11
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence(Qt.Key.Key_F11))
        delete_action.triggered.connect(self._delete_bumpmap)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        # Export
        export_action = QAction("Export Bumpmap...", self)
        export_action.triggered.connect(self._export_bumpmap)
        edit_menu.addAction(export_action)

        return menu_bar


    def _apply_changes(self): #vers 3
        """Apply changes and ensure parent workshop is fully updated"""
        if not self.modified:
            self.close()
            return

        try:
            # Mark parent as modified
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            # Find and update the texture in parent's texture list
            if hasattr(self.parent_workshop, 'texture_list'):
                texture_name = self.texture_data.get('name', '')
                for i, tex in enumerate(self.parent_workshop.texture_list):
                    if tex.get('name') == texture_name:
                        # Copy all bumpmap-related data back
                        if 'bumpmap_data' in self.texture_data:
                            tex['bumpmap_data'] = self.texture_data['bumpmap_data']
                            tex['has_bumpmap'] = True
                            tex['bumpmap_type'] = self.texture_data.get('bumpmap_type', 0)
                            tex['raster_format_flags'] = self.texture_data.get('raster_format_flags', 0) | 0x10
                        else:
                            # Remove bumpmap if deleted
                            if 'bumpmap_data' in tex:
                                del tex['bumpmap_data']
                            tex['has_bumpmap'] = False
                            tex['raster_format_flags'] = self.texture_data.get('raster_format_flags', 0) & ~0x10
                        break

            # Update selected texture if it's the current one
            if hasattr(self.parent_workshop, 'selected_texture'):
                if self.parent_workshop.selected_texture and \
                self.parent_workshop.selected_texture.get('name') == self.texture_data.get('name'):

                    # Copy bumpmap data to selected texture
                    if 'bumpmap_data' in self.texture_data:
                        self.parent_workshop.selected_texture['bumpmap_data'] = self.texture_data['bumpmap_data']
                        self.parent_workshop.selected_texture['has_bumpmap'] = True
                        self.parent_workshop.selected_texture['bumpmap_type'] = self.texture_data.get('bumpmap_type', 0)
                        self.parent_workshop.selected_texture['raster_format_flags'] = \
                            self.texture_data.get('raster_format_flags', 0) | 0x10
                    else:
                        if 'bumpmap_data' in self.parent_workshop.selected_texture:
                            del self.parent_workshop.selected_texture['bumpmap_data']
                        self.parent_workshop.selected_texture['has_bumpmap'] = False
                        self.parent_workshop.selected_texture['raster_format_flags'] = \
                            self.texture_data.get('raster_format_flags', 0) & ~0x10

                    # Force UI update
                    if hasattr(self.parent_workshop, '_update_texture_info'):
                        self.parent_workshop._update_texture_info(self.parent_workshop.selected_texture)

            # Log message
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Bumpmap changes applied")

            # Reset modified flag
            self.modified = False

            QMessageBox.information(self, "Success", "Changes applied to texture")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply changes:\n{str(e)}")


    def _has_bumpmap(self): #vers 1
        """Check if texture has bumpmap"""
        if 'bumpmap_data' in self.texture_data or self.texture_data.get('has_bumpmap', False):
            return True
        if 'raster_format_flags' in self.texture_data:
            return bool(self.texture_data.get('raster_format_flags', 0) & 0x10)
        return False


    def _update_bumpmap_preview(self): #vers 2
        """Update bumpmap preview display"""
        # Safety check - make sure widget exists
        if not hasattr(self, 'bumpmap_preview'):
            return

        try:
            if 'bumpmap_data' in self.texture_data:
                # Decode bumpmap data
                if hasattr(self.parent_workshop, '_decode_bumpmap'):
                    bumpmap_image = self.parent_workshop._decode_bumpmap(
                        self.texture_data['bumpmap_data']
                    )

                    # Convert grayscale to RGB for proper display
                    if bumpmap_image.format() == QImage.Format.Format_Grayscale8:
                        bumpmap_image = bumpmap_image.convertToFormat(QImage.Format.Format_RGB888)

                    pixmap = QPixmap.fromImage(bumpmap_image)
                    self.bumpmap_preview.setPixmap(
                        pixmap.scaled(280, 280,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                    )
            else:
                self.bumpmap_preview.setText("No bumpmap data")
        except Exception as e:
            self.bumpmap_preview.setText(f"Preview error:\n{str(e)}")


    def _add_new_texture(self): #vers 2
        """F9 - Generate bumpmap from texture"""
        self._generate_bumpmap()

    def _replace_bumpmap(self): #vers 2
        """F10 - Import/Replace bumpmap"""
        self._import_bumpmap()

    def _generate_bumpmap(self): #vers 2
        """Generate bumpmap from texture"""
        if hasattr(self.parent_workshop, '_generate_bumpmap_from_texture'):
            # Temporarily set selected texture
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data

            # Generate
            self.parent_workshop._generate_bumpmap_from_texture()

            # Copy bumpmap data back to our texture_data
            if 'bumpmap_data' in self.parent_workshop.selected_texture:
                self.texture_data['bumpmap_data'] = self.parent_workshop.selected_texture['bumpmap_data']
                self.texture_data['bumpmap_type'] = self.parent_workshop.selected_texture.get('bumpmap_type', 0)
                self.texture_data['has_bumpmap'] = True
                self.texture_data['raster_format_flags'] = \
                    self.parent_workshop.selected_texture.get('raster_format_flags', 0)

            # Restore selection
            self.parent_workshop.selected_texture = old_selection

            # Update preview
            self._update_bumpmap_preview()
            self.modified = True

    def _import_bumpmap(self): #vers 1
        """Import bumpmap from file"""
        if hasattr(self.parent_workshop, '_import_bumpmap'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data

            self.parent_workshop._import_bumpmap()

            self.parent_workshop.selected_texture = old_selection

            self._update_bumpmap_preview()
            self.modified = True

    def _export_bumpmap(self): #vers 1
        """Export bumpmap to file"""
        if not self._has_bumpmap():
            QMessageBox.warning(self, "No Bumpmap", "This texture has no bumpmap to export")
            return

        if hasattr(self.parent_workshop, '_export_bumpmap'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data

            self.parent_workshop._export_bumpmap()

            self.parent_workshop.selected_texture = old_selection

    def _delete_bumpmap(self): #vers 1
        """F11 - Delete bumpmap"""
        if not self._has_bumpmap():
            QMessageBox.information(self, "No Bumpmap", "This texture has no bumpmap")
            return

        reply = QMessageBox.question(
            self, "Delete Bumpmap",
            "Remove bumpmap from this texture?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove bumpmap
            if 'bumpmap_data' in self.texture_data:
                del self.texture_data['bumpmap_data']
            self.texture_data['has_bumpmap'] = False

            if 'raster_format_flags' in self.texture_data:
                self.texture_data['raster_format_flags'] &= ~0x10

            # Update preview
            self.bumpmap_preview.setText("No bumpmap data\n\nPress F9 or use Edit → Generate Bumpmap")
            self.modified = True

            # Mark parent as modified
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            QMessageBox.information(self, "Success", "Bumpmap deleted")

    def _toggle_maximize(self): #vers 1
        """Toggle window maximize"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _create_add_icon(self): #vers 1
        """Create add icon"""
        if hasattr(self.parent_workshop, '_create_add_icon'):
            return self.parent_workshop._create_add_icon()
        return QIcon()

    def _create_import_icon(self): #vers 1
        """Create import icon"""
        if hasattr(self.parent_workshop, '_create_import_icon'):
            return self.parent_workshop._create_import_icon()
        return QIcon()

    def _create_export_icon(self): #vers 1
        """Create export icon"""
        if hasattr(self.parent_workshop, '_create_export_icon'):
            return self.parent_workshop._create_export_icon()
        return QIcon()

    def _create_delete_icon(self): #vers 1
        """Create delete icon"""
        if hasattr(self.parent_workshop, '_create_delete_icon'):
            return self.parent_workshop._create_delete_icon()
        return QIcon()


    def _create_reflection_panel(self): #vers 2
        """Create panel for reflection map display and generation - WITH IMPORT"""
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox
        from PyQt6.QtCore import Qt

        panel = QGroupBox("Reflection Maps    .")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Info label
        info = QLabel("Generate from normal map\nor import existing maps")
        info.setFont(self.panel_font)
        info.setStyleSheet("color: #888; line-height: 1.4;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Reflection preview
        reflection_label = QLabel("Reflection Vector Map")
        reflection_label.setFont(self.panel_font)
        reflection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(reflection_label)

        self.reflection_preview = QLabel()
        self.reflection_preview.setMinimumSize(150, 150)
        self.reflection_preview.setMaximumSize(150, 150)
        self.reflection_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reflection_preview.setStyleSheet(
            "border: 1px solid #3a3a3a; background: #1e1e1e;"
        )
        self.reflection_preview.setText("No data")
        self.reflection_preview.setFont(self.panel_font)
        layout.addWidget(self.reflection_preview)

        # Fresnel preview
        fresnel_label = QLabel("Fresnel Reflectivity")
        fresnel_label.setFont(self.panel_font)
        fresnel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(fresnel_label)

        self.fresnel_preview = QLabel()
        self.fresnel_preview.setMinimumSize(150, 150)
        self.fresnel_preview.setMaximumSize(150, 150)
        self.fresnel_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fresnel_preview.setStyleSheet(
            "border: 1px solid #3a3a3a; background: #1e1e1e;"
        )
        self.fresnel_preview.setText("No data")
        self.fresnel_preview.setFont(self.panel_font)
        layout.addWidget(self.fresnel_preview)

        # Buttons
        button_layout = QHBoxLayout()

        generate_btn = QPushButton("Generate")
        generate_btn.setFont(self.button_font)
        generate_btn.setToolTip("Generate from RGB normal map")
        generate_btn.clicked.connect(self._generate_reflection_maps)
        button_layout.addWidget(generate_btn)

        layout.addLayout(button_layout) #moved and fixed

        # ADD IMPORT BUTTON
        import_btn = QPushButton("Import")
        import_btn.setFont(self.button_font)
        import_btn.setToolTip("Import reflection maps from files")
        import_btn.clicked.connect(self._import_reflection_maps)
        button_layout.addWidget(import_btn)

        # Export button (separate row)
        export_btn = QPushButton("Export")
        export_btn.setFont(self.button_font)
        export_btn.setToolTip("Export reflection maps to PNG files")
        export_btn.clicked.connect(self._export_reflection_maps)
        layout.addWidget(export_btn)

        layout.addStretch()

        return panel


    def _load_settings(self): #vers 1
        """Load settings from config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'txd_workshop_settings.json'
        )

        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.save_to_source_location = settings.get('save_to_source_location', True)
                    self.last_save_directory = settings.get('last_save_directory', None)
        except Exception as e:
            print(f"Failed to load settings: {e}")


    def _save_settings(self): #vers 1
        """Save settings to config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'txd_workshop_settings.json'
        )

        try:
            settings = {
                'save_to_source_location': self.save_to_source_location,
                'last_save_directory': self.last_save_directory
            }

            with open(settings_file, 'w') as f:
                json.dump(settings, indent=2, fp=f)
        except Exception as e:
            print(f"Failed to save settings: {e}")


    def _import_reflection_maps(self): #vers 1
        """Import reflection and Fresnel maps from files"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtGui import QImage

        try:
            # Get reflection map file
            reflection_path, _ = QFileDialog.getOpenFileName(
                self, "Import Reflection Vector Map",
                "",
                "Image Files (*.png *.jpg *.bmp);;All Files (*)"
            )

            if not reflection_path:
                return

            # Get Fresnel map file
            fresnel_path, _ = QFileDialog.getOpenFileName(
                self, "Import Fresnel Reflectivity Map",
                "",
                "Image Files (*.png *.jpg *.bmp);;All Files (*)"
            )

            if not fresnel_path:
                return

            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)

            # Load reflection map (RGB)
            reflection_img = QImage(reflection_path)
            if reflection_img.isNull():
                QMessageBox.warning(self, "Error", "Failed to load reflection map")
                return

            # Scale to texture size if needed
            if reflection_img.width() != width or reflection_img.height() != height:
                reflection_img = reflection_img.scaled(
                    width, height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            # Convert to RGB888
            reflection_img = reflection_img.convertToFormat(QImage.Format.Format_RGB888)
            reflection_data = reflection_img.bits().asstring(reflection_img.sizeInBytes())

            # Load Fresnel map (Grayscale)
            fresnel_img = QImage(fresnel_path)
            if fresnel_img.isNull():
                QMessageBox.warning(self, "Error", "Failed to load Fresnel map")
                return

            # Scale to texture size if needed
            if fresnel_img.width() != width or fresnel_img.height() != height:
                fresnel_img = fresnel_img.scaled(
                    width, height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            # Convert to grayscale
            fresnel_img = fresnel_img.convertToFormat(QImage.Format.Format_Grayscale8)
            fresnel_data = fresnel_img.bits().asstring(fresnel_img.sizeInBytes())

            # Store in texture data
            self.texture_data['reflection_map'] = reflection_data
            self.texture_data['fresnel_map'] = fresnel_data
            self.texture_data['has_reflection'] = True

            # Update previews
            self._update_reflection_previews()

            self.modified = True

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Imported reflection maps")

            QMessageBox.information(self, "Success", "Reflection maps imported successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import:\n{str(e)}")


    def _update_reflection_previews(self): #vers 1
        """Update reflection and Fresnel map previews"""
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt

        try:
            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)

            # Update reflection map preview
            if 'reflection_map' in self.texture_data:
                reflection_data = self.texture_data['reflection_map']

                # Convert to numpy for QImage
                reflection_arr = np.frombuffer(reflection_data, dtype=np.uint8)
                reflection_arr = reflection_arr.reshape((height, width, 3))

                img = self._convert_numpy_to_qimage(
                    reflection_arr, width, height, is_grayscale=False
                )

                if img:
                    pixmap = QPixmap.fromImage(img)
                    self.reflection_preview.setPixmap(
                        pixmap.scaled(200, 200,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                    )

            # Update Fresnel map preview
            if 'fresnel_map' in self.texture_data:
                fresnel_data = self.texture_data['fresnel_map']

                # Convert to numpy for QImage
                fresnel_arr = np.frombuffer(fresnel_data, dtype=np.uint8)
                fresnel_arr = fresnel_arr.reshape((height, width))

                img = self._convert_numpy_to_qimage(
                    fresnel_arr, width, height, is_grayscale=True
                )

                if img:
                    pixmap = QPixmap.fromImage(img)
                    self.fresnel_preview.setPixmap(
                        pixmap.scaled(200, 200,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                    )

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Preview update error: {str(e)}")


    def _generate_reflection_maps(self): #vers 1
        """Generate reflection and Fresnel maps from normal map data"""
        from PyQt6.QtWidgets import QMessageBox, QInputDialog
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt

        try:
            # Check if we have normal map data
            bumpmap_data = self.texture_data.get('bumpmap_data')
            if not bumpmap_data:
                QMessageBox.warning(self, "No Normal Map",
                    "Generate or import a normal map first")
                return

            # Check if it's RGB normal map
            bumpmap_type = self.texture_data.get('bumpmap_type', 0)
            if bumpmap_type == 0:  # Grayscale height map
                QMessageBox.information(self, "Info",
                    "Reflection maps require RGB normal map.\n"
                    "Current bumpmap is grayscale height map.")
                return

            # Check if numpy is available
            try:
                import numpy as np
            except ImportError:
                QMessageBox.warning(self, "Missing Dependency",
                    "Reflection map generation requires numpy.\n\n"
                    "Install with: pip install numpy")
                return

            # Get F0 value from user
            F0, ok = QInputDialog.getDouble(
                self, "Fresnel Reflectivity",
                "Base reflectivity (F0):\n"
                "0.04 = Dielectric (glass, plastic)\n"
                "0.5-1.0 = Metal",
                0.04, 0.01, 1.0, 2
            )
            if not ok:
                return

            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)

            # Extract normal map data
            if bumpmap_type == 1:  # RGB normal map
                normal_data = bumpmap_data
            elif bumpmap_type == 2:  # Both
                # Skip first byte (type identifier) and grayscale data
                normal_data = bumpmap_data[1 + width * height:]
            else:
                QMessageBox.warning(self, "Error", "Unknown bumpmap type")
                return

            # Generate reflection maps using parent workshop methods
            if hasattr(self.parent_workshop, '_generate_reflection_from_normal'):
                result = self.parent_workshop._generate_reflection_from_normal(
                    normal_data, width, height, auto_flip=True, F0=F0
                )

                if result:
                    # Store in texture data
                    self.texture_data['reflection_map'] = result['reflection_map']
                    self.texture_data['fresnel_map'] = result['fresnel_map']
                    self.texture_data['has_reflection'] = True

                    # Update previews
                    self._update_reflection_previews()

                    self.modified = True

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        flip_msg = " (Y-axis corrected)" if result['y_flipped'] else ""
                        self.main_window.log_message(
                            f"✅ Generated reflection maps{flip_msg}"
                        )

                    QMessageBox.information(self, "Success",
                        f"Generated reflection maps\nF0: {F0}")
            else:
                QMessageBox.warning(self, "Error",
                    "Reflection generation method not available.\n"
                    "Make sure TXDWorkshop has reflection methods.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate:\n{str(e)}")


    def _export_reflection_maps(self): #vers 1
        """Export reflection and Fresnel maps as PNG files"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PIL import Image
        import os

        try:
            if 'reflection_map' not in self.texture_data:
                QMessageBox.warning(self, "No Data", "No reflection maps to export")
                return

            # Get output directory
            output_dir = QFileDialog.getExistingDirectory(
                self, "Select Output Directory"
            )
            if not output_dir:
                return

            texture_name = self.texture_data.get('name', 'texture')
            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)

            exported = []

            # Export reflection map
            if 'reflection_map' in self.texture_data:
                reflection_arr = np.frombuffer(
                    self.texture_data['reflection_map'], dtype=np.uint8
                )
                reflection_arr = reflection_arr.reshape((height, width, 3))

                img = Image.fromarray(reflection_arr, mode='RGB')
                path = os.path.join(output_dir, f"{texture_name}_reflection.png")
                img.save(path)
                exported.append("reflection_vector_map.png")

            # Export Fresnel map
            if 'fresnel_map' in self.texture_data:
                fresnel_arr = np.frombuffer(
                    self.texture_data['fresnel_map'], dtype=np.uint8
                )
                fresnel_arr = fresnel_arr.reshape((height, width))

                img = Image.fromarray(fresnel_arr, mode='L')
                path = os.path.join(output_dir, f"{texture_name}_fresnel.png")
                img.save(path)
                exported.append("fresnel_reflectivity.png")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"✅ Exported {len(exported)} maps to: {output_dir}"
                )

            QMessageBox.information(self, "Success",
                f"Exported {len(exported)} maps:\n" + "\n".join(exported))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")


    def _generate_reflection_from_normal(self, normal_data, width, height, auto_flip=True, F0=0.04): #vers 1
        """
        Generate reflection and Fresnel maps from normal map data

        """
        try:
            # Convert bytes to numpy array
            normal_arr = np.frombuffer(normal_data, dtype=np.uint8)
            normal_arr = normal_arr.reshape((height, width, 3))

            # Convert to float [0, 1]
            normal_float = normal_arr.astype(np.float32) / 255.0

            # Auto-detect Y flip if requested
            y_flipped = False
            if auto_flip and self._detect_y_flip(normal_float):
                normal_float[:, :, 1] = 1.0 - normal_float[:, :, 1]
                y_flipped = True

            # Convert back to uint8
            normal_arr = (normal_float * 255.0).astype(np.uint8)

            # Generate reflection and Fresnel maps
            reflection, fresnel = self._normal_to_reflection(normal_arr, F0=F0)

            return {
                'reflection_map': reflection.tobytes(),
                'fresnel_map': fresnel.tobytes(),
                'y_flipped': y_flipped
            }

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Reflection generation error: {str(e)}")
            return None


    def _generate_all_maps_from_texture(self, rgba_data, width, height, F0=0.04): #vers 1
        """
        Generate complete set of maps from texture:
        """
        try:
            # Convert RGBA to grayscale for height map
            grayscale = bytearray(width * height)
            for i in range(0, len(rgba_data), 4):
                r, g, b = rgba_data[i:i+3]
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                grayscale[i // 4] = gray

            # Generate normal map from grayscale
            normal_map = self._generate_rgb_normal_map(grayscale, width, height, strength=1.0)

            # Generate bump map (height map)
            bump_map = self._sobel_filter(grayscale, width, height, strength=1.0)

            # Generate reflection and Fresnel from normal map
            reflection_fresnel = self._generate_reflection_from_normal(
                normal_map, width, height, auto_flip=True, F0=F0
            )

            if reflection_fresnel:
                return {
                    'bump_map': bytes(bump_map),
                    'normal_map': normal_map,
                    'reflection_map': reflection_fresnel['reflection_map'],
                    'fresnel_map': reflection_fresnel['fresnel_map']
                }
            else:
                return None

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Map generation error: {str(e)}")
            return None


    def _convert_numpy_to_qimage(self, numpy_array, width, height, is_grayscale=False): #vers 1
        """Convert numpy array to QImage for preview"""
        try:
            if is_grayscale:
                # Grayscale image
                img = QImage(numpy_array.tobytes(), width, height, width,
                            QImage.Format.Format_Grayscale8)
            else:
                # RGB image
                img = QImage(numpy_array.tobytes(), width, height, width * 3,
                            QImage.Format.Format_RGB888)
            return img
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Image conversion error: {str(e)}")
            return None


    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for window dragging"""
        from PyQt6.QtCore import Qt

        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on resize corner
            corner = self._get_resize_corner(event.pos())
            if corner:
                self.resizing = True
                self.resize_corner = corner
                self.drag_position = event.globalPosition().toPoint()
            # Check if clicking on title bar for dragging
            elif event.pos().y() < 35:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()


    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse move for window dragging/resizing"""
        from PyQt6.QtCore import Qt, QRect
        from PyQt6.QtGui import QCursor

        if self.resizing and self.resize_corner:
            # Handle resizing
            delta = event.globalPosition().toPoint() - self.drag_position
            self.drag_position = event.globalPosition().toPoint()

            rect = self.geometry()

            if self.resize_corner == 'bottom_right':
                rect.setBottomRight(rect.bottomRight() + delta)
            elif self.resize_corner == 'bottom_left':
                rect.setBottomLeft(rect.bottomLeft() + delta)
            elif self.resize_corner == 'top_right':
                rect.setTopRight(rect.topRight() + delta)
            elif self.resize_corner == 'top_left':
                rect.setTopLeft(rect.topLeft() + delta)

            # Enforce minimum size
            if rect.width() >= 900 and rect.height() >= 400:
                self.setGeometry(rect)

        elif self.dragging:
            # Handle window dragging
            self.move(event.globalPosition().toPoint() - self.drag_position)

        else:
            # Update cursor based on corner hover
            corner = self._get_resize_corner(event.pos())
            if corner:
                if corner in ['top_left', 'bottom_right']:
                    self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                else:
                    self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        from PyQt6.QtCore import Qt

        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None


    def _get_resize_corner(self, pos): #vers 1
        """Determine which corner (if any) the mouse is over"""
        rect = self.rect()
        corner_size = self.corner_size

        # Bottom right
        if (rect.width() - corner_size <= pos.x() <= rect.width() and
            rect.height() - corner_size <= pos.y() <= rect.height()):
            return 'bottom_right'

        # Bottom left
        if (0 <= pos.x() <= corner_size and
            rect.height() - corner_size <= pos.y() <= rect.height()):
            return 'bottom_left'

        # Top right
        if (rect.width() - corner_size <= pos.x() <= rect.width() and
            0 <= pos.y() <= corner_size):
            return 'top_right'

        # Top left
        if (0 <= pos.x() <= corner_size and
            0 <= pos.y() <= corner_size):
            return 'top_left'

        return None


    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line icon"""
        if hasattr(self.parent_workshop, '_create_minimize_icon'):
            return self.parent_workshop._create_minimize_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>''')

    def _create_maximize_icon(self): #vers 1
        """Maximize - Square icon"""
        if hasattr(self.parent_workshop, '_create_maximize_icon'):
            return self.parent_workshop._create_maximize_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>''')

    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        if hasattr(self.parent_workshop, '_create_close_icon'):
            return self.parent_workshop._create_close_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <line x1="6" y1="6" x2="18" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="18" y1="6" x2="6" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>''')

    def _create_add_icon(self): #vers 1
        """Add - Plus icon"""
        if hasattr(self.parent_workshop, '_create_add_icon'):
            return self.parent_workshop._create_add_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>''')

    def _create_delete_icon(self): #vers 1
        """Delete - Trash icon"""
        if hasattr(self.parent_workshop, '_create_delete_icon'):
            return self.parent_workshop._create_delete_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''')

    def _create_import_icon(self): #vers 1
        """Import - Download arrow icon"""
        if hasattr(self.parent_workshop, '_create_import_icon'):
            return self.parent_workshop._create_import_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>''')

    def _create_export_icon(self): #vers 1
        """Export - Upload arrow icon"""
        if hasattr(self.parent_workshop, '_create_export_icon'):
            return self.parent_workshop._create_export_icon()
        return self._svg_to_icon(b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>''')

    def _svg_to_icon(self, svg_data, size=24): #vers 1
        """Convert SVG data to QIcon - Helper method for all icon creation"""
        try:
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtGui import QPixmap, QPainter, QIcon
            from PyQt6.QtCore import Qt

            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            renderer = QSvgRenderer(svg_data)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except Exception as e:
            # Fallback to empty icon if SVG fails
            return QIcon()


    def _apply_changes(self): #vers 1
        """Apply changes to parent workshop without closing window"""
        if self.modified:
            # Mark parent as modified
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            # Update parent texture info
            if hasattr(self.parent_workshop, '_update_texture_info'):
                self.parent_workshop._update_texture_info(self.texture_data)

            # Log message
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Bumpmap changes applied")

            # Reset modified flag
            self.modified = False

            QMessageBox.information(self, "Success", "Changes applied to texture")


    def closeEvent(self, event): #vers 1
        """Handle window close event"""

        # Save settings before closing
        self._save_settings()

        if self.modified:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Apply changes before closing?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._apply_changes()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()



class MipmapManagerWindow(QWidget): #vers 2
    """Mipmap Manager - Modern card-based design matching mockup"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified_levels = {}  # Track modified levels

        texture_name = texture_data.get('name', 'Unknown')
        width = texture_data.get('width', 0)
        height = texture_data.get('height', 0)
        fmt = texture_data.get('format', 'Unknown')

        self.setWindowTitle(f"Mipmap Manager - {texture_name}")
        self.resize(900, 700)

        # Frameless window with custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setup_ui()

        # Enable dragging
        self.dragging = False
        self.drag_position = None


    def setup_ui(self): #vers 2
        """Setup modern UI matching mockup"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)

        # Toolbar with Apply/Close buttons
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #2b2b2b;
                border: none;
            }
        """)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(15)

        # Create level cards
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Bottom status bar
        #bottom_bar = self._create_bottom_bar()
        #layout.addWidget(bottom_bar)


    def _create_title_bar(self): #vers 1
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        title_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        title_bar.setFixedHeight(40)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Title text
        texture_name = self.texture_data.get('name', 'Unknown')
        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)
        fmt = self.texture_data.get('format', 'Unknown')

        title_label = QLabel(f"Mipmap Manager - {texture_name} ({width}x{height}, {fmt})")
        title_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Drag handle
        drag_btn = QPushButton("☰")
        drag_btn.setFixedSize(30, 30)
        drag_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        drag_btn.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(drag_btn)

        return title_bar

    def _create_toolbar(self): #vers 5
        """Create toolbar with action buttons AND Apply/Close"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background: #252525;
                border-bottom: 1px solid #3a3a3a;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        toolbar.setFixedHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Left side - Action buttons
        autogen_btn = QPushButton("🔄 Auto-Generate")
        autogen_btn.setToolTip("Generate all mipmap levels")
        autogen_btn.clicked.connect(self._auto_generate_mipmaps)
        layout.addWidget(autogen_btn)

        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.setToolTip("Export all levels as PNG")
        export_all_btn.clicked.connect(self._export_all_levels)
        layout.addWidget(export_all_btn)

        import_all_btn = QPushButton("📥 Import All")
        import_all_btn.setToolTip("Import levels from PNG files")
        import_all_btn.clicked.connect(self._import_all_levels)
        layout.addWidget(import_all_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setToolTip("Remove all mipmap levels except Level 0")
        clear_btn.clicked.connect(self._clear_all_levels)
        layout.addWidget(clear_btn)

        layout.addStretch()

        # Right side - Apply/Close buttons
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0d47a1;
                border-color: #1976d2;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        """)
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return toolbar


    def _create_level_card(self, level_data): #vers 2
        """Create modern level card matching mockup"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QFrame:hover {
                border-color: #4a6fa5;
                background: #252525;
            }
        """)
        card.setMinimumHeight(140)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Preview thumbnail
        preview_widget = self._create_preview_widget(level_data)
        layout.addWidget(preview_widget)

        # Level info section
        info_section = self._create_info_section(level_data)
        layout.addWidget(info_section, stretch=1)

        # Action buttons
        action_section = self._create_action_section(level_data)
        layout.addWidget(action_section)

        return card


    def _create_preview_widget(self, level_data): #vers 1
        """Create preview thumbnail with checkerboard"""
        level_num = level_data.get('level', 0)
        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        rgba_data = level_data.get('rgba_data')

        # Scale preview size based on level
        preview_size = max(45, 120 - (level_num * 15))

        preview = QLabel()
        preview.setFixedSize(preview_size, preview_size)
        preview.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 2px solid #3a3a3a;
                border-radius: 3px;
            }
        """)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if rgba_data and width > 0:
            try:
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    scaled_pixmap = pixmap.scaled(
                        preview_size - 10, preview_size - 10,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    preview.setPixmap(scaled_pixmap)
            except:
                preview.setText("🖼️")
        else:
            preview.setText("🖼️")

        return preview


    def _create_info_section(self, level_data): #vers 1
        """Create info section with stats grid"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with level number and dimensions
        header_layout = QHBoxLayout()

        level_num = level_data.get('level', 0)
        level_badge = QLabel(f"Level {level_num}")
        level_badge.setStyleSheet("""
            QLabel {
                background: #0d47a1;
                color: white;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        header_layout.addWidget(level_badge)

        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        dim_label = QLabel(f"{width} x {height}")
        dim_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a9eff;")
        header_layout.addWidget(dim_label)

        # Main texture indicator
        if level_num == 0:
            main_badge = QLabel("● Main Texture")
            main_badge.setStyleSheet("color: #4caf50; font-size: 12px;")
            header_layout.addWidget(main_badge)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Stats grid
        stats_grid = self._create_stats_grid(level_data)
        layout.addWidget(stats_grid)

        return info_widget


    def _create_stats_grid(self, level_data): #vers 1
        """Create stats grid"""
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)

        fmt = level_data.get('format', self.texture_data.get('format', 'Unknown'))
        size = level_data.get('compressed_size', 0)
        size_kb = size / 1024

        # Format stat
        format_stat = self._create_stat_box("Format:", fmt)
        grid_layout.addWidget(format_stat)

        # Size stat
        size_stat = self._create_stat_box("Size:", f"{size_kb:.1f} KB")
        grid_layout.addWidget(size_stat)

        # Compression stat
        if 'DXT' in fmt:
            ratio = "4:1" if 'DXT5' in fmt or 'DXT3' in fmt else "6:1"
            comp_stat = self._create_stat_box("Compression:", ratio)
        else:
            comp_stat = self._create_stat_box("Compression:", "None")
        grid_layout.addWidget(comp_stat)

        # Status stat
        is_modified = level_data.get('level', 0) in self.modified_levels
        status_text = "⚠ Modified" if is_modified else "✓ Valid"
        status_color = "#ff9800" if is_modified else "#4caf50"
        status_stat = self._create_stat_box("Status:", status_text, status_color)
        grid_layout.addWidget(status_stat)

        return grid_widget


    def _create_stat_box(self, label, value, value_color="#e0e0e0"): #vers 1
        """Create individual stat box"""
        stat = QFrame()
        stat.setStyleSheet("""
            QFrame {
                background: #252525;
                border-radius: 3px;
                padding: 6px 10px;
            }
        """)

        layout = QHBoxLayout(stat)
        layout.setContentsMargins(8, 4, 8, 4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {value_color}; font-weight: bold; font-size: 12px;")
        layout.addWidget(value_widget)

        return stat


    def _create_action_section(self, level_data): #vers 1
        """Create action buttons section"""
        action_widget = QWidget()
        layout = QVBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        level_num = level_data.get('level', 0)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2e5d2e;
                border: 1px solid #3d7d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #3d7d3d;
            }
        """)
        export_btn.clicked.connect(lambda: self._export_level(level_num))
        layout.addWidget(export_btn)

        # Import button
        import_btn = QPushButton("Import")
        import_btn.setStyleSheet("""
            QPushButton {
                background: #5d3d2e;
                border: 1px solid #7d4d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7d4d3d;
            }
        """)
        import_btn.clicked.connect(lambda: self._import_level(level_num))
        layout.addWidget(import_btn)

        # Delete button (not for level 0) or Edit button (for level 0)
        if level_num == 0:
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    border: 1px solid #4a4a4a;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                }
            """)
            edit_btn.clicked.connect(self._edit_main_texture)
            layout.addWidget(edit_btn)
        else:
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #5d2e2e;
                    border: 1px solid #7d3d3d;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #7d3d3d;
                }
            """)
            delete_btn.clicked.connect(lambda: self._delete_level(level_num))
            layout.addWidget(delete_btn)

        return action_widget


    def _create_bottom_bar(self): #vers 1
        """Create bottom status bar"""
        bottom_bar = QFrame()
        bottom_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        bottom_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-top: 1px solid #3a3a3a;
            }
        """)
        bottom_bar.setFixedHeight(45)

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Left side - Stats
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_levels = len(mipmap_levels)
        total_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        total_size_kb = total_size / 1024

        stats_label = QLabel(f"Total Levels: {num_levels} | Total Size: {total_size_kb:.1f} KB")
        stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(stats_label)

        # Modified badge if there are changes
        if self.modified_levels:
            modified_badge = QLabel("● Modified")
            modified_badge.setStyleSheet("""
                QLabel {
                    background: #ff6b35;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-left: 10px;
                }
            """)
            layout.addWidget(modified_badge)

        layout.addStretch()

        return bottom_bar


    def mousePressEvent(self, event): #vers 1
        """Enable window dragging from title bar"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 40:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()


    def mouseMoveEvent(self, event): #vers 1
        """Handle window dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


    def mouseReleaseEvent(self, event): #vers 1
        """Stop dragging"""
        self.dragging = False


    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("🔄 Auto-generating mipmaps...")
        # Call parent's generate method
        if hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data
            self.parent_workshop._auto_generate_mipmaps()
            self.parent_workshop.selected_texture = old_selection
            # Refresh window
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _export_all_levels(self): #vers 1
        """Export all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📤 Exporting all mipmap levels...")

        from PyQt6.QtWidgets import QFileDialog
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        # Export logic here
        QMessageBox.information(self, "Export", "Mipmap export functionality coming soon!")


    def _import_all_levels(self): #vers 1
        """Import mipmap levels from files"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📥 Importing mipmap levels...")
        QMessageBox.information(self, "Import", "Mipmap import functionality coming soon!")


    def _clear_all_levels(self): #vers 1
        """Clear all mipmap levels except Level 0"""
        reply = QMessageBox.question(
            self, "Clear Mipmaps",
            "Remove all mipmap levels except Level 0?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if 'mipmap_levels' in self.texture_data:
                # Keep only level 0
                level_0 = next((l for l in self.texture_data['mipmap_levels'] if l.get('level') == 0), None)
                if level_0:
                    self.texture_data['mipmap_levels'] = [level_0]
                    self.texture_data['mipmaps'] = 1
                    self.close()
                    new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
                    new_window.show()


    def _export_level(self, level_num): #vers 1
        """Export single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📤 Exporting Level {level_num}...")


    def _import_level(self, level_num): #vers 1
        """Import single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📥 Importing Level {level_num}...")
        self.modified_levels[level_num] = True


    def _delete_level(self, level_num): #vers 1
        """Delete mipmap level"""
        reply = QMessageBox.question(
            self, "Delete Level",
            f"Delete Level {level_num}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.texture_data['mipmap_levels'] = [
                l for l in self.texture_data.get('mipmap_levels', [])
                if l.get('level') != level_num
            ]
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _edit_main_texture(self): #vers 1
        """Edit main texture"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("✏️ Editing main texture...")


    def _apply_changes(self): #vers 1
        """Apply all changes and close"""
        if self.modified_levels:
            # Update parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Mipmap changes applied")

        self.close()


class MipmapManagerWindow(QWidget): #vers 2
    """Mipmap Manager - Modern card-based design matching mockup"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified_levels = {}  # Track modified levels

        texture_name = texture_data.get('name', 'Unknown')
        width = texture_data.get('width', 0)
        height = texture_data.get('height', 0)
        fmt = texture_data.get('format', 'Unknown')

        self.setWindowTitle(f"Mipmap Manager - {texture_name}")
        self.resize(1080, 700)  # 20% wider (900 * 1.2 = 1080)

        # Frameless window with custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        self.setup_ui()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)


    def setup_ui(self): #vers 2
        """Setup modern UI matching mockup"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar with Apply/Close buttons
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #2b2b2b;
                border: none;
            }
        """)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(15)

        # Create level cards
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Bottom status bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar)
        # Title bar
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)


    def _create_title_bar(self): #vers 1
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        title_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        title_bar.setFixedHeight(40)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Title text
        texture_name = self.texture_data.get('name', 'Unknown')
        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)
        fmt = self.texture_data.get('format', 'Unknown')

        title_label = QLabel(f"Mipmap Manager - {texture_name} ({width}x{height}, {fmt})")
        title_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Drag handle
        drag_btn = QPushButton("☰")
        drag_btn.setFixedSize(30, 30)
        drag_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        drag_btn.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(drag_btn)

        return title_bar


    def _create_toolbar(self): #vers 2
        """Create toolbar with action buttons AND Apply/Close"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background: #252525;
                border-bottom: 1px solid #3a3a3a;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        toolbar.setFixedHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Left side - Action buttons
        autogen_btn = QPushButton("🔄 Auto-Generate")
        autogen_btn.setToolTip("Generate all mipmap levels")
        autogen_btn.clicked.connect(self._auto_generate_mipmaps)
        layout.addWidget(autogen_btn)

        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.setToolTip("Export all levels as PNG")
        export_all_btn.clicked.connect(self._export_all_levels)
        layout.addWidget(export_all_btn)

        import_all_btn = QPushButton("📥 Import All")
        import_all_btn.setToolTip("Import levels from PNG files")
        import_all_btn.clicked.connect(self._import_all_levels)
        layout.addWidget(import_all_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setToolTip("Remove all mipmap levels except Level 0")
        clear_btn.clicked.connect(self._clear_all_levels)
        layout.addWidget(clear_btn)

        layout.addStretch()

        # Right side - Apply/Close buttons
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0d47a1;
                border-color: #1976d2;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        """)
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return toolbar


    def _create_level_card(self, level_data): #vers 2
        """Create modern level card matching mockup"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QFrame:hover {
                border-color: #4a6fa5;
                background: #252525;
            }
        """)
        card.setMinimumHeight(140)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Preview thumbnail
        preview_widget = self._create_preview_widget(level_data)
        layout.addWidget(preview_widget)

        # Level info section
        info_section = self._create_info_section(level_data)
        layout.addWidget(info_section, stretch=1)

        # Action buttons
        action_section = self._create_action_section(level_data)
        layout.addWidget(action_section)

        return card


    def _create_preview_widget(self, level_data): #vers 1
        """Create preview thumbnail with checkerboard"""
        level_num = level_data.get('level', 0)
        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        rgba_data = level_data.get('rgba_data')

        # Scale preview size based on level
        preview_size = max(45, 120 - (level_num * 15))

        preview = QLabel()
        preview.setFixedSize(preview_size, preview_size)
        preview.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 2px solid #3a3a3a;
                border-radius: 3px;
            }
        """)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if rgba_data and width > 0:
            try:
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    scaled_pixmap = pixmap.scaled(
                        preview_size - 10, preview_size - 10,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    preview.setPixmap(scaled_pixmap)
            except:
                preview.setText("🖼️")
        else:
            preview.setText("🖼️")

        return preview


    def _create_info_section(self, level_data): #vers 1
        """Create info section with stats grid"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with level number and dimensions
        header_layout = QHBoxLayout()

        level_num = level_data.get('level', 0)
        level_badge = QLabel(f"Level {level_num}")
        level_badge.setStyleSheet("""
            QLabel {
                background: #0d47a1;
                color: white;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        header_layout.addWidget(level_badge)

        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        dim_label = QLabel(f"{width} x {height}")
        dim_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a9eff;")
        header_layout.addWidget(dim_label)

        # Main texture indicator
        if level_num == 0:
            main_badge = QLabel("● Main Texture")
            main_badge.setStyleSheet("color: #4caf50; font-size: 12px;")
            header_layout.addWidget(main_badge)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Stats grid
        stats_grid = self._create_stats_grid(level_data)
        layout.addWidget(stats_grid)

        return info_widget


    def _create_stats_grid(self, level_data): #vers 1
        """Create stats grid"""
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)

        fmt = level_data.get('format', self.texture_data.get('format', 'Unknown'))
        size = level_data.get('compressed_size', 0)
        size_kb = size / 1024

        # Format stat
        format_stat = self._create_stat_box("Format:", fmt)
        grid_layout.addWidget(format_stat)

        # Size stat
        size_stat = self._create_stat_box("Size:", f"{size_kb:.1f} KB")
        grid_layout.addWidget(size_stat)

        # Compression stat
        if 'DXT' in fmt:
            ratio = "4:1" if 'DXT5' in fmt or 'DXT3' in fmt else "6:1"
            comp_stat = self._create_stat_box("Compression:", ratio)
        else:
            comp_stat = self._create_stat_box("Compression:", "None")
        grid_layout.addWidget(comp_stat)

        # Status stat
        is_modified = level_data.get('level', 0) in self.modified_levels
        status_text = "⚠ Modified" if is_modified else "✓ Valid"
        status_color = "#ff9800" if is_modified else "#4caf50"
        status_stat = self._create_stat_box("Status:", status_text, status_color)
        grid_layout.addWidget(status_stat)

        return grid_widget


    def _create_stat_box(self, label, value, value_color="#e0e0e0"): #vers 1
        """Create individual stat box"""
        stat = QFrame()
        stat.setStyleSheet("""
            QFrame {
                background: #252525;
                border-radius: 3px;
                padding: 6px 10px;
            }
        """)

        layout = QHBoxLayout(stat)
        layout.setContentsMargins(8, 4, 8, 4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {value_color}; font-weight: bold; font-size: 12px;")
        layout.addWidget(value_widget)

        return stat


    def _create_action_section(self, level_data): #vers 1
        """Create action buttons section"""
        action_widget = QWidget()
        layout = QVBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        level_num = level_data.get('level', 0)

        # Export button
        export_btn = QPushButton("📤 Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2e5d2e;
                border: 1px solid #3d7d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #3d7d3d;
            }
        """)
        export_btn.clicked.connect(lambda: self._export_level(level_num))
        layout.addWidget(export_btn)

        # Import button
        import_btn = QPushButton("📥 Import")
        import_btn.setStyleSheet("""
            QPushButton {
                background: #5d3d2e;
                border: 1px solid #7d4d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7d4d3d;
            }
        """)
        import_btn.clicked.connect(lambda: self._import_level(level_num))
        layout.addWidget(import_btn)

        # Delete button (not for level 0) or Edit button (for level 0)
        if level_num == 0:
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    border: 1px solid #4a4a4a;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                }
            """)
            edit_btn.clicked.connect(self._edit_main_texture)
            layout.addWidget(edit_btn)
        else:
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #5d2e2e;
                    border: 1px solid #7d3d3d;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #7d3d3d;
                }
            """)
            delete_btn.clicked.connect(lambda: self._delete_level(level_num))
            layout.addWidget(delete_btn)

        return action_widget


    def _create_bottom_bar(self): #vers 1
        """Create bottom status bar"""
        bottom_bar = QFrame()
        bottom_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        bottom_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-top: 1px solid #3a3a3a;
            }
        """)
        bottom_bar.setFixedHeight(45)

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Left side - Stats
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_levels = len(mipmap_levels)
        total_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        total_size_kb = total_size / 1024

        stats_label = QLabel(f"Total Levels: {num_levels} | Total Size: {total_size_kb:.1f} KB")
        stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(stats_label)

        # Modified badge if there are changes
        if self.modified_levels:
            modified_badge = QLabel("● Modified")
            modified_badge.setStyleSheet("""
                QLabel {
                    background: #ff6b35;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-left: 10px;
                }
            """)
            layout.addWidget(modified_badge)

        layout.addStretch()

        return bottom_bar


    def mousePressEvent(self, event): #vers 1
        """Enable window dragging from title bar"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 40:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event): #vers 1
        """Handle window dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


    def mouseReleaseEvent(self, event): #vers 1
        """Stop dragging"""
        self.dragging = False


    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("🔄 Auto-generating mipmaps...")
        # Call parent's generate method
        if hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data
            self.parent_workshop._auto_generate_mipmaps()
            self.parent_workshop.selected_texture = old_selection
            # Refresh window
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _export_all_levels(self): #vers 1
        """Export all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📤 Exporting all mipmap levels...")

        from PyQt6.QtWidgets import QFileDialog
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        # Export logic here
        QMessageBox.information(self, "Export", "Mipmap export functionality coming soon!")


    def _import_all_levels(self): #vers 1
        """Import mipmap levels from files"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📥 Importing mipmap levels...")
        QMessageBox.information(self, "Import", "Mipmap import functionality coming soon!")


    def _clear_all_levels(self): #vers 1
        """Clear all mipmap levels except Level 0"""
        reply = QMessageBox.question(
            self, "Clear Mipmaps",
            "Remove all mipmap levels except Level 0?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if 'mipmap_levels' in self.texture_data:
                # Keep only level 0
                level_0 = next((l for l in self.texture_data['mipmap_levels'] if l.get('level') == 0), None)
                if level_0:
                    self.texture_data['mipmap_levels'] = [level_0]
                    self.texture_data['mipmaps'] = 1
                    self.close()
                    new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
                    new_window.show()


    def _export_level(self, level_num): #vers 1
        """Export single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📤 Exporting Level {level_num}...")


    def _import_level(self, level_num): #vers 1
        """Import single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📥 Importing Level {level_num}...")
        self.modified_levels[level_num] = True


    def _delete_level(self, level_num): #vers 1
        """Delete mipmap level"""
        reply = QMessageBox.question(
            self, "Delete Level",
            f"Delete Level {level_num}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.texture_data['mipmap_levels'] = [
                l for l in self.texture_data.get('mipmap_levels', [])
                if l.get('level') != level_num
            ]
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _edit_main_texture(self): #vers 1
        """Edit main texture"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("✏️ Editing main texture...")


    def _apply_changes(self): #vers 1
        """Apply all changes and close"""
        if self.modified_levels:
            # Update parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Mipmap changes applied")

        self.close()


    def _recompress_modified_levels(self): #vers 1
        """Recompress modified mipmap levels to DXT format"""
        try:
            format_type = self.texture_data['format']

            for level_num, level_data in self.modified_levels.items():
                rgba_data = level_data.get('rgba_data')
                if not rgba_data:
                    continue

                width = level_data['width']
                height = level_data['height']

                # Compress based on format
                if 'DXT1' in format_type:
                    compressed_data = self._compress_to_dxt1(rgba_data, width, height)
                elif 'DXT3' in format_type:
                    compressed_data = self._compress_to_dxt3(rgba_data, width, height)
                elif 'DXT5' in format_type:
                    compressed_data = self._compress_to_dxt5(rgba_data, width, height)
                else:
                    compressed_data = rgba_data  # Uncompressed

                if compressed_data:
                    level_data['compressed_data'] = compressed_data
                    level_data['compressed_size'] = len(compressed_data)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Recompressed {len(self.modified_levels)} modified levels")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ Recompression warning: {str(e)}")


    # --- DXT1 and DXT5 encoders (pure Python) ---

    def _compress_to_dxt1(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT1 format"""
        try:
            # Use helper function
            return _encode_dxt1(rgba_data, width, height)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT1 compression error: {str(e)}")
            return None


    def _compress_to_dxt3(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT3 format"""
        try:
            # DXT3 uses DXT1 color + explicit alpha
            import struct

            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4
            dxt3_data = bytearray()

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    # Extract 4x4 block
                    block_alpha = bytearray()

                    for py in range(4):
                        for px in range(4):
                            x = bx * 4 + px
                            y = by * 4 + py

                            if x < width and y < height:
                                idx = (y * width + x) * 4
                                alpha = rgba_data[idx + 3]
                            else:
                                alpha = 255

                            block_alpha.append(alpha)

                    # Encode explicit alpha (4-bit per pixel)
                    alpha_block = 0
                    for i in range(16):
                        alpha_4bit = block_alpha[i] >> 4  # Convert 8-bit to 4-bit
                        alpha_block |= (alpha_4bit << (i * 4))

                    # Pack alpha block (8 bytes)
                    dxt3_data.extend(struct.pack('<Q', alpha_block))

                    # Add DXT1 color block (would need to encode, using placeholder)
                    dxt3_data.extend(b'\x00' * 8)  # Placeholder for color block

            return bytes(dxt3_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT3 compression error: {str(e)}")
            return None


    def _compress_to_dxt5(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT5 format"""
        try:
            # Use helper function
            return _encode_dxt5(rgba_data, width, height)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT5 compression error: {str(e)}")
            return None


class TexturePropertiesDialog(QDialog): #vers 1
    """Complete texture properties dialog with all settings"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data.copy()  # Work on copy
        self.original_texture = texture_data
        self.main_window = main_window
        self.changes_made = False

        self.setWindowTitle(f"Properties: {texture_data.get('name', 'Unknown')}")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "Settings")


    def setup_ui(self): #vers 1
        """Setup properties dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with texture name
        header = QLabel(f"Texture: {self.texture_data.get('name', 'Unknown')}")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Tabs for different property sections
        tabs = QTabWidget()

        # Tab 1: Basic Info
        basic_tab = self._create_basic_tab()
        tabs.addTab(basic_tab, "Basic")

        # Tab 2: Format Settings
        format_tab = self._create_format_tab()
        tabs.addTab(format_tab, "Format")

        # Tab 3: Mipmap Info
        mipmap_tab = self._create_mipmap_tab()
        tabs.addTab(mipmap_tab, "Mipmaps")

        # Tab 4: Advanced
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok_clicked)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)


    def _create_settings_tab(self): #vers 2
        """Create settings/appearance tab with button mode"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Workshop Appearance group
        workshop_group = QGroupBox("Workshop Appearance")
        workshop_layout = QFormLayout(workshop_group)

        # Button display mode
        button_mode_combo = QComboBox()
        button_mode_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])

        # Set current mode
        if hasattr(self.parent_workshop, 'button_display_mode'):
            mode_map = {'both': 0, 'icons': 1, 'text': 2}
            current_index = mode_map.get(self.parent_workshop.button_display_mode, 0)
            button_mode_combo.setCurrentIndex(current_index)

        # Connect to update
        button_mode_combo.currentIndexChanged.connect(
            lambda idx: self._change_workshop_button_mode(idx)
        )

        workshop_layout.addRow("Button Style:", button_mode_combo)

        layout.addWidget(workshop_group)

        # ... rest of settings tab ...

        layout.addStretch()
        return tab


    def _change_workshop_button_mode(self, index): #vers 1
        """Change button display mode from properties"""
        if not hasattr(self, 'parent_workshop'):
            return

        mode_map = {0: 'both', 1: 'icons', 2: 'text'}
        new_mode = mode_map[index]

        self.parent_workshop.button_display_mode = new_mode
        self.parent_workshop._update_all_buttons()


    def _create_basic_tab(self): #vers 1
        """Create basic info tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Names group
        names_group = QGroupBox("Names")
        names_layout = QFormLayout(names_group)

        self.name_edit = QLineEdit(self.texture_data.get('name', ''))
        self.name_edit.setMaxLength(32)
        names_layout.addRow("Texture Name:", self.name_edit)

        # Alpha name (if has alpha)
        if self.texture_data.get('has_alpha', False):
            alpha_name = self.texture_data.get('alpha_name', self.texture_data.get('name', '') + 'a')
            self.alpha_name_edit = QLineEdit(alpha_name)
            self.alpha_name_edit.setMaxLength(32)
            names_layout.addRow("Alpha Name:", self.alpha_name_edit)
        else:
            self.alpha_name_edit = None

        layout.addWidget(names_group)

        # Dimensions group
        dim_group = QGroupBox("Dimensions")
        dim_layout = QFormLayout(dim_group)

        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)

        dim_label = QLabel(f"{width} x {height} pixels")
        dim_label.setStyleSheet("font-weight: bold;")
        dim_layout.addRow("Size:", dim_label)

        # Calculate memory size
        uncompressed_size = width * height * 4  # RGBA
        size_kb = uncompressed_size / 1024
        size_mb = size_kb / 1024

        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"

        size_label = QLabel(f"{size_str} (uncompressed)")
        dim_layout.addRow("Memory:", size_label)

        # Aspect ratio
        if width > 0 and height > 0:
            from math import gcd
            divisor = gcd(width, height)
            aspect_w = width // divisor
            aspect_h = height // divisor
            aspect_label = QLabel(f"{aspect_w}:{aspect_h}")
            dim_layout.addRow("Aspect Ratio:", aspect_label)

        layout.addWidget(dim_group)

        # Color info group
        color_group = QGroupBox("Color Information")
        color_layout = QFormLayout(color_group)

        depth = self.texture_data.get('depth', 32)
        color_layout.addRow("Bit Depth:", QLabel(f"{depth} bit"))

        has_alpha = self.texture_data.get('has_alpha', False)
        alpha_status = QLabel("Yes" if has_alpha else "No")
        alpha_status.setStyleSheet("color: red; font-weight: bold;" if has_alpha else "")
        color_layout.addRow("Alpha Channel:", alpha_status)

        layout.addWidget(color_group)

        layout.addStretch()
        return tab


    def _create_settings_tab(self): #vers 1
        """Create settings/appearance tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Appearance group
        appearance_group = QGroupBox("Workshop Appearance")
        appearance_layout = QFormLayout(appearance_group)

        # Theme selector
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark Theme", "Light Theme", "Green Theme", "Blue Theme", "Custom"])
        appearance_layout.addRow("Theme:", theme_combo)

        # Button style
        button_style_combo = QComboBox()
        button_style_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])
        appearance_layout.addRow("Button Style:", button_style_combo)

        # Icon size
        icon_size_combo = QComboBox()
        icon_size_combo.addItems(["Small (16px)", "Medium (20px)", "Large (24px)"])
        icon_size_combo.setCurrentIndex(1)
        appearance_layout.addRow("Icon Size:", icon_size_combo)

        # Layout
        layout_combo = QComboBox()
        layout_combo.addItems(["Compact", "Normal", "Spacious"])
        layout_combo.setCurrentIndex(1)
        appearance_layout.addRow("Layout:", layout_combo)

        layout.addWidget(appearance_group)

        # Preview options
        preview_group = QGroupBox("Preview Settings")
        preview_layout = QFormLayout(preview_group)

        # Thumbnail size
        thumb_size_combo = QComboBox()
        thumb_size_combo.addItems(["Small (64px)", "Medium (80px)", "Large (120px)"])
        thumb_size_combo.setCurrentIndex(1)
        preview_layout.addRow("Thumbnail Size:", thumb_size_combo)

        # Preview background
        bg_combo = QComboBox()
        bg_combo.addItems(["Checkerboard", "Black", "White", "Gray"])
        preview_layout.addRow("Preview Background:", bg_combo)

        layout.addWidget(preview_group)

        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)

        font_size_combo = QComboBox()
        font_size_combo.addItems(["Small", "Medium", "Large"])
        font_size_combo.setCurrentIndex(1)
        font_layout.addRow("Font Size:", font_size_combo)

        layout.addWidget(font_group)

        layout.addStretch()

        # Note
        note = QLabel("Note: Some settings require restart to take full effect")
        note.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(note)

        return tab


    def _create_format_tab(self): #vers 1
        """Create format settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Current format group
        format_group = QGroupBox("Texture Format")
        format_layout = QFormLayout(format_group)

        current_format = self.texture_data.get('format', 'Unknown')
        format_label = QLabel(current_format)
        format_label.setStyleSheet("font-weight: bold;")
        format_layout.addRow("Current Format:", format_label)

        # Compression status
        is_compressed = 'DXT' in current_format
        compress_label = QLabel("Compressed" if is_compressed else "Uncompressed")
        compress_label.setStyleSheet("color: green;" if is_compressed else "color: orange;")
        format_layout.addRow("Status:", compress_label)

        # Show compression ratio if compressed
        if is_compressed:
            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)
            uncompressed = width * height * 4

            rgba_data = self.texture_data.get('rgba_data', b'')
            compressed = len(rgba_data) if rgba_data else 0

            if uncompressed > 0 and compressed > 0:
                ratio = uncompressed / compressed
                ratio_label = QLabel(f"{ratio:.1f}:1")
                format_layout.addRow("Compression Ratio:", ratio_label)

        layout.addWidget(format_group)

        # Format conversion group
        convert_group = QGroupBox("Format Conversion")
        convert_layout = QVBoxLayout(convert_group)

        convert_layout.addWidget(QLabel("Select target format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "DXT1 (No Alpha, 6:1)",
            "DXT3 (Sharp Alpha, 4:1)",
            "DXT5 (Smooth Alpha, 4:1)",
            "ARGB8888 (Uncompressed)",
            "RGB888 (Uncompressed, No Alpha)"
        ])

        # Set current selection
        format_map = {
            'DXT1': 0, 'DXT3': 1, 'DXT5': 2,
            'ARGB8888': 3, 'RGB888': 4
        }
        current_idx = format_map.get(current_format, 0)
        self.format_combo.setCurrentIndex(current_idx)

        convert_layout.addWidget(self.format_combo)

        convert_note = QLabel(
            "Note: Format conversion will be applied when you click Apply or OK.\n"
            "DXT formats reduce file size but may lose quality."
        )
        convert_note.setStyleSheet("color: #888; font-size: 10px;")
        convert_note.setWordWrap(True)
        convert_layout.addWidget(convert_note)

        layout.addWidget(convert_group)

        layout.addStretch()
        return tab


    def _create_mipmap_tab(self): #vers 1
        """Create mipmap info tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Mipmap status group
        status_group = QGroupBox("Mipmap Status")
        status_layout = QFormLayout(status_group)

        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_mipmaps = len(mipmap_levels)

        status_layout.addRow("Levels:", QLabel(str(num_mipmaps)))

        if num_mipmaps > 0:
            # Show level details
            details = QTextEdit()
            details.setReadOnly(True)
            details.setMaximumHeight(200)

            details_text = ""
            for level in mipmap_levels:
                level_num = level.get('level', 0)
                w = level.get('width', 0)
                h = level.get('height', 0)
                size = level.get('compressed_size', 0)
                size_kb = size / 1024

                details_text += f"Level {level_num}: {w}x{h} ({size_kb:.1f} KB)\n"

            details.setText(details_text)
            status_layout.addRow("Details:", details)
        else:
            no_mipmap_label = QLabel("No mipmaps generated")
            no_mipmap_label.setStyleSheet("color: orange;")
            status_layout.addRow("Status:", no_mipmap_label)

        layout.addWidget(status_group)

        # Mipmap actions group
        actions_group = QGroupBox("Mipmap Actions")
        actions_layout = QVBoxLayout(actions_group)

        generate_btn = QPushButton("Generate Mipmaps")
        generate_btn.clicked.connect(self._generate_mipmaps)
        actions_layout.addWidget(generate_btn)

        if num_mipmaps > 0:
            view_btn = QPushButton("View All Levels")
            view_btn.clicked.connect(self._view_mipmaps)
            actions_layout.addWidget(view_btn)

            export_btn = QPushButton("Export All Levels")
            export_btn.clicked.connect(self._export_mipmaps)
            actions_layout.addWidget(export_btn)

        layout.addWidget(actions_group)

        layout.addStretch()
        return tab


    def _create_advanced_tab(self): #vers 1
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Technical info group
        tech_group = QGroupBox("Technical Information")
        tech_layout = QFormLayout(tech_group)

        # RenderWare version
        rw_version = self.texture_data.get('rw_version', 'Unknown')
        tech_layout.addRow("RW Version:", QLabel(str(rw_version)))

        # Platform
        platform = self.texture_data.get('platform', 'PC')
        tech_layout.addRow("Platform:", QLabel(platform))

        # Texture flags
        flags = self.texture_data.get('flags', 0)
        tech_layout.addRow("Flags:", QLabel(f"0x{flags:04X}"))

        layout.addWidget(tech_group)

        # Memory stats group
        mem_group = QGroupBox("Memory Statistics")
        mem_layout = QFormLayout(mem_group)

        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)

        # Uncompressed size
        uncompressed = width * height * 4
        mem_layout.addRow("Uncompressed:", QLabel(f"{uncompressed:,} bytes"))

        # Current size
        rgba_data = self.texture_data.get('rgba_data', b'')
        current_size = len(rgba_data) if rgba_data else 0
        mem_layout.addRow("Current:", QLabel(f"{current_size:,} bytes"))

        # With mipmaps
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        total_mipmap_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        mem_layout.addRow("With Mipmaps:", QLabel(f"{total_mipmap_size:,} bytes"))

        layout.addWidget(mem_group)

        layout.addStretch()
        return tab


    def _apply_changes(self): #vers 1
        """Apply changes to texture"""
        # Update name
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.original_texture.get('name', ''):
            self.original_texture['name'] = new_name
            self.changes_made = True

        # Update alpha name if exists
        if self.alpha_name_edit:
            new_alpha_name = self.alpha_name_edit.text().strip()
            if new_alpha_name and new_alpha_name != self.original_texture.get('alpha_name', ''):
                self.original_texture['alpha_name'] = new_alpha_name
                self.changes_made = True

        # Update format if changed
        format_map = ['DXT1', 'DXT3', 'DXT5', 'ARGB8888', 'RGB888']
        new_format = format_map[self.format_combo.currentIndex()]

        if new_format != self.original_texture.get('format', ''):
            # Mark for format conversion
            self.original_texture['target_format'] = new_format
            self.changes_made = True

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"ℹ️ Format change queued: {new_format}")

        if self.changes_made:
            # Notify parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Properties updated")


    def _ok_clicked(self): #vers 1
        """Apply changes and close"""
        self._apply_changes()
        self.accept()


    def _generate_mipmaps(self): #vers 2
        """Generate mipmaps with user-selected depth"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout

        # Calculate possible mipmap levels
        width = self.texture_data.get('width', 256)
        height = self.texture_data.get('height', 256)
        max_dimension = max(width, height)

        # Calculate how many levels possible (down to 1x1)
        import math
        max_levels = int(math.log2(max_dimension)) + 1

        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Mipmaps")
        dialog.setModal(True)
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        # Header info
        header = QLabel(f"Texture Size: {width}x{height}\nSelect minimum mipmap size:")
        header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Slider with level preview
        slider_layout = QVBoxLayout()

        self.mipmap_slider = QSlider(Qt.Orientation.Horizontal)
        self.mipmap_slider.setMinimum(0)  # Down to 1x1
        self.mipmap_slider.setMaximum(max_levels - 1)
        self.mipmap_slider.setValue(max_levels - 6)  # Default to ~32x32
        self.mipmap_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.mipmap_slider.setTickInterval(1)

        # Preview label showing dimensions at each level
        self.mipmap_preview = QLabel()
        self.mipmap_preview.setStyleSheet("font-size: 14px; padding: 10px; background: #2a2a2a; border-radius: 3px;")
        self.mipmap_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)


        def update_preview(value):
            # Calculate dimensions at this level
            levels_from_top = max_levels - 1 - value
            min_w = max(1, width >> levels_from_top)
            min_h = max(1, height >> levels_from_top)
            num_levels = max_levels - value

            preview_text = f"Minimum Size: {min_w}x{min_h}\n"
            preview_text += f"Total Levels: {num_levels}\n\n"
            preview_text += f"Levels: {width}x{height}"

            # Show a few intermediate levels
            current_w, current_h = width, height
            shown = 1
            for i in range(1, num_levels):
                current_w = max(1, current_w // 2)
                current_h = max(1, current_h // 2)
                if shown < 4 or i == num_levels - 1:  # Show first 3 and last
                    preview_text += f" → {current_w}x{current_h}"
                    shown += 1
                elif shown == 4:
                    preview_text += " → ..."
                    shown += 1

            self.mipmap_preview.setText(preview_text)

        self.mipmap_slider.valueChanged.connect(update_preview)
        update_preview(self.mipmap_slider.value())

        slider_layout.addWidget(QLabel("More Levels ←  →  Fewer Levels"))
        slider_layout.addWidget(self.mipmap_slider)
        slider_layout.addWidget(self.mipmap_preview)

        layout.addLayout(slider_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(lambda: self._do_generate_mipmaps(dialog, max_levels))
        button_layout.addWidget(generate_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _do_generate_mipmaps(self, dialog, max_levels): #vers 1
        """Actually generate the mipmaps with selected depth"""
        slider_value = self.mipmap_slider.value()
        num_levels = max_levels - slider_value

        dialog.accept()

        if hasattr(self.parent_workshop, '_auto_generate_mipmaps_to_level'):
            # Use enhanced version with level control
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._auto_generate_mipmaps_to_level(num_levels)

            self.parent_workshop.selected_texture = old_selection
        elif hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            # Fallback to basic version
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._auto_generate_mipmaps()

            self.parent_workshop.selected_texture = old_selection

        # Refresh dialog
        self.close()
        new_dialog = TexturePropertiesDialog(self.parent_workshop, self.original_texture, self.main_window)
        new_dialog.exec()


    def _view_mipmaps(self): #vers 1
        """Open mipmap manager"""
        if hasattr(self.parent_workshop, '_open_mipmap_manager'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._open_mipmap_manager()

            self.parent_workshop.selected_texture = old_selection


    def _export_mipmaps(self): #vers 1
        """Export all mipmap levels"""
        from PyQt6.QtWidgets import QFileDialog
        import os

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        name = self.texture_data.get('name', 'texture')

        exported = 0
        for level in mipmap_levels:
            level_num = level.get('level', 0)
            rgba_data = level.get('rgba_data')
            width = level.get('width', 0)
            height = level.get('height', 0)

            if rgba_data and width > 0:
                file_path = os.path.join(output_dir, f"{name}_level{level_num}.png")
                if hasattr(self.parent_workshop, '_save_texture_png'):
                    self.parent_workshop._save_texture_png(rgba_data, width, height, file_path)
                    exported += 1

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Export Complete", f"Exported {exported} mipmap levels")


class TexturePreviewWidget(QLabel): #vers 1
    """ Test preview widget  """

    def set_checkerboard_background(self): #vers 1
        """Set checkerboard pattern background"""
        self.background_mode = 'checkerboard'
        self.bg_color = None
        self.update()

    def paintEvent(self, event): #vers 3 (update existing)
        """Paint the preview with proper background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Draw background
        if hasattr(self, 'background_mode') and self.background_mode == 'checkerboard':
            # Draw checkerboard pattern
            checker_size = 16
            light_gray = QColor(200, 200, 200)
            dark_gray = QColor(150, 150, 150)

            for y in range(0, self.height(), checker_size):
                for x in range(0, self.width(), checker_size):
                    if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                        painter.fillRect(x, y, checker_size, checker_size, light_gray)
                    else:
                        painter.fillRect(x, y, checker_size, checker_size, dark_gray)
        elif self.bg_color:
            painter.fillRect(self.rect(), self.bg_color)
        else:
            painter.fillRect(self.rect(), QColor(42, 42, 42))

        if self.pixmap and not self.pixmap.isNull():
            # Calculate position to center the image
            x = (self.width() - self.scaled_pixmap.width()) // 2
            y = (self.height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
        elif self.placeholder_text:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.placeholder_text)


class ZoomablePreview(QLabel): #vers 1
    """Custom preview widget with zoom and pan"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.original_pixmap = None
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.dragging = False
        self.drag_start = QPoint(0, 0)
        self.bg_color = QColor(42, 42, 42)  # Default dark gray

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("border: 1px solid #3a3a3a;")

        # Enable mouse tracking for pan
        self.setMouseTracking(True)


    def set_image(self, pixmap): #vers 1
        """Set image and reset view"""
        self.original_pixmap = pixmap
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def update_display(self): #vers 2
        """Update displayed image with zoom and pan"""
        if not self.original_pixmap:
            self.clear()
            return

        # Calculate zoomed size
        scaled_size = self.original_pixmap.size() * self.zoom_level
        zoomed_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Apply pan offset
        if self.pan_offset.x() != 0 or self.pan_offset.y() != 0:
            # Create a new pixmap with offset applied
            result = QPixmap(self.size())
            result.fill(self.bg_color)

            painter = QPainter(result)
            # Center the image and apply offset
            x = (self.width() - zoomed_pixmap.width()) // 2 + self.pan_offset.x()
            y = (self.height() - zoomed_pixmap.height()) // 2 + self.pan_offset.y()
            painter.drawPixmap(x, y, zoomed_pixmap)
            painter.end()

            self.setPixmap(result)
        else:
            self.setPixmap(zoomed_pixmap)


    def zoom_in(self): #vers 1
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 10.0)  # Max 10x zoom
        self.update_display()


    def zoom_out(self): #vers 1
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)  # Min 0.1x zoom
        self.update_display()


    def reset_view(self): #vers 1
        """Reset zoom and pan"""
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def fit_to_window(self): #vers 1
        """Fit image to window"""
        if not self.original_pixmap:
            return

        # Calculate zoom to fit
        img_size = self.original_pixmap.size()
        widget_size = self.size()

        zoom_w = widget_size.width() / img_size.width()
        zoom_h = widget_size.height() / img_size.height()

        self.zoom_level = min(zoom_w, zoom_h) * 0.95  # 95% to add padding
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def set_checkerboard_background(self): #vers 1 #placeholder bugfix
        """Set checkerboard pattern background"""
        self.background_mode = 'checkerboard'
        self.bg_color = None
        self.update()

    def set_background_color(self, color): #vers 1
        """Set background color"""
        self.bg_color = color
        self.setStyleSheet(f"border: 1px solid #3a3a3a; background-color: {color.name()};")


    def mousePressEvent(self, event): #vers 1
        """Start pan drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)


    def mouseMoveEvent(self, event): #vers 1
        """Handle pan drag"""
        if self.dragging:
            delta = event.pos() - self.drag_start
            self.pan_offset += delta
            self.drag_start = event.pos()
            # Pan handled by offset, update if needed


    def mouseReleaseEvent(self, event): #vers 1
        """End pan drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def wheelEvent(self, event): #vers 1
        """Mouse wheel zoom"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()



# Footer functions

def _rgb_to_565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _565_to_rgb(c):
    r = ((c >> 11) & 0x1F) << 3
    g = ((c >> 5) & 0x3F) << 2
    b = (c & 0x1F) << 3
    return r, g, b


def _best_color_index(palette, r, g, b):
    best = 0
    best_dist = None
    for i, (pr, pg, pb) in enumerate(palette):
        dr = pr - r
        dg = pg - g
        db = pb - b
        dist = dr*dr + dg*dg + db*db
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = i
    return best


def _encode_dxt1(rgba_bytes, width, height):
    """Encode raw RGBA bytes (RGBA8888) into DXT1 bytes.
    Simple block-wise encoder: select endpoints by luminance heuristic and assign indices.
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            pixels = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                    else:
                        r = g = b = 0
                    pixels.append((r,g,b))

            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels[max_i]
            c1_rgb = pixels[min_i]

            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)

            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            out.extend(struct.pack('<HHI', c0_565, c1_565, indices))

    return bytes(out)


def _encode_alpha_block(alpha_bytes):
    """Encode 4x4 alpha block for DXT5.
    alpha_bytes: list of 16 alpha values (0-255)
    Returns 8 bytes: a0, a1, and 48-bit index stream (little-endian packed 3 bits per pixel)
    """
    a0 = max(alpha_bytes)
    a1 = min(alpha_bytes)

    # Build alpha palette
    alpha_palette = [a0, a1]
    if a0 > a1:
        for i in range(1, 6):
            alpha_palette.append((( (6 - i) * a0 + i * a1 ) // 6))
    else:
        for i in range(1, 4):
            alpha_palette.append((( (4 - i) * a0 + i * a1 ) // 4))
        alpha_palette.extend([0, 255])

    # For each pixel, find best index (0..7)
    indices = 0
    bit_pos = 0
    for a in alpha_bytes:
        # find closest
        best_i = 0
        best_dist = None
        for i, av in enumerate(alpha_palette):
            dist = (av - a) * (av - a)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_i = i
        indices |= (best_i & 0x7) << bit_pos
        bit_pos += 3

    # pack into 6 bytes little endian
    idx_bytes = indices.to_bytes(6, 'little')
    return bytes([a0, a1]) + idx_bytes


def _encode_dxt5(rgba_bytes, width, height):
    """Encode raw RGBA8888 bytes into DXT5 bytes.
    DXT5 block = 8 bytes alpha block + 8 bytes color block (same as DXT1 color block)
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            alpha_vals = []
            pixels_rgb = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                        a = rgba_bytes[idx+3]
                    else:
                        r = g = b = a = 0
                    pixels_rgb.append((r,g,b))
                    alpha_vals.append(a)

            # alpha block
            alpha_block = _encode_alpha_block(alpha_vals)

            # color block same as DXT1
            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels_rgb]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels_rgb[max_i]
            c1_rgb = pixels_rgb[min_i]
            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)
            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels_rgb:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            color_bytes = struct.pack('<HHI', c0_565, c1_565, indices)

            out.extend(alpha_block)
            out.extend(color_bytes)

    return bytes(out)

# --- External AI upscaler integration helper ---
import subprocess
import tempfile
import shutil
import sys


def _call_external_upscaler(self, qimg, factor, command): #vers 1
    """Call external AI upscaler tool"""
    if not command:
        return None

    tmp_dir = tempfile.mkdtemp(prefix='txd_upscale_')
    input_path = os.path.join(tmp_dir, 'input.png')
    output_path = os.path.join(tmp_dir, 'output.png')

    try:
        # Save input image
        qimg.save(input_path)

        # Try common command patterns
        command_patterns = [
            [command, '-i', input_path, '-o', output_path, '-s', str(factor)],
            [command, input_path, output_path, str(factor)],
            [command, input_path, output_path],
            [command, '--input', input_path, '--output', output_path, '--scale', str(factor)]
        ]

        for cmd_args in command_patterns:
            try:
                result = subprocess.run(cmd_args, check=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        timeout=300)  # 5 minute timeout

                if os.path.exists(output_path):
                    result_img = QImage(output_path)
                    if not result_img.isNull():
                        return result_img.convertToFormat(QImage.Format.Format_RGBA8888)

            except subprocess.TimeoutExpired:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("External upscaler timed out")
                break
            except Exception:
                continue

        return None

    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


def open_txd_workshop(main_window, img_path=None): #vers 3
    """Open TXD Workshop from main window - works with or without IMG"""
    try:
        workshop = TXDWorkshop(main_window, main_window)

        if img_path:
            # Check if it's a TXD file or IMG file
            if img_path.lower().endswith('.txd'):
                # Load standalone TXD file
                workshop.open_txd_file(img_path)
            else:
                # Load from IMG archive
                workshop.load_from_img_archive(img_path)
        else:
            # Open in standalone mode (no IMG loaded)
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message("TXD Workshop opened in standalone mode")

        workshop.show()
        return workshop
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open TXD Workshop: {str(e)}")
        return None



if __name__ == "__main__":
    import sys
    import traceback

    print("Starting TXD Workshop...")

    try:
        app = QApplication(sys.argv)
        print("QApplication created")

        workshop = TXDWorkshop()
        print("TXDWorkshop instance created")

        workshop.setWindowTitle("TXD Workshop - Standalone")
        workshop.resize(1200, 800)
        workshop.show()
        print("Window shown, entering event loop")
        print(f"Window visible: {workshop.isVisible()}")
        print(f"Window geometry: {workshop.geometry()}")

        sys.exit(app.exec())

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

