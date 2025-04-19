import tkinter as tk
from tkinter import ttk, messagebox
from window_utils import center_window
import os
from PIL import Image, ImageTk
from functools import partial

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
        self._game_widgets = []

        self.original_bg = "white"
        self.hover_bg = "#f0f0f0"

        self._load_placeholder()

        self.width = 550
        self.height = 600
        center_window(self, self.width, self.height)
        self.title("Universal Games - Огляд")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ui_font = ("Verdana", 10)
        self.title_font = ("Verdana", 14, "bold")
        title_label = tk.Label(self, text="Список Ігор", font=self.title_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        list_frame = tk.Frame(self)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(list_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.games_frame = tk.Frame(self.canvas, background="#ffffff")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.games_frame, anchor="nw")

        self.games_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        refresh_button = ttk.Button(self, text="Оновити список", command=self.load_games)
        refresh_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_games()

    def _load_placeholder(self, size=(64, 64)):
        if PLACEHOLDER_IMAGE_NAME in self._image_references:
            self.placeholder_image = self._image_references[PLACEHOLDER_IMAGE_NAME]
            return
        try:
            if os.path.exists(PLACEHOLDER_IMAGE_PATH):
                img = Image.open(PLACEHOLDER_IMAGE_PATH)
                img = img.resize(size, Image.Resampling.LANCZOS)
                self.placeholder_image = ImageTk.PhotoImage(img)
                self._image_references[PLACEHOLDER_IMAGE_NAME] = self.placeholder_image
                print(f"Placeholder loaded from: {PLACEHOLDER_IMAGE_PATH}")
            else:
                 print(f"ERROR: Placeholder not found at {PLACEHOLDER_IMAGE_PATH}")
        except Exception as e:
             print(f"ERROR loading placeholder: {e}")

    def _load_image_internal(self, image_filename, full_path, size=(64, 64)):
        if not image_filename: return self.placeholder_image
        if image_filename in self._image_references: return self._image_references[image_filename]
        if full_path and os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self._image_references[image_filename] = photo_img
                return photo_img
            except Exception as e:
                print(f"Error loading image '{full_path}': {e}")
                return self.placeholder_image
        else:
            return self.placeholder_image

    def _get_image(self, image_filename):
        if not image_filename: return self.placeholder_image
        full_path = os.path.join(IMAGE_FOLDER, image_filename)
        return self._load_image_internal(image_filename, full_path)

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
        elif float(price) == 0.0: price_text = "Безкоштовно"
        else:
            try: price_text = f"Ціна: {float(price):.2f} $"
            except (ValueError, TypeError): price_text = "N/A"
        price_label = tk.Label(text_frame, text=price_text, font=self.ui_font, anchor="w", background=self.original_bg)
        price_label.pack(fill=tk.X)

        click_handler = partial(self._show_game_details, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        widgets_to_bind = [entry_frame, icon_label, text_frame, title_label, price_label]

        for widget in widgets_to_bind:
            widget.bind("<Button-1>", click_handler)
            widget.bind("<Enter>", enter_handler)
            widget.bind("<Leave>", leave_handler)
            widget.config(cursor="hand2")

        return entry_frame

    def _show_game_details(self, game_id, event=None):
        print(f"Клікнули на гру з ID: {game_id}")
        messagebox.showinfo("Деталі гри", f"Ви клікнули на гру з ID: {game_id}\n\n(Тут буде детальне вікно)")


    def load_games(self):
        for widget in self.games_frame.winfo_children():
            widget.destroy()
        self._game_widgets = []
        games_data = self.db_manager.fetch_all_games()
        if games_data is None:
            tk.Label(self.games_frame, text="Помилка завантаження даних", fg="red").pack(pady=20)
            print("DB: Failed to fetch games from DB.")
            return
        if not games_data:
            tk.Label(self.games_frame, text="Немає доступних ігор").pack(pady=20)
        else:
            for game in games_data:
                if len(game) < 5:
                    print(f"Error: Insufficient data: {game}")
                    continue
                game_widget = self._create_game_entry(self.games_frame, game)
                if game_widget:
                    game_widget.pack(fill=tk.X, pady=2, padx=2)
                    self._game_widgets.append(game_widget)
        self.games_frame.update_idletasks()
        self._on_frame_configure()

    def on_close(self):
        print("Closing Store Window...")
        self._image_references.clear()
        self.destroy()