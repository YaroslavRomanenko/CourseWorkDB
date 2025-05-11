import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from functools import partial

from ..utils import format_price_display 
from .admin_utils import create_search_bar, setup_treeview_with_scrollbar, update_treeview_sort_indicators

class AdminGameManagementPanel(ttk.Frame):
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
        self.current_sort_column_db_key = 'title' 
        self.current_sort_order_asc = True
        
        self.search_entry = None
        self.games_tree = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_entry_widget, _, search_bar_actual_frame = create_search_bar(
            parent_frame=self,
            load_list_command=self.load_games_list,
            original_bg=self.original_bg,
            custom_button_style=self.custom_button_style
        )
        self.search_entry = search_entry_widget
        search_bar_actual_frame.grid(row=0, column=0, sticky='ew', pady=(0,10), padx=5)
        
        game_columns_config = [
            ('game_id', 'ID', 50, tk.NO, 'center', lambda: self._handle_sort_request('game_id')),
            ('title', 'Назва', 300, tk.YES, 'w', lambda: self._handle_sort_request('title')),
            ('price', 'Ціна', 100, tk.YES, 'e', lambda: self._handle_sort_request('price')),
            ('release_date', 'Дата релізу', 120, tk.YES, 'center', lambda: self._handle_sort_request('release_date')),
            ('purchase_count', 'Продано', 80, tk.NO, 'center', lambda: self._handle_sort_request('purchase_count'))
        ]
        
        container_for_treeview = ttk.Frame(self, style='TFrame')
        container_for_treeview.grid(row=1, column=0, sticky='nsew')

        self.games_tree = setup_treeview_with_scrollbar(
            parent_frame=container_for_treeview,
            columns_config=game_columns_config,
            on_select_callback=self._on_game_select,
            on_double_click_callback=self._on_game_double_click
        )

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)
        
        self.load_games_list()

    def _handle_sort_request(self, treeview_col_id_clicked):
        db_sort_key = treeview_col_id_clicked
        
        if self.current_sort_column_db_key == db_sort_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column_db_key = db_sort_key
            self.current_sort_order_asc = True
        
        if self.games_tree:
            update_treeview_sort_indicators(
                self.games_tree,
                treeview_col_id_clicked,
                self.current_sort_column_db_key,
                self.current_sort_order_asc
            )
        self.load_games_list()

    def load_games_list(self):
        if not self.games_tree: return

        for i in self.games_tree.get_children():
            self.games_tree.delete(i)

        search_term = self.search_entry.get().strip() if self.search_entry else ""
        sort_order_str = 'ASC' if self.current_sort_order_asc else 'DESC'
        
        games_data = self.db_manager.fetch_all_games_for_admin(
            search_term=search_term,
            sort_by=self.current_sort_column_db_key,
            sort_order=sort_order_str
        )

        if games_data:
            for item_data in games_data:
                game_id = item_data.get('game_id')
                title = item_data.get('title', 'N/A')
                price = item_data.get('price')
                # status_val = item_data.get('status', 'N/A') # Статус не використовується
                release_date_raw = item_data.get('release_date')
                purchase_count = item_data.get('purchase_count', 0)
                
                release_date_display = "N/A"
                if release_date_raw:
                    try:
                        date_obj_to_format = None
                        if isinstance(release_date_raw, str):
                            date_part_str = release_date_raw.split(' ')[0]
                            date_obj_to_format = datetime.datetime.strptime(date_part_str, '%Y-%m-%d').date()
                        elif isinstance(release_date_raw, datetime.datetime):
                            date_obj_to_format = release_date_raw.date()
                        elif isinstance(release_date_raw, datetime.date):
                            date_obj_to_format = release_date_raw
                        
                        if date_obj_to_format:
                            release_date_display = date_obj_to_format.strftime('%d-%m-%Y')
                        elif release_date_raw: 
                            release_date_display = str(release_date_raw)
                    except ValueError:
                        release_date_display = str(release_date_raw) if release_date_raw else "N/A"
                    except Exception:
                        release_date_display = "Error" if release_date_raw else "N/A"
                
                current_columns = self.games_tree['columns']
                values_list = []
                if 'game_id' in current_columns: values_list.append(game_id if game_id is not None else "N/A")
                if 'title' in current_columns: values_list.append(title)
                if 'price' in current_columns: values_list.append(format_price_display(price))
                # if 'status' in current_columns: values_list.append(status_val) # Статус не додається
                if 'release_date' in current_columns: values_list.append(release_date_display)
                if 'purchase_count' in current_columns: values_list.append(purchase_count)
                
                values = tuple(values_list)

                game_id_val = item_data.get('game_id')
                iid_val = str(game_id_val) if game_id_val is not None else None
                if iid_val:
                    self.games_tree.insert('', tk.END, values=values, iid=iid_val)
                else:
                    self.games_tree.insert('', tk.END, values=values)

        self._on_game_select()

    def _on_game_select(self, event=None):
        pass 
    
    def _on_game_double_click(self, event=None):
        if not self.games_tree: return
        selected_items = self.games_tree.selection()
        if not selected_items:
            return
        item_iid = selected_items[0]
        game_id_values = self.games_tree.item(item_iid, 'values')
        if game_id_values:
            try:
                game_id_idx = self.games_tree['columns'].index('game_id')
                game_id_val = game_id_values[game_id_idx]
                if game_id_val != "N/A":
                    game_id = int(game_id_val)
                    if self.store_window_ref and hasattr(self.store_window_ref, '_show_detail_view'):
                        self.store_window_ref._show_detail_view(game_id)
                else:
                    print("Warning: Could not get valid game_id (N/A) for double click.")
            except (ValueError, IndexError):
                 print("Warning: Error getting game_id for double click from Treeview.")
        else:
            print("Warning: No values for selected item in game tree.")
            
    def refresh_panel_content(self):
        print("AdminGameManagementPanel: Refreshing content...")
        self.load_games_list()