#this belongs in gui/directory_tree_system.py - Version: 1
# X-Seti - August10 2025 - IMG Factory 1.5 - Interactive Directory Tree System

"""
INTERACTIVE DIRECTORY TREE SYSTEM
Replaces the placeholder "Directory Tree" tab with full functionality.
Parses game directories and provides context-sensitive file operations.
"""

import os
from typing import Dict, List, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QToolBar, QPushButton, QLineEdit, QLabel, QMenu, QMessageBox,
    QSplitter, QTextEdit, QGroupBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QFont

##Methods list -
# create_directory_tree_widget
# setup_directory_tree_toolbar
# setup_directory_tree_context_menu
# populate_directory_tree
# handle_tree_item_click
# handle_tree_item_double_click
# parse_game_directory_structure
# detect_gta_installation
# get_file_type_icon
# get_file_context_actions
# integrate_directory_tree_system

class DirectoryTreeWidget(QWidget):
    """Interactive directory tree widget for game file navigation"""
    
    # Signals
    file_selected = pyqtSignal(str)  # file_path
    img_file_requested = pyqtSignal(str)  # img_path
    text_file_requested = pyqtSignal(str)  # text_path
    directory_changed = pyqtSignal(str)  # directory_path
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.current_root = None
        self.project_folder = None
        self.game_root = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self): #vers 1
        """Setup directory tree UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        self.toolbar = self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # Create splitter for tree and info
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Directory tree
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        # Path display
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("📁 Current Path:"))
        self.path_label = QLabel("No directory selected")
        self.path_label.setStyleSheet("font-family: monospace; background: #f0f0f0; padding: 3px;")
        path_layout.addWidget(self.path_label)
        tree_layout.addLayout(path_layout)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size", "Files"])
        self.tree.setRootIsDecorated(True)
        self.tree.setAlternatingRowColors(True)
        tree_layout.addWidget(self.tree)
        
        splitter.addWidget(tree_widget)
        
        # Right: File info and actions
        info_widget = self.create_info_panel()
        splitter.addWidget(info_widget)
        
        # Set splitter proportions
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)
        
    def create_toolbar(self): #vers 1
        """Create directory tree toolbar"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Set game root action
        self.set_game_root_action = QAction("🎮 Set Game Root", self)
        self.set_game_root_action.setToolTip("Set GTA game root directory")
        self.set_game_root_action.triggered.connect(self.set_game_root_folder)
        toolbar.addAction(self.set_game_root_action)
        
        toolbar.addSeparator()
        
        # Set project folder action
        self.set_project_action = QAction("📁 Set Project", self)
        self.set_project_action.setToolTip("Set project folder for exports")
        self.set_project_action.triggered.connect(self.set_project_folder)
        toolbar.addAction(self.set_project_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        self.refresh_action = QAction("🔄 Refresh", self)
        self.refresh_action.setToolTip("Refresh directory tree")
        self.refresh_action.triggered.connect(self.refresh_tree)
        toolbar.addAction(self.refresh_action)
        
        # Auto-detect GTA action
        self.auto_detect_action = QAction("🔍 Auto-Detect", self)
        self.auto_detect_action.setToolTip("Auto-detect GTA installation")
        self.auto_detect_action.triggered.connect(self.auto_detect_gta)
        toolbar.addAction(self.auto_detect_action)
        
        return toolbar
        
    def create_info_panel(self): #vers 1
        """Create file information panel"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # File info group
        file_info_group = QGroupBox("📄 File Information")
        file_info_layout = QVBoxLayout(file_info_group)
        
        self.selected_file_label = QLabel("No file selected")
        self.file_type_label = QLabel("Type: Unknown")
        self.file_size_label = QLabel("Size: Unknown")
        self.file_path_label = QLabel("Path: Unknown")
        
        file_info_layout.addWidget(self.selected_file_label)
        file_info_layout.addWidget(self.file_type_label)
        file_info_layout.addWidget(self.file_size_label)
        file_info_layout.addWidget(self.file_path_label)
        
        info_layout.addWidget(file_info_group)
        
        # Actions group
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.load_img_btn = QPushButton("📂 Load IMG File")
        self.load_img_btn.clicked.connect(self.load_selected_img)
        self.load_img_btn.setEnabled(False)
        actions_layout.addWidget(self.load_img_btn)
        
        self.edit_text_btn = QPushButton("📝 Edit Text File")
        self.edit_text_btn.clicked.connect(self.edit_selected_text)
        self.edit_text_btn.setEnabled(False)
        actions_layout.addWidget(self.edit_text_btn)
        
        self.explore_btn = QPushButton("🗂️ Open in Explorer")
        self.explore_btn.clicked.connect(self.open_in_explorer)
        self.explore_btn.setEnabled(False)
        actions_layout.addWidget(self.explore_btn)
        
        info_layout.addWidget(actions_group)
        
        # Directory stats group
        stats_group = QGroupBox("📊 Directory Stats")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QTextEdit()
        self.stats_label.setMaximumHeight(100)
        self.stats_label.setReadOnly(True)
        stats_layout.addWidget(self.stats_label)
        
        info_layout.addWidget(stats_group)
        
        info_layout.addStretch()
        return info_widget
        
    def setup_connections(self): #vers 1
        """Setup signal connections"""
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
    def set_game_root_folder(self): #vers 1
        """Set game root folder via dialog"""
        from PyQt6.QtWidgets import QFileDialog
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select GTA Game Root Directory", 
            self.game_root or os.path.expanduser("~")
        )
        
        if folder:
            self.game_root = folder
            self.current_root = folder
            self.path_label.setText(folder)
            self.populate_tree(folder)
            self.log_message(f"🎮 Game root set: {folder}")
            
    def set_project_folder(self): #vers 1
        """Set project folder via dialog"""
        from PyQt6.QtWidgets import QFileDialog
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select Project Folder", 
            self.project_folder or os.path.expanduser("~")
        )
        
        if folder:
            self.project_folder = folder
            self.log_message(f"📁 Project folder set: {folder}")
            
    def auto_detect_gta(self): #vers 2
        """Auto-detect GTA installation using EXE + DAT validation"""
        detected_info = self.detect_gta_installations_with_info()
        
        if detected_info:
            if len(detected_info) == 1:
                # Single installation found
                game_path, game_info = detected_info[0]
                self.game_root = game_path
                self.current_root = game_path
                self.path_label.setText(game_path)
                self.populate_tree(game_path)
                self.log_message(f"🔍 Auto-detected {game_info['game_name']}: {game_path}")
                self.log_message(f"   EXE: {game_info['exe_file']}")
                self.log_message(f"   DAT: {game_info['dat_file']}")
                self.log_message(f"   IDE: {game_info['ide_file']}")
            else:
                # Multiple installations - show selection dialog
                self.show_gta_selection_dialog(detected_info)
        else:
            QMessageBox.information(
                self, "Auto-Detection", 
                "No GTA installation detected.\n\nChecked for:\n• gta_vc.exe + gta_vc.dat\n• gta_sa.exe + gta_sa.dat\n• gta3.exe + gta3.dat\n• gtasol.exe + gtasol.dat\n\nPlease set the game root manually."
            )
            
    def detect_gta_installations_with_info(self) -> List[tuple]: #vers 1
        """Detect GTA installations and return path + info"""
        installations = []
        
        # Common installation paths
        common_paths = [
            # Steam
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto San Andreas",
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto Vice City", 
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto III",
            
            # Rockstar Games Launcher
            "C:/Program Files/Rockstar Games/Grand Theft Auto San Andreas",
            "C:/Program Files/Rockstar Games/Grand Theft Auto Vice City",
            "C:/Program Files/Rockstar Games/Grand Theft Auto III",
            
            # Common manual installs
            "C:/Games/GTA San Andreas",
            "C:/Games/GTA Vice City", 
            "C:/Games/GTA III",
            "C:/Games/GTA Sol",
            
            # Program Files
            "C:/Program Files/Grand Theft Auto San Andreas",
            "C:/Program Files/Grand Theft Auto Vice City",
            "C:/Program Files/Grand Theft Auto III",
            "C:/Program Files/GTA Sol",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                game_info = self.verify_gta_installation(path)
                if game_info:
                    installations.append((path, game_info))
                    
        return installations
        
    def show_gta_selection_dialog(self, detected_info: List[tuple]): #vers 1
        """Show dialog to select from multiple detected GTA installations"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout, QListWidgetItem
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Multiple GTA Installations Found")
            dialog.setMinimumSize(600, 350)
            
            layout = QVBoxLayout(dialog)
            
            label = QLabel("Multiple GTA installations detected with valid EXE + DAT files:")
            layout.addWidget(label)
            
            list_widget = QListWidget()
            for path, game_info in detected_info:
                item_text = f"{game_info['game_name']} - {path}\n   EXE: {game_info['exe_file']} | DAT: {game_info['dat_file']} | IDE: {game_info['ide_file']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, (path, game_info))
                list_widget.addItem(item)
                
            list_widget.setCurrentRow(0)
            layout.addWidget(list_widget)
            
            button_layout = QHBoxLayout()
            ok_button = QPushButton("Select")
            cancel_button = QPushButton("Cancel")
            
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                current_item = list_widget.currentItem()
                if current_item:
                    path, game_info = current_item.data(Qt.ItemDataRole.UserRole)
                    self.game_root = path
                    self.current_root = path
                    self.path_label.setText(path)
                    self.populate_tree(path)
                    self.log_message(f"🔍 Selected {game_info['game_name']}: {path}")
                    
        except Exception as e:
            self.log_message(f"❌ Error in GTA selection dialog: {str(e)}")
            
    def detect_gta_installations(self) -> List[str]: #vers 2
        """Detect GTA installations on system using EXE + DAT validation"""
        potential_paths = []
        
        # Common installation paths
        common_paths = [
            # Steam
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto San Andreas",
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto Vice City", 
            "C:/Program Files (x86)/Steam/steamapps/common/Grand Theft Auto III",
            
            # Rockstar Games Launcher
            "C:/Program Files/Rockstar Games/Grand Theft Auto San Andreas",
            "C:/Program Files/Rockstar Games/Grand Theft Auto Vice City",
            "C:/Program Files/Rockstar Games/Grand Theft Auto III",
            
            # Common manual installs
            "C:/Games/GTA San Andreas",
            "C:/Games/GTA Vice City", 
            "C:/Games/GTA III",
            "C:/Games/GTA Sol",
            
            # Program Files
            "C:/Program Files/Grand Theft Auto San Andreas",
            "C:/Program Files/Grand Theft Auto Vice City",
            "C:/Program Files/Grand Theft Auto III",
            "C:/Program Files/GTA Sol",
        ]
        
        # Check each path
        for path in common_paths:
            if os.path.exists(path):
                # Verify it's actually a GTA installation
                game_info = self.verify_gta_installation(path)
                if game_info:
                    potential_paths.append(path)
                    
        return potential_paths
        
    def verify_gta_installation(self, path: str) -> dict: #vers 4
        """Verify path contains GTA installation using EXE + DAT method"""
        try:
            # Define GTA game signatures: (exe_name, dat_file, ide_file, game_name)
            gta_signatures = [
                # GTA Vice City
                ("gta_vc.exe", "gta_vc.dat", "default.ide", "GTA Vice City"),
                ("gta-vc.exe", "gta_vc.dat", "default.ide", "GTA Vice City"), 
                
                # GTA San Andreas
                ("gta_sa.exe", "gta_sa.dat", "default.ide", "GTA San Andreas"),
                ("gta-sa.exe", "gta_sa.dat", "default.ide", "GTA San Andreas"),
                
                # GTA III
                ("gta3.exe", "gta3.dat", "default.ide", "GTA III"),
                
                # GTA Sol (custom game) - FIXED: Match actual Sol structure
                ("solcore.exe", "SOL/gta_sol.dat", "Data/default.dat", "GTA Sol"),
                ("gtasol.exe", "SOL/gta_sol.dat", "Data/default.dat", "GTA Sol"),
                ("gta_sol.exe", "SOL/gta_sol.dat", "Data/default.dat", "GTA Sol"),
                ("solcore.exe", "SOL/gta_sol.dat", "default.ide", "GTA Sol"),
                ("gtasol.exe", "SOL/gta_sol.dat", "default.ide", "GTA Sol"),
                ("gta_sol.exe", "SOL/gta_sol.dat", "default.ide", "GTA Sol"),
                # Also check root locations
                ("solcore.exe", "gta_sol.dat", "Data/default.dat", "GTA Sol"),
                ("gtasol.exe", "gta_sol.dat", "Data/default.dat", "GTA Sol"),
                ("gta_sol.exe", "gta_sol.dat", "Data/default.dat", "GTA Sol"),
            ]
            
            for exe_name, dat_file, ide_file, game_name in gta_signatures:
                exe_path = os.path.join(path, exe_name)
                dat_path = os.path.join(path, dat_file)
                ide_path = os.path.join(path, ide_file)
                
                # Check if EXE exists
                if os.path.exists(exe_path):
                    self.log_message(f"🔍 Found EXE: {exe_path}")
                    # Check if DAT file exists
                    if os.path.exists(dat_path):
                        self.log_message(f"🔍 Found DAT: {dat_path}")
                        # Check if IDE file exists
                        if os.path.exists(ide_path):
                            self.log_message(f"🔍 Found IDE: {ide_path}")
                            return {
                                'game_name': game_name,
                                'exe_file': exe_name,
                                'dat_file': dat_file,
                                'ide_file': ide_file,
                                'validated': True
                            }
                        else:
                            self.log_message(f"❌ IDE not found: {ide_path}")
                    else:
                        self.log_message(f"❌ DAT not found: {dat_path}")
                else:
                    # Uncomment for debugging: self.log_message(f"❌ EXE not found: {exe_path}")
                    pass
                            
            return None
            
        except Exception as e:
            self.log_message(f"❌ Error verifying GTA installation at {path}: {str(e)}")
            return None
            
    def populate_tree(self, root_path: str): #vers 1
        """Populate directory tree"""
        try:
            self.tree.clear()
            
            if not os.path.exists(root_path):
                self.log_message(f"❌ Path does not exist: {root_path}")
                return
                
            self.log_message(f"🔄 Scanning directory: {root_path}")
            
            # Create root item
            root_item = QTreeWidgetItem(self.tree)
            root_item.setText(0, os.path.basename(root_path) or root_path)
            root_item.setText(1, "Folder")
            root_item.setData(0, Qt.ItemDataRole.UserRole, root_path)
            
            # Add icon based on folder type
            if "GTA" in root_path.upper() or "GRAND THEFT AUTO" in root_path.upper():
                root_item.setText(1, "🎮 Game Root")
            else:
                root_item.setText(1, "📁 Folder")
                
            # Populate children
            self.populate_tree_recursive(root_item, root_path, max_depth=3)
            
            # Expand root
            root_item.setExpanded(True)
            
            # Update stats
            self.update_directory_stats(root_path)
            
        except Exception as e:
            self.log_message(f"❌ Error populating tree: {str(e)}")
            
    def populate_tree_recursive(self, parent_item: QTreeWidgetItem, dir_path: str, max_depth: int = 2): #vers 1
        """Recursively populate tree items"""
        if max_depth <= 0:
            return
            
        try:
            items = os.listdir(dir_path)
            
            # Separate folders and files
            folders = []
            files = []
            
            for item in items:
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    files.append(item)
                    
            # Add folders first
            for folder in sorted(folders):
                folder_path = os.path.join(dir_path, folder)
                folder_item = QTreeWidgetItem(parent_item)
                folder_item.setText(0, folder)
                folder_item.setText(1, "📁 Folder")
                folder_item.setData(0, Qt.ItemDataRole.UserRole, folder_path)
                
                # Count files in folder
                try:
                    file_count = len([f for f in os.listdir(folder_path) 
                                    if os.path.isfile(os.path.join(folder_path, f))])
                    folder_item.setText(3, str(file_count))
                except:
                    folder_item.setText(3, "?")
                
                # Recurse into subfolders (but limited depth)
                if max_depth > 1:
                    self.populate_tree_recursive(folder_item, folder_path, max_depth - 1)
                    
            # Add important files (IMG, text files, etc.)
            important_extensions = {'.img', '.ide', '.ipl', '.dat', '.txd', '.dff', '.col'}
            for file in sorted(files):
                file_path = os.path.join(dir_path, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Only show important files to avoid clutter
                if file_ext in important_extensions:
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, file)
                    file_item.setText(1, self.get_file_type_display(file_ext))
                    file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                    
                    # File size
                    try:
                        size = os.path.getsize(file_path)
                        file_item.setText(2, self.format_file_size(size))
                    except:
                        file_item.setText(2, "?")
                        
        except Exception as e:
            self.log_message(f"❌ Error scanning {dir_path}: {str(e)}")
            
    def get_file_type_display(self, extension: str) -> str: #vers 1
        """Get display text for file type"""
        type_map = {
            '.img': '📦 IMG Archive',
            '.ide': '📝 IDE Definition', 
            '.ipl': '🗺️ IPL Placement',
            '.dat': '⚙️ DAT Config',
            '.txd': '🎨 TXD Texture',
            '.dff': '🏗️ DFF Model',
            '.col': '🛡️ COL Collision'
        }
        return type_map.get(extension, f'📄 {extension.upper()} File')
        
    def format_file_size(self, size: int) -> str: #vers 1
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
        
    def on_item_clicked(self, item: QTreeWidgetItem, column: int): #vers 1
        """Handle tree item click"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.update_file_info(file_path)
            self.file_selected.emit(file_path)
            
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int): #vers 1
        """Handle tree item double click"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isfile(file_path):
            self.handle_file_double_click(file_path)
            
    def handle_file_double_click(self, file_path: str): #vers 1
        """Handle double-click on file"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.img':
            self.img_file_requested.emit(file_path)
            self.log_message(f"📦 Loading IMG: {os.path.basename(file_path)}")
        elif file_ext in ['.ide', '.ipl', '.dat']:
            self.text_file_requested.emit(file_path)
            self.log_message(f"📝 Opening text file: {os.path.basename(file_path)}")
        else:
            self.log_message(f"ℹ️ Double-clicked: {os.path.basename(file_path)}")
            
    def update_file_info(self, file_path: str): #vers 1
        """Update file information panel"""
        try:
            self.selected_file_label.setText(f"📄 {os.path.basename(file_path)}")
            self.file_path_label.setText(f"Path: {file_path}")
            
            if os.path.isfile(file_path):
                # File info
                size = os.path.getsize(file_path)
                self.file_size_label.setText(f"Size: {self.format_file_size(size)}")
                
                file_ext = os.path.splitext(file_path)[1].lower()
                self.file_type_label.setText(f"Type: {self.get_file_type_display(file_ext)}")
                
                # Enable appropriate buttons
                self.load_img_btn.setEnabled(file_ext == '.img')
                self.edit_text_btn.setEnabled(file_ext in ['.ide', '.ipl', '.dat'])
                self.explore_btn.setEnabled(True)
                
            else:
                # Directory info
                self.file_type_label.setText("Type: 📁 Directory")
                self.file_size_label.setText("Size: Directory")
                
                self.load_img_btn.setEnabled(False)
                self.edit_text_btn.setEnabled(False)
                self.explore_btn.setEnabled(True)
                
        except Exception as e:
            self.log_message(f"❌ Error updating file info: {str(e)}")
            
    def update_directory_stats(self, dir_path: str): #vers 1
        """Update directory statistics"""
        try:
            stats = self.analyze_directory(dir_path)
            
            stats_text = f"""
📊 Directory Analysis:
• IMG Files: {stats['img_files']}
• Text Files: {stats['text_files']} (IDE: {stats['ide_files']}, IPL: {stats['ipl_files']}, DAT: {stats['dat_files']})
• Model Files: {stats['dff_files']} DFF
• Texture Files: {stats['txd_files']} TXD
• Collision Files: {stats['col_files']} COL
• Total Files: {stats['total_files']}
• Total Size: {self.format_file_size(stats['total_size'])}
            """.strip()
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            self.stats_label.setText(f"Error analyzing directory: {str(e)}")
            
    def analyze_directory(self, dir_path: str) -> Dict[str, int]: #vers 1
        """Analyze directory contents"""
        stats = {
            'img_files': 0, 'ide_files': 0, 'ipl_files': 0, 'dat_files': 0,
            'dff_files': 0, 'txd_files': 0, 'col_files': 0, 'text_files': 0,
            'total_files': 0, 'total_size': 0
        }
        
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    stats['total_files'] += 1
                    
                    try:
                        stats['total_size'] += os.path.getsize(file_path)
                    except:
                        pass
                    
                    if file_ext == '.img':
                        stats['img_files'] += 1
                    elif file_ext == '.ide':
                        stats['ide_files'] += 1
                        stats['text_files'] += 1
                    elif file_ext == '.ipl':
                        stats['ipl_files'] += 1
                        stats['text_files'] += 1
                    elif file_ext == '.dat':
                        stats['dat_files'] += 1
                        stats['text_files'] += 1
                    elif file_ext == '.dff':
                        stats['dff_files'] += 1
                    elif file_ext == '.txd':
                        stats['txd_files'] += 1
                    elif file_ext == '.col':
                        stats['col_files'] += 1
                        
        except Exception as e:
            self.log_message(f"❌ Error analyzing directory: {str(e)}")
            
        return stats
        
    def show_context_menu(self, position): #vers 1
        """Show context menu for tree item"""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_path:
            return
            
        menu = QMenu(self)
        
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.img':
                menu.addAction("📂 Load in IMG Factory", lambda: self.img_file_requested.emit(file_path))
                menu.addSeparator()
                
            if file_ext in ['.ide', '.ipl', '.dat']:
                menu.addAction("📝 Edit Text File", lambda: self.text_file_requested.emit(file_path))
                menu.addSeparator()
                
        menu.addAction("🗂️ Open in Explorer", lambda: self.open_in_explorer_path(file_path))
        menu.addAction("📋 Copy Path", lambda: self.copy_path_to_clipboard(file_path))
        
        menu.exec(self.tree.mapToGlobal(position))
        
    def load_selected_img(self): #vers 1
        """Load selected IMG file"""
        current_item = self.tree.currentItem()
        if current_item:
            file_path = current_item.data(0, Qt.ItemDataRole.UserRole)
            if file_path and file_path.lower().endswith('.img'):
                self.img_file_requested.emit(file_path)
                
    def edit_selected_text(self): #vers 1
        """Edit selected text file"""
        current_item = self.tree.currentItem()
        if current_item:
            file_path = current_item.data(0, Qt.ItemDataRole.UserRole)
            if file_path and os.path.splitext(file_path)[1].lower() in ['.ide', '.ipl', '.dat']:
                self.text_file_requested.emit(file_path)
                
    def open_in_explorer(self): #vers 1
        """Open selected item in file explorer"""
        current_item = self.tree.currentItem()
        if current_item:
            file_path = current_item.data(0, Qt.ItemDataRole.UserRole)
            if file_path:
                self.open_in_explorer_path(file_path)
                
    def open_in_explorer_path(self, file_path: str): #vers 1
        """Open specific path in file explorer"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(f'explorer /select,"{file_path}"', shell=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
                
        except Exception as e:
            self.log_message(f"❌ Error opening explorer: {str(e)}")
            
    def copy_path_to_clipboard(self, file_path: str): #vers 1
        """Copy file path to clipboard"""
        try:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(file_path)
            self.log_message(f"📋 Path copied: {file_path}")
        except Exception as e:
            self.log_message(f"❌ Error copying path: {str(e)}")
            
    def refresh_tree(self): #vers 1
        """Refresh the directory tree"""
        if self.current_root:
            self.populate_tree(self.current_root)
            self.log_message("🔄 Directory tree refreshed")
        else:
            self.log_message("⚠️ No directory to refresh")
            
    def log_message(self, message: str): #vers 1
        """Log message (to be connected to main window)"""
        print(f"[DirectoryTree] {message}")


def create_directory_tree_widget(main_window): #vers 1
    """Create directory tree widget for main window"""
    try:
        tree_widget = DirectoryTreeWidget(main_window)
        
        # Connect signals to main window
        tree_widget.img_file_requested.connect(main_window.load_file)
        tree_widget.log_message = main_window.log_message
        
        main_window.log_message("✅ Directory tree widget created")
        return tree_widget
        
    except Exception as e:
        main_window.log_message(f"❌ Error creating directory tree: {str(e)}")
        return None


def integrate_directory_tree_system(main_window): #vers 2
    """Replace placeholder with functional directory tree - PRESERVE TAB STRUCTURE"""
    try:
        # Find the directory tree tab in gui_layout
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'tab_widget'):
            main_window.log_message("❌ Tab widget not found for directory tree integration")
            return False
            
        tab_widget = main_window.gui_layout.tab_widget
        
        # Find the "Directory Tree" tab (should be index 1)
        directory_tab_index = -1
        for i in range(tab_widget.count()):
            if "Directory Tree" in tab_widget.tabText(i):
                directory_tab_index = i
                break
                
        if directory_tab_index == -1:
            main_window.log_message("❌ Directory Tree tab not found")
            return False
            
        # Get the existing tab widget at this index (to replace its contents)
        existing_tab = tab_widget.widget(directory_tab_index)
        if not existing_tab:
            main_window.log_message("❌ Directory Tree tab widget not found")
            return False
            
        # Clear the existing tab contents but keep the tab
        existing_layout = existing_tab.layout()
        if existing_layout:
            # Remove all widgets from existing layout
            while existing_layout.count():
                child = existing_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            # Create new layout if none exists
            from PyQt6.QtWidgets import QVBoxLayout
            existing_layout = QVBoxLayout(existing_tab)
            
        # Create new functional directory tree
        directory_tree = create_directory_tree_widget(main_window)
        if not directory_tree:
            return False
            
        # Add the directory tree to the existing tab (replace placeholder)
        existing_layout.addWidget(directory_tree)
        
        # Update the tab text with icon
        tab_widget.setTabText(directory_tab_index, "🌳 Directory Tree")
        
        # Store reference for later use
        main_window.directory_tree = directory_tree
        
        main_window.log_message("✅ Directory tree system integrated (tab structure preserved)")
        main_window.log_message("🌳 Use 'Set Game Root' in File menu to browse GTA directories")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error integrating directory tree: {str(e)}")
        return False


__all__ = [
    'DirectoryTreeWidget',
    'create_directory_tree_widget',
    'integrate_directory_tree_system'
]