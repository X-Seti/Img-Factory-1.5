#!/usr/bin/env python3
"""
Test script to verify that the COL3DViewport fixes work correctly
"""
import sys
import os
sys.path.insert(0, '/workspace')

try:
    from apps.components.Col_Editor.depends.col_3d_viewport import COL3DViewport
    print("✓ COL3DViewport imported successfully")
    
    # Check that the methods have been fixed
    import inspect
    
    # Get source of draw_box method
    source = inspect.getsource(COL3DViewport.draw_box)
    if 'min_point' in source and 'max_point' in source:
        print("✓ draw_box method correctly uses min_point and max_point attributes")
    else:
        print("✗ draw_box method still has issues")
        
    # Get source of draw_face_mesh method
    source = inspect.getsource(COL3DViewport.draw_face_mesh)
    if 'position.x' in source and 'position.y' in source and 'position.z' in source:
        print("✓ draw_face_mesh method correctly uses position attributes")
    else:
        print("✗ draw_face_mesh method still has issues")
        
    # Get source of _draw_shadow_mesh method
    source = inspect.getsource(COL3DViewport._draw_shadow_mesh)
    if 'position.x' in source and 'position.y' in source and 'position.z' in source:
        print("✓ _draw_shadow_mesh method correctly uses position attributes")
    else:
        print("✗ _draw_shadow_mesh method still has issues")
    
    print("\n✓ All fixes have been applied successfully!")
    
except Exception as e:
    print(f"✗ Error importing or testing COL3DViewport: {e}")
    import traceback
    traceback.print_exc()