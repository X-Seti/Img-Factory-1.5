#this belongs in components/ img_creator.py - version 16
# X-Seti - June29 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Creator - Dialog for creating new IMG files
Clean implementation with proper imports
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFileDialog, QMessageBox, QTextEdit, QProgressBar,
    QButtonGroup, QRadioButton, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon

# Import from consolidated img_core_classes
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, Platform, format_file_size


class GameType:
    """Game type definitions with specific configurations"""
    
    GTA3 = {
        'name': 'GTA III',
        'code': 'gta3',
        'img_version': IMGVersion.VERSION_1,
        'platform': Platform.PC,
        'default_size': 50,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['gta3.img'],
        'description': 'Grand Theft Auto III - Original format with DIR+IMG files'
    }
    
    GTAVC = {
        'name': 'GTA Vice City',
        'code': 'gtavc',
        'img_version': IMGVersion.VERSION_1,
        'platform': Platform.PC,
        'default_size': 75,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['gta3.img', 'cuts.img'],
        'description': 'Grand Theft Auto Vice City - Enhanced V1 format'
    }
    
    GTASA = {
        'name': 'GTA San Andreas',
        'code': 'gtasa',
        'img_version': IMGVersion.VERSION_2,
        'platform': Platform.PC,
        'default_size': 150,
        'supports_compression': True,
        'supports_encryption': False,
        'common_files': ['gta3.img', 'player.img', 'gta_int.img'],
        'description': 'Grand Theft Auto San Andreas - V2 format with compression'
    }
    
    # GTAIV removed - not RenderWare based, no DFF/TXD support


class NewIMGDialog(QDialog):
    """Dialog for creating new IMG files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG Archive")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.selected_game_type = None
        self.output_path = ""
        
        self._create_ui()
        self._connect_signals()
    
    def _create_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout(self)
        
        # Game selection
        game_group = QGroupBox("Select Game Type")
        game_layout = QVBoxLayout(game_group)
        
        self.game_buttons = QButtonGroup()
        
        for i, (game_key, game_config) in enumerate([
            ('GTA3', GameType.GTA3),
            ('GTAVC', GameType.GTAVC), 
            ('GTASA', GameType.GTASA)
            # GTAIV removed - not RenderWare based
        ]):
            radio = QRadioButton(f"{game_config['name']} - {game_config['description']}")
            radio.setProperty('game_type', game_config)
            self.game_buttons.addButton(radio, i)
            game_layout.addWidget(radio)
            
            if i == 0:  # Default selection
                radio.setChecked(True)
                self.selected_game_type = game_config
        
        layout.addWidget(game_group)
        
        # File settings
        settings_group = QGroupBox("File Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Output path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output path...")
        path_browse_btn = QPushButton("Browse...")
        path_browse_btn.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_browse_btn)
        settings_layout.addRow("Output Path:", path_layout)
        
        # Initial size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 2048)
        self.size_spin.setValue(50)
        self.size_spin.setSuffix(" MB")
        settings_layout.addRow("Initial Size:", self.size_spin)
        
        # Compression
        self.compression_check = QCheckBox("Enable Compression")
        settings_layout.addRow("Options:", self.compression_check)
        
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
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.game_buttons.buttonClicked.connect(self._on_game_selected)
    
    def _on_game_selected(self, button):
        """Handle game type selection"""
        self.selected_game_type = button.property('game_type')
        
        # Update settings based on game type
        if self.selected_game_type:
            self.size_spin.setValue(self.selected_game_type['default_size'])
            self.compression_check.setEnabled(self.selected_game_type['supports_compression'])
            self.compression_check.setChecked(self.selected_game_type['supports_compression'])
    
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
        
        if not self.selected_game_type:
            QMessageBox.warning(self, "Warning", "Please select a game type.")
            return
        
        try:
            # Create new IMG file
            img = IMGFile()
            
            # Set creation parameters
            version = self.selected_game_type['img_version']
            initial_size = self.size_spin.value()
            enable_compression = self.compression_check.isChecked()
            
            # Create the file
            if img.create_new(self.output_path, version, initial_size_mb=initial_size):
                if enable_compression:
                    img.compression_enabled = True
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"IMG archive created successfully!\n\nFile: {self.output_path}\nSize: {initial_size} MB\nVersion: {version.name}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to create IMG archive.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating IMG archive:\n{str(e)}")


class IMGCreationThread(QThread):
    """Background thread for IMG creation"""
    
    progress_updated = pyqtSignal(int, str)
    creation_finished = pyqtSignal(bool, str)
    
    def __init__(self, output_path, game_config, settings):
        super().__init__()
        self.output_path = output_path
        self.game_config = game_config
        self.settings = settings
    
    def run(self):
        """Create IMG file in background"""
        try:
            self.progress_updated.emit(10, "Initializing...")
            
            img = IMGFile()
            
            self.progress_updated.emit(30, "Creating file structure...")
            
            if img.create_new(
                self.output_path, 
                self.game_config['img_version'],
                initial_size_mb=self.settings.get('size', 50)
            ):
                self.progress_updated.emit(80, "Finalizing...")
                
                if self.settings.get('compression', False):
                    img.compression_enabled = True
                
                self.progress_updated.emit(100, "Complete!")
                self.creation_finished.emit(True, "IMG archive created successfully!")
            else:
                self.creation_finished.emit(False, "Failed to create IMG archive")
                
        except Exception as e:
            self.creation_finished.emit(False, f"Error: {str(e)}")


# Factory function for external use
def create_new_img_dialog(parent=None):
    """Factory function to create new IMG dialog"""
    return NewIMGDialog(parent)


def get_supported_game_types():
    """Get list of supported game types"""
    return [GameType.GTA3, GameType.GTAVC, GameType.GTASA]


def get_game_type_info(game_type):
    """Get information about a specific game type"""
    game_types = {
        GameType.GTA3: "Grand Theft Auto III - Original RenderWare format",
        GameType.GTAVC: "Grand Theft Auto Vice City - Enhanced V1 format", 
        GameType.GTASA: "Grand Theft Auto San Andreas - V2 format with compression"
    }
    return game_types.get(game_type, "Unknown game type")
