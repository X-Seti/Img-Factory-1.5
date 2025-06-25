#!/usr/bin/env python3
"""
X-Seti - June05, 2025 - IMG Format Support - Game-Specific Implementations
Handles the nuances of different GTA game IMG formats
"""

import struct
import os
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from img_core_classes import IMGFile, IMGEntry, IMGVersion
from new_img_creator import NewIMGDialog, GameType, add_new_img_functionality

class GameSpecificFormat:
    """Base class for game-specific IMG format handling"""
    
    def __init__(self, game_type):
        self.game_type = game_type
        self.sector_size = 2048
        self.entry_size = 32  # Standard DIR entry size
    
    def create_header(self, entry_count: int = 0) -> bytes:
        """Create format-specific header"""
        raise NotImplementedError
    
    def create_entry_data(self, name: str, offset: int, size: int) -> bytes:
        """Create format-specific entry data"""
        raise NotImplementedError
    
    def validate_entry_name(self, name: str) -> bool:
        """Validate entry name for this format"""
        return len(name) <= 23 and all(ord(c) < 128 for c in name)

class GTA3Format(GameSpecificFormat):
    """GTA III specific IMG format"""
    
    def __init__(self):
        super().__init__("GTA III")
        self.uses_dir_file = True
        self.max_filename_length = 23
        
    def create_header(self, entry_count: int = 0) -> bytes:
        """GTA III uses separate DIR file, no header in IMG"""
        return b''
    
    def create_entry_data(self, name: str, offset: int, size: int) -> bytes:
        """Create DIR entry for GTA III"""
        # Convert bytes to sectors
        offset_sectors = offset // self.sector_size
        size_sectors = (size + self.sector_size - 1) // self.sector_size
        
        # Pack DIR entry: offset(4) + size(4) + name(24)
        entry_data = struct.pack('<II', offset_sectors, size_sectors)
        
        # Pad name to 24 bytes
        name_bytes = name.encode('ascii')[:23]
        name_bytes += b'\x00' * (24 - len(name_bytes))
        
        return entry_data + name_bytes
    
    def create_img_files(self, base_path: str, initial_size: int = 0) -> Tuple[str, str]:
        """Create both IMG and DIR files for GTA III"""
        img_path = base_path
        dir_path = base_path.replace('.img', '.dir')
        
        # Create empty DIR file
        with open(dir_path, 'wb') as f:
            pass  # Empty file
        
        # Create IMG file with initial size
        with open(img_path, 'wb') as f:
            if initial_size > 0:
                f.write(b'\x00' * initial_size)
        
        return img_path, dir_path

class GTAVCFormat(GTA3Format):
    """GTA Vice City specific IMG format (similar to GTA III)"""
    
    def __init__(self):
        super().__init__()
        self.game_type = "GTA Vice City"
        # VC has some minor differences in handling but same basic structure

class GTASAFormat(GameSpecificFormat):
    """GTA San Andreas specific IMG format"""
    
    def __init__(self):
        super().__init__("GTA San Andreas")
        self.uses_dir_file = False
        self.max_filename_length = 23
        
    def create_header(self, entry_count: int = 0) -> bytes:
        """Create GTA SA IMG header"""
        # VER2 signature + entry count
        return b'VER2' + struct.pack('<I', entry_count)
    
    def create_entry_data(self, name: str, offset: int, size: int) -> bytes:
        """Create entry data for GTA SA"""
        # Convert to sectors
        offset_sectors = offset // self.sector_size
        
        # For SA, we store both archive size and streaming size
        size_sectors = (size + self.sector_size - 1) // self.sector_size
        
        # Pack entry: offset(4) + archive_size(2) + streaming_size(2) + name(24)
        entry_data = struct.pack('<I', offset_sectors)
        entry_data += struct.pack('<HH', size_sectors, size_sectors)
        
        # Pad name to 24 bytes
        name_bytes = name.encode('ascii')[:23]
        name_bytes += b'\x00' * (24 - len(name_bytes))
        
        return entry_data + name_bytes
    
    def create_img_files(self, base_path: str, initial_size: int = 0) -> Tuple[str, str]:
        """Create IMG file for GTA SA (single file)"""
        with open(base_path, 'wb') as f:
            # Write header
            f.write(self.create_header(0))
            
            # Write initial padding
            if initial_size > 8:  # Account for header
                f.write(b'\x00' * (initial_size - 8))
        
        return base_path, None

class GTAStoriesFormat(GTA3Format):
    """GTA Stories (LCS/VCS) specific IMG format"""
    
    def __init__(self, is_lcs=True):
        super().__init__()
        self.game_type = "GTA Liberty City Stories" if is_lcs else "GTA Vice City Stories"
        self.is_lcs = is_lcs
        # Stories games use modified DIR/IMG structure
        
    def create_entry_data(self, name: str, offset: int, size: int) -> bytes:
        """Create DIR entry for Stories games (slightly different structure)"""
        # Stories games may have different entry structure
        # For now, use standard GTA3 format but could be enhanced
        return super().create_entry_data(name, offset, size)

class BullyFormat(GameSpecificFormat):
    """Bully (Canis Canem Edit) specific IMG format"""
    
    def __init__(self):
        super().__init__("Bully")
        self.uses_dir_file = True
        self.max_filename_length = 23
        self.sector_size = 2048
        
    def create_header(self, entry_count: int = 0) -> bytes:
        """Bully uses DIR file, no header in IMG"""
        return b''
    
    def create_entry_data(self, name: str, offset: int, size: int) -> bytes:
        """Create DIR entry for Bully (similar to GTA3 but may have differences)"""
        return super().create_entry_data(name, offset, size)
    
    def validate_entry_name(self, name: str) -> bool:
        """Bully has specific filename restrictions"""
        # Bully might be more restrictive with filenames
        if not super().validate_entry_name(name):
            return False
        
        # Additional Bully-specific validations
        forbidden_chars = ['#', '@', '$', '%']
        return not any(char in name for char in forbidden_chars)

class EnhancedIMGCreator:
    """Enhanced IMG creator with game-specific format support"""
    
    FORMAT_CLASSES = {
        'gta3': GTA3Format,
        'gtavc': GTAVCFormat, 
        'gtasa': GTASAFormat,
        'gtalcs': lambda: GTAStoriesFormat(is_lcs=True),
        'gtavcs': lambda: GTAStoriesFormat(is_lcs=False),
        'bully': BullyFormat
    }
    
    def __init__(self, game_type: str):
        self.game_type = game_type
        if game_type in self.FORMAT_CLASSES:
            format_class = self.FORMAT_CLASSES[game_type]
            self.format_handler = format_class() if callable(format_class) else format_class()
        else:
            raise ValueError(f"Unsupported game type: {game_type}")
    
    def create_new_img(self, filename: str, output_dir: str, **options) -> str:
        """Create new IMG file with game-specific formatting"""
        # Ensure proper extension
        if not filename.endswith('.img'):
            filename += '.img'
        
        img_path = os.path.join(output_dir, filename)
        initial_size = options.get('initial_size_mb', 10) * 1024 * 1024
        
        # Create files using format-specific method
        if hasattr(self.format_handler, 'create_img_files'):
            primary_path, secondary_path = self.format_handler.create_img_files(img_path, initial_size)
        else:
            # Fallback to basic creation
            with open(img_path, 'wb') as f:
                header = self.format_handler.create_header(0)
                f.write(header)
                if initial_size > len(header):
                    f.write(b'\x00' * (initial_size - len(header)))
            primary_path = img_path
        
        # Create additional structure if requested
        if options.get('create_structure', False):
            self._create_modding_structure(output_dir)
        
        # Create sample entries if requested
        if options.get('create_samples', False):
            self._create_sample_entries(primary_path)
        
        return primary_path
    
    def _create_modding_structure(self, base_dir: str):
        """Create modding-friendly directory structure"""
        directories = {
            'extracted': 'Extracted files from IMG archives',
            'custom': 'Custom modifications and new content', 
            'backup': 'Backup files before modification',
            'tools': 'Modding tools and utilities',
            'docs': 'Documentation and notes'
        }
        
        for dir_name, description in directories.items():
            dir_path = os.path.join(base_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create README in each directory
            readme_path = os.path.join(dir_path, 'README.txt')
            with open(readme_path, 'w') as f:
                f.write(f"{dir_name.title()} Directory\n")
                f.write("=" * 20 + "\n\n")
                f.write(f"{description}\n\n")
                f.write(f"Game: {self.format_handler.game_type}\n")
                f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tool: IMG Factory Enhanced\n")
    
    def _create_sample_entries(self, img_path: str):
        """Create sample entries for testing"""
        # This would add some sample files to demonstrate the format
        # Implementation depends on whether you want to include sample data
        pass
    
    def validate_for_game(self, entry_name: str) -> Tuple[bool, str]:
        """Validate entry name for specific game"""
        if not self.format_handler.validate_entry_name(entry_name):
            return False, f"Invalid filename for {self.format_handler.game_type}"
        
        # Game-specific validation
        if self.game_type == 'bully' and not entry_name.lower().endswith(('.dff', '.txd', '.col')):
            return False, "Bully primarily uses DFF, TXD, and COL files"
        
        return True, "Valid"
    
    def get_recommended_settings(self) -> Dict:
        """Get recommended settings for this game type"""
        settings = {
            'gta3': {
                'initial_size_mb': 50,
                'create_structure': True,
                'typical_extensions': ['.dff', '.txd', '.col'],
                'notes': 'GTA III uses DIR/IMG pairs. Keep archives under 2GB.'
            },
            'gtavc': {
                'initial_size_mb': 75, 
                'create_structure': True,
                'typical_extensions': ['.dff', '.txd', '.col'],
                'notes': 'Vice City supports larger archives than GTA III.'
            },
            'gtasa': {
                'initial_size_mb': 100,
                'create_structure': True,
                'typical_extensions': ['.dff', '.txd', '.col', '.ifp'],
                'notes': 'San Andreas uses single IMG files with VER2 header.'
            },
            'bully': {
                'initial_size_mb': 30,
                'create_structure': False,
                'typical_extensions': ['.dff', '.txd', '.col'],
                'notes': 'Bully has smaller archives and stricter filename rules.'
            }
        }
        
        return settings.get(self.game_type, {
            'initial_size_mb': 50,
            'create_structure': True,
            'typical_extensions': ['.dff', '.txd'],
            'notes': 'Generic IMG archive settings.'
        })

# Integration with the main dialog
class GameSpecificIMGDialog(NewIMGDialog):
    """Enhanced dialog with game-specific features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enhanced_creators = {}
        
        # Initialize enhanced creators for each game type
        for game_key in EnhancedIMGCreator.FORMAT_CLASSES.keys():
            try:
                self.enhanced_creators[game_key] = EnhancedIMGCreator(game_key)
            except Exception as e:
                print(f"Failed to initialize {game_key}: {e}")
    
    def _on_game_type_changed(self, button):
        """Enhanced game type change with format-specific settings"""
        super()._on_game_type_changed(button)
        
        # Update settings based on game-specific recommendations
        game_key = button.game_type.value
        if game_key in self.enhanced_creators:
            creator = self.enhanced_creators[game_key]
            settings = creator.get_recommended_settings()
            
            # Apply recommended settings
            if 'initial_size_mb' in settings:
                self.initial_size_spin.setValue(settings['initial_size_mb'])
            
            if 'create_structure' in settings:
                self.auto_structure_check.setChecked(settings['create_structure'])
            
            # Update notes in template info
            if 'notes' in settings:
                current_text = self.template_info_label.text()
                enhanced_text = current_text + f"\n\n<b>Recommendations:</b><br>{settings['notes']}"
                self.template_info_label.setText(enhanced_text)
    
    def _create_img_file(self):
        """Enhanced IMG creation with game-specific handling"""
        if not self.filename_input.text() or not self.output_path:
            QMessageBox.warning(self, "Validation Error", "Please enter filename and select output directory")
            return
        
        game_key = self.selected_game_type.value
        
        if game_key in self.enhanced_creators:
            try:
                creator = self.enhanced_creators[game_key]
                
                # Validate filename for this game
                filename = self.filename_input.text()
                is_valid, message = creator.validate_for_game(filename)
                
                if not is_valid:
                    QMessageBox.warning(self, "Validation Error", message)
                    return
                
                # Create with enhanced creator
                options = {
                    'initial_size_mb': self.initial_size_spin.value(),
                    'create_structure': self.auto_structure_check.isChecked(),
                    'create_samples': False  # Could add checkbox for this
                }
                
                created_path = creator.create_new_img(
                    filename, 
                    self.output_path, 
                    **options
                )
                
                QMessageBox.information(self, "Success", 
                                      f"Enhanced {creator.format_handler.game_type} IMG created!\n\n{created_path}")
                
                self.img_created.emit(created_path)
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "Creation Error", f"Failed to create IMG:\n{str(e)}")
        else:
            # Fallback to original creation method
            super()._create_img_file()

# Export the enhanced dialog for use
__all__ = [
    'EnhancedIMGCreator',
    'GameSpecificIMGDialog', 
    'GTA3Format',
    'GTASAFormat',
    'BullyFormat'
]
