import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from functools import partial
import decimal

class LibraryTab:
    def __init__(self, parent, db_manager, user_id, image_cache, placeholder_list, placeholder_detail, image_folder_path, fonts, colors):
        self.parent = parent
        self.db_manager = db_manager
        self.user_id = user_id

        self._image_references = image_cache
        self.placeholder_image_list = placeholder_list
        self.placeholder_image_detail = placeholder_detail
        self.image_folder_path = image_folder_path
        self._game_widgets_library = []

        self.original_bg = colors.get('original_bg', "white")
        self.hover_bg = colors.get('hover_bg', "#f0f0f0")
        self.list_icon_size = (48, 48)
        self.detail_icon_size = (300, 180)

        self.ui_font = fonts.get('ui', ("Verdana", 10))
        self.title_font_list = fonts.get('list_title', ("Verdana", 11, "bold"))
        self.title_font_detail = fonts.get('detail_title', ("Verdana", 14, "bold"))
        self.detail_font = fonts.get('detail', ("Verdana", 11))

        self.paned_window = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=1, bg=self.original_bg)
        
        desired_left_width = 220
        min_left_width = 200
        self.left_frame = tk.Frame(self.paned_window, width=desired_left_width, bg=self.original_bg) 
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.paned_window.add(self.left_frame, width=desired_left_width, minsize=min_left_width, stretch="never")

        self.library_canvas, self.library_list_frame = self._create_scrollable_list_frame(self.left_frame)

        self.right_frame = tk.Frame(self.paned_window, bg=self.original_bg, padx=15, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.paned_window.add(self.right_frame, minsize=300, stretch="always")

        self._display_placeholder_details()

        self.load_library_games()


    def _create_scrollable_list_frame(self, parent):
        canvas_scrollbar_frame = tk.Frame(parent, bg=self.original_bg)
        canvas_scrollbar_frame.grid(row=0, column=0, sticky='nsew')
        canvas_scrollbar_frame.grid_rowconfigure(0, weight=1)
        canvas_scrollbar_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background=self.original_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, background=self.original_bg)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def _on_inner_frame_configure(event=None): canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_inner_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_frame_id, width=event.width)
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
        inner_frame.bind("<MouseWheel>", _on_inner_mousewheel)
        inner_frame.bind("<Button-4>", _on_inner_mousewheel)
        inner_frame.bind("<Button-5>", _on_inner_mousewheel)
        canvas.bind("<MouseWheel>", _on_inner_mousewheel)
        canvas.bind("<Button-4>", _on_inner_mousewheel)
        canvas.bind("<Button-5>", _on_inner_mousewheel)


        return canvas, inner_frame

    def _on_enter(self, event, frame):
        frame.config(background=self.hover_bg)
        for widget in frame.winfo_children():
             if isinstance(widget, tk.Label): widget.config(background=self.hover_bg)

    def _on_leave(self, event, frame):
        frame.config(background=self.original_bg)
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label): widget.config(background=self.original_bg)

    def _create_library_entry(self, parent, game_data):
        try: game_id, title, _, _, image_filename = game_data
        except (ValueError, TypeError): print(f"...: {game_data}"); return None

        entry_frame = tk.Frame(parent, background=self.original_bg, cursor="hand2")
        entry_frame.pack(fill=tk.X, pady=1)

        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_image(image_filename, size=self.list_icon_size)
        if tk_image: icon_label.config(image=tk_image); icon_label.image = tk_image
        icon_label.pack(side=tk.LEFT, padx=5, pady=3)

        title_label = tk.Label(entry_frame, text=title, font=self.title_font_list, anchor="w", background=self.original_bg)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        click_handler = partial(self._on_game_select, game_id)
        enter_handler = partial(self._on_enter, frame=entry_frame)
        leave_handler = partial(self._on_leave, frame=entry_frame)

        widgets_to_bind = [entry_frame, icon_label, title_label]
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", click_handler)
            widget.bind("<Enter>", enter_handler)
            widget.bind("<Leave>", leave_handler)
            widget.bind("<MouseWheel>", self.parent.master.master._on_mousewheel)
            widget.bind("<Button-4>", self.parent.master.master._on_mousewheel)
            widget.bind("<Button-5>", self.parent.master.master._on_mousewheel)


        return entry_frame

    def _on_game_select(self, game_id, event=None):
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
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        placeholder_label = tk.Label(self.right_frame, text="Виберіть гру зі списку зліва", font=self.detail_font, fg="grey", bg=self.original_bg)
        placeholder_label.pack(pady=50, padx=20)


    def _display_game_details(self, game_data):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        game_id = game_data.get('game_id')

        detail_img_label = tk.Label(self.right_frame, background=self.original_bg)
        img_filename = game_data.get('image')
        tk_detail_image = self._get_image(img_filename, size=self.detail_icon_size)
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
        print(f"Attempting to 'Play' game with ID: {game_id}")
        messagebox.showinfo("Запуск гри", f"Запуск гри з ID: {game_id}\n(Потрібна інтеграція з реальними файлами гри)")


    def load_library_games(self):
        for widget in self.library_list_frame.winfo_children(): widget.destroy()
        self._game_widgets_library = []
        try:
            games_data = self.db_manager.fetch_purchased_games(self.user_id)
        except AttributeError: tk.Label(self.library_list_frame, text="...", fg="orange").pack(pady=20); print("DB: fetch_purchased_games..."); return
        except Exception as e: tk.Label(self.library_list_frame, text="...", fg="red").pack(pady=20); print(f"...: {e}"); return

        if games_data is None: tk.Label(self.library_list_frame, text="...", fg="red").pack(pady=20); print("DB: Failed fetch (Library)."); return
        if not games_data: tk.Label(self.library_list_frame, text="Ваша бібліотека порожня").pack(pady=20)
        else:
            for game in games_data:
                 if len(game) < 5: print(f"...: {game}"); continue
                 game_widget = self._create_library_entry(self.library_list_frame, game)
                 if game_widget: self._game_widgets_library.append(game_widget)

        self.library_list_frame.update_idletasks()
        self.library_canvas.configure(scrollregion=self.library_canvas.bbox("all"))

    def _load_image_internal(self, image_filename, full_path, size=(64, 64)):
        placeholder = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image_list
        if not image_filename: return placeholder
        cache_key = f"{image_filename}_{size[0]}x{size[1]}"
        if cache_key in self._image_references: return self._image_references[cache_key]
        if full_path and os.path.exists(full_path):
            try: img = Image.open(full_path); img = img.resize(size, Image.Resampling.LANCZOS); photo_img = ImageTk.PhotoImage(img); self._image_references[cache_key] = photo_img; return photo_img
            except Exception as e: print(f"... '{full_path}' ...: {e}"); return placeholder
        else: return placeholder

    def _get_image(self, image_filename, size=(64, 64)):
        placeholder = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image_list
        if not image_filename: return placeholder
        image_path = os.path.join(self.image_folder_path, image_filename)
        return self._load_image_internal(image_filename, image_path, size)