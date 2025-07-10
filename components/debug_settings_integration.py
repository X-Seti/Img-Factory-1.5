#this belongs in components/debug_settings_integration.py - version 1
# X-Seti - July10 2025 - Img Factory 1.5
# Integration patch for existing debug settings

def integrate_col_debug_into_settings():
    """Integrate COL debug settings into existing settings dialog"""
    try:
        # Import and patch the settings system
        from utils.app_settings_system import SettingsDialog
        from components.col_debug_settings import patch_settings_dialog_for_col_debug
        
        # Patch the SettingsDialog class
        original_init = SettingsDialog.__init__
        
        def patched_init(self, app_settings, parent=None):
            # Call original init
            original_init(self, app_settings, parent)
            
            # Add COL debug functionality
            try:
                patch_settings_dialog_for_col_debug(self)
            except Exception as e:
                print(f"Warning: Could not add COL debug settings: {e}")
        
        # Apply the patch
        SettingsDialog.__init__ = patched_init
        
        print("✅ COL debug settings integrated into main settings dialog")
        return True
        
    except Exception as e:
        print(f"❌ Failed to integrate COL debug settings: {e}")
        return False

def setup_debug_categories_for_col():
    """Setup COL debug categories in the main app settings"""
    try:
        from utils.app_settings_system import AppSettings
        
        # Add COL debug categories to default settings
        col_categories = [
            'COL_LOADING',
            'COL_PARSING', 
            'COL_THREADING',
            'COL_DISPLAY',
            'COL_INTEGRATION',
            'COL_ESTIMATION',
            'COL_VALIDATION'
        ]
        
        # Patch the default settings
        original_get_default = AppSettings._get_default_settings
        
        def patched_get_default(self):
            defaults = original_get_default(self)
            
            # Add COL categories to existing debug categories
            existing_categories = defaults.get('debug_categories', [])
            for category in col_categories:
                if category not in existing_categories:
                    existing_categories.append(category)
            
            defaults['debug_categories'] = existing_categories
            return defaults
        
        AppSettings._get_default_settings = patched_get_default
        
        print("✅ COL debug categories added to default settings")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup COL debug categories: {e}")
        return False

# Main integration function
def setup_col_debug_integration():
    """Main function to setup COL debug integration"""
    try:
        # Setup debug categories first
        setup_debug_categories_for_col()
        
        # Integrate into settings dialog
        integrate_col_debug_into_settings()
        
        print("✅ COL debug integration setup complete")
        return True
        
    except Exception as e:
        print(f"❌ COL debug integration failed: {e}")
        return False

# Call this from imgfactory.py after imports
if __name__ != "__main__":
    setup_col_debug_integration()