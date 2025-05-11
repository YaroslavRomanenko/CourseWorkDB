import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import decimal

from ..utils import format_price_display, CustomAskStringDialog 
from .admin_utils import create_search_bar, setup_treeview_with_scrollbar, update_treeview_sort_indicators

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
        self.current_sort_column_db_key = 'username'
        self.current_sort_order_asc = True
        
        self.search_entry = None 
        self.users_tree = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_entry_widget, _, search_bar_actual_frame = create_search_bar(
            parent_frame=self,
            load_list_command=self.load_users_list,
            original_bg=self.original_bg,
            custom_button_style=self.custom_button_style
        )
        self.search_entry = search_entry_widget
        search_bar_actual_frame.grid(row=0, column=0, sticky='ew', pady=(0,10), padx=5)

        user_columns_config = [
            ('user_id', 'ID', 40, tk.NO, 'center', lambda: self._handle_sort_request('user_id')),
            ('username', 'Логін', 120, tk.YES, 'w', lambda: self._handle_sort_request('username')),
            ('email', 'Email', 180, tk.YES, 'w', lambda: self._handle_sort_request('email')),
            ('is_developer', 'Розробник', 70, tk.NO, 'center', None),
            ('studio', 'Студія', 120, tk.YES, 'w', None),
            ('owned_games', 'Ігор в бібл.', 80, tk.NO, 'center', lambda: self._handle_sort_request('owned_games')),
            ('is_admin', 'Адмін', 50, tk.NO, 'center', None),
            ('is_banned', 'Заблокований', 90, tk.NO, 'center', None),
            ('balance', 'Баланс', 90, tk.YES, 'e', lambda: self._handle_sort_request('balance'))
        ]
        
        container_for_treeview = ttk.Frame(self, style='TFrame')
        container_for_treeview.grid(row=1, column=0, sticky='nsew')
        
        self.users_tree = setup_treeview_with_scrollbar(
            parent_frame=container_for_treeview, 
            columns_config=user_columns_config,
            on_select_callback=self._on_user_select
        )

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10,5), padx=5)

        self.ban_user_button = ttk.Button(action_frame, text="Заблокувати", command=self._toggle_ban_user, style=self.custom_button_style, state=tk.DISABLED)
        self.ban_user_button.pack(side=tk.LEFT, padx=5)

        self.add_funds_button = ttk.Button(action_frame, text="Нарахувати кошти", command=self._admin_add_funds_to_user, style=self.custom_button_style, state=tk.DISABLED)
        self.add_funds_button.pack(side=tk.LEFT, padx=5)

        self.load_users_list()

    def _handle_sort_request(self, treeview_col_id_clicked):
        db_sort_key = treeview_col_id_clicked
        if treeview_col_id_clicked == 'owned_games':
            db_sort_key = 'owned_games_count'

        if self.current_sort_column_db_key == db_sort_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column_db_key = db_sort_key
            self.current_sort_order_asc = True
        
        if self.users_tree:
            update_treeview_sort_indicators(
                self.users_tree, 
                treeview_col_id_clicked, 
                self.current_sort_column_db_key, 
                self.current_sort_order_asc
            )
        self.load_users_list()

    def load_users_list(self):
        if not self.users_tree: return

        for i in self.users_tree.get_children():
            self.users_tree.delete(i)

        search_term = self.search_entry.get().strip() if self.search_entry else ""
        sort_order = 'ASC' if self.current_sort_order_asc else 'DESC'

        users_data = self.db_manager.fetch_all_users_for_admin(
            search_term=search_term,
            sort_by=self.current_sort_column_db_key,
            sort_order=sort_order
        )

        if users_data:
            for user in users_data:
                studio_name = user.get('developer_studio_name', '---') if user['is_developer'] else '---'
                owned_games = user.get('owned_games_count', 0)
                balance_val = user.get('balance')
                balance_display = f"{balance_val:.2f}₴" if balance_val is not None else "N/A"

                values = (
                    user.get('user_id', 'N/A'),
                    user.get('username', 'N/A'),
                    user.get('email', 'N/A'),
                    "Так" if user.get('is_developer') else "Ні",
                    studio_name,
                    owned_games,
                    "Так" if user.get('is_app_admin') else "Ні",
                    "Так" if user.get('is_banned') else "Ні",
                    balance_display
                )
                user_id_val = user.get('user_id')
                iid_val = str(user_id_val) if user_id_val is not None else None
                if iid_val:
                    self.users_tree.insert('', tk.END, values=values, iid=iid_val)
                else:
                    self.users_tree.insert('', tk.END, values=values) 
        self._on_user_select()

    def _on_user_select(self, event=None):
        if not self.users_tree: return
        selected_items = self.users_tree.selection()
        if selected_items:
            item_iid = selected_items[0]
            user_values = self.users_tree.item(item_iid, 'values')
            if not user_values or len(user_values) < 9:
                self.ban_user_button.config(state=tk.DISABLED, text="Заблокувати")
                self.add_funds_button.config(state=tk.DISABLED)
                return

            is_banned_str = user_values[7] 
            is_admin_str = user_values[6]
            try:
                if user_values[0] == "N/A": raise ValueError("User ID is N/A")
                selected_user_id = int(user_values[0])
            except ValueError: 
                self.ban_user_button.config(state=tk.DISABLED, text="Заблокувати")
                self.add_funds_button.config(state=tk.DISABLED)
                return

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
            
            if selected_user_id != admin_current_user_id:
                 self.add_funds_button.config(state=tk.NORMAL)
            else:
                 self.add_funds_button.config(state=tk.DISABLED)
        else:
            self.ban_user_button.config(state=tk.DISABLED, text="Заблокувати")
            self.add_funds_button.config(state=tk.DISABLED)

    def _toggle_ban_user(self):
        if not self.users_tree: return
        selected_items = self.users_tree.selection()
        if not selected_items:
            messagebox.showwarning("Дія неможлива", "Будь ласка, виберіть користувача зі списку.", parent=self)
            return

        item_iid = selected_items[0]
        user_values = self.users_tree.item(item_iid, 'values')
        if not user_values or len(user_values) < 9: return
        
        try:
            if user_values[0] == "N/A": raise ValueError("User ID is N/A")
            user_id_to_toggle = int(user_values[0])
        except ValueError: return

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

    def _admin_add_funds_to_user(self):
        if not self.users_tree: return
        selected_items = self.users_tree.selection()
        if not selected_items:
            messagebox.showwarning("Дія неможлива", "Будь ласка, виберіть користувача зі списку.", parent=self)
            return

        item_iid = selected_items[0]
        user_values = self.users_tree.item(item_iid, 'values')
        if not user_values or len(user_values) < 9: return
        
        try:
            if user_values[0] == "N/A": raise ValueError("User ID is N/A")
            target_user_id = int(user_values[0])
        except ValueError: return

        target_username = user_values[1]
        current_balance_str = user_values[8].replace('₴', '')

        amount_str = simpledialog.askstring(
            "Нарахування коштів",
            f"Введіть суму для нарахування користувачеві '{target_username}' (ID: {target_user_id}):\nПоточний баланс: {current_balance_str}₴",
            parent=self
        )

        if amount_str is None:
            return

        try:
            amount_to_add = decimal.Decimal(amount_str.replace(',', '.'))
            if amount_to_add <= 0:
                messagebox.showerror("Помилка Вводу", "Сума для нарахування повинна бути позитивним числом.", parent=self)
                return
        except decimal.InvalidOperation:
            messagebox.showerror("Помилка Вводу", "Некоректний формат суми. Будь ласка, введіть число.", parent=self)
            return
        except Exception as e:
            messagebox.showerror("Помилка Вводу", f"Невідома помилка при обробці суми: {e}", parent=self)
            return

        if messagebox.askyesno("Підтвердження нарахування",
                               f"Нарахувати {amount_to_add:.2f}₴ користувачеві '{target_username}'?",
                               parent=self):
            success = self.db_manager.add_funds(target_user_id, amount_to_add)
            if success:
                messagebox.showinfo("Успіх", f"Кошти успішно нараховано користувачеві '{target_username}'.", parent=self)
                self.load_users_list()
                if target_user_id == self.store_window_ref.current_user_id and hasattr(self.store_window_ref, 'refresh_user_info_display'):
                    self.store_window_ref.refresh_user_info_display()
    
    def refresh_panel_content(self):
        print("AdminUserManagementPanel: Refreshing content...")
        self.load_users_list()