#this belongs in components/ /img_creator.py
#!/usr/bin/env python3
"""
X-Seti - June25,2025 - IMG Factory 1.5 - IMG Creator
Enhanced IMG Creator dialog for creating new IMG files
"""

import os
import json
import struct
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFileDialog, QMessageBox, QTextEdit, QProgressBar,
    QButtonGroup, QRadioButton, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon
from .img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size


class Platform(Enum):
    """Platform enumeration"""
    PC = "PC"
    XBOX = "XBOX"
    PS2 = "PS2"
    PSP = "PSP"
    MOBILE = "Mobile"


class GameType:
    """Game type definitions with specific configurations"""
    
    GTA3 = {
        'name': 'GTA III',
        'code': 'gta3',
        'img_version': IMGVersion.IMG_1,  # Using correct enum value
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
        'img_version': IMGVersion.IMG_1,
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
        'img_version': IMGVersion.IMG_2,
        'platform': Platform.PC,
        'default_size': 150,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['gta3.img', 'player.img', 'gta_int.img'],
        'description': 'Grand Theft Auto San Andreas - Version 2 single file format'
    }
    
    GTAIV = {
        'name': 'GTA IV',
        'code': 'gtaiv',
        'img_version': IMGVersion.IMG_3,
        'platform': Platform.PC,
        'default_size': 200,
        'supports_compression': True,
        'supports_encryption': True,
        'common_files': ['pc.img', 'vehicles.img'],
        'description': 'Grand Theft Auto IV - Advanced format with compression'
    }
    
    GTASTORIES = {
        'name': 'GTA Stories',
        'code': 'gtastories',
        'img_version': IMGVersion.IMG_STORIES,
        'platform': Platform.PSP,
        'default_size': 100,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['gta3.img'],
        'description': 'GTA Liberty City/Vice City Stories - PSP format'
    }
    
    FASTMAN92 = {
        'name': 'Fastman92 Limit Adjuster',
        'code': 'fastman92',
        'img_version': IMGVersion.IMG_FASTMAN92,
        'platform': Platform.PC,
        'default_size': 500,
        'supports_compression': True,
        'supports_encryption': False,
        'common_files': ['gta3.img'],
        'description': 'Fastman92 extended format - Support for larger files'
    }

    @classmethod
    def get_all_types(cls):
        """Get all game type configurations"""
        return [cls.GTA3, cls.GTAVC, cls.GTASA, cls.GTAIV, cls.GTASTORIES, cls.FASTMAN92]

    @classmethod
    def get_by_code(cls, code: str):
        """Get game type by code"""
        for game_type in cls.get_all_types():
            if game_type['code'] == code:
                return game_type
        return None


class IMGCreationThread(QThread):
    """Background thread for IMG file creation"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    creation_finished = pyqtSignal(str)      # output_path
    creation_error = pyqtSignal(str)         # error_message
    
    def __init__(self, settings: Dict):
        super().__init__()
        self.settings = settings
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Initializing IMG creation...")
            
            output_path = self.settings['output_path']
            game_type = self.settings['game_type']
            initial_size_mb = self.settings.get('initial_size_mb', 10)
            
            self.progress_updated.emit(30, "Creating IMG file structure...")
            
            # Create the actual IMG file
            img_file = IMGFile()
            img_file.file_path = output_path
            img_file.version = game_type['img_version']
            img_file.platform = game_type['platform'].value
            
            self.progress_updated.emit(50, "Writing IMG header...")
            
            # Create the file based on version
            if game_type['img_version'] == IMGVersion.IMG_1:
                self._create_version1_img(output_path, initial_size_mb)
            elif game_type['img_version'] == IMGVersion.IMG_2:
                self._create_version2_img(output_path, initial_size_mb)
            elif game_type['img_version'] == IMGVersion.IMG_3:
                self._create_version3_img(output_path, initial_size_mb)
            elif game_type['img_version'] == IMGVersion.IMG_FASTMAN92:
                self._create_fastman92_img(output_path, initial_size_mb)
            else:
                self._create_version2_img(output_path, initial_size_mb)  # Default
            
            self.progress_updated.emit(80, "Finalizing IMG file...")
            
            # Create directory structure if requested
            if self.settings.get('create_structure', False):
                self._create_directory_structure(os.path.dirname(output_path))
            
            self.progress_updated.emit(100, "IMG creation completed")
            self.creation_finished.emit(output_path)
            
        except Exception as e:
            self.creation_error.emit(f"IMG creation failed: {str(e)}")
    
    def _create_version1_img(self, output_path: str, size_mb: int):
        """Create IMG Version 1 (GTA III/VC style)"""
        # Create DIR file
        dir_path = output_path.replace('.img', '.dir')
        with open(dir_path, 'wb') as dir_file:
            # Empty DIR file - entries will be added later
            pass
        
        # Create IMG file
        with open(output_path, 'wb') as img_file:
            # Fill with zeros to desired size
            size_bytes = size_mb * 1024 * 1024
            img_file.write(b'\x00' * size_bytes)
    
    def _create_version2_img(self, output_path: str, size_mb: int):
        """Create IMG Version 2 (GTA SA style)"""
        with open(output_path, 'wb') as img_file:
            # Write IMG Version 2 header
            img_file.write(b'VER2')  # Signature
            img_file.write(struct.pack('<I', 0))  # Entry count (initially 0)
            
            # Reserve space for entries (will be added later)
            size_bytes = size_mb * 1024 * 1024
            remaining_size = size_bytes - 8  # Subtract header size
            if remaining_size > 0:
                img_file.write(b'\x00' * remaining_size)
    
    def _create_version3_img(self, output_path: str, size_mb: int):
        """Create IMG Version 3 (GTA IV style)"""
        with open(output_path, 'wb') as img_file:
            # Write GTA IV magic number
            img_file.write(struct.pack('<I', 0xA94E2A52))
            img_file.write(struct.pack('<I', 2))  # Version
            img_file.write(struct.pack('<I', 0))  # Entry count
            img_file.write(struct.pack('<I', 0))  # Table size
            
            # Reserve space
            size_bytes = size_mb * 1024 * 1024
            remaining_size = size_bytes - 16
            if remaining_size > 0:
                img_file.write(b'\x00' * remaining_size)
    
    def _create_fastman92_img(self, output_path: str, size_mb: int):
        """Create Fastman92 IMG format"""
        with open(output_path, 'wb') as img_file:
            # Write Fastman92 signature
            img_file.write(b'VERF')  # Version Fastman92
            img_file.write(struct.pack('<I', 1))  # Version number
            img_file.write(struct.pack('<I', 0))  # Entry count
            img_file.write(struct.pack('<I', 0))  # Reserved
            
            # Reserve space
            size_bytes = size_mb * 1024 * 1024
            remaining_size = size_bytes - 16
            if remaining_size > 0:
                img_file.write(b'\x00' * remaining_size)
    
    def _create_directory_structure(self, base_dir: str):
        """Create typical directory structure for modding"""
        directories = [
            'extracted_files',
            'extracted_files/models',
            'extracted_files/textures', 
            'extracted_files/audio',
            'extracted_files/collision',
            'extracted_files/animation',
            'backup',
            'custom_mods'
        ]
        
        for directory in directories:
            dir_path = os.path.join(base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create README file in each directory
            readme_path = os.path.join(dir_path, 'README.txt')
            with open(readme_path, 'w') as readme:
                readme.write(f"Directory: {directory}\n")
                readme.write(f"Created by IMG Factory 1.5\n")
                readme.write(f"Purpose: {self._get_directory_purpose(directory)}\n")
    
    def _get_directory_purpose(self, directory: str) -> str:
        """Get purpose description for directory"""
        purposes = {
            'extracted_files': 'Store files extracted from IMG archives',
            'extracted_files/models': 'Store DFF model files',
            'extracted_files/textures': 'Store TXD texture files',
            'extracted_files/audio': 'Store WAV audio files',
            'extracted_files/collision': 'Store COL collision files',
            'extracted_files/animation': 'Store IFP animation files',
            'backup': 'Store backup copies of original IMG files',
            'custom_mods': 'Store custom modification files'
        }
        return purposes.get(directory, 'General purpose directory')


class NewIMGDialog(QDialog):
    """Dialog for creating new IMG files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG File - IMG Factory 1.5")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Initialize attributes
        self.selected_game_type = None
        self.creation_thread = None
        
        self._create_ui()
        self._connect_signals()
        self._load_default_settings()
    
    def _create_ui(self):
        """Create the dialog user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New IMG Archive")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Tab widget for organization
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Basic Settings Tab
        self._create_basic_tab()
        
        # Advanced Settings Tab
        self._create_advanced_tab()
        
        # Template Settings Tab
        self._create_template_tab()
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to create IMG file")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("📋 Preview Settings")
        self.preview_button.clicked.connect(self._preview_settings)
        button_layout.addWidget(self.preview_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("🆕 Create IMG")
        self.create_button.clicked.connect(self._create_img_file)
        self.create_button.setDefault(True)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def _create_basic_tab(self):
        """Create basic settings tab"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # Game Type Selection
        game_group = QGroupBox("Game Type")
        game_layout = QVBoxLayout(game_group)
        
        self.game_button_group = QButtonGroup()
        
        for i, game_type in enumerate(GameType.get_all_types()):
            radio = QRadioButton(f"{game_type['name']} - {game_type['description']}")
            radio.setProperty("game_type", game_type)
            self.game_button_group.addButton(radio, i)
            game_layout.addWidget(radio)
            
            if i == 2:  # Default to GTA SA
                radio.setChecked(True)
                self.selected_game_type = game_type
        
        layout.addWidget(game_group)
        
        # File Settings
        file_group = QGroupBox("File Settings")
        file_layout = QFormLayout(file_group)
        
        # Output path
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output location...")
        output_layout.addWidget(self.output_path_edit)
        
        browse_button = QPushButton("📂 Browse")
        browse_button.clicked.connect(self._browse_output_path)
        output_layout.addWidget(browse_button)
        
        file_layout.addRow("Output File:", output_layout)
        
        # Filename
        self.filename_edit = QLineEdit("new_archive.img")
        file_layout.addRow("Filename:", self.filename_edit)
        
        # Initial size
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(1)
        self.size_spin.setMaximum(2048)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        file_layout.addRow("Initial Size:", self.size_spin)
        
        layout.addWidget(file_group)
        
        # Platform Settings
        platform_group = QGroupBox("Platform")
        platform_layout = QHBoxLayout(platform_group)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["PC", "XBOX", "PS2", "PSP", "Mobile"])
        platform_layout.addWidget(self.platform_combo)
        
        layout.addWidget(platform_group)
        
        layout.addStretch()
        self.tab_widget.addTab(basic_widget, "🎮 Basic Settings")
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Compression Settings
        compression_group = QGroupBox("Compression")
        compression_layout = QVBoxLayout(compression_group)
        
        self.compression_check = QCheckBox("Enable compression")
        compression_layout.addWidget(self.compression_check)
        
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["None", "ZLIB", "LZ4", "LZO"])
        self.compression_combo.setEnabled(False)
        compression_layout.addWidget(self.compression_combo)
        
        layout.addWidget(compression_group)
        
        # Directory Structure
        structure_group = QGroupBox("Directory Structure")
        structure_layout = QVBoxLayout(structure_group)
        
        self.create_structure_check = QCheckBox("Create modding directory structure")
        self.create_structure_check.setChecked(True)
        structure_layout.addWidget(self.create_structure_check)
        
        structure_info = QLabel("Creates folders: extracted_files, backup, custom_mods, etc.")
        structure_info.setStyleSheet("color: gray; font-size: 9pt;")
        structure_layout.addWidget(structure_info)
        
        layout.addWidget(structure_group)
        
        # Validation Settings
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validate_creation_check = QCheckBox("Validate after creation")
        self.validate_creation_check.setChecked(True)
        validation_layout.addWidget(self.validate_creation_check)
        
        layout.addWidget(validation_group)
        
        layout.addStretch()
        self.tab_widget.addTab(advanced_widget, "⚙️ Advanced")
    
    def _create_template_tab(self):
        """Create template settings tab"""
        template_widget = QWidget()
        layout = QVBoxLayout(template_widget)
        
        # Template Selection
        template_group = QGroupBox("Templates")
        template_layout = QVBoxLayout(template_group)
        
        template_info = QLabel("Save current settings as template or load existing template")
        template_layout.addWidget(template_info)
        
        # Template buttons
        template_button_layout = QHBoxLayout()
        
        load_template_button = QPushButton("📥 Load Template")
        load_template_button.clicked.connect(self._load_template)
        template_button_layout.addWidget(load_template_button)
        
        save_template_button = QPushButton("💾 Save Template")
        save_template_button.clicked.connect(self._save_template)
        template_button_layout.addWidget(save_template_button)
        
        template_layout.addLayout(template_button_layout)
        
        layout.addWidget(template_group)
        
        # Template list placeholder
        template_list_group = QGroupBox("Available Templates")
        template_list_layout = QVBoxLayout(template_list_group)
        
        self.template_list = QTextEdit()
        self.template_list.setMaximumHeight(100)
        self.template_list.setPlainText("No templates available")
        self.template_list.setReadOnly(True)
        template_list_layout.addWidget(self.template_list)
        
        layout.addWidget(template_list_group)
        
        layout.addStretch()
        self.tab_widget.addTab(template_widget, "📋 Templates")
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.game_button_group.buttonClicked.connect(self._on_game_type_changed)
        self.compression_check.toggled.connect(self.compression_combo.setEnabled)
        self.filename_edit.textChanged.connect(self._update_output_path)
    
    def _load_default_settings(self):
        """Load default settings"""
        # Set default output path
        default_path = os.path.expanduser("~/Desktop")
        self.output_path_edit.setText(default_path)
        self._update_output_path()
    
    def _on_game_type_changed(self, button):
        """Handle game type selection change"""
        self.selected_game_type = button.property("game_type")
        
        # Update UI based on selected game type
        if self.selected_game_type:
            # Update default size
            self.size_spin.setValue(self.selected_game_type['default_size'])
            
            # Update platform
            platform_name = self.selected_game_type['platform'].value
            index = self.platform_combo.findText(platform_name)
            if index >= 0:
                self.platform_combo.setCurrentIndex(index)
            
            # Update compression availability
            supports_compression = self.selected_game_type.get('supports_compression', False)
            self.compression_check.setEnabled(supports_compression)
            if not supports_compression:
                self.compression_check.setChecked(False)
    
    def _browse_output_path(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory",
            self.output_path_edit.text() or os.path.expanduser("~")
        )
        if directory:
            self.output_path_edit.setText(directory)
            self._update_output_path()
    
    def _update_output_path(self):
        """Update the full output path preview"""
        output_dir = self.output_path_edit.text()
        filename = self.filename_edit.text()
        if output_dir and filename:
            full_path = os.path.join(output_dir, filename)
            self.status_label.setText(f"Output: {full_path}")
    
    def _preview_settings(self):
        """Preview creation settings"""
        settings = self.get_creation_settings()
        
        preview_text = "IMG Creation Settings:\n\n"
        preview_text += f"Game Type: {settings['game_type']['name']}\n"
        preview_text += f"Version: {settings['game_type']['img_version'].name}\n"
        preview_text += f"Platform: {settings['platform']}\n"
        preview_text += f"Output File: {settings['output_path']}\n"
        preview_text += f"Initial Size: {settings['initial_size_mb']} MB\n"
        preview_text += f"Compression: {settings['compression_enabled']}\n"
        preview_text += f"Create Structure: {settings['create_structure']}\n"
        
        QMessageBox.information(self, "Preview Settings", preview_text)
    
    def _load_template(self):
        """Load settings from template"""
        QMessageBox.information(self, "Load Template", "Template loading not yet implemented")
    
    def _save_template(self):
        """Save current settings as template"""
        QMessageBox.information(self, "Save Template", "Template saving not yet implemented")
    
    def _create_img_file(self):
        """Create the IMG file"""
        # Validate settings
        if not self._validate_settings():
            return
        
        # Get creation settings
        settings = self.get_creation_settings()
        
        # Disable UI during creation
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        
        # Start creation thread
        self.creation_thread = IMGCreationThread(settings)
        self.creation_thread.progress_updated.connect(self._on_progress_updated)
        self.creation_thread.creation_finished.connect(self._on_creation_finished)
        self.creation_thread.creation_error.connect(self._on_creation_error)
        self.creation_thread.start()
    
    def _validate_settings(self) -> bool:
        """Validate creation settings"""
        if not self.selected_game_type:
            QMessageBox.warning(self, "Validation Error", "Please select a game type")
            return False
        
        if not self.filename_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a filename")
            return False
        
        if not self.output_path_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please select an output directory")
            return False
        
        output_dir = self.output_path_edit.text()
        if not os.path.exists(output_dir):
            QMessageBox.warning(self, "Validation Error", "Output directory does not exist")
            return False
        
        # Check if file already exists
        full_path = os.path.join(output_dir, self.filename_edit.text())
        if os.path.exists(full_path):
            reply = QMessageBox.question(
                self, "File Exists",
                f"File '{full_path}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False
        
        return True
    
    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.tab_widget.setEnabled(enabled)
        self.create_button.setEnabled(enabled)
        self.preview_button.setEnabled(enabled)
    
    def _on_progress_updated(self, progress: int, status: str):
        """Handle progress updates"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_creation_finished(self, output_path: str):
        """Handle successful creation"""
        self.progress_bar.setVisible(False)
        self._set_ui_enabled(True)
        
        QMessageBox.information(
            self, "Creation Complete",
            f"IMG file created successfully:\n{output_path}"
        )
        
        self.accept()
    
    def _on_creation_error(self, error_message: str):
        """Handle creation error"""
        self.progress_bar.setVisible(False)
        self._set_ui_enabled(True)
        self.status_label.setText("Creation failed")
        
        QMessageBox.critical(self, "Creation Error", f"Failed to create IMG file:\n{error_message}")
    
    def get_creation_settings(self) -> Dict:
        """Get current creation settings"""
        output_dir = self.output_path_edit.text()
        filename = self.filename_edit.text()
        
        return {
            'game_type': self.selected_game_type or GameType.GTASA,
            'output_path': os.path.join(output_dir, filename),
            'filename': filename,
            'initial_size_mb': self.size_spin.value(),
            'platform': self.platform_combo.currentText(),
            'compression_enabled': self.compression_check.isChecked(),
            'compression_type': self.compression_combo.currentText(),
            'create_structure': self.create_structure_check.isChecked(),
            'validate_after_creation': self.validate_creation_check.isChecked()
        }


def add_new_img_functionality(main_window):
    """Add new IMG creation functionality to main window"""
    def create_new_img():
        dialog = NewIMGDialog(main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_creation_settings()
            # Handle successful creation
            main_window.log_message(f"New IMG created: {settings['output_path']}")
    
    # Add to main window if it has the method
    if hasattr(main_window, 'create_new_img'):
        main_window.create_new_img = create_new_img
    
    return create_new_img


# Test function for development
def test_new_img_dialog():
    """Test the NewIMGDialog"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = NewIMGDialog()
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        settings = dialog.get_creation_settings()
        print("Creation settings:", settings)
    
    return result


if __name__ == "__main__":
    test_new_img_dialog()
