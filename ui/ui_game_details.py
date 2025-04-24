import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from decimal import Decimal, InvalidOperation

class GameDetailView(tk.Frame):
    def __init__(self, parent, db_manager, user_id, game_id, game_data,
                 image_cache, placeholder_list, placeholder_detail,
                 image_folder, placeholder_path, placeholder_name,
                 fonts, colors, styles, back_command, **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.db_manager = db_manager
        self.user_id = user_id
        self.game_id = game_id
        self.game_data = game_data
        self._image_references = image_cache 
        self.placeholder_image_list = placeholder_list
        self.placeholder_image_detail = placeholder_detail
        self.image_folder = image_folder
        self.placeholder_path = placeholder_path
        self.placeholder_name = placeholder_name
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.back_command = back_command 

        self.ui_font = self.fonts.get('ui', ("Verdana", 10))
        self.title_font = self.fonts.get('title', ("Verdana", 16, "bold"))
        self.detail_font = self.fonts.get('detail', ("Verdana", 11))
        self.price_font = self.fonts.get('price', ("Verdana", 12))
        self.comment_font = self.fonts.get('comment', ("Verdana", 9))
        self.description_font = self.fonts.get('description', ("Verdana", 10))

        self.original_bg = self.colors.get('original_bg', 'white')
        self.listbox_select_bg = self.colors.get('listbox_select_bg', self.original_bg)
        self.listbox_select_fg = self.colors.get('listbox_select_fg', 'black')
        self.no_comments_fg = self.colors.get('no_comments_fg', 'grey')
        self.comment_fg = self.colors.get('comment_fg', 'black')
        self.no_comments_message = self.colors.get('no_comments_message', " Коментарів ще немає.")

        self.detail_icon_size = (160, 160)

        self.custom_button_style = self.styles.get('custom_button', 'TButton')

        self._setup_ui()
        self._load_comments()

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(7, weight=1) 

        back_button = ttk.Button(self, text="< Назад", command=self.back_command, style=self.custom_button_style)
        back_button.grid(row=0, column=0, columnspan=2, pady=(5, 15), padx=5, sticky='w')

        icon_label = tk.Label(self, background=self.original_bg)
        img_filename = self.game_data.get('image')
        tk_detail_image = self._get_image(img_filename, size=self.detail_icon_size)

        if tk_detail_image:
            icon_label.config(image=tk_detail_image)
            icon_label.image = tk_detail_image
        else:
            icon_label.config(text="Немає фото", font=self.ui_font,
                              width=round(self.detail_icon_size[0]/8),
                              height=round(self.detail_icon_size[1]/15))
        icon_label.grid(row=1, column=0, padx=(10, 20), pady=5, sticky='nw')

        info_frame = tk.Frame(self, background=self.original_bg)
        info_frame.grid(row=1, column=1, sticky='nsew', pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(info_frame, text=self.game_data.get('title', 'Назва невідома'),
                               font=self.title_font, background=self.original_bg,
                               wraplength=self.winfo_width()-self.detail_icon_size[0]-100,
                               justify=tk.LEFT, anchor='nw')
        title_label.grid(row=0, column=0, sticky='nw')
        self.bind('<Configure>', lambda e: title_label.config(wraplength=self.winfo_width() - self.detail_icon_size[0] - 50 if self.winfo_width() > self.detail_icon_size[0] + 50 else 100))

        price_buy_frame = tk.Frame(info_frame, background=self.original_bg)
        price_buy_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=(15, 0))
        
        price = self.game_data.get('price')
        
        is_owned = False
        try:
            if self.user_id is not None and self.game_id is not None:
                is_owned = self.db_manager.check_ownership(self.user_id, self.game_id)
            else:
                print("Warning: Cannot check ownership, user_id or game_id is None.")
        except AttributeError:
            print("Warning: DB manager does not have 'check_ownership' method. Assuming not owned.")
        except Exception as e:
            print(f"Error checking ownership, assuming not owned: {e}")

        if is_owned:
            in_library_label = tk.Label(price_buy_frame, text="У бібліотеці",
                                        font=self.detail_font, background=self.original_bg, fg="green")
            in_library_label.pack(side=tk.LEFT, anchor='w')
        else:
            price = self.game_data.get('price') 
            price_text_raw = "N/A" 

            if price is None:
                price_text_raw = "N/A"
            elif isinstance(price, (int, float, Decimal)) and float(price) == 0.0:
                price_text_raw = "Безкоштовно"
            else:
                try:
                    price_text_raw = f"{float(price):.2f}₴"
                except (ValueError, TypeError):
                    price_text_raw = "N/A"

            if price_text_raw != "N/A":
                price_label_detail = tk.Label(price_buy_frame, text=price_text_raw, font=self.detail_font, background=self.original_bg)
                price_label_detail.pack(side=tk.LEFT, anchor='w')
                buy_button = ttk.Button(price_buy_frame, text="Придбати", style=self.custom_button_style, command=self._buy_game)
                if price_text_raw == "Безкоштовно":
                    buy_button.config(text="Отримати")
                buy_button.pack(side=tk.LEFT, padx=(15, 0), anchor='w')
            else:
                status_text = f"Статус: {self.game_data.get('status', 'N/A')}"
                status_label = tk.Label(price_buy_frame, text=status_text, font=self.detail_font, background=self.original_bg)
                status_label.pack(side=tk.LEFT, anchor='w')

        separator1 = ttk.Separator(self, orient='horizontal')
        separator1.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=15)

        desc_label = tk.Label(self, text="Опис:", font=("Verdana", 12, "bold"), background=self.original_bg)
        desc_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 5))

        description = self.game_data.get('description', 'Опис відсутній.')

        desc_content_label = tk.Label(self, text=description, font=self.description_font,
                                      wraplength=self.winfo_width() - 40,
                                      justify=tk.LEFT, anchor='nw', background=self.original_bg)
        desc_content_label.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=10, pady=(0, 10))
        self.bind('<Configure>', lambda e: desc_content_label.config(wraplength=self.winfo_width() - 40 if self.winfo_width() > 50 else 10))


        self.grid_rowconfigure(4, weight=0)

        separator2 = ttk.Separator(self, orient='horizontal')
        separator2.grid(row=5, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        comments_label = tk.Label(self, text="Коментарі:", font=("Verdana", 12, "bold"), background=self.original_bg)
        comments_label.grid(row=6, column=0, columnspan=2, sticky='w', padx=10, pady=(5, 2))

        comments_list_frame = tk.Frame(self)
        comments_list_frame.grid(row=7, column=0, columnspan=2, sticky='nsew', padx=10)
        comments_list_frame.grid_rowconfigure(0, weight=1)
        comments_list_frame.grid_columnconfigure(0, weight=1)

        comments_scrollbar = ttk.Scrollbar(comments_list_frame)
        comments_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.comments_listbox = tk.Listbox(comments_list_frame, yscrollcommand=comments_scrollbar.set,
                                           font=self.comment_font, height=6, background=self.original_bg,
                                           selectbackground=self.listbox_select_bg,
                                           selectforeground=self.listbox_select_fg,
                                           activestyle='none', highlightthickness=0, borderwidth=0)
        self.comments_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        comments_scrollbar.config(command=self.comments_listbox.yview)
        self.comments_listbox.bind("<<ListboxSelect>>", self._on_comment_select)
        self.comments_listbox.bind("<MouseWheel>", self._on_listbox_mousewheel)
        self.comments_listbox.bind("<Button-4>", self._on_listbox_mousewheel)
        self.comments_listbox.bind("<Button-5>", self._on_listbox_mousewheel)

        comment_input_frame = tk.Frame(self, background=self.original_bg)
        comment_input_frame.grid(row=8, column=0, columnspan=2, sticky='ew', padx=10, pady=(5, 10))
        comment_input_frame.grid_columnconfigure(0, weight=1)

        self.comment_entry = tk.Entry(comment_input_frame, font=self.ui_font, width=60)
        self.comment_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.comment_entry.bind("<Return>", lambda event: self._post_comment())

        post_comment_button = ttk.Button(comment_input_frame, text="Надіслати", command=self._post_comment, style=self.custom_button_style)
        post_comment_button.grid(row=0, column=1, sticky='e')

    def _on_listbox_mousewheel(self, event):
        """Прокручування списку коментарів колесом миші."""
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.comments_listbox.yview_scroll(delta, "units")
        return "break"

    def _on_comment_select(self, event=None):
        """Скидає виділення, якщо вибрано 'Коментарів немає'."""
        widget = self.comments_listbox
        selected_indices = widget.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        item_text = widget.get(index)
        if item_text == self.no_comments_message:
            widget.selection_clear(index)
            widget.itemconfig(index, {'fg': self.no_comments_fg})


    def _load_comments(self):
        self.comments_listbox.delete(0, tk.END)
        if self.game_id is None:
            print("Cannot load comments: game_id is None")
            return

        print(f"Loading comments for game_id: {self.game_id}")
        comments_data = []
        try:
            if self.game_id == 1:
                comments_data = [('User1', 'Great game!', '2023-10-27'), ('User2', 'A bit buggy.', '2023-10-26')]
            elif self.game_id == 2:
                comments_data = [('Tester', 'Nice graphics.', '2023-10-25')]
            else:
                comments_data = [] 
            print(f"Fetched comments: {comments_data}")

        except AttributeError:
            print("DB manager does not have 'fetch_game_comments' method (using placeholder).")
            comments_data = [("System", "Error loading comments (DB method missing).", "")]
        except Exception as e:
            print(f"Error fetching comments from DB: {e}")
            comments_data = [("System", f"Error loading comments: {e}", "")]

        if not comments_data:
            self.comments_listbox.insert(tk.END, self.no_comments_message)
            self.comments_listbox.itemconfig(tk.END, {'fg': self.no_comments_fg})
        else:
            for comment in comments_data:
                try:
                    if isinstance(comment, (list, tuple)) and len(comment) == 3:
                        user, text, date = comment
                        display_string = f" {user} ({date}): {text}" if date else f" {user}: {text}"
                        self.comments_listbox.insert(tk.END, display_string)
                        self.comments_listbox.itemconfig(tk.END, {'fg': self.comment_fg})
                    else:
                        print(f"Skipping invalid comment data: {comment}")
                        self.comments_listbox.insert(tk.END, " [Недійсний формат коментаря] ")
                        self.comments_listbox.itemconfig(tk.END, {'fg': 'red'})
                except Exception as e:
                     print(f"Error processing comment '{comment}': {e}")
                     self.comments_listbox.insert(tk.END, " [Помилка відображення коментаря] ")
                     self.comments_listbox.itemconfig(tk.END, {'fg': 'red'})

    def _post_comment(self):
        comment_text = self.comment_entry.get().strip()
        if not comment_text:
            messagebox.showwarning("Порожній коментар", "Будь ласка, введіть текст коментаря.")
            return
        if self.game_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID гри для коментаря.")
            return
        if self.user_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID користувача.")
            return

        print(f"Posting comment for game_id: {self.game_id}, user_id: {self.user_id}")
        success = False
        try:
            print(f"Simulating adding comment: User {self.user_id}, Game {self.game_id}, Text: '{comment_text}'")
            success = True 

            if success:
                print("Comment added successfully (simulated).")
                self.comment_entry.delete(0, tk.END)
                self._load_comments()
            else:
                print("Failed to add comment (simulated).")
                messagebox.showerror("Помилка", "Не вдалося додати коментар.")

        except AttributeError:
            print("DB manager does not have 'add_comment' method.")
            messagebox.showerror("Помилка", "Функціонал додавання коментарів не реалізовано (DB method missing).")
        except Exception as e:
            print(f"Error posting comment to DB: {e}")
            messagebox.showerror("Помилка бази даних", f"Не вдалося додати коментар:\n{e}")

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
        try:
            info_frame = self.winfo_children()[2] 
            price_buy_frame = info_frame.winfo_children()[1] 
        except IndexError:
            print("Error: Could not find price_buy_frame to update.")
            return

        for widget in price_buy_frame.winfo_children():
            widget.destroy()

        in_library_label = tk.Label(price_buy_frame, text="✔ У бібліотеці",
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