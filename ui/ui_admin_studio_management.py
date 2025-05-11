import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import datetime

from .ui_utils import setup_text_widget_editing

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
        self.current_sort_column = 'name'
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
        self.search_entry.bind("<Return>", lambda e: self.load_studios_list())

        search_button = ttk.Button(search_refresh_frame, text="Знайти", command=self.load_studios_list, style=self.custom_button_style)
        search_button.pack(side=tk.LEFT, padx=(5,10))
        refresh_button = ttk.Button(search_refresh_frame, text="Оновити", command=self.load_studios_list, style=self.custom_button_style)
        refresh_button.pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self, style='TFrame')
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ('studio_id', 'name', 'country', 'established_date', 'game_count', 'developer_count')
        self.studios_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.studios_tree.heading('studio_id', text='ID', command=lambda: self._sort_tree_column('studio_id'))
        self.studios_tree.heading('name', text='Назва', command=lambda: self._sort_tree_column('name'))
        self.studios_tree.heading('country', text='Країна', command=lambda: self._sort_tree_column('country'))
        self.studios_tree.heading('established_date', text='Засновано', command=lambda: self._sort_tree_column('established_date'))
        self.studios_tree.heading('game_count', text='Ігор', command=lambda: self._sort_tree_column('game_count'))
        self.studios_tree.heading('developer_count', text='Розробників', command=lambda: self._sort_tree_column('developer_count'))

        self.studios_tree.column('studio_id', width=50, stretch=tk.NO, anchor='center')
        self.studios_tree.column('name', width=200, anchor='w')
        self.studios_tree.column('country', width=120, anchor='w')
        self.studios_tree.column('established_date', width=100, anchor='center')
        self.studios_tree.column('game_count', width=70, stretch=tk.NO, anchor='center')
        self.studios_tree.column('developer_count', width=90, stretch=tk.NO, anchor='center')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.studios_tree.yview)
        self.studios_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.studios_tree.pack(side='left', fill='both', expand=True)

        self.studios_tree.bind('<<TreeviewSelect>>', self._on_studio_select)
        self.studios_tree.bind("<Double-1>", self._on_studio_double_click)

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)

        self.load_studios_list()

    def _sort_tree_column(self, col_identifier):
        db_col_key = col_identifier
        if self.current_sort_column == db_col_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column = db_col_key
            self.current_sort_order_asc = True

        for c in self.studios_tree['columns']:
            self.studios_tree.heading(c, text=self.studios_tree.heading(c, 'text').replace('▲', '').replace('▼', '').strip())

        arrow = ' ▲' if self.current_sort_order_asc else ' ▼'
        current_heading_text = self.studios_tree.heading(col_identifier, 'text')
        self.studios_tree.heading(col_identifier, text=current_heading_text + arrow)
        
        self.load_studios_list()

    def load_studios_list(self):
        for i in self.studios_tree.get_children():
            self.studios_tree.delete(i)

        search_term = self.search_entry.get().strip()
        sort_order_str = 'ASC' if self.current_sort_order_asc else 'DESC'
        
        studios_data = self.db_manager.fetch_all_studios_for_admin(
            search_term=search_term,
            sort_by=self.current_sort_column,
            sort_order=sort_order_str
        )

        if studios_data:
            for studio in studios_data:
                est_date_str = studio.get('established_date')
                if est_date_str:
                    try:
                        if isinstance(est_date_str, str):
                            est_date_str = est_date_str.split(' ')[0] 
                            est_date_obj = datetime.datetime.strptime(est_date_str, '%Y-%m-%d').date()
                            est_date_obj = est_date_str
                        est_date_display = est_date_obj.strftime('%d-%m-%Y')
                    except ValueError:
                        est_date_display = str(est_date_str)
                else:
                    est_date_display = "N/A"

                values = (
                    studio.get('studio_id'),
                    studio.get('name', 'N/A'),
                    studio.get('country', 'N/A'),
                    est_date_display,
                    studio.get('game_count', 0),
                    studio.get('developer_count', 0)
                )
                self.studios_tree.insert('', tk.END, values=values, iid=str(studio.get('studio_id')))
        self._on_studio_select()

    def _on_studio_select(self, event=None):
        selected_items = self.studios_tree.selection()
        if selected_items:
            pass
        else:
            pass

    def _on_studio_double_click(self, event=None):
        selected_items = self.studios_tree.selection()
        if not selected_items:
            return
        item_iid = selected_items[0]
        studio_name = self.studios_tree.item(item_iid, 'values')[1]
        if studio_name and studio_name != 'N/A':
            if self.store_window_ref and hasattr(self.store_window_ref, '_show_studio_detail_view'):
                self.store_window_ref._show_studio_detail_view(studio_name)


    def _edit_studio(self):
        messagebox.showinfo("В розробці", "Функція редагування студії знаходиться в розробці.", parent=self)

    def _toggle_verify_studio(self):
        messagebox.showinfo("В розробці", "Функція верифікації студії знаходиться в розробці.", parent=self)
    
    def refresh_panel_content(self):
        print("AdminStudioManagementPanel: Refreshing content...")
        self.load_studios_list()