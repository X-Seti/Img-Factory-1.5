#!/usr/bin/env python3
"""
Quick Fix Script for img_creator.py
Fixes the IMGVersion attribute name conflicts
"""

import os
import re
from pathlib import Path

def fix_img_creator():
    """Fix the img_creator.py file attribute conflicts"""
    
    # Find the file
    creator_file = Path("components/img_creator.py")
    
    if not creator_file.exists():
        print(f"❌ File not found: {creator_file}")
        return False
    
    print(f"🔧 Fixing {creator_file}...")
    
    # Read the current file
    try:
        with open(creator_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Create backup
    backup_file = creator_file.with_suffix('.py.backup')
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Apply fixes
    fixes = [
        ('IMGVersion.VERSION_1', 'IMGVersion.IMG_1'),
        ('IMGVersion.VERSION_2', 'IMGVersion.IMG_2'),
        ('IMGVersion.VERSION_3', 'IMGVersion.IMG_3'),
        ('IMGVersion.FASTMAN92', 'IMGVersion.IMG_FASTMAN92'),
        ('IMGVersion.STORIES', 'IMGVersion.IMG_STORIES'),
    ]
    
    fixed_content = content
    changes_made = 0
    
    for old_attr, new_attr in fixes:
        if old_attr in fixed_content:
            fixed_content = fixed_content.replace(old_attr, new_attr)
            changes_made += 1
            print(f"  ✓ Fixed: {old_attr} -> {new_attr}")
    
    # Additional fixes for Platform references if needed
    if 'Platform.PC' in fixed_content and 'class Platform' not in fixed_content:
        # Add Platform class if missing
        platform_class = '''
class Platform(Enum):
    """Platform enumeration"""
    PC = "PC"
    XBOX = "XBOX"
    PS2 = "PS2"
    PSP = "PSP"
    MOBILE = "Mobile"

'''
        # Insert after imports
        import_pattern = r'(from [^\n]+ import [^\n]+\n)'
        if re.search(import_pattern, fixed_content):
            fixed_content = re.sub(
                r'((?:from [^\n]+ import [^\n]+\n)+)',
                r'\1\n' + platform_class,
                fixed_content,
                count=1
            )
            changes_made += 1
            print("  ✓ Added Platform class")
    
    if changes_made == 0:
        print("  ℹ️  No changes needed")
        return True
    
    # Write the fixed file
    try:
        with open(creator_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Fixed file written with {changes_made} changes")
        return True
    except Exception as e:
        print(f"❌ Error writing fixed file: {e}")
        return False

def fix_core_classes():
    """Also check and fix img_core_classes.py if needed"""
    
    core_file = Path("components/img_core_classes.py") 
    
    if not core_file.exists():
        print(f"⚠️  Core classes file not found: {core_file}")
        return True  # Not critical
    
    try:
        with open(core_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it has the correct enum values
        if 'IMG_1 = 1' in content and 'IMG_2 = 2' in content:
            print("✅ Core classes file looks correct")
            return True
        else:
            print("⚠️  Core classes file may need updating")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not check core classes: {e}")
        return True

def main():
    """Main fix function"""
    print("🔧 IMG Factory 1.5 - Quick Fix for img_creator.py")
    print("=" * 50)
    
    # Check current directory
    if not Path("components").exists():
        print("❌ Components directory not found")
        print("Make sure you're running this from the IMG Factory root directory")
        return False
    
    # Fix img_creator.py
    if not fix_img_creator():
        return False
    
    # Check core classes
    fix_core_classes()
    
    print("\n✅ Fix completed!")
    print("\nNow try running:")
    print("  python imgfactory_demo.py")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Fix failed!")
        input("Press Enter to exit...")
    else:
        print("\n🎉 Fix successful!")
        
        # Ask if user wants to test
        try:
            test = input("\nTest the import now? (y/n): ").lower().strip()
            if test in ['y', 'yes']:
                print("\n🧪 Testing import...")
                try:
                    from components.img_creator import NewIMGDialog, GameType
                    print("✅ Import test successful!")
                except Exception as e:
                    print(f"❌ Import test failed: {e}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
