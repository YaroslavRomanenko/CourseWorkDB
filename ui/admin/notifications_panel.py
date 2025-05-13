import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from functools import partial

from .admin_utils import create_search_bar, setup_treeview_with_scrollbar, update_treeview_sort_indicators
from ..utils import format_datetime_display

class AdminNotificationsPanel(ttk.Frame):
    def __init__(self, parent, db_manager, store_window_ref, fonts, colors, styles, **kwargs):
        super().__init__(parent, **kwargs)
        self.db_manager = db_manager
        self.store_window_ref = store_window_ref
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.custom_button_style = styles.get('custom_button', 'TButton')

        self.current_sort_column_db_key = 'created_at'
        self.current_sort_order_asc = True 

        self.notifications_tree = None
        self.approve_button = None
        self.reject_button = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        columns_config = [
            ('notification_id', 'ID', 40, tk.NO, 'center', lambda: self._handle_sort_request('notification_id')),
            ('created_at', 'Дата', 130, tk.NO, 'w', lambda: self._handle_sort_request('created_at')),
            ('notification_type', 'Тип', 150, tk.NO, 'w', lambda: self._handle_sort_request('notification_type')),
            ('initiator_username', 'Від кого', 120, tk.YES, 'w', lambda: self._handle_sort_request('user_id')),
            ('target_username', 'Кому/Що', 120, tk.YES, 'w', lambda: self._handle_sort_request('target_user_id')),
            ('message', 'Повідомлення', 250, tk.YES, 'w', None),
        ]

        container_for_treeview = ttk.Frame(self, style='TFrame')
        container_for_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.notifications_tree = setup_treeview_with_scrollbar(
            parent_frame=container_for_treeview,
            columns_config=columns_config,
            on_select_callback=self._on_notification_select
        )

        action_frame = ttk.Frame(self, style='TFrame')
        action_frame.pack(fill=tk.X, pady=(5,10), padx=5)

        self.approve_button = ttk.Button(action_frame, text="Схвалити", command=self._approve_request, style=self.custom_button_style, state=tk.DISABLED)
        self.approve_button.pack(side=tk.LEFT, padx=5)
        self.reject_button = ttk.Button(action_frame, text="Відхилити", command=self._reject_request, style=self.custom_button_style, state=tk.DISABLED)
        self.reject_button.pack(side=tk.LEFT, padx=5)

        refresh_list_button = ttk.Button(action_frame, text="Оновити список", command=self.load_notifications, style=self.custom_button_style)
        refresh_list_button.pack(side=tk.RIGHT, padx=5)

        self.load_notifications()

    def _handle_sort_request(self, treeview_col_id_clicked):
        db_sort_key = treeview_col_id_clicked
        if treeview_col_id_clicked == 'initiator_username':
            db_sort_key = 'user_id'
        elif treeview_col_id_clicked == 'target_username':
            db_sort_key = 'target_user_id'

        if self.current_sort_column_db_key == db_sort_key:
            self.current_sort_order_asc = not self.current_sort_order_asc
        else:
            self.current_sort_column_db_key = db_sort_key
            self.current_sort_order_asc = True

        if self.notifications_tree:
            update_treeview_sort_indicators(
                self.notifications_tree,
                treeview_col_id_clicked,
                self.current_sort_column_db_key,
                self.current_sort_order_asc
            )
        self.load_notifications()

    def load_notifications(self):
        if not self.notifications_tree: return

        for i in self.notifications_tree.get_children():
            self.notifications_tree.delete(i)

        notifications_data = self.db_manager.fetch_pending_admin_notifications(
            sort_by=self.current_sort_column_db_key,
            sort_order='ASC' if self.current_sort_order_asc else 'DESC'
        )

        if notifications_data:
            for notif in notifications_data:
                created_at_display = format_datetime_display(notif.get('created_at'))

                values = (
                    notif.get('notification_id'),
                    created_at_display,
                    notif.get('notification_type'),
                    notif.get('initiator_username', 'Система'),
                    notif.get('target_username', 'N/A'),
                    notif.get('message', '')
                )
                notif_id_val = notif.get('notification_id')
                iid_val = str(notif_id_val) if notif_id_val is not None else None
                if iid_val:
                    self.notifications_tree.insert('', tk.END, values=values, iid=iid_val, tags=(notif.get('notification_type'),))
                else:
                    self.notifications_tree.insert('', tk.END, values=values, tags=(notif.get('notification_type'),))

        self._on_notification_select()

    def _on_notification_select(self, event=None):
        if not self.notifications_tree: return
        selected_items = self.notifications_tree.selection()
        if selected_items:
            self.approve_button.config(state=tk.NORMAL)
            self.reject_button.config(state=tk.NORMAL)
        else:
            self.approve_button.config(state=tk.DISABLED)
            self.reject_button.config(state=tk.DISABLED)

    def _approve_request(self):
        self._process_selected_request(approve=True)

    def _reject_request(self):
        self._process_selected_request(approve=False)

    def _process_selected_request(self, approve: bool):
        if not self.notifications_tree: return
        selected_items = self.notifications_tree.selection()
        if not selected_items:
            messagebox.showwarning("Дія неможлива", "Будь ласка, виберіть запит зі списку.", parent=self)
            return

        item_iid = selected_items[0]
        try:
            notification_id = int(item_iid)
        except ValueError:
            messagebox.showerror("Помилка", "Некоректний ID запиту.", parent=self)
            return

        notif_type_tuple = self.notifications_tree.item(item_iid, 'tags')
        if not notif_type_tuple:
            messagebox.showerror("Помилка", "Не вдалося визначити тип сповіщення.", parent=self)
            return
        notif_type = notif_type_tuple[0]

        admin_user_id = self.store_window_ref.current_user_id
        action_text = "схвалити" if approve else "відхилити"

        success = False
        if notif_type == 'developer_status_request':
            if messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете {action_text} цей запит на статус розробника?", parent=self):
                success = self.db_manager.process_developer_status_request(notification_id, admin_user_id, approve)
        else:
            messagebox.showerror("Невідомий тип", f"Обробка для типу сповіщення '{notif_type}' не реалізована.", parent=self)
            return

        if success:
            messagebox.showinfo("Успіх", f"Запит успішно {action_text}но.", parent=self)
            self.load_notifications()

    def refresh_panel_content(self):
        print("AdminNotificationsPanel: Refreshing content...")
        self.load_notifications()