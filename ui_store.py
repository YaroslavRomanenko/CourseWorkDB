import tkinter as tk
from tkinter import ttk, messagebox
# scrolledtext is no longer needed
import os
from PIL import Image, ImageTk
from functools import partial
import decimal

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
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._image_references = {}
        self.placeholder_image = None
        self.placeholder_image_detail = None
        self._game_widgets = []
        self.current_detail_game_id = None

        self.original_bg = "white"
        self.hover_bg = "#f0f0f0"
        self.listbox_select_bg = self.original_bg
        self.listbox_select_fg = "black"

        self.detail_icon_size = (160, 160)

        self._load_placeholders(detail_size=self.detail_icon_size)

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
        self.price_font = ("Verdana", 12, "bold")
        self.comment_font = ("Verdana", 9)
        self.description_font = ("Verdana", 10)

        self.list_container_frame = tk.Frame(self)
        self.list_container_frame.grid_rowconfigure(1, weight=1)
        self.list_container_frame.grid_columnconfigure(0, weight=1)

        self.detail_frame = tk.Frame(self, background=self.original_bg)
        self.detail_frame.grid_columnconfigure(0, weight=0)
        self.detail_frame.grid_columnconfigure(1, weight=1)
        self.detail_frame.grid_rowconfigure(7, weight=1)

        app_title_label = tk.Label(self, text="Universal Games", font=("Verdana", 18, "bold"))
        app_title_label.grid(row=0, column=0, pady=(10,5))

        list_title_label = tk.Label(self.list_container_frame, text="Список Ігор", font=self.title_font)
        list_title_label.grid(row=0, column=0, columnspan=2, pady=5)

        canvas_scrollbar_frame = tk.Frame(self.list_container_frame)
        canvas_scrollbar_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        canvas_scrollbar_frame.grid_rowconfigure(0, weight=1)
        canvas_scrollbar_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=self.canvas.yview)
        self.games_list_frame = tk.Frame(self.canvas, background="#ffffff")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.games_list_frame, anchor="nw")

        self.games_list_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        refresh_button = ttk.Button(self.list_container_frame, text="Оновити список", command=self.load_games)
        refresh_button.grid(row=2, column=0, columnspan=2, pady=(5,10))

        self._show_list_view()
        self.load_games()

    def _show_list_view(self):
        self.current_detail_game_id = None
        self.detail_frame.grid_remove()
        self.list_container_frame.grid(row=1, column=0, sticky='nsew')
        self.title("Universal Games - Список Ігор")

    def _show_detail_view(self, game_id, event=None):
        self.current_detail_game_id = game_id
        self.list_container_frame.grid_remove()
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        try:
            game_details = self.db_manager.fetch_game_details(game_id)
        except AttributeError:
             messagebox.showerror("Помилка", "Функція отримання деталей гри ще не реалізована.")
             self._show_list_view()
             return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі гри:\n{e}")
            self._show_list_view()
            return

        if not game_details:
            messagebox.showwarning("Не знайдено", f"Гра з ID {game_id} не знайдена.")
            self._show_list_view()
            return

        self._populate_detail_frame(game_details)
        self.detail_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.title(f"Universal Games - {game_details.get('title', 'Деталі гри')}")

    def _populate_detail_frame(self, game_data):
        back_button = ttk.Button(self.detail_frame, text="< Назад до списку", command=self._show_list_view)
        back_button.grid(row=0, column=0, columnspan=2, pady=(5, 15), padx=5, sticky='w')

        icon_label = tk.Label(self.detail_frame, background=self.original_bg)
        img_filename = game_data.get('image')
        tk_detail_image = self._get_image(img_filename, size=self.detail_icon_size)
        if tk_detail_image:
             icon_label.config(image=tk_detail_image)
             icon_label.image = tk_detail_image
        else:
             icon_label.config(text="Немає фото", font=self.ui_font, width=round(self.detail_icon_size[0]/8), height=round(self.detail_icon_size[1]/15))
        icon_label.grid(row=1, column=0, padx=(10, 20), pady=5, sticky='nw')

        info_frame = tk.Frame(self.detail_frame, background=self.original_bg)
        info_frame.grid(row=1, column=1, sticky='nsew', pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(info_frame, text=game_data.get('title', 'Без назви'), font=self.title_font, background=self.original_bg, wraplength=self.width-self.detail_icon_size[0]-100, justify=tk.LEFT)
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
            price_label_detail = tk.Label(price_buy_frame, text=price_text_raw, font=self.price_font, background=self.original_bg)
            price_label_detail.pack(side=tk.LEFT, anchor='w')
            buy_button = ttk.Button(price_buy_frame, text="Придбати")
            if price_text_raw == "Безкоштовно":
                 buy_button.config(text="Отримати Безкоштовно")
            buy_button.pack(side=tk.LEFT, padx=(15, 0), anchor='w')
        else:
            status_text = f"Статус: {game_data.get('status', 'N/A')}"
            status_label = tk.Label(price_buy_frame, text=status_text, font=self.detail_font, background=self.original_bg)
            status_label.pack(side=tk.LEFT, anchor='w')

        separator1 = ttk.Separator(self.detail_frame, orient='horizontal')
        separator1.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=15)

        desc_label = tk.Label(self.detail_frame, text="Опис:", font=("Verdana", 12, "bold"), background=self.original_bg)
        desc_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 5))

        description = game_data.get('description', 'Опис відсутній.')
        desc_content_label = tk.Label(
            self.detail_frame,
            text=description,
            font=self.description_font,
            wraplength=self.width - 40,
            justify=tk.LEFT,
            anchor='nw',
            background=self.original_bg
        )
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
        self.detail_frame.grid_rowconfigure(7, weight=1)

        comments_scrollbar = ttk.Scrollbar(comments_list_frame)
        comments_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.comments_listbox = tk.Listbox(
            comments_list_frame,
            yscrollcommand=comments_scrollbar.set,
            font=self.comment_font,
            height=6,
            background=self.original_bg,
            selectbackground=self.listbox_select_bg,
            selectforeground=self.listbox_select_fg,
            activestyle='none',
            highlightthickness=0,
            borderwidth=0
        )
        self.comments_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        comments_scrollbar.config(command=self.comments_listbox.yview)

        comment_input_frame = tk.Frame(self.detail_frame, background=self.original_bg)
        comment_input_frame.grid(row=8, column=0, columnspan=2, sticky='ew', padx=10, pady=(5, 10))
        comment_input_frame.grid_columnconfigure(0, weight=1)

        self.comment_entry = tk.Entry(comment_input_frame, font=self.ui_font, width=60)
        self.comment_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        post_comment_button = ttk.Button(
            comment_input_frame, text="Надіслати", command=self._post_comment
        )
        post_comment_button.grid(row=0, column=1, sticky='e')

        self._load_comments(game_data.get('game_id'))

    def _load_comments(self, game_id):
        self.comments_listbox.delete(0, tk.END)
        if game_id is None: return
        print(f"Завантаження коментарів для гри ID: {game_id} (потрібна реалізація в DB)")
        comments_data = []
        try:
             if game_id == 1: comments_data = [('Гравець1', 'Дуже сподобалось!', '2024-05-20 10:30'), ('Тестувальник', 'Потрібно більше контенту.', '2024-05-21 15:00')]
             else: comments_data = []
        except AttributeError: print("Метод fetch_comments не реалізовано в db_manager."); comments_data = [("System", "Функція коментарів не активна.", "")]
        except Exception as e: print(f"Помилка завантаження коментарів: {e}"); comments_data = [("System", "Помилка завантаження коментарів.", "")]
        if not comments_data: self.comments_listbox.insert(tk.END, " Коментарів ще немає."); self.comments_listbox.itemconfig(tk.END, {'fg': 'grey'})
        else:
            for comment in comments_data:
                try:
                    user, text, date = comment
                    display_string = f" {user} ({date}): {text}"
                    self.comments_listbox.insert(tk.END, display_string)
                except Exception as e: print(f"Помилка відображення коментаря {comment}: {e}"); self.comments_listbox.insert(tk.END, " Помилка завантаження коментаря")

    def _post_comment(self):
        comment_text = self.comment_entry.get().strip()
        if not comment_text: messagebox.showwarning("Порожній коментар", "Будь ласка, введіть текст коментаря."); return
        if self.current_detail_game_id is None: messagebox.showerror("Помилка", "Не вдалося визначити ID гри для коментаря."); return
        print(f"Відправка коментаря для гри ID {self.current_detail_game_id}: '{comment_text}' (потрібна реалізація в DB)")
        success = False
        try:
             success = True
        except AttributeError: print("Метод add_comment не реалізовано в db_manager."); messagebox.showerror("Помилка", "Функція додавання коментарів не активна.")
        except Exception as e: print(f"Помилка додавання коментаря: {e}"); messagebox.showerror("Помилка", "Не вдалося додати коментар.")
        if success: self.comment_entry.delete(0, tk.END); self._load_comments(self.current_detail_game_id)

    def _load_placeholders(self, list_size=(64, 64), detail_size=(160, 160)):
        self.placeholder_image = self._load_image_internal(PLACEHOLDER_IMAGE_NAME, PLACEHOLDER_IMAGE_PATH, size=list_size, is_placeholder=True)
        self.placeholder_image_detail = self._load_image_internal(f"{PLACEHOLDER_IMAGE_NAME}_detail", PLACEHOLDER_IMAGE_PATH, size=detail_size, is_placeholder=True)
        if not self.placeholder_image_detail and self.placeholder_image:
            self.placeholder_image_detail = self.placeholder_image
        print(f"Placeholder for list: {'Loaded' if self.placeholder_image else 'Failed'}")
        print(f"Placeholder for detail: {'Loaded' if self.placeholder_image_detail else 'Failed'}")

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
                print(f"Error loading image '{full_path}' size {size}: {e}")
                return placeholder_to_return
        else:
             if not is_placeholder: print(f"Warning: Image file not found: {full_path}")
             return placeholder_to_return

    def _get_image(self, image_filename, size=(64, 64)):
        if not image_filename:
             return self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image

        full_path = os.path.join(IMAGE_FOLDER, image_filename)
        return self._load_image_internal(image_filename, full_path, size)

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def _on_mousewheel(self, event):
        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else: delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")

    def _on_enter(self, event, frame, icon_widget):
        frame.config(background=self.hover_bg)
        for widget in frame.winfo_children():
            if widget != icon_widget:
                if isinstance(widget, (tk.Label, tk.Frame)):
                     widget.config(background=self.hover_bg)

    def _on_leave(self, event, frame, icon_widget):
        frame.config(background=self.original_bg)
        for widget in frame.winfo_children():
             if widget != icon_widget:
                if isinstance(widget, (tk.Label, tk.Frame)):
                     widget.config(background=self.original_bg)

    def _create_game_entry(self, parent, game_data):
        try:
            game_id, title, genre, price, image_filename = game_data
        except (ValueError, TypeError):
            print(f"Помилка розпаковки: {game_data}")
            return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.RIDGE, background=self.original_bg)

        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_image(image_filename)
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        title_label = tk.Label(text_frame, text=title, font=("Verdana", 12, "bold"), anchor="w", background=self.original_bg)
        title_label.pack(fill=tk.X)

        if price is None: price_text = "N/A"
        elif isinstance(price, (int, float, decimal.Decimal)) and float(price) == 0.0: price_text = "Безкоштовно"
        else:
            try: price_text = f"Ціна: {float(price):.2f}₴"
            except (ValueError, TypeError): price_text = "N/A"
        price_label = tk.Label(text_frame, text=price_text, font=self.ui_font, anchor="w", background=self.original_bg)
        price_label.pack(fill=tk.X)

        click_handler = partial(self._show_detail_view, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        widgets_to_bind = [entry_frame, icon_label, text_frame, title_label, price_label]

        for widget in widgets_to_bind:
            widget.bind("<Button-1>", click_handler)
            widget.bind("<Enter>", enter_handler)
            widget.bind("<Leave>", leave_handler)
            widget.config(cursor="hand2")

        return entry_frame

    def load_games(self):
        for widget in self.games_list_frame.winfo_children():
            widget.destroy()
        self._game_widgets = []
        games_data = self.db_manager.fetch_all_games()
        if games_data is None:
            tk.Label(self.games_list_frame, text="Помилка завантаження даних", fg="red").pack(pady=20)
            print("DB: Failed to fetch games from DB.")
            return
        if not games_data:
            tk.Label(self.games_list_frame, text="Немає доступних ігор").pack(pady=20)
        else:
            for game in games_data:
                if len(game) < 5:
                    print(f"Error: Insufficient data: {game}")
                    continue
                game_widget = self._create_game_entry(self.games_list_frame, game)
                if game_widget:
                    game_widget.pack(fill=tk.X, pady=2, padx=2)
                    self._game_widgets.append(game_widget)
        self.games_list_frame.update_idletasks()
        self._on_frame_configure()

    def on_close(self):
        print("Closing Store Window...")
        self._image_references.clear()
        self.destroy()