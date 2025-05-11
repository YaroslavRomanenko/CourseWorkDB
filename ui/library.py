import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from functools import partial
import decimal

from ui.utils import *

class LibraryTab:
    def __init__(self, parent, db_manager, user_id, image_cache, placeholder_list, placeholder_detail, image_folder_path, fonts, colors):
        """Initializes the Library Tab frame"""
        self.parent = parent
        self.db_manager = db_manager
        self.user_id = user_id

        self._image_references = image_cache
        self.placeholder_image_list = placeholder_list
        self.placeholder_image_detail = placeholder_detail
        self.image_folder_path = image_folder_path

        self.original_bg = colors.get('original_bg', "white")
        self.hover_bg = colors.get('hover_bg', "#f0f0f0")
        self.list_icon_size = (48, 48)
        self.detail_icon_size = (300, 180)

        self.ui_font = fonts.get('ui', ("Verdana", 10))
        self.title_font_list = fonts.get('library_list_title', ("Verdana", 11, "bold"))
        self.title_font_detail = fonts.get('library_detail_title', ("Verdana", 14, "bold"))
        self.detail_font = fonts.get('detail', ("Verdana", 11))

        self.paned_window = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=1, bg=self.original_bg)

        desired_left_width = 290
        min_left_width = 240
        min_right_width = 520

        self.left_frame = tk.Frame(self.paned_window, width=desired_left_width, bg=self.original_bg)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.paned_window.add(self.left_frame, width=desired_left_width, minsize=min_left_width, stretch="never")

        self.library_list_container = tk.Frame(self.left_frame, bg=self.original_bg)
        self.library_list_container.grid(row=0, column=0, sticky='nsew')

        self.right_frame = tk.Frame(self.paned_window, bg=self.original_bg, padx=15, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.paned_window.add(self.right_frame, minsize=min_right_width, stretch="always")

        self.library_canvas = None
        self.library_list_frame = None
        self._game_widgets_library = []

        self._display_placeholder_details()
        self.load_library_games()

    def _create_library_entry(self, parent, game_data):
        """Creates a tk.Frame widget representing a single game in the library list"""
        try:
            game_id, title, _, _, image_filename = game_data
        except (ValueError, TypeError):
            print(f"LibraryTab Error: Invalid game data format: {game_data}")
            return None

        entry_frame = tk.Frame(parent, background=self.original_bg, cursor="hand2")

        icon_label = tk.Label(entry_frame, background=self.original_bg, cursor="hand2")
        tk_image = load_image_cached(self._image_references, image_filename,
                                    self.image_folder_path, self.list_icon_size,
                                    self.placeholder_image_list)
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.ui_font, width=int(self.list_icon_size[0]/6), height=int(self.list_icon_size[1]/12), relief="solid", borderwidth=1)
        icon_label.pack(side=tk.LEFT, padx=5, pady=3)

        title_label = tk.Label(entry_frame, text=title, font=self.title_font_list, anchor="w", background=self.original_bg, cursor="hand2")
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        click_handler = partial(self._on_game_select, game_id)

        entry_frame.bind("<Enter>",
                        lambda e, frm=entry_frame, hb=self.hover_bg, ob=self.original_bg, ign=[icon_label]:
                        apply_hover_effect(frm, hb, ob, ign))
        entry_frame.bind("<Leave>",
                        lambda e, frm=entry_frame, ob=self.original_bg, ign=[icon_label]:
                        remove_hover_effect(frm, ob, ign))
        entry_frame.bind("<Button-1>", click_handler)


        widgets_to_set_cursor = [icon_label, title_label]
        for widget in widgets_to_set_cursor:
            if widget and widget.winfo_exists():
                try:
                    widget.config(cursor="hand2")
                    widget.bind("<Button-1>", click_handler)
                except tk.TclError: pass

        return entry_frame

    def _on_game_select(self, game_id, event=None):
        """Handles the click event on a game entry in the library list"""
        print(f"Library: Selected game ID: {game_id}")
        try:
            game_details = self.db_manager.fetch_game_details(game_id)
            if game_details:
                self._display_game_details(game_details)
            else:
                messagebox.showwarning("Не знайдено", f"Не вдалося знайти деталі гри з ID: {game_id}")
                self._display_placeholder_details()
        except AttributeError:
             messagebox.showerror("Помилка", "Функція отримання деталей гри не реалізована.")
             self._display_placeholder_details()
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі гри:\n{e}")
            self._display_placeholder_details()

    def _display_placeholder_details(self):
        """Clears the right frame and displays a placeholder message"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        placeholder_label = tk.Label(self.right_frame, text="Виберіть гру зі списку зліва", font=self.detail_font, fg="grey", bg=self.original_bg)
        placeholder_label.pack(pady=50, padx=20)


    def _display_game_details(self, game_data):
        """Clears the right frame and displays the details for the selected game"""    
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        game_id = game_data.get('game_id')

        detail_img_label = tk.Label(self.right_frame, background=self.original_bg)
        img_filename = game_data.get('image')
        tk_detail_image = load_image_cached(
            cache_dict=self._image_references,
            image_filename=img_filename,
            folder_path=self.image_folder_path,
            size=self.detail_icon_size,
            placeholder_image=self.placeholder_image_detail 
        )
        
        if tk_detail_image:
             detail_img_label.config(image=tk_detail_image)
             detail_img_label.image = tk_detail_image
        else:
             detail_img_label.config(text="Немає зображення", font=self.ui_font, width=40, height=10)
        detail_img_label.pack(pady=(0, 15))

        title_label = tk.Label(self.right_frame, text=game_data.get('title', '...'), font=self.title_font_detail, bg=self.original_bg)
        title_label.pack(pady=(0, 20))

        play_button = ttk.Button(self.right_frame, text="Грати", command=partial(self._play_game, game_id))
        play_button.pack(pady=10)

    def _play_game(self, game_id):
        """Placeholder action for when the "Play" button is clicked"""
        print(f"Attempting to 'Play' game with ID: {game_id}")
        messagebox.showinfo("Запуск гри", f"Запуск гри з ID: {game_id}\n(Реалізація відсутня)")


    def load_library_games(self):
        """
        Fetches the list of purchased games for the user and populates the
        left list pane using the create_scrollable_list utility.
        """
        print("LibraryTab: Loading library games...")
        games_data = []
        try:
            games_data = self.db_manager.fetch_purchased_games(self.user_id)
            print(f"DEBUG LibraryTab: Fetched {len(games_data) if games_data else 0} games.")
        except AttributeError:
            print("DB Error: fetch_purchased_games method missing.")
            games_data = None
        except Exception as e:
            print(f"DB Error fetching purchased games: {e}")
            games_data = None

        self.library_canvas, self.library_list_frame, self._game_widgets_library = create_scrollable_list(
            parent=self.library_list_container,
            item_creation_func=self._create_library_entry,
            item_data_list=games_data,
            bg_color=self.original_bg,
            placeholder_text="Ваша бібліотека порожня.",
            placeholder_font=self.ui_font,
            item_pack_config={'fill': tk.X, 'pady': 0}
        )
        print(f"LibraryTab: List updated. Widgets created: {len(self._game_widgets_library)}")
    
    def after(self, ms, func):
        """Wrapper for the parent widget's 'after' method"""
        self.parent.after(ms, func)
