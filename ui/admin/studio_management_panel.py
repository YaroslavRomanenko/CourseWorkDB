import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import datetime

from ..utils import setup_text_widget_editing # setup_text_widget_editing з загальних utils
from .admin_utils import create_search_bar, setup_treeview_with_scrollbar, update_treeview_sort_indicators

class AdminStudioManagementPanel(ttk.Frame):
    def __init__(self, parent, db_manager, store_window_ref, fonts, colors, styles, **kwargs):
        super().__init__(parent, **kwargs)
        self.db_manager = db_manager
        self.store_window_ref = store_window_ref
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.custom_button_style = styles.get('custom_button', 'TButton')
        self.original_bg = colors.get('original_bg', 'white')

        self.configure(style='TFrame')
        self.current_sort_column_db_key = 'name'
        self.current_sort_order_asc = True
        
        self.search_entry = None
        self.studios_tree = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_entry_widget, _, search_bar_actual_frame = create_search_bar(
            parent_frame=self,
            load_list_command=self.load_studios_list,
            original_bg=self.original_bg,
            custom_button_style=self.custom_button_style
        )
        self.search_entry = search_entry_widget
        search_bar_actual_frame.grid(row=0, column=0, sticky='ew', pady=(0,10), padx=5)
        
        studio_columns_config = [
            ('studio_id', 'ID', 50, tk.NO, 'center', lambda: self._handle_sort_request('studio_id')),
            ('name', 'Назва', 200, tk.YES, 'w', lambda: self._handle_sort_request('name')),
            ('country', 'Країна', 120, tk.YES, 'w', lambda: self._handle_sort_request('country')),
            ('established_date', 'Засновано', 100, tk.YES, 'center', lambda: self._handle_sort_request('established_date')),
            ('game_count', 'Ігор', 70, tk.NO, 'center', lambda: self._handle_sort_request('game_count')),
            ('developer_count', 'Розробників', 90, tk.NO, 'center', lambda: self._handle_sort_request('developer_count'))
        ]

        container_for_treeview = ttk.Frame(self, style='TFrame')
        container_for_treeview.grid(row=1, column=0, sticky='nsew')

        self.studios_tree = setup_treeview_with_scrollbar(
            parent_frame=container_for_treeview,
            columns_config=studio_columns_config,
            on_select_callback=self._on_studio_select,
            on_double_click_callback=self._on_studio_double_click
        )

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)
        
        self.load_studios_list()

    def _handle_sort_request(self, treeview_col_id_clicked):
        db_sort_key = treeview_col_id_clicked
        
        if self.current_sort_column_db_key == db_sort_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column_db_key = db_sort_key
            self.current_sort_order_asc = True
        
        if self.studios_tree:
            update_treeview_sort_indicators(
                self.studios_tree,
                treeview_col_id_clicked,
                self.current_sort_column_db_key,
                self.current_sort_order_asc
            )
        self.load_studios_list()

    def load_studios_list(self):
        if not self.studios_tree: return

        for i in self.studios_tree.get_children():
            self.studios_tree.delete(i)

        search_term = self.search_entry.get().strip() if self.search_entry else ""
        sort_order_str = 'ASC' if self.current_sort_order_asc else 'DESC'
        
        studios_data = self.db_manager.fetch_all_studios_for_admin(
            search_term=search_term,
            sort_by=self.current_sort_column_db_key,
            sort_order=sort_order_str
        )

        if studios_data:
            for studio in studios_data:
                est_date_raw = studio.get('established_date')
                est_date_display = "N/A"

                if est_date_raw:
                    try:
                        date_obj_to_format = None
                        if isinstance(est_date_raw, str):
                            date_part_str = est_date_raw.split(' ')[0]
                            date_obj_to_format = datetime.datetime.strptime(date_part_str, '%Y-%m-%d').date()
                        elif isinstance(est_date_raw, datetime.datetime): 
                            date_obj_to_format = est_date_raw.date()
                        elif isinstance(est_date_raw, datetime.date): 
                            date_obj_to_format = est_date_raw
                        
                        if date_obj_to_format: 
                            est_date_display = date_obj_to_format.strftime('%d-%m-%Y')
                        elif est_date_raw:
                            est_date_display = str(est_date_raw)
                    except ValueError:
                        est_date_display = str(est_date_raw) if est_date_raw else "N/A"
                    except Exception:
                        est_date_display = "Error" if est_date_raw else "N/A"
                
                values = (
                    studio.get('studio_id', "N/A"),
                    studio.get('name', 'N/A'),
                    studio.get('country', 'N/A'),
                    est_date_display,
                    studio.get('game_count', 0),
                    studio.get('developer_count', 0)
                )
                studio_id_val = studio.get('studio_id')
                iid_val = str(studio_id_val) if studio_id_val is not None else None
                if iid_val:
                    self.studios_tree.insert('', tk.END, values=values, iid=iid_val)
                else:
                    self.studios_tree.insert('', tk.END, values=values)
        self._on_studio_select()

    def _on_studio_select(self, event=None):
        pass

    def _on_studio_double_click(self, event=None):
        if not self.studios_tree: return
        selected_items = self.studios_tree.selection()
        if not selected_items:
            return
        item_iid = selected_items[0]
        studio_values = self.studios_tree.item(item_iid, 'values')
        if studio_values and len(studio_values) > 1:
            try:
                name_idx = self.studios_tree['columns'].index('name')
                studio_name = studio_values[name_idx]
                if studio_name and studio_name != 'N/A':
                    if self.store_window_ref and hasattr(self.store_window_ref, '_show_studio_detail_view'):
                        self.store_window_ref._show_studio_detail_view(studio_name)
            except (ValueError, IndexError):
                print("Error getting studio name for double click from Treeview.")
    
    def refresh_panel_content(self):
        print("AdminStudioManagementPanel: Refreshing content...")
        self.load_studios_list()