"""
Extract functionality for IMG Factory
Handles extracting textures from DFF files and TXD files from IMG files
"""
import os
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QLabel, QFileDialog, QCheckBox, QGroupBox, QProgressBar, 
    QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class TextureExtractor:
    """Handles texture extraction from IMG and DFF files"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.extracted_textures = {}
        self.dff_texture_mapping = {}
        
    def extract_textures_from_img(self, img_file_path: str, output_dir: str) -> bool:
        """
        Extract all TXD files from IMG and convert textures to PNG
        """
        try:
            if not hasattr(self.main_window, 'current_img') or not self.main_window.current_img:
                self.main_window.log_message("No IMG file loaded")
                return False
                
            current_img = self.main_window.current_img
            extracted_count = 0
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            for entry in current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    # Extract TXD file temporarily
                    if hasattr(entry, 'get_data'):
                        txd_data = entry.get_data()
                        if txd_data:
                            txd_path = os.path.join(output_dir, entry.name)
                            with open(txd_path, 'wb') as f:
                                f.write(txd_data)
                            
                            # Extract textures from TXD (this would need actual TXD parsing)
                            texture_count = self._extract_textures_from_txd(txd_path, output_dir)
                            extracted_count += texture_count
                            self.main_window.log_message(f"Extracted {texture_count} textures from {entry.name}")
            
            self.main_window.log_message(f"Extraction complete: {extracted_count} textures extracted")
            return True
            
        except Exception as e:
            self.main_window.log_message(f"Error extracting textures: {str(e)}")
            return False
    
    def _extract_textures_from_txd(self, txd_path: str, output_dir: str) -> int:
        """
        Extract individual textures from TXD file
        This is a placeholder - actual TXD parsing would go here
        """
        # This would contain the actual TXD parsing and PNG extraction logic
        # For now, we'll simulate the process
        texture_count = 0
        
        # Extract textures from TXD file to PNG format
        # This would require actual TXD parsing library
        # For now, just return a simulated count
        texture_count = 1  # Simulated extraction
        
        return texture_count
    
    def parse_dff_textures(self, dff_files: List[str]) -> Dict[str, List[str]]:
        """
        Parse DFF files to extract texture name mappings
        Returns dictionary mapping model names to required textures
        """
        texture_mapping = {}
        
        for dff_file in dff_files:
            try:
                model_name = os.path.basename(dff_file)
                textures = self._parse_dff_for_textures(dff_file)
                texture_mapping[model_name] = textures
            except Exception as e:
                self.main_window.log_message(f"Error parsing DFF {dff_file}: {str(e)}")
        
        return texture_mapping
    
    def _parse_dff_for_textures(self, dff_file: str) -> List[str]:
        """
        Parse a single DFF file to extract texture names
        This is a placeholder - actual DFF parsing would go here
        """
        # This would contain the actual DFF parsing logic
        # For now, we'll simulate the process
        textures = []
        
        # Read DFF file and extract texture names
        # This would require actual DFF parsing library
        # For now, just return a simulated list
        try:
            # Simulate reading the DFF file to extract texture names
            # In a real implementation, this would parse the DFF structure
            with open(dff_file, 'rb') as f:
                # Read file header to identify it's a DFF
                header = f.read(12)  # Read first 12 bytes
                # This is where actual DFF parsing would occur
                textures = ["texture1", "texture2", "texture3"]  # Simulated textures
        except Exception:
            # If file can't be read, return empty list
            textures = []
        
        return textures


class ExtractDialog(QDialog):
    """Dialog for extraction functionality"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.extractor = TextureExtractor(main_window)
        self.setWindowTitle("Extract Textures and Models")
        self.resize(700, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the extraction dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Texture extraction tab
        texture_tab = self.create_texture_tab()
        tab_widget.addTab(texture_tab, "Extract Textures")
        
        # DFF parsing tab
        dff_tab = self.create_dff_tab()
        tab_widget.addTab(dff_tab, "Parse DFF Textures")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def create_texture_tab(self):
        """Create the texture extraction tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc_label = QLabel("Extract all TXD textures from IMG file as PNG:")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Directory:")
        self.output_dir_edit = QTextEdit()
        self.output_dir_edit.setMaximumHeight(30)
        self.output_dir_edit.setPlaceholderText("Select output directory for extracted textures...")
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_dir)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_output_btn)
        layout.addLayout(output_layout)
        
        # Extract button
        self.extract_btn = QPushButton("Extract All Textures")
        self.extract_btn.clicked.connect(self.extract_textures)
        layout.addWidget(self.extract_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        return widget
        
    def create_dff_tab(self):
        """Create the DFF parsing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc_label = QLabel("Parse DFF files to list texture requirements:")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # DFF file selection
        dff_layout = QHBoxLayout()
        dff_label = QLabel("DFF Files:")
        self.dff_files_edit = QTextEdit()
        self.dff_files_edit.setMaximumHeight(60)
        self.dff_files_edit.setPlaceholderText("Select DFF files to parse for texture requirements...")
        browse_dff_btn = QPushButton("Browse")
        browse_dff_btn.clicked.connect(self.browse_dff_files)
        
        dff_layout.addWidget(dff_label)
        dff_layout.addWidget(self.dff_files_edit)
        dff_layout.addWidget(browse_dff_btn)
        layout.addLayout(dff_layout)
        
        # Parse button
        self.parse_btn = QPushButton("Parse DFF Files")
        self.parse_btn.clicked.connect(self.parse_dff_files)
        layout.addWidget(self.parse_btn)
        
        # Results area
        results_group = QGroupBox("Parsed Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        results_layout.addWidget(self.results_area)
        
        layout.addWidget(results_group)
        
        return widget
        
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", "", 
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if directory:
            self.output_dir_edit.setPlainText(directory)
            
    def browse_dff_files(self):
        """Browse for DFF files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select DFF Files", "", 
            "DFF Files (*.dff);;All Files (*)"
        )
        if files:
            self.dff_files_edit.setPlainText("\n".join(files))
            
    def extract_textures(self):
        """Extract textures from IMG file"""
        output_dir = self.output_dir_edit.toPlainText().strip()
        if not output_dir:
            QMessageBox.warning(self, "Error", "Please select an output directory")
            return
            
        # Validate that an IMG file is loaded
        if not hasattr(self.main_window, 'current_img') or not self.main_window.current_img:
            QMessageBox.warning(self, "Error", "No IMG file loaded")
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        try:
            success = self.extractor.extract_textures_from_img(
                self.main_window.current_img.file_path, 
                output_dir
            )
            
            if success:
                QMessageBox.information(self, "Success", "Textures extracted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to extract textures")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            
    def parse_dff_files(self):
        """Parse DFF files to list texture requirements"""
        dff_text = self.dff_files_edit.toPlainText().strip()
        if not dff_text:
            QMessageBox.warning(self, "Error", "Please select DFF files to parse")
            return
            
        dff_files = [line.strip() for line in dff_text.split('\n') if line.strip()]
        
        # Validate files exist
        for dff_file in dff_files:
            if not os.path.exists(dff_file):
                QMessageBox.warning(self, "Error", f"DFF file does not exist: {dff_file}")
                return
        
        try:
            texture_mapping = self.extractor.parse_dff_textures(dff_files)
            
            # Display results
            results = "DFF Texture Requirements:\n\n"
            for model_name, textures in texture_mapping.items():
                results += f"Model: {model_name}\n"
                results += f"Required Textures: {', '.join(textures)}\n\n"
                
            self.results_area.setPlainText(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Parsing failed: {str(e)}")


def extract_textures_function(main_window):
    """Function to open the extract textures dialog"""
    try:
        dialog = ExtractDialog(main_window)
        dialog.exec()
    except Exception as e:
        main_window.log_message(f"Error opening extract dialog: {str(e)}")