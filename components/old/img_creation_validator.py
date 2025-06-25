#!/usr/bin/env python3
"""
IMG Factory Qt6 - Advanced Validation System
Comprehensive validation for IMG creation with smart suggestions and fixes
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from new_img_creator import GameType, IMGTemplate

class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: ValidationLevel
    code: str
    message: str
    suggestion: Optional[str] = None
    auto_fix_available: bool = False
    category: str = "general"

@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    issues: List[ValidationIssue]
    warnings_count: int
    errors_count: int
    can_proceed: bool
    auto_fixes: List[str]

class IMGCreationValidator:
    """Advanced validator for IMG creation parameters"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.platform_specific_rules = self._load_platform_rules()
        self.game_specific_rules = self._load_game_rules()
    
    def validate_creation_params(self, **params) -> ValidationResult:
        """Perform comprehensive validation of creation parameters"""
        issues = []
        auto_fixes = []
        
        # Basic parameter validation
        issues.extend(self._validate_basic_params(params))
        
        # Filename validation
        filename_issues, filename_fixes = self._validate_filename(params.get('filename', ''))
        issues.extend(filename_issues)
        auto_fixes.extend(filename_fixes)
        
        # Directory validation
        issues.extend(self._validate_output_directory(params.get('output_dir', '')))
        
        # Size validation
        issues.extend(self._validate_size_settings(params))
        
        # Game-specific validation
        issues.extend(self._validate_game_compatibility(params))
        
        # Platform-specific validation
        issues.extend(self._validate_platform_compatibility(params))
        
        # Advanced validation
        issues.extend(self._validate_advanced_settings(params))
        
        # Resource validation
        issues.extend(self._validate_system_resources(params))
        
        # Calculate summary
        warnings_count = sum(1 for issue in issues if issue.level == ValidationLevel.WARNING)
        errors_count = sum(1 for issue in issues if issue.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL])
        
        is_valid = errors_count == 0
        can_proceed = errors_count == 0  # Can proceed if no errors (warnings are OK)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings_count=warnings_count,
            errors_count=errors_count,
            can_proceed=can_proceed,
            auto_fixes=auto_fixes
        )
    
    def _validate_basic_params(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate basic required parameters"""
        issues = []
        
        # Required parameters
        required_params = ['filename', 'output_dir', 'game_type']
        for param in required_params:
            if not params.get(param):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code=f"MISSING_{param.upper()}",
                    message=f"Required parameter '{param}' is missing",
                    category="basic"
                ))
        
        # Game type validation
        game_type = params.get('game_type')
        if game_type and not isinstance(game_type, GameType):
            if hasattr(GameType, game_type.upper()):
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    code="GAME_TYPE_CONVERSION",
                    message=f"Game type will be converted to {game_type.upper()}",
                    auto_fix_available=True,
                    category="basic"
                ))
            else:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code="INVALID_GAME_TYPE",
                    message=f"Invalid game type: {game_type}",
                    suggestion="Choose from: GTA_III, GTA_VC, GTA_SA, GTA_IV, BULLY",
                    category="basic"
                ))
        
        return issues
    
    def _validate_filename(self, filename: str) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate filename with auto-fix suggestions"""
        issues = []
        auto_fixes = []
        
        if not filename:
            return [ValidationIssue(
                level=ValidationLevel.ERROR,
                code="EMPTY_FILENAME",
                message="Filename cannot be empty",
                category="filename"
            )], []
        
        # Length validation
        if len(filename) > 100:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="FILENAME_TOO_LONG",
                message=f"Filename is very long ({len(filename)} characters)",
                suggestion="Consider using a shorter, more descriptive name",
                category="filename"
            ))
        elif len(filename) < 3:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="FILENAME_TOO_SHORT",
                message="Filename is very short",
                suggestion="Consider using a more descriptive name",
                category="filename"
            ))
        
        # Invalid characters
        invalid_chars = r'<>:"/\\|?*'
        found_invalid = [char for char in invalid_chars if char in filename]
        if found_invalid:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="INVALID_FILENAME_CHARS",
                message=f"Filename contains invalid characters: {', '.join(found_invalid)}",
                suggestion="Remove or replace invalid characters with underscores",
                auto_fix_available=True,
                category="filename"
            ))
            auto_fixes.append(f"Replace invalid characters in filename")
        
        # Reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        if filename.upper() in reserved_names:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="RESERVED_FILENAME",
                message=f"'{filename}' is a reserved filename on Windows",
                suggestion="Choose a different filename",
                category="filename"
            ))
        
        # Naming conventions
        if filename.lower() in ['img', 'archive', 'file', 'new']:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="GENERIC_FILENAME",
                message="Filename is very generic",
                suggestion="Use a more descriptive name (e.g., 'custom_vehicles', 'my_mod')",
                category="filename"
            ))
        
        # Special character suggestions
        if ' ' in filename:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="SPACES_IN_FILENAME",
                message="Filename contains spaces",
                suggestion="Consider using underscores instead of spaces for better compatibility",
                auto_fix_available=True,
                category="filename"
            ))
            auto_fixes.append("Replace spaces with underscores")
        
        # Case sensitivity warning
        if filename != filename.lower():
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="MIXED_CASE_FILENAME",
                message="Filename uses mixed case",
                suggestion="Consider using lowercase for better compatibility across platforms",
                auto_fix_available=True,
                category="filename"
            ))
        
        return issues, auto_fixes
    
    def _validate_output_directory(self, output_dir: str) -> List[ValidationIssue]:
        """Validate output directory"""
        issues = []
        
        if not output_dir:
            return [ValidationIssue(
                level=ValidationLevel.ERROR,
                code="NO_OUTPUT_DIR",
                message="Output directory not specified",
                category="directory"
            )]
        
        # Existence check
        if not os.path.exists(output_dir):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="DIR_NOT_EXISTS",
                message=f"Output directory does not exist: {output_dir}",
                suggestion="Create the directory or choose an existing one",
                category="directory"
            ))
            return issues  # Can't check further if directory doesn't exist
        
        # Permission checks
        if not os.access(output_dir, os.W_OK):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="NO_WRITE_PERMISSION",
                message="No write permission to output directory",
                suggestion="Choose a directory you have write access to",
                category="directory"
            ))
        
        # Disk space check
        try:
            free_space = shutil.disk_usage(output_dir).free
            free_space_gb = free_space / (1024**3)
            
            if free_space_gb < 0.1:  # Less than 100MB
                issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    code="INSUFFICIENT_DISK_SPACE",
                    message=f"Very low disk space: {free_space_gb:.1f} GB available",
                    suggestion="Free up disk space before creating IMG files",
                    category="directory"
                ))
            elif free_space_gb < 1.0:  # Less than 1GB
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="LOW_DISK_SPACE",
                    message=f"Low disk space: {free_space_gb:.1f} GB available",
                    suggestion="Consider freeing up more space for large IMG files",
                    category="directory"
                ))
        except Exception:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="DISK_SPACE_CHECK_FAILED",
                message="Could not check available disk space",
                category="directory"
            ))
        
        # Path length check (Windows limitation)
        if len(output_dir) > 200:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="LONG_PATH",
                message="Output path is very long",
                suggestion="Use a shorter path to avoid potential issues",
                category="directory"
            ))
        
        # Special directory warnings
        system_dirs = ['C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', '/System', '/usr']
        if any(output_dir.startswith(sys_dir) for sys_dir in system_dirs):
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="SYSTEM_DIRECTORY",
                message="Creating files in system directory",
                suggestion="Consider using a user directory instead",
                category="directory"
            ))
        
        return issues
    
    def _validate_size_settings(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate size-related settings"""
        issues = []
        
        initial_size_mb = params.get('initial_size_mb', 0)
        game_type = params.get('game_type')
        
        if initial_size_mb <= 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="INVALID_SIZE",
                message="Initial size must be greater than 0",
                category="size"
            ))
            return issues
        
        # Size recommendations based on game type
        if game_type and hasattr(GameType, game_type.upper() if isinstance(game_type, str) else game_type.name):
            game_enum = GameType[game_type.upper()] if isinstance(game_type, str) else game_type
            template = IMGTemplate.TEMPLATES.get(game_enum)
            
            if template:
                recommended_size = template['default_size_mb']
                
                if initial_size_mb < recommended_size * 0.5:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        code="SIZE_BELOW_RECOMMENDED",
                        message=f"Size ({initial_size_mb} MB) is below recommended for {game_enum.name} ({recommended_size} MB)",
                        suggestion=f"Consider using at least {recommended_size} MB",
                        category="size"
                    ))
                elif initial_size_mb > recommended_size * 3:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        code="SIZE_ABOVE_RECOMMENDED",
                        message=f"Size ({initial_size_mb} MB) is much larger than typical for {game_enum.name}",
                        suggestion="Large files take longer to create and may affect game performance",
                        category="size"
                    ))
        
        # General size warnings
        if initial_size_mb > 1000:  # 1GB
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="VERY_LARGE_SIZE",
                message=f"Very large IMG size: {initial_size_mb} MB",
                suggestion="Large IMG files may cause performance issues in older games",
                category="size"
            ))
        elif initial_size_mb < 5:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="VERY_SMALL_SIZE",
                message=f"Very small IMG size: {initial_size_mb} MB",
                suggestion="May not be sufficient for substantial mods",
                category="size"
            ))
        
        return issues
    
    def _validate_game_compatibility(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate game-specific compatibility"""
        issues = []
        
        game_type = params.get('game_type')
        if not game_type:
            return issues
        
        # Convert string to enum if needed
        if isinstance(game_type, str):
            try:
                game_type = GameType[game_type.upper()]
            except KeyError:
                return [ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code="INVALID_GAME_TYPE",
                    message=f"Unknown game type: {game_type}",
                    category="compatibility"
                )]
        
        template = IMGTemplate.TEMPLATES.get(game_type)
        if not template:
            return issues
        
        # Compression compatibility
        compression_enabled = params.get('compression_enabled', False)
        if compression_enabled and not template['supports_compression']:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="COMPRESSION_NOT_SUPPORTED",
                message=f"Compression is not supported for {game_type.name}",
                suggestion="Disable compression for this game type",
                auto_fix_available=True,
                category="compatibility"
            ))
        
        # Encryption compatibility
        encryption_enabled = params.get('encryption_enabled', False)
        if encryption_enabled and not template['supports_encryption']:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code="ENCRYPTION_NOT_SUPPORTED",
                message=f"Encryption is not supported for {game_type.name}",
                suggestion="Disable encryption for this game type",
                auto_fix_available=True,
                category="compatibility"
            ))
        
        # Size limits
        initial_size_mb = params.get('initial_size_mb', 0)
        max_size_mb = template.get('max_size_mb', float('inf'))
        if initial_size_mb > max_size_mb:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code="SIZE_EXCEEDS_LIMIT",
                message=f"Size ({initial_size_mb} MB) exceeds maximum for {game_type.name} ({max_size_mb} MB)",
                suggestion=f"Reduce size to {max_size_mb} MB or less",
                category="compatibility"
            ))
        
        return issues
    
    def _validate_platform_compatibility(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate platform-specific compatibility"""
        issues = []
        
        platform = params.get('platform', 'PC')
        game_type = params.get('game_type')
        
        # Platform-specific validations
        if platform == 'PlayStation 2':
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="PS2_ENDIANNESS",
                message="PS2 platform uses different byte order",
                suggestion="Ensure target files are compatible with PS2 format",
                category="platform"
            ))
            
            # PS2 size limitations
            initial_size_mb = params.get('initial_size_mb', 0)
            if initial_size_mb > 100:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="PS2_SIZE_WARNING",
                    message="Large IMG files may cause issues on PS2",
                    suggestion="Consider keeping IMG files under 100MB for PS2",
                    category="platform"
                ))
        
        elif platform == 'Xbox':
            compression_enabled = params.get('compression_enabled', False)
            if compression_enabled:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    code="XBOX_COMPRESSION",
                    message="Xbox platform supports LZO compression",
                    suggestion="LZO compression will be used for Xbox platform",
                    category="platform"
                ))
        
        elif platform == 'Mobile':
            initial_size_mb = params.get('initial_size_mb', 0)
            if initial_size_mb > 50:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="MOBILE_SIZE_WARNING",
                    message="Large IMG files may impact mobile performance",
                    suggestion="Consider smaller IMG files for mobile platforms",
                    category="platform"
                ))
        
        return issues
    
    def _validate_advanced_settings(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate advanced settings combinations"""
        issues = []
        
        compression_enabled = params.get('compression_enabled', False)
        encryption_enabled = params.get('encryption_enabled', False)
        
        # Compression + Encryption interaction
        if compression_enabled and encryption_enabled:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="COMPRESSION_ENCRYPTION_COMBO",
                message="Both compression and encryption are enabled",
                suggestion="Files will be compressed first, then encrypted",
                category="advanced"
            ))
        
        # Directory structure validation
        create_structure = params.get('create_structure', False)
        output_dir = params.get('output_dir', '')
        
        if create_structure and output_dir:
            # Check if directory is empty
            try:
                if os.path.exists(output_dir) and os.listdir(output_dir):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        code="NON_EMPTY_DIRECTORY",
                        message="Output directory is not empty",
                        suggestion="Directory structure will be created alongside existing files",
                        category="advanced"
                    ))
            except Exception:
                pass
        
        return issues
    
    def _validate_system_resources(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate system resource requirements"""
        issues = []
        
        initial_size_mb = params.get('initial_size_mb', 0)
        
        # Memory usage estimation
        estimated_memory_mb = initial_size_mb * 0.1  # Rough estimate
        
        try:
            import psutil
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            
            if estimated_memory_mb > available_memory_gb * 1024 * 0.5:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="HIGH_MEMORY_USAGE",
                    message="IMG creation may use significant memory",
                    suggestion="Close other applications to free up memory",
                    category="resources"
                ))
        except ImportError:
            # psutil not available, skip memory check
            pass
        
        # Performance warnings for large files
        if initial_size_mb > 500:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                code="LARGE_FILE_PERFORMANCE",
                message="Large IMG files may take longer to create",
                suggestion="Consider creating smaller IMG files for better performance",
                category="resources"
            ))
        
        return issues
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration"""
        return {
            'max_filename_length': 100,
            'min_filename_length': 3,
            'max_size_mb': 2000,
            'min_size_mb': 1,
            'reserved_names': ['CON', 'PRN', 'AUX', 'NUL'],
            'invalid_chars': r'<>:"/\\|?*'
        }
    
    def _load_platform_rules(self) -> Dict[str, Any]:
        """Load platform-specific validation rules"""
        return {
            'PC': {
                'max_path_length': 260,
                'max_size_mb': 2000
            },
            'PlayStation 2': {
                'max_size_mb': 100,
                'endianness': 'big'
            },
            'Xbox': {
                'max_size_mb': 200,
                'compression_type': 'lzo'
            },
            'Mobile': {
                'max_size_mb': 50,
                'performance_critical': True
            }
        }
    
    def _load_game_rules(self) -> Dict[str, Any]:
        """Load game-specific validation rules"""
        return {
            'GTA_III': {
                'max_entries': 65536,
                'supports_compression': False,
                'supports_encryption': False
            },
            'GTA_VC': {
                'max_entries': 65536,
                'supports_compression': False,
                'supports_encryption': False
            },
            'GTA_SA': {
                'max_entries': 2147483647,
                'supports_compression': True,
                'supports_encryption': False
            },
            'GTA_IV': {
                'max_entries': 2147483647,
                'supports_compression': True,
                'supports_encryption': True
            }
        }
    
    def apply_auto_fixes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic fixes to parameters"""
        fixed_params = params.copy()
        
        # Fix filename issues
        filename = fixed_params.get('filename', '')
        if filename:
            # Remove invalid characters
            invalid_chars = r'<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            # Replace spaces with underscores
            filename = filename.replace(' ', '_')
            
            # Convert to lowercase
            filename = filename.lower()
            
            fixed_params['filename'] = filename
        
        # Fix compatibility issues
        game_type = fixed_params.get('game_type')
        if game_type:
            template = IMGTemplate.TEMPLATES.get(game_type)
            if template:
                # Disable unsupported features
                if not template['supports_compression']:
                    fixed_params['compression_enabled'] = False
                
                if not template['supports_encryption']:
                    fixed_params['encryption_enabled'] = False
        
        return fixed_params
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """Generate a human-readable validation summary"""
        if result.errors_count == 0 and result.warnings_count == 0:
            return "✅ All validation checks passed successfully!"
        
        summary_lines = []
        
        if result.errors_count > 0:
            summary_lines.append(f"❌ {result.errors_count} error(s) found")
        
        if result.warnings_count > 0:
            summary_lines.append(f"⚠️ {result.warnings_count} warning(s) found")
        
        if result.can_proceed:
            summary_lines.append("✅ Can proceed with creation")
        else:
            summary_lines.append("❌ Cannot proceed - fix errors first")
        
        if result.auto_fixes:
            summary_lines.append(f"🔧 {len(result.auto_fixes)} auto-fix(es) available")
        
        return " | ".join(summary_lines)

# Integration with the main creator
def integrate_validation_with_creator():
    """Example of how to integrate validation with the IMG creator"""
    
    def enhanced_create_img_with_validation(**params):
        """Create IMG with comprehensive validation"""
        validator = IMGCreationValidator()
        
        # Validate parameters
        validation_result = validator.validate_creation_params(**params)
        
        if not validation_result.can_proceed:
            raise ValueError(f"Validation failed: {validator.get_validation_summary(validation_result)}")
        
        # Apply auto-fixes if available
        if validation_result.auto_fixes:
            params = validator.apply_auto_fixes(params)
            print(f"Applied {len(validation_result.auto_fixes)} auto-fixes")
        
        # Show warnings to user
        if validation_result.warnings_count > 0:
            print(f"Proceeding with {validation_result.warnings_count} warnings")
        
        # Proceed with creation
        # ... (actual IMG creation code here)
        
        return "img_created_successfully.img"
    
    return enhanced_create_img_with_validation