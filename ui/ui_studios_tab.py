import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import traceback
import os
import datetime

from PIL import Image, ImageTk
from functools import partial

from .ui_utils import *

class StudiosTab(tk.Frame):
    def __init__(self, parent, db_manager, user_id, is_developer_initial,
                 fonts, colors, styles, store_window_ref, **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.db_manager = db_manager
        self.user_id = user_id
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.store_window_ref = store_window_ref

        self.original_bg = colors.get('original_bg', 'white')
        self.hover_bg = colors.get('hover_bg', '#f0f0f0')
        self.custom_button_style = styles.get('custom_button', 'TButton')
        self.list_icon_size = (64, 64)

        self._image_references = getattr(store_window_ref, '_image_references', {})
        self.placeholder_image_list = getattr(store_window_ref, 'placeholder_image', None)
        self.studio_logo_folder = getattr(store_window_ref, 'studio_logo_folder', None)
        self.placeholder_image_name = getattr(store_window_ref, 'placeholder_image_name', 'placeholder.png')

        self.main_content_area = tk.Frame(self, bg=self.original_bg)
        self.main_content_area.pack(fill=tk.BOTH, expand=True)
        self.main_content_area.grid_rowconfigure(0, weight=1)
        self.main_content_area.grid_columnconfigure(0, weight=1)

        self.studios_canvas = None
        self.studios_inner_frame = None
        self._studio_widgets = []

        self._setup_ui()
        
    def _setup_ui(self):
        self.load_studios_list()
        
    def load_studios_list(self):
        print("StudiosTab: Loading studios list...")
        studios_data = None
        try:
            studios_data = self.db_manager.fetch_all_studios(sort_by='name', sort_order='ASC')
        except AttributeError:
            messagebox.showerror("Помилка", "Функція fetch_all_studios не реалізована в DB Manager.", parent=self)
            studios_data = None
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити список студій:\n{e}", parent=self)
            traceback.print_exc()
            studios_data = None

        self.studios_canvas, self.studios_inner_frame, self._studio_widgets = create_scrollable_list(
            parent=self.main_content_area,
            item_creation_func=self._create_studio_entry,
            item_data_list=studios_data,
            bg_color=self.original_bg,
            placeholder_text="На платформі ще немає зареєстрованих студій.",
            placeholder_font=self.fonts['ui'],
            item_pack_config={'fill': tk.X, 'pady': 2, 'padx': 2}
        )
        print(f"Studios list created/updated. Found {len(self._studio_widgets)} studio widgets.")
            
    def _create_studio_entry(self, parent, studio_data):
        studio_id = studio_data.get('studio_id')
        name = studio_data.get('name', 'Невідома студія')
        logo_filename = studio_data.get('logo')
        country = studio_data.get('country', 'Невідомо')

        if studio_id is None: return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.FLAT, background=self.original_bg, cursor="hand2")

        icon_label = tk.Label(entry_frame, background=self.original_bg, cursor="hand2")
        tk_image = load_image_cached(
            cache_dict=self._image_references,
            image_filename=logo_filename,
            folder_path=self.studio_logo_folder,
            size=self.list_icon_size,
            placeholder_image=self.placeholder_image_list
        )

        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.fonts['ui'], width=int(self.list_icon_size[0]/8), height=int(self.list_icon_size[1]/16), relief="solid", borderwidth=1)
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg, cursor="hand2")
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        name_label = tk.Label(text_frame, text=name,
                            font=self.fonts.get('list_title', ("Verdana", 12, "bold")),
                            anchor="w", justify=tk.LEFT, background=self.original_bg, cursor="hand2")
        name_label.pack(fill=tk.X, pady=(0, 2))

        country_label = tk.Label(text_frame, text=f"Країна: {country}",
                                font=self.fonts['ui'], anchor="w", justify=tk.LEFT, background=self.original_bg, cursor="hand2")
        country_label.pack(fill=tk.X)

        click_handler = partial(self._on_studio_select, name)

        entry_frame.bind("<Enter>",
                        lambda e, frm=entry_frame, hb=self.hover_bg, ob=self.original_bg, ign=[icon_label]:
                        apply_hover_effect(frm, hb, ob, ign))
        entry_frame.bind("<Leave>",
                        lambda e, frm=entry_frame, ob=self.original_bg, ign=[icon_label]:
                        remove_hover_effect(frm, ob, ign))
        entry_frame.bind("<Button-1>", click_handler)

        widgets_to_set_cursor = [
            icon_label, text_frame, name_label, country_label
        ]

        for widget in widgets_to_set_cursor:
            if widget and widget.winfo_exists():
                try:
                    widget.config(cursor="hand2")
                    widget.bind("<Button-1>", click_handler)
                except tk.TclError: pass

        return entry_frame

    def _on_studio_select(self, studio_name, event=None):
        print(f"StudiosTab: Selected studio: {studio_name}")
        if self.store_window_ref and hasattr(self.store_window_ref, '_show_studio_detail_view'):
            self.store_window_ref._show_studio_detail_view(studio_name)
        else:
            messagebox.showerror("Помилка", "Не вдалося відкрити деталі студії.", parent=self)

    def refresh_content(self):
        print("StudiosTab: Refreshing studios list.")
        self.load_studios_list()