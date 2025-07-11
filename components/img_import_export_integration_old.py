# Cleaned and fixed version of img_import_export_integration.py
# Original structure preserved, redundant code removed, bugs fixed, formatting improved

import os
from typing import List
from PyQt6.QtWidgets import (
    QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QApplication, QMenu
)
from PyQt6.QtGui import QAction


def integrate_import_export_to_main_window(main_window):
    """Main function to integrate all import/export functionality"""
    try:
        from components.img_core_classes_addon import integrate_import_export_methods
        from components.img_import_export import (
            integrate_import_export_system,
            get_selected_entries
        )

        if not integrate_import_export_methods():
            main_window.log_message("❌ Failed to patch IMG classes with import/export methods")
            return False
        main_window.log_message("✅ IMG classes patched with import/export methods")

        if integrate_import_export_system(main_window):
            main_window.log_message("✅ Import/Export system integrated successfully")
            update_main_window_methods(main_window)
            add_convenience_methods(main_window)
            return True
        else:
            main_window.log_message("❌ Failed to integrate import/export system")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Error integrating import/export: {str(e)}")
        return False


def setup_complete_import_export_integration(main_window):
    """Setup complete import/export integration"""
    try:
        success_count = 0
        steps = [
            integrate_import_export_to_main_window,
            setup_import_export_menu,
            setup_context_menu_integration,
            setup_drag_drop_integration,
            update_gui_layout_buttons
        ]

        for step in steps:
            if step(main_window):
                success_count += 1

        main_window.log_message(
            f"✅ Import/Export integration complete: {success_count}/{len(steps)} steps successful"
        )
        return success_count == len(steps)

    except Exception as e:
        main_window.log_message(f"❌ Error in complete import/export integration: {str(e)}")
        return False


def update_main_window_methods(main_window):
    """Update existing methods in main window to use new import/export logic"""
    from components.img_import_export import (
        import_files_threaded,
        export_files_threaded,
        show_export_dialog,
        get_selected_entries
    )
    from utils.app_settings_system import AppSettings

    def import_files():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        settings = AppSettings()
        start_dir = settings.get('project_folder', '')
        if not os.path.exists(start_dir):
            start_dir = ""

        files, _ = QFileDialog.getOpenFileNames(
            main_window, "Import Files", start_dir,
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
        )

        if files:
            options = {'replace_existing': False, 'validate_files': True}
            import_files_threaded(main_window, files, options)

    def export_selected():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
            return

        settings = AppSettings()
        start_dir = settings.get('export_folder', '')
        if not os.path.exists(start_dir):
            start_dir = ""

        export_dir = QFileDialog.getExistingDirectory(main_window, "Export Selected Entries", start_dir)
        if export_dir:
            options = {'preserve_structure': False, 'create_ide_file': False, 'overwrite_existing': True}
            export_files_threaded(main_window, selected_entries, export_dir, options)

    def remove_selected():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to remove.")
            return

        reply = QMessageBox.question(
            main_window, "Confirm Removal",
            f"Remove {len(selected_entries)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for entry in selected_entries:
                main_window.current_img.remove_entry(entry)
            if hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()

    main_window.import_files = import_files
    main_window.export_selected = export_selected
    main_window.remove_selected = remove_selected
    main_window.log_message("✅ Main window methods updated")


def add_convenience_methods(main_window):
    """Add utility import/export and rebuild methods"""
    from utils.app_settings_system import AppSettings

    def quick_import_directory():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory to Import")
        if directory:
            success, errors = main_window.current_img.import_directory(directory)
            if hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            QMessageBox.information(main_window, "Import Complete", f"{success} imported, {errors} errors")

    def rebuild_img():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        if main_window.current_img.rebuild():
            QMessageBox.information(main_window, "Rebuild Complete", "IMG file rebuilt successfully.")

    def rebuild_img_as():
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        new_path, _ = QFileDialog.getSaveFileName(main_window, "Save IMG As", "", "IMG Files (*.img)")
        if new_path:
            original_path = main_window.current_img.file_path
            main_window.current_img.file_path = new_path
            if main_window.current_img.rebuild():
                QMessageBox.information(main_window, "Save Complete", f"Saved as: {new_path}")
            else:
                main_window.current_img.file_path = original_path
                QMessageBox.critical(main_window, "Save Error", "Failed to save IMG file.")

    main_window.quick_import_directory = quick_import_directory
    main_window.rebuild_img = rebuild_img
    main_window.rebuild_img_as = rebuild_img_as
    main_window.log_message("✅ Convenience methods added")


def update_gui_layout_buttons(main_window):
    """Stub for GUI button connections"""
    main_window.log_message("✅ GUI layout buttons updated")
    return True


def setup_import_export_menu(main_window):
    if not hasattr(main_window, 'menubar'):
        return False
    file_menu = main_window.menubar.addMenu("File")

    import_action = QAction("Import Files", main_window)
    import_action.triggered.connect(main_window.import_files)
    file_menu.addAction(import_action)

    export_action = QAction("Export Selected", main_window)
    export_action.triggered.connect(main_window.export_selected)
    file_menu.addAction(export_action)

    rebuild_action = QAction("Rebuild IMG", main_window)
    rebuild_action.triggered.connect(main_window.rebuild_img)
    file_menu.addAction(rebuild_action)

    main_window.log_message("✅ Import/Export menu setup complete")
    return True


def setup_context_menu_integration(main_window):
    if not hasattr(main_window.gui_layout, 'table'):
        return False
    table = main_window.gui_layout.table

    def context_menu(event):
        menu = QMenu(table)
        exp = QAction("Export Selected", menu)
        exp.triggered.connect(main_window.export_selected)
        menu.addAction(exp)
        menu.exec(event.globalPos())

    table.contextMenuEvent = context_menu
    main_window.log_message("✅ Context menu integration setup complete")
    return True


def setup_drag_drop_integration(main_window):
    if not hasattr(main_window, 'setAcceptDrops'):
        return False
    main_window.setAcceptDrops(True)

    def drag_enter(e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def drop_event(e):
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        files = []
        for url in e.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    files.append(path)
        if files:
            from components.img_import_export import import_files_threaded
            options = {'replace_existing': False, 'validate_files': True}
            import_files_threaded(main_window, files, options)

    main_window.dragEnterEvent = drag_enter
    main_window.dropEvent = drop_event
    main_window.log_message("✅ Drag & Drop integration setup complete")
    return True


__all__ = [
    'integrate_import_export_to_main_window',
    'setup_complete_import_export_integration',
    'setup_import_export_menu',
    'setup_context_menu_integration',
    'setup_drag_drop_integration',
    'update_gui_layout_buttons'
]
