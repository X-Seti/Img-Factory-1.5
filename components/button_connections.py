#this belongs in components/ button_connections.py - Version: 1
# X-Seti - JUNE28 2025 - Img Factory 1.5 - Button Connection Module

def connect_img_buttons(main_window, buttons):
    """Connect IMG operation buttons to their functions"""
    button_map = {
        "New": main_window.create_new_img,
        "Open": main_window.open_img_file, 
        "Close": main_window.close_img_file,
        "Close All": main_window.close_all_img,
        "Rebuild": main_window.rebuild_img,
        "Rebuild As": main_window.rebuild_img_as,
        "Rebuild All": main_window.rebuild_all_img,
        "Merge": main_window.merge_img,
        "Split": main_window.split_img,
        "Convert": main_window.convert_img
    }
    
    for button in buttons:
        if hasattr(button, 'full_text'):
            func = button_map.get(button.full_text)
            if func:
                button.clicked.connect(func)

def connect_entry_buttons(main_window, buttons):
    """Connect entry operation buttons to their functions"""
    button_map = {
        "Import": main_window.import_files,
        "Import via": main_window.import_via_tool,
        "Export": main_window.export_selected,
        "Export via": main_window.export_via_tool,
        "Remove": main_window.remove_selected,
        "Remove All": main_window.remove_all_entries,
        "Update list": main_window.refresh_table,
        "Quick Export": main_window.quick_export,
        "Pin selected": main_window.pin_selected
    }
    
    for button in buttons:
        if hasattr(button, 'full_text'):
            func = button_map.get(button.full_text)
            if func:
                button.clicked.connect(func)

def connect_col_buttons(main_window, buttons):
    """Connect COL functionality buttons"""
    button_map = {
        "Col Edit": main_window.open_col_editor,
        "Txd Edit": main_window.open_txd_editor,
        "Dff Edit": main_window.open_dff_editor,
        "Ipf Edit": main_window.open_ipf_editor,
        "IPL Edit": main_window.open_ipl_editor,
        "IDE Edit": main_window.open_ide_editor,
        "Dat Edit": main_window.open_dat_editor,
        "Zons Edit": main_window.open_zons_editor,
        "Weap Edit": main_window.open_weap_editor,
        "Vehi Edit": main_window.open_vehi_editor,
        "Radar Map": main_window.open_radar_map,
        "Paths Map": main_window.open_paths_map,
        "Waterpro": main_window.open_waterpro
    }
    
    for button in buttons:
        if hasattr(button, 'full_text'):
            func = button_map.get(button.full_text)
            if func:
                button.clicked.connect(func)