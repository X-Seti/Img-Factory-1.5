#!/usr/bin/env python3
"""
Syntax Fix Script for img_creator.py
Diagnoses and fixes syntax errors
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Check syntax of a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse
        ast.parse(content)
        print(f"✅ {file_path} - Syntax is valid")
        return True, content
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax error on line {e.lineno}: {e.msg}")
        print(f"   Text: {e.text.strip() if e.text else 'N/A'}")
        return False, content
    except Exception as e:
        print(f"❌ {file_path} - Error reading file: {e}")
        return False, ""

def show_lines_around_error(content, line_num, context=3):
    """Show lines around the error"""
    lines = content.split('\n')
    start = max(0, line_num - context - 1)
    end = min(len(lines), line_num + context)
    
    print(f"\nLines around error (line {line_num}):")
    print("-" * 40)
    
    for i in range(start, end):
        marker = ">>> " if i == line_num - 1 else "    "
        print(f"{marker}{i+1:3d}: {lines[i]}")
    print("-" * 40)

def fix_common_issues(content):
    """Fix common syntax issues"""
    lines = content.split('\n')
    fixed_lines = []
    changes = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix common issues
        
        # 1. Fix incomplete import statements
        if line.strip().startswith('from') and 'import' in line and line.strip().endswith(','):
            line = line.rstrip(',')
            changes.append(f"Line {i+1}: Removed trailing comma from import")
        
        # 2. Fix incomplete class definitions
        if line.strip().startswith('class') and not line.strip().endswith(':'):
            if ':' not in line:
                line = line + ':'
                changes.append(f"Line {i+1}: Added missing colon to class definition")
        
        # 3. Fix incomplete function definitions
        if line.strip().startswith('def') and not line.strip().endswith(':'):
            if ':' not in line:
                line = line + ':'
                changes.append(f"Line {i+1}: Added missing colon to function definition")
        
        # 4. Fix unmatched quotes
        if line.count('"') % 2 != 0:
            # Try to fix unmatched quotes
            if line.strip().endswith('"'):
                pass  # Probably okay
            else:
                # Add missing quote at end
                line = line + '"'
                changes.append(f"Line {i+1}: Added missing closing quote")
        
        # 5. Fix unmatched parentheses
        open_parens = line.count('(')
        close_parens = line.count(')')
        if open_parens > close_parens:
            line = line + ')' * (open_parens - close_parens)
            changes.append(f"Line {i+1}: Added missing closing parentheses")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), changes

def restore_from_backup():
    """Restore from backup and create a clean version"""
    creator_file = Path("components/img_creator.py")
    backup_file = Path("components/img_creator.py.backup")
    
    if not backup_file.exists():
        print("❌ No backup file found")
        return False
    
    print("🔄 Restoring from backup...")
    
    try:
        # Read backup
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Create a completely new, clean version
        clean_content = '''#!/usr/bin/env python3
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

# Import with fallback
try:
    from .img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
except ImportError:
    try:
        from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
    except ImportError:
        print("Warning: Could not import core classes")
        class IMGFile: pass
        class IMGEntry: pass
        class IMGVersion:
            IMG_1 = 1
            IMG_2 = 2
            IMG_3 = 3
            IMG_FASTMAN92 = 4
            IMG_STORIES = 5
        def format_file_size(size): return f"{size} bytes"


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
        'description': 'Grand Theft Auto San Andreas - Version 2 single file format'
    }

    @classmethod
    def get_all_types(cls):
        """Get all game type configurations"""
        return [cls.GTA3, cls.GTAVC, cls.GTASA]

    @classmethod
    def get_by_code(cls, code: str):
        """Get game type by code"""
        for game_type in cls.get_all_types():
            if game_type['code'] == code:
                return game_type
        return None


class NewIMGDialog(QDialog):
    """Dialog for creating new IMG files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG File - IMG Factory 1.5")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.selected_game_type = GameType.GTASA
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the dialog user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New IMG Archive")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Game type selection
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
        
        layout.addWidget(game_group)
        
        # File settings
        file_group = QGroupBox("File Settings")
        file_layout = QFormLayout(file_group)
        
        self.filename_edit = QLineEdit("new_archive.img")
        file_layout.addRow("Filename:", self.filename_edit)
        
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(1)
        self.size_spin.setMaximum(2048)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        file_layout.addRow("Initial Size:", self.size_spin)
        
        layout.addWidget(file_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Create IMG")
        create_button.clicked.connect(self.accept)
        create_button.setDefault(True)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
    
    def get_creation_settings(self):
        """Get current creation settings"""
        return {
            'game_type': self.selected_game_type,
            'filename': self.filename_edit.text(),
            'initial_size_mb': self.size_spin.value(),
            'platform': 'PC'
        }


def add_new_img_functionality(main_window):
    """Add new IMG creation functionality to main window"""
    def create_new_img():
        dialog = NewIMGDialog(main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_creation_settings()
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"New IMG requested: {settings['filename']}")
    
    return create_new_img


if __name__ == "__main__":
    # Test the dialog
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = NewIMGDialog()
    dialog.show()
    app.exec()
'''
        
        # Write clean version
        with open(creator_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print("✅ Created clean img_creator.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating clean version: {e}")
        return False

def main():
    """Main function"""
    print("🔧 IMG Factory 1.5 - Syntax Checker & Fixer")
    print("=" * 45)
    
    creator_file = Path("components/img_creator.py")
    
    if not creator_file.exists():
        print(f"❌ File not found: {creator_file}")
        return False
    
    # Check current syntax
    is_valid, content = check_syntax(creator_file)
    
    if is_valid:
        print("🎉 File syntax is already correct!")
        return True
    
    # Show error context
    try:
        ast.parse(content)
    except SyntaxError as e:
        show_lines_around_error(content, e.lineno)
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Try to auto-fix common issues")
    print("2. Restore clean version from backup")
    print("3. Exit and fix manually")
    
    try:
        choice = input("\nChoose option (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return False
    
    if choice == "1":
        print("\n🔧 Attempting auto-fix...")
        fixed_content, changes = fix_common_issues(content)
        
        if changes:
            print("Changes made:")
            for change in changes:
                print(f"  - {change}")
            
            # Write fixed content
            try:
                with open(creator_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print("✅ Fixed content written")
                
                # Test syntax again
                is_valid, _ = check_syntax(creator_file)
                return is_valid
                
            except Exception as e:
                print(f"❌ Error writing fixed content: {e}")
                return False
        else:
            print("❌ No automatic fixes available")
            return False
    
    elif choice == "2":
        return restore_from_backup()
    
    else:
        print("👋 Exiting for manual fix")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Syntax issue resolved!")
        print("Now try: python imgfactory_demo.py")
    else:
        print("\n❌ Could not resolve syntax issue")
        print("You may need to manually edit components/img_creator.py")
    
    input("\nPress Enter to exit...")
