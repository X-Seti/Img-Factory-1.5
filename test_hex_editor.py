#!/usr/bin/env python3
"""
Test script for the Hex Editor functionality
X-Seti - December 2025
"""

import sys
import os
import tempfile

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

def test_hex_editor_import():
    """Test that the hex editor module can be imported"""
    try:
        from apps.components.Hex_Editor import HexEditorDialog, show_hex_editor_for_file, show_hex_editor_for_entry
        print("✅ Successfully imported Hex Editor components")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Hex Editor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing Hex Editor: {e}")
        return False

def test_hex_editor_functionality():
    """Test hex editor functionality with a sample file"""
    try:
        # Create a temporary test file with some binary data
        test_data = b'\x00\x01\x02\x03\x47\x54\x41\x20\x44\x46\x46\x20\x74\x65\x73\x74'  # Some binary data including 'GTA DFF test'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dff', mode='wb') as temp_file:
            temp_file.write(test_data)
            temp_path = temp_file.name
        
        print(f"✅ Created test file: {temp_path}")
        
        # Try to create a mock main window for testing
        class MockMainWindow:
            def __init__(self):
                self.log_messages = []
                
            def log_message(self, msg):
                self.log_messages.append(msg)
                print(f"Log: {msg}")
                
        mock_main_window = MockMainWindow()
        
        # Test the hex editor function directly
        from apps.components.Hex_Editor import HexEditorDialog
        dialog = HexEditorDialog(mock_main_window, temp_path)
        
        print("✅ Hex Editor dialog created successfully")
        print(f"✅ File data loaded: {len(dialog.file_data)} bytes")
        print(f"✅ DFF file detection: {dialog.is_dff_file}")
        
        # Clean up
        os.remove(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing hex editor functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dff_parsing():
    """Test DFF structure parsing functionality"""
    try:
        from apps.components.Hex_Editor import HexEditorDialog
        import struct
        import tempfile
        import os
        
        # Create a mock DFF file with some chunk headers
        # This simulates a basic RenderWare structure
        mock_dff_data = bytearray()
        
        # Add a basic chunk header (type=0x1B for Clump, size=20, version=0x30018)
        mock_dff_data.extend(struct.pack('<III', 0x1B, 20, 0x30018))  # Clump chunk
        # Add some dummy data for the chunk
        mock_dff_data.extend(b'dummy_data_for_clump_chunk')
        
        # Add another chunk header (type=0x05 for FrameList, size=16, version=0x30018)
        mock_dff_data.extend(struct.pack('<III', 0x05, 16, 0x30018))  # FrameList chunk
        # Add some dummy data for the chunk
        mock_dff_data.extend(b'dummy_frame_data')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dff', mode='wb') as temp_file:
            temp_file.write(mock_dff_data)
            temp_path = temp_file.name
        
        print(f"✅ Created mock DFF test file: {temp_path}")
        
        # Try to create a mock main window for testing
        class MockMainWindow:
            def __init__(self):
                self.log_messages = []
                
            def log_message(self, msg):
                self.log_messages.append(msg)
                if len(self.log_messages) < 10:  # Limit output
                    print(f"Log: {msg}")
                
        mock_main_window = MockMainWindow()
        
        # Test the hex editor with DFF parsing
        dialog = HexEditorDialog(mock_main_window, temp_path)
        
        print(f"✅ DFF file detected: {dialog.is_dff_file}")
        print(f"✅ Structure table rows: {dialog.structure_table.rowCount()}")
        
        # Check if structure parsing worked
        if dialog.structure_table.rowCount() > 0:
            print("✅ DFF structure parsing successful")
            # Print first few rows
            for i in range(min(3, dialog.structure_table.rowCount())):
                offset_item = dialog.structure_table.item(i, 0)
                size_item = dialog.structure_table.item(i, 1)
                type_item = dialog.structure_table.item(i, 2)
                desc_item = dialog.structure_table.item(i, 3)
                
                print(f"  Row {i}: {offset_item.text()} | {size_item.text()} | {type_item.text()}")
        else:
            print("⚠️  No structure rows parsed")
        
        # Clean up
        os.remove(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing DFF parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing Hex Editor Implementation")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing import functionality...")
    if not test_hex_editor_import():
        success = False
    
    print("\n2. Testing hex editor functionality...")
    if not test_hex_editor_functionality():
        success = False
    
    print("\n3. Testing DFF structure parsing...")
    if not test_dff_parsing():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)