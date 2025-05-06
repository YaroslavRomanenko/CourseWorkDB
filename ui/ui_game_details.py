import tkinter as tk
import os
import decimal

from tkinter import ttk, messagebox, scrolledtext, simpledialog, Toplevel
from PIL import Image, ImageTk
from decimal import Decimal, InvalidOperation
from functools import partial
import traceback

from datetime import datetime
from .ui_utils import *

class GameDetailView(tk.Frame):
    def __init__(self, parent, db_manager, user_id, game_id, game_data,
                 image_cache, placeholder_list, placeholder_detail,
                 image_folder, placeholder_image_path, placeholder_image_name,
                 fonts, colors, styles,
                 scroll_target_canvas,
                 store_window_ref,
                 **kwargs):
        """Initializes the GameDetailView frame"""
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
        self.store_window_ref = store_window_ref

        self.can_edit = False
        if self.user_id and self.game_id:
            try:
                self.can_edit = self.db_manager.check_game_edit_permission(self.user_id, self.game_id)
                print(f"GameDetailView: User {self.user_id} can edit game {self.game_id}: {self.can_edit}")
            except Exception as e:
                print(f"Error checking edit permission in GameDetailView init: {e}")

        self.genre_names = []
        self.platform_names = []
        self.developer_names = []
        self.publisher_names = []
        if self.game_id is not None:
            try:
                self.genre_names = self.db_manager.fetch_game_genres(self.game_id)
                self.platform_names = self.db_manager.fetch_game_platforms(self.game_id)
                self.developer_names = self.db_manager.fetch_game_studios_by_role(self.game_id, 'Developer')
                self.publisher_names = self.db_manager.fetch_game_studios_by_role(self.game_id, 'Publisher')
            except AttributeError as ae:
                print(f"AttributeError fetching game details (maybe method missing?): {ae}")
            except Exception as e:
                print(f"Error fetching genres/platforms/studios during GameDetailView init: {e}")
                traceback.print_exc()

        self.ui_font = self.fonts.get('ui', ("Verdana", 10))
        self.title_font = self.fonts.get('title', ("Verdana", 16, "bold"))
        self.info_font = self.fonts.get('detail', ("Verdana", 10))
        self.detail_font = self.fonts.get('detail', ("Verdana", 11))
        self.dev_pub_font = self.fonts.get('comment', ("Verdana", 9))
        dev_pub_tuple = list(self.fonts.get('comment', ("Verdana", 9)))
        if len(dev_pub_tuple) == 2: dev_pub_tuple.append("bold")
        elif len(dev_pub_tuple) > 2: dev_pub_tuple[2] = f"{dev_pub_tuple[2]} bold".replace(" normal","").strip()
        self.dev_pub_bold_font = tuple(dev_pub_tuple)
        link_font_tuple = list(self.dev_pub_font)
        if len(link_font_tuple) == 2: link_font_tuple.append("underline")
        elif len(link_font_tuple) > 2: link_font_tuple[2] = f"{link_font_tuple[2]} underline".replace(" normal","").strip()
        self.dev_pub_link_font = tuple(link_font_tuple)
        self.price_font = self.fonts.get('price', ("Verdana", 12))
        self.review_author_font = self.fonts.get('review_author', ("Verdana", 9, "bold"))
        self.review_text_font = self.fonts.get('review_text', ("Verdana", 9))
        self.description_font = self.fonts.get('description', ("Verdana", 10))
        self.review_input_font = self.fonts.get('review_input', ("Verdana", 10))
        self.section_header_font = ("Verdana", 12, "bold")
        self.edit_button_font = self.fonts.get('ui', ("Verdana", 9))

        self.original_bg = self.colors.get('original_bg', 'white')
        self.link_fg = self.colors.get('link_fg', 'blue')
        self.no_reviews_message = " Рецензій ще немає."
        self.detail_icon_size = (160, 160)
        self.custom_button_style = self.styles.get('custom_button', 'TButton')

        self.title_label = None
        self.edit_button = None
        self.info_developer_prefix_label = None
        self.info_developer_names_label = None
        self.info_publisher_prefix_label = None
        self.info_publisher_names_label = None
        self.dev_pub_frame = None
        self.desc_content_label = None
        self.genres_content_label = None
        self.platforms_content_label = None
        self.price_buy_frame = None
        self.review_text_widget = None
        self.reviews_display_text = None

        self._setup_ui()
        self._load_reviews()

        self.bind("<Configure>", lambda e: self.after_idle(lambda: self._update_wraplengths(e.width)))

    def _update_wraplengths(self, container_width):
        """
        Adjusts the 'wraplength' option for various labels based on the
        current width of the container, ensuring text wraps correctly
        """
        try:
            if not self.winfo_exists(): return
            if not isinstance(container_width, (int, float)) or container_width <= 1:
                try:
                    self.update_idletasks()
                    container_width = self.winfo_width()
                    if container_width <= 1: return
                except Exception: return

            min_content_width = 100
            content_wraplength = max(min_content_width, container_width - 20)

            for label_widget in [self.desc_content_label, self.genres_content_label,
                                 self.platforms_content_label]:
                if label_widget and label_widget.winfo_exists():
                    current_wl = label_widget.cget("wraplength")
                    if current_wl != content_wraplength:
                        label_widget.config(wraplength=content_wraplength)

            info_frame_wraplength = content_wraplength
            prefix_col_width_approx = 80
            try:
                icon_width = self.detail_icon_size[0]
                info_frame_base_width = max(min_content_width, container_width - 10 - icon_width - 20 - 10)
                if self.title_label and self.title_label.winfo_exists():
                     current_wl = self.title_label.cget("wraplength")
                     if current_wl != info_frame_base_width:
                         self.title_label.config(wraplength=info_frame_base_width)

                names_wraplength = max(min_content_width, info_frame_base_width - prefix_col_width_approx)
                for label_widget in [self.info_developer_names_label, self.info_publisher_names_label]:
                    if label_widget and label_widget.winfo_exists():
                         current_wl = label_widget.cget("wraplength")
                         if current_wl != names_wraplength:
                             label_widget.config(wraplength=names_wraplength)

            except Exception as e:
                print(f"DEBUG: Error calculating info_frame_wraplength/names_wraplength: {e}")
                fallback_wl = max(min_content_width, container_width - 10 - (self.detail_icon_size[0] if self.detail_icon_size else 160) - 20 - 10)
                for label_widget in [self.title_label, self.info_developer_names_label, self.info_publisher_names_label]:
                    if label_widget and label_widget.winfo_exists():
                         label_widget.config(wraplength=fallback_wl)


        except tk.TclError as e:
            pass
        except Exception as e:
            print(f"DEBUG: Unexpected error in _update_wraplengths:")
            traceback.print_exc()

    def _setup_ui(self):
        """Creates and arranges all the widgets within the GameDetailView frame"""
        self.grid_columnconfigure(0, weight=1)
        current_row = 0
        initial_wraplength = 10000

        top_info_frame = tk.Frame(self, bg=self.original_bg)
        top_info_frame.grid(row=current_row, column=0, sticky='new', padx=10, pady=5)
        top_info_frame.grid_columnconfigure(1, weight=1)

        icon_label = tk.Label(top_info_frame, background=self.original_bg)
        tk_detail_image = load_image_cached(self._image_references,
                                    self.game_data.get('image'),
                                    self.image_folder,
                                    self.detail_icon_size,
                                    self.placeholder_image_detail)
        if tk_detail_image:
            icon_label.config(image=tk_detail_image); icon_label.image = tk_detail_image
        else:
            icon_label.config(text="Фото?", font=self.ui_font, width=20, height=10, relief="solid", borderwidth=1)
        icon_label.grid(row=0, column=0, rowspan=4, padx=(0, 20), pady=0, sticky='nw')

        info_frame = tk.Frame(top_info_frame, background=self.original_bg)
        info_frame.grid(row=0, column=1, rowspan=4, sticky='nsew', pady=0)
        info_frame.grid_columnconfigure(0, weight=1)
        info_row = 0

        title_edit_frame = tk.Frame(info_frame, background=self.original_bg)
        title_edit_frame.grid(row=info_row, column=0, sticky='nw', pady=(0, 5))
        title_edit_frame.grid_columnconfigure(0, weight=1)
        info_row += 1

        self.title_label = tk.Label(title_edit_frame, text=self.game_data.get('title', 'Назва невідома'),
                                     font=self.title_font, background=self.original_bg, justify=tk.LEFT, anchor='nw', wraplength=initial_wraplength)
        self.title_label.grid(row=0, column=0, sticky='nw')

        if self.can_edit:
            self.edit_button = ttk.Button(title_edit_frame, text="✏️ Редагувати",
                                          command=self._show_edit_dialog,
                                          style=self.styles.get('custom_button', 'TButton'),
                                          width=12
                                          )
            self.edit_button.grid(row=0, column=1, sticky='ne', padx=(10, 0))
            title_edit_frame.grid_columnconfigure(1, weight=0)

        review_count = self.game_data.get('review_count', 0)
        review_count_text = f"Відгуків: {review_count}"
        self.review_count_label = tk.Label(info_frame, text=review_count_text, font=self.fonts['comment'], background=self.original_bg, fg='grey', anchor='nw')
        self.review_count_label.grid(row=info_row, column=0, sticky='nw', pady=(0, 10)); info_row += 1

        self.price_buy_frame = tk.Frame(info_frame, background=self.original_bg)
        self.price_buy_frame.grid(row=info_row, column=0, sticky='nw', pady=(0, 10)); info_row += 1
        self._build_price_buy_content()

        self.dev_pub_frame = tk.Frame(info_frame, background=self.original_bg)
        self.dev_pub_frame.grid(row=info_row, column=0, sticky='nw', pady=(5, 0)); info_row += 1
        self.dev_pub_frame.grid_columnconfigure(0, weight=0)
        self.dev_pub_frame.grid_columnconfigure(1, weight=1)
        dev_pub_row = 0
        developer_text = ", ".join(self.developer_names) if self.developer_names else ""
        if developer_text:
            self.info_developer_prefix_label = tk.Label(self.dev_pub_frame, text="Розробник:", font=self.dev_pub_bold_font, background=self.original_bg, justify=tk.LEFT, anchor='nw')
            self.info_developer_prefix_label.grid(row=dev_pub_row, column=0, sticky='nw', padx=(0, 5))
            self.info_developer_names_label = tk.Label(self.dev_pub_frame, text=developer_text, font=self.dev_pub_link_font, fg=self.link_fg, cursor="hand2", background=self.original_bg, justify=tk.LEFT, anchor='nw', wraplength=initial_wraplength)
            self.info_developer_names_label.grid(row=dev_pub_row, column=1, sticky='nw')
            self.info_developer_names_label.bind("<Button-1>", partial(self._on_studio_click, studio_names=self.developer_names))
            dev_pub_row += 1
        else: self.info_developer_prefix_label = None; self.info_developer_names_label = None
        publisher_text = ", ".join(self.publisher_names) if self.publisher_names else ""
        if publisher_text:
            self.info_publisher_prefix_label = tk.Label(self.dev_pub_frame, text="Видавець:", font=self.dev_pub_bold_font, background=self.original_bg, justify=tk.LEFT, anchor='nw')
            self.info_publisher_prefix_label.grid(row=dev_pub_row, column=0, sticky='nw', padx=(0, 5))
            self.info_publisher_names_label = tk.Label(self.dev_pub_frame, text=publisher_text, font=self.dev_pub_link_font, fg=self.link_fg, cursor="hand2", background=self.original_bg, justify=tk.LEFT, anchor='nw', wraplength=initial_wraplength)
            self.info_publisher_names_label.grid(row=dev_pub_row, column=1, sticky='nw')
            self.info_publisher_names_label.bind("<Button-1>", partial(self._on_studio_click, studio_names=self.publisher_names))
            dev_pub_row += 1
        else: self.info_publisher_prefix_label = None; self.info_publisher_names_label = None

        current_row += 1
        separator1 = ttk.Separator(self, orient='horizontal')
        separator1.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(15, 10))

        current_row += 1
        desc_label = tk.Label(self, text="Опис:", font=self.section_header_font, background=self.original_bg)
        desc_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
        description_from_db = self.game_data.get('description')
        description_text = description_from_db if description_from_db else "Не вказано"
        self.desc_content_label = tk.Label(self, text=description_text, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg, wraplength=initial_wraplength)
        self.desc_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))

        current_row += 1
        separator2 = ttk.Separator(self, orient='horizontal')
        separator2.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        genres_label = tk.Label(self, text="Жанри:", font=self.section_header_font, background=self.original_bg)
        genres_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
        genres_text = ", ".join(self.genre_names) if self.genre_names else "Не вказано"
        self.genres_content_label = tk.Label(self, text=genres_text, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg, wraplength=initial_wraplength)
        self.genres_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))

        current_row += 1
        separator3 = ttk.Separator(self, orient='horizontal')
        separator3.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        platforms_label = tk.Label(self, text="Платформи:", font=self.section_header_font, background=self.original_bg)
        platforms_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
        platforms_text = ", ".join(self.platform_names) if self.platform_names else "Не вказано"
        self.platforms_content_label = tk.Label(self, text=platforms_text, font=self.description_font, justify=tk.LEFT, anchor='nw', bg=self.original_bg, wraplength=initial_wraplength)
        self.platforms_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))

        current_row += 1
        separator_add = ttk.Separator(self, orient='horizontal')
        separator_add.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        add_details_header = tk.Label(self, text="Додаткова інформація:", font=self.section_header_font, background=self.original_bg)
        add_details_header.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
        add_details_frame = tk.Frame(self, bg=self.original_bg)
        add_details_frame.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
        add_details_frame.grid_columnconfigure(1, weight=1)
        add_details_row = 0
        status_val = self.game_data.get('status'); release_date_val = self.game_data.get('release_date'); created_at_val = self.game_data.get('created_at'); updated_at_val = self.game_data.get('updated_at')
        if status_val:
            status_prefix = tk.Label(add_details_frame, text="Стан:", font=self.description_font, bg=self.original_bg, anchor='nw'); status_prefix.grid(row=add_details_row, column=0, sticky='nw', padx=(0,5))
            status_value = tk.Label(add_details_frame, text=status_val, font=self.description_font, bg=self.original_bg, anchor='nw', justify=tk.LEFT); status_value.grid(row=add_details_row, column=1, sticky='nw'); add_details_row += 1
        release_text = "Не вказано"; dt_format = '%d-%m-%Y'
        if release_date_val:
            try: release_text = release_date_val.strftime(dt_format) if isinstance(release_date_val, datetime) else datetime.strptime(str(release_date_val), '%Y-%m-%d').strftime(dt_format)
            except Exception: release_text = str(release_date_val)
        release_prefix = tk.Label(add_details_frame, text="Дата релізу:", font=self.description_font, bg=self.original_bg, anchor='nw'); release_prefix.grid(row=add_details_row, column=0, sticky='nw', padx=(0,5))
        release_value = tk.Label(add_details_frame, text=release_text, font=self.description_font, bg=self.original_bg, anchor='nw', justify=tk.LEFT); release_value.grid(row=add_details_row, column=1, sticky='nw'); add_details_row += 1
        created_text = "Не вказано"
        if created_at_val:
            try: created_text = created_at_val.strftime(dt_format) if isinstance(created_at_val, datetime) else datetime.strptime(str(created_at_val), '%Y-%m-%d').strftime(dt_format)
            except Exception: created_text = str(created_at_val)
        created_prefix = tk.Label(add_details_frame, text="Дата створення:", font=self.description_font, bg=self.original_bg, anchor='nw'); created_prefix.grid(row=add_details_row, column=0, sticky='nw', padx=(0,5))
        created_value = tk.Label(add_details_frame, text=created_text, font=self.description_font, bg=self.original_bg, anchor='nw', justify=tk.LEFT); created_value.grid(row=add_details_row, column=1, sticky='nw'); add_details_row += 1
        updated_text = "Не вказано"
        if updated_at_val:
            try: updated_text = updated_at_val.strftime(dt_format) if isinstance(updated_at_val, datetime) else datetime.strptime(str(updated_at_val), '%Y-%m-%d').strftime(dt_format)
            except Exception: updated_text = str(updated_at_val)
        updated_prefix = tk.Label(add_details_frame, text="Дата оновлення:", font=self.description_font, bg=self.original_bg, anchor='nw'); updated_prefix.grid(row=add_details_row, column=0, sticky='nw', padx=(0,5))
        updated_value = tk.Label(add_details_frame, text=updated_text, font=self.description_font, bg=self.original_bg, anchor='nw', justify=tk.LEFT); updated_value.grid(row=add_details_row, column=1, sticky='nw'); add_details_row += 1

        current_row += 1
        separator4 = ttk.Separator(self, orient='horizontal')
        separator4.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        reviews_label = tk.Label(self, text="Рецензії:", font=self.section_header_font, background=self.original_bg)
        reviews_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(5, 5)); current_row += 1

        self.reviews_display_text = scrolledtext.ScrolledText(self, height=10, wrap=tk.WORD, font=self.review_text_font, relief=tk.SOLID, borderwidth=1, state=tk.DISABLED, padx=5, pady=5, background=self.colors.get('textbox_bg', 'white'), foreground=self.colors.get('text_fg', 'black'))
        self.reviews_display_text.grid(row=current_row, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.grid_rowconfigure(current_row, weight=1)
        setup_text_widget_editing(self.reviews_display_text)

        current_row += 1
        separator5 = ttk.Separator(self, orient='horizontal')
        separator5.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        write_review_label = tk.Label(self, text="Написати рецензію:", font=self.section_header_font, background=self.original_bg)
        write_review_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(5, 5)); current_row += 1

        self.review_text_widget = scrolledtext.ScrolledText(self, height=6, font=self.review_input_font, wrap=tk.WORD, borderwidth=1, relief=tk.SOLID, highlightthickness=0, background=self.colors.get('input_bg', 'white'), foreground=self.colors.get('input_fg', 'black'))
        self.review_text_widget.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 5))
        setup_text_widget_editing(self.review_text_widget)

        current_row += 1
        post_review_button = ttk.Button(self, text="Надіслати рецензію", command=self._post_review, style=self.custom_button_style)
        post_review_button.grid(row=current_row, column=0, sticky='e', padx=10, pady=(0, 10))

        scrolled_text_handler = lambda event, c=self.scroll_target_canvas: handle_mouse_wheel_event(event, c)

        if self.reviews_display_text:
            self.reviews_display_text.bind("<MouseWheel>", scrolled_text_handler)
            self.reviews_display_text.bind("<Button-4>", scrolled_text_handler)
            self.reviews_display_text.bind("<Button-5>", scrolled_text_handler)
            try:
                 text_widget_inside = self.reviews_display_text.winfo_children()[0]
                 if isinstance(text_widget_inside, tk.Text):
                     text_widget_inside.bind("<MouseWheel>", scrolled_text_handler)
                     text_widget_inside.bind("<Button-4>", scrolled_text_handler)
                     text_widget_inside.bind("<Button-5>", scrolled_text_handler)
            except Exception as e: print(f"Could not bind to inner widget of reviews_display_text: {e}")

        if self.review_text_widget:
            self.review_text_widget.bind("<MouseWheel>", scrolled_text_handler)
            self.review_text_widget.bind("<Button-4>", scrolled_text_handler)
            self.review_text_widget.bind("<Button-5>", scrolled_text_handler)
            try:
                 text_widget_inside_input = self.review_text_widget.winfo_children()[0]
                 if isinstance(text_widget_inside_input, tk.Text):
                      text_widget_inside_input.bind("<MouseWheel>", scrolled_text_handler)
                      text_widget_inside_input.bind("<Button-4>", scrolled_text_handler)
                      text_widget_inside_input.bind("<Button-5>", scrolled_text_handler)
            except Exception as e: print(f"Could not bind to inner widget of review_text_widget: {e}")

        bind_recursive_mousewheel(self, self.scroll_target_canvas)

    def _post_review(self):
        """Handles the 'Post Review' button click."""
        if not self.review_text_widget:
            print("UI Error: Review text widget not found.")
            messagebox.showerror("Помилка UI", "Не знайдено поле для введення рецензії.")
            return

        review_text = self.review_text_widget.get("1.0", tk.END).strip()

        if not review_text:
            messagebox.showwarning("Порожня рецензія", "Будь ласка, введіть текст рецензії.", parent=self)
            return
        if self.game_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID гри для рецензії.", parent=self)
            return
        if self.user_id is None:
             messagebox.showerror("Помилка", "Не вдалося визначити користувача.", parent=self)
             return

        print(f"UI: Posting review for game_id: {self.game_id}, user_id: {self.user_id}")

        success = False
        try:
            success = self.db_manager.add_or_update_review(self.user_id, self.game_id, review_text)
        except AttributeError:
            print("UI Error: DB manager does not have 'add_or_update_review' method.")
            messagebox.showerror("Помилка", "Функціонал додавання рецензій не реалізовано (DB method missing).", parent=self)
            return
        except Exception as e:
            print(f"UI Error: Unexpected error calling add_or_update_review: {e}")
            messagebox.showerror("Неочікувана Помилка", f"Сталася помилка під час спроби зберегти рецензію:\n{e}", parent=self)
            return

        if success:
             print("UI: Review saved/updated successfully.")
             self.review_text_widget.delete("1.0", tk.END)
             messagebox.showinfo("Успіх", "Вашу рецензію збережено!", parent=self)
             self._load_reviews()
        else:
             print("UI: Failed to save/update review (DB error likely shown).")
             self.review_text_widget.focus_set()
             
    def _load_reviews(self):
        """Loads and displays existing reviews and comments for the current game"""
        if not hasattr(self, 'reviews_display_text') or not self.reviews_display_text.winfo_exists():
            return

        self.reviews_display_text.config(state=tk.NORMAL)
        self.reviews_display_text.delete('1.0', tk.END)

        if self.game_id is None:
            self.reviews_display_text.insert(tk.END, "Помилка: ID гри не визначено.")
            self.reviews_display_text.config(state=tk.DISABLED)
            return

        author_font = self.fonts.get('review_author', ("Verdana", 10, "bold"))
        date_font = self.fonts.get('review_text', ("Verdana", 8))
        text_font = self.fonts.get('review_text', ("Verdana", 9))
        comment_header_font = self.fonts.get('comment', ("Verdana", 9, "bold"))
        comment_author_font = self.fonts.get('review_author', ("Verdana", 9, "bold"))
        comment_date_font = self.fonts.get('review_text', ("Verdana", 7))
        comment_text_font = self.fonts.get('review_text', ("Verdana", 9))
        reply_link_font = self.fonts.get('ui', ("Verdana", 8))
        no_reviews_font = self.fonts.get('ui', ("Verdana", 10))

        text_color = self.colors.get('text_fg', 'black')
        date_color = self.colors.get('date_fg', '#555555')
        link_color = self.colors.get('link_fg', 'blue')
        separator_color = self.colors.get('separator_fg', 'grey')
        no_reviews_color = self.colors.get('placeholder_fg', 'grey')

        review_indent = 10
        comment_base_indent = review_indent + 15
        spacing_after_author = 2
        spacing_after_date = 5
        spacing_after_text = 10
        spacing_after_comment = 5
        spacing_before_reply = 8
        separator_spacing = 15

        self.reviews_display_text.tag_configure("review_author", font=author_font, foreground=text_color, spacing1=spacing_after_date, spacing3=spacing_after_author)
        self.reviews_display_text.tag_configure("review_date", font=date_font, foreground=date_color, lmargin1=review_indent, lmargin2=review_indent)
        self.reviews_display_text.tag_configure("review_text", font=text_font, foreground=text_color, lmargin1=review_indent, lmargin2=review_indent, spacing3=spacing_after_text)
        self.reviews_display_text.tag_configure("comment_header", font=comment_header_font, foreground=text_color, lmargin1=comment_base_indent, lmargin2=comment_base_indent, spacing1=8, spacing3=4)
        self.reviews_display_text.tag_configure("comment_author", font=comment_author_font, foreground=text_color, lmargin1=comment_base_indent, lmargin2=comment_base_indent, spacing1=3, spacing3=1)
        self.reviews_display_text.tag_configure("comment_date", font=comment_date_font, foreground=date_color, lmargin1=comment_base_indent, lmargin2=comment_base_indent)
        self.reviews_display_text.tag_configure("comment_text", font=comment_text_font, foreground=text_color, lmargin1=comment_base_indent, lmargin2=comment_base_indent, spacing3=spacing_after_comment)
        self.reviews_display_text.tag_configure("reply_link", font=reply_link_font, foreground=link_color, underline=True, lmargin1=review_indent, lmargin2=review_indent, spacing1=spacing_before_reply)
        self.reviews_display_text.tag_configure("separator", foreground=separator_color, justify=tk.LEFT, spacing1=separator_spacing, spacing3=separator_spacing)
        self.reviews_display_text.tag_configure("no_reviews", foreground=no_reviews_color, justify=tk.CENTER, font=no_reviews_font)


        reviews_data_from_db = None
        try:
            reviews_data_from_db = self.db_manager.fetch_game_reviews(self.game_id)
        except Exception as e:
            print(f"Error fetching reviews from DB: {e}")
            self.reviews_display_text.insert(tk.END, f"Помилка завантаження рецензій: {e}", "no_reviews")
            self.reviews_display_text.config(state=tk.DISABLED)
            return

        if reviews_data_from_db is None:
            self.reviews_display_text.insert(tk.END, "Не вдалося завантажити рецензії (DB повернув None)...", "no_reviews")
        elif not reviews_data_from_db:
            self.reviews_display_text.insert(tk.END, self.no_reviews_message, "no_reviews")
        else:
            num_reviews = len(reviews_data_from_db)
            for i, review in enumerate(reviews_data_from_db):
                try:
                    if isinstance(review, (list, tuple)) and len(review) >= 4:
                        review_id, user, text, date_obj = review[:4]
                        date_str = date_obj.strftime('%d %b, %Y @ %H:%M') if date_obj else "Невідома дата"

                        self.reviews_display_text.insert(tk.END, f"{user}\n", "review_author")
                        self.reviews_display_text.insert(tk.END, f"Опубліковано: {date_str}\n", "review_date")
                        self.reviews_display_text.insert(tk.END, f"{text or '[Порожня рецензія]'}\n", "review_text")

                        comments_data = None
                        try:
                            comments_data = self.db_manager.fetch_review_comments(review_id)
                        except Exception as ce:
                            print(f"Error fetching comments for review {review_id}: {ce}")
                            self.reviews_display_text.insert(tk.END, "[Помилка завантаження коментарів]\n", "comment_text")

                        if comments_data:
                            self.reviews_display_text.insert(tk.END, "Коментарі:\n", "comment_header")
                            for c_idx, comment in enumerate(comments_data):
                                if isinstance(comment, (list, tuple)) and len(comment) >= 3:
                                    c_user, c_text, c_date_obj = comment[:3]
                                    c_date_str = c_date_obj.strftime('%d %b, %Y @ %H:%M') if c_date_obj else "..."
                                    self.reviews_display_text.insert(tk.END, f"{c_user}\n", "comment_author")
                                    self.reviews_display_text.insert(tk.END, f"{c_date_str}\n", "comment_date")
                                    self.reviews_display_text.insert(tk.END, f"{c_text or '[Порожній коментар]'}\n", "comment_text")
                                else:
                                    print(f"UI Warning: Skipping invalid comment data format: {comment}")
                                    self.reviews_display_text.insert(tk.END, "[Некоректний формат коментаря]\n", "comment_text")

                        reply_tag = f"reply_{review_id}"
                        self.reviews_display_text.insert(tk.END, "[Відповісти]", ("reply_link", reply_tag))
                        self.reviews_display_text.tag_bind(reply_tag, "<Button-1>", lambda e, r_id=review_id: self._prompt_add_comment(target_review_id=r_id))
                        self.reviews_display_text.insert(tk.END, "\n")

                        if i < num_reviews - 1:
                             separator_line = "─" * 60
                             self.reviews_display_text.insert(tk.END, f"\n{separator_line}\n\n", "separator")
                        else:
                             self.reviews_display_text.insert(tk.END, "\n\n")

                    else:
                        print(f"UI Warning: Skipping invalid review data format: {review}")
                        self.reviews_display_text.insert(tk.END, "[Некоректний формат рецензії]\n\n")
                except Exception as e:
                     print(f"UI Error: Error processing review/comments display loop: {e}")
                     traceback.print_exc()
                     self.reviews_display_text.insert(tk.END, f"[Помилка обробки відображення: {e}]\n\n")

        self.reviews_display_text.config(state=tk.DISABLED)
        self.reviews_display_text.yview_moveto(0)

    def _prompt_add_comment(self, target_review_id):
        """Opens a simple dialog to ask the user for comment text"""
        if self.user_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити користувача. Увійдіть в акаунт.", parent=self)
            return

        prompt_title = f"Відповідь на рецензію"
        prompt_message = f"Ваш коментар до рецензії:"

        comment_text = simpledialog.askstring(prompt_title, prompt_message, parent=self)

        if comment_text:
            comment_text = comment_text.strip()
            if not comment_text:
                messagebox.showwarning("Порожній коментар", "Ви не ввели текст коментаря.", parent=self)
                return

            print(f"UI: Adding comment to review {target_review_id} by user {self.user_id}")
            success = False
            try:
                success = self.db_manager.add_review_comment(target_review_id, self.user_id, comment_text)
            except AttributeError:
                 messagebox.showerror("Помилка", "Функціонал додавання коментарів не реалізовано.", parent=self)
                 return
            except Exception as e:
                 messagebox.showerror("Помилка Бази Даних", f"Не вдалося додати коментар:\n{e}", parent=self)
                 return

            if success:
                messagebox.showinfo("Успіх", "Ваш коментар додано!", parent=self)
                self._load_reviews()
            else:
                pass
        else:
             print("UI: Comment input cancelled or empty.")
             
    def _buy_game(self):
        """Handles the 'Buy' or 'Get' button click"""
        if self.game_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити ID гри.", parent=self)
            return
        if self.user_id is None:
            messagebox.showerror("Помилка", "Не вдалося визначити користувача.", parent=self)
            return

        price = self.game_data.get('price')
        title = self.game_data.get('title', 'цієї гри')
        is_free = False
        price_numeric = decimal.Decimal('0.00')

        try:
            if price is not None:
                price_float = float(price)
                if price_float > 0.0:
                     price_numeric = decimal.Decimal(str(price)).quantize(decimal.Decimal("0.01"))
                     action_verb = "придбати"
                     price_desc = f"за {price_numeric}₴"
                else:
                     is_free = True
                     action_verb = "додати до бібліотеки"
                     price_desc = "безкоштовно"
            else:
                 messagebox.showerror("Помилка", "Не вдалося визначити ціну для покупки.", parent=self)
                 return

        except (ValueError, TypeError, decimal.InvalidOperation) as e:
             print(f"Error parsing price '{price}': {e}")
             messagebox.showerror("Помилка ціни", f"Некоректний формат ціни для гри: {price}", parent=self)
             return

        confirm = messagebox.askyesno(
            "Підтвердження",
            f"Ви впевнені, що хочете {action_verb} гру '{title}' {price_desc}?",
            parent=self
        )

        if confirm:
            print(f"UI: Attempting to '{action_verb}' game_id: {self.game_id} for user_id: {self.user_id} at price {price_numeric}")
            success = False
            try:
                success = self.db_manager.purchase_game(self.user_id, self.game_id, price_numeric)

                if success:
                     action_past = "додано до" if is_free else "придбано та додано до"
                     messagebox.showinfo("Успіх", f"Гру '{title}' успішно {action_past} вашої бібліотеки!", parent=self)
                     self._build_price_buy_content()
                     if self.store_window_ref and hasattr(self.store_window_ref, 'refresh_user_info_display'):
                         self.store_window_ref.refresh_user_info_display()
                     if self.store_window_ref and hasattr(self.store_window_ref, 'load_games_library'):
                          self.store_window_ref.load_games_library()

            except AttributeError:
                 messagebox.showerror("Помилка", "Функціонал покупки/додавання гри не реалізовано (DB method missing).", parent=self)
            except Exception as e:
                 print(f"UI Error during purchase process: {e}")
                 traceback.print_exc()
                 messagebox.showerror("Помилка", f"Під час процесу покупки сталася неочікувана помилка:\n{e}", parent=self)
        
    def _build_price_buy_content(self):
        """Updates the content of the price/buy button area based on ownership status and price"""
        if not self.price_buy_frame or not self.price_buy_frame.winfo_exists():
            print("Error: price_buy_frame not available for content.")
            return

        for widget in self.price_buy_frame.winfo_children():
            widget.destroy()

        is_owned = False
        try:
            if self.user_id is not None and self.game_id is not None:
                is_owned = self.db_manager.check_ownership(self.user_id, self.game_id)
        except Exception as e:
            print(f"Error checking ownership: {e}")

        if is_owned:
            owned_label = tk.Label(self.price_buy_frame, text="✔ У бібліотеці", font=self.detail_font, bg=self.original_bg, fg="green")
            owned_label.pack(side=tk.LEFT, anchor='w')
        else:
            price = self.game_data.get('price')
            price_text_raw = format_price_display(price)
            can_buy = False
            is_free = False

            if price is None:
                price_text_raw = f"Статус: {self.game_data.get('status', 'N/A')}"
            elif isinstance(price, (int, float, Decimal)) and float(price) == 0.0:
                price_text_raw = "Безкоштовно"
                is_free = True
                can_buy = True
            else:
                try:
                    price_decimal = Decimal(str(price)).quantize(Decimal("0.01"))
                    price_text_raw = f"{price_decimal}₴"
                    can_buy = True
                except (ValueError, TypeError, InvalidOperation):
                    price_text_raw = "N/A"

            price_label = tk.Label(self.price_buy_frame, text=price_text_raw, font=self.price_font, bg=self.original_bg)
            price_label.pack(side=tk.LEFT, anchor='w')

            if can_buy:
                 button_text = "Отримати" if is_free else "Придбати"
                 buy_button = ttk.Button(self.price_buy_frame, text=button_text, style=self.custom_button_style, command=self._buy_game)
                 buy_button.pack(side=tk.LEFT, padx=(15, 0), anchor='w')
                        
    def _on_studio_click(self, event, studio_names):
        """Handles clicks on developer/publisher studio name labels"""
        if not studio_names:
            return
        target_studio_name = studio_names[0]
        print(f"Clicked on studio link for: {target_studio_name}")
        if self.store_window_ref and hasattr(self.store_window_ref, '_show_studio_detail_view'):
            self.store_window_ref._show_studio_detail_view(target_studio_name)
        else:
            print("Error: Cannot show studio details. Reference to StoreWindow or method is missing.")
            
    def _show_edit_dialog(self):
        """Shows a modal dialog for editing the game's price and description"""
        if not self.can_edit:
            messagebox.showerror("Помилка", "У вас немає прав редагувати цю гру.", parent=self)
            return

        edit_dialog = Toplevel(self)
        edit_dialog.title(f"Редагування '{self.game_data.get('title', '')}'")
        edit_dialog.transient(self.store_window_ref)
        edit_dialog.grab_set()
        edit_dialog.resizable(False, False)

        dialog_frame = ttk.Frame(edit_dialog, padding="10 10 10 10")
        dialog_frame.pack(expand=True, fill=tk.BOTH)

        current_price_raw = self.game_data.get('price')
        current_price_str = ""
        if current_price_raw is not None:
            try:
                price_decimal = Decimal(str(current_price_raw))
                current_price_str = f"{price_decimal:.2f}"
            except (InvalidOperation, TypeError):
                current_price_str = "N/A"
        current_description = self.game_data.get('description', '')

        price_label = ttk.Label(dialog_frame, text="Ціна (₴):")
        price_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        price_entry = ttk.Entry(dialog_frame, width=15)
        price_entry.grid(row=0, column=1, sticky=tk.EW, pady=(0, 10))
        price_entry.insert(0, current_price_str if current_price_str != "N/A" else "")
        setup_text_widget_editing(price_entry)


        desc_label = ttk.Label(dialog_frame, text="Опис:")
        desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        desc_text = scrolledtext.ScrolledText(dialog_frame, width=60, height=10, wrap=tk.WORD, font=self.fonts['review_input'])
        desc_text.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        desc_text.insert(tk.END, current_description)
        setup_text_widget_editing(desc_text)

        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E)

        save_button = ttk.Button(button_frame, text="Зберегти",
                                 command=lambda: self._save_edits(edit_dialog, price_entry, desc_text),
                                 style=self.custom_button_style)
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Скасувати",
                                   command=edit_dialog.destroy,
                                   style=self.custom_button_style)
        cancel_button.pack(side=tk.LEFT)

        edit_dialog.update_idletasks()
        center_window(edit_dialog, edit_dialog.winfo_reqwidth(), edit_dialog.winfo_reqheight())

        edit_dialog.wait_window()
        
    def _save_edits(self, dialog, price_widget, description_widget):
        """Validates and saves the edited price and description to the database"""
        new_price_str = price_widget.get().strip().replace(',', '.')
        new_description = description_widget.get("1.0", tk.END).strip()

        final_price = None
        if new_price_str:
            try:
                price_decimal = Decimal(new_price_str).quantize(Decimal("0.01"))
                if price_decimal < 0:
                    messagebox.showerror("Помилка Вводу", "Ціна не може бути від'ємною.", parent=dialog)
                    return
                original_price_raw = self.game_data.get('price')
                original_price_decimal = None
                if original_price_raw is not None:
                    try:
                         original_price_decimal = Decimal(str(original_price_raw)).quantize(Decimal("0.01"))
                    except (InvalidOperation, TypeError):
                         pass

                if price_decimal != original_price_decimal:
                    final_price = price_decimal
                else:
                    print("Price entered is the same as the current price. No price update needed.")

            except (ValueError, InvalidOperation) as e:
                messagebox.showerror("Помилка Формату", f"Некоректний формат ціни: {new_price_str}. Введіть число.", parent=dialog)
                return
        else:
            final_price = None

        final_description = None
        original_description = self.game_data.get('description', '')
        if new_description != original_description:
            final_description = new_description
        else:
             print("Description is the same as the current description. No description update needed.")

        if final_price is None and final_description is None:
            print("No changes detected. Closing edit dialog.")
            dialog.destroy()
            return

        print(f"UI: Saving edits for game {self.game_id}. Price: {final_price}, Desc changed: {final_description is not None}")
        success = False
        try:
            success = self.db_manager.update_game_details(
                game_id=self.game_id,
                new_description=final_description,
                new_price=final_price,
                editor_user_id=self.user_id
            )
        except AttributeError:
             messagebox.showerror("Помилка", "Функціонал оновлення гри не реалізовано (DB method missing).", parent=dialog)
             return
        except Exception as e:
             print(f"UI Error calling update_game_details: {e}")
             traceback.print_exc()
             messagebox.showerror("Неочікувана Помилка", f"Сталася помилка під час збереження змін:\n{e}", parent=dialog)
             return

        if success:
             messagebox.showinfo("Успіх", "Зміни успішно збережено!", parent=self.store_window_ref)
             dialog.destroy()
             if self.store_window_ref and hasattr(self.store_window_ref, 'refresh_current_tab'):
                 print("Triggering StoreWindow refresh after edit.")
                 self.store_window_ref.after(50, self.store_window_ref.refresh_current_tab)
             else:
                  print("Cannot refresh store window - reference missing.")
        else:
             print("UI: Failed to save edits (DB error likely shown).")
             price_widget.focus_set()