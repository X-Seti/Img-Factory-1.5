#!/bin/bash
# Demo script to run the Amiga MUI application

echo "Amiga MUI Demo Application"
echo "=========================="

# Check if PyQt6 is installed
if python -c "import PyQt6" &> /dev/null; then
    echo "✓ PyQt6 is installed"
else
    echo "✗ PyQt6 is not installed. Please install it with: pip install PyQt6"
    exit 1
fi

echo ""
echo "To run the MUI demo application, use one of the following commands:"
echo ""
echo "1. Standard run (requires display):"
echo "   python run_mui_demo.py"
echo ""
echo "2. Headless run (for server environments):"
echo "   QT_QPA_PLATFORM=offscreen python run_mui_demo.py"
echo ""
echo "3. Run with virtual framebuffer:"
echo "   xvfb-run -a python run_mui_demo.py"
echo ""
echo "4. Run the test suite:"
echo "   QT_QPA_PLATFORM=offscreen python test_mui_components.py"
echo ""

echo "Documentation files:"
echo "- MUI_DEMO_README.md: Detailed documentation about the MUI implementation"
echo "- MUI_IMPLEMENTATION_SUMMARY.md: Summary of implemented features"
echo ""

echo "Key features demonstrated:"
echo "- Multiple tabs with various gadget types"
echo "- String, Gauge, Scale, Colorfield, List, Numeric, Knob, Levelmeter, Slider, Radio, Cycle, Palette, Popstring gadgets"
echo "- Transparency controls (0.0-1.0 opacity)"
echo "- Shadow effects with adjustable depth"
echo "- UI Management Components (Group, Scrollbar, Listview, Register, etc.)"
echo "- Image background support (panel_bg, bg_primary, bg_secondary, shaded, stretched, tiled)"
echo ""