# this belongs in root/update_theme_jsons.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - Theme JSON Updater
Automatically adds button_text_color entries to all theme JSON files
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class ThemeUpdater:
    """Automatically update theme JSON files with button text colors"""
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.backup_dir = self.themes_dir / "backup"
        
        # Define which themes should have light vs dark text
        self.light_text_themes = {
            # Themes that need WHITE text (dark backgrounds)
            "lcars": "#ffffff",
            "deep_purple": "#ffffff", 
            "cyberpunk": "#ffffff",
            "matrix": "#ffffff",
            "dark_mode": "#ffffff",
            "midnight": "#ffffff",
            "space": "#ffffff"
        }
        
        self.dark_text_themes = {
            # Themes that need BLACK text (light backgrounds)  
            "lightgreen": "#000000",
            "lightblue": "#000000",
            "lightyellow": "#000000",
            "lightpink": "#000000",
            "lightlavender": "#000000",
            "lightpeach": "#000000",
            "img_factory": "#000000",
            "pastel": "#000000",
            "cream": "#000000",
            "white": "#000000"
        }
    
    def detect_theme_brightness(self, theme_data: Dict[str, Any]) -> str:
        """Auto-detect if theme is light or dark based on background color"""
        try:
            bg_color = theme_data["colors"]["bg_primary"]
            
            # Remove # if present
            if bg_color.startswith('#'):
                bg_color = bg_color[1:]
            
            # Convert to RGB and calculate brightness
            r = int(bg_color[:2], 16)
            g = int(bg_color[2:4], 16) 
            b = int(bg_color[4:6], 16)
            
            # Calculate perceived brightness
            brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
            
            # Return appropriate text color
            return "#000000" if brightness > 0.5 else "#ffffff"
            
        except (KeyError, ValueError, IndexError):
            # Default to black text if detection fails
            return "#000000"
    
    def get_text_color_for_theme(self, theme_filename: str, theme_data: Dict[str, Any]) -> str:
        """Get appropriate text color for a theme"""
        theme_name = theme_filename.replace('.json', '').lower()
        
        # Check manual overrides first
        if theme_name in self.light_text_themes:
            return self.light_text_themes[theme_name]
        elif theme_name in self.dark_text_themes:
            return self.dark_text_themes[theme_name]
        else:
            # Auto-detect based on background brightness
            detected_color = self.detect_theme_brightness(theme_data)
            print(f"  🔍 Auto-detected text color for {theme_name}: {detected_color}")
            return detected_color
    
    def backup_themes(self):
        """Create backup of existing theme files"""
        if not self.themes_dir.exists():
            print(f"❌ Themes directory not found: {self.themes_dir}")
            return False
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        json_files = list(self.themes_dir.glob("*.json"))
        if not json_files:
            print(f"❌ No JSON files found in {self.themes_dir}")
            return False
        
        print(f"📦 Creating backup of {len(json_files)} theme files...")
        
        for json_file in json_files:
            backup_file = self.backup_dir / json_file.name
            try:
                backup_file.write_text(json_file.read_text())
                print(f"  ✅ Backed up: {json_file.name}")
            except Exception as e:
                print(f"  ❌ Failed to backup {json_file.name}: {e}")
                return False
        
        return True
    
    def update_theme_file(self, json_file: Path) -> bool:
        """Update a single theme file with button text colors"""
        try:
            # Load existing theme
            with open(json_file, 'r') as f:
                theme_data = json.load(f)
            
            # Check if already has button text colors
            colors = theme_data.get("colors", {})
            if "button_text_color" in colors:
                print(f"  ⏭️ {json_file.name} already has button text colors - skipping")
                return True
            
            # Determine appropriate text color
            text_color = self.get_text_color_for_theme(json_file.name, theme_data)
            
            # Add button text color entries
            colors.update({
                "button_text_color": text_color,
                "button_text_hover": text_color, 
                "button_text_pressed": text_color
            })
            
            # Save updated theme
            with open(json_file, 'w') as f:
                json.dump(theme_data, f, indent=4)
            
            print(f"  ✅ Updated {json_file.name} with text color: {text_color}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to update {json_file.name}: {e}")
            return False
    
    def update_all_themes(self):
        """Update all theme files in the themes directory"""
        print("🎨 IMG Factory Theme Updater")
        print("=" * 40)
        
        # Create backup first
        if not self.backup_themes():
            print("❌ Backup failed - aborting update")
            return False
        
        print()
        
        # Find all JSON files
        json_files = list(self.themes_dir.glob("*.json"))
        if not json_files:
            print(f"❌ No JSON theme files found in {self.themes_dir}")
            return False
        
        print(f"🔄 Updating {len(json_files)} theme files...")
        
        success_count = 0
        for json_file in json_files:
            if self.update_theme_file(json_file):
                success_count += 1
        
        print()
        print("=" * 40)
        print(f"✅ Successfully updated {success_count}/{len(json_files)} theme files")
        
        if success_count < len(json_files):
            print(f"⚠️ {len(json_files) - success_count} files had issues")
        
        print(f"📦 Backups saved in: {self.backup_dir}")
        print()
        print("🎯 Next steps:")
        print("1. Restart IMG Factory")
        print("2. Test themes in Settings > Demo tab")
        print("3. Button text should now be readable!")
        
        return success_count == len(json_files)
    
    def restore_backup(self):
        """Restore themes from backup"""
        if not self.backup_dir.exists():
            print("❌ No backup directory found")
            return False
        
        backup_files = list(self.backup_dir.glob("*.json"))
        if not backup_files:
            print("❌ No backup files found")
            return False
        
        print(f"🔄 Restoring {len(backup_files)} theme files from backup...")
        
        for backup_file in backup_files:
            original_file = self.themes_dir / backup_file.name
            try:
                original_file.write_text(backup_file.read_text())
                print(f"  ✅ Restored: {backup_file.name}")
            except Exception as e:
                print(f"  ❌ Failed to restore {backup_file.name}: {e}")
        
        print("✅ Backup restoration complete")
        return True
    
    def list_themes(self):
        """List all themes and their detected text colors"""
        json_files = list(self.themes_dir.glob("*.json"))
        if not json_files:
            print("❌ No theme files found")
            return
        
        print("🎨 Theme Analysis:")
        print("-" * 50)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    theme_data = json.load(f)
                
                theme_name = theme_data.get("name", json_file.stem)
                bg_color = theme_data["colors"]["bg_primary"]
                text_color = self.get_text_color_for_theme(json_file.name, theme_data)
                
                # Check if already has button text
                has_button_text = "button_text_color" in theme_data["colors"]
                status = "✅ Ready" if has_button_text else "❌ Needs Update"
                
                print(f"{json_file.name:20} | {theme_name:25} | BG: {bg_color} | Text: {text_color} | {status}")
                
            except Exception as e:
                print(f"{json_file.name:20} | ERROR: {e}")


def main():
    """Main function with user menu"""
    updater = ThemeUpdater()
    
    while True:
        print("\n🎨 IMG Factory Theme Updater")
        print("=" * 30)
        print("1. 🔄 Update all themes (add button text colors)")
        print("2. 📋 List themes and status")
        print("3. 📦 Restore from backup")
        print("4. ❌ Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            updater.update_all_themes()
        elif choice == "2":
            updater.list_themes()
        elif choice == "3":
            updater.restore_backup()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
