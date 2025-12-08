#!/usr/bin/env python3
"""
Test script to verify MUI components without GUI display
"""

import sys
import os
from pathlib import Path

# Add workspace to path
workspace_dir = Path(__file__).parent.resolve()
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

# Create minimal QApplication for testing
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

def test_imports():
    """Test that all MUI components can be imported without errors"""
    print("Testing MUI component imports...")
    
    try:
        # Import the main module
        from apps.components.Img_Factory.mui_demo import (
            MUISlider, MUIKnob, MUILevelMeter, 
            MUIPaletteWidget, MUITabWidget, MUIWindow
        )
        print("✓ All MUI components imported successfully")
        
        # Test creating instances
        print("\nTesting component instantiation...")
        
        # Test MUISlider
        slider = MUISlider()
        print("✓ MUISlider instantiated")
        
        # Test MUIKnob
        knob = MUIKnob()
        print("✓ MUIKnob instantiated")
        
        # Test MUILevelMeter
        level_meter = MUILevelMeter()
        print("✓ MUILevelMeter instantiated")
        
        # Test MUIPaletteWidget
        palette = MUIPaletteWidget()
        print("✓ MUIPaletteWidget instantiated")
        
        # Test MUITabWidget
        tab_widget = MUITabWidget()
        print("✓ MUITabWidget instantiated")
        
        print("\n✓ All MUI components instantiated successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_functionality():
    """Test basic functionality of MUI components"""
    print("\nTesting component functionality...")
    
    try:
        from apps.components.Img_Factory.mui_demo import (
            MUISlider, MUIKnob, MUILevelMeter, 
            MUIPaletteWidget
        )
        
        # Test MUISlider functionality
        slider = MUISlider(minimum=0, maximum=100, value=50)
        slider.setValue(75)
        assert slider.getValue() == 75, f"Expected 75, got {slider.getValue()}"
        print("✓ MUISlider functionality working")
        
        # Test MUIKnob functionality
        knob = MUIKnob(minimum=0.0, maximum=100.0, value=50.0)
        knob.setValue(75.5)
        assert abs(knob.getValue() - 75.5) < 0.01, f"Expected ~75.5, got {knob.getValue()}"
        print("✓ MUIKnob functionality working")
        
        # Test MUILevelMeter functionality
        meter = MUILevelMeter(num_bars=5)
        meter.setLevel(0, 0.8)
        levels = [0.2, 0.4, 0.6, 0.8, 1.0]
        meter.setAllLevels(levels)
        print("✓ MUILevelMeter functionality working")
        
        # Test MUIPaletteWidget functionality
        palette = MUIPaletteWidget()
        color = palette.getSelectedColor()
        assert color is not None, "Should return a color"
        print("✓ MUIPaletteWidget functionality working")
        
        print("\n✓ All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("MUI Components Test Suite")
    print("=" * 30)
    
    success1 = test_imports()
    success2 = test_functionality()
    
    if success1 and success2:
        print("\n✓ All tests passed! MUI components are working correctly.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)