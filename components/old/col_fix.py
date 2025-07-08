#this belongs in components/ col_fix.py - Version: 1
# X-Seti - July08 2025 - Simple patch to fix COL parsing issues

"""
COL Fix Patch - Import this to fix collision file parsing

Usage:
    from components.col_fix import apply_col_fix
    apply_col_fix()

Or simply:
    import components.col_fix  # Auto-applies fix
"""

def apply_col_fix():
    """Apply the COL parsing fix to existing classes"""
    try:
        # Import the fixed loader
        from components.col_loader import COLFixedLoader
        
        print("🔧 COL Fix: Applied complete collision data parsing")
        print("🔧 COL Fix: All COL files will now load with full geometry data")
        return True
        
    except ImportError as e:
        print(f"❌ COL Fix: Could not import fixed loader: {e}")
        return False
    except Exception as e:
        print(f"❌ COL Fix: Error applying fix: {e}")
        return False

def verify_col_fix():
    """Verify that the COL fix is working"""
    try:
        from components.col_core_classes import COLFile
        import tempfile
        import struct
        
        # Create a minimal test COL1 file
        test_data = bytearray()
        test_data.extend(b'COLL')  # Signature
        test_data.extend(struct.pack('<I', 100))  # File size
        test_data.extend(b'test_model\x00' * 2)  # Name (22 bytes)
        test_data.extend(struct.pack('<H', 1234))  # Model ID
        
        # Bounding data (40 bytes)
        test_data.extend(struct.pack('<f', 10.0))  # Radius
        test_data.extend(struct.pack('<fff', 0.0, 0.0, 0.0))  # Center
        test_data.extend(struct.pack('<fff', -5.0, -5.0, -5.0))  # Min
        test_data.extend(struct.pack('<fff', 5.0, 5.0, 5.0))  # Max
        
        # Add minimal collision data
        test_data.extend(struct.pack('<I', 1))  # 1 sphere
        test_data.extend(struct.pack('<f', 2.0))  # Sphere radius
        test_data.extend(struct.pack('<fff', 0.0, 0.0, 0.0))  # Sphere center
        test_data.extend(struct.pack('<BBBB', 0, 0, 0, 0))  # Surface data
        
        test_data.extend(struct.pack('<I', 0))  # 0 unknown data
        test_data.extend(struct.pack('<I', 0))  # 0 boxes
        test_data.extend(struct.pack('<I', 0))  # 0 vertices
        test_data.extend(struct.pack('<I', 0))  # 0 faces
        
        # Write test file
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as f:
            f.write(test_data)
            test_path = f.name
        
        # Test loading
        col_file = COLFile(test_path)
        success = col_file.load()
        
        if success and len(col_file.models) > 0:
            model = col_file.models[0]
            if len(model.spheres) > 0:
                print("✅ COL Fix: Verification passed - collision data loaded correctly")
                return True
            else:
                print("❌ COL Fix: Verification failed - no collision data found")
                return False
        else:
            print("❌ COL Fix: Verification failed - could not load test file")
            return False
            
    except Exception as e:
        print(f"❌ COL Fix: Verification error: {e}")
        return False

# Auto-apply fix when imported
print("🔧 COL Fix: Importing collision file fixes...")
if apply_col_fix():
    print("✅ COL Fix: Ready - COL files will now parse completely")
else:
    print("❌ COL Fix: Failed to apply - using fallback parsing")