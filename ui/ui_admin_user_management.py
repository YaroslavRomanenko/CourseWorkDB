
import tkinter as tk
from tkinter import ttk, messagebox

from .ui_utils import setup_text_widget_editing

class AdminUserManagementPanel(ttk.Frame):
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

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_refresh_frame = ttk.Frame(self, style='TFrame')
        search_refresh_frame.grid(row=0, column=0, sticky='ew', pady=(0,10), padx=5)
        search_refresh_frame.grid_columnconfigure(1, weight=1)

        search_label = ttk.Label(search_refresh_frame, text="Пошук:", background=self.original_bg)
        search_label.pack(side=tk.LEFT, padx=(0,5))

        self.search_entry = ttk.Entry(search_refresh_frame, width=30)
        setup_text_widget_editing(self.search_entry)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", lambda e: self.load_users_list())

        search_button = ttk.Button(search_refresh_frame, text="Знайти", command=self.load_users_list, style=self.custom_button_style)
        search_button.pack(side=tk.LEFT, padx=(5,10))
        refresh_button = ttk.Button(search_refresh_frame, text="Оновити", command=self.load_users_list, style=self.custom_button_style)
        refresh_button.pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self, style='TFrame')
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ('user_id', 'username', 'email', 'is_developer', 'studio', 'owned_games', 'is_admin', 'is_banned', 'balance')
        self.users_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.users_tree.heading('user_id', text='ID', command=lambda: self._sort_tree_column('user_id'))
        self.users_tree.heading('username', text='Логін', command=lambda: self._sort_tree_column('username'))
        self.users_tree.heading('email', text='Email', command=lambda: self._sort_tree_column('email'))
        self.users_tree.heading('is_developer', text='Розробник')
        self.users_tree.heading('studio', text='Студія')
        self.users_tree.heading('owned_games', text='Ігор в бібл.', command=lambda: self._sort_tree_column('owned_games_count'))
        self.users_tree.heading('is_admin', text='Адмін')
        self.users_tree.heading('is_banned', text='Заблокований')
        self.users_tree.heading('balance', text='Баланс', command=lambda: self._sort_tree_column('balance'))


        self.users_tree.column('user_id', width=40, stretch=tk.NO, anchor='center')
        self.users_tree.column('username', width=120, anchor='w')
        self.users_tree.column('email', width=180, anchor='w')
        self.users_tree.column('is_developer', width=70, stretch=tk.NO, anchor='center')
        self.users_tree.column('studio', width=120, anchor='w')
        self.users_tree.column('owned_games', width=80, stretch=tk.NO, anchor='center')
        self.users_tree.column('is_admin', width=50, stretch=tk.NO, anchor='center')
        self.users_tree.column('is_banned', width=90, stretch=tk.NO, anchor='center')
        self.users_tree.column('balance', width=90, anchor='e')
        
        self.current_sort_column = 'username'
        self.current_sort_order_asc = True


        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.users_tree.pack(side='left', fill='both', expand=True)

        self.users_tree.bind('<<TreeviewSelect>>', self._on_user_select)

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)

        self.ban_user_button = ttk.Button(action_frame, text="Заблокувати", command=self._toggle_ban_user, style=self.custom_button_style, state=tk.DISABLED)
        self.ban_user_button.pack(side=tk.LEFT, padx=5)

        self.load_users_list()

    def _sort_tree_column(self, col_identifier):
        db_col_key = 'owned_games_count' if col_identifier == 'owned_games' else col_identifier

        if self.current_sort_column == db_col_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column = db_col_key
            self.current_sort_order_asc = True

        for c in self.users_tree['columns']:
            self.users_tree.heading(c, text=self.users_tree.heading(c, 'text').replace('▲', '').replace('▼', '').strip())

        arrow = ' ▲' if self.current_sort_order_asc else ' ▼'
        current_heading_text = self.users_tree.heading(col_identifier, 'text')
        self.users_tree.heading(col_identifier, text=current_heading_text + arrow)
        
        self.load_users_list()


    def load_users_list(self):
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)

        search_term = self.search_entry.get().strip()
        sort_order = 'ASC' if self.current_sort_order_asc else 'DESC'

        users_data = self.db_manager.fetch_all_users_for_admin(
            search_term=search_term,
            sort_by=self.current_sort_column,
            sort_order=sort_order
        )

        if users_data:
            for user in users_data:
                studio_name = user.get('developer_studio_name', '---') if user['is_developer'] else '---'
                owned_games = user.get('owned_games_count', 0)

                values = (
                    user['user_id'],
                    user['username'],
                    user['email'],
                    "Так" if user['is_developer'] else "Ні",
                    studio_name,
                    owned_games,
                    "Так" if user['is_app_admin'] else "Ні",
                    "Так" if user['is_banned'] else "Ні",
                    f"{user['balance']:.2f}₴" if user['balance'] is not None else "N/A"
                )
                self.users_tree.insert('', tk.END, values=values, iid=str(user['user_id']))
        self._on_user_select()

    def _on_user_select(self, event=None):
        selected_items = self.users_tree.selection()
        if selected_items:
            item_iid = selected_items[0]
            user_values = self.users_tree.item(item_iid, 'values')
            if not user_values:
                self.ban_user_button.config(state=tk.DISABLED, text="Заблокувати")
                return

            is_banned_str = user_values[7]
            is_admin_str = user_values[6]
            selected_user_id = int(user_values[0])
            admin_current_user_id = self.store_window_ref.current_user_id

            can_ban_unban = True
            if is_admin_str == "Так" and selected_user_id != admin_current_user_id:
                can_ban_unban = False
            if selected_user_id == admin_current_user_id and is_banned_str == "Ні":
                can_ban_unban = False

            if can_ban_unban:
                self.ban_user_button.config(state=tk.NORMAL)
                self.ban_user_button.config(text="Розблокувати" if is_banned_str == "Так" else "Заблокувати")
            else:
                self.ban_user_button.config(state=tk.DISABLED)
                self.ban_user_button.config(text="Заблокувати")
        else:
            self.ban_user_button.config(state=tk.DISABLED, text="Заблокувати")

    def _toggle_ban_user(self):
        selected_items = self.users_tree.selection()
        if not selected_items:
            messagebox.showwarning("Дія неможлива", "Будь ласка, виберіть користувача зі списку.", parent=self)
            return

        item_iid = selected_items[0]
        user_values = self.users_tree.item(item_iid, 'values')
        if not user_values: return

        user_id_to_toggle = int(user_values[0])
        username_to_toggle = user_values[1]
        current_ban_status_str = user_values[7]
        new_ban_status = True if current_ban_status_str == "Ні" else False
        action_verb = "заблокувати" if new_ban_status else "розблокувати"
        admin_current_user_id = self.store_window_ref.current_user_id

        if messagebox.askyesno("Підтвердження",
                               f"Ви впевнені, що хочете {action_verb} користувача '{username_to_toggle}' (ID: {user_id_to_toggle})?",
                               parent=self):
            success = self.db_manager.set_user_ban_status(user_id_to_toggle, new_ban_status, admin_current_user_id)
            if success:
                messagebox.showinfo("Успіх", f"Користувача '{username_to_toggle}' успішно {action_verb}но.", parent=self)
                self.load_users_list()
    
    def refresh_panel_content(self):
        print("AdminUserManagementPanel: Refreshing content...")
        self.load_users_list()