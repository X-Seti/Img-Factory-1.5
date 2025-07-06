#this belongs in components/ img_creator.py - version 18
# X-Seti - July06 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Creator - Clean dialog for creating new IMG files
Streamlined implementation with no conflicts
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

# Import from consolidated img_core_classes
from components.img_core_classes import IMGFile, IMGVersion, format_file_size


class GamePreset:
    """Game preset configurations for IMG creation"""
    
    PRESETS = {
        'gta3': {
            'name': 'GTA III',
            'version': IMGVersion.VERSION_1,
            'default_size': 50,
            'max_size': 500,
            'compression': False,
            'description': 'Original RenderWare format with DIR+IMG files'
        },
        'gtavc': {
            'name': 'GTA Vice City', 
            'version': IMGVersion.VERSION_1,
            'default_size': 75,
            'max_size': 750,
            'compression': False,
            'description': 'Enhanced V1 format with improved DIR handling'
        },
        'gtasa': {
            'name': 'GTA San Andreas',
            'version': IMGVersion.VERSION_2,
            'default_size': 150,
            'max_size': 2048,
            'compression': True,
            'description': 'V2 format with integrated header and compression'
        },
        'bully': {
            'name': 'Bully',
            'version': IMGVersion.VERSION_2,
            'default_size': 100,
            'max_size': 1024,
            'compression': True,
            'description': 'Modified V2 format for Bully game engine'
        },
        'custom': {
            'name': 'Custom Configuration',
            'version': IMGVersion.VERSION_2,
            'default_size': 100,
            'max_size': 4096,
            'compression': False,
            'description': 'Custom settings for advanced users'
        }
    }
    
    @classmethod
    def get_preset(cls, code: str) -> Optional[Dict[str, Any]]:
        """Get preset by code"""
        return cls.PRESETS.get(code)
    
    @classmethod
    def get_all_presets(cls) -> Dict[str, Dict[str, Any]]:
        """Get all available presets"""
        return cls.PRESETS.copy()


class NewIMGDialog(QDialog):
    """Clean dialog for creating new IMG files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG Archive")
        self.setModal(True)
        self.setFixedSize(480, 420)
        
        self.selected_preset = None
        self.output_path = ""
        
        self._setup_ui()
        self._connect_signals()
        self._load_preset('gtasa')  # Default to GTA SA
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🏭 Create New IMG Archive")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32; margin: 10px;")
        layout.addWidget(title)
        
        # Game preset selection
        preset_group = QGroupBox("Game Preset")
        preset_layout = QFormLayout(preset_group)
        
        self.preset_combo = QComboBox()
        for code, preset in GamePreset.get_all_presets().items():
            self.preset_combo.addItem(preset['name'], code)
        preset_layout.addRow("Target Game:", self.preset_combo)
        
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #666; font-style: italic;")
        preset_layout.addRow("Description:", self.desc_label)
        
        layout.addWidget(preset_group)
        
        # Creation options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        # Size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 4096)
        self.size_spin.setSuffix(" MB")
        options_layout.addRow("Initial Size:", self.size_spin)
        
        # Version
        self.version_combo = QComboBox()
        self.version_combo.addItem("Version 1 (DIR+IMG)", IMGVersion.VERSION_1)
        self.version_combo.addItem("Version 2 (Single File)", IMGVersion.VERSION_2)
        options_layout.addRow("IMG Version:", self.version_combo)
        
        # Compression
        self.compression_check = QCheckBox("Enable compression")
        options_layout.addRow("Compression:", self.compression_check)
        
        # Structure
        self.structure_check = QCheckBox("Create basic structure")
        self.structure_check.setChecked(True)
        options_layout.addRow("Structure:", self.structure_check)
        
        layout.addWidget(options_group)
        
        # Output path
        path_group = QGroupBox("Output File")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output location...")
        path_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_output)
        path_layout.addWidget(self.browse_btn)
        
        layout.addWidget(path_group)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.create_btn = QPushButton("Create IMG")
        self.create_btn.clicked.connect(self._create_img)
        self.create_btn.setEnabled(False)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.path_edit.textChanged.connect(self._validate_form)
    
    def _load_preset(self, code: str):
        """Load preset configuration"""
        preset = GamePreset.get_preset(code)
        if not preset:
            return
        
        self.selected_preset = preset
        
        # Update UI
        self.desc_label.setText(preset['description'])
        self.size_spin.setValue(preset['default_size'])
        self.size_spin.setMaximum(preset['max_size'])
        
        # Set version
        version_index = 0 if preset['version'] == IMGVersion.VERSION_1 else 1
        self.version_combo.setCurrentIndex(version_index)
        
        # Set compression
        self.compression_check.setChecked(preset['compression'])
        self.compression_check.setEnabled(preset['compression'] or code == 'custom')
    
    def _on_preset_changed(self):
        """Handle preset selection change"""
        code = self.preset_combo.currentData()
        if code:
            self._load_preset(code)
    
    def _browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save IMG Archive",
            "",
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            if not file_path.lower().endswith('.img'):
                file_path += '.img'
            
            self.path_edit.setText(file_path)
            self.output_path = file_path
    
    def _validate_form(self):
        """Validate form inputs"""
        has_path = bool(self.path_edit.text().strip())
        has_preset = self.selected_preset is not None
        
        self.create_btn.setEnabled(has_path and has_preset)
    
    def _create_img(self):
        """Create the IMG file"""
        if not self.output_path:
            QMessageBox.warning(self, "Warning", "Please select an output file.")
            return
        
        if not self.selected_preset:
            QMessageBox.warning(self, "Warning", "Please select a game preset.")
            return
        
        # Get creation settings
        settings = {
            'output_path': self.output_path,
            'version': self.version_combo.currentData(),
            'size_mb': self.size_spin.value(),
            'compression': self.compression_check.isChecked(),
            'create_structure': self.structure_check.isChecked(),
            'preset_name': self.selected_preset['name']
        }
        
        # Show progress and disable UI
        self.progress_bar.setVisible(True)
        self.create_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        
        # Start creation thread
        self.creation_thread = IMGCreationThread(settings)
        self.creation_thread.progress_updated.connect(self._update_progress)
        self.creation_thread.creation_finished.connect(self._creation_finished)
        self.creation_thread.start()
    
    def _update_progress(self, value: int, message: str):
        """Update progress display"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message} ({value}%)")
    
    def _creation_finished(self, success: bool, message: str):
        """Handle creation completion"""
        self.progress_bar.setVisible(False)
        self.create_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)


class IMGCreationThread(QThread):
    """Background thread for IMG creation"""
    
    progress_updated = pyqtSignal(int, str)
    creation_finished = pyqtSignal(bool, str)
    
    def __init__(self, settings: Dict[str, Any]):
        super().__init__()
        self.settings = settings
    
    def run(self):
        """Create IMG file in background thread"""
        try:
            output_path = self.settings['output_path']
            version = self.settings['version']
            size_mb = self.settings['size_mb']
            compression = self.settings['compression']
            create_structure = self.settings['create_structure']
            preset_name = self.settings['preset_name']
            
            self.progress_updated.emit(10, "Initializing")
            
            # Create IMG file
            img = IMGFile()
            
            self.progress_updated.emit(30, "Creating file")
            
            creation_options = {
                'initial_size_mb': size_mb,
                'compression_enabled': compression
            }
            
            if not img.create_new(output_path, version, **creation_options):
                self.creation_finished.emit(False, "Failed to create IMG file structure")
                return
            
            self.progress_updated.emit(60, "Configuring")
            
            # Add basic structure if requested
            if create_structure:
                self.progress_updated.emit(80, "Creating structure")
                
                # Add common directories based on version
                if version == IMGVersion.VERSION_2:
                    # Add some basic entries for structure
                    try:
                        img.add_entry('vehicles/', b'')
                        img.add_entry('peds/', b'')
                        img.add_entry('weapons/', b'')
                    except:
                        pass  # Structure creation is optional
            
            self.progress_updated.emit(100, "Complete")
            
            # Success message
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            size_str = format_file_size(file_size)
            
            success_msg = (
                f"IMG archive created successfully!\n\n"
                f"Game: {preset_name}\n"
                f"File: {output_path}\n"
                f"Version: {version.name}\n"
                f"Size: {size_str}"
            )
            
            self.creation_finished.emit(True, success_msg)
            
        except Exception as e:
            self.creation_finished.emit(False, f"Creation failed: {str(e)}")


class BasicIMGCreator:
    """Static utility class for basic IMG creation"""
    
    @staticmethod
    def create_simple(output_path: str, size_mb: int = 100) -> bool:
        """Create simple IMG file with minimal configuration"""
        try:
            img = IMGFile()
            return img.create_new(
                output_path, 
                IMGVersion.VERSION_2, 
                initial_size_mb=size_mb
            )
        except Exception as e:
            print(f"❌ Error creating simple IMG: {e}")
            return False
    
    @staticmethod
    def create_with_preset(output_path: str, preset_code: str) -> bool:
        """Create IMG using game preset"""
        try:
            preset = GamePreset.get_preset(preset_code)
            if not preset:
                return False
            
            img = IMGFile()
            return img.create_new(
                output_path,
                preset['version'],
                initial_size_mb=preset['default_size'],
                compression_enabled=preset['compression']
            )
        except Exception as e:
            print(f"❌ Error creating with preset: {e}")
            return False


# Factory functions for external use
def create_new_img_dialog(parent=None) -> NewIMGDialog:
    """Create new IMG dialog instance"""
    return NewIMGDialog(parent)


def get_available_presets() -> Dict[str, Dict[str, Any]]:
    """Get all available game presets"""
    return GamePreset.get_all_presets()


def create_basic_img(output_path: str, preset_code: str = 'gtasa') -> bool:
    """Quick function to create basic IMG file"""
    return BasicIMGCreator.create_with_preset(output_path, preset_code)