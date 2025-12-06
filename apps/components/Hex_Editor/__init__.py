"""
Hex Editor Component for IMG Factory
X-Seti - December 2025
"""

# This file makes Hex_Editor a Python package
from .Hex_Editor import HexEditorDialog, show_hex_editor_for_file, show_hex_editor_for_entry

__all__ = ['HexEditorDialog', 'show_hex_editor_for_file', 'show_hex_editor_for_entry']