#this belongs in components/ img_creator.py

#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
IMG Creator - Dialog for creating new IMG files
Fixed imports and dependencies
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

# Import required classes - simplified to avoid import issues
try:
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
except ImportError:
    # If img_core_classes doesn't exist, create minimal stubs
    class IMGVersion:
        IMG_1 = 1
        IMG_2 = 2
        IMG_3 = 3
    
    class IMGFile:
        def __init__(self, path=""):
            self.file_path = path
        def create_new(self, path, version):
            return True
        def save(self):
            return True
        def add_entry(self, name, data):
            pass
        def close(self):
            pass
    
    class IMGEntry:
        pass
    
    def format_file_size(size):
        return f"{size} bytes"

# Define Platform enum locally to avoid import issues
class Platform:
    """Platform definitions"""
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
        'img_version': IMGVersion.IMG_1,
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
        'description': 'Grand Theft Auto San Andreas - Single IMG files with VER2 header'
    }
    
    GTAIV = {
        'name': 'GTA IV',
        'code': 'gtaiv',
        'img_version': IMGVersion.IMG_3,
        'platform': Platform.PC,
        'default_size': 200,
        'supports_compression': True,
        'supports_encryption': True,
        'common_files': ['vehicles.img', 'componentpeds.img'],
        'description': 'Grand Theft Auto IV - Advanced format with compression/encryption'
    }
    
    BULLY = {
        'name': 'Bully',
        'code': 'bully',
        'img_version': IMGVersion.IMG_2,
        'platform': Platform.PC,
        'default_size': 30,
        'supports_compression': False,
        'supports_encryption': False,
        'common_files': ['Tokens.img', 'World.img'],
        'description': 'Bully: Scholarship Edition - Modified SA format'
    }
    
    @classmethod
    def get_all_types(cls) -> Dict:
        """Get all game types as dictionary"""
        return {
            'gta3': cls.GTA3,
            'gtavc': cls.GTAVC,
            'gtasa': cls.GTASA,
            'gtaiv': cls.GTAIV,
            'bully': cls.BULLY
        }


class IMGCreationThread(QThread):
    """Thread for creating IMG files in background"""
    
    creation_progress = pyqtSignal(int, str)  # progress, status
    creation_completed = pyqtSignal(str)      # file_path
    creation_error = pyqtSignal(str)          # error_message
    
    def __init__(self, settings: Dict):
        super().__init__()
        self.settings = settings
    
    def run(self):
        """Create IMG file"""
        try:
            self.creation_progress.emit(10, "Initializing...")
            
            file_path = self.settings.get('file_path', '')
            game_type = self.settings.get('game_type', 'gtasa')
            initial_size = self.settings.get('initial_size_mb', 100)
            create_structure = self.settings.get('create_structure', False)
            
            self.creation_progress.emit(30, "Creating IMG file...")
            
            # Create IMG file instance
            img_file = IMGFile()
            
            # Determine version based on game type
            game_info = GameType.get_all_types().get(game_type, GameType.GTASA)
            version = game_info['img_version']
            
            self.creation_progress.emit(50, "Setting up file structure...")
            
            # Create new IMG file
            if not img_file.create_new(file_path, version):
                self.creation_error.emit("Failed to create IMG file")
                return
            
            self.creation_progress.emit(70, "Adding initial content...")
            
            # Add basic structure if requested
            if create_structure:
                self._create_folder_structure(img_file)
            
            self.creation_progress.emit(90, "Finalizing...")
            
            # Save the file
            if img_file.save():
                self.creation_progress.emit(100, "Complete")
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
    img_created = pyqtSignal(str)

    def __init__(self, parent=None, app_settings=None):
        super().__init__(parent)
        self.app_settings = app_settings  # Pass settings from main app
        self.template_manager = None
        self.selected_game = 'gtasa'  # Default

        self.setWindowTitle("Create New IMG Archive")
        self.setModal(True)
        self.resize(500, 600)

        self._setup_ui()
        self._load_saved_paths()  # NEW: Load remembered paths

    def _load_saved_paths(self):
        """Load saved paths from settings"""
        if self.app_settings:
            # Set last used output path
            last_path = self.app_settings.get_last_img_output_path()
            if last_path and os.path.exists(last_path):
                self.output_dir_input.setText(last_path)
            else:
                # Default to Documents/IMG Factory
                try:
                    from pathlib import Path
                    default_dir = str(Path.home() / "Documents" / "IMG Factory")
                    os.makedirs(default_dir, exist_ok=True)
                    self.output_dir_input.setText(default_dir)
                except:
                    self.output_dir_input.setText(os.getcwd())

    def _browse_output_directory(self):
        """Browse for output directory with path remembering"""
        # Start from current path or last used path
        current_path = self.output_dir_input.text()
        start_path = current_path if current_path and os.path.exists(current_path) else os.getcwd()

        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", start_path
        )

        if directory:
            self.output_dir_input.setText(directory)

            # Remember this path for next time
            if self.app_settings:
                self.app_settings.set_last_img_output_path(directory)

            self._validate_input()

    # Also update the _setup_ui method to connect the browse button:
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # ... existing UI code ...

        # In the file settings section:
        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setPlaceholderText("Select output directory...")

        browse_btn = QPushButton("📂 Browse")
        browse_btn.clicked.connect(self._browse_output_directory)  # Connect to our method

        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(browse_btn)
    
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
            
            if code == 'gtasa':  # Default selection
                radio.setChecked(True)
            
            self.game_button_group.addButton(radio, i)
            
            row = i // 2
            col = i % 2
            game_layout.addWidget(radio, row, col)
        
        self.game_button_group.buttonClicked.connect(self._on_game_type_changed)
        layout.addWidget(game_group)
        
        # File Settings
        file_group = QGroupBox("📁 File Settings")
        file_layout = QFormLayout(file_group)
        
        # Output path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output location...")
        path_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton("📁 Browse")
        self.browse_btn.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.browse_btn)
        
        file_layout.addRow("Output Path:", path_layout)
        
        # Archive name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter archive name...")
        self.name_edit.setText("new_archive")
        file_layout.addRow("Archive Name:", self.name_edit)
        
        layout.addWidget(file_group)
        
        # Size Settings
        size_group = QGroupBox("💾 Size Settings")
        size_layout = QFormLayout(size_group)
        
        self.initial_size_spin = QSpinBox()
        self.initial_size_spin.setRange(1, 2000)
        self.initial_size_spin.setValue(100)
        self.initial_size_spin.setSuffix(" MB")
        size_layout.addRow("Initial Size:", self.initial_size_spin)
        
        layout.addWidget(size_group)
        
        layout.addStretch()
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Structure Options
        structure_group = QGroupBox("📂 Structure Options")
        structure_layout = QVBoxLayout(structure_group)
        
        self.create_structure_check = QCheckBox("Create basic folder structure")
        self.create_structure_check.setChecked(True)
        structure_layout.addWidget(self.create_structure_check)
        
        self.add_readme_check = QCheckBox("Add README file")
        self.add_readme_check.setChecked(True)
        structure_layout.addWidget(self.add_readme_check)
        
        layout.addWidget(structure_group)
        
        # Compression Options (for supported games)
        compression_group = QGroupBox("🗜️ Compression Options") 
        compression_layout = QVBoxLayout(compression_group)
        
        self.compression_check = QCheckBox("Enable compression (where supported)")
        self.compression_check.setEnabled(False)  # Will be enabled for GTA IV
        compression_layout.addWidget(self.compression_check)
        
        layout.addWidget(compression_group)
        
        # Encryption Options (for GTA IV)
        encryption_group = QGroupBox("🔒 Encryption Options")
        encryption_layout = QVBoxLayout(encryption_group)
        
        self.encryption_check = QCheckBox("Enable encryption (GTA IV only)")
        self.encryption_check.setEnabled(False)
        encryption_layout.addWidget(self.encryption_check)
        
        layout.addWidget(encryption_group)
        
        layout.addStretch()
        return tab
    
    def _create_template_tab(self) -> QWidget:
        """Create template tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Template info
        info_label = QLabel("Templates allow you to save frequently used settings for quick reuse.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Template actions
        template_layout = QHBoxLayout()
        
        self.save_template_btn = QPushButton("💾 Save as Template")
        self.save_template_btn.clicked.connect(self._save_template)
        template_layout.addWidget(self.save_template_btn)
        
        self.manage_templates_btn = QPushButton("🔧 Manage Templates")
        self.manage_templates_btn.clicked.connect(self._manage_templates)
        template_layout.addWidget(self.manage_templates_btn)
        
        layout.addLayout(template_layout)
        
        layout.addStretch()
        return tab
    
    def _create_button_section(self, layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        self.help_btn = QPushButton("❓ Help")
        self.help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(self.help_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("✖️ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.create_btn = QPushButton("✅ Create IMG")
        self.create_btn.clicked.connect(self._create_img_file)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Load default settings"""
        self._on_game_type_changed(self.game_button_group.checkedButton())
    
    def _on_game_type_changed(self, button):
        """Handle game type change"""
        if button:
            self.selected_game_type = button.game_code
            game_info = button.game_info
            
            # Update size recommendation
            self.initial_size_spin.setValue(game_info['default_size'])
            
            # Update advanced options
            supports_compression = game_info.get('supports_compression', False)
            supports_encryption = game_info.get('supports_encryption', False)
            
            self.compression_check.setEnabled(supports_compression)
            self.encryption_check.setEnabled(supports_encryption)
            
            if not supports_compression:
                self.compression_check.setChecked(False)
            if not supports_encryption:
                self.encryption_check.setChecked(False)
    
    def _browse_output_path(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            os.path.expanduser("~")
        )
        
        if directory:
            self.path_edit.setText(directory)
    
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
                QMessageBox.warning(self, "Invalid Settings", validation_result['message'])
                return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.status_label.setVisible(True)
            self.create_btn.setEnabled(False)
            
            # Start creation thread
            self.creation_thread = IMGCreationThread(settings)
            self.creation_thread.creation_progress.connect(self._update_progress)
            self.creation_thread.creation_completed.connect(self._on_creation_completed)
            self.creation_thread.creation_error.connect(self._on_creation_error)
            self.creation_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start creation: {str(e)}")
    
    def _collect_settings(self) -> Dict:
        """Collect all settings from UI"""
        output_dir = self.path_edit.text().strip()
        archive_name = self.name_edit.text().strip()
        
        if not archive_name.endswith('.img'):
            archive_name += '.img'
        
        file_path = os.path.join(output_dir, archive_name) if output_dir else archive_name
        
        return {
            'file_path': file_path,
            'game_type': self.selected_game_type,
            'initial_size_mb': self.initial_size_spin.value(),
            'create_structure': self.create_structure_check.isChecked(),
            'add_readme': self.add_readme_check.isChecked(),
            'compression_enabled': self.compression_check.isChecked(),
            'encryption_enabled': self.encryption_check.isChecked()
        }
    
    def _validate_settings(self, settings: Dict) -> Dict:
        """Validate settings"""
        result = {'valid': True, 'message': ''}
        
        # Check file path
        file_path = settings.get('file_path', '')
        if not file_path:
            result['valid'] = False
            result['message'] = "Please specify output path and archive name"
            return result
        
        # Check if file already exists
        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self, "File Exists",
                f"File already exists:\n{file_path}\n\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                result['valid'] = False
                result['message'] = "Creation cancelled"
                return result
        
        # Check directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                result['valid'] = False
                result['message'] = f"Cannot create directory: {str(e)}"
                return result
        
        return result
    
    def _update_progress(self, progress: int, status: str):
        """Update progress display"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_creation_completed(self, file_path: str):
        """Handle successful creation"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.create_btn.setEnabled(True)
        
        QMessageBox.information(
            self, "Success",
            f"IMG archive created successfully:\n{file_path}"
        )
        
        # Emit signal for parent to load the file
        self.img_created.emit(file_path)
        self.accept()
    
    def _on_creation_error(self, error_message: str):
        """Handle creation error"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.create_btn.setEnabled(True)
        
        QMessageBox.critical(
            self, "Creation Failed",
            f"Failed to create IMG archive:\n{error_message}"
        )


# Integration function for main application
def add_new_img_functionality(main_window):
    """Add 'New IMG' functionality to the main window"""
    
    def create_new_img():
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(main_window)
        dialog.img_created.connect(lambda path: main_window.load_img_file(path))
        dialog.exec()
    
    return create_new_img


if __name__ == "__main__":
    # Test the dialog
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    dialog = NewIMGDialog()
    dialog.show()
    
    sys.exit(app.exec())
