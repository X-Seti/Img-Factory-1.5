# Amiga MUI Demo Application

This application demonstrates advanced MUI (Magic User Interface) features implemented in PyQt, showcasing the key enhancements requested:

## Key Features Implemented

### 1. New Tabs with Various Gadget Types
- **Basic Gadgets Tab**: String, Numeric, Double Numeric, Color Field, List, Checkbox, Radio Button, Cycle gadgets
- **Advanced Gadgets Tab**: Scale/Slider, Knob, Gauge, Level Meter, Palette, Popstring gadgets
- **Visual Effects Tab**: Buttons with various visual styles (normal, raised, sunken, 3D)
- **Image Backgrounds Tab**: Support for panel_bg, bg_primary, bg_secondary, shaded, stretched, tiled backgrounds
- **Transparency & Components Tab**: Transparency controls and UI management components

### 2. Advanced Gadgets Support
The following gadget types are implemented with proper Amiga MUI styling:

- **String**: QLineEdit for text input
- **Gauge**: QProgressBar for progress indication
- **Scale/Slider**: Custom MUISlider with horizontal/vertical orientation
- **Colorfield**: QPushButton with color selection
- **List**: QListWidget for item selection
- **Numeric**: QSpinBox and QDoubleSpinBox for integer and decimal input
- **Knob**: Custom MUIKnob with circular control
- **Levelmeter**: Custom MUILevelMeter with multiple bars
- **Slider**: Custom MUISlider with visual styling
- **Radio**: QRadioButton for exclusive selection
- **Cycle**: QComboBox for dropdown selection
- **Palette**: Custom MUIPaletteWidget with color grid
- **Popstring**: QComboBox for string selection

### 3. Transparency Features
- Configurable opacity levels (0.0-1.0) for titlebar and panels
- Menu option to toggle transparency
- Visual feedback when transparency changes

### 4. Shadow Effects
- Adjustable shadow depth settings for buttons and panels
- Menu option to toggle shadows
- Visual feedback when shadow effects change

### 5. UI Management Components
- **Group**: QGroupBox for organizing related controls
- **Scrollbar**: QSlider for scrolling functionality
- **Listview**: QListView for list display
- **Register**: Tab widget metaphor for tabbed interface
- **Virtgroup**: Not specifically implemented but available via layouts
- **Scrollgroup**: Not specifically implemented but available via scroll areas
- **Popobject**: Available through various popup mechanisms

### 6. Image Background Support
- Support for different background types:
  - `panel_bg`: Panel background styling
  - `bg_primary`: Primary background styling
  - `bg_secondary`: Secondary background styling
  - `shaded`: Shaded gradient background
  - `stretched`: Stretched gradient background
  - `tiled`: Tiled pattern background

## File Structure
- `apps/components/Img_Factory/mui_demo.py`: Main MUI application with all components
- `run_mui_demo.py`: Launcher script to run the application
- `test_mui_components.py`: Test suite to verify functionality

## Running the Application
To run the MUI demo application:

```bash
python run_mui_demo.py
```

Or with specific Qt platform:

```bash
QT_QPA_PLATFORM=offscreen python run_mui_demo.py
```

## Technical Implementation Details

### Custom MUI Widgets
1. **MUISlider**: Custom slider with track and knob visualization
2. **MUIKnob**: Circular knob control with indicator line
3. **MUILevelMeter**: Audio level meter with multiple colored bars
4. **MUIPaletteWidget**: Color palette grid with selection
5. **MUITabWidget**: Tab widget with transparency and shadow support

### Styling and Theming
- Linear and radial gradients for authentic MUI appearance
- Custom CSS styling for buttons and panels
- Transparency support via RGBA colors
- Visual effects for different widget states (normal, pressed, hover)

### Event Handling
- Mouse event handling for custom widgets
- Value change signals for interactive controls
- Menu and toolbar integration

## Testing
The application includes a comprehensive test suite that verifies:
- All components can be imported successfully
- All components can be instantiated without errors
- Basic functionality of each component type
- Value setting and getting operations

Run tests with:
```bash
QT_QPA_PLATFORM=offscreen python test_mui_components.py
```

## Integration with Existing System
The MUI demo is integrated into the existing Img_Factory component structure and can be launched independently or potentially integrated into the main application as needed.

## Amiga MUI Design Principles
The implementation follows Amiga MUI design principles:
- Consistent visual styling across all components
- Intuitive user interaction patterns
- Visual feedback for user actions
- Responsive and interactive controls
- Proper grouping and organization of related functions