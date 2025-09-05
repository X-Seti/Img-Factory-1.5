#this belongs in methods/ img_validation.py - Version: 1
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Validation

"""
IMG Validation - File and Structure Validation
Validation functions extracted from img_core_classes.py
Used for IMG file integrity and structure validation
"""

import os
import struct
from typing import Optional, Any, List, Dict, Tuple
from pathlib import Path
from enum import Enum

##Methods list -
# validate_img_file_structure
# validate_img_entries
# validate_entry_integrity
# check_file_corruption
# validate_rw_data
# repair_img_structure
# get_validation_report
# ValidationResult
# integrate_validation_functions

##Classes -
# ValidationResult
# ValidationLevel

class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """Validation result container"""
    def __init__(self, level: ValidationLevel, message: str, details: str = ""): #vers 1
        self.level = level
        self.message = message
        self.details = details
        self.timestamp = None
        
        # Set timestamp
        try:
            from datetime import datetime
            self.timestamp = datetime.now()
        except ImportError:
            pass
    
    def __str__(self):
        return f"[{self.level.value.upper()}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'level': self.level.value,
            'message': self.message,
            'details': self.details,
            'timestamp': str(self.timestamp) if self.timestamp else None
        }


def validate_img_file_structure(img_file) -> List[ValidationResult]: #vers 1
    """Validate IMG file structure and return issues"""
    results = []
    
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Check basic attributes
        if not hasattr(img_file, 'file_path'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "IMG file missing file_path attribute"
            ))
            return results
        
        file_path = getattr(img_file, 'file_path', '')
        if not file_path:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "IMG file has empty file_path"
            ))
            return results
        
        # Check file existence
        if not os.path.exists(file_path):
            results.append(ValidationResult(
                ValidationLevel.CRITICAL,
                f"IMG file not found: {file_path}"
            ))
            return results
        
        # Check version attribute
        if not hasattr(img_file, 'version'):
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                "IMG file missing version attribute"
            ))
        else:
            version = getattr(img_file, 'version', None)
            if version is None:
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    "IMG file has null version"
                ))
        
        # Check entries attribute
        if not hasattr(img_file, 'entries'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "IMG file missing entries attribute"
            ))
        else:
            entries = getattr(img_file, 'entries', [])
            if not isinstance(entries, list):
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    "IMG entries is not a list"
                ))
            else:
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"IMG file has {len(entries)} entries"
                ))
        
        # Check platform attribute
        if hasattr(img_file, 'platform'):
            platform = getattr(img_file, 'platform', None)
            if platform:
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"IMG platform: {platform}"
                ))
        
        # File size check
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    "IMG file is empty (0 bytes)"
                ))
            elif file_size < 2048:  # Minimum reasonable size
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    f"IMG file very small ({file_size} bytes)"
                ))
            else:
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"IMG file size: {file_size} bytes"
                ))
        except OSError as e:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"Cannot read IMG file size: {e}"
            ))
        
        if img_debugger:
            img_debugger.debug(f"IMG structure validation completed: {len(results)} issues found")
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.CRITICAL,
            f"IMG structure validation failed: {str(e)}"
        ))
    
    return results


def validate_img_entries(img_file) -> List[ValidationResult]: #vers 1
    """Validate all entries in IMG file"""
    results = []
    
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not hasattr(img_file, 'entries'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "No entries to validate"
            ))
            return results
        
        entries = getattr(img_file, 'entries', [])
        if not entries:
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "IMG file has no entries"
            ))
            return results
        
        # Validate each entry
        duplicate_names = set()
        seen_names = set()
        
        for i, entry in enumerate(entries):
            # Validate individual entry
            entry_results = validate_entry_integrity(entry, i)
            results.extend(entry_results)
            
            # Check for duplicate names
            entry_name = getattr(entry, 'name', '')
            if entry_name:
                if entry_name.lower() in seen_names:
                    duplicate_names.add(entry_name)
                else:
                    seen_names.add(entry_name.lower())
        
        # Report duplicates
        for dup_name in duplicate_names:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"Duplicate entry name found: {dup_name}"
            ))
        
        # Summary
        results.append(ValidationResult(
            ValidationLevel.INFO,
            f"Validated {len(entries)} entries, {len(duplicate_names)} duplicates found"
        ))
        
        if img_debugger:
            img_debugger.debug(f"Entry validation completed for {len(entries)} entries")
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.CRITICAL,
            f"Entry validation failed: {str(e)}"
        ))
    
    return results


def validate_entry_integrity(entry, index: int = -1) -> List[ValidationResult]: #vers 1
    """Validate single entry integrity"""
    results = []
    
    try:
        entry_id = f"Entry {index}" if index >= 0 else "Entry"
        
        # Check name
        if not hasattr(entry, 'name'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"{entry_id} missing name attribute"
            ))
        else:
            name = getattr(entry, 'name', '')
            if not name:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    f"{entry_id} has empty name"
                ))
            elif len(name) > 24:  # IMG filename limit
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    f"{entry_id} name too long ({len(name)} chars): {name}"
                ))
        
        # Check size
        if not hasattr(entry, 'size'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"{entry_id} missing size attribute"
            ))
        else:
            size = getattr(entry, 'size', 0)
            if size < 0:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    f"{entry_id} has negative size: {size}"
                ))
            elif size == 0:
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    f"{entry_id} has zero size"
                ))
        
        # Check offset
        if not hasattr(entry, 'offset'):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"{entry_id} missing offset attribute"
            ))
        else:
            offset = getattr(entry, 'offset', 0)
            if offset < 0:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    f"{entry_id} has negative offset: {offset}"
                ))
        
        # Check for data availability
        has_data = False
        if hasattr(entry, 'data') and getattr(entry, 'data'):
            has_data = True
        elif hasattr(entry, '_cached_data') and getattr(entry, '_cached_data'):
            has_data = True
        elif hasattr(entry, 'get_data'):
            has_data = True
        
        if not has_data:
            results.append(ValidationResult(
                ValidationLevel.INFO,
                f"{entry_id} has no cached data (will read from file)"
            ))
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.CRITICAL,
            f"Entry integrity check failed: {str(e)}"
        ))
    
    return results


def check_file_corruption(img_file) -> List[ValidationResult]: #vers 1
    """Check for signs of file corruption"""
    results = []
    
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        file_path = getattr(img_file, 'file_path', '')
        if not file_path or not os.path.exists(file_path):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "Cannot check corruption - file not accessible"
            ))
            return results
        
        # Check file header for Version 2 IMG
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if len(header) >= 8:
                    # Check for VER2 signature
                    if header[:4] == b'VER2':
                        # Read entry count
                        entry_count = struct.unpack('<I', header[4:8])[0]
                        
                        # Sanity check entry count
                        if entry_count > 100000:  # Unreasonably high
                            results.append(ValidationResult(
                                ValidationLevel.ERROR,
                                f"Suspicious entry count: {entry_count} (possible corruption)"
                            ))
                        elif entry_count == 0:
                            results.append(ValidationResult(
                                ValidationLevel.INFO,
                                "IMG file has 0 entries in header"
                            ))
                        else:
                            results.append(ValidationResult(
                                ValidationLevel.INFO,
                                f"Header entry count: {entry_count}"
                            ))
                    else:
                        # No VER2 signature - might be Version 1 or corrupted
                        results.append(ValidationResult(
                            ValidationLevel.WARNING,
                            "No VER2 signature found (Version 1 or corrupted)"
                        ))
        except Exception as e:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"Header corruption check failed: {e}"
            ))
        
        # Check entry offset consistency
        if hasattr(img_file, 'entries'):
            entries = getattr(img_file, 'entries', [])
            file_size = os.path.getsize(file_path)
            
            for i, entry in enumerate(entries):
                offset = getattr(entry, 'offset', 0)
                size = getattr(entry, 'size', 0)
                
                # Check if entry extends beyond file
                if offset + size > file_size:
                    results.append(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Entry {i} extends beyond file end (offset: {offset}, size: {size}, file: {file_size})"
                    ))
        
        if img_debugger:
            img_debugger.debug("File corruption check completed")
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.CRITICAL,
            f"Corruption check failed: {str(e)}"
        ))
    
    return results


def validate_rw_data(entry) -> List[ValidationResult]: #vers 1
    """Validate RenderWare data structure"""
    results = []
    
    try:
        # Check if entry has RW data
        if not hasattr(entry, 'rw_version'):
            results.append(ValidationResult(
                ValidationLevel.INFO,
                f"{entry.name} has no RW version info"
            ))
            return results
        
        rw_version = getattr(entry, 'rw_version', 0)
        if rw_version == 0:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"{entry.name} has invalid RW version (0)"
            ))
            return results
        
        # Check RW version string
        if hasattr(entry, 'rw_version_string'):
            rw_version_string = getattr(entry, 'rw_version_string', '')
            results.append(ValidationResult(
                ValidationLevel.INFO,
                f"{entry.name} RW version: {rw_version_string}"
            ))
        
        # Check section type
        if hasattr(entry, 'rw_section_type'):
            section_type = getattr(entry, 'rw_section_type', 0)
            results.append(ValidationResult(
                ValidationLevel.INFO,
                f"{entry.name} RW section type: 0x{section_type:X}"
            ))
        
        # Check section size
        if hasattr(entry, 'rw_section_size'):
            section_size = getattr(entry, 'rw_section_size', 0)
            entry_size = getattr(entry, 'size', 0)
            
            if section_size > entry_size:
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    f"{entry.name} RW section size ({section_size}) larger than entry size ({entry_size})"
                ))
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.ERROR,
            f"RW data validation failed for {getattr(entry, 'name', 'unknown')}: {str(e)}"
        ))
    
    return results


def repair_img_structure(img_file) -> List[ValidationResult]: #vers 1
    """Attempt to repair IMG structure issues"""
    results = []
    
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Initialize missing attributes
        if not hasattr(img_file, 'entries'):
            img_file.entries = []
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "Initialized missing entries list"
            ))
        
        if not hasattr(img_file, 'is_open'):
            img_file.is_open = False
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "Initialized missing is_open attribute"
            ))
        
        if not hasattr(img_file, 'modified'):
            img_file.modified = False
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "Initialized missing modified attribute"
            ))
        
        # Fix entry issues
        entries = getattr(img_file, 'entries', [])
        for i, entry in enumerate(entries):
            # Fix missing name
            if not hasattr(entry, 'name') or not getattr(entry, 'name', ''):
                entry.name = f"unknown_{i}"
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"Fixed missing name for entry {i}"
                ))
            
            # Fix missing size
            if not hasattr(entry, 'size'):
                entry.size = 0
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"Fixed missing size for entry {i}"
                ))
            
            # Fix missing offset
            if not hasattr(entry, 'offset'):
                entry.offset = 0
                results.append(ValidationResult(
                    ValidationLevel.INFO,
                    f"Fixed missing offset for entry {i}"
                ))
        
        if img_debugger:
            img_debugger.success(f"IMG structure repair completed: {len(results)} fixes applied")
        
    except Exception as e:
        results.append(ValidationResult(
            ValidationLevel.ERROR,
            f"Structure repair failed: {str(e)}"
        ))
    
    return results


def get_validation_report(img_file) -> Dict[str, Any]: #vers 1
    """Get comprehensive validation report"""
    try:
        # Run all validations
        structure_results = validate_img_file_structure(img_file)
        entry_results = validate_img_entries(img_file)
        corruption_results = check_file_corruption(img_file)
        
        # Combine results
        all_results = structure_results + entry_results + corruption_results
        
        # Count by severity
        counts = {
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
        
        for result in all_results:
            counts[result.level.value] += 1
        
        # Determine overall status
        if counts['critical'] > 0:
            status = 'critical'
        elif counts['error'] > 0:
            status = 'error'
        elif counts['warning'] > 0:
            status = 'warning'
        else:
            status = 'valid'
        
        return {
            'status': status,
            'total_issues': len(all_results),
            'counts': counts,
            'results': [result.to_dict() for result in all_results],
            'file_path': getattr(img_file, 'file_path', 'Unknown'),
            'entry_count': len(getattr(img_file, 'entries', []))
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Validation report generation failed: {str(e)}",
            'total_issues': 0,
            'counts': {},
            'results': [],
            'file_path': getattr(img_file, 'file_path', 'Unknown'),
            'entry_count': 0
        }


def integrate_validation_functions(main_window) -> bool: #vers 1
    """Integrate validation functions into main window"""
    try:
        # Add validation methods
        main_window.validate_img_file_structure = validate_img_file_structure
        main_window.validate_img_entries = validate_img_entries
        main_window.validate_entry_integrity = validate_entry_integrity
        main_window.check_file_corruption = check_file_corruption
        main_window.validate_rw_data = validate_rw_data
        main_window.repair_img_structure = repair_img_structure
        main_window.get_validation_report = get_validation_report
        
        # Add classes
        main_window.ValidationResult = ValidationResult
        main_window.ValidationLevel = ValidationLevel
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG validation functions integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Validation integration failed: {e}")
        return False


# Export functions and classes
__all__ = [
    'ValidationLevel',
    'ValidationResult',
    'validate_img_file_structure',
    'validate_img_entries',
    'validate_entry_integrity',
    'check_file_corruption',
    'validate_rw_data',
    'repair_img_structure',
    'get_validation_report',
    'integrate_validation_functions'
]