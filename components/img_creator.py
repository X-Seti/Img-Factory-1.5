#!/usr/bin/env python3
"""
IMG Creator - Dialog for creating new IMG files
Based on the enhanced creation system from the original codebase
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
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size

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
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['gta3.img', 'cutscene.img', 'gta_int.img', 'player.img'],
        'description': 'Grand Theft Auto San Andreas - V2 format with single file'
    }
    
    GTAIV = {
        'name': 'GTA IV',
        'code': 'gtaiv',
        'img_version': IMGVersion.VERSION_3,
        'platform': Platform.PC,
        'default_size': 500,
        'supports_compression': True,
        'supports_encryption': True,
        'common_files': ['pc.img', 'vehicles.img', 'componentpeds.img'],
        'description': 'Grand Theft Auto IV - Advanced V3 format with encryption support'
    }
    
    BULLY = {
        'name': 'Bully',
        'code': 'bully',
        'img_version': IMGVersion.VERSION_2,
        'platform': Platform.PC,
        'default_size': 100,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['models.img', 'textures.img'],
        'description': 'Bully - Modified V2 format'
    }
    
    CUSTOM = {
        'name': 'Custom',
        'code': 'custom',
        'img_version': IMGVersion.VERSION_2,
        'platform': Platform.PC,
        'default_size': 100,
        'supports_compression': True,
        'supports_encryption': False,
        'common_files': [],
        'description': 'Custom IMG format with user-defined settings'
    }
    
    @classmethod
    def get_all_types(cls):
        """Get all game type definitions"""
        return {
            'gta3': cls.GTA3,
            'gtavc': cls.GTAVC,
            'gtasa': cls.GTASA,
            'gtaiv': cls.GTAIV,
            'bully': cls.BULLY,
            'custom': cls.CUSTOM
        }
    
    @classmethod
    def get_type(cls, code: str):
        """Get specific game type by code"""
        return cls.get_all_types().get(code, cls.CUSTOM)


class IMGCreationThread(QThread):
    """Background thread for IMG file creation"""
    
    progress_updated = pyqtSignal(int, str)  # progress, status
    creation_completed = pyqtSignal(str)  # file_path
    creation_error = pyqtSignal(str)  # error_message
    
    def __init__(self, settings: Dict):
        super().__init__()
        self.settings = settings
    
    def run(self):
        """Run IMG creation in background"""
        try:
            self.progress_updated.emit(10, "Initializing...")
            
            # Create IMG file
            img_file = IMGFile()
            file_path = self.settings['output_path']
            img_version = self.settings['img_version']
            
            self.progress_updated.emit(30, "Creating IMG structure...")
            
            if not img_file.create_new(file_path, img_version):
                self.creation_error.emit("Failed to create IMG file structure")
                return
            
            self.progress_updated.emit(50, "Setting up file properties...")
            
            # Apply settings
            img_file.platform = self.settings.get('platform', Platform.PC)
            
            self.progress_updated.emit(70, "Creating initial structure...")
            
            # Add initial structure if requested
            if self.settings.get('create_structure', False):
                self._create_folder_structure(img_file)
            
            self.progress_updated.emit(90, "Finalizing...")
            
            # Save the file
            if img_file.rebuild(file_path):
                self.progress_updated.emit(100, "IMG file created successfully!")
                self.creation_completed.emit(file_path)
            else:
                self.creation_error.emit("Failed to save IMG file")
            
            img_file.close()
            
        except Exception as e:
            self.creation_error.emit(f"Creation failed: {str(e)}")
    
    def _create_folder_structure(self, img_file: IMGFile):
        """Create basic folder structure in IMG"""
        game_type = self.settings.get('game_type', 'custom')
        
        if game_type in ['gta3', 'gtavc']:
            # Basic structure for GTA III/VC
            structure_files = [
                ('readme.txt', b'IMG Factory generated file\nGame: ' + game_type.upper().encode()),
            ]
        elif game_type == 'gtasa':
            # GTA SA structure
            structure_files = [
                ('readme.txt', b'IMG Factory generated file for GTA San Andreas'),
            ]
        elif game_type == 'gtaiv':
            # GTA IV structure
            structure_files = [
                ('readme.txt', b'IMG Factory generated file for GTA IV'),
            ]
        else:
            # Custom structure
            structure_files = [
                ('readme.txt', b'IMG Factory generated custom IMG file'),
            ]
        
        # Add structure files
        for filename, content in structure_files:
            img_file.add_entry(filename, content)


class NewIMGDialog(QDialog):
    """Enhanced dialog for creating new IMG files"""
    
    img_created = pyqtSignal(str)  # Emits path of created IMG file
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG Archive")
        self.setMinimumSize(650, 550)
        self.setModal(True)
        
        self.selected_game_type = 'gtasa'  # Default
        self.template_manager = None  # Will be set by parent if available
        
        self._create_ui()
        self._load_settings()
    
    def _create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎮 Create New IMG Archive")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin: 10px;")
        layout.addWidget(header)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Basic Settings Tab
        basic_tab = self._create_basic_tab()
        tab_widget.addTab(basic_tab, "📋 Basic Settings")
        
        # Advanced Settings Tab
        advanced_tab = self._create_advanced_tab()
        tab_widget.addTab(advanced_tab, "⚙️ Advanced Settings")
        
        # Templates Tab
        template_tab = self._create_template_tab()
        tab_widget.addTab(template_tab, "📄 Templates")
        
        layout.addWidget(tab_widget)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        self._create_button_section(layout)
    
    def _create_basic_tab(self) -> QWidget:
        """Create basic settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Game Type Selection
        game_group = QGroupBox("🎮 Game Type")
        game_layout = QGridLayout(game_group)
        
        self.game_button_group = QButtonGroup()
        game_types = GameType.get_all_types()
        
        for i, (code, game_info) in enumerate(game_types.items()):
            radio = QRadioButton(game_info['name'])
            radio.game_code = code
            radio.game_info = game_info
            radio.setToolTip(game_info['description'])
            
            if code == 'gtasa':  # Default selection
                radio.setChecked(True)
            
            self.game_button_group.addButton(radio)
            radio.toggled.connect(lambda checked, r=radio: self._on_game_type_changed(r) if checked else None)
            
            game_layout.addWidget(radio, i // 2, i % 2)
        
        layout.addWidget(game_group)
        
        # File Settings
        file_group = QGroupBox("📁 File Settings")
        file_layout = QFormLayout(file_group)
        
        # Filename
        self.filename_input = QLineEdit("new_archive.img")
        self.filename_input.textChanged.connect(self._validate_input)
        file_layout.addRow("Filename:", self.filename_input)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setPlaceholderText("Select output directory...")
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.clicked.connect(self._browse_output_dir)
        
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(browse_btn)
        file_layout.addRow("Output Directory:", dir_layout)
        
        # Initial size
        self.initial_size_spin = QSpinBox()
        self.initial_size_spin.setRange(1, 2048)
        self.initial_size_spin.setValue(100)
        self.initial_size_spin.setSuffix(" MB")
        self.initial_size_spin.setToolTip("Initial size allocation for the IMG file")
        file_layout.addRow("Initial Size:", self.initial_size_spin)
        
        layout.addWidget(file_group)
        
        # Quick Options
        options_group = QGroupBox("⚡ Quick Options")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_structure_check = QCheckBox("Create basic folder structure")
        self.auto_structure_check.setToolTip("Add basic directory structure to the IMG file")
        options_layout.addWidget(self.auto_structure_check)
        
        self.open_after_create_check = QCheckBox("Open in IMG Factory after creation")
        self.open_after_create_check.setChecked(True)
        options_layout.addWidget(self.open_after_create_check)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Platform Settings
        platform_group = QGroupBox("🖥️ Platform Settings")
        platform_layout = QFormLayout(platform_group)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([platform.value for platform in Platform])
        self.platform_combo.setCurrentText(Platform.PC.value)
        platform_layout.addRow("Target Platform:", self.platform_combo)
        
        layout.addWidget(platform_group)
        
        # Compression Settings
        compression_group = QGroupBox("🗜️ Compression Settings")
        compression_layout = QVBoxLayout(compression_group)
        
        self.compression_check = QCheckBox("Enable compression (if supported)")
        self.compression_check.setToolTip("Enable compression for supported IMG formats")
        compression_layout.addWidget(self.compression_check)
        
        compression_options_layout = QFormLayout()
        
        self.compression_type_combo = QComboBox()
        self.compression_type_combo.addItems(["ZLib", "LZ4", "Auto"])
        self.compression_type_combo.setEnabled(False)
        compression_options_layout.addRow("Compression Type:", self.compression_type_combo)
        
        self.compression_level_spin = QSpinBox()
        self.compression_level_spin.setRange(1, 9)
        self.compression_level_spin.setValue(6)
        self.compression_level_spin.setEnabled(False)
        compression_options_layout.addRow("Compression Level:", self.compression_level_spin)
        
        compression_layout.addLayout(compression_options_layout)
        
        self.compression_check.toggled.connect(self.compression_type_combo.setEnabled)
        self.compression_check.toggled.connect(self.compression_level_spin.setEnabled)
        
        layout.addWidget(compression_group)
        
        # Encryption Settings
        encryption_group = QGroupBox("🔒 Encryption Settings")
        encryption_layout = QVBoxLayout(encryption_group)
        
        self.encryption_check = QCheckBox("Enable encryption (GTA IV only)")
        self.encryption_check.setToolTip("Enable encryption for GTA IV format")
        self.encryption_check.setEnabled(False)  # Only for GTA IV
        encryption_layout.addWidget(self.encryption_check)
        
        layout.addWidget(encryption_group)
        
        # Advanced Options
        advanced_group = QGroupBox("🔧 Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        self.sector_size_combo = QComboBox()
        self.sector_size_combo.addItems(["2048 bytes (standard)", "4096 bytes", "8192 bytes"])
        advanced_layout.addRow("Sector Size:", self.sector_size_combo)
        
        self.endianness_combo = QComboBox()
        self.endianness_combo.addItems(["Little Endian (PC)", "Big Endian (Console)"])
        advanced_layout.addRow("Byte Order:", self.endianness_combo)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        return tab
    
    def _create_template_tab(self) -> QWidget:
        """Create templates tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Template info
        info_label = QLabel("💡 Templates allow you to save and reuse IMG creation settings.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        layout.addWidget(info_label)
        
        # Template actions
        template_actions_layout = QHBoxLayout()
        
        load_template_btn = QPushButton("📁 Load Template")
        load_template_btn.setToolTip("Load a saved template")
        load_template_btn.clicked.connect(self._load_template)
        template_actions_layout.addWidget(load_template_btn)
        
        save_template_btn = QPushButton("💾 Save as Template")
        save_template_btn.setToolTip("Save current settings as a reusable template")
        save_template_btn.clicked.connect(self._save_template)
        template_actions_layout.addWidget(save_template_btn)
        
        manage_templates_btn = QPushButton("⚙️ Manage Templates")
        manage_templates_btn.setToolTip("Open template manager")
        manage_templates_btn.clicked.connect(self._manage_templates)
        template_actions_layout.addWidget(manage_templates_btn)
        
        template_actions_layout.addStretch()
        layout.addLayout(template_actions_layout)
        
        # Recent templates preview
        recent_group = QGroupBox("🕒 Recent Templates")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_templates_text = QTextEdit()
        self.recent_templates_text.setMaximumHeight(150)
        self.recent_templates_text.setReadOnly(True)
        self.recent_templates_text.setPlaceholderText("No recent templates available...")
        recent_layout.addWidget(self.recent_templates_text)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        return tab
    
    def _create_button_section(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setToolTip("Show help information")
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        # Standard buttons
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.create_btn = QPushButton("✨ Create IMG Archive")
        self.create_btn.setDefault(True)
        self.create_btn.clicked.connect(self._create_img_file)
        button_layout.addWidget(self.create_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _on_game_type_changed(self, radio_button):
        """Handle game type selection change"""
        if not radio_button.isChecked():
            return
        
        self.selected_game_type = radio_button.game_code
        game_info = radio_button.game_info
        
        # Update default values based on game type
        self.initial_size_spin.setValue(game_info['default_size'])
        
        # Enable/disable features based on game capabilities
        self.compression_check.setEnabled(game_info['supports_compression'])
        self.encryption_check.setEnabled(game_info['supports_encryption'])
        
        if not game_info['supports_compression']:
            self.compression_check.setChecked(False)
        
        if not game_info['supports_encryption']:
            self.encryption_check.setChecked(False)
        
        # Update filename suggestion
        if not self.filename_input.text() or self.filename_input.text().startswith('new_'):
            suggested_name = f"{game_info['code']}_custom.img"
            self.filename_input.setText(suggested_name)
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setText(directory)
            self._validate_input()
    
    def _validate_input(self):
        """Validate user input and enable/disable create button"""
        filename = self.filename_input.text().strip()
        output_dir = self.output_dir_input.text().strip()
        
        # Check filename
        valid_filename = bool(filename and not any(c in filename for c in '<>:"|?*'))
        
        # Check output directory
        valid_output_dir = bool(output_dir and os.path.isdir(output_dir))
        
        # Check if file already exists
        file_exists = False
        if valid_filename and valid_output_dir:
            full_path = os.path.join(output_dir, filename)
            file_exists = os.path.exists(full_path)
        
        # Update create button state
        can_create = valid_filename and valid_output_dir
        self.create_btn.setEnabled(can_create)
        
        # Update button text based on file existence
        if file_exists:
            self.create_btn.setText("⚠️ Overwrite IMG Archive")
            self.create_btn.setToolTip("File already exists and will be overwritten")
        else:
            self.create_btn.setText("✨ Create IMG Archive")
            self.create_btn.setToolTip("Create new IMG archive")
    
    def _load_template(self):
        """Load template from template manager"""
        if not self.template_manager:
            QMessageBox.information(self, "Templates", "Template system not available")
            return
        
        # This would open a template selection dialog
        QMessageBox.information(self, "Load Template", "Template loading feature coming soon!")
    
    def _save_template(self):
        """Save current settings as template"""
        if not self.template_manager:
            QMessageBox.information(self, "Templates", "Template system not available")
            return
        
        # This would save current settings
        QMessageBox.information(self, "Save Template", "Template saving feature coming soon!")
    
    def _manage_templates(self):
        """Open template manager"""
        if not self.template_manager:
            QMessageBox.information(self, "Templates", "Template system not available")
            return
        
        # This would open the template manager dialog
        QMessageBox.information(self, "Manage Templates", "Template manager coming soon!")
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
<h3>IMG Factory - Create New Archive</h3>

<h4>Game Types:</h4>
<ul>
<li><b>GTA III:</b> Uses DIR+IMG file pair, limited features</li>
<li><b>GTA Vice City:</b> Enhanced version of GTA III format</li>
<li><b>GTA San Andreas:</b> Single IMG file with header, most popular</li>
<li><b>GTA IV:</b> Advanced format with compression and encryption</li>
<li><b>Bully:</b> Modified San Andreas format</li>
<li><b>Custom:</b> User-defined settings</li>
</ul>

<h4>Settings:</h4>
<ul>
<li><b>Initial Size:</b> Starting size allocation for the IMG file</li>
<li><b>Structure:</b> Create basic folder structure in the archive</li>
<li><b>Compression:</b> Reduce file size (where supported)</li>
<li><b>Encryption:</b> Password protection (GTA IV only)</li>
</ul>

<h4>Templates:</h4>
<p>Save frequently used settings as templates for quick reuse.</p>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def _create_img_file(self):
        """Create the IMG file"""
        try:
            # Collect settings
            settings = self._collect_settings()
            
            # Validate settings
            validation_result = self._validate_settings(settings)
            if not validation_result['valid']:
                QMessageBox.warning(self, "Validation Error", validation_result['message'])
                return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.status_label.setVisible(True)
            self.create_btn.setEnabled(False)
            
            # Start creation thread
            self.creation_thread = IMGCreationThread(settings)
            self.creation_thread.progress_updated.connect(self._update_progress)
            self.creation_thread.creation_completed.connect(self._on_creation_completed)
            self.creation_thread.creation_error.connect(self._on_creation_error)
            self.creation_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start IMG creation:\n{str(e)}")
            self._reset_ui()
    
    def _collect_settings(self) -> Dict:
        """Collect all settings from the dialog"""
        game_info = GameType.get_type(self.selected_game_type)
        
        filename = self.filename_input.text().strip()
        output_dir = self.output_dir_input.text().strip()
        output_path = os.path.join(output_dir, filename)
        
        return {
            'game_type': self.selected_game_type,
            'img_version': game_info['img_version'],
            'filename': filename,
            'output_dir': output_dir,
            'output_path': output_path,
            'initial_size_mb': self.initial_size_spin.value(),
            'platform': Platform(self.platform_combo.currentText()),
            'create_structure': self.auto_structure_check.isChecked(),
            'compression_enabled': self.compression_check.isChecked(),
            'encryption_enabled': self.encryption_check.isChecked(),
            'open_after_create': self.open_after_create_check.isChecked()
        }
    
    def _validate_settings(self, settings: Dict) -> Dict:
        """Validate creation settings"""
        # Check output directory exists
        if not os.path.isdir(settings['output_dir']):
            return {'valid': False, 'message': 'Output directory does not exist'}
        
        # Check write permissions
        try:
            test_file = os.path.join(settings['output_dir'], 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except:
            return {'valid': False, 'message': 'No write permission in output directory'}
        
        # Check filename
        filename = settings['filename']
        if not filename or any(c in filename for c in '<>:"|?*'):
            return {'valid': False, 'message': 'Invalid filename'}
        
        # Check file extension
        if not filename.lower().endswith('.img'):
            return {'valid': False, 'message': 'Filename must end with .img'}
        
        return {'valid': True, 'message': 'Settings are valid'}
    
    def _update_progress(self, progress: int, status: str):
        """Update progress display"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_creation_completed(self, file_path: str):
        """Handle successful IMG creation"""
        self._reset_ui()
        
        # Save to recent settings if template manager available
        if self.template_manager:
            settings = self._collect_settings()
            self.template_manager.save_recent_settings(settings)
        
        # Show success message
        QMessageBox.information(
            self, "Success", 
            f"IMG archive created successfully!\n\nLocation: {file_path}"
        )
        
        # Emit signal and close dialog
        self.img_created.emit(file_path)
        self.accept()
    
    def _on_creation_error(self, error_message: str):
        """Handle IMG creation error"""
        self._reset_ui()
        QMessageBox.critical(self, "Creation Error", f"Failed to create IMG archive:\n{error_message}")
    
    def _reset_ui(self):
        """Reset UI to normal state"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.create_btn.setEnabled(True)
    
    def _load_settings(self):
        """Load saved settings"""
        # Set default output directory to Documents
        try:
            from pathlib import Path
            default_dir = str(Path.home() / "Documents" / "IMG Factory")
            os.makedirs(default_dir, exist_ok=True)
            self.output_dir_input.setText(default_dir)
        except:
            pass
        
        self._validate_input()


# Utility function for integration
def add_new_img_functionality(main_window):
    """Add new IMG functionality to main window"""
    # This function can be called from the main application
    # to add new IMG creation capabilities
    
    # Add menu item
    file_menu = None
    for action in main_window.menuBar().actions():
        if action.text() == "File":
            file_menu = action.menu()
            break
    
    if file_menu:
        new_action = file_menu.addAction("🆕 New IMG Archive...")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: show_new_img_dialog(main_window))
        
        # Insert at the beginning
        actions = file_menu.actions()
        if actions:
            file_menu.insertAction(actions[0], new_action)
            file_menu.insertSeparator(actions[0])


def show_new_img_dialog(parent=None):
    """Show new IMG creation dialog"""
    dialog = NewIMGDialog(parent)
    return dialog.exec()


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the dialog
    dialog = NewIMGDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("IMG creation dialog completed successfully")
    else:
        print("IMG creation dialog cancelled")
    
    sys.exit(app.exec())
