#!/usr/bin/env python3
"""
IMG Factory Qt6 - Quick Start Wizard
Simplified wizard for beginners to create IMG files quickly
"""

import os
from typing import Dict, Any, Optional
from enum import Enum

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QLineEdit, QTextEdit, QFrame,
    QProgressBar, QWidget, QStackedWidget, QWizard, QWizardPage,
    QFormLayout, QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPalette, QMovie

from new_img_creator import GameType, NewIMGDialog
from img_creation_validator import IMGCreationValidator

class WizardMode(Enum):
    """Different wizard modes for different user types"""
    BEGINNER = "beginner"
    QUICK = "quick"
    GUIDED = "guided"

class QuickStartWizard(QWizard):
    """Simplified wizard for creating IMG files quickly"""
    
    img_created = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMG Quick Start Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Wizard data
        self.wizard_data = {}
        self.validator = IMGCreationValidator()
        
        # Set up wizard appearance
        self._setup_wizard_style()
        
        # Create wizard pages
        self._create_welcome_page()
        self._create_game_selection_page() 
        self._create_quick_setup_page()
        self._create_confirmation_page()
        self._create_creation_page()
        
        # Configure navigation
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.DisabledBackButtonOnLastPage, True)
    
    def _setup_wizard_style(self):
        """Setup modern wizard styling"""
        self.setStyleSheet("""
            QWizard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QWizardPage {
                background: white;
                border-radius: 8px;
                margin: 10px;
            }
            QLabel[heading="true"] {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            QLabel[subtitle="true"] {
                font-size: 12pt;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
            QRadioButton {
                font-size: 11pt;
                padding: 8px;
                margin: 4px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QPushButton {
                font-size: 11pt;
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
    
    def _create_welcome_page(self):
        """Create the welcome page"""
        page = QWizardPage()
        page.setTitle("Welcome to IMG Factory")
        page.setSubTitle("Create custom IMG archives for GTA games in just a few steps")
        
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Welcome content
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 30px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)
        
        # Title
        title_label = QLabel("🏗️ IMG Factory Quick Start")
        title_label.setProperty("heading", True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; background: transparent;")
        welcome_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Create custom IMG archives for your favorite GTA games")
        desc_label.setProperty("subtitle", True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
        welcome_layout.addWidget(desc_label)
        
        layout.addWidget(welcome_frame)
        
        # Features list
        features_frame = QFrame()
        features_layout = QVBoxLayout(features_frame)
        
        features_title = QLabel("What you can do:")
        features_title.setProperty("heading", True)
        features_layout.addWidget(features_title)
        
        features = [
            "🎮 Support for GTA III, Vice City, San Andreas, IV, and more",
            "⚡ Quick setup with smart defaults",
            "🔧 Advanced options for experienced users", 
            "✅ Built-in validation and error checking",
            "📁 Automatic directory structure creation"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("font-size: 11pt; margin: 4px 0px;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_frame)
        
        # Mode selection
        mode_frame = QGroupBox("Choose your experience level:")
        mode_layout = QVBoxLayout(mode_frame)
        
        self.mode_group = QButtonGroup()
        
        # Beginner mode
        beginner_radio = QRadioButton("🔰 Beginner - I'm new to IMG modding")
        beginner_radio.setChecked(True)
        beginner_radio.mode = WizardMode.BEGINNER
        self.mode_group.addButton(beginner_radio)
        mode_layout.addWidget(beginner_radio)
        
        # Quick mode
        quick_radio = QRadioButton("⚡ Quick - I know what I want")
        quick_radio.mode = WizardMode.QUICK
        self.mode_group.addButton(quick_radio)
        mode_layout.addWidget(quick_radio)
        
        # Guided mode
        guided_radio = QRadioButton("🎯 Guided - Help me choose the best options")
        guided_radio.mode = WizardMode.GUIDED
        self.mode_group.addButton(guided_radio)
        mode_layout.addWidget(guided_radio)
        
        layout.addWidget(mode_frame)
        layout.addStretch()
        
        self.addPage(page)
    
    def _create_game_selection_page(self):
        """Create game selection page"""
        page = QWizardPage()
        page.setTitle("Select Your Game")
        page.setSubTitle("Choose the GTA game you want to create mods for")
        
        layout = QVBoxLayout(page)
        
        # Game selection grid
        self.game_group = QButtonGroup()
        
        games_data = [
            (GameType.GTA_III, "🏙️ GTA III", "Classic Liberty City", "#e74c3c"),
            (GameType.GTA_VC, "🌴 GTA Vice City", "80s Miami vibes", "#f39c12"),
            (GameType.GTA_SA, "🏜️ GTA San Andreas", "Grove Street, home", "#27ae60"),
            (GameType.GTA_IV, "🌆 GTA IV", "Modern Liberty City", "#3498db"),
            (GameType.BULLY, "🏫 Bully", "Bullworth Academy", "#9b59b6")
        ]
        
        for i, (game_type, title, desc, color) in enumerate(games_data):
            game_frame = QFrame()
            game_frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid #ecf0f1;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                    background: white;
                }}
                QFrame:hover {{
                    border-color: {color};
                    background: #f8f9fa;
                }}
            """)
            
            game_layout = QHBoxLayout(game_frame)
            
            # Radio button
            radio = QRadioButton()
            radio.game_type = game_type
            self.game_group.addButton(radio)
            game_layout.addWidget(radio)
            
            # Game info
            info_layout = QVBoxLayout()
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-weight: bold; font-size: 14pt; color: {color};")
            info_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
            info_layout.addWidget(desc_label)
            
            game_layout.addLayout(info_layout, 1)
            layout.addWidget(game_frame)
            
            # Default selection (GTA SA)
            if game_type == GameType.GTA_SA:
                radio.setChecked(True)
        
        layout.addStretch()
        
        # Register field for validation
        page.registerField("game_type*", self.game_group, "checkedButton")
        
        self.addPage(page)
    
    def _create_quick_setup_page(self):
        """Create quick setup page"""
        page = QWizardPage()
        page.setTitle("Quick Setup")
        page.setSubTitle("Configure your IMG archive")
        
        layout = QVBoxLayout(page)
        
        # Basic settings form
        form_layout = QFormLayout()
        
        # Archive name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my_custom_mod")
        self.name_input.textChanged.connect(self._update_preview)
        form_layout.addRow("Archive Name:", self.name_input)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        self.dir_input.setPlaceholderText("Click Browse to select...")
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.clicked.connect(self._browse_directory)
        
        dir_layout.addWidget(self.dir_input, 1)
        dir_layout.addWidget(browse_btn)
        form_layout.addRow("Save Location:", dir_layout)
        
        # Purpose/type (affects size and settings)
        self.purpose_combo = QComboBox()
        purposes = [
            ("Small Mod (vehicles, weapons)", 50),
            ("Medium Mod (map additions)", 150),
            ("Large Mod (total conversion)", 300),
            ("Texture Pack", 200),
            ("Custom (I'll choose size)", 100)
        ]
        
        for purpose_name, size in purposes:
            self.purpose_combo.addItem(purpose_name, size)
        
        self.purpose_combo.currentTextChanged.connect(self._update_size_recommendation)
        form_layout.addRow("What are you making?", self.purpose_combo)
        
        # Size (auto-filled based on purpose)
        self.size_display = QLabel("100 MB (recommended)")
        self.size_display.setStyleSheet("color: #27ae60; font-weight: bold;")
        form_layout.addRow("Archive Size:", self.size_display)
        
        layout.addLayout(form_layout)
        
        # Advanced options (collapsible)
        self.advanced_frame = QFrame()
        self.advanced_frame.setVisible(False)
        advanced_layout = QFormLayout(self.advanced_frame)
        
        self.compression_check = QCheckBox("Enable compression (saves space)")
        self.compression_check.setChecked(True)
        advanced_layout.addRow("Compression:", self.compression_check)
        
        self.structure_check = QCheckBox("Create modding folders")
        self.structure_check.setChecked(True)
        advanced_layout.addRow("Directory Structure:", self.structure_check)
        
        layout.addWidget(self.advanced_frame)
        
        # Advanced toggle
        self.advanced_btn = QPushButton("⚙️ Show Advanced Options")
        self.advanced_btn.clicked.connect(self._toggle_advanced)
        layout.addWidget(self.advanced_btn)
        
        # Preview area
        preview_frame = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_frame)
        layout.addStretch()
        
        # Register required fields
        page.registerField("archive_name*", self.name_input)
        page.registerField("output_dir*", self.dir_input)
        
        self.addPage(page)
    
    def _create_confirmation_page(self):
        """Create confirmation page"""
        page = QWizardPage()
        page.setTitle("Ready to Create")
        page.setSubTitle("Review your settings before creating the IMG archive")
        
        layout = QVBoxLayout(page)
        
        # Summary display
        summary_frame = QGroupBox("📋 Summary")
        summary_layout = QVBoxLayout(summary_frame)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_frame)
        
        # Validation results
        validation_frame = QGroupBox("✅ Validation")
        validation_layout = QVBoxLayout(validation_frame)
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        validation_layout.addWidget(self.validation_text)
        
        layout.addWidget(validation_frame)
        
        # Tips
        tips_frame = QGroupBox("💡 Tips")
        tips_layout = QVBoxLayout(tips_frame)
        
        tips = [
            "💾 Your IMG archive will be created in the selected directory",
            "📁 Additional folders will be created for organizing your mods",
            "🔄 You can always create more archives later",
            "📖 Check the documentation for advanced usage"
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet("margin: 2px 0px;")
            tips_layout.addWidget(tip_label)
        
        layout.addWidget(tips_frame)
        layout.addStretch()
        
        self.addPage(page)
    
    def _create_creation_page(self):
        """Create the creation progress page"""
        page = QWizardPage()
        page.setTitle("Creating Your IMG Archive")
        page.setSubTitle("Please wait while your IMG archive is being created...")
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # Progress animation area
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 12px;
                padding: 40px;
            }
        """)
        progress_layout = QVBoxLayout(progress_frame)
        
        # Status label
        self.status_label = QLabel("🔄 Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Current step
        self.step_label = QLabel("Preparing to create IMG archive...")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet("color: #7f8c8d; font-size: 11pt;")
        progress_layout.addWidget(self.step_label)
        
        layout.addWidget(progress_frame)
        
        # Results area (hidden initially)
        self.results_frame = QFrame()
        self.results_frame.setVisible(False)
        results_layout = QVBoxLayout(self.results_frame)
        
        self.results_label = QLabel()
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.results_label)
        
        # Action buttons (shown after completion)
        self.action_buttons = QHBoxLayout()
        
        self.open_folder_btn = QPushButton("📂 Open Folder")
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        self.action_buttons.addWidget(self.open_folder_btn)
        
        self.load_img_btn = QPushButton("📋 Load IMG")
        self.load_img_btn.clicked.connect(self._load_created_img)
        self.action_buttons.addWidget(self.load_img_btn)
        
        results_layout.addLayout(self.action_buttons)
        layout.addWidget(self.results_frame)
        
        layout.addStretch()
        
        self.addPage(page)
    
    def _browse_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.dir_input.setText(directory)
            self._update_preview()
    
    def _toggle_advanced(self):
        """Toggle advanced options visibility"""
        visible = self.advanced_frame.isVisible()
        self.advanced_frame.setVisible(not visible)
        
        if visible:
            self.advanced_btn.setText("⚙️ Show Advanced Options")
        else:
            self.advanced_btn.setText("⚙️ Hide Advanced Options")
    
    def _update_size_recommendation(self):
        """Update size recommendation based on purpose"""
        current_data = self.purpose_combo.currentData()
        if current_data:
            self.size_display.setText(f"{current_data} MB (recommended)")
            self._update_preview()
    
    def _update_preview(self):
        """Update the preview text"""
        if not hasattr(self, 'preview_text'):
            return
        
        name = self.name_input.text() or "my_archive"
        directory = self.dir_input.text() or "Not selected"
        purpose = self.purpose_combo.currentText()
        size = self.purpose_combo.currentData() or 100
        
        preview_lines = [
            f"📄 Archive: {name}.img",
            f"📁 Location: {directory}",
            f"🎯 Purpose: {purpose}",
            f"💾 Size: {size} MB",
        ]
        
        if hasattr(self, 'compression_check') and self.compression_check.isChecked():
            preview_lines.append("🗜️ Compression: Enabled")
        
        if hasattr(self, 'structure_check') and self.structure_check.isChecked():
            preview_lines.append("📁 Structure: Will create folders")
        
        self.preview_text.setPlainText('\n'.join(preview_lines))
    
    def initializePage(self, page_id):
        """Initialize page when it becomes current"""
        super().initializePage(page_id)
        
        if page_id == 3:  # Confirmation page
            self._update_confirmation_page()
        elif page_id == 4:  # Creation page
            self._start_creation_process()
    
    def _update_confirmation_page(self):
        """Update the confirmation page with current settings"""
        # Collect all wizard data
        self._collect_wizard_data()
        
        # Generate summary
        summary_lines = [
            f"🎮 Game: {self.wizard_data['game_type'].name}",
            f"📄 Archive Name: {self.wizard_data['archive_name']}.img",
            f"📁 Output Directory: {self.wizard_data['output_dir']}",
            f"🎯 Purpose: {self.wizard_data['purpose']}",
            f"💾 Size: {self.wizard_data['size']} MB",
            f"🗜️ Compression: {'Enabled' if self.wizard_data['compression'] else 'Disabled'}",
            f"📁 Directory Structure: {'Yes' if self.wizard_data['create_structure'] else 'No'}",
        ]
        
        self.summary_text.setPlainText('\n'.join(summary_lines))
        
        # Run validation
        validation_result = self.validator.validate_creation_params(**self.wizard_data)
        
        validation_lines = [
            self.validator.get_validation_summary(validation_result),
            ""
        ]
        
        for issue in validation_result.issues[:5]:  # Show first 5 issues
            icon = "❌" if issue.level.value in ["error", "critical"] else "⚠️" if issue.level.value == "warning" else "ℹ️"
            validation_lines.append(f"{icon} {issue.message}")
        
        if len(validation_result.issues) > 5:
            validation_lines.append(f"... and {len(validation_result.issues) - 5} more")
        
        self.validation_text.setPlainText('\n'.join(validation_lines))
    
    def _collect_wizard_data(self):
        """Collect all data from wizard pages"""
        # Get selected game
        for button in self.game_group.buttons():
            if button.isChecked():
                self.wizard_data['game_type'] = button.game_type
                break
        
        # Get basic settings
        self.wizard_data['archive_name'] = self.name_input.text()
        self.wizard_data['output_dir'] = self.dir_input.text()
        self.wizard_data['purpose'] = self.purpose_combo.currentText()
        self.wizard_data['size'] = self.purpose_combo.currentData()
        
        # Get advanced settings
        self.wizard_data['compression'] = getattr(self.compression_check, 'isChecked', lambda: True)()
        self.wizard_data['create_structure'] = getattr(self.structure_check, 'isChecked', lambda: True)()
        
        # Convert to IMG creator parameters
        self.wizard_data.update({
            'filename': self.wizard_data['archive_name'],
            'initial_size_mb': self.wizard_data['size'],
            'compression_enabled': self.wizard_data['compression'],
            'encryption_enabled': False,  # Not exposed in quick wizard
            'platform': 'PC'
        })
    
    def _start_creation_process(self):
        """Start the IMG creation process"""
        from PyQt6.QtCore import QTimer
        
        # Simulate creation process with progress updates
        self.creation_steps = [
            (10, "🔍 Validating settings..."),
            (30, "📁 Creating directory structure..."),
            (50, "💾 Initializing IMG archive..."),
            (70, "🔧 Configuring archive settings..."),
            (90, "✅ Finalizing creation..."),
            (100, "🎉 IMG archive created successfully!")
        ]
        
        self.current_step = 0
        self.creation_timer = QTimer()
        self.creation_timer.timeout.connect(self._update_creation_progress)
        self.creation_timer.start(1000)  # Update every second
    
    def _update_creation_progress(self):
        """Update creation progress"""
        if self.current_step < len(self.creation_steps):
            progress, message = self.creation_steps[self.current_step]
            
            self.progress_bar.setValue(progress)
            self.step_label.setText(message)
            
            if progress == 100:
                self.status_label.setText("✅ Creation Complete!")
                self._show_completion_results()
                self.creation_timer.stop()
            
            self.current_step += 1
        else:
            self.creation_timer.stop()
    
    def _show_completion_results(self):
        """Show completion results"""
        self.results_frame.setVisible(True)
        
        # Create the actual IMG file here
        try:
            from new_img_creator import EnhancedIMGCreator
            creator = EnhancedIMGCreator(self.wizard_data['game_type'])
            created_path = creator.create_img(**self.wizard_data)
            
            self.created_img_path = created_path
            
            self.results_label.setText(f"✅ Successfully created: {os.path.basename(created_path)}")
            self.results_label.setStyleSheet("color: #27ae60; font-size: 14pt; font-weight: bold;")
            
        except Exception as e:
            self.results_label.setText(f"❌ Creation failed: {str(e)}")
            self.results_label.setStyleSheet("color: #e74c3c; font-size: 14pt; font-weight: bold;")
            
            # Hide action buttons on failure
            self.open_folder_btn.setVisible(False)
            self.load_img_btn.setVisible(False)
    
    def _open_output_folder(self):
        """Open the output folder"""
        if hasattr(self, 'created_img_path'):
            import subprocess
            import platform
            
            folder_path = os.path.dirname(self.created_img_path)
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
    
    def _load_created_img(self):
        """Load the created IMG file"""
        if hasattr(self, 'created_img_path'):
            self.img_created.emit(self.created_img_path)
            self.accept()

# Integration function
def add_quick_start_wizard(main_window):
    """Add quick start wizard to main window"""
    
    def show_quick_start():
        """Show the quick start wizard"""
        wizard = QuickStartWizard(main_window)
        wizard.img_created.connect(lambda path: main_window.load_img_file(path))
        wizard.img_created.connect(lambda path: main_window.log_message(f"Quick Start: Created {os.path.basename(path)}"))
        wizard.exec()
    
    # Add to main toolbar or menu
    if hasattr(main_window, 'menuBar'):
        help_menu = None
        for action in main_window.menuBar().actions():
            if action.text() == "Help":
                help_menu = action.menu()
                break
        
        if help_menu:
            wizard_action = help_menu.addAction("🚀 Quick Start Wizard")
            wizard_action.triggered.connect(show_quick_start)
            
            # Move to top of help menu
            actions = help_menu.actions()
            help_menu.removeAction(wizard_action)
            if actions:
                help_menu.insertAction(actions[0], wizard_action)
    
    return show_quick_start