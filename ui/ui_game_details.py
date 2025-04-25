import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from PIL import Image, ImageTk
from decimal import Decimal, InvalidOperation

class GameDetailView(tk.Frame):
    def __init__(self, parent, db_manager, user_id, game_id, game_data,
                 image_cache, placeholder_list, placeholder_detail,
                 image_folder, placeholder_image_path, placeholder_image_name,
                 fonts, colors, styles,
                 scroll_target_canvas, 
                 **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.db_manager = db_manager
        self.user_id = user_id
        self.game_id = game_id
        self.game_data = game_data
        self._image_references = image_cache
        self.placeholder_image_list = placeholder_list
        self.placeholder_image_detail = placeholder_detail
        self.image_folder = image_folder
        self.placeholder_path = placeholder_image_path
        self.placeholder_name = placeholder_image_name
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.scroll_target_canvas = scroll_target_canvas 

        self.ui_font = self.fonts.get('ui', ("Verdana", 10))
        self.title_font = self.fonts.get('title', ("Verdana", 16, "bold"))
        self.detail_font = self.fonts.get('detail', ("Verdana", 11))
        self.price_font = self.fonts.get('price', ("Verdana", 12))
        self.review_author_font = self.fonts.get('review_author', ("Verdana", 9, "bold"))
        self.review_text_font = self.fonts.get('review_text', ("Verdana", 9))
        self.description_font = self.fonts.get('description', ("Verdana", 10))
        self.review_input_font = self.fonts.get('review_input', ("Verdana", 10))

        self.original_bg = self.colors.get('original_bg', 'white')
        self.no_reviews_message = " Рецензій ще немає."
        self.detail_icon_size = (160, 160)
        self.custom_button_style = self.styles.get('custom_button', 'TButton')

        self.title_label = None
        self.desc_content_label = None
        self.genres_content_label = None
        self.platforms_content_label = None
        self.reviews_frame = None
        self.price_buy_frame = None
        self.review_text_widget = None

        self._setup_ui()
        self._load_reviews()

    def _update_wraplengths(self, event=None):
        main_frame_width = self.winfo_width()
        content_width = main_frame_width - 20
        if content_width < 20: content_width = 10

        if self.desc_content_label:
            self.desc_content_label.config(wraplength=content_width)
        if self.genres_content_label:
            self.genres_content_label.config(wraplength=content_width)
        if self.platforms_content_label:
            self.platforms_content_label.config(wraplength=content_width)

        if self.title_label and self.title_label.master.winfo_exists():
            icon_width = self.detail_icon_size[0]
            padding = 40
            title_available_width = main_frame_width - icon_width - padding
            if title_available_width < 20: title_available_width = 10
            self.title_label.config(wraplength=title_available_width)

    def _handle_mousewheel(self, event):
        if not self.scroll_target_canvas:
            return
        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return
        self.scroll_target_canvas.yview_scroll(delta, "units")
        return "break"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        current_row = 0

        top_info_frame = tk.Frame(self, bg=self.original_bg)
        top_info_frame.grid(row=current_row, column=0, sticky='ew', padx=10)
        top_info_frame.grid_columnconfigure(1, weight=1)

        icon_label = tk.Label(top_info_frame, background=self.original_bg)
        tk_detail_image = self._get_image(self.game_data.get('image'), size=self.detail_icon_size)
        if tk_detail_image:
            icon_label.config(image=tk_detail_image); icon_label.image = tk_detail_image
        else:
            icon_label.config(text="Фото?", font=self.ui_font, width=20, height=10)
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 20), pady=5, sticky='nw')

        info_frame = tk.Frame(top_info_frame, background=self.original_bg)
        info_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', pady=(5, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(info_frame, text=self.game_data.get('title', 'Назва невідома'),
                                    font=self.title_font, background=self.original_bg,
                                    justify=tk.LEFT, anchor='nw')
        self.title_label.grid(row=0, column=0, sticky='nw')

        self.price_buy_frame = tk.Frame(info_frame, background=self.original_bg)
        self.price_buy_frame.grid(row=1, column=0, sticky='w', pady=(15, 0))

        is_owned = False
        try:
            if self.user_id is not None and self.game_id is not None:
                is_owned = self.db_manager.check_ownership(self.user_id, self.game_id)
        except Exception as e:
            print(f"Error checking ownership: {e}")

        if is_owned:
            tk.Label(self.price_buy_frame, text="✔ У бібліотеці", font=self.detail_font, bg=self.original_bg, fg="green").pack(side=tk.LEFT, anchor='w')
        else:
            price = self.game_data.get('price')
            price_text_raw = "N/A"
            if price is None: price_text_raw = "N/A"
            elif isinstance(price, (int, float, Decimal)) and float(price) == 0.0: price_text_raw = "Безкоштовно"
            else:
                try: price_text_raw = f"{float(price):.2f}₴"
                except (ValueError, TypeError): price_text_raw = "N/A"

            if price_text_raw != "N/A":
                 tk.Label(self.price_buy_frame, text=price_text_raw, font=self.detail_font, bg=self.original_bg).pack(side=tk.LEFT, anchor='w')
                 buy_button = ttk.Button(self.price_buy_frame, text="Придбати", style=self.custom_button_style, command=self._buy_game)
                 if price_text_raw == "Безкоштовно": buy_button.config(text="Отримати")
                 buy_button.pack(side=tk.LEFT, padx=(15, 0), anchor='w')
            else:
                 tk.Label(self.price_buy_frame, text=f"Статус: {self.game_data.get('status', 'N/A')}", font=self.detail_font, bg=self.original_bg).pack(side=tk.LEFT, anchor='w')

        current_row += 1

        separator1 = ttk.Separator(self, orient='horizontal')
        separator1.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(15, 10))
        current_row += 1

        desc_label = tk.Label(self, text="Опис:", font=("Verdana", 12, "bold"), background=self.original_bg)
        desc_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5))
        current_row += 1
        description = self.game_data.get('description', 'Опис відсутній.')
        self.desc_content_label = tk.Label(self, text=description, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg)
        self.desc_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
        current_row += 1

        separator2 = ttk.Separator(self, orient='horizontal')
        separator2.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10)
        current_row += 1

        genres_label = tk.Label(self, text="Жанри:", font=("Verdana", 12, "bold"), background=self.original_bg)
        genres_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5))
        current_row += 1
        genres_text = self.game_data.get('genres', 'Не вказано')
        self.genres_content_label = tk.Label(self, text=genres_text, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg)
        self.genres_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
        current_row += 1

        separator3 = ttk.Separator(self, orient='horizontal')
        separator3.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10)
        current_row += 1

        platforms_label = tk.Label(self, text="Платформи:", font=("Verdana", 12, "bold"), background=self.original_bg)
        platforms_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5))
        current_row += 1
        platforms_text = self.game_data.get('platforms', 'Не вказано')
        self.platforms_content_label = tk.Label(self, text=platforms_text, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg)
        self.platforms_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
        current_row += 1

        separator4 = ttk.Separator(self, orient='horizontal')
        separator4.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10)
        current_row += 1

        reviews_label = tk.Label(self, text="Рецензії:", font=("Verdana", 12, "bold"), background=self.original_bg)
        reviews_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(5, 5))
        current_row += 1
        self.reviews_frame = tk.Frame(self, background=self.original_bg)
        self.reviews_frame.grid(row=current_row, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.reviews_frame.grid_columnconfigure(0, weight=1)
        current_row += 1

        separator5 = ttk.Separator(self, orient='horizontal')
        separator5.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10)
        current_row += 1

        write_review_label = tk.Label(self, text="Написати рецензію:", font=("Verdana", 12, "bold"), background=self.original_bg)
        write_review_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(5, 5))
        current_row += 1
        self.review_text_widget = scrolledtext.ScrolledText(
            self, height=6, font=self.review_input_font, wrap=tk.WORD,
            borderwidth=1, relief=tk.SOLID, highlightthickness=0
        )
        self.review_text_widget.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 5))
        self.review_text_widget.bind("<MouseWheel>", self._handle_mousewheel)
        self.review_text_widget.bind("<Button-4>", self._handle_mousewheel)
        self.review_text_widget.bind("<Button-5>", self._handle_mousewheel)
        current_row += 1
        post_review_button = ttk.Button(
            self, text="Надіслати рецензію", command=self._post_review,
            style=self.custom_button_style
        )
        post_review_button.grid(row=current_row, column=0, sticky='e', padx=10, pady=(0, 10))
        current_row += 1

        widgets_to_bind_scroll = [
            self, top_info_frame, icon_label, info_frame, self.title_label,
            self.price_buy_frame, desc_label, self.desc_content_label,
            genres_label, self.genres_content_label, platforms_label,
            self.platforms_content_label, reviews_label, self.reviews_frame,
            write_review_label, post_review_button
        ]

        if self.price_buy_frame:
             for child in self.price_buy_frame.winfo_children():
                  if isinstance(child, (tk.Label, tk.Frame, ttk.Button)):
                     widgets_to_bind_scroll.append(child)

        for widget in widgets_to_bind_scroll:
             if widget and widget.winfo_exists():
                 try: 
                     widget.bind("<MouseWheel>", self._handle_mousewheel)
                     widget.bind("<Button-4>", self._handle_mousewheel)
                     widget.bind("<Button-5>", self._handle_mousewheel)
                 except tk.TclError as e:
                      print(f"Warning: Could not bind scroll to {widget}: {e}")

        self.after_idle(self._update_wraplengths)

    def _load_reviews(self):
        if not self.reviews_frame:
            print("Error: reviews_frame is not initialized yet in _load_reviews.")
            return
        
        for widget in self.reviews_frame.winfo_children():
            widget.destroy()

        if self.game_id is None:
            print("Cannot load reviews: game_id is None")
            error_label = tk.Label(self.reviews_frame, text="Помилка: ID гри не визначено.", fg="red", bg=self.original_bg)
            error_label.pack(anchor='w', pady=5)
            return

        print(f"Loading reviews for game_id: {self.game_id}")
        reviews_data = []
        try:
            if self.game_id == 1:
                reviews_data = [('User1', 'Great game!', '2023-10-27'), ('User2', 'A bit buggy.', '2023-10-26'), ('LongReviewer', 'This game has a lot of potential, but the developers need to fix the performance issues on older hardware. The story is engaging, and the core gameplay loop is fun, however, repetitive quests can become tedious later on.', '2023-10-25')]
            elif self.game_id == 2:
                  reviews_data = [('Tester', 'Nice graphics.', '2023-10-25')]
            else:
                  reviews_data = []
            print(f"Fetched reviews: {reviews_data}")

        except AttributeError:
            print("DB manager does not have 'fetch_game_reviews' method (using placeholder).")
            reviews_data = [("System", "Error loading reviews (DB method missing).", "")]
        except Exception as e:
            print(f"Error fetching reviews from DB: {e}")
            reviews_data = [("System", f"Error loading reviews: {e}", "")]

        if not reviews_data:
            no_reviews_label = tk.Label(self.reviews_frame, text=self.no_reviews_message, font=self.fonts.get('ui', ("Verdana", 10)), fg="grey", bg=self.original_bg)
            no_reviews_label.pack(anchor='w', pady=5)
        else:
            review_text_labels = []
            for review in reviews_data:
                try:
                    if isinstance(review, (list, tuple)) and len(review) >= 2: 
                        user = review[0]
                        text = review[1]
                        date = review[2] if len(review) > 2 else None

                        review_entry_frame = tk.Frame(self.reviews_frame, background=self.original_bg)
                        review_entry_frame.pack(fill='x', pady=(5, 10)) 
                        review_entry_frame.grid_columnconfigure(0, weight=1)

                        author_text = f"{user}" + (f" ({date})" if date else "")
                        author_label = tk.Label(review_entry_frame, text=author_text, font=self.fonts.get('comment_author', ("Verdana", 9, "bold")), anchor='w', bg=self.original_bg)
                        author_label.grid(row=0, column=0, sticky='w')

                        review_text_label = tk.Label(review_entry_frame, text=text, font=self.fonts.get('comment_text', ("Verdana", 9)), anchor='nw', justify=tk.LEFT, bg=self.original_bg)
                        review_text_label.grid(row=1, column=0, sticky='ew')
                        review_text_labels.append(review_text_label) 
                        
                    else:
                        print(f"Skipping invalid review data format: {review}")
                except Exception as e:
                     print(f"Error processing review '{review}': {e}")
                     error_label = tk.Label(self.reviews_frame, text="[Помилка відображення рецензії]", fg="red", bg=self.original_bg)
                     error_label.pack(anchor='w', pady=2)
                    
            def _update_review_wraplengths(event):
                width = event.width - 10
                if width < 20: width = 10
                for lbl in review_text_labels:
                    lbl.config(wraplength=width)
                    
            self.reviews_frame.unbind('<Configure>')
            self.reviews_frame.bind('<Configure>', _update_review_wraplengths)

    def _post_review(self):
        """Handles posting a new review."""
        if not self.review_text_widget:
            print("Error: Review text widget not found.")
            return

        review_text = self.review_text_widget.get("1.0", tk.END).strip()

        if not review_text:
            messagebox.showwarning("Порожня рецензія", "Будь ласка, введіть текст рецензії.")
            return
        if self.game_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID гри для рецензії.")
            return
        if self.user_id is None:
             messagebox.showerror("Помилка", "Не вдалося визначити користувача.")
             return

        print(f"Posting review for game_id: {self.game_id}, user_id: {self.user_id}")
        success = False
        try:
            print(f"Simulating adding review: User {self.user_id}, Game {self.game_id}, Text: '{review_text[:50]}...'")
            success = True

            if success:
                 print("Review added successfully (simulated).")
                 self.review_text_widget.delete("1.0", tk.END)
                 messagebox.showinfo("Успіх", "Вашу рецензію надіслано!")
                 self._load_reviews()
            else:
                 print("Failed to add review (simulated).")
                 messagebox.showerror("Помилка", "Не вдалося додати рецензію.")

        except AttributeError:
            print("DB manager does not have 'add_review' method.")
            messagebox.showerror("Помилка", "Функціонал додавання рецензій не реалізовано (DB method missing).")
        except Exception as e:
            print(f"Error posting review to DB: {e}")
            messagebox.showerror("Помилка бази даних", f"Не вдалося додати рецензію:\n{e}")

    def _buy_game(self):
        """Handles the 'Buy'/'Get' button click."""
        if self.game_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID гри.")
            return
        if self.user_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити користувача.")
            return

        price = self.game_data.get('price')
        title = self.game_data.get('title', 'цієї гри')
        is_free = False
        price_numeric = Decimal('0.00')
        try:
            if price is not None and float(price) > 0.0:
                 price_numeric = Decimal(str(price)).quantize(Decimal("0.01"))
                 action = "придбати"
                 price_text = f"за {price_numeric}₴"
            else:
                 is_free = True
                 action = "додати до бібліотеки"
                 price_text = "безкоштовно"
        except (ValueError, TypeError, InvalidOperation):
             messagebox.showerror("Помилка ціни", f"Некоректний формат ціни для гри: {price}")
             return

        confirm = messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете {action} гру '{title}' {price_text}?")

        if confirm:
            print(f"Attempting to '{action}' game_id: {self.game_id} for user_id: {self.user_id} at price {price_numeric}")
            success = False
            try:
                success = self.db_manager.purchase_game(self.user_id, self.game_id, price_numeric)

                if success:
                     messagebox.showinfo("Успіх", f"Гру '{title}' успішно {('додано до' if is_free else 'придбано та додано до')} вашої бібліотеки!")
                     self._update_price_buy_area()

                else:
                    messagebox.showerror("Помилка", f"Не вдалося {action} гру. Дивіться консоль для деталей.")

            except AttributeError:
                 messagebox.showerror("Помилка", "Функціонал покупки/додавання гри не реалізовано (DB method missing).")
            except Exception as e:
                 messagebox.showerror("Помилка", f"Під час процесу покупки сталася помилка:\n{e}")


    def _update_price_buy_area(self):
        """Clears and rebuilds the content of the price_buy_frame."""
        if not self.price_buy_frame or not self.price_buy_frame.winfo_exists():
            print("Error: Could not find price_buy_frame to update (reference missing or destroyed).")
            try:
                info_frame = self.winfo_children()[1].winfo_children()[1]
                self.price_buy_frame = info_frame.winfo_children()[1]
            except:
                 print("Error: Fallback attempt to find price_buy_frame failed.")
                 return

        for widget in self.price_buy_frame.winfo_children():
            widget.destroy()
        in_library_label = tk.Label(self.price_buy_frame, text="У бібліотеці",
                                    font=self.detail_font, background=self.original_bg, fg="green")
        in_library_label.pack(side=tk.LEFT, anchor='w')

    def _load_image_internal(self, image_filename, full_path, size=(64, 64), is_placeholder=False):
        placeholder_to_return = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image_list

        if not image_filename:
            return placeholder_to_return

        cache_key = f"{image_filename}_{size[0]}x{size[1]}"
        if cache_key in self._image_references:
            return self._image_references[cache_key]

        if full_path and os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self._image_references[cache_key] = photo_img
                
                return photo_img
            except Exception as e:
                print(f"Error loading image '{full_path}' (will use placeholder): {e}")
                return placeholder_to_return
        else:
            if not is_placeholder:
                print(f"Image file not found: {full_path} (using placeholder)")
            return placeholder_to_return

    def _get_image(self, image_filename, size=(64, 64)):
        placeholder_to_return = self.placeholder_image_detail if size == self.detail_icon_size else self.placeholder_image_list

        if not image_filename:
            return placeholder_to_return
        if self.image_folder is None:
            print("IMAGE_FOLDER is not set, cannot load image.")
            return placeholder_to_return

        if os.path.isabs(image_filename) and os.path.exists(image_filename):
            full_path = image_filename
        else:
            full_path = os.path.join(self.image_folder, image_filename)

        is_placeholder = (image_filename == self.placeholder_name)

        return self._load_image_internal(image_filename, full_path, size=size, is_placeholder=is_placeholder)