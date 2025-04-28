import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from functools import partial
import decimal
import traceback

from .ui_utils import center_window
from .ui_library import LibraryTab
from .ui_game_details import GameDetailView
from .ui_studio_details import StudioDetailView

class StoreWindow(tk.Tk):
    def __init__(self, db_manager, user_id, image_folder, studio_logo_folder,
                 placeholder_image_path, placeholder_image_name):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = user_id
        self.username = "User"
        self.current_balance = decimal.Decimal('0.00')
        self._image_references = {}
        self.placeholder_image = None
        self.placeholder_image_detail = None
        self._game_widgets_store = []

        self.image_folder = image_folder
        self.studio_logo_folder = studio_logo_folder
        self.placeholder_image_path = placeholder_image_path
        self.placeholder_image_name = placeholder_image_name

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

        self.original_bg = "white"
        self.hover_bg = "#f0f0f0"
        self.listbox_select_bg = self.original_bg
        self.listbox_select_fg = "black"
        self.no_comments_fg = "grey"
        self.comment_fg = "black"
        self.no_comments_message = " Коментарів ще немає."

        self.list_icon_size = (64, 64)
        self.detail_icon_size = (160, 160)

        self.fonts = {
            'ui': ("Verdana", 10),
            'title': ("Verdana", 16, "bold"),
            'detail': ("Verdana", 11),
            'price': ("Verdana", 12),
            'comment': ("Verdana", 9),
            'description': ("Verdana", 10),
            'list_title': ("Verdana", 12, "bold"),
            'library_list_title': ("Verdana", 11, "bold"),
            'library_detail_title': ("Verdana", 14, "bold"),
            'review_author': ("Verdana", 9, "bold"),
            'review_text': ("Verdana", 9),
            'review_input': ("Verdana", 10),
            'section_header': ("Verdana", 12, "bold")
        }
        self.styles = {'custom_button': 'NoFocus.TButton'}
        self.colors = {
            'original_bg': self.original_bg,
            'hover_bg': self.hover_bg,
            'listbox_select_bg': self.listbox_select_bg,
            'listbox_select_fg': self.listbox_select_fg,
            'no_comments_fg': self.no_comments_fg,
            'comment_fg': self.comment_fg,
            'no_comments_message': self.no_comments_message,
            'no_reviews_message': " Рецензій ще немає.",
            'link_fg': 'blue',
            'placeholder_fg': 'grey',
            'date_fg': '#555555',
            'separator_fg': 'grey',
            'textbox_bg': 'white',
            'input_bg': 'white',
            'input_fg': 'black',
            'user_panel_text_fg': 'black',
            'user_panel_bg': '#e0e0e0',
            'username_fg': '#67c1f5'
        }

        self._load_placeholders(list_size=self.list_icon_size, detail_size=self.detail_icon_size)
        self._fetch_and_set_user_info()

        self.width = 950
        self.height = 700
        center_window(self, self.width, self.height)
        self.title("Universal Games")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        style = ttk.Style(self)
        try:
            theme_bg = style.lookup('TFrame', 'background')
            if theme_bg:
                self.original_bg = theme_bg
                self.colors['original_bg'] = theme_bg
            self.colors['user_panel_bg'] = '#ededed'
            self.configure(bg=self.original_bg)

            self.custom_button_style = 'NoFocus.TButton'
            style.configure(self.custom_button_style, focuscolor=style.lookup('TButton', 'background'))
            style.configure('TNotebook', background=self.original_bg)
            style.configure('TNotebook.Tab', font=self.fonts['ui'], padding=[5, 2], background=self.original_bg, lightcolor=self.original_bg, bordercolor=self.original_bg)
            style.map('TNotebook.Tab',
                      background=[('selected', self.original_bg)],
                      focuscolor=[('focus', style.lookup('TNotebook', 'background'))])
            style.configure('TFrame', background=self.original_bg)
            style.configure('TPanedwindow', background=self.original_bg)
            style.configure('Vertical.TScrollbar', background=self.original_bg)

        except tk.TclError as e:
            print(f"Помилка налаштування стилів ttk: {e}. Defaulting background.")
            self.original_bg = "white"
            self.colors['original_bg'] = self.original_bg
            self.colors['user_panel_bg'] = '#ededed'
            self.custom_button_style = 'TButton'
            self.configure(bg=self.original_bg)


        top_bar_frame = tk.Frame(self, bg=self.original_bg)
        top_bar_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        top_bar_frame.grid_columnconfigure(0, weight=1)
        top_bar_frame.grid_columnconfigure(1, weight=0)

        app_title_label = tk.Label(top_bar_frame, text="Universal Games", font=("Verdana", 18, "bold"), bg=top_bar_frame['bg'])
        app_title_label.grid(row=0, column=0, pady=(10,5), sticky='w', padx=10)

        self.user_info_frame = self._create_user_info_panel(top_bar_frame)
        self.user_info_frame.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.bind("<FocusIn>", self._unfocus_notebook)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky='nsew')

        self.store_tab_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.store_tab_frame, text='Магазин')
        self.store_tab_frame.grid_rowconfigure(0, weight=1)
        self.store_tab_frame.grid_columnconfigure(0, weight=1)
        self.store_canvas, self.store_list_frame = self._create_scrollable_list_frame(self.store_tab_frame, self.original_bg)

        self.library_tab_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.library_tab_frame, text='Бібліотека')
        self.library_view = LibraryTab(
             parent=self.library_tab_frame, db_manager=self.db_manager, user_id=self.current_user_id,
             image_cache=self._image_references, placeholder_list=self.placeholder_image,
             placeholder_detail=self.placeholder_image_detail,
             image_folder_path=self.image_folder,
             fonts=self.fonts, colors=self.colors
        )
        self.library_view.paned_window.pack(fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(self, text="Оновити", command=self.refresh_current_tab, style=self.custom_button_style)
        refresh_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_games_store()

        self.bind_all("<MouseWheel>", self._on_mousewheel, add='+')
        self.bind_all("<Button-4>", self._on_mousewheel, add='+')
        self.bind_all("<Button-5>", self._on_mousewheel, add='+')
        self.bind_all("<Button-1>", self._on_global_click, add='+')

    def _unfocus_notebook(self, event):
        self.focus_set()
        self.after_idle(lambda: self.notebook.tk_focusNext().focus_set() if self.notebook.winfo_ismapped() else None)

    def _create_scrollable_list_frame(self, parent, bg_color):
        canvas_scrollbar_frame = tk.Frame(parent, bg=bg_color)
        canvas_scrollbar_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        canvas_scrollbar_frame.grid_rowconfigure(0, weight=1)
        canvas_scrollbar_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, background=bg_color)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def _on_inner_frame_configure(event=None):
             canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_inner_canvas_configure(event):
             canvas_width = event.width
             canvas.itemconfig(canvas_frame_id, width=canvas_width)
             inner_frame.config(width=canvas_width)
             canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_inner_mousewheel(event):
            if event.num == 4: delta = -1
            elif event.num == 5: delta = 1
            else:
                try: delta = -1 if event.delta > 0 else 1
                except AttributeError: return
            canvas.yview_scroll(delta, "units")
            return "break"

        inner_frame.bind("<Configure>", _on_inner_frame_configure)
        canvas.bind('<Configure>', _on_inner_canvas_configure)

        for widget in [canvas, inner_frame]:
            widget.bind("<MouseWheel>", _on_inner_mousewheel)
            widget.bind("<Button-4>", _on_inner_mousewheel)
            widget.bind("<Button-5>", _on_inner_mousewheel)

        return canvas, inner_frame

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
                if selected_tab_index == 0:
                    print("Refreshing Store Tab...")
                    self.load_games_store()
                elif selected_tab_index == 1:
                    print("Refreshing Library Tab...")
                    if hasattr(self, 'library_view') and self.library_view:
                        self.library_view.load_library_games()
                    else:
                        print("Library view not initialized or available.")
                self.refresh_user_info_display()
            except tk.TclError:
                print("Could not get selected tab (Notebook might not be visible).")
            except AttributeError as e:
                print(f"Error refreshing tab: {e}")
                traceback.print_exc()
        else:
             print("No active view identified to refresh.")
             self.refresh_user_info_display()

    def _show_notebook_view(self):
        if self.detail_area_frame:
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_back_button = None
            self.detail_frame_container = None
            self.detail_canvas = None
            self.detail_scrollbar = None
            self.detail_view_instance = None
        if self.studio_detail_area_frame:
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_back_button = None
            self.studio_detail_frame_container = None
            self.studio_detail_canvas = None
            self.studio_detail_scrollbar = None
            self.studio_detail_view_instance = None

        self.notebook.grid(row=1, column=0, sticky='nsew')
        self.title("Universal Games")
        
    def _show_detail_view(self, game_id, event=None):
        self.notebook.grid_remove()
        if self.studio_detail_area_frame:
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_view_instance = None

        if self.detail_area_frame:
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_view_instance = None

        try:
            game_details = self.db_manager.fetch_game_details(game_id)
            if not game_details:
                messagebox.showwarning("Не знайдено", f"Гра з ID {game_id} не знайдена.")
                self._show_notebook_view(); return
        except AttributeError:
             messagebox.showerror("Помилка", "Функція отримання деталей гри ще не реалізована в DB Manager.")
             self._show_notebook_view(); return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі гри:\n{e}")
            traceback.print_exc()
            self._show_notebook_view(); return

        self.detail_area_frame = tk.Frame(self, bg=self.original_bg)
        self.detail_area_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')# columnspan = 2
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

        if self.detail_view_instance:
            self.detail_view_instance.bind("<Configure>", _on_detail_frame_configure)
        if self.detail_canvas:
            self.detail_canvas.bind('<Configure>', _on_detail_canvas_configure)

        self.title(f"{game_details.get('title', 'Деталі гри')}")

    def _load_placeholders(self, list_size=(64, 64), detail_size=(160, 160)):
        print("Loading placeholders...")
        if self.placeholder_image_path and os.path.exists(self.placeholder_image_path):
            self.placeholder_image = self._load_image_internal(
                self.placeholder_image_name, self.placeholder_image_path, size=list_size, is_placeholder=True
            )
            detail_placeholder_key = f"{self.placeholder_image_name}_detail_{detail_size[0]}x{detail_size[1]}"
            self.placeholder_image_detail = self._load_image_internal(
                detail_placeholder_key, self.placeholder_image_path, size=detail_size, is_placeholder=True
            )

            if self.placeholder_image: print(f"List placeholder loaded ({list_size}): {self.placeholder_image}")
            else: print(f"Failed to load list placeholder ({list_size}).")

            if self.placeholder_image_detail: print(f"Detail placeholder loaded ({detail_size}): {self.placeholder_image_detail}")
            else:
                print(f"Failed to load detail placeholder ({detail_size}).")
                if self.placeholder_image:
                    print("Using list placeholder for detail view as fallback.")
                    self.placeholder_image_detail = self.placeholder_image
                else:
                    print("Warning: Both list and detail placeholders failed to load.")
                    self.placeholder_image_detail = None
        else:
            print(f"Placeholder image file not found or path not set: {self.placeholder_image_path}")
            self.placeholder_image = None
            self.placeholder_image_detail = None

    def _load_image_internal(self, cache_key_base, full_path, size=(64, 64), is_placeholder=False):
        default_placeholder = None
        if not is_placeholder:
             default_placeholder = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image

        cache_key = f"{cache_key_base}_{size[0]}x{size[1]}"
        if cache_key in self._image_references: return self._image_references[cache_key]
        if not cache_key_base: return default_placeholder

        if full_path and os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                if img.mode != 'RGBA': img = img.convert('RGBA')
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self._image_references[cache_key] = photo_img
                return photo_img
            except Exception as e:
                print(f"Error loading image '{full_path}' (key: {cache_key}). Using default placeholder. Error: {e}")
                self._image_references[cache_key] = default_placeholder
                return default_placeholder
        else:
             if not is_placeholder:
                 print(f"Image file not found: {full_path} (key: {cache_key}). Using default placeholder.")
             self._image_references[cache_key] = default_placeholder
             return default_placeholder


    def _get_image(self, image_filename, size=(64, 64)):
        placeholder_to_return = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image
        if not image_filename: return placeholder_to_return

        folder = self.image_folder
        if folder is None:
             print("GetImage: IMAGE_FOLDER is not set, cannot load image.")
             return placeholder_to_return

        full_path = os.path.join(folder, image_filename)
        is_placeholder_request = (image_filename == self.placeholder_image_name)

        return self._load_image_internal(image_filename, full_path, size=size, is_placeholder=is_placeholder_request)
    
    def _on_mousewheel(self, event):
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
                if current_tab_index == 0:
                     if widget_under_cursor.winfo_exists():
                        try:
                            is_child = str(self.store_list_frame.winfo_parent()) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id()))
                            if is_child: target_canvas = self.store_canvas
                        except tk.TclError: pass
                elif current_tab_index == 1:
                     if hasattr(self, 'library_view') and hasattr(self.library_view, 'library_canvas'):
                         if widget_under_cursor.winfo_exists():
                             try:
                                is_child = str(self.library_view.library_list_frame.winfo_parent()) in str(widget_under_cursor.winfo_pathname(widget_under_cursor.winfo_id()))
                                if is_child: target_canvas = self.library_view.library_canvas
                             except tk.TclError: pass
            except (tk.TclError, AttributeError): pass
        else: return

        if not target_canvas or not target_canvas.winfo_exists(): return

        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return

        target_canvas.yview_scroll(delta, "units")
        return "break"

    def _on_enter(self, event, frame, icon_widget=None):
        try:
            if frame.winfo_exists():
                frame.config(background=self.hover_bg)
                for widget in frame.winfo_children():
                     if widget == icon_widget: continue
                     if isinstance(widget, (tk.Label, tk.Frame)):
                         if widget.winfo_exists(): widget.config(background=self.hover_bg)
                         if isinstance(widget, tk.Frame):
                             for grandchild in widget.winfo_children():
                                 if isinstance(grandchild, tk.Label):
                                     if grandchild.winfo_exists(): grandchild.config(background=self.hover_bg)
        except tk.TclError: pass

    def _on_leave(self, event, frame, icon_widget=None):
        try:
             if frame.winfo_exists():
                frame.config(background=self.original_bg)
                for widget in frame.winfo_children():
                     if widget == icon_widget: continue
                     if isinstance(widget, (tk.Label, tk.Frame)):
                          if widget.winfo_exists(): widget.config(background=self.original_bg)
                          if isinstance(widget, tk.Frame):
                              for grandchild in widget.winfo_children():
                                  if isinstance(grandchild, tk.Label):
                                      if grandchild.winfo_exists(): grandchild.config(background=self.original_bg)
        except tk.TclError: pass

    def _create_game_entry(self, parent, game_data):
        try:
            if len(game_data) < 5:
                 print(f"Skipping game entry due to insufficient data: {game_data}")
                 return None
            game_id, title, _, price, image_filename = game_data[:5]
        except (ValueError, TypeError) as e:
            print(f"Error unpacking game data for store list: {game_data}, Error: {e}")
            return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.FLAT, background=self.original_bg)
        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_image(image_filename, size=self.list_icon_size)
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.fonts['ui'], width=int(self.list_icon_size[0]/8), height=int(self.list_icon_size[1]/16), relief="solid", borderwidth=1)
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        title_label = tk.Label(text_frame, text=title or "Без назви",
                               font=self.fonts['list_title'], anchor="w", justify=tk.LEFT, background=self.original_bg)
        title_label.pack(fill=tk.X, pady=(0, 2))

        price_text = "N/A"
        if price is None: price_text = "Ціна не вказана"
        elif isinstance(price, (int, float, decimal.Decimal)) and float(price) <= 0.0: price_text = "Безкоштовно"
        else:
            try:
                price_decimal = decimal.Decimal(str(price)).quantize(decimal.Decimal("0.01"))
                price_text = f"Ціна: {price_decimal}₴"
            except (ValueError, TypeError, decimal.InvalidOperation): price_text = "N/A"
        price_label = tk.Label(text_frame, text=price_text, font=self.fonts['ui'], anchor="w", justify=tk.LEFT, background=self.original_bg)
        price_label.pack(fill=tk.X)

        widgets_to_bind_hover_click = [entry_frame, icon_label, text_frame, title_label, price_label]
        click_handler = partial(self._show_detail_view, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        for widget in widgets_to_bind_hover_click:
            if widget and widget.winfo_exists():
                widget.bind("<Button-1>", click_handler)
                widget.bind("<Enter>", enter_handler)
                widget.bind("<Leave>", leave_handler)
                widget.config(cursor="hand2")

        return entry_frame
    
    def load_games_store(self):
        for widget in self.store_list_frame.winfo_children(): widget.destroy()
        self._game_widgets_store = []
        games_data = []
        try:
            games_data = self.db_manager.fetch_all_games()
        except AttributeError:
            messagebox.showerror("Помилка", "Функція fetch_all_games не реалізована в DB Manager.")
            tk.Label(self.store_list_frame, text="Помилка завантаження даних (DB)", fg="red", bg=self.original_bg).pack(pady=20)
            return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити список ігор:\n{e}")
            tk.Label(self.store_list_frame, text=f"Помилка бази даних:\n{e}", fg="red", wraplength=self.width-50, bg=self.original_bg).pack(pady=20)
            traceback.print_exc()
            return

        if games_data is None:
            print("DB: fetch_all_games returned None.")
            tk.Label(self.store_list_frame, text="Не вдалося отримати дані з бази даних.", fg="red", bg=self.original_bg).pack(pady=20)
            return

        if not games_data:
            tk.Label(self.store_list_frame, text="В магазині поки немає ігор.", font=self.fonts['ui'], bg=self.original_bg).pack(pady=20)
        else:
            print(f"Store: Displaying {len(games_data)} games.")
            for game in games_data:
                game_widget = self._create_game_entry(self.store_list_frame, game)
                if game_widget:
                    game_widget.pack(fill=tk.X, pady=2, padx=2)
                    self._game_widgets_store.append(game_widget)

        self.store_list_frame.update_idletasks()
        self.store_canvas.configure(scrollregion=self.store_canvas.bbox("all"))
        self.store_canvas.yview_moveto(0)


    def load_games_library(self):
        if hasattr(self, 'library_view') and self.library_view:
            print("Triggering library refresh from StoreWindow...")
            self.library_view.load_library_games()
        else:
            print("Warning: Library view is not initialized yet, cannot refresh.")

    def switch_to_tab(self, tab_name_or_id, data=None):
        try:
            if self.detail_area_frame and self.detail_area_frame.winfo_ismapped(): self._show_notebook_view()
            if self.studio_detail_area_frame and self.studio_detail_area_frame.winfo_ismapped(): self._show_notebook_view()
            self.notebook.select(tab_name_or_id)
        except tk.TclError as e:
            print(f"Error switching to tab '{tab_name_or_id}': {e}")
        except Exception as e:
            print(f"Unexpected error during tab switch: {e}")
            traceback.print_exc()
            
    def _show_studio_detail_view(self, studio_name):
        self.notebook.grid_remove()
        if self.detail_area_frame:
            self.detail_area_frame.destroy()
            self.detail_area_frame = None
            self.detail_view_instance = None

        if self.studio_detail_area_frame:
            self.studio_detail_area_frame.destroy()
            self.studio_detail_area_frame = None
            self.studio_detail_view_instance = None

        print(f"Attempting to show details for studio: {studio_name}")

        self.studio_detail_area_frame = tk.Frame(self, bg=self.original_bg)
        self.studio_detail_area_frame.grid(row=1, column=0, columnspan=2, sticky='nsew') 
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

        self.title(f"Студія: {studio_name}")

    def _fetch_and_set_user_info(self):
        if self.current_user_id and self.db_manager:
            user_data = self.db_manager.fetch_user_info(self.current_user_id)
            if user_data:
                self.username = user_data.get('username', "User")
                self.current_balance = user_data.get('balance', decimal.Decimal('0.00'))
                print(f"StoreWindow: User info set - {self.username}, Balance: {self.current_balance}")
            else:
                print("StoreWindow: Failed to fetch user info.")
                self.username = "Error"
                self.current_balance = decimal.Decimal('0.00')
        else:
            print("StoreWindow: Cannot fetch user info - user_id or db_manager missing.")
            
    def _create_user_info_panel(self, parent):
        panel_bg = self.colors.get('user_panel_bg', '#ededed')
        panel_fg = self.colors.get('user_panel_text_fg', 'black')

        frame = tk.Frame(parent, bg=panel_bg, relief=tk.SOLID, borderwidth=1, padx=5, pady=2)

        self.username_label = tk.Label(frame, text=self.username,
                                  font=self.fonts['ui'],
                                  fg=panel_fg,
                                  bg=frame['bg'], cursor="hand2")
        self.username_label.pack(side=tk.LEFT, padx=(5, 2))
        self.username_label.bind("<Button-1>", self._on_username_click)

        arrow_fg = '#555555'
        arrow_label = tk.Label(frame, text="▼", font=(self.fonts['ui'][0], 8),
                               fg=arrow_fg,
                               bg=frame['bg'], cursor="hand2")
        arrow_label.pack(side=tk.LEFT, padx=(0, 8))
        arrow_label.bind("<Button-1>", self._on_dropdown_click)

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

    def refresh_user_info_display(self):
        print("StoreWindow: Refreshing user info display...")
        self._fetch_and_set_user_info()
        if hasattr(self, 'username_label') and self.username_label.winfo_exists():
            self.username_label.config(text=self.username)
        if hasattr(self, 'balance_label') and self.balance_label.winfo_exists():
            self.balance_label.config(text=f"{self.current_balance:.2f}₴")
        print(f"StoreWindow: Display updated - {self.username}, Balance: {self.current_balance:.2f}₴")

    def _on_username_click(self, event=None):
        print(f"Clicked on username: {self.username}")
        messagebox.showinfo("Профіль", "Функція керування профілем ще не реалізована.", parent=self)

    def _on_dropdown_click(self, event=None):
        if self.user_dropdown_menu:
            try:
                self.user_dropdown_menu.unpost()
                self.user_dropdown_menu = None
            except tk.TclError:
                self.user_dropdown_menu = None
            return "break" # <-- Додано, щоб зупинити тут, якщо меню закрили

        print("Clicked on dropdown arrow - creating menu")
        self.user_dropdown_menu = tk.Menu(self, tearoff=0)
        self.user_dropdown_menu.add_command(label="Налаштування акаунту (неактивно)")
        self.user_dropdown_menu.add_command(label="Додати кошти (неактивно)")
        self.user_dropdown_menu.add_separator()
        self.user_dropdown_menu.add_command(label="Вийти (неактивно)")
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
        if event is None or event.widget == self.user_dropdown_menu:
             self.user_dropdown_menu = None

    def _on_global_click(self, event):
        if self.user_dropdown_menu:
            try:
                menu_x = self.user_dropdown_menu.winfo_rootx()
                menu_y = self.user_dropdown_menu.winfo_rooty()
                menu_width = self.user_dropdown_menu.winfo_width()
                menu_height = self.user_dropdown_menu.winfo_height()

                if not (menu_x <= event.x_root < menu_x + menu_width and
                        menu_y <= event.y_root < menu_y + menu_height):
                    self.user_dropdown_menu.unpost()
            except tk.TclError:
                self.user_dropdown_menu = None
            except Exception as e:
                print(f"Error in _on_global_click: {e}")
                self.user_dropdown_menu = None

    def on_close(self):
        self._image_references.clear()
        self.destroy()