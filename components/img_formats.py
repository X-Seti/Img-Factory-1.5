#this belongs in /components/img_formats.py - version 7
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - Enhanced IMG Formats - Complete Format System
Credit MexUK 2007 IMG Factory 1.2 - All format variations and game-specific handling
"""

import os
import struct
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFileDialog, QMessageBox, QTextEdit, QProgressBar,
    QButtonGroup, QRadioButton, QTabWidget, QWidget, QSlider,
    QTreeWidget, QTreeWidgetItem, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from img_manager import IMGFile, IMGEntry, IMGVersion, Platform, CompressionType


class GameType(Enum):
    """Supported game types with specific configurations"""
    GTA3 = "gta3"
    GTAVC = "gtavc" 
    GTASA = "gtasa"
    GTAIV = "gtaiv"
    BULLY = "bully"
    MANHUNT = "manhunt"
    MANHUNT2 = "manhunt2"
    RDR = "rdr"
    GTAEFLC = "gtaeflc"
    MAXPAYNE3 = "maxpayne3"


class PlatformType(Enum):
    """Platform-specific configurations"""
    PC = "pc"
    XBOX = "xbox"
    XBOX360 = "xbox360"
    PS2 = "ps2"
    PSP = "psp"
    ANDROID = "android"
    IOS = "ios"


@dataclass
class GameConfiguration:
    """Game-specific IMG configuration"""
    name: str
    code: str
    img_version: IMGVersion
    platform: PlatformType
    default_size_mb: int
    max_size_mb: int
    max_entries: int
    supports_compression: bool
    supports_encryption: bool
    common_files: List[str]
    file_extensions: List[str]
    sector_size: int = 2048
    alignment_required: bool = True
    description: str = ""
    
    def get_format_specific_options(self) -> Dict[str, Any]:
        """Get format-specific options"""
        return {
            'sector_size': self.sector_size,
            'alignment_required': self.alignment_required,
            'max_entries': self.max_entries,
            'max_size_mb': self.max_size_mb
        }


class GameConfigurations:
    """Game configuration database"""
    
    CONFIGURATIONS = {
        GameType.GTA3: GameConfiguration(
            name="Grand Theft Auto III",
            code="gta3",
            img_version=IMGVersion.VERSION_1,
            platform=PlatformType.PC,
            default_size_mb=50,
            max_size_mb=500,
            max_entries=5000,
            supports_compression=False,
            supports_encryption=False,
            common_files=["gta3.img"],
            file_extensions=["DFF", "TXD", "COL", "IFP"],
            description="Original GTA III format with DIR+IMG files"
        ),
        
        GameType.GTAVC: GameConfiguration(
            name="Grand Theft Auto: Vice City",
            code="gtavc",
            img_version=IMGVersion.VERSION_1,
            platform=PlatformType.PC,
            default_size_mb=75,
            max_size_mb=750,
            max_entries=7500,
            supports_compression=False,
            supports_encryption=False,
            common_files=["gta3.img", "cuts.img"],
            file_extensions=["DFF", "TXD", "COL", "IFP", "WAV"],
            description="Vice City enhanced V1 format"
        ),
        
        GameType.GTASA: GameConfiguration(
            name="Grand Theft Auto: San Andreas",
            code="gtasa",
            img_version=IMGVersion.VERSION_2,
            platform=PlatformType.PC,
            default_size_mb=150,
            max_size_mb=2000,
            max_entries=15000,
            supports_compression=False,
            supports_encryption=False,
            common_files=["gta3.img", "player.img", "cutscene.img"],
            file_extensions=["DFF", "TXD", "COL", "IFP", "WAV", "SCM"],
            description="San Andreas Version 2 format"
        ),
        
        GameType.GTAIV: GameConfiguration(
            name="Grand Theft Auto IV",
            code="gtaiv",
            img_version=IMGVersion.VERSION_3,
            platform=PlatformType.PC,
            default_size_mb=200,
            max_size_mb=4000,
            max_entries=20000,
            supports_compression=True,
            supports_encryption=True,
            common_files=["vehicles.img", "componentpeds.img", "playerped.img"],
            file_extensions=["WDR", "WTD", "WDD", "WAD"],
            sector_size=512,
            description="GTA IV advanced format with encryption support"
        ),
        
        GameType.BULLY: GameConfiguration(
            name="Bully",
            code="bully",
            img_version=IMGVersion.VERSION_2,
            platform=PlatformType.PC,
            default_size_mb=100,
            max_size_mb=1000,
            max_entries=10000,
            supports_compression=False,
            supports_encryption=False,
            common_files=["Bully.img"],
            file_extensions=["DFF", "TXD", "COL", "IFP"],
            description="Bully game format"
        )
    }
    
    @classmethod
    def get_config(cls, game_type: GameType) -> GameConfiguration:
        """Get configuration for game type"""
        return cls.CONFIGURATIONS.get(game_type, cls.CONFIGURATIONS[GameType.GTASA])
    
    @classmethod
    def get_all_configs(cls) -> Dict[GameType, GameConfiguration]:
        """Get all configurations"""
        return cls.CONFIGURATIONS.copy()


class EnhancedIMGCreator:
    """Enhanced IMG creator with format-specific handling"""
    
    def __init__(self):
        self.game_config: Optional[GameConfiguration] = None
        self.custom_options: Dict[str, Any] = {}
        
    def set_game_type(self, game_type: GameType):
        """Set target game type"""
        self.game_config = GameConfigurations.get_config(game_type)
    
    def create_img(self, output_path: str, **options) -> bool:
        """Create IMG file with game-specific settings"""
        if not self.game_config:
            raise ValueError("Game type not set")
        
        try:
            img = IMGFile()
            
            # Merge options with game defaults
            create_options = {
                'initial_size_mb': options.get('initial_size_mb', self.game_config.default_size_mb),
                'platform': options.get('platform', self.game_config.platform.value),
                'compression_enabled': options.get('compression_enabled', False),
                'encryption_enabled': options.get('encryption_enabled', False),
                'create_structure': options.get('create_structure', True)
            }
            
            # Validate options against game limits
            if create_options['initial_size_mb'] > self.game_config.max_size_mb:
                create_options['initial_size_mb'] = self.game_config.max_size_mb
            
            # Create with game-specific version
            success = img.create_new(output_path, self.game_config.img_version, **create_options)
            
            if success and create_options.get('create_structure'):
                self._create_game_specific_structure(output_path)
            
            return success
            
        except Exception as e:
            print(f"Error creating IMG: {e}")
            return False
    
    def _create_game_specific_structure(self, img_path: str):
        """Create game-specific directory structure"""
        base_dir = os.path.dirname(img_path)
        game_dirs = {
            GameType.GTA3: ['models', 'textures', 'collision', 'animation'],
            GameType.GTAVC: ['models', 'textures', 'collision', 'animation', 'audio'],
            GameType.GTASA: ['models', 'textures', 'collision', 'animation', 'audio', 'scripts'],
            GameType.GTAIV: ['models', 'textures', 'audio', 'scripts', 'shaders'],
            GameType.BULLY: ['models', 'textures', 'collision', 'animation', 'scripts']
        }
        
        if self.game_config and GameType(self.game_config.code) in game_dirs:
            dirs = game_dirs[GameType(self.game_config.code)]
            
            for dir_name in dirs:
                dir_path = os.path.join(base_dir, f"{self.game_config.code}_{dir_name}")
                os.makedirs(dir_path, exist_ok=True)
                
                # Create README with file type info
                readme_path = os.path.join(dir_path, "README.txt")
                with open(readme_path, 'w') as f:
                    f.write(f"{self.game_config.name} - {dir_name.title()} Directory\n")
                    f.write(f"Created by IMG Factory\n\n")
                    f.write(f"Supported file types: {', '.join(self.game_config.file_extensions)}\n")


class GameSpecificIMGDialog(QDialog):
    """Enhanced IMG creation dialog with game-specific options"""
    
    img_created = pyqtSignal(str, dict)  # path, options
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Game-Specific IMG Archive")
        self.setMinimumSize(800, 700)
        self.setModal(True)
        
        self.selected_game_type = GameType.GTASA
        self.current_config = GameConfigurations.get_config(self.selected_game_type)
        
        self._create_ui()
        self._update_game_options()
    
    def _create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎮 Create Game-Specific IMG Archive")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin: 15px;")
        layout.addWidget(header)
        
        # Main content in tabs
        self.tab_widget = QTabWidget()
        
        # Game Selection Tab
        self.game_tab = self._create_game_selection_tab()
        self.tab_widget.addTab(self.game_tab, "🎯 Game Selection")
        
        # Basic Options Tab
        self.basic_tab = self._create_basic_options_tab()
        self.tab_widget.addTab(self.basic_tab, "⚙️ Basic Options")
        
        # Advanced Options Tab
        self.advanced_tab = self._create_advanced_options_tab()
        self.tab_widget.addTab(self.advanced_tab, "🔧 Advanced Options")
        
        # Preview Tab
        self.preview_tab = self._create_preview_tab()
        self.tab_widget.addTab(self.preview_tab, "👁️ Preview")
        
        layout.addWidget(self.tab_widget)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        self._create_buttons(layout)
        
        # Status label
        self.status_label = QLabel("Ready to create IMG archive")
        self.status_label.setStyleSheet("color: #666; font-size: 11pt;")
        layout.addWidget(self.status_label)
    
    def _create_game_selection_tab(self) -> QWidget:
        """Create game selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Game type selection
        game_group = QGroupBox("🎮 Select Target Game")
        game_layout = QGridLayout(game_group)
        
        self.game_buttons = QButtonGroup()
        
        row = 0
        col = 0
        for game_type in GameType:
            config = GameConfigurations.get_config(game_type)
            
            radio = QRadioButton(config.name)
            radio.setProperty("game_type", game_type)
            radio.toggled.connect(self._on_game_type_changed)
            
            if game_type == GameType.GTASA:
                radio.setChecked(True)
            
            self.game_buttons.addButton(radio)
            game_layout.addWidget(radio, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(game_group)
        
        # Game information display
        self.game_info_group = QGroupBox("ℹ️ Game Information")
        self.game_info_layout = QVBoxLayout(self.game_info_group)
        
        self.game_info_label = QLabel()
        self.game_info_label.setWordWrap(True)
        self.game_info_label.setStyleSheet("padding: 10px; background: #f8f9fa; border-radius: 5px;")
        self.game_info_layout.addWidget(self.game_info_label)
        
        layout.addWidget(self.game_info_group)
        
        # Platform selection
        platform_group = QGroupBox("🖥️ Target Platform")
        platform_layout = QHBoxLayout(platform_group)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([platform.value.upper() for platform in PlatformType])
        platform_layout.addWidget(self.platform_combo)
        
        layout.addWidget(platform_group)
        
        layout.addStretch()
        return widget
    
    def _create_basic_options_tab(self) -> QWidget:
        """Create basic options tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File options
        file_group = QGroupBox("📁 File Options")
        file_layout = QFormLayout(file_group)
        
        # Output path
        path_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output path for IMG file...")
        self.browse_button = QPushButton("📂 Browse")
        self.browse_button.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.output_path_input)
        path_layout.addWidget(self.browse_button)
        file_layout.addRow("Output Path:", path_layout)
        
        # Filename
        self.filename_input = QLineEdit("new_archive.img")
        file_layout.addRow("Filename:", self.filename_input)
        
        layout.addWidget(file_group)
        
        # Size options
        size_group = QGroupBox("📏 Size Configuration")
        size_layout = QFormLayout(size_group)
        
        # Initial size
        self.initial_size_spin = QSpinBox()
        self.initial_size_spin.setRange(1, 4096)
        self.initial_size_spin.setValue(150)
        self.initial_size_spin.setSuffix(" MB")
        size_layout.addRow("Initial Size:", self.initial_size_spin)
        
        # Size slider for visual feedback
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 500)
        self.size_slider.setValue(150)
        self.size_slider.valueChanged.connect(self._on_size_slider_changed)
        self.initial_size_spin.valueChanged.connect(self._on_size_spin_changed)
        size_layout.addRow("Quick Size:", self.size_slider)
        
        layout.addWidget(size_group)
        
        # Feature options
        features_group = QGroupBox("✨ Features")
        features_layout = QVBoxLayout(features_group)
        
        self.create_structure_check = QCheckBox("Create directory structure")
        self.create_structure_check.setChecked(True)
        self.create_structure_check.setToolTip("Create organized directories for different file types")
        features_layout.addWidget(self.create_structure_check)
        
        self.add_readme_check = QCheckBox("Add README files")
        self.add_readme_check.setChecked(True)
        features_layout.addWidget(self.add_readme_check)
        
        layout.addWidget(features_group)
        
        layout.addStretch()
        return widget
    
    def _create_advanced_options_tab(self) -> QWidget:
        """Create advanced options tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Compression options
        compression_group = QGroupBox("🗜️ Compression")
        compression_layout = QVBoxLayout(compression_group)
        
        self.compression_check = QCheckBox("Enable compression (Fastman92 format only)")
        self.compression_check.toggled.connect(self._on_compression_toggled)
        compression_layout.addWidget(self.compression_check)
        
        # Compression level
        compression_level_layout = QHBoxLayout()
        compression_level_layout.addWidget(QLabel("Level:"))
        self.compression_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_level_slider.setRange(1, 9)
        self.compression_level_slider.setValue(6)
        self.compression_level_slider.setEnabled(False)
        self.compression_level_label = QLabel("6")
        self.compression_level_slider.valueChanged.connect(
            lambda v: self.compression_level_label.setText(str(v))
        )
        compression_level_layout.addWidget(self.compression_level_slider)
        compression_level_layout.addWidget(self.compression_level_label)
        compression_layout.addLayout(compression_level_layout)
        
        layout.addWidget(compression_group)
        
        # Encryption options
        encryption_group = QGroupBox("🔒 Encryption")
        encryption_layout = QVBoxLayout(encryption_group)
        
        self.encryption_check = QCheckBox("Enable encryption (GTA IV format only)")
        encryption_layout.addWidget(self.encryption_check)
        
        # Encryption key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.encryption_key_input = QLineEdit()
        self.encryption_key_input.setPlaceholderText("Enter encryption key...")
        self.encryption_key_input.setEnabled(False)
        self.encryption_check.toggled.connect(self.encryption_key_input.setEnabled)
        key_layout.addWidget(self.encryption_key_input)
        encryption_layout.addLayout(key_layout)
        
        layout.addWidget(encryption_group)
        
        # Performance options
        performance_group = QGroupBox("⚡ Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.sector_size_combo = QComboBox()
        self.sector_size_combo.addItems(["512", "2048", "4096"])
        self.sector_size_combo.setCurrentText("2048")
        performance_layout.addRow("Sector Size:", self.sector_size_combo)
        
        self.alignment_check = QCheckBox("Force sector alignment")
        self.alignment_check.setChecked(True)
        performance_layout.addRow("Alignment:", self.alignment_check)
        
        layout.addWidget(performance_group)
        
        # Custom options
        custom_group = QGroupBox("🛠️ Custom Options")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_options_text = QTextEdit()
        self.custom_options_text.setPlaceholderText("Enter custom options as JSON...")
        self.custom_options_text.setMaximumHeight(100)
        custom_layout.addWidget(self.custom_options_text)
        
        layout.addWidget(custom_group)
        
        layout.addStretch()
        return widget
    
    def _create_preview_tab(self) -> QWidget:
        """Create preview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration preview
        preview_group = QGroupBox("📋 Configuration Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabels(["Option", "Value"])
        self.preview_tree.setAlternatingRowColors(True)
        preview_layout.addWidget(self.preview_tree)
        
        # Update preview button
        self.update_preview_button = QPushButton("🔄 Update Preview")
        self.update_preview_button.clicked.connect(self._update_preview)
        preview_layout.addWidget(self.update_preview_button)
        
        layout.addWidget(preview_group)
        
        # Validation results
        validation_group = QGroupBox("✅ Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validation_label = QLabel("Configuration is valid")
        self.validation_label.setStyleSheet("color: green;")
        validation_layout.addWidget(self.validation_label)
        
        layout.addWidget(validation_group)
        
        return widget
    
    def _create_buttons(self, layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("🚀 Create IMG Archive")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.create_button.clicked.connect(self._create_img)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.help_button = QPushButton("❓ Help")
        self.help_button.clicked.connect(self._show_help)
        
        button_layout.addWidget(self.help_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def _on_game_type_changed(self):
        """Handle game type selection change"""
        for button in self.game_buttons.buttons():
            if button.isChecked():
                self.selected_game_type = button.property("game_type")
                self.current_config = GameConfigurations.get_config(self.selected_game_type)
                self._update_game_options()
                break
    
    def _update_game_options(self):
        """Update UI based on selected game"""
        config = self.current_config
        
        # Update game info
        info_text = f"""
<b>{config.name}</b><br>
<b>Format:</b> {config.img_version.name}<br>
<b>Default Size:</b> {config.default_size_mb} MB<br>
<b>Max Size:</b> {config.max_size_mb} MB<br>
<b>Max Entries:</b> {config.max_entries:,}<br>
<b>Compression:</b> {'Yes' if config.supports_compression else 'No'}<br>
<b>Encryption:</b> {'Yes' if config.supports_encryption else 'No'}<br>
<br>
<b>Common Files:</b> {', '.join(config.common_files)}<br>
<b>File Types:</b> {', '.join(config.file_extensions)}<br>
<br>
<i>{config.description}</i>
        """
        self.game_info_label.setText(info_text.strip())
        
        # Update size limits
        self.initial_size_spin.setMaximum(config.max_size_mb)
        self.initial_size_spin.setValue(config.default_size_mb)
        self.size_slider.setMaximum(min(500, config.max_size_mb))
        self.size_slider.setValue(config.default_size_mb)
        
        # Update compression/encryption availability
        self.compression_check.setEnabled(config.supports_compression)
        if not config.supports_compression:
            self.compression_check.setChecked(False)
        
        self.encryption_check.setEnabled(config.supports_encryption)
        if not config.supports_encryption:
            self.encryption_check.setChecked(False)
        
        # Update sector size
        self.sector_size_combo.setCurrentText(str(config.sector_size))
        
        # Update filename suggestion
        suggested_name = f"{config.code}_archive.img"
        self.filename_input.setText(suggested_name)
        
        self._update_preview()
    
    def _on_compression_toggled(self, enabled: bool):
        """Handle compression toggle"""
        self.compression_level_slider.setEnabled(enabled)
    
    def _on_size_slider_changed(self, value: int):
        """Handle size slider change"""
        self.initial_size_spin.setValue(value)
    
    def _on_size_spin_changed(self, value: int):
        """Handle size spinbox change"""
        self.size_slider.setValue(value)
    
    def _browse_output_path(self):
        """Browse for output path"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path_input.setText(path)
    
    def _update_preview(self):
        """Update configuration preview"""
        self.preview_tree.clear()
        
        # Game configuration
        game_item = QTreeWidgetItem(["Game Configuration", ""])
        self.preview_tree.addTopLevelItem(game_item)
        
        game_item.addChild(QTreeWidgetItem(["Name", self.current_config.name]))
        game_item.addChild(QTreeWidgetItem(["Version", self.current_config.img_version.name]))
        game_item.addChild(QTreeWidgetItem(["Platform", self.platform_combo.currentText()]))
        
        # File options
        file_item = QTreeWidgetItem(["File Options", ""])
        self.preview_tree.addTopLevelItem(file_item)
        
        output_path = self.output_path_input.text() or "Not selected"
        file_item.addChild(QTreeWidgetItem(["Output Path", output_path]))
        file_item.addChild(QTreeWidgetItem(["Filename", self.filename_input.text()]))
        file_item.addChild(QTreeWidgetItem(["Size", f"{self.initial_size_spin.value()} MB"]))
        
        # Features
        features_item = QTreeWidgetItem(["Features", ""])
        self.preview_tree.addTopLevelItem(features_item)
        
        features_item.addChild(QTreeWidgetItem(["Create Structure", "Yes" if self.create_structure_check.isChecked() else "No"]))
        features_item.addChild(QTreeWidgetItem(["Add README", "Yes" if self.add_readme_check.isChecked() else "No"]))
        features_item.addChild(QTreeWidgetItem(["Compression", "Yes" if self.compression_check.isChecked() else "No"]))
        features_item.addChild(QTreeWidgetItem(["Encryption", "Yes" if self.encryption_check.isChecked() else "No"]))
        
        # Expand all items
        self.preview_tree.expandAll()
        
        # Validate configuration
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate current configuration"""
        errors = []
        warnings = []
        
        # Check output path
        if not self.output_path_input.text():
            errors.append("Output path not selected")
        
        # Check filename
        filename = self.filename_input.text()
        if not filename:
            errors.append("Filename is empty")
        elif not filename.endswith('.img'):
            warnings.append("Filename should end with .img")
        
        # Check size limits
        size = self.initial_size_spin.value()
        if size > self.current_config.max_size_mb:
            errors.append(f"Size exceeds maximum for {self.current_config.name} ({self.current_config.max_size_mb} MB)")
        
        # Check feature compatibility
        if self.compression_check.isChecked() and not self.current_config.supports_compression:
            errors.append("Compression not supported for selected game")
        
        if self.encryption_check.isChecked() and not self.current_config.supports_encryption:
            errors.append("Encryption not supported for selected game")
        
        # Update validation display
        if errors:
            self.validation_label.setText(f"❌ Errors: {'; '.join(errors)}")
            self.validation_label.setStyleSheet("color: red;")
            self.create_button.setEnabled(False)
        elif warnings:
            self.validation_label.setText(f"⚠️ Warnings: {'; '.join(warnings)}")
            self.validation_label.setStyleSheet("color: orange;")
            self.create_button.setEnabled(True)
        else:
            self.validation_label.setText("✅ Configuration is valid")
            self.validation_label.setStyleSheet("color: green;")
            self.create_button.setEnabled(True)
    
    def _create_img(self):
        """Create IMG file with current configuration"""
        # Validate first
        self._validate_configuration()
        if not self.create_button.isEnabled():
            return
        
        try:
            # Get output file path
            output_dir = self.output_path_input.text()
            filename = self.filename_input.text()
            output_path = os.path.join(output_dir, filename)
            
            # Check if file already exists
            if os.path.exists(output_path):
                reply = QMessageBox.question(
                    self, "File Exists",
                    f"File '{filename}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.status_label.setText("Creating IMG archive...")
            self.create_button.setEnabled(False)
            
            # Collect options
            options = {
                'initial_size_mb': self.initial_size_spin.value(),
                'platform': self.platform_combo.currentText().lower(),
                'compression_enabled': self.compression_check.isChecked(),
                'compression_level': self.compression_level_slider.value(),
                'encryption_enabled': self.encryption_check.isChecked(),
                'encryption_key': self.encryption_key_input.text(),
                'create_structure': self.create_structure_check.isChecked(),
                'add_readme': self.add_readme_check.isChecked(),
                'sector_size': int(self.sector_size_combo.currentText()),
                'alignment_required': self.alignment_check.isChecked(),
                'game_type': self.selected_game_type.value
            }
            
            # Parse custom options
            if self.custom_options_text.toPlainText().strip():
                try:
                    custom_options = json.loads(self.custom_options_text.toPlainText())
                    options.update(custom_options)
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Invalid JSON", "Custom options contain invalid JSON")
                    self._reset_ui()
                    return
            
            # Create IMG using enhanced creator
            creator = EnhancedIMGCreator()
            creator.set_game_type(self.selected_game_type)
            
            success = creator.create_img(output_path, **options)
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.create_button.setEnabled(True)
            
            if success:
                self.status_label.setText("IMG archive created successfully!")
                self.img_created.emit(output_path, options)
                
                # Show success message with options
                msg = QMessageBox(self)
                msg.setWindowTitle("Success")
                msg.setText("IMG archive created successfully!")
                msg.setDetailedText(f"Path: {output_path}\nGame: {self.current_config.name}\nSize: {options['initial_size_mb']} MB")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()
                
                self.accept()
            else:
                self.status_label.setText("Failed to create IMG archive")
                QMessageBox.critical(self, "Error", "Failed to create IMG archive")
                
        except Exception as e:
            self._reset_ui()
            QMessageBox.critical(self, "Error", f"Error creating IMG archive: {str(e)}")
    
    def _reset_ui(self):
        """Reset UI after operation"""
        self.progress_bar.setVisible(False)
        self.create_button.setEnabled(True)
        self.status_label.setText("Ready to create IMG archive")
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
<h2>IMG Archive Creation Help</h2>

<h3>Game Selection</h3>
<p>Choose the target game to ensure compatibility. Each game has specific format requirements and limitations.</p>

<h3>Basic Options</h3>
<ul>
<li><b>Output Path:</b> Directory where the IMG file will be created</li>
<li><b>Filename:</b> Name of the IMG file (should end with .img)</li>
<li><b>Initial Size:</b> Starting size of the archive in MB</li>
<li><b>Create Structure:</b> Creates organized directories for different file types</li>
</ul>

<h3>Advanced Options</h3>
<ul>
<li><b>Compression:</b> Reduces file size (Fastman92 format only)</li>
<li><b>Encryption:</b> Secures the archive (GTA IV format only)</li>
<li><b>Sector Size:</b> Size of data sectors (affects performance)</li>
<li><b>Alignment:</b> Forces sector alignment for compatibility</li>
</ul>

<h3>Game-Specific Notes</h3>
<ul>
<li><b>GTA III/VC:</b> Uses DIR+IMG file pairs</li>
<li><b>San Andreas:</b> Single IMG file with embedded directory</li>
<li><b>GTA IV:</b> Advanced format with compression and encryption support</li>
<li><b>Bully:</b> Similar to San Andreas but with game-specific optimizations</li>
</ul>

<p>For more information, consult the IMG Factory documentation.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help - IMG Archive Creation")
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


class IMGFormatConverter:
    """Convert between different IMG format versions"""
    
    @staticmethod
    def convert_format(input_path: str, output_path: str, target_version: IMGVersion, **options) -> bool:
        """Convert IMG file to different format version"""
        try:
            # Open source IMG
            source_img = IMGFile(input_path)
            if not source_img.open():
                return False
            
            # Create target IMG
            target_img = IMGFile()
            if not target_img.create_new(output_path, target_version, **options):
                return False
            
            # Copy all entries
            for entry in source_img.entries:
                try:
                    data = entry.get_data()
                    target_img.add_entry(entry.name, data)
                except Exception as e:
                    print(f"Error copying entry {entry.name}: {e}")
            
            # Rebuild target IMG
            success = target_img.rebuild()
            
            # Cleanup
            source_img.close()
            target_img.close()
            
            return success
            
        except Exception as e:
            print(f"Error converting IMG format: {e}")
            return False
    
    @staticmethod
    def batch_convert_format(input_dir: str, output_dir: str, target_version: IMGVersion, **options) -> int:
        """Batch convert IMG files to different format"""
        converted_count = 0
        
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.img'):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename)
                
                if IMGFormatConverter.convert_format(input_path, output_path, target_version, **options):
                    converted_count += 1
                    print(f"Converted: {filename}")
                else:
                    print(f"Failed to convert: {filename}")
        
        return converted_count


class IMGCompatibilityChecker:
    """Check IMG compatibility with different games"""
    
    @staticmethod
    def check_compatibility(img_path: str, target_game: GameType) -> Dict[str, Any]:
        """Check IMG compatibility with target game"""
        result = {
            'compatible': True,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            img = IMGFile(img_path)
            if not img.open():
                result['compatible'] = False
                result['issues'].append("Cannot open IMG file")
                return result
            
            config = GameConfigurations.get_config(target_game)
            
            # Check version compatibility
            if img.version != config.img_version:
                result['issues'].append(f"Version mismatch: IMG is {img.version.name}, game expects {config.img_version.name}")
                result['recommendations'].append(f"Convert to {config.img_version.name} format")
                result['compatible'] = False
            
            # Check entry count
            if len(img.entries) > config.max_entries:
                result['issues'].append(f"Too many entries: {len(img.entries)} > {config.max_entries}")
                result['compatible'] = False
            
            # Check file size
            file_size_mb = os.path.getsize(img_path) / (1024 * 1024)
            if file_size_mb > config.max_size_mb:
                result['warnings'].append(f"Large file size: {file_size_mb:.1f} MB")
            
            # Check file extensions
            unsupported_exts = []
            for entry in img.entries:
                if entry.extension and entry.extension not in config.file_extensions:
                    if entry.extension not in unsupported_exts:
                        unsupported_exts.append(entry.extension)
            
            if unsupported_exts:
                result['warnings'].append(f"Unsupported file types: {', '.join(unsupported_exts)}")
            
            # Check compression/encryption
            if any(entry.is_compressed for entry in img.entries) and not config.supports_compression:
                result['issues'].append("Compressed files not supported by target game")
                result['compatible'] = False
            
            if img.is_encrypted and not config.supports_encryption:
                result['issues'].append("Encrypted IMG not supported by target game")
                result['compatible'] = False
            
            img.close()
            
        except Exception as e:
            result['compatible'] = False
            result['issues'].append(f"Error checking compatibility: {str(e)}")
        
        return result


class IMGFormatOptimizer:
    """Optimize IMG files for specific games/platforms"""
    
    @staticmethod
    def optimize_for_game(img_path: str, target_game: GameType, output_path: str = None) -> bool:
        """Optimize IMG file for specific game"""
        if not output_path:
            output_path = img_path
        
        try:
            config = GameConfigurations.get_config(target_game)
            
            # Open IMG
            img = IMGFile(img_path)
            if not img.open():
                return False
            
            # Apply game-specific optimizations
            if target_game == GameType.GTASA:
                # San Andreas optimizations
                IMGFormatOptimizer._optimize_for_gtasa(img, config)
            elif target_game == GameType.GTAIV:
                # GTA IV optimizations
                IMGFormatOptimizer._optimize_for_gtaiv(img, config)
            elif target_game in [GameType.GTA3, GameType.GTAVC]:
                # GTA III/VC optimizations
                IMGFormatOptimizer._optimize_for_gta3vc(img, config)
            
            # Rebuild optimized IMG
            success = img.rebuild(output_path)
            img.close()
            
            return success
            
        except Exception as e:
            print(f"Error optimizing IMG: {e}")
            return False
    
    @staticmethod
    def _optimize_for_gtasa(img: IMGFile, config: GameConfiguration):
        """Apply San Andreas specific optimizations"""
        # Sort entries alphabetically for better performance
        img.entries.sort(key=lambda e: e.name.upper())
        
        # Remove empty entries
        img.entries = [e for e in img.entries if e.size > 0]
        
        # Ensure sector alignment
        for entry in img.entries:
            if entry.offset % config.sector_size != 0:
                entry.offset = ((entry.offset + config.sector_size - 1) // config.sector_size) * config.sector_size
    
    @staticmethod
    def _optimize_for_gtaiv(img: IMGFile, config: GameConfiguration):
        """Apply GTA IV specific optimizations"""
        # Enable compression for large files if supported
        if config.supports_compression:
            for entry in img.entries:
                if entry.size > 10240 and not entry.is_compressed:  # > 10KB
                    # Mark for compression (actual compression would happen during rebuild)
                    entry.is_compressed = True
        
        # Sort by file type for better loading
        type_order = {'WDR': 1, 'WTD': 2, 'WDD': 3, 'WAD': 4}
        img.entries.sort(key=lambda e: (type_order.get(e.extension, 99), e.name.upper()))
    
    @staticmethod
    def _optimize_for_gta3vc(img: IMGFile, config: GameConfiguration):
        """Apply GTA III/VC specific optimizations"""
        # Ensure strict sector alignment for older games
        for entry in img.entries:
            if entry.offset % 2048 != 0:
                entry.offset = ((entry.offset + 2047) // 2048) * 2048
        
        # Sort by extension then name
        img.entries.sort(key=lambda e: (e.extension or 'ZZZ', e.name.upper()))


# Template system for quick IMG creation
class IMGTemplateSystem:
    """Template system for common IMG configurations"""
    
    TEMPLATES = {
        'gta_sa_vehicle_pack': {
            'name': 'GTA SA Vehicle Pack',
            'game_type': GameType.GTASA,
            'size_mb': 200,
            'structure': ['vehicles/models', 'vehicles/textures', 'vehicles/collision'],
            'description': 'Template for vehicle modification packs'
        },
        
        'gta_iv_mod_pack': {
            'name': 'GTA IV Mod Pack', 
            'game_type': GameType.GTAIV,
            'size_mb': 500,
            'compression': True,
            'structure': ['models', 'textures', 'audio'],
            'description': 'Template for comprehensive GTA IV mods'
        },
        
        'bully_character_pack': {
            'name': 'Bully Character Pack',
            'game_type': GameType.BULLY,
            'size_mb': 100,
            'structure': ['characters/models', 'characters/textures', 'characters/animation'],
            'description': 'Template for Bully character modifications'
        }
    }
    
    @classmethod
    def create_from_template(cls, template_name: str, output_path: str, **overrides) -> bool:
        """Create IMG from template"""
        if template_name not in cls.TEMPLATES:
            return False
        
        template = cls.TEMPLATES[template_name].copy()
        template.update(overrides)
        
        try:
            creator = EnhancedIMGCreator()
            creator.set_game_type(template['game_type'])
            
            options = {
                'initial_size_mb': template.get('size_mb', 100),
                'compression_enabled': template.get('compression', False),
                'create_structure': True
            }
            
            return creator.create_img(output_path, **options)
            
        except Exception as e:
            print(f"Error creating from template: {e}")
            return False
    
    @classmethod
    def get_template_list(cls) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {
                'id': key,
                'name': template['name'],
                'description': template['description'],
                'game': template['game_type'].value
            }
            for key, template in cls.TEMPLATES.items()
        ]


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test game-specific dialog
    dialog = GameSpecificIMGDialog()
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("IMG creation dialog completed successfully")
    
    # Test format conversion
    test_img = "test.img"
    if os.path.exists(test_img):
        print("Testing format conversion...")
        if IMGFormatConverter.convert_format(test_img, "converted.img", IMGVersion.VERSION_2):
            print("✓ Format conversion successful")
        
        # Test compatibility check
        compatibility = IMGCompatibilityChecker.check_compatibility(test_img, GameType.GTASA)
        print(f"✓ Compatibility check: {'Compatible' if compatibility['compatible'] else 'Issues found'}")
        
        # Test optimization
        if IMGFormatOptimizer.optimize_for_game(test_img, GameType.GTASA, "optimized.img"):
            print("✓ Optimization successful")
    
    # Test template system
    templates = IMGTemplateSystem.get_template_list()
    print(f"✓ Available templates: {len(templates)}")
    
    print("IMG Formats tests completed!")
    sys.exit(0)
