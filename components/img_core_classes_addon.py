#this belongs in components/ img_core_classes_addon.py - Version: 2
# X-Seti - July13 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Core Classes Addon - Adds essential methods to existing IMG classes
Only contains non-duplicate functionality not covered in img_import_export_functions.py
"""

from typing import Optional, Tuple


def patch_img_file_with_core_methods(img_file_class):
    """Add essential core methods to IMGFile class (non-import/export)"""
    
    def get_entry_by_name(self, name: str):
        """Find entry by exact name match"""
        try:
            if hasattr(self, 'entries'):
                for entry in self.entries:
                    if getattr(entry, 'name', '') == name:
                        return entry
            return None
        except Exception:
            return None
    
    def get_entries_by_type(self, file_type: str):
        """Get all entries of specified file type"""
        try:
            matching_entries = []
            if hasattr(self, 'entries'):
                for entry in self.entries:
                    entry_name = getattr(entry, 'name', '')
                    if '.' in entry_name:
                        ext = entry_name.split('.')[-1].upper()
                        if ext == file_type.upper():
                            matching_entries.append(entry)
            return matching_entries
        except Exception:
            return []
    
    def get_file_statistics(self) -> dict:
        """Get IMG file statistics"""
        try:
            stats = {
                'total_entries': 0,
                'total_size': 0,
                'file_types': {},
                'largest_entry': None,
                'smallest_entry': None
            }
            
            if not hasattr(self, 'entries') or not self.entries:
                return stats
            
            stats['total_entries'] = len(self.entries)
            largest_size = 0
            smallest_size = float('inf')
            
            for entry in self.entries:
                entry_size = getattr(entry, 'size', 0)
                entry_name = getattr(entry, 'name', '')
                
                # Total size
                stats['total_size'] += entry_size
                
                # File types
                if '.' in entry_name:
                    ext = entry_name.split('.')[-1].upper()
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                # Largest entry
                if entry_size > largest_size:
                    largest_size = entry_size
                    stats['largest_entry'] = {
                        'name': entry_name,
                        'size': entry_size
                    }
                
                # Smallest entry
                if entry_size < smallest_size and entry_size > 0:
                    smallest_size = entry_size
                    stats['smallest_entry'] = {
                        'name': entry_name,
                        'size': entry_size
                    }
            
            return stats
            
        except Exception:
            return {'error': 'Failed to calculate statistics'}
    
    def validate_integrity(self) -> Tuple[bool, str]:
        """Validate IMG file integrity"""
        try:
            if not hasattr(self, 'entries'):
                return False, "No entries found"
            
            if not self.entries:
                return True, "Empty IMG file is valid"
            
            issues = []
            
            # Check for duplicate names
            names = []
            for entry in self.entries:
                name = getattr(entry, 'name', '')
                if name in names:
                    issues.append(f"Duplicate entry name: {name}")
                else:
                    names.append(name)
            
            # Check entry sizes
            for entry in self.entries:
                size = getattr(entry, 'size', 0)
                if size < 0:
                    name = getattr(entry, 'name', 'unknown')
                    issues.append(f"Invalid size for entry: {name}")
            
            # Check total entries
            if len(self.entries) > 65535:  # IMG format limit
                issues.append("Too many entries (>65535)")
            
            if issues:
                return False, "; ".join(issues)
            else:
                return True, "IMG file integrity OK"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _read_entry_data_fallback(self, entry):
        """Fallback method for reading entry data when other methods fail"""
        try:
            if not hasattr(self, 'file_path') or not self.file_path:
                return b''
            
            offset = getattr(entry, 'offset', 0)
            size = getattr(entry, 'size', 0)
            
            if size <= 0:
                return b''
            
            with open(self.file_path, 'rb') as f:
                f.seek(offset)
                return f.read(size)
                
        except Exception:
            return b''
    
    # Add methods to the class
    img_file_class.get_entry_by_name = get_entry_by_name
    img_file_class.get_entries_by_type = get_entries_by_type
    img_file_class.get_file_statistics = get_file_statistics
    img_file_class.validate_integrity = validate_integrity
    img_file_class._read_entry_data_fallback = _read_entry_data_fallback
    
    print("✅ IMGFile class patched with core utility methods")


def patch_img_entry_with_data_methods(img_entry_class):
    """Add data access methods to IMGEntry class"""
    
    def get_data(self):
        """Get entry data with multiple fallback methods"""
        try:
            # Method 1: Check for cached data
            if hasattr(self, '_cached_data') and self._cached_data:
                return self._cached_data
            
            # Method 2: Use IMG file's get_entry_data method
            if hasattr(self, '_img_file') and self._img_file:
                if hasattr(self._img_file, 'get_entry_data'):
                    return self._img_file.get_entry_data(self)
                
                # Method 3: Use fallback method
                if hasattr(self._img_file, '_read_entry_data_fallback'):
                    return self._img_file._read_entry_data_fallback(self)
            
            return b''
            
        except Exception as e:
            print(f"❌ Error getting entry data: {e}")
            return b''
    
    def set_data(self, data: bytes):
        """Set entry data (cache for later writing)"""
        try:
            self._cached_data = data
            self.size = len(data)
            
            # Mark as replaced if attribute exists
            if hasattr(self, 'is_replaced'):
                self.is_replaced = True
            
            # Mark IMG file as modified if available
            if hasattr(self, '_img_file') and self._img_file and hasattr(self._img_file, '_modified'):
                self._img_file._modified = True
                
        except Exception as e:
            print(f"❌ Error setting entry data: {e}")
    
    def set_img_file(self, img_file):
        """Set reference to parent IMG file"""
        try:
            self._img_file = img_file
        except Exception as e:
            print(f"❌ Error setting IMG file reference: {e}")
    
    def get_file_type(self) -> str:
        """Get file type based on extension"""
        try:
            name = getattr(self, 'name', '')
            if '.' in name:
                return name.split('.')[-1].upper()
            return 'UNKNOWN'
        except Exception:
            return 'UNKNOWN'
    
    def is_valid(self) -> bool:
        """Check if entry has valid data"""
        try:
            name = getattr(self, 'name', '')
            size = getattr(self, 'size', 0)
            offset = getattr(self, 'offset', 0)
            
            return bool(name and size >= 0 and offset >= 0)
        except Exception:
            return False
    
    # Add methods to the class
    img_entry_class.get_data = get_data
    img_entry_class.set_data = set_data
    img_entry_class.set_img_file = set_img_file
    img_entry_class.get_file_type = get_file_type
    img_entry_class.is_valid = is_valid
    
    print("✅ IMGEntry class patched with data access methods")


def integrate_core_class_methods():
    """Main function to integrate core class methods into existing classes"""
    try:
        # Import existing classes
        from components.img_core_classes import IMGFile, IMGEntry
        
        # Patch the classes with non-duplicate functionality
        patch_img_file_with_core_methods(IMGFile)
        patch_img_entry_with_data_methods(IMGEntry)
        
        print("✅ Core class methods integrated successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import existing IMG classes: {e}")
        return False
    except Exception as e:
        print(f"❌ Error integrating core class methods: {e}")
        return False


# Export main function
__all__ = [
    'patch_img_file_with_core_methods',
    'patch_img_entry_with_data_methods', 
    'integrate_core_class_methods'
]