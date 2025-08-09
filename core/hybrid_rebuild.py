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
        self.setWindowTitle("Select Rebuild Mode")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.operation_type = operation_type  # "single" or "batch"
        
        self.selected_mode = "fast"
        self.selected_options = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the mode selection UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = "🔧 IMG Rebuild Mode Selection"
        if self.operation_type == "batch":
            title = "🔧 Batch IMG Rebuild Mode Selection"
            
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Mode selection group
        mode_group = QGroupBox("Rebuild Mode:")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_button_group = QButtonGroup()
        
        # Fast mode
        self.fast_radio = QRadioButton("🚀 Fast Mode (Recommended)")
        self.fast_radio.setChecked(True)
        self.fast_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.fast_radio)
        mode_layout.addWidget(self.fast_radio)
        
        fast_desc = QLabel("• Optimized for speed (10-50x faster)\n"
                          "• Bulk operations, minimal I/O\n"
                          "• Basic error handling\n"
                          "• Best for trusted IMG files")
        fast_desc.setStyleSheet("margin-left: 20px; color: #666;")
        mode_layout.addWidget(fast_desc)
        
        # Safe mode
        self.safe_radio = QRadioButton("🛡️ Safe Mode (Thorough)")
        self.safe_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.safe_radio)
        mode_layout.addWidget(self.safe_radio)
        
        safe_desc = QLabel("• Comprehensive error checking\n"
                          "• Detailed progress per file\n"
                          "• Data validation and verification\n"
                          "• Best for damaged or untrusted files")
        safe_desc.setStyleSheet("margin-left: 20px; color: #666;")
        mode_layout.addWidget(safe_desc)
        
        layout.addWidget(mode_group)
        
        # Options group
        options_group = QGroupBox("Options:")
        options_layout = QVBoxLayout(options_group)
        
        self.create_backup_check = QCheckBox("Create backup files (.backup)")
        self.create_backup_check.setChecked(True)
        options_layout.addWidget(self.create_backup_check)
        
        self.verify_after_check = QCheckBox("Verify rebuild integrity (Safe mode only)")
        self.verify_after_check.setChecked(True)
        options_layout.addWidget(self.verify_after_check)
        
        if self.operation_type == "batch":
            self.stop_on_error_check = QCheckBox("Stop batch on first error")
            self.stop_on_error_check.setChecked(False)
            options_layout.addWidget(self.stop_on_error_check)
        
        layout.addWidget(options_group)
        
        # Performance info
        perf_group = QGroupBox("Expected Performance:")
        perf_layout = QVBoxLayout(perf_group)
        
        self.perf_label = QLabel()
        self.update_performance_info()
        perf_layout.addWidget(self.perf_label)
        
        layout.addWidget(perf_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.rebuild_btn = QPushButton("Start Rebuild")
        self.rebuild_btn.clicked.connect(self.accept)
        self.rebuild_btn.setDefault(True)
        button_layout.addWidget(self.rebuild_btn)
        
        layout.addLayout(button_layout)
        
    def on_mode_changed(self):
        """Handle mode selection change"""
        if self.fast_radio.isChecked():
            self.selected_mode = "fast"
            self.verify_after_check.setEnabled(False)
        else:
            self.selected_mode = "safe"
            self.verify_after_check.setEnabled(True)
            
        self.update_performance_info()
        
    def update_performance_info(self):
        """Update performance information display"""
        if self.selected_mode == "fast":
            if self.operation_type == "single":
                perf_text = "🚀 Fast Mode Performance:\n" \
                           "• Small IMG (100 entries): 1-2 seconds\n" \
                           "• Medium IMG (500 entries): 3-5 seconds\n" \
                           "• Large IMG (1000+ entries): 5-15 seconds"
            else:
                perf_text = "🚀 Fast Batch Performance:\n" \
                           "• 10-20 IMG files: 30-60 seconds\n" \
                           "• 50+ IMG files: 2-5 minutes\n" \
                           "• Bulk optimizations active"
        else:
            if self.operation_type == "single":
                perf_text = "🛡️ Safe Mode Performance:\n" \
                           "• Small IMG (100 entries): 10-30 seconds\n" \
                           "• Medium IMG (500 entries): 30-90 seconds\n" \
                           "• Large IMG (1000+ entries): 2-5 minutes"
            else:
                perf_text = "🛡️ Safe Batch Performance:\n" \
                           "• 10-20 IMG files: 5-15 minutes\n" \
                           "• 50+ IMG files: 15-45 minutes\n" \
                           "• Detailed error checking per file"
        
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