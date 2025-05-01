import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import traceback
import os
from PIL import Image, ImageTk
from functools import partial

from .ui_utils import create_scrollable_list 

class StudiosTab(tk.Frame):
    def __init__(self, parent, db_manager, user_id, is_developer_initial,
                 fonts, colors, styles, store_window_ref, **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.db_manager = db_manager
        self.user_id = user_id
        self.fonts = fonts
        self.colors = colors
        self.styles = styles
        self.store_window_ref = store_window_ref

        self.original_bg = colors.get('original_bg', 'white')
        self.hover_bg = colors.get('hover_bg', '#f0f0f0')
        self.custom_button_style = styles.get('custom_button', 'TButton')
        self.list_icon_size = (64, 64)

        self._image_references = getattr(store_window_ref, '_image_references', {})
        self.placeholder_image_list = getattr(store_window_ref, 'placeholder_image', None)
        self.studio_logo_folder = getattr(store_window_ref, 'studio_logo_folder', None)
        self.placeholder_image_name = getattr(store_window_ref, 'placeholder_image_name', 'placeholder.png')

        self.main_content_area = tk.Frame(self, bg=self.original_bg)
        self.main_content_area.pack(fill=tk.BOTH, expand=True)
        self.main_content_area.grid_rowconfigure(0, weight=1)
        self.main_content_area.grid_columnconfigure(0, weight=1)

        self.studios_canvas = None
        self.studios_inner_frame = None
        self._studio_widgets = []

        self._setup_ui()
        
    def _setup_ui(self):
        self.load_studios_list()

    def load_studios_list(self):
        print("StudiosTab: Loading studios list...")
        studios_data = None
        try:
            studios_data = self.db_manager.fetch_all_studios(sort_by='name', sort_order='ASC')
        except AttributeError:
            messagebox.showerror("Помилка", "Функція fetch_all_studios не реалізована в DB Manager.", parent=self)
            studios_data = None
        except Exception as e:
            messagebox.showerror("Помилка бази даних", f"Не вдалося завантажити список студій:\n{e}", parent=self)
            traceback.print_exc()
            studios_data = None

        self.studios_canvas, self.studios_inner_frame, self._studio_widgets = create_scrollable_list(
            parent=self.main_content_area,
            item_creation_func=self._create_studio_entry,
            item_data_list=studios_data,
            bg_color=self.original_bg,
            placeholder_text="На платформі ще немає зареєстрованих студій.",
            placeholder_font=self.fonts['ui'],
            item_pack_config={'fill': tk.X, 'pady': 2, 'padx': 2}
        )
        print(f"Studios list created/updated. Found {len(self._studio_widgets)} studio widgets.")
            
    def _create_studio_entry(self, parent, studio_data):
        studio_id = studio_data.get('studio_id')
        name = studio_data.get('name', 'Невідома студія')
        logo_filename = studio_data.get('logo')
        country = studio_data.get('country', 'Невідомо')

        if studio_id is None: return None

        entry_frame = tk.Frame(parent, borderwidth=1, relief=tk.FLAT, background=self.original_bg)

        icon_label = tk.Label(entry_frame, background=self.original_bg)
        tk_image = self._get_studio_logo(logo_filename, size=self.list_icon_size)
        if tk_image:
            icon_label.config(image=tk_image)
            icon_label.image = tk_image
        else:
            icon_label.config(text="?", font=self.fonts['ui'], width=int(self.list_icon_size[0]/8), height=int(self.list_icon_size[1]/16), relief="solid", borderwidth=1)
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)

        text_frame = tk.Frame(entry_frame, background=self.original_bg)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        name_label = tk.Label(text_frame, text=name,
                              font=self.fonts.get('list_title', ("Verdana", 12, "bold")),
                              anchor="w", justify=tk.LEFT, background=self.original_bg)
        name_label.pack(fill=tk.X, pady=(0, 2))

        country_label = tk.Label(text_frame, text=f"Країна: {country}",
                                 font=self.fonts['ui'], anchor="w", justify=tk.LEFT, background=self.original_bg)
        country_label.pack(fill=tk.X)

        click_handler = partial(self._on_studio_select, name)
        enter_handler = partial(self._on_enter, frame=entry_frame, icon_widget=icon_label)
        leave_handler = partial(self._on_leave, frame=entry_frame, icon_widget=icon_label)

        widgets_to_bind = [entry_frame, icon_label, text_frame, name_label, country_label]
        for widget in widgets_to_bind:
            if widget and widget.winfo_exists():
                widget.bind("<Button-1>", click_handler)
                widget.bind("<Enter>", enter_handler)
                widget.bind("<Leave>", leave_handler)
                widget.config(cursor="hand2")

        return entry_frame

    def _on_studio_select(self, studio_name, event=None):
        print(f"StudiosTab: Selected studio: {studio_name}")
        if self.store_window_ref and hasattr(self.store_window_ref, '_show_studio_detail_view'):
            self.store_window_ref._show_studio_detail_view(studio_name)
        else:
            messagebox.showerror("Помилка", "Не вдалося відкрити деталі студії.", parent=self)
            
    def _on_enter(self, event, frame, icon_widget=None):
        try:
            if frame.winfo_exists():
                frame.config(background=self.hover_bg)
                for widget in frame.winfo_children():
                     if widget == icon_widget: continue
                     if isinstance(widget, (tk.Label, tk.Frame)):
                         if widget.winfo_exists(): widget.config(background=self.hover_bg)
                         if isinstance(widget, tk.Frame):
                             for grandchild in widget.winfo_children():
                                 if isinstance(grandchild, tk.Label):
                                     if grandchild.winfo_exists(): grandchild.config(background=self.hover_bg)
        except tk.TclError: pass

    def _on_leave(self, event, frame, icon_widget=None):
        try:
             if frame.winfo_exists():
                frame.config(background=self.original_bg)
                for widget in frame.winfo_children():
                     if widget == icon_widget: continue
                     if isinstance(widget, (tk.Label, tk.Frame)):
                          if widget.winfo_exists(): widget.config(background=self.original_bg)
                          if isinstance(widget, tk.Frame):
                              for grandchild in widget.winfo_children():
                                  if isinstance(grandchild, tk.Label):
                                      if grandchild.winfo_exists(): grandchild.config(background=self.original_bg)
        except tk.TclError: pass
        
    def _get_studio_logo(self, logo_filename, size=(64, 64)):
        placeholder = self.placeholder_image_list
        if not logo_filename: return placeholder
        if not self.studio_logo_folder:
            print("StudiosTab: STUDIO_LOGO_FOLDER is not set.")
            return placeholder

        full_path = os.path.join(self.studio_logo_folder, logo_filename)
        if self.store_window_ref and hasattr(self.store_window_ref, '_load_image_internal'):
             cache_key_base = f"studio_{logo_filename}"
             return self.store_window_ref._load_image_internal(cache_key_base, full_path, size=size)
        else:
             print("StudiosTab: Warning - Cannot access _load_image_internal from store_window_ref.")
             try:
                 if os.path.exists(full_path):
                     img = Image.open(full_path)
                     img = img.resize(size, Image.Resampling.LANCZOS)
                     return ImageTk.PhotoImage(img)
                 else: return placeholder
             except Exception: return placeholder

    def _prompt_become_developer(self):
        if self.is_developer:
            messagebox.showinfo("Статус розробника", "Ви вже є розробником.", parent=self)
            return

        contact_email = simpledialog.askstring(
            "Стати розробником",
            "Будь ласка, введіть вашу **робочу** електронну пошту.\n"
            "Вона може бути використана для зв'язку зі студіями або адміністрацією.\n\n"
            "Ваша основна пошта акаунту залишиться незмінною.",
            parent=self
        )

        if contact_email:
            contact_email = contact_email.strip()
            if not contact_email:
                messagebox.showwarning("Помилка", "Ви не ввели електронну пошту.", parent=self)
                return
            if "@" not in contact_email or "." not in contact_email.split('@')[-1]:
                 messagebox.showwarning("Помилка", "Будь ласка, введіть дійсну адресу електронної пошти.", parent=self)
                 return

            confirm = messagebox.askyesno("Підтвердження",
                                       f"Ви впевнені, що хочете отримати статус розробника?\n"
                                       f"Контактна пошта розробника буде встановлена як:\n{contact_email}",
                                       parent=self)

            if confirm:
                print(f"StudiosTab: User ID {self.user_id} confirmed becoming a developer with contact email: {contact_email}.")
                success = False
                try:
                    success = self.db_manager.set_developer_status(
                        self.user_id,
                        status=True,
                        contact_email=contact_email
                    )
                except TypeError as te:
                     if 'contact_email' in str(te) or "unexpected keyword argument 'contact_email'" in str(te):
                         messagebox.showerror("Помилка Програми", "Помилка: Метод set_developer_status не оновлено для прийому contact_email.", parent=self)
                         print("!!! PROGRAM ERROR: db_manager.set_developer_status needs 'contact_email' argument or handling !!!")
                         return
                     else:
                         messagebox.showerror("Помилка Типу", f"Помилка під час виклику функції розробника:\n{te}", parent=self)
                         traceback.print_exc()
                         return
                except AttributeError:
                    messagebox.showerror("Помилка", "Функція зміни статусу розробника не реалізована в DB Manager.", parent=self)
                    return
                except Exception as e:
                     messagebox.showerror("Помилка Бази Даних", f"Не вдалося оновити статус:\n{e}", parent=self)
                     traceback.print_exc()
                     return

                if success:
                    messagebox.showinfo("Успіх", "Вітаємо! Ви отримали статус розробника.", parent=self)
                    self.is_developer = True
                    if self.store_window_ref and hasattr(self.store_window_ref, 'update_developer_status'):
                        self.store_window_ref.update_developer_status(True)
                    self._setup_ui()
                else:
                    print("StudiosTab: Failed to set developer status in DB (error message should have been shown by DBManager).")
        else:
            print("StudiosTab: Becoming developer cancelled by user.")

    def refresh_content(self):
        print("StudiosTab: Refreshing studios list.")
        self.load_studios_list()
        
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

        def _on_inner_frame_configure(event=None):
             canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_inner_canvas_configure(event):
             canvas_width = event.width
             canvas.itemconfig(canvas_frame_id, width=canvas_width)
             inner_frame.config(width=canvas_width)
             canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

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

        for widget in [canvas, inner_frame]:
            widget.bind("<MouseWheel>", _on_inner_mousewheel)
            widget.bind("<Button-4>", _on_inner_mousewheel)
            widget.bind("<Button-5>", _on_inner_mousewheel)

        return canvas, inner_frame