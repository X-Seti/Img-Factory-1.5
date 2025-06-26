# this belongs in root/debug_img_creation.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - Debug IMG Creation Issue
Quick test script to debug the IMG creation problem
"""

import sys
import os
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent / "components"))

print("🔍 IMG Creation Debug Test")
print("=" * 40)

# Test 1: Import debugging
print("\n1. Testing imports...")
try:
    from components.img_debug import img_debugger, debug_import_errors
    print("✓ Debug system imported")
    debug_import_errors()
except Exception as e:
    print(f"✗ Failed to import debug system: {e}")

# Test 2: Test IMG core classes
print("\n2. Testing IMG core classes...")
try:
    from components.img_core_classes import IMGFile, IMGVersion
    print("✓ IMG core classes imported")
    
    # Create test IMG file object
    img_file = IMGFile()
    img_debugger.inspect_object(img_file, "IMGFile")
    
    # Test if create_new method exists
    if hasattr(img_file, 'create_new'):
        print("✓ create_new method found")
        
        # Test method signature
        import inspect
        sig = inspect.signature(img_file.create_new)
        print(f"Method signature: create_new{sig}")
        
        # Test creating a file
        test_path = "test_debug.img"
        print(f"\n3. Testing create_new method with path: {test_path}")
        
        try:
            result = img_file.create_new(
                output_path=test_path,
                version=IMGVersion.VER2,
                initial_size_mb=1
            )
            print(f"create_new result: {result}")
            
            if result and os.path.exists(test_path):
                size = os.path.getsize(test_path)
                print(f"✓ File created successfully! Size: {size} bytes")
                # Clean up
                os.remove(test_path)
                print("✓ Test file cleaned up")
            else:
                print("✗ File was not created")
                
        except Exception as e:
            print(f"✗ Error during creation: {e}")
            img_debugger.trace_exception(e)
    else:
        print("✗ create_new method NOT found!")
        print("Available methods:")
        methods = [attr for attr in dir(img_file) if callable(getattr(img_file, attr)) and not attr.startswith('_')]
        for method in methods:
            print(f"  - {method}")

except Exception as e:
    print(f"✗ Failed to test IMG core: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test IMG creator dialog
print("\n4. Testing IMG creator dialog...")
try:
    from components.img_creator import NewIMGDialog
    print("✓ NewIMGDialog imported")
    
    # We can't fully test the dialog without Qt app, but we can check its structure
    print("Dialog class inspection would require Qt application")
    
except Exception as e:
    print(f"✗ Failed to import NewIMGDialog: {e}")

# Test 4: Check file permissions
print("\n5. Testing file system permissions...")
current_dir = Path.cwd()
print(f"Current directory: {current_dir}")
print(f"Directory writable: {os.access(current_dir, os.W_OK)}")

test_file = current_dir / "permission_test.tmp"
try:
    test_file.write_text("test")
    print("✓ Can create files in current directory")
    test_file.unlink()
except Exception as e:
    print(f"✗ Cannot create files: {e}")

print("\n" + "=" * 40)
print("Debug test complete!")
print("\nTo run this debug:")
print("1. cd to your IMG Factory directory")
print("2. python debug_img_creation.py")
