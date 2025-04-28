import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import traceback
import os

from PIL import Image, ImageTk

class StudioDetailView(tk.Frame):
    def __init__(self, parent, db_manager, studio_name,
                 fonts, colors, styles,
                 scroll_target_canvas, store_window_ref,
                 image_cache, placeholder_detail, image_folder, # Added image params
                 **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.db_manager = db_manager
        self.studio_name = studio_name
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.scroll_target_canvas = scroll_target_canvas
        self.store_window_ref = store_window_ref

        self._image_references = image_cache
        self.placeholder_image_detail = placeholder_detail
        self.image_folder = image_folder
        self.studio_logo_size = (128, 128)

        self.studio_details = None
        self.studio_title_label = None
        self.logo_label = None
        self.description_content_label = None
        self.details_content_label = None

        self._fetch_studio_data()
        self._setup_ui()

        self.bind("<Configure>", lambda e: self.after_idle(lambda: self._update_wraplengths(e.width)))

    def _fetch_studio_data(self):
        print(f"StudioDetailView: Fetching details for studio: {self.studio_name}")
        if hasattr(self.db_manager, 'fetch_studio_details_by_name'):
            try:
                self.studio_details = self.db_manager.fetch_studio_details_by_name(self.studio_name)
                if not self.studio_details:
                     print(f"Studio '{self.studio_name}' not found in DB.")
                     messagebox.showwarning("Не знайдено", f"Не вдалося знайти деталі для студії: {self.studio_name}", parent=self)
                else:
                    self.studio_name = self.studio_details.get('name', self.studio_name)
            except Exception as e:
                print(f"Error fetching studio details for '{self.studio_name}': {e}")
                traceback.print_exc()
                messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити деталі студії:\n{e}", parent=self)
                self.studio_details = None
        else:
            print("Error: db_manager does not have 'fetch_studio_details_by_name' method.")
            messagebox.showerror("Помилка", "Не вдалося завантажити деталі студії (метод відсутній).", parent=self)
            self.studio_details = None

    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_default_view(self):
        self._clear_content_frame()
        self.content_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(self.content_frame, text="Студії",
                               font=self.fonts.get('title', ("Verdana", 16, "bold")),
                               bg=self.colors.get('original_bg', 'white'))
        title_label.pack(pady=20)

        placeholder_text = tk.Label(self.content_frame, text="Оберіть студію зі списку гри\nабо реалізуйте тут список усіх студій.",
                                   font=self.fonts.get('ui', ("Verdana", 10)),
                                   bg=self.colors.get('original_bg', 'white'),
                                   fg='grey',
                                   justify=tk.CENTER)
        placeholder_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def _setup_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure(0, weight=1)
        current_row = 0
        initial_wraplength = 10000

        top_frame = tk.Frame(self, bg=self.colors.get('original_bg', 'white'))
        top_frame.grid(row=current_row, column=0, sticky='new', padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        self.logo_label = tk.Label(top_frame, background=self.colors.get('original_bg', 'white'))
        logo_filename = self.studio_details.get('logo') if self.studio_details else None
        tk_logo_image = self._get_image(logo_filename, size=self.studio_logo_size)

        if tk_logo_image:
            self.logo_label.config(image=tk_logo_image)
            self.logo_label.image = tk_logo_image
        else:
            self.logo_label.config(text="Лого?", font=self.fonts.get('ui', ("Verdana", 10)), width=16, height=8, relief="solid", borderwidth=1)
        self.logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 20), pady=0, sticky='nw')

        display_name = self.studio_name
        if self.studio_details and self.studio_details.get('name'):
            display_name = self.studio_details['name']

        self.studio_title_label = tk.Label(top_frame, text=display_name,
                                            font=self.fonts.get('title', ("Verdana", 16, "bold")),
                                            bg=self.colors.get('original_bg', 'white'),
                                            justify=tk.LEFT, anchor='nw')
        self.studio_title_label.grid(row=0, column=1, sticky='nw', pady=(0, 5))

        current_row += 1
        separator1 = ttk.Separator(self, orient='horizontal')
        separator1.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(5, 10))

        if self.studio_details and self.studio_details.get('description'):
            current_row += 1
            desc_title_label = tk.Label(self, text="Опис:",
                                        font=self.fonts.get('section_header', ("Verdana", 12, "bold")),
                                        bg=self.colors.get('original_bg', 'white'))
            desc_title_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5))

            current_row += 1
            description = self.studio_details.get('description', 'Опис відсутній.')
            self.description_content_label = tk.Label(self, text=description,
                                                      font=self.fonts.get('description', ("Verdana", 10)),
                                                      bg=self.colors.get('original_bg', 'white'),
                                                      wraplength=initial_wraplength, justify=tk.LEFT, anchor='nw')
            self.description_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
        elif self.studio_details is None:
             current_row += 1
             error_label = tk.Label(self, text=f"Не вдалося завантажити інформацію для студії '{self.studio_name}'.",
                                     font=self.fonts.get('detail'), fg='red',
                                     bg=self.colors.get('original_bg', 'white'))
             error_label.grid(row=current_row, column=0, sticky='nw', padx=10, pady=20)


        current_row += 1
        separator2 = ttk.Separator(self, orient='horizontal')
        separator2.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10)

        details_text_lines = []
        if self.studio_details:
            if self.studio_details.get('country'):
                details_text_lines.append(f"Країна: {self.studio_details['country']}")
            if self.studio_details.get('established_date'):
                date_str = str(self.studio_details['established_date'])
                details_text_lines.append(f"Засновано: {date_str}")
            if self.studio_details.get('website_url'):
                 details_text_lines.append(f"Веб-сайт: {self.studio_details['website_url']}")

        if details_text_lines:
            current_row += 1
            details_title_label = tk.Label(self, text="Деталі:",
                                          font=self.fonts.get('section_header', ("Verdana", 12, "bold")),
                                          bg=self.colors.get('original_bg', 'white'))
            details_title_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5))

            current_row += 1
            self.details_content_label = tk.Label(self, text="\n".join(details_text_lines),
                                                 font=self.fonts.get('detail', ("Verdana", 10)),
                                                 bg=self.colors.get('original_bg', 'white'),
                                                 justify=tk.LEFT, anchor='nw')
            self.details_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))

        widgets_to_bind = [self, top_frame, self.logo_label, self.studio_title_label, separator1, separator2]
        if 'desc_title_label' in locals(): widgets_to_bind.append(desc_title_label)
        if self.description_content_label: widgets_to_bind.append(self.description_content_label)
        if 'details_title_label' in locals(): widgets_to_bind.append(details_title_label)
        if self.details_content_label: widgets_to_bind.append(self.details_content_label)
        if 'error_label' in locals(): widgets_to_bind.append(error_label)

        self._bind_mousewheel_to_children(widgets_to_bind)
        
    def _update_wraplengths(self, container_width):
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

            if self.description_content_label and self.description_content_label.winfo_exists():
                current_wl = self.description_content_label.cget("wraplength")
                if current_wl != content_wraplength:
                    self.description_content_label.config(wraplength=content_wraplength)

            if self.studio_title_label and self.studio_title_label.winfo_exists() and self.logo_label and self.logo_label.winfo_exists():
                try:
                     logo_width = self.logo_label.winfo_reqwidth()
                     padding_between = 20
                     title_wraplength = max(min_content_width, container_width - logo_width - padding_between - 20)
                     current_wl = self.studio_title_label.cget("wraplength")
                     if current_wl != title_wraplength:
                         self.studio_title_label.config(wraplength=title_wraplength)
                except tk.TclError: pass
                except Exception as e:
                     print(f"Debug: Error calculating title wraplength: {e}")


        except tk.TclError as e:
            pass
        except Exception as e:
            print(f"DEBUG: Unexpected error in _update_wraplengths:")
            traceback.print_exc()
        
    def _load_image_internal(self, image_filename, full_path, size=(64, 64), is_placeholder=False):
        placeholder_to_return = self.placeholder_image_detail

        if not image_filename:
            return placeholder_to_return

        cache_key = f"studio_{image_filename}_{size[0]}x{size[1]}"
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
                print(f"StudioDetailView: Error loading/processing image '{full_path}' (using placeholder): {e}")
                self._image_references[cache_key] = placeholder_to_return
                return placeholder_to_return
        else:
            if not is_placeholder:
                 print(f"StudioDetailView: Image file not found: {full_path} (using placeholder)")
            self._image_references[cache_key] = placeholder_to_return
            return placeholder_to_return

    def refresh_content(self):
        print("StudioTab: Refreshing content (showing default view)...")
        self._show_default_view()

    def display_studio_info(self, studio_name):
        print(f"StudioTab: Request to display info for: {studio_name}")
        self._clear_content_frame()
        self.content_frame.grid_columnconfigure(0, weight=1)

        studio_details = None
        if hasattr(self.db_manager, 'fetch_studio_details_by_name'):
            studio_details = self.db_manager.fetch_studio_details_by_name(studio_name)
        else:
            print("Error: db_manager does not have 'fetch_studio_details_by_name' method.")
            messagebox.showerror("Помилка", "Не вдалося завантажити деталі студії (метод відсутній).", parent=self)
            self._show_default_view()
            return

        if not studio_details:
            messagebox.showwarning("Не знайдено", f"Не вдалося знайти деталі для студії: {studio_name}", parent=self)
            self._show_default_view()
            return

        back_button = ttk.Button(self.content_frame, text="< Всі студії",
                                 command=self._show_default_view,
                                 style=self.styles.get('custom_button', 'TButton'))
        back_button.pack(anchor='nw', padx=10, pady=(5, 10))

        title_label = tk.Label(self.content_frame, text=studio_details.get('name', studio_name),
                               font=self.fonts.get('title', ("Verdana", 16, "bold")),
                               bg=self.colors.get('original_bg', 'white'))
        title_label.pack(pady=(0, 15))

        desc = studio_details.get('description', 'Опис відсутній.')
        desc_label = tk.Label(self.content_frame, text=desc,
                              font=self.fonts.get('description', ("Verdana", 10)),
                              bg=self.colors.get('original_bg', 'white'),
                              wraplength=600, justify=tk.LEFT)
        desc_label.pack(pady=10, padx=20, anchor='w')

        details_text = []
        if studio_details.get('country'):
            details_text.append(f"Країна: {studio_details['country']}")
        if studio_details.get('established_date'):
            details_text.append(f"Засновано: {studio_details['established_date']}")
        if studio_details.get('website_url'):
             details_text.append(f"Веб-сайт: {studio_details['website_url']}")

        if details_text:
            other_details_label = tk.Label(self.content_frame, text="\n".join(details_text),
                                          font=self.fonts.get('detail', ("Verdana", 10)),
                                          bg=self.colors.get('original_bg', 'white'),
                                          justify=tk.LEFT)
            other_details_label.pack(pady=10, padx=20, anchor='w')
            
    def _handle_mousewheel(self, event):
        if isinstance(event.widget, (ttk.Scrollbar, scrolledtext.ScrolledText)):
            return

        if not self.scroll_target_canvas:
            return

        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try:
                delta = -1 if event.delta > 0 else 1
            except AttributeError:
                return

        self.scroll_target_canvas.yview_scroll(delta, "units")
        return "break"
    
    def _bind_mousewheel_to_children(self, widgets):
        if not isinstance(widgets, (list, tuple)):
            widgets = [widgets]

        for widget in widgets:
            if widget and widget.winfo_exists():
                if not isinstance(widget, scrolledtext.ScrolledText):
                    try:
                        widget.bind("<MouseWheel>", self._handle_mousewheel, add='+')
                        widget.bind("<Button-4>", self._handle_mousewheel, add='+')
                        widget.bind("<Button-5>", self._handle_mousewheel, add='+')
                    except tk.TclError as e:
                        print(f"StudioDetailView: Warning - Could not bind scroll to widget {widget}: {e}")
                        
    def _get_image(self, image_filename, size=(128, 128)):
        placeholder_to_return = self.placeholder_image_detail

        if not image_filename:
            return placeholder_to_return
        if self.image_folder is None:
            print("StudioDetailView: IMAGE_FOLDER is not set, cannot load image.")
            return placeholder_to_return

        full_path = os.path.join(self.image_folder, image_filename)

        is_placeholder_request = False
        if hasattr(self.store_window_ref, 'placeholder_image_path') and hasattr(self.store_window_ref, 'placeholder_image_name'):
             is_placeholder_request = (image_filename == self.store_window_ref.placeholder_image_name)


        return self._load_image_internal(image_filename, full_path, size=size, is_placeholder=is_placeholder_request)