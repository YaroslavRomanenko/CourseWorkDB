import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
import datetime

from ..utils import setup_text_widget_editing, format_price_display

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
        self.current_sort_column = 'title' 
        self.current_sort_order_asc = True

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_refresh_frame = ttk.Frame(self, style='TFrame')
        search_refresh_frame.grid(row=0, column=0, sticky='ew', pady=(0,10), padx=5)
        search_refresh_frame.grid_columnconfigure(1, weight=1)

        search_label = ttk.Label(search_refresh_frame, text="Пошук (назва):", background=self.original_bg)
        search_label.pack(side=tk.LEFT, padx=(0,5))
        self.search_entry = ttk.Entry(search_refresh_frame, width=30)
        setup_text_widget_editing(self.search_entry)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", lambda e: self.load_games_list())

        search_button = ttk.Button(search_refresh_frame, text="Знайти", command=self.load_games_list, style=self.custom_button_style)
        search_button.pack(side=tk.LEFT, padx=(5,0))
        
        tree_frame = ttk.Frame(self, style='TFrame')
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('game_id', 'title', 'price', 'release_date', 'purchase_count') 
        self.games_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.games_tree.heading('game_id', text='ID', command=lambda: self._sort_tree_column('game_id'))
        self.games_tree.heading('title', text='Назва', command=lambda: self._sort_tree_column('title'))
        self.games_tree.heading('price', text='Ціна', command=lambda: self._sort_tree_column('price'))
        self.games_tree.heading('release_date', text='Дата релізу', command=lambda: self._sort_tree_column('release_date'))
        self.games_tree.heading('purchase_count', text='Продано', command=lambda: self._sort_tree_column('purchase_count'))

        self.games_tree.column('game_id', width=50, stretch=tk.NO, anchor='center')
        self.games_tree.column('title', width=300, anchor='w')
        self.games_tree.column('price', width=100, anchor='e')
        self.games_tree.column('release_date', width=120, anchor='center')
        self.games_tree.column('purchase_count', width=80, stretch=tk.NO, anchor='center')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.games_tree.pack(side='left', fill='both', expand=True)

        self.games_tree.bind('<<TreeviewSelect>>', self._on_game_select)
        self.games_tree.bind("<Double-1>", self._on_game_double_click)

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)
        
        self.load_games_list()

    def _sort_tree_column(self, col_identifier):
        if col_identifier == 'status':
            return

        db_col_key = col_identifier
        
        if self.current_sort_column == db_col_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column = db_col_key
            self.current_sort_order_asc = True

        for c in self.games_tree['columns']:
            if c == 'status': continue 
            self.games_tree.heading(c, text=self.games_tree.heading(c, 'text').replace('▲', '').replace('▼', '').strip())

        arrow = ' ▲' if self.current_sort_order_asc else ' ▼'
        if col_identifier in self.games_tree['columns']:
            current_heading_text = self.games_tree.heading(col_identifier, 'text')
            self.games_tree.heading(col_identifier, text=current_heading_text + arrow)
        
        self.load_games_list()

    def load_games_list(self):
        for i in self.games_tree.get_children():
            self.games_tree.delete(i)

        search_term = self.search_entry.get().strip()
        sort_order_str = 'ASC' if self.current_sort_order_asc else 'DESC'
        
        sort_by_db = self.current_sort_column
        if sort_by_db == 'status': 
            sort_by_db = 'title' 

        games_data = self.db_manager.fetch_all_games_for_admin(
            search_term=search_term,
            sort_by=sort_by_db,
            sort_order=sort_order_str
        )

        if games_data:
            for item_data in games_data:
                game_id = item_data.get('game_id')
                title = item_data.get('title', 'N/A')
                price = item_data.get('price')
                status_val = item_data.get('status', 'N/A') 
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
                if 'status' in current_columns: values_list.append(status_val)
                if 'release_date' in current_columns: values_list.append(release_date_display)
                if 'purchase_count' in current_columns: values_list.append(purchase_count)
                
                values = tuple(values_list)

                if game_id is not None:
                    self.games_tree.insert('', tk.END, values=values, iid=str(game_id))
                else:
                    self.games_tree.insert('', tk.END, values=values)

        self._on_game_select()

    def _on_game_select(self, event=None):
        selected_items = self.games_tree.selection()
        if selected_items:
            pass
        else:
            pass
    
    def _on_game_double_click(self, event=None):
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
            except ValueError:
                 print("Warning: 'game_id' column not found in Treeview for double click.")
            except IndexError:
                 print("Warning: Index out of bounds when accessing game_id_values for double click.")
        else:
            print("Warning: No values for selected item in game tree.")
            
    def refresh_panel_content(self):
        print("AdminGameManagementPanel: Refreshing content...")
        self.load_games_list()