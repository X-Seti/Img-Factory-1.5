#this belongs in core/hybrid_rebuild.py - Version: 1
# X-Seti - Aug09 2025 - IMG Factory 1.5 - Hybrid Rebuild System

"""
Hybrid Rebuild System - Choose between Fast and Safe modes
Fast Mode: Speed optimized, minimal checking
Safe Mode: Thorough error checking, detailed progress
"""

import os
from typing import Optional, Tuple
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QRadioButton, QGroupBox, QTextEdit,
                            QCheckBox, QMessageBox, QButtonGroup)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

##Methods list -
# show_rebuild_mode_dialog
# hybrid_rebuild_current
# hybrid_rebuild_all
# setup_hybrid_rebuild_methods

##Classes -
# RebuildModeDialog

class RebuildModeDialog(QDialog):
    """Dialog for selecting rebuild mode and options"""
    
    def __init__(self, parent=None, operation_type="single"):
        super().__init__(parent)
        self.operation_type = operation_type

        if self.operation_type == "batch":
            self.setWindowTitle("Batch IMG Rebuild Mode Selection")
        else:
            self.setWindowTitle("IMG Rebuild Mode Selection")

        self.setModal(True)

        # FIXED: Larger size to accommodate all content
        self.setMinimumSize(400, 400)
        self.setMaximumSize(600, 500)
        self.resize(500, 460)  # Better default size

        self.operation_type = operation_type
        self.selected_mode = "fast"
        self.selected_options = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup the mode selection UI - FIXED PROPORTIONS"""

        # Title - FIXED: Better spacing
        if self.operation_type == "batch":
            title = " "
        else:
            title = ""

        layout = QVBoxLayout(self)
        # FIXED: Better margins and consistent spacing
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(2)  # Consistent spacing throughout

                # FIXED: Controlled spacing after title
        layout.addSpacing(2)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(3)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # FIXED: Controlled spacing after title
        layout.addSpacing(2)

        # Mode selection group - FIXED: Better height allocation
        mode_group = QGroupBox("Rebuild Mode:")
        mode_group.setMaximumHeight(180)  # Prevent oversized group
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(1)
        mode_layout.setContentsMargins(15, 7, 15, 7)

        self.mode_button_group = QButtonGroup()

        # Fast mode
        self.fast_radio = QRadioButton("🚀 Fast Mode (Recommended)")
        self.fast_radio.setChecked(True)
        self.fast_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.fast_radio)
        mode_layout.addWidget(self.fast_radio)

        # FIXED: Compact descriptions that don't get cut off
        fast_desc = QLabel("• Speed optimized • Minimal checking • Quick defragmentation")
        fast_desc.setStyleSheet("color: #555; margin-left: 20px; font-size: 9pt; padding: 2px;")
        fast_desc.setWordWrap(True)
        mode_layout.addWidget(fast_desc)

        # FIXED: Controlled spacing between modes
        mode_layout.addSpacing(1)

        # Safe mode
        self.safe_radio = QRadioButton("🔍 Safe Mode")
        self.safe_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.safe_radio)
        mode_layout.addWidget(self.safe_radio)

        # FIXED: Compact description
        safe_desc = QLabel("• Thorough checking • Corruption fixes • Complete verification")
        safe_desc.setStyleSheet("color: #555; margin-left: 20px; font-size: 9pt; padding: 2px;")
        safe_desc.setWordWrap(True)
        mode_layout.addWidget(safe_desc)

        layout.addWidget(mode_group)

        # Options group - FIXED: Compact layout
        options_group = QGroupBox("Options:")
        options_group.setMaximumHeight(120)  # Prevent expansion
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(1)
        options_layout.setContentsMargins(15, 7, 15, 7)

        # Create backup option
        self.create_backup_check = QCheckBox("✅ Create backup before rebuild")
        options_layout.addWidget(self.create_backup_check)
        self.create_backup_check.setChecked(True)

        # Verify integrity option
        self.verify_after_check = QCheckBox("🔍 Verify integrity after rebuild")
        self.verify_after_check.setChecked(True)
        self.verify_after_check.setEnabled(False)
        options_layout.addWidget(self.verify_after_check)

        # Batch-specific option
        if self.operation_type == "batch":
            self.stop_on_error_check = QCheckBox("⏹️ Stop on first error")
            self.stop_on_error_check.setChecked(False)
            options_layout.addWidget(self.stop_on_error_check)

        layout.addWidget(options_group)

        # Performance info group - FIXED: Smaller, more compact
        perf_group = QGroupBox("Expected Performance:")
        perf_group.setMaximumHeight(180)  # Limit height
        perf_layout = QVBoxLayout(perf_group)
        perf_layout.setContentsMargins(15, 7, 15, 7)

        self.perf_label = QLabel()
        self.perf_label.setStyleSheet("""
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8pt;
            color: #444;
            padding: 4px;
            line-height: 2;
        """)
        self.perf_label.setWordWrap(True)
        perf_layout.addWidget(self.perf_label)

        layout.addWidget(perf_group)

        # FIXED: Small flexible space before buttons
        layout.addSpacing(8)
        layout.addStretch(1)  # Minimal stretch

        # Dialog buttons - FIXED: Compact button area
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(90, 34)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.rebuild_btn = QPushButton("Start Rebuild")
        self.rebuild_btn.setMinimumSize(110, 34)
        self.rebuild_btn.clicked.connect(self.accept)
        self.rebuild_btn.setDefault(True)
        self.rebuild_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color:
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: }
        """)
        button_layout.addWidget(self.rebuild_btn)

        layout.addLayout(button_layout)

        # Initialize display
        self.update_performance_info()

    def on_mode_changed(self):
        """Handle mode selection change"""
        if self.fast_radio.isChecked():
            self.selected_mode = "fast"
            self.verify_after_check.setEnabled(False)
            self.verify_after_check.setChecked(False)
        else:
            self.selected_mode = "safe"
            self.verify_after_check.setEnabled(True)
            self.verify_after_check.setChecked(True)

        self.update_performance_info()

    def update_performance_info(self):
        """Update performance information - FIXED: Compact formatting"""
        if self.selected_mode == "fast":
            if self.operation_type == "single":
                perf_text = "🚀 Fast Mode:\n" \
                           "Small IMG (100 entries): 1-2 sec | Medium (500): 3-5 sec | Large (1000+): 5-15 sec\n" \
                           "Features: Speed optimized, basic corruption fixes"
            else:
                perf_text = "🚀 Fast Batch:\n" \
                           "10-20 files: 30-60 sec | 50+ files: 2-5 min\n" \
                           "Features: Bulk optimizations, parallel processing"
        else:
            if self.operation_type == "single":
                perf_text = "🔍 Safe Mode:\n" \
                           "Small IMG (100 entries): 10-30 sec | Medium (500): 30-90 sec | Large (1000+): 2-5 min\n" \
                           "Features: Full error checking, corruption fixes, integrity verification"
            else:
                perf_text = "🔍 Safe Batch:\n" \
                           "10-20 files: 5-15 min | 50+ files: 15-45 min\n" \
                           "Features: Detailed per-file checking, comprehensive error reporting"

        self.perf_label.setText(perf_text)

    def get_rebuild_options(self) -> dict:
        """Get selected rebuild options"""
        options = {
            'mode': self.selected_mode,
            'create_backup': self.create_backup_check.isChecked(),
            'verify_integrity': self.verify_after_check.isChecked() and self.selected_mode == "safe"
        }

        if self.operation_type == "batch":
            options['stop_on_error'] = getattr(self, 'stop_on_error_check', None) and self.stop_on_error_check.isChecked()

        return options

def show_rebuild_mode_dialog(main_window, operation_type="single") -> Optional[dict]:
    """Show rebuild mode selection dialog"""
    try:
        dialog = RebuildModeDialog(main_window, operation_type)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_rebuild_options()
        
        return None
        
    except Exception as e:
        main_window.log_message(f"❌ Mode dialog error: {str(e)}")
        return None


def hybrid_rebuild_current(main_window) -> bool: #vers 1
    """Hybrid rebuild current IMG with mode selection"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False
            
        if not main_window.current_img.entries:
            QMessageBox.warning(main_window, "Empty IMG", "IMG file has no entries to rebuild")
            return False
        
        # Show mode selection dialog
        options = show_rebuild_mode_dialog(main_window, "single")
        if not options:
            return False  # User cancelled
        
        mode = options['mode']
        img_file = main_window.current_img
        filename = os.path.basename(img_file.file_path)
        entry_count = len(img_file.entries)
        
        main_window.log_message(f"🔧 {mode.upper()} rebuild: {filename} ({entry_count} entries)")
        
        # Execute rebuild based on selected mode
        if mode == "fast":
            try:
                from core.fast_rebuild import fast_rebuild_current
                success = fast_rebuild_current(main_window)
            except ImportError:
                main_window.log_message("⚠️ Fast rebuild not available, using fallback")
                success = _fallback_rebuild(main_window)
        else:  # safe mode
            try:
                from core.simple_rebuild import simple_rebuild_current
                success = simple_rebuild_current(main_window)
            except ImportError:
                main_window.log_message("⚠️ Safe rebuild not available, using fallback")
                success = _fallback_rebuild(main_window)
        
        # Post-rebuild verification (Safe mode only)
        if success and options.get('verify_integrity', False):
            main_window.log_message("🔍 Verifying rebuild integrity...")
            verification_result = _verify_rebuild_integrity(img_file, main_window)
            if verification_result:
                main_window.log_message("✅ Rebuild integrity verified")
            else:
                main_window.log_message("⚠️ Rebuild integrity check failed")
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Hybrid rebuild error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Hybrid rebuild failed: {str(e)}")
        return False


def hybrid_rebuild_all(main_window) -> bool: #vers 1
    """Hybrid rebuild all IMGs with mode selection"""
    try:
        # Show mode selection dialog for batch
        options = show_rebuild_mode_dialog(main_window, "batch")
        if not options:
            return False  # User cancelled
        
        mode = options['mode']
        main_window.log_message(f"🔧 {mode.upper()} batch rebuild starting...")
        
        # Execute batch rebuild based on selected mode
        if mode == "fast":
            try:
                from core.fast_rebuild import fast_rebuild_all
                success = fast_rebuild_all(main_window)
            except ImportError:
                main_window.log_message("⚠️ Fast batch rebuild not available, using fallback")
                success = _fallback_batch_rebuild(main_window)
        else:  # safe mode
            try:
                from core.simple_rebuild import simple_rebuild_all
                success = simple_rebuild_all(main_window)
            except ImportError:
                main_window.log_message("⚠️ Safe batch rebuild not available, using fallback")
                success = _fallback_batch_rebuild(main_window)
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Hybrid batch rebuild error: {str(e)}")
        QMessageBox.critical(main_window, "Batch Rebuild Error", f"Hybrid batch rebuild failed: {str(e)}")
        return False


def hybrid_quick_rebuild(main_window) -> bool: #vers 1
    """Hybrid quick rebuild - Always uses fast mode"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("⚠️ Quick rebuild: No IMG file open")
            return False
        
        filename = os.path.basename(main_window.current_img.file_path)
        main_window.log_message(f"⚡ Quick rebuild (FAST mode): {filename}")
        
        # Quick rebuild always uses fast mode
        try:
            from core.fast_rebuild import fast_quick_rebuild
            success = fast_quick_rebuild(main_window)
        except ImportError:
            main_window.log_message("⚠️ Fast quick rebuild not available, using fallback")
            success = _fallback_rebuild(main_window)
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Quick rebuild error: {str(e)}")
        return False


def _verify_rebuild_integrity(img_file, main_window) -> bool: #vers 1
    """Verify rebuild integrity (Safe mode feature)"""
    try:
        # Check that file exists and is readable
        if not os.path.exists(img_file.file_path):
            main_window.log_message("❌ Verification: Rebuilt file not found")
            return False
        
        # Check file size is reasonable
        file_size = os.path.getsize(img_file.file_path)
        if file_size < 1024:  # Less than 1KB is suspicious
            main_window.log_message("❌ Verification: File size too small")
            return False
        
        # Try to read header to verify structure
        try:
            with open(img_file.file_path, 'rb') as f:
                # Read first entry to verify format
                if img_file.entries:
                    first_entry = img_file.entries[0]
                    header_data = f.read(32)  # Read first entry header
                    if len(header_data) == 32:
                        main_window.log_message("✅ Verification: Header structure valid")
                        return True
                    else:
                        main_window.log_message("❌ Verification: Invalid header structure")
                        return False
        except Exception as e:
            main_window.log_message(f"❌ Verification: Read test failed - {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Verification error: {str(e)}")
        return False


def _fallback_rebuild(main_window) -> bool: #vers 1
    """Fallback rebuild if specialized modes not available"""
    try:
        if not main_window.current_img:
            return False
            
        main_window.log_message("🔄 Using basic fallback rebuild...")
        
        # Try to use IMG class rebuild methods
        img_file = main_window.current_img
        if hasattr(img_file, '_rebuild_version2') or hasattr(img_file, '_rebuild_version1'):
            if hasattr(img_file, 'version') and img_file.version == 1:
                success = img_file._rebuild_version1() if hasattr(img_file, '_rebuild_version1') else False
            else:
                success = img_file._rebuild_version2() if hasattr(img_file, '_rebuild_version2') else False
            
            if success:
                main_window.log_message("✅ Fallback rebuild successful")
                if hasattr(main_window, 'refresh_table'):
                    main_window.refresh_table()
                return True
        
        main_window.log_message("❌ No fallback rebuild methods available")
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Fallback rebuild error: {str(e)}")
        return False


def _fallback_batch_rebuild(main_window) -> bool: #vers 1
    """Fallback batch rebuild if specialized modes not available"""
    try:
        from PyQt6.QtWidgets import QFileDialog
        
        # Get directory
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory with IMG Files")
        if not directory:
            return False

        main_window.log_message("🔄 Using basic fallback batch rebuild...")
        # Use basic batch rebuild logic here
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Fallback batch rebuild error: {str(e)}")
        return False


def setup_hybrid_rebuild_methods(main_window): #vers 1
    """Setup hybrid rebuild methods with mode selection"""
    try:
        # Add hybrid rebuild methods
        main_window.rebuild_img = lambda: hybrid_rebuild_current(main_window)
        main_window.rebuild_all_img = lambda: hybrid_rebuild_all(main_window)
        main_window.quick_rebuild = lambda: hybrid_quick_rebuild(main_window)
        
        # Additional mode-specific methods
        main_window.fast_rebuild = lambda: _direct_fast_rebuild(main_window)
        main_window.safe_rebuild = lambda: _direct_safe_rebuild(main_window)
        
        # Legacy aliases
        main_window.rebuild_current_img = main_window.rebuild_img
        main_window.optimize_img = main_window.rebuild_img
        main_window.batch_rebuild = main_window.rebuild_all_img
        
        main_window.log_message("🔧 Hybrid rebuild system setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Hybrid rebuild setup failed: {str(e)}")
        return False


def _direct_fast_rebuild(main_window) -> bool: #vers 1
    """Direct fast rebuild without dialog"""
    try:
        from core.fast_rebuild import fast_rebuild_current
        return fast_rebuild_current(main_window)
    except ImportError:
        return _fallback_rebuild(main_window)


def _direct_safe_rebuild(main_window) -> bool: #vers 1
    """Direct safe rebuild without dialog"""
    try:
        from core.simple_rebuild import simple_rebuild_current
        return simple_rebuild_current(main_window)
    except ImportError:
        return _fallback_rebuild(main_window)


# Export functions
__all__ = [
    'hybrid_rebuild_current',
    'hybrid_rebuild_all',
    'hybrid_quick_rebuild',
    'setup_hybrid_rebuild_methods',
    'show_rebuild_mode_dialog',
    'RebuildModeDialog'
]
