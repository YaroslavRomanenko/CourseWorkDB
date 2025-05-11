import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial

from .ui_utils import setup_text_widget_editing, format_price_display

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
        search_button.pack(side=tk.LEFT, padx=(5,10))
        refresh_button = ttk.Button(search_refresh_frame, text="Оновити", command=self.load_games_list, style=self.custom_button_style)
        refresh_button.pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self, style='TFrame')
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ('game_id', 'title', 'price', 'status', 'release_date', 'purchase_count') # Додано purchase_count
        self.games_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.games_tree.heading('game_id', text='ID', command=lambda: self._sort_tree_column('game_id'))
        self.games_tree.heading('title', text='Назва', command=lambda: self._sort_tree_column('title'))
        self.games_tree.heading('price', text='Ціна', command=lambda: self._sort_tree_column('price'))
        self.games_tree.heading('status', text='Статус', command=lambda: self._sort_tree_column('status'))
        self.games_tree.heading('release_date', text='Дата релізу', command=lambda: self._sort_tree_column('release_date'))
        self.games_tree.heading('purchase_count', text='Продано', command=lambda: self._sort_tree_column('purchase_count'))

        self.games_tree.column('game_id', width=50, stretch=tk.NO, anchor='center')
        self.games_tree.column('title', width=250, anchor='w')
        self.games_tree.column('price', width=100, anchor='e')
        self.games_tree.column('status', width=100, anchor='center')
        self.games_tree.column('release_date', width=100, anchor='center')
        self.games_tree.column('purchase_count', width=70, stretch=tk.NO, anchor='center')

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
        db_col_key = col_identifier

        if self.current_sort_column == db_col_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column = db_col_key
            self.current_sort_order_asc = True

        for c in self.games_tree['columns']:
            self.games_tree.heading(c, text=self.games_tree.heading(c, 'text').replace('▲', '').replace('▼', '').strip())

        arrow = ' ▲' if self.current_sort_order_asc else ' ▼'
        current_heading_text = self.games_tree.heading(col_identifier, 'text')
        self.games_tree.heading(col_identifier, text=current_heading_text + arrow)
        
        self.load_games_list()

    def load_games_list(self):
        for i in self.games_tree.get_children():
            self.games_tree.delete(i)

        search_term = self.search_entry.get().strip()
        sort_order_str = 'ASC' if self.current_sort_order_asc else 'DESC'
        
        games_data = self.db_manager.fetch_all_games(
            sort_by=self.current_sort_column,
            sort_order=sort_order_str
        )

        if games_data:
            for game in games_data:
                game_id = game[0]
                title = game[1]
                price = game[3]
                status = "N/A"
                release_date_str = "N/A"
                purchase_count = game[5] if len(game) > 5 else 0

                if search_term and search_term.lower() not in title.lower():
                    continue

                values = (
                    game_id,
                    title,
                    format_price_display(price),
                    status,
                    release_date_str,
                    purchase_count
                )
                self.games_tree.insert('', tk.END, values=values, iid=str(game_id))
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
        game_id = int(self.games_tree.item(item_iid, 'values')[0])
        if self.store_window_ref and hasattr(self.store_window_ref, '_show_detail_view'):
            self.store_window_ref._show_detail_view(game_id)


    def _edit_game(self):
        messagebox.showinfo("В розробці", "Функція редагування гри знаходиться в розробці.", parent=self)

    def _toggle_game_visibility(self):
        messagebox.showinfo("В розробці", "Функція зміни видимості гри знаходиться в розробці.", parent=self)

    def refresh_panel_content(self):
        print("AdminGameManagementPanel: Refreshing content...")
        self.load_games_list()