import tkinter as tk
import webbrowser
from datetime import datetime
from functools import partial
from tkinter import ttk, messagebox, scrolledtext
import traceback
import os

from PIL import Image, ImageTk
from .ui_utils import *

class StudioDetailView(tk.Frame):
    def __init__(self, parent, db_manager, studio_name,
                 fonts, colors, styles,
                 scroll_target_canvas, store_window_ref,
                 image_cache, placeholder_detail, studio_logo_folder,
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
        self.logo_folder = studio_logo_folder
        self.studio_logo_size = (128, 128)
        self.studio_details = None
        self.studio_title_label = None
        self.logo_label = None
        self.description_content_label = None
        self.details_content_label = None
        self.apply_button = None
        self.applications_frame = None
        self.is_current_user_admin = False
        self.has_pending_application = False

        self._fetch_studio_data()
        self._check_admin_status()
        self._check_if_already_applied()
        self._setup_ui()

        self.bind("<Configure>", lambda e: self.after_idle(lambda: self._update_wraplengths(e.width)))
          
    def _check_admin_status(self):
        self.is_current_user_admin = False
        if self.studio_details and self.store_window_ref and self.db_manager:
            studio_id = self.studio_details.get('studio_id')
            current_user_id = self.store_window_ref.current_user_id
            if studio_id and current_user_id:
                try:
                    role = self.db_manager.check_developer_role(current_user_id, studio_id)
                    if role == 'Admin':
                        self.is_current_user_admin = True
                        print(f"StudioDetailView: User {current_user_id} is an 'Admin' for studio {studio_id}")
                    else:
                         print(f"StudioDetailView: User {current_user_id} is not an admin for studio {studio_id}. Role: {role}")
                except Exception as e:
                     print(f"Error checking admin status: {e}")
          
    def _fetch_studio_data(self):
        print(f"StudioDetailView: Fetching details for studio: {self.studio_name}")
        if hasattr(self.db_manager, 'fetch_studio_details_by_name'):
            try:
                self.studio_details = self.db_manager.fetch_studio_details_by_name(self.studio_name)
                if not self.studio_details:
                     print(f"Studio '{self.studio_name}' not found in DB.")
                else:
                    self.studio_name = self.studio_details.get('name', self.studio_name)
                    print(f"StudioDetailView: Fetched details, Studio ID: {self.studio_details.get('studio_id')}")
            except Exception as e:
                print(f"Error fetching studio details for '{self.studio_name}': {e}")
                traceback.print_exc()
                self.studio_details = None
        else:
            print("Error: db_manager does not have 'fetch_studio_details_by_name' method.")
            self.studio_details = None

    def _setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        self.grid_columnconfigure(0, weight=1)
        current_row = 0
        initial_wraplength = 10000
        bg_color = self.colors.get('original_bg', 'white')
        target_font = self.fonts.get('description', ("Verdana", 10))

        top_frame = tk.Frame(self, bg=bg_color)
        top_frame.grid(row=current_row, column=0, sticky='new', padx=10, pady=10); current_row += 1
        top_frame.grid_columnconfigure(1, weight=1)
        self.logo_label = tk.Label(top_frame, background=bg_color)
        logo_filename = self.studio_details.get('logo') if self.studio_details else None
        tk_logo_image = self._get_image(logo_filename, size=self.studio_logo_size)
        if tk_logo_image: self.logo_label.config(image=tk_logo_image); self.logo_label.image = tk_logo_image
        else: self.logo_label.config(text="Лого?", font=self.fonts.get('ui', ("Verdana", 10)), width=16, height=8, relief="solid", borderwidth=1)
        self.logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 20), pady=0, sticky='nw')

        display_name = self.studio_name
        if self.studio_details and self.studio_details.get('name'): display_name = self.studio_details['name']
        self.studio_title_label = tk.Label(top_frame, text=display_name, font=self.fonts.get('title', ("Verdana", 16, "bold")), bg=bg_color, wraplength=initial_wraplength, justify=tk.LEFT, anchor='nw')
        self.studio_title_label.grid(row=0, column=1, sticky='nw', pady=(0, 5))

        info_frame_under_title = tk.Frame(top_frame, bg=bg_color)
        info_frame_under_title.grid(row=1, column=1, sticky='nw')

        apply_button_text = "Подати заявку на вступ"
        apply_button_state = tk.NORMAL
        if self.has_pending_application:
             apply_button_text = "Заявку вже подано"
             apply_button_state = tk.DISABLED
        elif self.store_window_ref and hasattr(self.db_manager, 'get_developer_studio_id'):
             user_studio_id = self.db_manager.get_developer_studio_id(self.store_window_ref.current_user_id)
             if self.studio_details and user_studio_id == self.studio_details.get('studio_id'):
                 apply_button_text = "Ви вже учасник"
                 apply_button_state = tk.DISABLED

        self.apply_button = ttk.Button(
            info_frame_under_title,
            text=apply_button_text,
            command=self._submit_application,
            style=self.styles.get('custom_button', 'TButton'),
            state=apply_button_state
        )
        if self.studio_details:
             self.apply_button.pack(pady=(5, 0))
        else:
             self.apply_button = None

        separator1 = ttk.Separator(self, orient='horizontal')
        separator1.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(5, 10)); current_row += 1
        desc_title_label = None; error_label = None
        if self.studio_details:
            if self.studio_details.get('description'):
                desc_title_label = tk.Label(self, text="Опис:", font=self.fonts.get('section_header', ("Verdana", 12, "bold")), bg=bg_color)
                desc_title_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
                description = self.studio_details.get('description', 'Опис відсутній.')
                self.description_content_label = tk.Label(self, text=description, font=target_font, bg=bg_color, wraplength=initial_wraplength, justify=tk.LEFT, anchor='nw')
                self.description_content_label.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10)); current_row += 1
        else:
             error_label = tk.Label(self, text=f"Не вдалося завантажити інформацію для студії '{self.studio_name}'.", font=target_font, fg='red', bg=bg_color)
             error_label.grid(row=current_row, column=0, sticky='nw', padx=10, pady=20); current_row += 1

        separator2 = ttk.Separator(self, orient='horizontal')
        separator2.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
        details_title_label = tk.Label(self, text="Деталі:", font=self.fonts.get('section_header', ("Verdana", 12, "bold")), bg=bg_color)
        details_title_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
        details_frame = tk.Frame(self, bg=bg_color)
        details_frame.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 5)); current_row += 1
        details_frame.grid_columnconfigure(1, weight=1)
        details_row_internal = 0; website_link_label = None
        if self.studio_details:
            if self.studio_details.get('country'):
                tk.Label(details_frame, text="Країна:", font=target_font, bg=bg_color, anchor='nw').grid(row=details_row_internal, column=0, sticky='nw', padx=(0,5))
                tk.Label(details_frame, text=self.studio_details['country'], font=target_font, bg=bg_color, anchor='nw', justify=tk.LEFT).grid(row=details_row_internal, column=1, sticky='nw'); details_row_internal += 1
            date_val = self.studio_details.get('established_date')
            if date_val:
                formatted_date = str(date_val) 
                try: formatted_date = (date_val.strftime('%d-%m-%Y') if isinstance(date_val, datetime) else datetime.strptime(str(date_val), '%Y-%m-%d').strftime('%d-%m-%Y')) 
                except Exception: pass
                
                tk.Label(details_frame, text="Засновано:", font=target_font, bg=bg_color, anchor='nw').grid(row=details_row_internal, column=0, sticky='nw', padx=(0,5))
                tk.Label(details_frame, text=formatted_date, font=target_font, bg=bg_color, anchor='nw', justify=tk.LEFT).grid(row=details_row_internal, column=1, sticky='nw'); details_row_internal += 1
            dev_count = self.studio_details.get('developer_count', 0)
            tk.Label(details_frame, text="Розробників:", font=target_font, bg=bg_color, anchor='nw').grid(row=details_row_internal, column=0, sticky='nw', padx=(0,5))
            tk.Label(details_frame, text=str(dev_count), font=target_font, bg=bg_color, anchor='nw', justify=tk.LEFT).grid(row=details_row_internal, column=1, sticky='nw'); details_row_internal += 1
            game_count = self.studio_details.get('game_count', 0)
            tk.Label(details_frame, text="Ігор:", font=target_font, bg=bg_color, anchor='nw').grid(row=details_row_internal, column=0, sticky='nw', padx=(0,5))
            tk.Label(details_frame, text=str(game_count), font=target_font, bg=bg_color, anchor='nw', justify=tk.LEFT).grid(row=details_row_internal, column=1, sticky='nw'); details_row_internal += 1
            website_url = self.studio_details.get('website_url')
            if website_url:
                tk.Label(details_frame, text="Веб-сайт:", font=target_font, bg=bg_color, anchor='nw').grid(row=details_row_internal, column=0, sticky='nw', padx=(0,5))
                link_font_tuple = list(target_font); link_font_tuple.append("underline"); link_font = tuple(link_font_tuple)
                website_link_label = tk.Label(details_frame, text=website_url, font=link_font, fg=self.colors.get('link_fg', 'blue'), cursor="hand2", bg=bg_color, anchor='nw', justify=tk.LEFT); website_link_label.grid(row=details_row_internal, column=1, sticky='nw')
                website_link_label.bind("<Button-1>", partial(self._open_website, website_url)); details_row_internal += 1

        if self.is_current_user_admin:
            separator3 = ttk.Separator(self, orient='horizontal')
            separator3.grid(row=current_row, column=0, sticky='ew', padx=10, pady=10); current_row += 1
            pending_app_count = 0
            try:
                if self.studio_details:
                    studio_id = self.studio_details.get('studio_id')
                    admin_id = self.store_window_ref.current_user_id
                    if studio_id and admin_id:
                         pending_app_count = self.db_manager.get_pending_application_count(studio_id, admin_id)
            except Exception as e:
                print(f"Error getting pending app count in UI: {e}")
            apps_title_text = f"Заявки на вступ ({pending_app_count})"
            apps_title_label = tk.Label(self, text=apps_title_text, font=self.fonts.get('section_header', ("Verdana", 12, "bold")), bg=bg_color)
            apps_title_label.grid(row=current_row, column=0, sticky='w', padx=10, pady=(0, 5)); current_row += 1
            self.applications_frame = tk.Frame(self, bg=self.colors.get('hover_bg', '#f0f0f0'))
            self.applications_frame.grid(row=current_row, column=0, sticky='ew', padx=10, pady=(0, 10))
            self.applications_frame.grid_columnconfigure(0, weight=1)
            self.applications_frame.grid_columnconfigure(1, weight=0)
            self.applications_frame.grid_columnconfigure(2, weight=0)
            self.applications_frame.grid_columnconfigure(3, weight=0)
            current_row += 1
            self._load_and_display_applications()
        else:
             self.applications_frame = None

        bind_recursive_mousewheel(self, self.scroll_target_canvas)
        
    def _accept_application(self, application_id):
        if not self.is_current_user_admin: return
        current_user_id = self.store_window_ref.current_user_id
        print(f"UI: Admin {current_user_id} accepting application {application_id}")
        success = False
        try:
             success = self.db_manager.process_studio_application(application_id, 'Accepted', current_user_id)
        except Exception as e:
             messagebox.showerror("Помилка", f"Не вдалося прийняти заявку:\n{e}", parent=self)
        if success:
             messagebox.showinfo("Успіх", "Заявку прийнято.", parent=self)
             self._load_and_display_applications()
        
    def _reject_application(self, application_id):
        if not self.is_current_user_admin: return
        current_user_id = self.store_window_ref.current_user_id
        print(f"UI: Admin {current_user_id} rejecting application {application_id}")
        success = False
        try:
             success = self.db_manager.process_studio_application(application_id, 'Rejected', current_user_id)
        except Exception as e:
             messagebox.showerror("Помилка", f"Не вдалося відхилити заявку:\n{e}", parent=self)
        if success:
             messagebox.showinfo("Успіх", "Заявку відхилено.", parent=self)
             self._load_and_display_applications()
        
    def _submit_application(self):
        if not self.store_window_ref or not hasattr(self.store_window_ref, 'is_developer'):
            messagebox.showerror("Помилка", "Не вдалося перевірити статус розробника.", parent=self)
            return
        if not self.studio_details or 'studio_id' not in self.studio_details:
            messagebox.showerror("Помилка", "Не вдалося визначити ID студії.", parent=self)
            return

        is_dev = self.store_window_ref.is_developer
        user_id = self.store_window_ref.current_user_id
        studio_id = self.studio_details['studio_id']
        studio_name_display = self.studio_details.get('name', self.studio_name)

        if not is_dev:
            messagebox.showinfo(
                "Потрібен статус розробника",
                "Щоб подати заявку на вступ до студії, вам потрібно спочатку отримати статус розробника.\n\n"
                "Це можна зробити у вкладці 'Майстерня'.",
                parent=self
            )
            return

        print(f"User {user_id} (developer) is applying to studio {studio_id} ('{studio_name_display}')")

        success = False
        try:
            if hasattr(self.db_manager, 'submit_studio_application'):
                 success = self.db_manager.submit_studio_application(user_id, studio_id)
            else:
                 messagebox.showerror("Помилка", "Функціонал подачі заявок не реалізовано (DB).", parent=self)
                 return
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося подати заявку:\n{e}", parent=self)
            traceback.print_exc()
            return

        if success:
             messagebox.showinfo("Заявку подано", f"Вашу заявку на вступ до студії '{studio_name_display}' подано.\nОчікуйте на розгляд.", parent=self)
             if self.apply_button:
                 self.apply_button.config(state=tk.DISABLED, text="Заявку вже подано")
                 self.has_pending_application = True         
    
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
                     print(f"Debug: Error calculating title wraplength in StudioDetailView: {e}")

        except tk.TclError as e:
            pass
        except Exception as e:
            print(f"DEBUG: Unexpected error in StudioDetailView._update_wraplengths:")
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
                        
    def _get_image(self, image_filename, size=(128, 128)):
        placeholder_to_return = self.placeholder_image_detail

        if not image_filename:
            return placeholder_to_return
        if self.logo_folder is None:
            print("StudioDetailView: LOGO_FOLDER is not set, cannot load image.")
            return placeholder_to_return

        full_path = os.path.join(self.logo_folder, image_filename)

        is_placeholder_request = False
        if hasattr(self.store_window_ref, 'placeholder_image_name'):
            is_placeholder_request = (image_filename == self.store_window_ref.placeholder_image_name)

        return self._load_image_internal(image_filename, full_path, size=size, is_placeholder=is_placeholder_request)

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
    
    def _open_website(self, url, event=None):
        if url:
            try:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                print(f"Opening website: {url}")
                webbrowser.open_new_tab(url)
            except Exception as e:
                print(f"Error opening website {url}: {e}")
                messagebox.showerror("Помилка", f"Не вдалося відкрити посилання:\n{url}\n\nПомилка: {e}", parent=self)
        else:
            print("No URL provided to open.")
            
    def _load_and_display_applications(self):
        if not self.applications_frame or not self.is_current_user_admin:
            return

        for widget in self.applications_frame.winfo_children():
            widget.destroy()

        studio_id = self.studio_details.get('studio_id')
        current_user_id = self.store_window_ref.current_user_id
        if not studio_id or not current_user_id:
            return

        pending_apps = None
        try:
            pending_apps = self.db_manager.fetch_pending_applications(studio_id, current_user_id)
        except Exception as e:
             print(f"Error fetching pending applications UI: {e}")
             messagebox.showerror("Помилка", f"Не вдалося завантажити заявки:\n{e}", parent=self)

        if pending_apps is None:
            tk.Label(self.applications_frame, text="Помилка завантаження заявок.", fg="red", bg=self.applications_frame['bg']).grid(row=0, column=0, columnspan=4, pady=5)
        elif not pending_apps:
            tk.Label(self.applications_frame, text="Немає заявок на розгляд.", bg=self.applications_frame['bg']).grid(row=0, column=0, columnspan=4, pady=5)
        else:
            app_row = 0
            for app in pending_apps:
                app_id = app['id']
                username = app['username']
                date_obj = app['date']
                date_str = date_obj.strftime('%d-%m-%Y %H:%M') if date_obj else "Невідомо"

                username_label = tk.Label(self.applications_frame, text=username, anchor='w', bg=self.applications_frame['bg'])
                username_label.grid(row=app_row, column=0, sticky='w', padx=5, pady=2)

                date_label = tk.Label(self.applications_frame, text=date_str, anchor='w', bg=self.applications_frame['bg'], fg='grey')
                date_label.grid(row=app_row, column=1, sticky='w', padx=10, pady=2)

                accept_button = ttk.Button(self.applications_frame, text="Прийняти", width=10, style=self.styles.get('custom_button', 'TButton'),
                                          command=partial(self._accept_application, app_id))
                accept_button.grid(row=app_row, column=2, padx=5, pady=2)

                reject_button = ttk.Button(self.applications_frame, text="Відхилити", width=10, style=self.styles.get('custom_button', 'TButton'),
                                           command=partial(self._reject_application, app_id))
                reject_button.grid(row=app_row, column=3, padx=5, pady=2)

                app_row += 1
                
    def _check_if_already_applied(self):
        self.has_pending_application = False
        if self.studio_details and self.store_window_ref and self.db_manager:
            studio_id = self.studio_details.get('studio_id')
            current_user_id = self.store_window_ref.current_user_id
            if studio_id and current_user_id and not self.is_current_user_admin:
                try:
                    self.has_pending_application = self.db_manager.check_pending_application(current_user_id, studio_id)
                except Exception as e:
                    print(f"Error checking if already applied: {e}")
    