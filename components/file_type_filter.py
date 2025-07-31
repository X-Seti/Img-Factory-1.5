#this belongs in core/file_type_filter.py - Version: 1
# X-Seti - July23 2025 - IMG Factory 1.5 - File Type Filter - Complete Port
# Ported from file_type_filter.py-old with 100% functionality preservation
# ONLY debug system changed from old COL debug to img_debugger

"""
File Type Filter - COMPLETE PORT
Advanced file filtering and extraction with type-based organization
Uses IMG debug system throughout - preserves 100% original functionality
"""

import os
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QDialog, QTableWidget, QTableWidgetItem, QProgressBar, QCheckBox,
    QGroupBox, QLineEdit, QSpinBox, QFileDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import IMG debug system - NO fallback code
from components.img_debug_functions import img_debugger

##Functions list -
# apply_file_filter
# browse_output_dir
# cancel_extraction
# check_entry_matches_criteria
# check_size_filter
# create_type_directories
# emit_filter_changed
# extract_single_file
# extraction_failed
# extraction_finished
# file_extracted
# format_type_summary
# get_file_type
# get_filter_criteria
# get_type_counts
# get_type_subdirectory
# integrate_file_filtering
# run
# setup_ui (multiple classes)
# show_extraction_dialog
# start_extraction
# update_filter_options
# update_filter_statistics
# update_progress

##Classes list -
# ExtractionDialog
# FileExtractionManager
# FileTypeFilter

class FileTypeFilter(QWidget):
    """Advanced file type filter widget with statistics"""
    
    filter_changed = pyqtSignal(dict)  # Filter criteria changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("file_type_filter")
        
        # Initialize data
        self.file_type_stats = {}
        self.total_entries = 0
        
        self.setup_ui()
        
    def setup_ui(self): #vers 1
        """Setup filter UI components"""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(4)
            
            # Main filter dropdown
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Filter:"))
            
            self.main_filter_combo = QComboBox()
            self.main_filter_combo.addItem("All Files")
            self.main_filter_combo.currentTextChanged.connect(self.emit_filter_changed)
            filter_layout.addWidget(self.main_filter_combo)
            
            layout.addLayout(filter_layout)
            
            # Statistics label
            self.stats_label = QLabel("0 files")
            self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
            layout.addWidget(self.stats_label)
            
            # Advanced options group (collapsed by default)
            self.setup_advanced_options(layout)
            
            img_debugger.debug("✅ File type filter UI setup complete")
            
        except Exception as e:
            img_debugger.error(f"❌ Failed to setup filter UI: {str(e)}")
    
    def setup_advanced_options(self, parent_layout): #vers 1
        """Setup advanced filtering options"""
        try:
            self.advanced_group = QGroupBox("Advanced Filters")
            self.advanced_group.setCheckable(True)
            self.advanced_group.setChecked(False)
            self.advanced_group.toggled.connect(self.emit_filter_changed)
            
            advanced_layout = QVBoxLayout(self.advanced_group)
            
            # Size filter
            size_layout = QHBoxLayout()
            size_layout.addWidget(QLabel("Size:"))
            
            self.size_filter_combo = QComboBox()
            self.size_filter_combo.addItems([
                "Any Size", "< 1 KB", "< 10 KB", "< 100 KB",
                "< 1 MB", "< 10 MB", "> 1 MB", "> 10 MB"
            ])
            self.size_filter_combo.currentTextChanged.connect(self.emit_filter_changed)
            size_layout.addWidget(self.size_filter_combo)
            
            advanced_layout.addLayout(size_layout)
            
            # Version filter
            version_layout = QHBoxLayout()
            version_layout.addWidget(QLabel("RW Version:"))
            
            self.version_filter_combo = QComboBox()
            self.version_filter_combo.addItems(["Any Version"])
            self.version_filter_combo.currentTextChanged.connect(self.emit_filter_changed)
            version_layout.addWidget(self.version_filter_combo)
            
            advanced_layout.addLayout(version_layout)
            
            # Name pattern
            pattern_layout = QHBoxLayout()
            pattern_layout.addWidget(QLabel("Name Pattern:"))
            
            self.pattern_input = QLineEdit()
            self.pattern_input.setPlaceholderText("*.dff or vehicle*")
            self.pattern_input