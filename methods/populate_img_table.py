#this belongs in methods/populate_img_table.py - Version: 1
# X-Seti - July11 2025 - Img Factory 1.5 - Populate img table

"""
Table Structure Functions
Handles table population and setup for Img files
"""

import os
import shutil
import struct
import zlib
from typing import List, Tuple, Optional
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

from components.img_core_classes import IMGFile

## Methods list
# populate_img_table

def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries - FIXED VERSION"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries
    print(f"DEBUG: Populating table with {len(entries)} entries")

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension) - FIXED: Always use name-based detection
        if '.' in entry.name:
            file_type = entry.name.split('.')[-1].upper()
        else:
            file_type = "NO_EXT"

        print(f"DEBUG: Row {row}: {entry.name} -> Type: {file_type}")
        table.setItem(row, 1, QTableWidgetItem(file_type))

        # Size (formatted)
        try:
            from components.img_core_classes import format_file_size
            size_text = format_file_size(entry.size)
        except:
            size_text = f"{entry.size} bytes"
        table.setItem(row, 2, QTableWidgetItem(size_text))

        # Offset (hex format)
        table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))

        # Version - Improved detection
        version = "Unknown"
        try:
            if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                version = entry.get_version_text()
            elif hasattr(entry, 'version') and entry.version:
                version = str(entry.version)
            else:
                # Provide sensible defaults based on file type
                if file_type in ['DFF', 'TXD']:
                    version = "RenderWare"
                elif file_type == 'COL':
                    version = "COL"
                elif file_type == 'IFP':
                    version = "IFP"
                elif file_type == 'WAV':
                    version = "Audio"
                elif file_type == 'SCM':
                    version = "Script"
                else:
                    version = "Unknown"
        except Exception as e:
            print(f"DEBUG: Version detection error for {entry.name}: {e}")
            version = "Unknown"

        table.setItem(row, 4, QTableWidgetItem(version))

        # Compression
        compression = "None"
        try:
            if hasattr(entry, 'compression_type') and entry.compression_type:
                compression = str(entry.compression_type)
            elif hasattr(entry, 'compressed') and entry.compressed:
                compression = "Compressed"
        except:
            compression = "None"

        table.setItem(row, 5, QTableWidgetItem(compression))

        # Status
        status = "Ready"
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                status = "New"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                status = "Modified"
        except:
            status = "Ready"

        table.setItem(row, 6, QTableWidgetItem(status))

        # Make items read-only
        for col in range(7):
            item = table.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    print(f"DEBUG: Table population complete. Table now has {table.rowCount()} rows")

    # IMPORTANT: Clear any filters that might be hiding rows
    for row in range(table.rowCount()):
        table.setRowHidden(row, False)

    print(f"DEBUG: All rows made visible")


class IMGLoadThread():
    def populate_img_table(table: QTableWidget, img_file): #vers 4
        """Populate table with IMG file entries"""
        if not img_file or not img_file.entries:
            table.setRowCount(0)
            return

        entries = img_file.entries
        print(f"DEBUG: Populating table with {len(entries)} entries")

        # Clear existing data first
        table.setRowCount(0)
        table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # Name
            table.setItem(row, 0, QTableWidgetItem(entry.name))

            # Type (file extension) - FIXED: Always use name-based detection
            if '.' in entry.name:
                file_type = entry.name.split('.')[-1].upper()
            else:
                file_type = "Unknown"
            table.setItem(row, 1, QTableWidgetItem(file_type))

            # Size
            try:
                from components.img_core_classes import format_file_size
                size_text = format_file_size(entry.size)
            except:
                size_text = f"{entry.size} bytes"
            table.setItem(row, 2, QTableWidgetItem(size_text))

            # Offset
            table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))

            # Version
            version = "Unknown"
            try:
                if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                    version = entry.get_version_text()
                elif hasattr(entry, 'version') and entry.version:
                    version = str(entry.version)
                else:
                    # Provide sensible defaults based on file type
                    if file_type in ['DFF', 'TXD']:
                        version = "RenderWare"
                    elif file_type == 'COL':
                        version = "COL"
                    elif file_type == 'IFP':
                        version = "IFP"
                    elif file_type == 'WAV':
                        version = "Audio"
                    elif file_type == 'SCM':
                        version = "Script"
                    else:
                        version = "Unknown"
            except Exception as e:
                print(f"DEBUG: Version detection error for {entry.name}: {e}")
                version = "Unknown"

            table.setItem(row, 4, QTableWidgetItem(version))

            # Compression
            compression = "None"
            try:
                if hasattr(entry, 'compression_type') and entry.compression_type:
                    compression = str(entry.compression_type)
                elif hasattr(entry, 'compressed') and entry.compressed:
                    compression = "Compressed"
            except:
                compression = "None"

            table.setItem(row, 5, QTableWidgetItem(compression))

            # Status
            status = "Ready"
            try:
                if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                    status = "New"
                elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                    status = "Modified"
            except:
                status = "Ready"

            table.setItem(row, 6, QTableWidgetItem(status))

            # Make items read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        print(f"DEBUG: Table population complete.")


    def populate_img_table2(table: QTableWidget, img_file: IMGFile):
        """Populate table with IMG file entries"""
        if not img_file or not img_file.entries:
            table.setRowCount(0)
            return

        table.setRowCount(len(img_file.entries))

        for row, entry in enumerate(img_file.entries):
            # Filename
            table.setItem(row, 0, QTableWidgetItem(entry.name))
            # File type
            file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
            table.setItem(row, 1, QTableWidgetItem(file_type))
            # Size
            table.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
            # Offset
            table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))
            # Version
            table.setItem(row, 4, QTableWidgetItem(str(entry.version)))
            # Compression
            compression = "ZLib" if hasattr(entry, 'compressed') and entry.compressed else "None"
            table.setItem(row, 5, QTableWidgetItem(compression))
            # Status
            table.setItem(row, 6, QTableWidgetItem("Ready"))



# Export functions
__all__ = [
    'populate_img_table'
]
