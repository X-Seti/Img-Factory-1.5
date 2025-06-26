#this belongs in /components/img_validator.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - IMG Validator - Complete Validation and Repair System
Credit MexUK 2007 IMG Factory 1.2 - Full validation suite port
"""

import os
import struct
import zlib
import hashlib
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

from img_manager import IMGVersion, IMGValidationResult, IMGEntry,  IMGFile, format_file_size


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation issues"""
    STRUCTURE = "structure"
    INTEGRITY = "integrity"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    CORRUPTION = "corruption"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    entry_name: Optional[str] = None
    offset: Optional[int] = None
    size: Optional[int] = None
    suggested_fix: Optional[str] = None
    auto_repairable: bool = False


@dataclass
class ValidationReport:
    """Complete validation report"""
    is_valid: bool = True
    file_path: str = ""
    img_version: IMGVersion = IMGVersion.UNKNOWN
    total_entries: int = 0
    total_size: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict = field(default_factory=dict)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues by severity level"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues by category"""
        return [issue for issue in self.issues if issue.category == category]
    
    def has_critical_issues(self) -> bool:
        """Check if report has critical issues"""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    def has_errors(self) -> bool:
        """Check if report has errors"""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    def get_summary(self) -> str:
        """Get validation summary"""
        if not self.issues:
            return "No issues found"
        
        summary = []
        for severity in ValidationSeverity:
            count = len(self.get_issues_by_severity(severity))
            if count > 0:
                summary.append(f"{severity.value.title()}: {count}")
        
        return ", ".join(summary)
    
    def get_auto_repairable_count(self) -> int:
        """Get count of auto-repairable issues"""
        return sum(1 for issue in self.issues if issue.auto_repairable)


class IMGValidator:
    """Complete IMG file validation system"""
    
    def __init__(self):
        self.deep_scan = False
        self.check_file_headers = True
        self.check_compression = True
        self.check_encryption = True
        self.check_duplicates = True
        self.calculate_checksums = True
        
        # Known file signatures for validation
        self.file_signatures = {
            'DFF': [b'\x10\x00\x00\x00', b'\x0F\x00\x00\x00'],  # RenderWare DFF
            'TXD': [b'\x16\x00\x00\x00'],  # RenderWare TXD
            'COL': [b'COLL'],  # Collision
            'IFP': [b'ANPK'],  # Animation package
            'WAV': [b'RIFF'],  # WAV audio
            'IMG': [b'VER2', b'VERF'],  # IMG signatures
        }
    
    @staticmethod
    def validate_img_file(img_file: IMGFile, deep_scan: bool = False) -> ValidationReport:
        """Main validation entry point"""
        validator = IMGValidator()
        validator.deep_scan = deep_scan
        return validator._validate_img(img_file)
    
    def _validate_img(self, img_file: IMGFile) -> ValidationReport:
        """Internal validation method"""
        report = ValidationReport()
        report.file_path = img_file.file_path
        report.img_version = img_file.version
        report.total_entries = len(img_file.entries)
        report.total_size = sum(entry.size for entry in img_file.entries)
        
        try:
            # Basic file system checks
            self._validate_file_system(img_file, report)
            
            # Version-specific validation
            self._validate_version_specific(img_file, report)
            
            # Header validation
            self._validate_headers(img_file, report)
            
            # Entry validation
            self._validate_entries(img_file, report)
            
            # Structure validation
            self._validate_structure(img_file, report)
            
            # Integrity validation
            if self.deep_scan:
                self._validate_integrity_deep(img_file, report)
            else:
                self._validate_integrity_basic(img_file, report)
            
            # Performance analysis
            self._analyze_performance(img_file, report)
            
            # Compatibility checks
            self._check_compatibility(img_file, report)
            
            # Generate statistics
            self._generate_statistics(img_file, report)
            
            # Determine overall validity
            report.is_valid = not (report.has_critical_issues() or report.has_errors())
            
        except Exception as e:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.STRUCTURE,
                message=f"Validation failed: {str(e)}"
            ))
            report.is_valid = False
        
        return report
    
    def _validate_file_system(self, img_file: IMGFile, report: ValidationReport):
        """Validate file system level issues"""
        # Check if file exists
        if not os.path.exists(img_file.file_path):
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.STRUCTURE,
                message="IMG file does not exist",
                suggested_fix="Restore file from backup"
            ))
            return
        
        # Check file size
        try:
            file_size = os.path.getsize(img_file.file_path)
            if file_size == 0:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.STRUCTURE,
                    message="IMG file is empty"
                ))
            elif file_size < 8:  # Minimum header size
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.STRUCTURE,
                    message="IMG file too small to contain valid header"
                ))
        except OSError as e:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.STRUCTURE,
                message=f"Cannot access file: {str(e)}"
            ))
        
        # Check for DIR file (Version 1)
        if img_file.version == IMGVersion.VERSION_1:
            dir_path = img_file.file_path.replace('.img', '.dir')
            if not os.path.exists(dir_path):
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.STRUCTURE,
                    message="DIR file missing for Version 1 IMG",
                    suggested_fix="Recreate DIR file or convert to Version 2"
                ))
        
        # Check file permissions
        if not os.access(img_file.file_path, os.R_OK):
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.STRUCTURE,
                message="IMG file not readable"
            ))
    
    def _validate_version_specific(self, img_file: IMGFile, report: ValidationReport):
        """Validate version-specific requirements"""
        if img_file.version == IMGVersion.UNKNOWN:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.STRUCTURE,
                message="Unknown IMG version",
                suggested_fix="Check file format or try manual version detection"
            ))
            return
        
        try:
            with open(img_file.file_path, 'rb') as f:
                header = f.read(32)
                
                if img_file.version == IMGVersion.VERSION_2:
                    if not header.startswith(b'VER2'):
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURE,
                            message="Invalid Version 2 signature"
                        ))
                
                elif img_file.version == IMGVersion.FASTMAN92:
                    if not header.startswith(b'VERF'):
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURE,
                            message="Invalid Fastman92 signature"
                        ))
                
                elif img_file.version == IMGVersion.VERSION_3:
                    try:
                        signature = struct.unpack('<I', header[:4])[0]
                        if signature != 0xA94E2A52:
                            report.issues.append(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category=ValidationCategory.STRUCTURE,
                                message="Invalid Version 3 signature"
                            ))
                    except struct.error:
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURE,
                            message="Cannot read Version 3 header"
                        ))
                        
        except Exception as e:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.STRUCTURE,
                message=f"Error validating version: {str(e)}"
            ))
    
    def _validate_headers(self, img_file: IMGFile, report: ValidationReport):
        """Validate IMG headers"""
        try:
            with open(img_file.file_path, 'rb') as f:
                if img_file.version == IMGVersion.VERSION_2:
                    f.seek(4)  # Skip signature
                    entry_count = struct.unpack('<I', f.read(4))[0]
                    
                    if entry_count != len(img_file.entries):
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURE,
                            message=f"Entry count mismatch: header={entry_count}, actual={len(img_file.entries)}",
                            auto_repairable=True,
                            suggested_fix="Rebuild IMG file to fix header"
                        ))
                    
                    # Check for reasonable entry count
                    if entry_count > 65535:  # Arbitrary reasonable limit
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.PERFORMANCE,
                            message=f"Very large entry count: {entry_count}"
                        ))
                
                elif img_file.version == IMGVersion.FASTMAN92:
                    f.seek(4)  # Skip signature
                    version, entry_count = struct.unpack('<II', f.read(8))
                    
                    if entry_count != len(img_file.entries):
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURE,
                            message=f"Fastman92 entry count mismatch: header={entry_count}, actual={len(img_file.entries)}",
                            auto_repairable=True
                        ))
                        
        except Exception as e:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.STRUCTURE,
                message=f"Error validating headers: {str(e)}"
            ))
    
    def _validate_entries(self, img_file: IMGFile, report: ValidationReport):
        """Validate individual entries"""
        seen_names = set()
        seen_offsets = set()
        
        for i, entry in enumerate(img_file.entries):
            # Check for duplicate names
            name_upper = entry.name.upper()
            if name_upper in seen_names:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Duplicate entry name: {entry.name}",
                    entry_name=entry.name,
                    auto_repairable=True,
                    suggested_fix="Rename duplicate entries"
                ))
            seen_names.add(name_upper)
            
            # Check for invalid names
            if not entry.name or len(entry.name.strip()) == 0:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Entry {i} has empty name",
                    auto_repairable=True
                ))
            
            # Check name length (IMG format limitation)
            if len(entry.name) > 23:  # 24 bytes with null terminator
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.COMPATIBILITY,
                    message=f"Entry name too long: {entry.name} ({len(entry.name)} chars)",
                    entry_name=entry.name,
                    suggested_fix="Shorten filename to 23 characters or less"
                ))
            
            # Check for invalid characters
            invalid_chars = '<>:"|?*'
            if any(char in entry.name for char in invalid_chars):
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPATIBILITY,
                    message=f"Entry name contains invalid characters: {entry.name}",
                    entry_name=entry.name
                ))
            
            # Check entry size
            if entry.size <= 0:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Entry has invalid size: {entry.name} ({entry.size} bytes)",
                    entry_name=entry.name
                ))
            elif entry.size > 1024 * 1024 * 1024:  # 1GB limit
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message=f"Entry is very large: {entry.name} ({format_file_size(entry.size)})",
                    entry_name=entry.name
                ))
            
            # Check entry offset
            if entry.offset < 0:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Entry has invalid offset: {entry.name} ({entry.offset})",
                    entry_name=entry.name,
                    offset=entry.offset
                ))
            
            # Check for overlapping offsets
            if entry.offset in seen_offsets:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.CORRUPTION,
                    message=f"Entry has overlapping offset: {entry.name} at {entry.offset}",
                    entry_name=entry.name,
                    offset=entry.offset
                ))
            
            if entry.offset > 0:  # Skip entries with 0 offset (new entries)
                seen_offsets.add(entry.offset)
            
            # Check sector alignment for versions that require it
            if img_file.version in [IMGVersion.VERSION_1, IMGVersion.VERSION_2]:
                if entry.offset % 2048 != 0:
                    report.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.STRUCTURE,
                        message=f"Entry not sector-aligned: {entry.name} (offset {entry.offset})",
                        entry_name=entry.name,
                        offset=entry.offset,
                        auto_repairable=True,
                        suggested_fix="Rebuild IMG to fix alignment"
                    ))
            
            # Validate file extension
            if not entry.extension and '.' in entry.name:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Entry extension not detected: {entry.name}",
                    entry_name=entry.name
                ))
            
            # Check for common file types
            if entry.extension:
                known_extensions = ['DFF', 'TXD', 'COL', 'IFP', 'WAV', 'SCM', 'CS', 'FXT', 'DAT']
                if entry.extension not in known_extensions:
                    report.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.COMPATIBILITY,
                        message=f"Unknown file type: {entry.name} (.{entry.extension})",
                        entry_name=entry.name
                    ))
    
    def _validate_structure(self, img_file: IMGFile, report: ValidationReport):
        """Validate overall IMG structure"""
        if not img_file.entries:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.STRUCTURE,
                message="IMG file contains no entries"
            ))
            return
        
        # Check for gaps and fragmentation
        sorted_entries = sorted([e for e in img_file.entries if e.offset > 0], key=lambda x: x.offset)
        
        total_gaps = 0
        overlaps = 0
        
        for i in range(len(sorted_entries) - 1):
            current = sorted_entries[i]
            next_entry = sorted_entries[i + 1]
            
            current_end = current.offset + current.get_padded_size()
            gap = next_entry.offset - current_end
            
            if gap > 0:
                total_gaps += gap
            elif gap < 0:
                overlaps += 1
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.CORRUPTION,
                    message=f"Overlapping entries: {current.name} and {next_entry.name}",
                    entry_name=current.name
                ))
        
        # Calculate fragmentation
        if sorted_entries:
            total_used = sum(e.get_padded_size() for e in sorted_entries)
            fragmentation = (total_gaps / (total_used + total_gaps)) * 100 if total_used > 0 else 0
            
            if fragmentation > 25:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message=f"High fragmentation: {fragmentation:.1f}%",
                    auto_repairable=True,
                    suggested_fix="Defragment IMG file"
                ))
            
            # Store fragmentation in statistics
            report.statistics['fragmentation_percentage'] = fragmentation
            report.statistics['total_gaps'] = total_gaps
            report.statistics['overlap_count'] = overlaps
    
    def _validate_integrity_basic(self, img_file: IMGFile, report: ValidationReport):
        """Basic integrity validation"""
        unreadable_entries = 0
        
        for entry in img_file.entries:
            try:
                # Try to read first few bytes
                if entry.offset > 0:  # Skip new entries
                    with open(img_file.file_path, 'rb') as f:
                        f.seek(entry.offset)
                        data = f.read(min(1024, entry.size))
                        
                        if len(data) == 0:
                            report.issues.append(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category=ValidationCategory.CORRUPTION,
                                message=f"Cannot read entry data: {entry.name}",
                                entry_name=entry.name
                            ))
                            unreadable_entries += 1
                        elif len(data) < min(1024, entry.size):
                            report.issues.append(ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                category=ValidationCategory.INTEGRITY,
                                message=f"Partial data read for entry: {entry.name}",
                                entry_name=entry.name
                            ))
                            
            except Exception as e:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.CORRUPTION,
                    message=f"Error reading entry {entry.name}: {str(e)}",
                    entry_name=entry.name
                ))
                unreadable_entries += 1
        
        report.statistics['unreadable_entries'] = unreadable_entries
    
    def _validate_integrity_deep(self, img_file: IMGFile, report: ValidationReport):
        """Deep integrity validation"""
        self._validate_integrity_basic(img_file, report)
        
        corrupted_files = 0
        signature_mismatches = 0
        
        for entry in img_file.entries:
            try:
                if entry.offset <= 0:  # Skip new entries
                    continue
                
                # Read full entry data
                data = entry.get_data()
                
                # Validate file signatures
                if self.check_file_headers and entry.extension in self.file_signatures:
                    expected_sigs = self.file_signatures[entry.extension]
                    if not any(data.startswith(sig) for sig in expected_sigs):
                        report.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.INTEGRITY,
                            message=f"File signature mismatch: {entry.name}",
                            entry_name=entry.name
                        ))
                        signature_mismatches += 1
                
                # Check for null/empty data
                if len(set(data[:min(1024, len(data))])) <= 1:
                    report.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.INTEGRITY,
                        message=f"Suspicious uniform data pattern: {entry.name}",
                        entry_name=entry.name
                    ))
                
                # Validate RenderWare files
                if entry.extension in ['DFF', 'TXD']:
                    self._validate_renderware_file(entry, data, report)
                
                # Calculate and store checksums if enabled
                if self.calculate_checksums:
                    entry.crc32 = zlib.crc32(data) & 0xffffffff
                    entry.md5_hash = hashlib.md5(data).hexdigest()
                
            except Exception as e:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.CORRUPTION,
                    message=f"Deep validation failed for {entry.name}: {str(e)}",
                    entry_name=entry.name
                ))
                corrupted_files += 1
        
        report.statistics['corrupted_files'] = corrupted_files
        report.statistics['signature_mismatches'] = signature_mismatches
    
    def _validate_renderware_file(self, entry: IMGEntry, data: bytes, report: ValidationReport):
        """Validate RenderWare file structure"""
        try:
            if len(data) < 12:  # Minimum RW section header
                return
            
            # Read RenderWare header
            section_type, section_size, rw_version = struct.unpack('<III', data[:12])
            
            # Validate section size
            if section_size + 12 > len(data):
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.INTEGRITY,
                    message=f"RenderWare section size mismatch: {entry.name}",
                    entry_name=entry.name
                ))
            
            # Store RenderWare version
            entry.rw_version = rw_version
            
            # Check for reasonable RW version
            if rw_version < 0x30000 or rw_version > 0x40000:
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.COMPATIBILITY,
                    message=f"Unusual RenderWare version: {entry.name} (0x{rw_version:08X})",
                    entry_name=entry.name
                ))
                
        except Exception:
            # Not a valid RenderWare file or corrupted
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.INTEGRITY,
                message=f"Invalid RenderWare structure: {entry.name}",
                entry_name=entry.name
            ))
    
    def _analyze_performance(self, img_file: IMGFile, report: ValidationReport):
        """Analyze performance-related issues"""
        if not img_file.entries:
            return
        
        # Analyze entry sizes
        sizes = [entry.size for entry in img_file.entries]
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        
        # Check for very small files (potential waste)
        small_files = [e for e in img_file.entries if e.size < 1024]
        if len(small_files) > len(img_file.entries) * 0.3:  # More than 30% are small files
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.PERFORMANCE,
                message=f"Many small files detected: {len(small_files)} files < 1KB",
                suggested_fix="Consider file consolidation"
            ))
        
        # Check for potential compression candidates
        if img_file.version == IMGVersion.FASTMAN92:
            large_uncompressed = [e for e in img_file.entries 
                                 if e.size > 10240 and not e.is_compressed]  # > 10KB
            if large_uncompressed:
                total_potential_savings = 0
                for entry in large_uncompressed[:10]:  # Test first 10 files
                    try:
                        data = entry.get_data()
                        compressed = zlib.compress(data, 6)
                        if len(compressed) < len(data) * 0.8:  # At least 20% compression
                            total_potential_savings += len(data) - len(compressed)
                    except:
                        continue
                
                if total_potential_savings > 1024 * 1024:  # > 1MB potential savings
                    report.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.PERFORMANCE,
                        message=f"Compression could save ~{format_file_size(total_potential_savings)}",
                        suggested_fix="Enable compression for large files"
                    ))
        
        # Store performance statistics
        report.statistics.update({
            'average_file_size': avg_size,
            'largest_file_size': max_size,
            'smallest_file_size': min_size,
            'small_files_count': len(small_files)
        })
    
    def _check_compatibility(self, img_file: IMGFile, report: ValidationReport):
        """Check compatibility issues"""
        # Check for game-specific issues
        if img_file.version == IMGVersion.VERSION_3:
            # GTA IV specific checks
            if any(entry.size > 16 * 1024 * 1024 for entry in img_file.entries):
                report.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPATIBILITY,
                    message="Very large files may cause issues in GTA IV"
                ))
        
        # Check total file count limits
        entry_count = len(img_file.entries)
        if entry_count > 10000:
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.COMPATIBILITY,
                message=f"Very high entry count ({entry_count}) may impact performance"
            ))
        
        # Check for long paths that might cause issues
        long_names = [e for e in img_file.entries if len(e.name) > 20]
        if len(long_names) > entry_count * 0.1:  # More than 10% have long names
            report.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.COMPATIBILITY,
                message=f"{len(long_names)} entries have long filenames"
            ))
    
    def _generate_statistics(self, img_file: IMGFile, report: ValidationReport):
        """Generate comprehensive statistics"""
        if not img_file.entries:
            return
        
        # File type distribution
        type_counts = {}
        for entry in img_file.entries:
            ext = entry.extension or "Unknown"
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        # Size distribution
        size_ranges = {
            '< 1KB': 0,
            '1KB - 10KB': 0,
            '10KB - 100KB': 0,
            '100KB - 1MB': 0,
            '1MB - 10MB': 0,
            '> 10MB': 0
        }
        
        for entry in img_file.entries:
            size = entry.size
            if size < 1024:
                size_ranges['< 1KB'] += 1
            elif size < 10240:
                size_ranges['1KB - 10KB'] += 1
            elif size < 102400:
                size_ranges['10KB - 100KB'] += 1
            elif size < 1048576:
                size_ranges['100KB - 1MB'] += 1
            elif size < 10485760:
                size_ranges['1MB - 10MB'] += 1
            else:
                size_ranges['> 10MB'] += 1
        
        # Compression statistics
        compression_stats = {
            'compressed_entries': 0,
            'uncompressed_entries': 0,
            'total_compressed_size': 0,
            'total_uncompressed_size': 0
        }
        
        for entry in img_file.entries:
            if entry.is_compressed:
                compression_stats['compressed_entries'] += 1
                compression_stats['total_compressed_size'] += entry.size
                compression_stats['total_uncompressed_size'] += entry.uncompressed_size
            else:
                compression_stats['uncompressed_entries'] += 1
        
        report.statistics.update({
            'file_type_distribution': type_counts,
            'size_distribution': size_ranges,
            'compression_statistics': compression_stats,
            'total_disk_size': os.path.getsize(img_file.file_path) if os.path.exists(img_file.file_path) else 0
        })
    
    def repair_img(self, img_file: IMGFile, report: ValidationReport, backup: bool = True) -> bool:
        """Attempt to repair IMG file based on validation report"""
        if backup:
            backup_path = img_file.file_path + '.backup'
            try:
                import shutil
                shutil.copy2(img_file.file_path, backup_path)
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
        
        repairs_made = 0
        
        # Fix auto-repairable issues
        for issue in report.issues:
            if not issue.auto_repairable:
                continue
            
            try:
                if "Entry count mismatch" in issue.message:
                    # This would be fixed by rebuilding
                    repairs_made += 1
                
                elif "not sector-aligned" in issue.message:
                    # This would be fixed by rebuilding
                    repairs_made += 1
                
                elif "Duplicate entry name" in issue.message:
                    # Rename duplicate entries
                    self._repair_duplicate_names(img_file)
                    repairs_made += 1
                
                elif "fragmentation" in issue.message.lower():
                    # Defragment by rebuilding
                    repairs_made += 1
                    
            except Exception as e:
                print(f"Error during repair: {e}")
        
        # If repairs were made, rebuild the IMG
        if repairs_made > 0:
            try:
                return img_file.rebuild()
            except Exception as e:
                print(f"Error rebuilding IMG during repair: {e}")
                return False
        
        return repairs_made > 0
    
    def _repair_duplicate_names(self, img_file: IMGFile):
        """Repair duplicate entry names"""
        seen_names = set()
        
        for entry in img_file.entries:
            original_name = entry.name
            base_name = os.path.splitext(original_name)[0]
            extension = os.path.splitext(original_name)[1]
            
            counter = 1
            while entry.name.upper() in seen_names:
                entry.name = f"{base_name}_{counter:02d}{extension}"
                counter += 1
            
            seen_names.add(entry.name.upper())
            
            if entry.name != original_name:
                img_file.is_modified = True


class IMGRepairTool:
    """Advanced IMG repair utilities"""
    
    @staticmethod
    def attempt_recovery(file_path: str) -> Optional[IMGFile]:
        """Attempt to recover corrupted IMG file"""
        try:
            # Try different version parsers
            for version in [IMGVersion.VERSION_2, IMGVersion.VERSION_1, IMGVersion.FASTMAN92]:
                try:
                    img = IMGFile(file_path)
                    img.version = version
                    if img.open():
                        return img
                except:
                    continue
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def rebuild_from_fragments(file_path: str, output_path: str) -> bool:
        """Attempt to rebuild IMG from file fragments"""
        try:
            # This would implement advanced recovery techniques
            # For now, just return False as it's a complex operation
            return False
        except Exception:
            return False
    
    @staticmethod
    def extract_recoverable_files(file_path: str, output_dir: str) -> int:
        """Extract files that can be recovered from corrupted IMG"""
        recovered_count = 0
        
        try:
            with open(file_path, 'rb') as f:
                # Scan for file signatures
                signatures = {
                    b'RIFF': 'wav',
                    b'\x10\x00\x00\x00': 'dff',
                    b'\x16\x00\x00\x00': 'txd',
                    b'COLL': 'col'
                }
                
                f.seek(0)
                data = f.read()
                
                for i, byte in enumerate(data[:-4]):
                    for sig, ext in signatures.items():
                        if data[i:i+len(sig)] == sig:
                            # Found potential file
                            try:
                                # Extract reasonable amount of data
                                file_data = data[i:i+1024*1024]  # 1MB max
                                output_file = os.path.join(output_dir, f"recovered_{recovered_count:04d}.{ext}")
                                
                                with open(output_file, 'wb') as out_f:
                                    out_f.write(file_data)
                                
                                recovered_count += 1
                                
                            except:
                                continue
            
            return recovered_count
            
        except Exception:
            return 0


# Example usage and testing
if __name__ == "__main__":
    # Test validation system
    print("Testing IMG Validator...")
    
    # Test with a sample IMG file
    test_img_path = "test.img"
    if os.path.exists(test_img_path):
        img = IMGFile(test_img_path)
        if img.open():
            # Basic validation
            report = IMGValidator.validate_img_file(img, deep_scan=False)
            print(f"✓ Basic validation: {report.get_summary()}")
            
            # Deep validation
            deep_report = IMGValidator.validate_img_file(img, deep_scan=True)
            print(f"✓ Deep validation: {deep_report.get_summary()}")
            
            # Print issues
            for issue in deep_report.issues:
                print(f"  {issue.severity.value.upper()}: {issue.message}")
            
            # Attempt repair if needed
            if deep_report.get_auto_repairable_count() > 0:
                validator = IMGValidator()
                if validator.repair_img(img, deep_report):
                    print("✓ Repairs applied successfully")
                else:
                    print("✗ Failed to apply repairs")
            
            img.close()
    else:
        print("No test IMG file found")
    
    print("IMG Validator tests completed!")
                
