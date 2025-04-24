import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from functools import partial
import decimal

from .ui_utils import center_window
from .ui_library import LibraryTab
from .ui_game_details import GameDetailView

class StoreWindow(tk.Tk):
    def __init__(self, db_manager, user_id, image_folder, placeholder_image_path, placeholder_image_name):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = user_id
        self._image_references = {}
        self.placeholder_image = None
        self.placeholder_image_detail = None
        self._game_widgets_store = []
        
        self.image_folder = image_folder
        self.placeholder_image_path = placeholder_image_path
        self.placeholder_image_name = placeholder_image_name

        self.detail_view_instance = None

        self.original_bg = "white"
        self.hover_bg = "#f0f0f0"
        self.listbox_select_bg = self.original_bg
        self.listbox_select_fg = "black"
        self.no_comments_fg = "grey"
        self.comment_fg = "black"
        self.no_comments_message = " Коментарів ще немає."

        self.detail_icon_size = (160, 160)
        self.list_icon_size = (64, 64)

        self._load_placeholders(list_size=self.list_icon_size, detail_size=self.detail_icon_size)

        self.width = 850
        self.height = 700
        center_window(self, self.width, self.height)
        self.title("Universal Games")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

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
        }

        self._load_placeholders(list_size=self.list_icon_size, detail_size=self.detail_icon_size)

        self.width = 850
        self.height = 700
        center_window(self, self.width, self.height)
        self.title("Universal Games")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


        app_title_label = tk.Label(self, text="Universal Games", font=("Verdana", 18, "bold"))
        app_title_label.grid(row=0, column=0, pady=(10,5))


        style = ttk.Style(self)
        try:

            self.custom_button_style = 'NoFocus.TButton'
            style.configure(self.custom_button_style, focuscolor=style.lookup('TButton', 'background'))

            style.configure('TNotebook.Tab', font=self.fonts['ui'], padding=[5, 2], focusthickness=0)
            style.map('TNotebook.Tab', focuscolor=[('focus', style.lookup('TNotebook', 'background'))]) 
        except tk.TclError as e:
            print(f"Помилка налаштування стилів ttk: {e}")
            self.custom_button_style = 'TButton' 

        self.notebook = ttk.Notebook(self)
        self.notebook.bind("<FocusIn>", self._unfocus_notebook) 

        self.store_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.store_tab_frame, text='Магазин')
        self.store_tab_frame.grid_rowconfigure(0, weight=1)
        self.store_tab_frame.grid_columnconfigure(0, weight=1)

        self.store_canvas, self.store_list_frame = self._create_scrollable_list_frame(self.store_tab_frame)

        self.library_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.library_tab_frame, text='Бібліотека')
        
        self.library_view = LibraryTab(
            parent=self.library_tab_frame,
            db_manager=self.db_manager,
            user_id=self.current_user_id,
            image_cache=self._image_references, 
            placeholder_list=self.placeholder_image, 
            placeholder_detail=self.placeholder_image_detail,
            image_folder_path=self.image_folder,
            fonts={ 
                'ui': self.fonts['ui'],
                'list_title': self.fonts['library_list_title'],
                'detail_title': self.fonts['library_detail_title'],
                'detail': self.fonts['detail']
            },
            colors=self.colors 
        )
        self.library_view.paned_window.pack(fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(self, text="Оновити поточну вкладку", command=self.refresh_current_tab, style=self.custom_button_style)
        refresh_button.grid(row=2, column=0, pady=10)

        self.notebook.grid(row=1, column=0, sticky='nsew') 

        self.load_games_store()

    def _unfocus_notebook(self, event):
        """Забирає фокус з Notebook, щоб уникнути рамки навколо вкладки."""
        self.after_idle(self.focus_set)

    def _create_scrollable_list_frame(self, parent):
        canvas_scrollbar_frame = tk.Frame(parent, bg=self.original_bg)
        canvas_scrollbar_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        canvas_scrollbar_frame.grid_rowconfigure(0, weight=1)
        canvas_scrollbar_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background=self.original_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, background=self.original_bg)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def _on_inner_frame_configure(event=None):
             canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_inner_canvas_configure(event):
             canvas_width = event.width
             canvas.itemconfig(canvas_frame_id, width=canvas_width)
             inner_frame.config(width=canvas_width)


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
        """Оновлює вміст поточної активної вкладки."""
        if self.detail_view_instance and self.detail_view_instance.winfo_ismapped():
             print("Refreshing Detail View...")
             game_id = self.detail_view_instance.game_id
             self._show_detail_view(game_id)
             return

        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
            if selected_tab_index == 0: 
                print("Refreshing Store Tab...")
                self.load_games_store()
            elif selected_tab_index == 1:
                print("Refreshing Library Tab...")
                if hasattr(self, 'library_view'):
                    self.library_view.load_library_games()
                else:
                    print("Library view not initialized.")
        except tk.TclError:
            print("Could not get selected tab (Notebook might not be visible).")
        except AttributeError as e:
            print(f"Error refreshing tab: {e}")


    def _show_notebook_view(self):
        """Показує вкладки, ховає детальний вигляд."""
        if self.detail_view_instance:
            self.detail_view_instance.destroy() 
            self.detail_view_instance = None
        self.notebook.grid(row=1, column=0, sticky='nsew')
        self.title("Universal Games") 
        
    def _show_detail_view(self, game_id, event=None):
        """Показує детальний вигляд гри, ховає вкладки."""

        self.notebook.grid_remove()

        if self.detail_view_instance:
            self.detail_view_instance.destroy()
            self.detail_view_instance = None

        try:
            game_details = self.db_manager.fetch_game_details(game_id)
        except AttributeError:
             messagebox.showerror("Помилка", "Функція отримання деталей гри ще не реалізована в DB Manager.")
             self._show_notebook_view()
             return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі гри:\n{e}")
            self._show_notebook_view()
            return

        if not game_details:
            messagebox.showwarning("Не знайдено", f"Гра з ID {game_id} не знайдена.")
            self._show_notebook_view()
            return

        self.detail_view_instance = GameDetailView(
            parent=self, 
            db_manager=self.db_manager,
            user_id=self.current_user_id,
            game_id=game_id,
            game_data=game_details,
            image_cache=self._image_references,
            placeholder_list=self.placeholder_image,
            placeholder_detail=self.placeholder_image_detail,
            fonts=self.fonts, 
            colors=self.colors, 
            styles=self.styles,
            back_command=self._show_notebook_view
        )
        self.detail_view_instance.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.title(f"Universal Games - {game_details.get('title', 'Деталі гри')}")

    def _load_placeholders(self, list_size=(64, 64), detail_size=(160, 160)):
        """Завантажує зображення-заповнювачі."""
        print("Loading placeholders...")
        if self.placeholder_image_path and os.path.exists(self.placeholder_image_path):
            self.placeholder_image = self._load_image_internal(
                self.placeholder_image_name, self.placeholder_image_path, size=list_size, is_placeholder=True
            )
            detail_placeholder_key = f"{self.placeholder_image_name}_detail"
            self.placeholder_image_detail = self._load_image_internal(
                detail_placeholder_key, self.placeholder_image_path, size=detail_size, is_placeholder=True
            )

            if self.placeholder_image:
                print(f"List placeholder loaded: {self.placeholder_image}")
            else:
                print("Failed to load list placeholder.")
            if self.placeholder_image_detail:
                print(f"Detail placeholder loaded: {self.placeholder_image_detail}")
            else:
                print("Failed to load detail placeholder.")
                if self.placeholder_image:
                    print("Using list placeholder for detail view as fallback.")
                    self.placeholder_image_detail = self.placeholder_image

        else:
            print(f"Placeholder image file not found or path not set: {self.placeholder_image_path}")
            self.placeholder_image = None
            self.placeholder_image_detail = None


    def _load_image_internal(self, image_filename, full_path, size=(64, 64), is_placeholder=False):
        default_placeholder = None
        if not is_placeholder:
             default_placeholder = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image

        if not image_filename:
            return default_placeholder

        cache_key = f"{image_filename}_{size[0]}x{size[1]}"
        if cache_key in self._image_references:
            return self._image_references[cache_key]

        if full_path and os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self._image_references[cache_key] = photo_img
                return photo_img
            except Exception as e:
                print(f"Error loading image '{full_path}' (will use default placeholder or None): {e}")
                return default_placeholder
        else:
             if not is_placeholder:
                 print(f"Image file not found: {full_path} (using default placeholder or None)")
             return default_placeholder


    def _get_image(self, image_filename, size=(64, 64)):
        placeholder_to_return = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image

        if not image_filename:
            return placeholder_to_return
        if self.image_folder is None:
             print("IMAGE_FOLDER is not set, cannot load image.")
             return None

        full_path = os.path.join(self.image_folder, image_filename)
        is_placeholder_request = (image_filename == self.placeholder_image_name) and (full_path == self.placeholder_image_path)
        
        return self._load_image_internal(image_filename, full_path, size=size, is_placeholder=is_placeholder_request)
    
    def _on_mousewheel(self, event):
        active_canvas = None
        if self.notebook.winfo_ismapped():
            try:
                current_tab_index = self.notebook.index(self.notebook.select())
                if current_tab_index == 0:
                    active_canvas = self.store_canvas
                elif current_tab_index == 1:
                    if hasattr(self, 'library_view') and hasattr(self.library_view, 'library_canvas'):
                       active_canvas = self.library_view.library_canvas
                    else: return
            except tk.TclError:
                 return
        elif self.detail_view_instance and self.detail_view_instance.winfo_ismapped():
             return
        else:
             return

        if not active_canvas: return

        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return
        active_canvas.yview_scroll(delta, "units")
        return "break"

    def _on_enter(self, event, frame, icon_widget=None):
        frame.config(background=self.hover_bg)
        for widget in frame.winfo_children():
            if widget == icon_widget: continue 
            if isinstance(widget, (tk.Label, tk.Frame)):
                widget.config(background=self.hover_bg)
                
                if isinstance(widget, tk.Frame):
                    for grandchild in widget.winfo_children():
                        if isinstance(grandchild, tk.Label):
                            grandchild.config(background=self.hover_bg)

    def _on_leave(self, event, frame, icon_widget=None):
        frame.config(background=self.original_bg)
        for widget in frame.winfo_children():
             if widget == icon_widget: continue
             if isinstance(widget, (tk.Label, tk.Frame)):
                 widget.config(background=self.original_bg)
                 if isinstance(widget, tk.Frame):
                     for grandchild in widget.winfo_children():
                         if isinstance(grandchild, tk.Label):
                             grandchild.config(background=self.original_bg)

    def _create_game_entry(self, parent, game_data):
        """Створює віджет для однієї гри в списку магазину."""
        try:
            if len(game_data) < 5:
                 print(f"Skipping game entry due to insufficient data: {game_data}")
                 return None
            game_id, title, _, price, image_filename = game_data[:5]
        except (ValueError, TypeError) as e:
            print(f"Error unpacking game data for store list: {game_data}, Error: {e}")
            return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.RIDGE, background=self.original_bg)

        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_image(image_filename, size=self.list_icon_size)
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.fonts['ui'], width=8, height=4)

        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        title_label = tk.Label(text_frame, text=title or "Без назви",
                               font=self.fonts['list_title'], anchor="w", background=self.original_bg)
        title_label.pack(fill=tk.X)

        if price is None: price_text = "N/A"
        elif isinstance(price, (int, float, decimal.Decimal)) and float(price) == 0.0: price_text = "Безкоштовно"
        else:
            try: price_text = f"Ціна: {float(price):.2f}₴"
            except (ValueError, TypeError): price_text = "N/A"
        price_label = tk.Label(text_frame, text=price_text, font=self.fonts['ui'], anchor="w", background=self.original_bg)
        price_label.pack(fill=tk.X)

        widgets_to_bind_hover_click = [entry_frame, icon_label, text_frame, title_label, price_label]

        click_handler = partial(self._show_detail_view, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        for widget in widgets_to_bind_hover_click:
            widget.bind("<Button-1>", click_handler)
            widget.bind("<Enter>", enter_handler)   
            widget.bind("<Leave>", leave_handler)   
            widget.config(cursor="hand2")
            widget.bind("<MouseWheel>", self._on_mousewheel) 
            widget.bind("<Button-4>", self._on_mousewheel) 
            widget.bind("<Button-5>", self._on_mousewheel)

        return entry_frame

    def load_games_store(self):
        for widget in self.store_list_frame.winfo_children():
            widget.destroy()
        self._game_widgets_store = []

        games_data = []
        try:
            games_data = self.db_manager.fetch_all_games()
        except AttributeError:
            messagebox.showerror("Помилка", "Функція fetch_all_games не реалізована в DB Manager.")
            tk.Label(self.store_list_frame, text="Помилка завантаження даних (DB)", fg="red").pack(pady=20)
            return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити список ігор:\n{e}")
            tk.Label(self.store_list_frame, text=f"Помилка бази даних:\n{e}", fg="red", wraplength=self.width-50).pack(pady=20)
            return


        if games_data is None:
            print("DB: fetch_all_games returned None.")
            tk.Label(self.store_list_frame, text="Не вдалося отримати дані з бази даних.", fg="red").pack(pady=20)
            return

        if not games_data:
            tk.Label(self.store_list_frame, text="В магазині поки немає ігор.", font=self.fonts['ui']).pack(pady=20)
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
        if hasattr(self, 'library_view'):
            print("Triggering library refresh from StoreWindow...")
            self.library_view.load_library_games()
        else:
            print("Warning: Library view is not initialized yet, cannot refresh.")

    def on_close(self):
        self._image_references.clear()
        self.destroy()