#this belongs in /components/img_formats.py - version 8
# X-Seti - June29 2025 - Img Factory 1.5  
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
Enhanced IMG Formats - Complete Format System
Game-specific handling for different IMG format variations
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

# Import from consolidated img_core_classes
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, CompressionType


class GameType(Enum):
    """Supported game types with specific configurations"""
    GTA3 = "gta3"
    GTAVC = "gtavc" 
    GTASA = "gtasa"
    # GTAIV removed - not RenderWare based
    BULLY = "bully"
    MANHUNT = "manhunt"
    MANHUNT2 = "manhunt2"


class PlatformType(Enum):
    """Platform-specific configurations for games"""
    PC = "pc"
    XBOX = "xbox"
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
            max_entries=8000,
            supports_compression=False,
            supports_encryption=False,
            common_files=['gta3.img'],
            file_extensions=['.dff', '.txd', '.col', '.ifp'],
            description="Original RenderWare format with DIR+IMG files"
        ),
        
        GameType.GTAVC: GameConfiguration(
            name="Grand Theft Auto Vice City",
            code="gtavc",
            img_version=IMGVersion.VERSION_1,
            platform=PlatformType.PC,
            default_size_mb=75,
            max_size_mb=750,
            max_entries=10000,
            supports_compression=False,
            supports_encryption=False,
            common_files=['gta3.img', 'cuts.img'],
            file_extensions=['.dff', '.txd', '.col', '.ifp'],
            description="Enhanced V1 format with improved DIR handling"
        ),
        
        GameType.GTASA: GameConfiguration(
            name="Grand Theft Auto San Andreas",
            code="gtasa",
            img_version=IMGVersion.VERSION_2,
            platform=PlatformType.PC,
            default_size_mb=150,
            max_size_mb=2048,
            max_entries=16000,
            supports_compression=True,
            supports_encryption=False,
            common_files=['gta3.img', 'player.img', 'gta_int.img'],
            file_extensions=['.dff', '.txd', '.col', '.ifp', '.wav'],
            description="V2 format with integrated header and compression support"
        ),
        
        GameType.BULLY: GameConfiguration(
            name="Bully",
            code="bully",
            img_version=IMGVersion.VERSION_2,
            platform=PlatformType.PC,
            default_size_mb=100,
            max_size_mb=1024,
            max_entries=12000,
            supports_compression=True,
            supports_encryption=False,
            common_files=['world.img', 'chars.img'],
            file_extensions=['.dff', '.txd', '.col', '.ifp'],
            description="Modified V2 format for Bully game engine"
        )
    }
    
    @classmethod
    def get_configuration(cls, game_type: GameType) -> GameConfiguration:
        """Get configuration for specific game type"""
        return cls.CONFIGURATIONS.get(game_type)
    
    @classmethod
    def get_all_games(cls) -> List[GameType]:
        """Get list of all supported games"""
        return list(cls.CONFIGURATIONS.keys())


class GameSpecificIMGDialog(QDialog):
    """Dialog for creating game-specific IMG files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Game-Specific IMG Archive")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.selected_config = None
        self.output_path = ""
        
        self._create_ui()
        self._connect_signals()
    
    def _create_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout(self)
        
        # Game selection
        game_group = QGroupBox("Select Game & Platform")
        game_layout = QVBoxLayout(game_group)
        
        # Game type combo
        self.game_combo = QComboBox()
        for game_type in GameConfigurations.get_all_games():
            config = GameConfigurations.get_configuration(game_type)
            self.game_combo.addItem(config.name, game_type)
        game_layout.addWidget(QLabel("Game:"))
        game_layout.addWidget(self.game_combo)
        
        # Platform combo
        self.platform_combo = QComboBox()
        for platform in PlatformType:
            self.platform_combo.addItem(platform.value.upper(), platform)
        game_layout.addWidget(QLabel("Platform:"))
        game_layout.addWidget(self.platform_combo)
        
        layout.addWidget(game_group)
        
        # Configuration display
        config_group = QGroupBox("Configuration Details")
        config_layout = QFormLayout(config_group)
        
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        config_layout.addRow("Description:", self.desc_label)
        
        self.version_label = QLabel()
        config_layout.addRow("IMG Version:", self.version_label)
        
        self.size_limits_label = QLabel()
        config_layout.addRow("Size Limits:", self.size_limits_label)
        
        self.features_label = QLabel()
        config_layout.addRow("Features:", self.features_label)
        
        layout.addWidget(config_group)
        
        # File settings
        settings_group = QGroupBox("File Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Output path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        path_browse_btn = QPushButton("Browse...")
        path_browse_btn.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_browse_btn)
        settings_layout.addRow("Output Path:", path_layout)
        
        # Size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 4096)
        self.size_spin.setSuffix(" MB")
        settings_layout.addRow("Initial Size:", self.size_spin)
        
        # Options
        self.compression_check = QCheckBox("Enable Compression")
        self.encryption_check = QCheckBox("Enable Encryption")
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.compression_check)
        options_layout.addWidget(self.encryption_check)
        settings_layout.addRow("Options:", options_layout)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create IMG")
        create_btn.setDefault(True)
        create_btn.clicked.connect(self._create_img)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize with first game
        self._update_configuration()
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.game_combo.currentIndexChanged.connect(self._update_configuration)
        self.platform_combo.currentIndexChanged.connect(self._update_configuration)
    
    def _update_configuration(self):
        """Update configuration display"""
        game_type = self.game_combo.currentData()
        if not game_type:
            return
        
        config = GameConfigurations.get_configuration(game_type)
        if not config:
            return
        
        self.selected_config = config
        
        # Update display
        self.desc_label.setText(config.description)
        self.version_label.setText(config.img_version.name)
        self.size_limits_label.setText(f"{config.default_size_mb} MB (max: {config.max_size_mb} MB)")
        
        features = []
        if config.supports_compression:
            features.append("Compression")
        if config.supports_encryption:
            features.append("Encryption")
        self.features_label.setText(", ".join(features) if features else "None")
        
        # Update controls
        self.size_spin.setValue(config.default_size_mb)
        self.size_spin.setMaximum(config.max_size_mb)
        
        self.compression_check.setEnabled(config.supports_compression)
        self.compression_check.setChecked(config.supports_compression)
        
        self.encryption_check.setEnabled(config.supports_encryption)
        self.encryption_check.setChecked(False)
    
    def _browse_output_path(self):
        """Browse for output file path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save IMG Archive",
            "",
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            self.output_path = file_path
    
    def _create_img(self):
        """Create the new IMG file"""
        if not self.output_path:
            QMessageBox.warning(self, "Warning", "Please select an output path.")
            return
        
        if not self.selected_config:
            QMessageBox.warning(self, "Warning", "No configuration selected.")
            return
        
        try:
            img = IMGFile()
            
            creation_options = {
                'initial_size_mb': self.size_spin.value(),
                'compression_enabled': self.compression_check.isChecked(),
                'encryption_enabled': self.encryption_check.isChecked(),
                'sector_size': self.selected_config.sector_size,
                'alignment_required': self.selected_config.alignment_required
            }
            
            if img.create_new(self.output_path, self.selected_config.img_version, **creation_options):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Game-specific IMG archive created!\n\n"
                    f"Game: {self.selected_config.name}\n"
                    f"File: {self.output_path}\n"
                    f"Version: {self.selected_config.img_version.name}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to create IMG archive.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating IMG archive:\n{str(e)}")


class EnhancedIMGCreator:
    """Enhanced IMG creation with advanced options"""
    
    @staticmethod
    def create_from_template(template_path: str, output_path: str, game_type: GameType) -> bool:
        """Create IMG from template file"""
        try:
            config = GameConfigurations.get_configuration(game_type)
            if not config:
                return False
            
            img = IMGFile()
            if img.create_new(output_path, config.img_version):
                # Load template and populate
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                
                for entry_info in template_data.get('entries', []):
                    # Create placeholder entries
                    img.add_entry(entry_info['name'], b'')
                
                return img.rebuild()
            
        except Exception as e:
            print(f"Error creating from template: {e}")
        
        return False
    
    @staticmethod
    def validate_game_compatibility(img_path: str, target_game: GameType) -> Dict[str, Any]:
        """Validate IMG compatibility with target game"""
        result = {
            'compatible': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            img = IMGFile(img_path)
            if img.open():
                config = GameConfigurations.get_configuration(target_game)
                
                # Check version compatibility
                if img.version != config.img_version:
                    result['issues'].append(f"Version mismatch: IMG is {img.version.name}, game expects {config.img_version.name}")
                
                # Check file count
                if len(img.entries) > config.max_entries:
                    result['issues'].append(f"Too many entries: {len(img.entries)} > {config.max_entries}")
                
                # Check file types
                unsupported_extensions = []
                for entry in img.entries:
                    if entry.extension.lower() not in [ext.lower() for ext in config.file_extensions]:
                        unsupported_extensions.append(entry.extension)
                
                if unsupported_extensions:
                    result['issues'].append(f"Unsupported file types: {', '.join(set(unsupported_extensions))}")
                
                result['compatible'] = len(result['issues']) == 0
                img.close()
        
        except Exception as e:
            result['issues'].append(f"Error analyzing file: {str(e)}")
        
        return result


# Factory functions
def create_game_specific_dialog(parent=None):
    """Create game-specific IMG dialog"""
    return GameSpecificIMGDialog(parent)


def get_supported_games():
    """Get list of supported games"""
    return GameConfigurations.get_all_games()


def get_game_configuration(game_type: GameType):
    """Get configuration for specific game"""
    return GameConfigurations.get_configuration(game_type)
