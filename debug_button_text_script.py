# this belongs in root/debug_button_text.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - Debug Button Text Colors
Check if themes are loading button_text_color properly
"""

import json
import os
from pathlib import Path


def debug_themes():
    """Debug theme loading and button text colors"""
    print("🔍 DEBUG: Button Text Color Loading")
    print("=" * 50)
    
    themes_dir = Path("themes")
    if not themes_dir.exists():
        print("❌ themes/ directory not found")
        return
    
    # Check all theme files
    for theme_file in themes_dir.glob("*.json"):
        print(f"\n📁 {theme_file.name}")
        
        try:
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)
            
            colors = theme_data.get("colors", {})
            
            # Check for button text colors
            button_text = colors.get("button_text_color")
            button_hover = colors.get("button_text_hover") 
            button_pressed = colors.get("button_text_pressed")
            
            if button_text:
                print(f"  ✅ button_text_color: {button_text}")
                print(f"  ✅ button_text_hover: {button_hover}")
                print(f"  ✅ button_text_pressed: {button_pressed}")
            else:
                print(f"  ❌ Missing button_text_color")
                
        except Exception as e:
            print(f"  ❌ Error reading: {e}")


def debug_app_settings():
    """Debug App Settings theme loading"""
    print("\n🔍 DEBUG: App Settings Theme Loading")
    print("=" * 50)
    
    try:
        # Import your app settings
        from app_settings_system import AppSettings
        
        settings = AppSettings()
        current_theme = settings.current_settings.get("theme", "unknown")
        
        print(f"Current theme setting: {current_theme}")
        
        # Get theme data
        theme = settings.get_theme()
        theme_name = theme.get("name", "Unknown")
        colors = theme.get("colors", {})
        
        print(f"Loaded theme name: {theme_name}")
        
        # Check button text colors
        button_text = colors.get("button_text_color")
        button_hover = colors.get("button_text_hover")
        button_pressed = colors.get("button_text_pressed")
        
        print(f"button_text_color: {button_text}")
        print(f"button_text_hover: {button_hover}")
        print(f"button_text_pressed: {button_pressed}")
        
        if button_text:
            print("✅ App Settings is reading button text colors correctly")
        else:
            print("❌ App Settings is NOT reading button text colors")
            
            # Check what colors ARE available
            print("\nAvailable colors in theme:")
            for key in sorted(colors.keys()):
                print(f"  {key}: {colors[key]}")
        
        # Test stylesheet generation
        print(f"\n🎨 Testing stylesheet generation...")
        stylesheet = settings.get_stylesheet()
        
        # Check if button text color appears in stylesheet
        if button_text and button_text in stylesheet:
            print(f"✅ Button text color {button_text} found in stylesheet")
        else:
            print(f"❌ Button text color {button_text} NOT found in stylesheet")
            
            # Show relevant parts of stylesheet
            lines = stylesheet.split('\n')
            button_lines = [line for line in lines if 'QPushButton' in line and 'color:' in line]
            print("\nButton color lines in stylesheet:")
            for line in button_lines:
                print(f"  {line.strip()}")
        
    except Exception as e:
        print(f"❌ Error testing App Settings: {e}")
        import traceback
        traceback.print_exc()


def debug_settings_file():
    """Debug the settings file"""
    print("\n🔍 DEBUG: Settings File")
    print("=" * 50)
    
    settings_file = "imgfactory.settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        current_theme = settings.get("theme", "not found")
        print(f"Current theme in settings: {current_theme}")
    else:
        print(f"❌ Settings file not found: {settings_file}")


def main():
    """Run all debug checks"""
    debug_themes()
    debug_app_settings()
    debug_settings_file()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. If button_text_color is missing from JSON → Run update_theme_jsons.py")
    print("2. If App Settings not reading colors → Check get_theme() method")
    print("3. If colors not in stylesheet → Check get_stylesheet() method")
    print("4. Try restarting the app completely")
    print("5. Try switching to a different theme and back")


if __name__ == "__main__":
    main()
