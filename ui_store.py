import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from functools import partial
import decimal
from ui_library import LibraryTab

def center_window(window, width, height):
    try:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception as e:
        print(f"Помилка центрування вікна: {e}")
        window.geometry(f"{width}x{height}")

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()
IMAGE_FOLDER = os.path.join(SCRIPT_DIR, 'resources', 'games_icons')
PLACEHOLDER_IMAGE_NAME = 'placeholder.png'
PLACEHOLDER_IMAGE_PATH = os.path.join(IMAGE_FOLDER, PLACEHOLDER_IMAGE_NAME)

class StoreWindow(tk.Tk):
    def __init__(self, db_manager, user_id):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = user_id
        self._image_references = {}
        self.placeholder_image = None
        self.placeholder_image_detail = None
        self._game_widgets_store = []
        self.current_detail_game_id = None

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

        self.ui_font = ("Verdana", 10)
        self.title_font = ("Verdana", 16, "bold")
        self.detail_font = ("Verdana", 11)
        self.price_font = ("Verdana", 12)
        self.comment_font = ("Verdana", 9)
        self.description_font = ("Verdana", 10)

        self.detail_frame = tk.Frame(self, background=self.original_bg)
        self.detail_frame.grid_columnconfigure(0, weight=0)
        self.detail_frame.grid_columnconfigure(1, weight=1)

        app_title_label = tk.Label(self, text="Universal Games", font=("Verdana", 18, "bold"))
        app_title_label.grid(row=0, column=0, pady=(10,5))

        style = ttk.Style(self)
        self.custom_button_style = 'NoFocus.TButton'
        style.configure(self.custom_button_style, focuscolor=style.lookup('TButton', 'background'))
        
        try:
            style.configure('TNotebook.Tab', focusthickness=0)
        except tk.TclError as e:
            print(f"Помилка налаштування стилю TNotebook.Tab: {e}")   
            
        try:
            style.configure(self.custom_button_style, focusthickness=0)
            style.map(self.custom_button_style, focuscolor=[('focus', style.lookup('TButton', 'background'))])
        except tk.TclError as e:
            print(f"Помилка налаштування стилю TButton: {e}")
        
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
            placeholder_detail=self.placeholder_image_detail
        )
        
        self.library_view.paned_window.pack(fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(self, text="Оновити поточну вкладку", command=self.refresh_current_tab, style=self.custom_button_style)
        refresh_button.grid(row=2, column=0, pady=10)

        self.notebook.grid(row=1, column=0, sticky='nsew')
        
        self.load_games_store()

    def _unfocus_notebook(self, event):
        self.after_idle(self.focus_set)
    
    def _create_scrollable_list_frame(self, parent):
        canvas_scrollbar_frame = tk.Frame(parent)
        canvas_scrollbar_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        canvas_scrollbar_frame.grid_rowconfigure(0, weight=1)
        canvas_scrollbar_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background="#ffffff")
        scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, background="#ffffff")

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def _on_inner_frame_configure(event=None):
             canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_inner_canvas_configure(event):
             canvas.itemconfig(canvas_frame_id, width=event.width)

        def _on_inner_mousewheel(event):
            if event.num == 4: delta = -1
            elif event.num == 5: delta = 1
            else:
                try: delta = -1 if event.delta > 0 else 1
                except AttributeError: return
            canvas.yview_scroll(delta, "units")

        inner_frame.bind("<Configure>", _on_inner_frame_configure)
        canvas.bind('<Configure>', _on_inner_canvas_configure)
        canvas.bind("<MouseWheel>", _on_inner_mousewheel)
        canvas.bind("<Button-4>", _on_inner_mousewheel)
        canvas.bind("<Button-5>", _on_inner_mousewheel)

        return canvas, inner_frame

    def refresh_current_tab(self):
        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
            if selected_tab_index == 0:
                print("Refreshing Store Tab...")
                self.load_games_store()
            elif selected_tab_index == 1:
                print("Refreshing Library Tab...")
                self.library_view.load_library_games()
        except tk.TclError:
            print("Could not get selected tab (Notebook might be hidden).")
        except AttributeError:
            print("Library view not yet initialized.")


    def _show_notebook_view(self):
        self.current_detail_game_id = None
        self.detail_frame.grid_remove()
        self.notebook.grid(row=1, column=0, sticky='nsew')
        self.title("Universal Games")

    def _show_detail_view(self, game_id, event=None):
        self.current_detail_game_id = game_id
        self.notebook.grid_remove()
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        try:
            game_details = self.db_manager.fetch_game_details(game_id)
        except AttributeError:
             messagebox.showerror("Помилка", "Функція отримання деталей гри ще не реалізована.")
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

        self._populate_detail_frame(game_details)
        self.detail_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.title(f"Universal Games - {game_details.get('title', 'Деталі гри')}")

    def _populate_detail_frame(self, game_data):
        self.detail_frame.grid_rowconfigure(7, weight=1)
        
        back_button = ttk.Button(self.detail_frame, text="< Назад", command=self._show_notebook_view, style=self.custom_button_style)
        back_button.grid(row=0, column=0, columnspan=2, pady=(5, 15), padx=5, sticky='w')
        
        icon_label = tk.Label(self.detail_frame, background=self.original_bg)
        img_filename = game_data.get('image')
        tk_detail_image = self._get_image(img_filename, size=self.detail_icon_size)
        
        if tk_detail_image:
            icon_label.config(image=tk_detail_image)
            icon_label.image = tk_detail_image
        else:
            icon_label.config(text="Немає фото", font=self.ui_font, width=round(self
                                                                                .detail_icon_size[0]/8), height=round(self.detail_icon_size[1]/15))
        icon_label.grid(row=1, column=0, padx=(10, 20), pady=5, sticky='nw')
        info_frame = tk.Frame(self.detail_frame, background=self.original_bg)
        info_frame.grid(row=1, column=1, sticky='nsew', pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(info_frame, text=game_data.get('title', '...'), font=self.title_font, background=self.original_bg, wraplength=self.width-self.detail_icon_size[0]-100, justify=tk.LEFT)
        title_label.grid(row=0, column=0, sticky='nw')
        
        price_buy_frame = tk.Frame(info_frame, background=self.original_bg)
        price_buy_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=(15, 0))
        price = game_data.get('price')
        if price is None: price_text_raw = "N/A"
        elif isinstance(price, (int, float, decimal.Decimal)) and float(price) == 0.0: price_text_raw = "Безкоштовно"
        else:
            try: price_text_raw = f"{float(price):.2f}₴"
            except (ValueError, TypeError): price_text_raw = "N/A"
        if price_text_raw != "N/A":
            price_label_detail = tk.Label(price_buy_frame, text=price_text_raw, font=self.detail_font, background=self.original_bg)
            price_label_detail.pack(side=tk.LEFT, anchor='w')
            buy_button = ttk.Button(price_buy_frame, text="Придбати", style=self.custom_button_style)
            if price_text_raw == "Безкоштовно": buy_button.config(text="Отримати")
            buy_button.pack(side=tk.LEFT, padx=(15, 0), anchor='w')
        else:
            status_text = f"Статус: {game_data.get('status', 'N/A')}"
            status_label = tk.Label(price_buy_frame, text=status_text, font=self.detail_font, background=self.original_bg)
            status_label.pack(side=tk.LEFT, anchor='w')
            
        separator1 = ttk.Separator(self.detail_frame, orient='horizontal')
        separator1.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=15)
        
        desc_label = tk.Label(self.detail_frame, text="Опис:", font=("Verdana", 12, "bold"), background=self.original_bg)
        desc_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 5))
        
        description = game_data.get('description', '...')
        
        desc_content_label = tk.Label(self.detail_frame, text=description, font=self.description_font, wraplength=self.width - 40, justify=tk.LEFT, anchor='nw', background=self.original_bg)
        desc_content_label.grid(row=4, column=0, columnspan=2, sticky='nw', padx=10, pady=(0, 10))
        
        self.detail_frame.grid_rowconfigure(4, weight=0)
        
        separator2 = ttk.Separator(self.detail_frame, orient='horizontal')
        separator2.grid(row=5, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        
        comments_label = tk.Label(self.detail_frame, text="Коментарі:", font=("Verdana", 12, "bold"), background=self.original_bg)
        comments_label.grid(row=6, column=0, columnspan=2, sticky='w', padx=10, pady=(5, 2))
        comments_list_frame = tk.Frame(self.detail_frame)
        comments_list_frame.grid(row=7, column=0, columnspan=2, sticky='nsew', padx=10)
        comments_list_frame.grid_rowconfigure(0, weight=1)
        comments_list_frame.grid_columnconfigure(0, weight=1)
        comments_scrollbar = ttk.Scrollbar(comments_list_frame)
        comments_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.comments_listbox = tk.Listbox(comments_list_frame, yscrollcommand=comments_scrollbar.set, font=self.comment_font, height=6, background=self.original_bg, selectbackground=self.listbox_select_bg, selectforeground=self.listbox_select_fg, activestyle='none', highlightthickness=0, borderwidth=0)
        self.comments_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        comments_scrollbar.config(command=self.comments_listbox.yview)
        self.comments_listbox.bind("<<ListboxSelect>>", self._on_comment_select)
        
        comment_input_frame = tk.Frame(self.detail_frame, background=self.original_bg)
        comment_input_frame.grid(row=8, column=0, columnspan=2, sticky='ew', padx=10, pady=(5, 10))
        comment_input_frame.grid_columnconfigure(0, weight=1)
        
        self.comment_entry = tk.Entry(comment_input_frame, font=self.ui_font, width=60)
        self.comment_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        post_comment_button = ttk.Button(comment_input_frame, text="Надіслати", command=self._post_comment, style=self.custom_button_style)
        post_comment_button.grid(row=0, column=1, sticky='e')
        self._load_comments(game_data.get('game_id'))

    def _on_comment_select(self, event):
        widget = event.widget
        selected_indices = widget.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        item_text = widget.get(index)
        if item_text == self.no_comments_message:
            widget.selection_clear(index)
            widget.itemconfig(index, {'fg': self.no_comments_fg})

    def _load_comments(self, game_id):
        self.comments_listbox.delete(0, tk.END)
        if game_id is None: return
        print(f"...")
        comments_data = []
        try:
             if game_id == 1: comments_data = [('...', '...', '...'), ('...', '...', '...')]
             else: comments_data = []
        except AttributeError: print("..."); comments_data = [("...", "...", "")]
        except Exception as e: print(f"...: {e}"); comments_data = [("...", "...", "")]
        if not comments_data:
            self.comments_listbox.insert(tk.END, self.no_comments_message)
            self.comments_listbox.itemconfig(tk.END, {'fg': self.no_comments_fg})
        else:
            for comment in comments_data:
                try:
                    user, text, date = comment
                    display_string = f" {user} ({date}): {text}"
                    self.comments_listbox.insert(tk.END, display_string)
                    self.comments_listbox.itemconfig(tk.END, {'fg': self.comment_fg})
                except Exception as e: print(f"... {comment}: {e}"); self.comments_listbox.insert(tk.END, "...")

    def _post_comment(self):
        comment_text = self.comment_entry.get().strip()
        if not comment_text: messagebox.showwarning("...", "..."); return
        if self.current_detail_game_id is None: messagebox.showerror("...", "..."); return
        print(f"...")
        success = False
        try:
             success = True
        except AttributeError: print("..."); messagebox.showerror("...", "...")
        except Exception as e: print(f"...: {e}"); messagebox.showerror("...", "...")
        if success: self.comment_entry.delete(0, tk.END); self._load_comments(self.current_detail_game_id)

    def _load_placeholders(self, list_size=(64, 64), detail_size=(160, 160)):
        self.placeholder_image = self._load_image_internal(PLACEHOLDER_IMAGE_NAME, PLACEHOLDER_IMAGE_PATH, size=list_size, is_placeholder=True)
        self.placeholder_image_detail = self._load_image_internal(f"{PLACEHOLDER_IMAGE_NAME}_detail", PLACEHOLDER_IMAGE_PATH, size=detail_size, is_placeholder=True)
        if not self.placeholder_image_detail and self.placeholder_image:
            self.placeholder_image_detail = self.placeholder_image
        print(f"...")
        print(f"...")

    def _load_image_internal(self, image_filename, full_path, size=(64, 64), is_placeholder=False):
        placeholder_to_return = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image
        if not image_filename: return placeholder_to_return
        cache_key = f"{image_filename}_{size[0]}x{size[1]}"
        if cache_key in self._image_references: return self._image_references[cache_key]
        if full_path and os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self._image_references[cache_key] = photo_img
                return photo_img
            except Exception as e:
                print(f"... '{full_path}' ...: {e}")
                return placeholder_to_return
        else:
             if not is_placeholder: print(f"...not found: {full_path}")
             return placeholder_to_return

    def _get_image(self, image_filename, size=(64, 64)):
        placeholder_to_return = self.placeholder_image_detail if size[0] > 100 else self.placeholder_image
        if not image_filename: return placeholder_to_return
        full_path = os.path.join(IMAGE_FOLDER, image_filename)
        return self._load_image_internal(image_filename, full_path, size=size)

    def _on_mousewheel(self, event):
        active_canvas = None
        if self.notebook.winfo_ismapped():
            try:
                current_tab_index = self.notebook.index(self.notebook.select())
                if current_tab_index == 0: active_canvas = self.store_canvas
                elif current_tab_index == 1: active_canvas = self.library_canvas
            except tk.TclError: pass
        if not active_canvas: return

        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return
        active_canvas.yview_scroll(delta, "units")

    def _on_enter(self, event, frame, icon_widget):
        frame.config(background=self.hover_bg)
        for widget in frame.winfo_children():
            if widget != icon_widget:
                if isinstance(widget, (tk.Label, tk.Frame)):
                    widget.config(background=self.hover_bg)
                    if isinstance(widget, tk.Frame):
                        for grandchild in widget.winfo_children():
                            if isinstance(grandchild, tk.Label): grandchild.config(background=self.hover_bg)

    def _on_leave(self, event, frame, icon_widget):
        frame.config(background=self.original_bg)
        for widget in frame.winfo_children():
             if widget != icon_widget:
                if isinstance(widget, (tk.Label, tk.Frame)):
                     widget.config(background=self.original_bg)
                     if isinstance(widget, tk.Frame):
                         for grandchild in widget.winfo_children():
                             if isinstance(grandchild, tk.Label): grandchild.config(background=self.original_bg)

    def _create_game_entry(self, parent, game_data, is_library=False):
        try: game_id, title, genre, price, image_filename = game_data
        except (ValueError, TypeError): print(f"...: {game_data}"); return None
        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.RIDGE, background=self.original_bg)
        
        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_image(image_filename, size=self.list_icon_size)
        if tk_image: icon_label.config(image=tk_image); icon_label.image = tk_image
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        text_frame = tk.Frame(entry_frame, background=self.original_bg)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        title_label = tk.Label(text_frame, text=title, font=("Verdana", 12, "bold"), anchor="w", background=self.original_bg)
        title_label.pack(fill=tk.X)

        if not is_library:
            if price is None: price_text = "N/A"
            elif isinstance(price, (int, float, decimal.Decimal)) and float(price) == 0.0: price_text = "Безкоштовно"
            else:
                try: price_text = f"Ціна: {float(price):.2f}₴"
                except (ValueError, TypeError): price_text = "N/A"
            price_label = tk.Label(text_frame, text=price_text, font=self.ui_font, anchor="w", background=self.original_bg)
            price_label.pack(fill=tk.X)
            widgets_to_bind_click_scroll = [entry_frame, icon_label, text_frame, title_label, price_label]
        else:
            purchase_date_label = tk.Label(text_frame, text="У бібліотеці", font=self.ui_font, anchor="w", background=self.original_bg)
            purchase_date_label.pack(fill=tk.X)
            widgets_to_bind_click_scroll = [entry_frame, icon_label, text_frame, title_label, purchase_date_label]

        click_handler = partial(self._show_detail_view, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        entry_frame.bind("<Enter>", enter_handler)
        entry_frame.bind("<Leave>", leave_handler)

        for widget in widgets_to_bind_click_scroll:
            widget.bind("<Button-1>", click_handler)
            widget.config(cursor="hand2")
            widget.bind("<MouseWheel>", self._on_mousewheel)
            widget.bind("<Button-4>", self._on_mousewheel)
            widget.bind("<Button-5>", self._on_mousewheel)
        return entry_frame

    def load_games_store(self):
        for widget in self.store_list_frame.winfo_children(): widget.destroy()
        self._game_widgets_store = []
        games_data = self.db_manager.fetch_all_games()
        if games_data is None: tk.Label(self.store_list_frame, text="...", fg="red").pack(pady=20); print("..."); return
        if not games_data: tk.Label(self.store_list_frame, text="...").pack(pady=20)
        else:
            for game in games_data:
                if len(game) < 5: print(f"...: {game}"); continue
                game_widget = self._create_game_entry(self.store_list_frame, game, is_library=False)
                if game_widget: game_widget.pack(fill=tk.X, pady=2, padx=2); self._game_widgets_store.append(game_widget)
        self.store_list_frame.update_idletasks()
        self.store_canvas.configure(scrollregion=self.store_canvas.bbox("all"))

    def load_games_library(self):
        if hasattr(self, 'library_view'):
            self.library_view.load_library_games()
        else:
            print("Warning: Library view is not initialized yet.")

    def on_close(self):
        print("Closing Store Window...")
        self._image_references.clear()
        self.destroy()