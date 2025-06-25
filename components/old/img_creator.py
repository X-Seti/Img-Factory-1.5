#!/usr/bin/env python3
"""
X-Seti June 05, 2025 - IMG Factory Qt6 - New IMG File Creation
Supports GTA III, Vice City, San Andreas, Stories, and Bully formats
"""

import os
import struct
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QButtonGroup, QLineEdit, QPushButton, QLabel, QComboBox,
    QCheckBox, QTextEdit, QFileDialog, QMessageBox, QFormLayout,
    QSpinBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from img_core_classes import IMGFile, IMGVersion

class GameType(Enum):
    """Supported game types for IMG creation"""
    GTA_III = "gta3"
    GTA_VC = "gtavc" 
    GTA_SA = "gtasa"
    GTA_LC_STORIES = "gtalcs"
    GTA_VC_STORIES = "gtavcs"
    BULLY = "bully"
    MANHUNT = "manhunt"  # Bonus support

class IMGTemplate:
    """Template information for different IMG types"""
    
    TEMPLATES = {
        GameType.GTA_III: {
            "name": "GTA III",
            "description": "Grand Theft Auto III (2001)\nUses IMG Version 1 (DIR/IMG pair)",
            "version": IMGVersion.IMG_1,
            "extension": ".img",
            "has_dir": True,
            "sector_size": 2048,
            "max_entries": 65536,
            "typical_files": ["player.dff", "player.txd", "genericmale02.dff"],
            "icon": "🏙️"
        },
        
        GameType.GTA_VC: {
            "name": "GTA Vice City", 
            "description": "Grand Theft Auto: Vice City (2002)\nUses IMG Version 1 (DIR/IMG pair)",
            "version": IMGVersion.IMG_1,
            "extension": ".img",
            "has_dir": True,
            "sector_size": 2048,
            "max_entries": 65536,
            "typical_files": ["player.dff", "player.txd", "hmoca.dff"],
            "icon": "🌴"
        },
        
        GameType.GTA_SA: {
            "name": "GTA San Andreas",
            "description": "Grand Theft Auto: San Andreas (2004)\nUses IMG Version 2 (Single file with header)",
            "version": IMGVersion.IMG_2,
            "extension": ".img",
            "has_dir": False,
            "sector_size": 2048,
            "max_entries": 2147483647,
            "typical_files": ["cj.dff", "cj.txd", "grove.dff"],
            "icon": "🏜️"
        },
        
        GameType.GTA_LC_STORIES: {
            "name": "GTA Liberty City Stories",
            "description": "Grand Theft Auto: Liberty City Stories (2005)\nUses modified IMG Version 1",
            "version": IMGVersion.IMG_STORIES,
            "extension": ".img", 
            "has_dir": True,
            "sector_size": 2048,
            "max_entries": 65536,
            "typical_files": ["toni.dff", "toni.txd", "lcs_player.dff"],
            "icon": "🏙️📱"
        },
        
        GameType.GTA_VC_STORIES: {
            "name": "GTA Vice City Stories",
            "description": "Grand Theft Auto: Vice City Stories (2006)\nUses modified IMG Version 1", 
            "version": IMGVersion.IMG_STORIES,
            "extension": ".img",
            "has_dir": True,
            "sector_size": 2048,
            "max_entries": 65536,
            "typical_files": ["vic.dff", "vic.txd", "vcs_player.dff"],
            "icon": "🌴📱"
        },
        
        GameType.BULLY: {
            "name": "Bully (Canis Canem Edit)",
            "description": "Bully: Scholarship Edition (2008)\nUses specialized IMG format",
            "version": IMGVersion.IMG_1,  # Similar to IMG1 but with differences
            "extension": ".img",
            "has_dir": True,
            "sector_size": 2048,
            "max_entries": 32768,
            "typical_files": ["player_h.dff", "player_h.txd", "school.dff"],
            "icon": "🏫"
        }
    }

class NewIMGDialog(QDialog):
    """Dialog for creating new IMG files"""
    
    img_created = pyqtSignal(str)  # Emits the path of created IMG file
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG Archive")
        self.setMinimumSize(600, 700)
        self.setModal(True)
        
        self.selected_game_type = GameType.GTA_SA  # Default to most common
        self.output_path = ""
        
        self._create_ui()
        self._connect_signals()
        self._update_template_info()
    
    def _create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Create New IMG Archive")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Game type selection
        self._create_game_selection_section(layout)
        
        # Template information
        self._create_template_info_section(layout)
        
        # File settings
        self._create_file_settings_section(layout)
        
        # Advanced options
        self._create_advanced_options_section(layout)
        
        # Preview
        self._create_preview_section(layout)
        
        # Buttons
        self._create_button_section(layout)
    
    def _create_game_selection_section(self, parent_layout):
        """Create game type selection section"""
        game_group = QGroupBox("🎮 Select Game Type")
        game_layout = QGridLayout(game_group)
        
        self.game_button_group = QButtonGroup()
        
        # Create radio buttons for each game type
        for i, (game_type, template) in enumerate(IMGTemplate.TEMPLATES.items()):
            radio = QRadioButton()
            
            # Create rich label with icon and description
            label_text = f"{template['icon']} {template['name']}"
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; font-size: 11pt;")
            
            desc_label = QLabel(template['description'].split('\n')[0])  # First line only
            desc_label.setStyleSheet("color: #666; font-style: italic; margin-left: 20px;")
            
            # Layout for this game option
            row = i // 2
            col = (i % 2) * 2
            
            game_layout.addWidget(radio, row * 2, col)
            game_layout.addWidget(label, row * 2, col + 1)
            game_layout.addWidget(desc_label, row * 2 + 1, col + 1)
            
            # Store game type reference
            radio.game_type = game_type
            self.game_button_group.addButton(radio)
            
            # Default selection
            if game_type == GameType.GTA_SA:
                radio.setChecked(True)
        
        parent_layout.addWidget(game_group)
    
    def _create_template_info_section(self, parent_layout):
        """Create template information display"""
        info_group = QGroupBox("📋 Template Information")
        info_layout = QVBoxLayout(info_group)
        
        # Template details
        self.template_info_label = QLabel()
        self.template_info_label.setWordWrap(True)
        self.template_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                line-height: 1.4;
            }
        """)
        info_layout.addWidget(self.template_info_label)
        
        parent_layout.addWidget(info_group)
    
    def _create_file_settings_section(self, parent_layout):
        """Create file settings section"""
        file_group = QGroupBox("📁 File Settings")
        file_layout = QFormLayout(file_group)
        
        # File name
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("e.g., custom_models.img")
        self.filename_input.textChanged.connect(self._update_preview)
        file_layout.addRow("Archive Name:", self.filename_input)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("No directory selected")
        self.output_dir_label.setStyleSheet("border: 1px solid #ccc; padding: 4px; background: #f9f9f9;")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output_directory)
        
        dir_layout.addWidget(self.output_dir_label, 1)
        dir_layout.addWidget(browse_btn)
        file_layout.addRow("Output Directory:", dir_layout)
        
        # Initial size (for pre-allocation)
        self.initial_size_spin = QSpinBox()
        self.initial_size_spin.setRange(0, 1000)
        self.initial_size_spin.setValue(10)
        self.initial_size_spin.setSuffix(" MB")
        self.initial_size_spin.setToolTip("Pre-allocate space for the IMG file")
        file_layout.addRow("Initial Size:", self.initial_size_spin)
        
        parent_layout.addWidget(file_group)
    
    def _create_advanced_options_section(self, parent_layout):
        """Create advanced options section"""
        advanced_group = QGroupBox("⚙️ Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["PC", "PlayStation 2", "Xbox", "Mobile"])
        self.platform_combo.setCurrentText("PC")
        advanced_layout.addRow("Target Platform:", self.platform_combo)
        
        # Compression option
        self.compression_check = QCheckBox("Enable compression support")
        self.compression_check.setToolTip("Adds support for compressed entries (where applicable)")
        advanced_layout.addRow("Compression:", self.compression_check)
        
        # Encryption option (for newer formats)
        self.encryption_check = QCheckBox("Enable encryption (GTA IV+ only)")
        self.encryption_check.setEnabled(False)
        self.encryption_check.setToolTip("Encryption only available for IMG Version 3")
        advanced_layout.addRow("Encryption:", self.encryption_check)
        
        # Auto-create directory structure
        self.auto_structure_check = QCheckBox("Create typical directory structure")
        self.auto_structure_check.setChecked(True)
        self.auto_structure_check.setToolTip("Creates common subdirectories for organized modding")
        advanced_layout.addRow("Structure:", self.auto_structure_check)
        
        parent_layout.addWidget(advanced_group)
    
    def _create_preview_section(self, parent_layout):
        """Create preview section"""
        preview_group = QGroupBox("👁️ Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("File preview will appear here...")
        preview_layout.addWidget(self.preview_text)
        
        parent_layout.addWidget(preview_group)
    
    def _create_button_section(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        # Template button
        template_btn = QPushButton("📄 Save as Template")
        template_btn.setToolTip("Save current settings as a reusable template")
        template_btn.clicked.connect(self._save_template)
        button_layout.addWidget(template_btn)
        
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
    
    def _connect_signals(self):
        """Connect all signals"""
        self.game_button_group.buttonClicked.connect(self._on_game_type_changed)
        self.platform_combo.currentTextChanged.connect(self._update_preview)
        self.compression_check.toggled.connect(self._update_preview)
        self.initial_size_spin.valueChanged.connect(self._update_preview)
    
    def _on_game_type_changed(self, button):
        """Handle game type selection change"""
        self.selected_game_type = button.game_type
        self._update_template_info()
        self._update_preview()
        
        # Update encryption availability
        template = IMGTemplate.TEMPLATES[self.selected_game_type]
        self.encryption_check.setEnabled(template['version'] == IMGVersion.IMG_3)
    
    def _update_template_info(self):
        """Update template information display"""
        template = IMGTemplate.TEMPLATES[self.selected_game_type]
        
        info_html = f"""
        <h3>{template['icon']} {template['name']}</h3>
        <p><strong>Description:</strong> {template['description'].replace(chr(10), '<br>')}</p>
        <p><strong>IMG Version:</strong> {template['version'].name}</p>
        <p><strong>File Structure:</strong> {'DIR/IMG pair' if template['has_dir'] else 'Single IMG file'}</p>
        <p><strong>Sector Size:</strong> {template['sector_size']} bytes</p>
        <p><strong>Max Entries:</strong> {template['max_entries']:,}</p>
        <p><strong>Typical Files:</strong> {', '.join(template['typical_files'][:3])}...</p>
        """
        
        self.template_info_label.setText(info_html)
    
    def _update_preview(self):
        """Update the preview display"""
        if not self.filename_input.text() or not hasattr(self, 'output_path') or not self.output_path:
            self.preview_text.setPlainText("Enter filename and select output directory to see preview")
            return
        
        template = IMGTemplate.TEMPLATES[self.selected_game_type]
        filename = self.filename_input.text()
        
        # Ensure proper extension
        if not filename.endswith(template['extension']):
            filename += template['extension']
        
        preview_lines = [
            f"📂 Game Type: {template['name']}",
            f"📄 IMG Version: {template['version'].name}",
            f"💾 Platform: {self.platform_combo.currentText()}",
            f"📁 Output Directory: {self.output_path}",
            f"📋 Main File: {filename}",
        ]
        
        if template['has_dir']:
            dir_filename = filename.replace('.img', '.dir')
            preview_lines.append(f"📋 Directory File: {dir_filename}")
        
        preview_lines.extend([
            f"💾 Initial Size: {self.initial_size_spin.value()} MB",
            f"🗜️ Compression: {'Enabled' if self.compression_check.isChecked() else 'Disabled'}",
        ])
        
        if template['version'] == IMGVersion.IMG_3:
            preview_lines.append(f"🔒 Encryption: {'Enabled' if self.encryption_check.isChecked() else 'Disabled'}")
        
        if self.auto_structure_check.isChecked():
            preview_lines.append("📁 Will create: models/, textures/, audio/ subdirectories")
        
        self.preview_text.setPlainText('\n'.join(preview_lines))
    
    def _browse_output_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_path = directory
            self.output_dir_label.setText(directory)
            self._update_preview()
    
    def _save_template(self):
        """Save current settings as template"""
        # Implementation for saving user templates
        QMessageBox.information(self, "Template Saved", 
                              "Template saving will be implemented in a future version!")
    
    def _load_template(self):
        """Load template from template manager"""
    # Implementation from artifact above

    def _create_img_file(self):
        """Create the IMG file with current settings"""
        # Validate inputs
        if not self.filename_input.text():
            QMessageBox.warning(self, "Validation Error", "Please enter a filename")
            return
        
        if not self.output_path:
            QMessageBox.warning(self, "Validation Error", "Please select an output directory")
            return
        
        try:
            creator = IMGCreator(self.selected_game_type)
            
            # Build creation parameters
            params = {
                'filename': self.filename_input.text(),
                'output_dir': self.output_path,
                'platform': self.platform_combo.currentText(),
                'initial_size_mb': self.initial_size_spin.value(),
                'compression_enabled': self.compression_check.isChecked(),
                'encryption_enabled': self.encryption_check.isChecked(),
                'create_structure': self.auto_structure_check.isChecked()
            }
            
            # Create the IMG file
            created_path = creator.create_img(**params)
            
            # Success
            QMessageBox.information(self, "Success", 
                                  f"IMG archive created successfully!\n\nLocation: {created_path}")
            
            self.img_created.emit(created_path)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Creation Error", 
                               f"Failed to create IMG archive:\n\n{str(e)}")

class IMGCreator:
    """Core IMG file creation functionality"""
    
    def __init__(self, game_type: GameType):
        self.game_type = game_type
        self.template = IMGTemplate.TEMPLATES[game_type]
    
    def create_img(self, **params) -> str:
        """Create IMG file with specified parameters"""
        filename = params['filename']
        output_dir = params['output_dir']
        
        # Ensure proper extension
        if not filename.endswith(self.template['extension']):
            filename += self.template['extension']
        
        img_path = os.path.join(output_dir, filename)
        
        # Create based on IMG version
        if self.template['version'] == IMGVersion.IMG_1:
            return self._create_img_version1(img_path, **params)
        elif self.template['version'] == IMGVersion.IMG_2:
            return self._create_img_version2(img_path, **params)
        elif self.template['version'] == IMGVersion.IMG_STORIES:
            return self._create_img_stories(img_path, **params)
        else:
            raise ValueError(f"Unsupported IMG version: {self.template['version']}")
    
    def _create_img_version1(self, img_path: str, **params) -> str:
        """Create IMG Version 1 (GTA III/VC style)"""
        dir_path = img_path.replace('.img', '.dir')
        
        # Create empty DIR file (will contain entry headers)
        with open(dir_path, 'wb') as dir_file:
            # Empty DIR file - entries will be added later
            pass
        
        # Create IMG file with initial size
        initial_size = params.get('initial_size_mb', 10) * 1024 * 1024
        with open(img_path, 'wb') as img_file:
            # Fill with zeros to reserve space
            img_file.write(b'\x00' * initial_size)
        
        # Create directory structure if requested
        if params.get('create_structure', False):
            self._create_directory_structure(os.path.dirname(img_path))
        
        return img_path
    
    def _create_img_version2(self, img_path: str, **params) -> str:
        """Create IMG Version 2 (GTA SA style)"""
        with open(img_path, 'wb') as img_file:
            # Write IMG Version 2 header
            img_file.write(b'VER2')  # Signature
            img_file.write(struct.pack('<I', 0))  # Entry count (initially 0)
            
            # Reserve space for entries (will be added later)
            initial_size = params.get('initial_size_mb', 10) * 1024 * 1024
            img_file.write(b'\x00' * (initial_size - 8))  # Subtract header size
        
        # Create directory structure if requested
        if params.get('create_structure', False):
            self._create_directory_structure(os.path.dirname(img_path))
        
        return img_path
    
    def _create_img_stories(self, img_path: str, **params) -> str:
        """Create IMG Stories format"""
        # Stories format is similar to Version 1 but with different internal structure
        return self._create_img_version1(img_path, **params)
    
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
                readme.write(f"Created by IMG Factory\n")
                readme.write(f"Game: {self.template['name']}\n")

# Integration function for ImgFactoryDemo
def add_new_img_functionality(main_window):
    """Add 'New IMG' functionality to the main window"""
    
    def create_new_img():
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(main_window)
        dialog.img_created.connect(lambda path: main_window.load_img_file(path))
        dialog.exec()
    
    # Add to File menu
    file_menu = None
    for action in main_window.menuBar().actions():
        if action.text() == "File":
            file_menu = action.menu()
            break
    
    if file_menu:
        # Add separator and new action
        file_menu.insertSeparator(file_menu.actions()[1])  # After "Open IMG"
        
        new_action = file_menu.addAction("New IMG Archive...")
        new_action.setShortcut("Ctrl+N") 
        new_action.triggered.connect(create_new_img)
        
        # Move to correct position
        actions = file_menu.actions()
        file_menu.removeAction(new_action)
        file_menu.insertAction(actions[1], new_action)  # Insert after "Open IMG"
    
    # Also add to IMG menu if it exists
    img_menu = None
    for action in main_window.menuBar().actions():
        if action.text() == "IMG":
            img_menu = action.menu()
            break
    
    if img_menu:
        new_img_action = img_menu.addAction("New IMG Archive...")
        new_img_action.triggered.connect(create_new_img)
        
        # Move to top
        actions = img_menu.actions()
        img_menu.removeAction(new_img_action)
        img_menu.insertAction(actions[0], new_img_action)
    
    # Add toolbar button
    main_window.new_img_btn = main_window.themed_button("🆕 New IMG", "import", "document-new")
    main_window.new_img_btn.clicked.connect(create_new_img)
    
    return create_new_img
