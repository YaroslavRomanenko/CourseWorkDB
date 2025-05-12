import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from PIL import Image, ImageTk
from functools import partial
import decimal
import traceback

from .utils import *
from .library import LibraryTab
from .studios_tab import StudiosTab
from .game_details import GameDetailView
from .studio_details import StudioDetailView

from .admin import *

class StoreWindow(tk.Tk):
    def __init__(self, db_manager, user_id, is_app_admin, 
                 image_folder, studio_logo_folder,
                 placeholder_image_path, placeholder_image_name, open_login_func):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = user_id
        self.is_app_admin = is_app_admin
        self.username = "User"
        self.current_balance = decimal.Decimal('0.00')
        self._image_references = {}
        self.placeholder_image = None
        self.placeholder_image_detail = None
        self._game_widgets_store = []
        self.is_developer = False
        self.studios_tab_instance = None
        self.admin_user_management_panel_instance = None
        self.admin_studio_management_panel_instance = None
        self.admin_game_management_panel_instance = None

        self.current_sort_key = 'title'
        self.current_sort_reverse = False

        self.image_folder = image_folder
        self.studio_logo_folder = studio_logo_folder
        self.placeholder_image_path = placeholder_image_path
        self.placeholder_image_name = placeholder_image_name
        self.open_login_callback = open_login_func

        self.detail_area_frame = None
        self.detail_back_button = None
        self.detail_frame_container = None
        self.detail_canvas = None
        self.detail_scrollbar = None
        self.detail_view_instance = None

        self.studio_detail_area_frame = None
        self.studio_detail_back_button = None
        self.studio_detail_frame_container = None
        self.studio_detail_canvas = None
        self.studio_detail_scrollbar = None
        self.studio_detail_view_instance = None

        self.user_info_frame = None
        self.username_label = None
        self.balance_label = None
        self.user_dropdown_menu = None

        self.store_canvas = None
        self.store_inner_frame = None
        self._game_widgets_store = []

        self.original_bg = "white"
        self.hover_bg = "#f0f0f0"
        self.list_icon_size = (64, 64)
        self.detail_icon_size = (160, 160)
        self.fonts = {
            'ui': ("Verdana", 10), 'title': ("Verdana", 16, "bold"),
            'detail': ("Verdana", 11), 'price': ("Verdana", 12),
            'comment': ("Verdana", 9), 'description': ("Verdana", 10),
            'list_title': ("Verdana", 12, "bold"), 'library_list_title': ("Verdana", 11, "bold"),
            'library_detail_title': ("Verdana", 14, "bold"), 'review_author': ("Verdana", 9, "bold"),
            'review_text': ("Verdana", 9), 'review_input': ("Verdana", 10),
            'section_header': ("Verdana", 12, "bold")
        }
        self.styles = {'custom_button': 'NoFocus.TButton'}
        self.colors = {
            'original_bg': self.original_bg, 'hover_bg': self.hover_bg,
            'listbox_select_bg': self.original_bg, 'listbox_select_fg': 'black',
            'no_comments_fg': 'grey', 'comment_fg': 'black',
            'no_comments_message': " Коментарів ще немає.", 'no_reviews_message': " Рецензій ще немає.",
            'link_fg': 'blue', 'placeholder_fg': 'grey',
            'date_fg': '#555555', 'separator_fg': 'grey',
            'textbox_bg': 'white', 'input_bg': 'white', 'input_fg': 'black',
            'user_panel_text_fg': 'black', 'user_panel_bg': '#ededed',
            'username_fg': '#67c1f5'
        }
        self.sort_label_style_name = 'TLabel'

        self._fetch_and_set_user_info()
        self._load_placeholders(list_size=self.list_icon_size, detail_size=self.detail_icon_size)

        self.width = 950
        self.height = 700
        center_window(self, self.width, self.height)
        self.title("Universal Games")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style(self)
        try:
            pass 
        except tk.TclError as e:
            print(f"Error setting theme: {e}")

        try:
            theme_bg = style.lookup('TFrame', 'background')
            self.original_bg = theme_bg if theme_bg else "white"
            self.colors['original_bg'] = self.original_bg
            self.colors['user_panel_bg'] = '#ededed'
            self.configure(bg=self.original_bg)

            self.custom_button_style = 'NoFocus.TButton'
            try:
                 button_bg = style.lookup('TButton', 'background')
                 style.configure(self.custom_button_style, focuscolor=button_bg)
            except tk.TclError:
                 print("Could not configure NoFocus.TButton style for the current theme.")
                 self.custom_button_style = 'TButton'

            style.configure('TNotebook', background=self.original_bg)
            style.configure('TNotebook.Tab', font=self.fonts['ui'], padding=[5, 2])
            style.map('TNotebook.Tab',
                       background=[('selected', self.original_bg)],
                       focuscolor=[('focus', self.original_bg)])

            style.configure('TFrame', background=self.original_bg)
            style.configure('TPanedwindow', background=self.original_bg)
            style.configure('Vertical.TScrollbar', background=self.original_bg)

        except tk.TclError as e:
             print(f"Помилка налаштування стилів ttk після зміни теми: {e}.")
             self.original_bg = "white"
             self.colors['original_bg'] = self.original_bg
             self.colors['user_panel_bg'] = '#ededed'
             self.custom_button_style = 'TButton'
             self.configure(bg=self.original_bg)

        top_bar_frame = tk.Frame(self, bg=self.original_bg)
        top_bar_frame.grid(row=0, column=0, sticky='ew')
        top_bar_frame.grid_columnconfigure(0, weight=1)
        top_bar_frame.grid_columnconfigure(1, weight=0)

        app_title_label = tk.Label(top_bar_frame, text="Universal Games", font=("Verdana", 18, "bold"), bg=top_bar_frame['bg'])
        app_title_label.grid(row=0, column=0, pady=(10,5), sticky='w', padx=10)

        self.user_info_frame = self._create_user_info_panel(top_bar_frame)
        self.user_info_frame.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

        self.main_content_frame = tk.Frame(self, bg=self.original_bg)
        self.main_content_frame.grid(row=1, column=0, sticky='nsew')
        self.main_content_frame.pack_propagate(False)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.main_content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.store_tab_main_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.store_tab_main_frame, text='Магазин')
        self.store_tab_main_frame.grid_rowconfigure(1, weight=1)
        self.store_tab_main_frame.grid_columnconfigure(0, weight=1)
        self.sort_panel_frame = self._create_sort_panel(self.store_tab_main_frame)
        self.sort_panel_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5,0))
        self.store_list_container = tk.Frame(self.store_tab_main_frame, bg=self.original_bg)
        self.store_list_container.grid(row=1, column=0, sticky='nsew')
        self.store_list_container.grid_rowconfigure(0, weight=1)
        self.store_list_container.grid_columnconfigure(0, weight=1)

        self.library_tab_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.library_tab_frame, text='Бібліотека')
        self.library_view = LibraryTab(
             parent=self.library_tab_frame, db_manager=self.db_manager, user_id=self.current_user_id,
             image_cache=self._image_references, placeholder_list=self.placeholder_image,
             placeholder_detail=self.placeholder_image_detail, image_folder_path=self.image_folder,
             fonts=self.fonts, colors=self.colors
        )
        self.library_view.paned_window.pack(fill=tk.BOTH, expand=True)

        self.studios_tab_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.studios_tab_frame, text='Студії')
        self.studios_tab_instance = StudiosTab(
            parent=self.studios_tab_frame,
            db_manager=self.db_manager,
            user_id=self.current_user_id,
            is_developer_initial=self.is_developer,
            fonts=self.fonts,
            colors=self.colors,
            styles=self.styles,
            store_window_ref=self
        )
        self.studios_tab_instance.pack(fill=tk.BOTH, expand=True)

        self.workshop_tab_frame = ttk.Frame(self.notebook, style='TFrame', padding=(10, 10))
        self.notebook.add(self.workshop_tab_frame, text='Майстерня')
        self.workshop_tab_frame.grid_columnconfigure(0, weight=1)
        self._setup_workshop_tab()

        if self.is_app_admin:
            self.admin_panel_tab_frame = ttk.Frame(self.notebook, style='TFrame')
            self.notebook.add(self.admin_panel_tab_frame, text='Адмін-панель')
            
            self.admin_notebook = ttk.Notebook(self.admin_panel_tab_frame)
            self.admin_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            self.user_mgmt_tab = ttk.Frame(self.admin_notebook, style='TFrame')
            self.admin_notebook.add(self.user_mgmt_tab, text='Користувачі')
            self.admin_user_management_panel_instance = AdminUserManagementPanel(
                parent=self.user_mgmt_tab,
                db_manager=self.db_manager,
                store_window_ref=self,
                fonts=self.fonts, colors=self.colors, styles=self.styles
            )
            self.admin_user_management_panel_instance.pack(fill=tk.BOTH, expand=True)

            self.studio_mgmt_tab = ttk.Frame(self.admin_notebook, style='TFrame')
            self.admin_notebook.add(self.studio_mgmt_tab, text='Студії')
            self.admin_studio_management_panel_instance = AdminStudioManagementPanel(
                parent=self.studio_mgmt_tab,
                db_manager=self.db_manager,
                store_window_ref=self,
                fonts=self.fonts, colors=self.colors, styles=self.styles
            )
            self.admin_studio_management_panel_instance.pack(fill=tk.BOTH, expand=True)
            
            self.game_mgmt_tab = ttk.Frame(self.admin_notebook, style='TFrame')
            self.admin_notebook.add(self.game_mgmt_tab, text='Ігри')
            self.admin_game_management_panel_instance = AdminGameManagementPanel(
                parent=self.game_mgmt_tab,
                db_manager=self.db_manager,
                store_window_ref=self,
                fonts=self.fonts, colors=self.colors, styles=self.styles
            )
            self.admin_game_management_panel_instance.pack(fill=tk.BOTH, expand=True)

            self.notifications_tab = ttk.Frame(self.admin_notebook, style='TFrame')
            self.admin_notebook.add(self.notifications_tab, text='Сповіщення')
            self.admin_notifications_panel_instance = AdminNotificationsPanel(
                parent=self.notifications_tab,
                db_manager=self.db_manager,
                store_window_ref=self,
                fonts=self.fonts, colors=self.colors, styles=self.styles
            )
            self.admin_notifications_panel_instance.pack(fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(self, text="Оновити", command=self.refresh_current_tab, style=self.custom_button_style)
        refresh_button.grid(row=2, column=0, pady=10)

        self.load_games_store()

        self.bind_all("<MouseWheel>", self._on_mousewheel, add='+')
        self.bind_all("<Button-4>", self._on_mousewheel, add='+')
        self.bind_all("<Button-5>", self._on_mousewheel, add='+')
    
    def _show_notebook_view(self):
        """Hides detail views and shows the main notebook view"""
        if self.detail_area_frame and self.detail_area_frame.winfo_exists():
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_view_instance = None
        if self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_exists():
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_view_instance = None

        if not self.notebook.winfo_ismapped():
             self.notebook.pack(fill=tk.BOTH, expand=True)

        self.title("Universal Games")
        
    def _show_detail_view(self, game_id, event=None):
        """Hides the notebook and displays the GameDetailView for the selected game"""
        self.notebook.pack_forget()
        if self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_exists():
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_view_instance = None
        if self.detail_area_frame and self.detail_area_frame.winfo_exists():
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_view_instance = None

        try:
            game_details = self.db_manager.fetch_game_details(game_id)
            if not game_details:
                 messagebox.showwarning("Не знайдено", f"Гра з ID {game_id} не знайдена.")
                 self._show_notebook_view(); return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі гри:\n{e}")
            traceback.print_exc()
            self._show_notebook_view(); return

        self.detail_area_frame = tk.Frame(self.main_content_frame, bg=self.original_bg)
        self.detail_area_frame.pack(fill=tk.BOTH, expand=True)
        self.detail_area_frame.grid_rowconfigure(1, weight=1)
        self.detail_area_frame.grid_columnconfigure(0, weight=1)

        self.detail_back_button = ttk.Button(
            self.detail_area_frame, text="< Назад", command=self._show_notebook_view, style=self.custom_button_style
        )
        self.detail_back_button.grid(row=0, column=0, pady=(5, 10), padx=5, sticky='w')

        self.detail_frame_container = tk.Frame(self.detail_area_frame, bg=self.original_bg)
        self.detail_frame_container.grid(row=1, column=0, sticky='nsew')
        self.detail_frame_container.grid_rowconfigure(0, weight=1)
        self.detail_frame_container.grid_columnconfigure(0, weight=1)

        self.detail_canvas = tk.Canvas(self.detail_frame_container, borderwidth=0, background=self.original_bg, highlightthickness=0)
        self.detail_scrollbar = ttk.Scrollbar(self.detail_frame_container, orient="vertical", command=self.detail_canvas.yview)
        self.detail_canvas.configure(yscrollcommand=self.detail_scrollbar.set)
        self.detail_scrollbar.pack(side="right", fill="y")
        self.detail_canvas.pack(side="left", fill="both", expand=True)

        self.detail_view_instance = GameDetailView(
            parent=self.detail_canvas,
            db_manager=self.db_manager,
            user_id=self.current_user_id,
            game_id=game_id,
            game_data=game_details,
            image_cache=self._image_references,
            placeholder_list=self.placeholder_image,
            placeholder_detail=self.placeholder_image_detail,
            image_folder=self.image_folder,
            placeholder_image_path=self.placeholder_image_path,
            placeholder_image_name=self.placeholder_image_name,
            fonts=self.fonts,
            colors=self.colors,
            styles=self.styles,
            scroll_target_canvas=self.detail_canvas,
            store_window_ref=self
        )
        detail_canvas_window_id = self.detail_canvas.create_window((0, 0), window=self.detail_view_instance, anchor="nw")

        def _on_detail_frame_configure(event=None):
            if self.detail_canvas and self.detail_canvas.winfo_exists():
                 self.detail_canvas.after_idle(lambda: self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all")))

        def _on_detail_canvas_configure(event):
             canvas_width = event.width
             if self.detail_canvas and self.detail_canvas.winfo_exists():
                 self.detail_canvas.itemconfig(detail_canvas_window_id, width=canvas_width)
             if self.detail_view_instance and self.detail_view_instance.winfo_exists():
                 self.detail_view_instance.after_idle(lambda w=canvas_width: self.detail_view_instance._update_wraplengths(container_width=w))

        if self.detail_view_instance: self.detail_view_instance.bind("<Configure>", _on_detail_frame_configure)
        if self.detail_canvas: self.detail_canvas.bind('<Configure>', _on_detail_canvas_configure)
        self.detail_area_frame.after(50, _on_detail_frame_configure)

        self.title(f"{game_details.get('title', 'Деталі гри')}")

    def _load_placeholders(self, list_size=(64, 64), detail_size=(160, 160)):
        """Loads and caches placeholder ImageTk objects using the utility function."""
        print("Loading and caching placeholders...")
        if self.placeholder_image_path and os.path.exists(self.placeholder_image_path):
            self.placeholder_image = load_image_cached(
                cache_dict=self._image_references,
                image_filename=self.placeholder_image_name,
                folder_path=self.image_folder, 
                size=list_size,
                placeholder_image=None 
            )
            self.placeholder_image_detail = load_image_cached(
                cache_dict=self._image_references,
                image_filename=self.placeholder_image_name,
                folder_path=self.image_folder,
                size=detail_size,
                placeholder_image=None
            )

            if self.placeholder_image: 
                print(f"List placeholder loaded/cached ({list_size})")
            else: 
                print(f"Failed to load list placeholder ({list_size}).")
            if self.placeholder_image_detail: 
                print(f"Detail placeholder loaded/cached ({detail_size})")
            else: 
                print(f"Failed to load detail placeholder ({detail_size}).")
        else:
            print(f"Placeholder image file not found or path not set: {self.placeholder_image_path}")
            self.placeholder_image = None
            self.placeholder_image_detail = None
    
          
    def _on_mousewheel(self, event):
        """Global mousewheel handler to scroll the appropriate canvas"""
        grab_holder = self.grab_current()
        if grab_holder is not None and grab_holder != self:
             return

        widget_under_cursor = event.widget
        target_canvas = None

        if self.detail_view_instance and self.detail_area_frame and self.detail_area_frame.winfo_ismapped():
            if widget_under_cursor.winfo_exists():
                 try:
                    is_child = str(self.detail_view_instance.winfo_parent()) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id()))
                    if is_child: return
                 except tk.TclError: pass
            target_canvas = self.detail_canvas
        elif self.studio_detail_view_instance and self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_ismapped():
            if widget_under_cursor.winfo_exists():
                 try:
                    is_child = str(self.studio_detail_view_instance.winfo_parent()) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id()))
                    if is_child: return
                 except tk.TclError: pass
            target_canvas = self.studio_detail_canvas
        elif self.notebook.winfo_ismapped():
            try:
                current_tab_index = self.notebook.index(self.notebook.select())
                tab_name = self.notebook.tab(current_tab_index, "text")

                if tab_name == 'Магазин':
                     if hasattr(self, 'store_canvas') and self.store_canvas:
                         if widget_under_cursor.winfo_exists():
                             try:
                                 parent_check = self.store_inner_frame if hasattr(self, 'store_inner_frame') else self.store_canvas
                                 if str(parent_check) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id())):
                                     target_canvas = self.store_canvas
                             except tk.TclError: pass
                         elif self.store_canvas:
                              target_canvas = self.store_canvas

                elif tab_name == 'Бібліотека':
                     if hasattr(self, 'library_view') and hasattr(self.library_view, 'library_canvas'):
                         if widget_under_cursor.winfo_exists():
                             try:
                                 parent_check = self.library_view.library_list_frame if hasattr(self.library_view, 'library_list_frame') else self.library_view.library_canvas
                                 if str(parent_check) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id())):
                                     target_canvas = self.library_view.library_canvas
                             except tk.TclError: pass
                         elif self.library_view.library_canvas:
                             target_canvas = self.library_view.library_canvas

                elif tab_name == 'Студії':
                     if hasattr(self, 'studios_tab_instance') and hasattr(self.studios_tab_instance, 'studios_canvas'):
                          if widget_under_cursor.winfo_exists():
                              try:
                                  parent_check = self.studios_tab_instance.studios_inner_frame if hasattr(self.studios_tab_instance, 'studios_inner_frame') else self.studios_tab_instance.studios_canvas
                                  if str(parent_check) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id())):
                                      target_canvas = self.studios_tab_instance.studios_canvas
                              except tk.TclError: pass
                          elif self.studios_tab_instance.studios_canvas:
                                target_canvas = self.studios_tab_instance.studios_canvas
                elif tab_name == 'Адмін-панель' and self.is_app_admin:
                    if hasattr(self, 'admin_notebook') and self.admin_notebook.winfo_exists():
                        admin_current_tab_idx = self.admin_notebook.index(self.admin_notebook.select())
                        admin_tab_name_selected = self.admin_notebook.tab(admin_current_tab_idx, "text")

            except (tk.TclError, AttributeError): pass

        if not target_canvas or not target_canvas.winfo_exists(): return

        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return

        yview_result = target_canvas.yview()
        can_scroll_up = yview_result[0] > 0.0001
        can_scroll_down = yview_result[1] < 0.9999

        if (delta < 0 and can_scroll_up) or (delta > 0 and can_scroll_down):
            target_canvas.yview_scroll(delta, "units")

        return "break"

    def _create_game_entry(self, parent, game_data):
        """Creates a tk.Frame widget representing a single game in the store list"""
        try:
            game_id, title, _, price, image_filename, purchase_count = game_data[:6]
        except (ValueError, TypeError) as e:
            print(f"Error unpacking game data in _create_game_entry: {game_data}, Error: {e}")
            return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.FLAT, background=self.original_bg, cursor="hand2")

        icon_label = tk.Label(entry_frame, background=self.original_bg, cursor="hand2")
        tk_image = load_image_cached(
            cache_dict=self._image_references,
            image_filename=image_filename,
            folder_path=self.image_folder,
            size=self.list_icon_size,
            placeholder_image=self.placeholder_image
        )
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.fonts['ui'], width=int(self.list_icon_size[0]/8), height=int(self.list_icon_size[1]/16), relief="solid", borderwidth=1)
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg, cursor="hand2")
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        title_label = tk.Label(text_frame, text=title or "Без назви", font=self.fonts['list_title'], anchor="w", justify=tk.LEFT, background=self.original_bg, cursor="hand2")
        title_label.pack(fill=tk.X, pady=(0, 2))

        price_purchase_frame = tk.Frame(text_frame, background=self.original_bg, cursor="hand2")
        price_purchase_frame.pack(fill=tk.X)
        price_text = format_price_display(price)
        price_label = tk.Label(price_purchase_frame, text=price_text, font=self.fonts['ui'], anchor="w", justify=tk.LEFT, background=self.original_bg, cursor="hand2")
        price_label.pack(side=tk.LEFT, anchor='w')

        purchase_label = None
        if isinstance(purchase_count, int) and purchase_count > 0:
            purchase_label = tk.Label(price_purchase_frame, text=f"Покупок: {purchase_count}", font=self.fonts['comment'], fg='grey', anchor="e", justify=tk.RIGHT, background=self.original_bg, cursor="hand2")
            purchase_label.pack(side=tk.RIGHT, anchor='e', padx=(10, 0))

        click_handler = partial(self._show_detail_view, game_id)

        entry_frame.bind("<Enter>",
                        lambda e, frm=entry_frame, hb=self.hover_bg, ob=self.original_bg, ign=[icon_label]:
                        apply_hover_effect(frm, hb, ob, ign))
        entry_frame.bind("<Leave>",
                        lambda e, frm=entry_frame, ob=self.original_bg, ign=[icon_label]:
                        remove_hover_effect(frm, ob, ign))
        entry_frame.bind("<Button-1>", click_handler)

        widgets_to_set_cursor = [icon_label, text_frame, title_label, price_purchase_frame, price_label]
        if purchase_label:
            widgets_to_set_cursor.append(purchase_label)

        for widget in widgets_to_set_cursor:
            if widget and widget.winfo_exists():
                try:
                    widget.config(cursor="hand2")
                    widget.bind("<Button-1>", click_handler)
                except tk.TclError: pass

        return entry_frame
    
    def load_games_store(self):
        """Fetches game data based on current sort settings and populates the store list using the create_scrollable_list utility"""
        print(f"Loading store games. Sort by: {self.current_sort_key}, Reverse: {self.current_sort_reverse}")
        db_sort_key = self.current_sort_key
        db_sort_order = 'DESC' if self.current_sort_reverse else 'ASC'

        games_data_from_db = []
        try:
            games_data_from_db = self.db_manager.fetch_all_games(
                sort_by=db_sort_key,
                sort_order=db_sort_order
            )
        except AttributeError:
            messagebox.showerror("Помилка", "Функція fetch_all_games не реалізована або не приймає параметри сортування в DB Manager.")
            games_data_from_db = None
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити список ігор:\n{e}")
            traceback.print_exc()
            games_data_from_db = None

        self.store_canvas, self.store_inner_frame, self._game_widgets_store = create_scrollable_list(
            parent=self.store_list_container,
            item_creation_func=self._create_game_entry,
            item_data_list=games_data_from_db,
            bg_color=self.original_bg,
            placeholder_text="В магазині поки немає ігор.",
            placeholder_font=self.fonts['ui']
        )
        print(f"Store list created/updated. Found {len(self._game_widgets_store)} game widgets.")

    def load_games_library(self):
        """Triggers a refresh of the library tab view"""
        if hasattr(self, 'library_view') and self.library_view:
            print("Triggering library refresh from StoreWindow...")
            self.library_view.load_library_games()
        else:
            print("Warning: Library view is not initialized yet, cannot refresh.")
            
    def _show_studio_detail_view(self, studio_name):
        """Hides the notebook and displays the StudioDetailView for the selected studio"""
        self.notebook.pack_forget()
        if self.detail_area_frame and self.detail_area_frame.winfo_exists():
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_view_instance = None
        if self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_exists():
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_view_instance = None

        print(f"Attempting to show details for studio: {studio_name}")

        self.studio_detail_area_frame = tk.Frame(self.main_content_frame, bg=self.original_bg)
        self.studio_detail_area_frame.pack(fill=tk.BOTH, expand=True)
        self.studio_detail_area_frame.grid_rowconfigure(1, weight=1)
        self.studio_detail_area_frame.grid_columnconfigure(0, weight=1)

        self.studio_detail_back_button = ttk.Button(
            self.studio_detail_area_frame, text="< Назад",
            command=self._show_notebook_view, style=self.custom_button_style
        )
        self.studio_detail_back_button.grid(row=0, column=0, pady=(5, 10), padx=5, sticky='w')

        self.studio_detail_frame_container = tk.Frame(self.studio_detail_area_frame, bg=self.original_bg)
        self.studio_detail_frame_container.grid(row=1, column=0, sticky='nsew')
        self.studio_detail_frame_container.grid_rowconfigure(0, weight=1)
        self.studio_detail_frame_container.grid_columnconfigure(0, weight=1)

        self.studio_detail_canvas = tk.Canvas(self.studio_detail_frame_container, borderwidth=0, background=self.original_bg, highlightthickness=0)
        self.studio_detail_scrollbar = ttk.Scrollbar(self.studio_detail_frame_container, orient="vertical", command=self.studio_detail_canvas.yview)
        self.studio_detail_canvas.configure(yscrollcommand=self.studio_detail_scrollbar.set)
        self.studio_detail_scrollbar.pack(side="right", fill="y")
        self.studio_detail_canvas.pack(side="left", fill="both", expand=True)

        self.studio_detail_view_instance = StudioDetailView(
            parent=self.studio_detail_canvas,
            db_manager=self.db_manager,
            studio_name=studio_name,
            fonts=self.fonts, colors=self.colors, styles=self.styles,
            scroll_target_canvas=self.studio_detail_canvas,
            store_window_ref=self,
            image_cache=self._image_references,
            placeholder_detail=self.placeholder_image_detail,
            studio_logo_folder=self.studio_logo_folder
        )
        studio_canvas_window_id = self.studio_detail_canvas.create_window((0, 0), window=self.studio_detail_view_instance, anchor="nw")

        def _on_studio_detail_frame_configure(event=None):
             if self.studio_detail_canvas and self.studio_detail_canvas.winfo_exists():
                 self.studio_detail_canvas.after_idle(lambda: self.studio_detail_canvas.configure(scrollregion=self.studio_detail_canvas.bbox("all")))

        def _on_studio_detail_canvas_configure(event):
            canvas_width = event.width
            if self.studio_detail_canvas and self.studio_detail_canvas.winfo_exists():
                self.studio_detail_canvas.itemconfig(studio_canvas_window_id, width=canvas_width)
            if self.studio_detail_view_instance and self.studio_detail_view_instance.winfo_exists():
                 self.studio_detail_view_instance.after_idle(lambda w=canvas_width: self.studio_detail_view_instance._update_wraplengths(container_width=w))

        if self.studio_detail_view_instance: self.studio_detail_view_instance.bind("<Configure>", _on_studio_detail_frame_configure)
        if self.studio_detail_canvas: self.studio_detail_canvas.bind('<Configure>', _on_studio_detail_canvas_configure)
        self.studio_detail_area_frame.after(50, _on_studio_detail_frame_configure)

        self.title(f"Студія: {studio_name}")

    def _fetch_and_set_user_info(self):
        """Fetches current user's info and updates instance variables"""
        self.developer_contact_email = None
        if self.current_user_id and self.db_manager:
            user_data = self.db_manager.fetch_user_info(self.current_user_id)
            developer_status = self.db_manager.check_developer_status(self.current_user_id)

            if user_data:
                self.username = user_data.get('username', "User")
                self.current_balance = user_data.get('balance', decimal.Decimal('0.00'))
                self.is_developer = developer_status
                print(f"StoreWindow: User info set - {self.username}, Balance: {self.current_balance}, Is Developer: {self.is_developer}")
                if self.is_developer:
                    dev_info_query = "SELECT contact_email FROM Developers WHERE user_id = %s;"
                    dev_result = self.db_manager.execute_query(dev_info_query, (self.current_user_id,), fetch_one=True)
                    if dev_result:
                        self.developer_contact_email = dev_result[0]
                        print(f"StoreWindow: Developer contact email: {self.developer_contact_email}")
                    else:
                         print(f"StoreWindow: Warning - Could not fetch developer contact email for user {self.current_user_id}.")

            else:
                print("StoreWindow: Failed to fetch user info.")
                self.username = "Error"
                self.current_balance = decimal.Decimal('0.00')
                self.is_developer = False
        else:
             print("StoreWindow: Cannot fetch user info - user_id or db_manager missing.")
             self.is_developer = False
             self.username = "N/A"
             self.current_balance = decimal.Decimal('0.00')
            
    def _create_user_info_panel(self, parent):
        """Creates the user info panel with username, balance, and dropdown arrow"""
        panel_bg = self.colors.get('user_panel_bg', '#ededed')
        panel_fg = self.colors.get('user_panel_text_fg', 'black')

        frame = tk.Frame(parent, bg=panel_bg, relief=tk.SOLID, borderwidth=1, padx=5, pady=2)

        self.username_label = tk.Label(frame, text=self.username,
                                  font=self.fonts['ui'],
                                  fg=panel_fg,
                                  bg=frame['bg'], cursor="hand2")
        self.username_label.pack(side=tk.LEFT, padx=(5, 2))
        self.username_label.bind("<Button-1>", self._on_dropdown_click)

        arrow_fg = '#555555'
        self.arrow_label = tk.Label(frame, text="▼", font=(self.fonts['ui'][0], 8),
                               fg=arrow_fg,
                               bg=frame['bg'], cursor="hand2")
        self.arrow_label.pack(side=tk.LEFT, padx=(0, 8))
        self.arrow_label.bind("<Button-1>", self._on_dropdown_click)

        self.balance_label = tk.Label(frame, text=f"{self.current_balance:.2f}₴",
                                      font=self.fonts['ui'],
                                      fg=panel_fg,
                                      bg=frame['bg'])
        self.balance_label.pack(side=tk.LEFT, padx=(0, 0))

        for widget in frame.winfo_children():
            widget.bind("<MouseWheel>", self._on_mousewheel)
            widget.bind("<Button-4>", self._on_mousewheel)
            widget.bind("<Button-5>", self._on_mousewheel)

        return frame
    
    def update_developer_status(self, new_status: bool):
        """Updates the internal developer status flag and refreshes UI elements if status changed"""
        print(f"StoreWindow: Received developer status update. New status: {new_status}")
        if self.is_developer != new_status:
            self.is_developer = new_status
            self.refresh_user_info_display()

    def refresh_current_tab(self):
        active_view = None
        if self.detail_view_instance and self.detail_area_frame and self.detail_area_frame.winfo_ismapped():
            active_view = 'game_detail'
            print("Refreshing Game Detail View...")
            game_id = self.detail_view_instance.game_id
            self._show_detail_view(game_id)
        elif self.studio_detail_view_instance and self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_ismapped():
            active_view = 'studio_detail'
            print("Refreshing Studio Detail View...")
            if hasattr(self.studio_detail_view_instance, 'studio_name'):
                 studio_name = self.studio_detail_view_instance.studio_name
                 self._show_studio_detail_view(studio_name)
            else:
                 print("Cannot refresh studio details: studio_name not found in instance.")
                 self._show_notebook_view()
        elif self.notebook.winfo_ismapped():
            active_view = 'notebook'
            try:
                selected_tab_index = self.notebook.index(self.notebook.select())
                tab_name = self.notebook.tab(selected_tab_index, "text")
                print(f"Refreshing tab: Index {selected_tab_index}, Name '{tab_name}'")

                if tab_name == 'Магазин':
                    print("Refreshing Store Tab (re-fetching and sorting)...")
                    self.load_games_store()
                elif tab_name == 'Бібліотека':
                    print("Refreshing Library Tab...")
                    if hasattr(self, 'library_view') and self.library_view:
                        self.library_view.load_library_games()
                elif tab_name == 'Студії':
                    print("Refreshing Studios Tab...")
                    if self.studios_tab_instance:
                        self.studios_tab_instance.refresh_content()
                elif tab_name == 'Майстерня':
                     print("Refreshing Workshop Tab...")
                     self._setup_workshop_tab()
                elif tab_name == 'Адмін-панель' and self.is_app_admin:
                    if hasattr(self, 'admin_notebook') and self.admin_notebook.winfo_exists():
                        try: 
                            admin_current_tab_idx = self.admin_notebook.index(self.admin_notebook.select())
                            admin_tab_name = self.admin_notebook.tab(admin_current_tab_idx, "text")
                            if admin_tab_name == 'Користувачі' and self.admin_user_management_panel_instance:
                                self.admin_user_management_panel_instance.refresh_panel_content()
                            elif admin_tab_name == 'Студії' and self.admin_studio_management_panel_instance:
                                self.admin_studio_management_panel_instance.refresh_panel_content()
                            elif admin_tab_name == 'Ігри' and self.admin_game_management_panel_instance:
                                self.admin_game_management_panel_instance.refresh_panel_content()
                            elif admin_tab_name == 'Сповіщення' and self.admin_notifications_panel_instance: 
                                self.admin_notifications_panel_instance.refresh_panel_content()
                        except tk.TclError:
                            print("Admin panel sub-tab not selected or notebook not ready for refresh.")
                self.refresh_user_info_display()
            except tk.TclError:
                print("Could not get selected tab (Notebook might not be visible).")
                self.refresh_user_info_display()
            except AttributeError as e:
                print(f"Error refreshing tab: {e}")
                traceback.print_exc()
                self.refresh_user_info_display()
        else:
             print("No active view identified to refresh.")
             self.refresh_user_info_display()

    def _on_dropdown_click(self, event=None):
        """Handles clicks on the username or dropdown arrow to show the user menu"""
        if self.user_dropdown_menu:
            try:
                self.user_dropdown_menu.unpost()
                self.user_dropdown_menu = None
            except tk.TclError:
                self.user_dropdown_menu = None
            return "break"

        print("Clicked on dropdown arrow/username - creating menu")
        self.user_dropdown_menu = tk.Menu(self, tearoff=0)

        self.user_dropdown_menu.add_command(label="Видалити акаунт", command=self._delete_account, foreground="red")
        self.user_dropdown_menu.add_command(label="Вийти", command=self._logout)
        
        self.user_dropdown_menu.bind("<Unmap>", self._on_menu_unmap, add='+')

        widget = event.widget
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        try:
            self.user_dropdown_menu.tk_popup(x, y)
        except tk.TclError as e:
             print(f"Error showing popup menu: {e}")
             self.user_dropdown_menu = None

        return "break"
             
    def _on_menu_unmap(self, event=None):
        """Callback when the user dropdown menu is closed"""
        if event is None or event.widget == self.user_dropdown_menu:
             self.user_dropdown_menu = None
                
    def _logout(self):
        """Logs out the current user and returns to the login screen"""
        if messagebox.askyesno("Вихід", "Ви впевнені, що хочете вийти з акаунту?", parent=self):
            print("Logging out...")
            self.destroy()
            if self.open_login_callback:
                self.open_login_callback()
            else:
                print("Error: Login callback function is not set in StoreWindow.")
                messagebox.showerror("Помилка", "Не вдалося повернутися до вікна входу.")

    def _delete_account(self):
        """Handles the process of deleting the current user's account"""
        if self.is_app_admin:
            messagebox.showerror(
                "Дія заборонена",
                "Ви не можете видалити акаунт адміністратора додатку.\n"
                "Для цього зверніться до розробників системи або іншого адміністратора.",
                parent=self
            )
            print(f"Attempt to delete app admin account {self.username} (ID: {self.current_user_id}) was blocked.")
            return

        if self.is_developer:
            messagebox.showerror(
                "Дія неможлива",
                "Ви не можете видалити акаунт, маючи статус розробника.\n"
                "Будь ласка, спочатку відмовтеся від статусу розробника у вкладці 'Майстерня'.",
                parent=self
            )
            print(f"Attempt to delete developer account {self.username} (ID: {self.current_user_id}) was blocked.")
            return

        print(f"Attempting to delete account for user: {self.username} (ID: {self.current_user_id})")
        
        confirm1 = messagebox.askyesno(
            "Видалення Акаунту",
            f"ПОПЕРЕДЖЕННЯ!\n\nВи впевнені, що хочете видалити акаунт '{self.username}'?\n\n"
            "ЦЯ ДІЯ НЕЗВОРОТНЯ!\n"
            "Будуть видалені всі ваші покупки, рецензії та коментарі.",
            icon='warning',
            parent=self
        )

        if not confirm1:
            print("Account deletion cancelled (first confirmation).")
            return

        try:
            entered_username = simpledialog.askstring(
                "Підтвердження Видалення",
                f"Для підтвердження видалення акаунту '{self.username}', "
                "будь ласка, введіть ваше ім'я користувача ще раз:",
                parent=self
            )
        except Exception as e:
             print(f"Error showing confirmation dialog: {e}")
             return

        if entered_username is None:
             print("Account deletion cancelled (second confirmation - Cancel button).")
             return

        if entered_username != self.username:
            print("Account deletion cancelled (second confirmation - wrong username).")
            messagebox.showerror("Помилка", "Введене ім'я користувача не співпадає. Видалення скасовано.", parent=self)
            return

        print(f"Proceeding with account deletion for user: {self.username} (ID: {self.current_user_id})")
        success = False
        try:
            success = self.db_manager.delete_user_account(self.current_user_id)
        except AttributeError:
             messagebox.showerror("Помилка", "Функція видалення акаунту не реалізована в DB Manager.", parent=self)
             return
        except Exception as e:
             print(f"UI Error calling delete_user_account: {e}")
             traceback.print_exc()
             messagebox.showerror("Неочікувана Помилка", f"Сталася неочікувана помилка під час спроби видалення:\n{e}", parent=self)
             return

        if success:
            messagebox.showinfo("Успіх", f"Акаунт '{self.username}' було успішно видалено.", parent=self)
            print("Scheduling logout after account deletion...")

            if self.user_dropdown_menu:
                try:
                    self.user_dropdown_menu.unpost()
                except tk.TclError:
                    pass
                self.user_dropdown_menu = None

            if self.open_login_callback:
                self.after(10, self.open_login_callback)
            else:
                 print("Error: Login callback function is not set in StoreWindow.")
                 self.after(10, self.destroy)
                 return
            self.after(20, self.destroy)
        else:
            print(f"Failed to delete account for user: {self.username} (ID: {self.current_user_id})")

    def _create_sort_panel(self, parent):
        """Creates the sorting panel with criteria and order comboboxes"""
        frame = tk.Frame(parent, bg=self.original_bg)

        disabled_fg = '#777777'

        self.sort_by_label = tk.Label(
            frame,
            text="Сортувати за:",
            bg=self.original_bg,
            font=self.fonts['ui'],
            takefocus=0,
            highlightthickness=0
        )
        self.sort_by_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='w')

        self.sort_criteria_combobox = ttk.Combobox(
            frame, values=["Назвою", "Ціною"], state="readonly", width=10, font=self.fonts['ui']
        )
        self.sort_criteria_combobox.set("Назвою")
        self.sort_criteria_combobox.grid(row=0, column=1, padx=(0, 15), pady=5, sticky='w')

        self.order_label = tk.Label(
            frame,
            text="Порядок:",
            bg=self.original_bg,
            font=self.fonts['ui'],
            takefocus=0,
            highlightthickness=0
        )
        self.order_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky='w')

        self.sort_order_combobox = ttk.Combobox(
            frame, values=["За зростанням", "За спаданням"], state="readonly", width=15, font=self.fonts['ui']
        )
        self.sort_order_combobox.set("За зростанням")
        self.sort_order_combobox.grid(row=0, column=3, padx=(0, 0), pady=5, sticky='w')

        def handle_selection(event):
            self._on_sort_change(event)
            event.widget.master.focus_set()
            self.after(1, self._reset_sort_label_bg)

        self.sort_criteria_combobox.bind("<<ComboboxSelected>>", handle_selection)
        self.sort_order_combobox.bind("<<ComboboxSelected>>", handle_selection)

        return frame
          
    def _reset_sort_label_bg(self):
        """Resets the background color of sort labels"""
        try:
            if hasattr(self, 'sort_by_label') and self.sort_by_label.winfo_exists():
                self.sort_by_label.config(bg=self.original_bg)
            if hasattr(self, 'order_label') and self.order_label.winfo_exists():
                self.order_label.config(bg=self.original_bg)
        except tk.TclError:
            pass
    
    def _on_sort_change(self, event=None):
        """Handles changes in the sorting comboboxes and reloads the store list"""
        criteria_map = {"Назвою": "title", "Ціною": "price"}
        order_map = {"За зростанням": False, "За спаданням": True}

        selected_criteria = self.sort_criteria_combobox.get()
        selected_order = self.sort_order_combobox.get()

        self.current_sort_key = criteria_map.get(selected_criteria, 'title')
        self.current_sort_reverse = order_map.get(selected_order, False)

        print(f"Sort selection changed to: Key='{self.current_sort_key}', Reverse={self.current_sort_reverse}. Reloading games...")
        self.load_games_store()

    def _setup_workshop_tab(self):
        for widget in self.workshop_tab_frame.winfo_children():
            widget.destroy()

        self.workshop_tab_frame.grid_columnconfigure(0, weight=1)
        self.workshop_tab_frame.grid_rowconfigure(0, weight=1)
        self.workshop_tab_frame.grid_rowconfigure(2, weight=1)

        content_frame = tk.Frame(self.workshop_tab_frame, bg=self.original_bg)
        content_frame.grid(row=1, column=0, sticky='')

        if self.is_developer:
            title_text = "Майстерня розробника"
            if self.is_app_admin:
                title_text += " (Адміністратор)"

            info_label = tk.Label(content_frame, text=title_text,
                                 font=self.fonts.get('title', ("Verdana", 16, "bold")),
                                 bg=self.original_bg)
            info_label.pack(pady=10)

            dev_info_text = "Тут ви зможете керувати своїми ігровими проєктами, \nподавати ігри на розгляд та взаємодіяти зі спільнотою."
            if self.is_app_admin:
                dev_info_text += "\n\nЯк адміністратор, ви маєте доступ до всіх функцій розробника."

            developer_specific_info_label = tk.Label(content_frame,
                                 text=dev_info_text,
                                 font=self.fonts.get('detail', ("Verdana", 11)),
                                 bg=self.original_bg, justify=tk.CENTER, wraplength=500)
            developer_specific_info_label.pack(pady=(10, 15))

            developer_studio_info = None
            if self.current_user_id and self.db_manager:
                 try:
                      developer_studio_info = self.db_manager.get_developer_studio_details(self.current_user_id)
                 except AttributeError:
                      print("Warning: db_manager.get_developer_studio_details method not found.")
                 except Exception as e:
                      print(f"Error fetching developer studio details: {e}")


            if developer_studio_info and developer_studio_info.get('studio_id'):
                studio_name = developer_studio_info.get('studio_name', 'Невідома студія')
                studio_info_frame = tk.Frame(content_frame, bg=self.original_bg)
                studio_info_frame.pack(pady=(5,10))

                studio_label_text = f"Ви є учасником студії: {studio_name}"
                studio_label = tk.Label(studio_info_frame, text=studio_label_text,
                                         font=self.fonts.get('detail', ("Verdana", 10)),
                                         bg=self.original_bg)
                studio_label.pack(side=tk.LEFT, padx=(0, 10))

                leave_studio_button = ttk.Button(studio_info_frame, text="Покинути студію",
                                                 command=self._prompt_leave_studio,
                                                 style=self.custom_button_style)
                leave_studio_button.pack(side=tk.LEFT)

            if not self.is_app_admin:
                if not (developer_studio_info and developer_studio_info.get('studio_id')):
                    revoke_dev_status_button = ttk.Button(content_frame, text="Відмовитися від статусу розробника",
                                                   command=self._prompt_revoke_developer_status,
                                                   style=self.custom_button_style)
                    revoke_dev_status_button.pack(pady=(10,15))
                else:
                    revoke_info_label = tk.Label(content_frame,
                                              text="(Щоб відмовитися від статусу розробника, спочатку покиньте студію)",
                                              font=self.fonts.get('comment', ("Verdana", 9)),
                                              fg="grey", bg=self.original_bg)
                    revoke_info_label.pack(pady=(0, 15))
        else:
            title_label = tk.Label(content_frame, text="Стати розробником",
                                  font=self.fonts.get('title', ("Verdana", 16, "bold")),
                                  bg=self.original_bg)
            title_label.pack(pady=(0, 15))

            info_text = (
                "Станьте розробником на нашій платформі!\n\n"
                "Отримайте доступ до інструментів для публікації ваших ігор та приєднуйтесь до спільноти творців.\n"
                "Щоб отримати статус розробника, натисніть кнопку нижче та надайте вашу контактну електронну пошту. "
                "Вона може бути використана для зв'язку щодо ваших проєктів або співпраці зі студіями."
            )
            info_label = tk.Label(content_frame,
                                 text=info_text,
                                 font=self.fonts.get('detail', ("Verdana", 11)),
                                 bg=self.original_bg, justify=tk.CENTER, wraplength=550)
            info_label.pack(pady=15)

            request_dev_status_button = ttk.Button(content_frame, text="Подати запит на статус розробника",
                                           command=self._prompt_formal_developer_request,
                                           style=self.custom_button_style)
            request_dev_status_button.pack(pady=(10,15))

    def _prompt_become_developer_from_workshop(self):
        if self.is_app_admin:
            messagebox.showinfo(
                "Статус адміністратора",
                "Ви є адміністратором додатку і вже маєте розширені права.\n"
                "Отримання окремого статусу розробника не потрібне.",
                parent=self
            )
            return

        if self.is_developer:
            messagebox.showinfo("Статус розробника", "Ви вже є розробником.", parent=self)
            return
        
        dialog_prompt = (
            "Будь ласка, введіть вашу робочу електронну пошту.\n"
            "Вона може бути використана для зв'язку зі студіями або адміністрацією.\n\n"
            "Ваша основна пошта акаунту залишиться незмінною."
        )
        dialog = CustomAskStringDialog(self, title="Стати розробником", prompt=dialog_prompt)
        contact_email = dialog.result

        if contact_email is not None:
             contact_email = contact_email.strip()
             if not contact_email:
                 messagebox.showwarning("Помилка", "Ви не ввели електронну пошту.", parent=self)
                 return
             if "@" not in contact_email or "." not in contact_email.split('@')[-1]:
                  messagebox.showwarning("Помилка", "Будь ласка, введіть дійсну адресу електронної пошти.", parent=self)
                  return

             confirm = messagebox.askyesno("Підтвердження",
                                        f"Ви впевнені, що хочете отримати статус розробника?\n"
                                        f"Контактна пошта розробника буде встановлена як:\n{contact_email}",
                                        parent=self)

             if confirm:
                 print(f"StoreWindow (Workshop): User ID {self.current_user_id} confirmed becoming a developer with contact email: {contact_email}.")
                 success = False
                 try:
                     success = self.db_manager.set_developer_status(
                         self.current_user_id,
                         status=True,
                         contact_email=contact_email
                     )
                 except TypeError as te:
                      if 'contact_email' in str(te) or "unexpected keyword argument 'contact_email'" in str(te):
                          messagebox.showerror("Помилка Програми", "Помилка: Метод set_developer_status не оновлено для прийому contact_email.", parent=self)
                          print("!!! PROGRAM ERROR: db_manager.set_developer_status needs 'contact_email' argument or handling !!!")
                          return
                      else:
                          messagebox.showerror("Помилка Типу", f"Помилка під час виклику функції розробника:\n{te}", parent=self)
                          traceback.print_exc()
                          return
                 except AttributeError:
                     messagebox.showerror("Помилка", "Функція зміни статусу розробника не реалізована в DB Manager.", parent=self)
                     return
                 except Exception as e:
                      messagebox.showerror("Помилка Бази Даних", f"Не вдалося оновити статус:\n{e}", parent=self)
                      traceback.print_exc()
                      return

                 if success:
                     messagebox.showinfo("Успіх", "Вітаємо! Ви отримали статус розробника.", parent=self)
                     self.update_developer_status(True) 
                     self._setup_workshop_tab() 
                 else:
                     print("StoreWindow (Workshop): Failed to set developer status in DB (error message should have been shown by DBManager).")
        else:
             print("StoreWindow (Workshop): Becoming developer cancelled by user.")
             
    def refresh_user_info_display(self):
        """Refreshes the user info panel and potentially the Workshop tab"""
        print("StoreWindow: Refreshing user info display...")
        self._fetch_and_set_user_info()

        if hasattr(self, 'username_label') and self.username_label and self.username_label.winfo_exists():
            self.username_label.config(text=self.username)
        else:
            print("StoreWindow: Username label not found or destroyed, cannot update.")

        if hasattr(self, 'balance_label') and self.balance_label and self.balance_label.winfo_exists():
            self.balance_label.config(text=f"{self.current_balance:.2f}₴")
        else:
             print("StoreWindow: Balance label not found or destroyed, cannot update.")

        current_tab_name = None
        try:
            if self.notebook.winfo_exists() and self.notebook.winfo_ismapped():
                current_tab_name = self.notebook.tab(self.notebook.select(), "text")
        except tk.TclError:
             pass

        if hasattr(self, 'workshop_tab_frame') and self.workshop_tab_frame.winfo_exists():
             if current_tab_name == 'Майстерня':
                  print("StoreWindow: Refreshing workshop tab as part of user info refresh (because it's active).")
                  self._setup_workshop_tab()
                  
    def _prompt_formal_developer_request(self):
        if self.is_app_admin:
            messagebox.showinfo("Інформація", "Адміністратори вже мають розширені права.", parent=self)
            return
        if self.is_developer:
            messagebox.showinfo("Інформація", "Ви вже є розробником.", parent=self)
            return

        dialog_prompt = (
            "Будь ласка, введіть вашу робочу електронну пошту для цього запиту.\n"
            "Вона буде розглянута адміністратором.\n"
            "Ваша основна пошта акаунту залишиться незмінною."
        )
        dialog = CustomAskStringDialog(self, title="Запит на статус розробника", prompt=dialog_prompt)
        contact_email = dialog.result

        if contact_email is not None:
             contact_email = contact_email.strip()
             if not contact_email:
                 messagebox.showwarning("Помилка", "Ви не ввели електронну пошту.", parent=self)
                 return
             if "@" not in contact_email or "." not in contact_email.split('@')[-1]:
                  messagebox.showwarning("Помилка", "Будь ласка, введіть дійсну адресу електронної пошти.", parent=self)
                  return
            
             if messagebox.askyesno("Підтвердження запиту",
                                    f"Надіслати запит на отримання статусу розробника з контактною поштою:\n{contact_email}\n\nВаш запит буде розглянуто адміністратором.",
                                    parent=self):
                
                success = self.db_manager.create_developer_status_request(self.current_user_id, contact_email)
                if success:
                    messagebox.showinfo("Запит надіслано", "Ваш запит на отримання статусу розробника було успішно надіслано та очікує на розгляд.", parent=self)
        else:
            print("Formal developer request cancelled by user.")
    
    def _prompt_revoke_developer_status(self):
        if not self.is_developer or self.is_app_admin :
            messagebox.showerror("Дія неможлива", "Ця дія доступна лише для розробників (не адміністраторів).", parent=self)
            return

        developer_studio_info = self.db_manager.get_developer_studio_details(self.current_user_id)
        if developer_studio_info and developer_studio_info.get('studio_id'):
             messagebox.showerror("Дія неможлива",
                                  "Ви не можете відмовитися від статусу розробника, будучи учасником студії.\n"
                                  "Будь ласка, спочатку покиньте студію.",
                                  parent=self)
             return

        if messagebox.askyesno("Відмова від статусу розробника",
                               "Ви впевнені, що хочете відмовитися від статусу розробника?\n"
                               "Ви втратите доступ до функцій розробника, але ваш акаунт та ігри залишаться.",
                               icon='warning', parent=self):

            success = self.db_manager.set_developer_status(self.current_user_id, status=False)
            if success:
                messagebox.showinfo("Статус оновлено", "Ви успішно відмовилися від статусу розробника.", parent=self)
                self._fetch_and_set_user_info()
                self._setup_workshop_tab()
                self.refresh_user_info_display()
                if self.studios_tab_instance:
                    self.studios_tab_instance.refresh_content()

    def _prompt_leave_studio(self):
        if not self.is_developer:
            messagebox.showinfo("Інформація", "Ця дія доступна лише для розробників.", parent=self)
            return

        developer_studio_info = self.db_manager.get_developer_studio_details(self.current_user_id)
        if not developer_studio_info or not developer_studio_info.get('studio_id'):
            messagebox.showinfo("Інформація", "Ви не є учасником жодної студії.", parent=self)
            return

        studio_name = developer_studio_info.get('studio_name', 'поточної студії')

        if messagebox.askyesno("Покинути студію",
                               f"Ви впевнені, що хочете покинути студію '{studio_name}'?\n"
                               "Ви втратите зв'язок зі студією, але ваш статус розробника залишиться.",
                               icon='warning', parent=self):
            success = self.db_manager.leave_studio(self.current_user_id)
            if success:
                messagebox.showinfo("Успіх", f"Ви успішно покинули студію '{studio_name}'.", parent=self)
                self._fetch_and_set_user_info()
                self._setup_workshop_tab()
                self.refresh_user_info_display()
                if self.studios_tab_instance:
                    self.studios_tab_instance.refresh_content()
    
    def on_close(self):
        """Handles the window close event"""
        self._image_references.clear()
        self.destroy()
        
    