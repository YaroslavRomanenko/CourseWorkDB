import tkinter as tk
from tkinter import ttk, messagebox

class StudioDetailView(tk.Frame):
    def __init__(self, parent, db_manager, user_id, fonts, colors, styles, **kwargs):
        super().__init__(parent, bg=colors.get('original_bg', 'white'), **kwargs)

        self.parent = parent
        self.db_manager = db_manager
        self.user_id = user_id
        self.fonts = fonts
        self.colors = colors
        self.styles = styles

        self.content_frame = tk.Frame(self, bg=self.colors.get('original_bg', 'white'))
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self._show_default_view()

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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        main_frame = tk.Frame(self, bg=self.colors.get('original_bg', 'white'))
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(main_frame, text="Студії",
                               font=self.fonts.get('title', ("Verdana", 16, "bold")),
                               bg=self.colors.get('original_bg', 'white'))
        title_label.pack(pady=(0, 5))

        self.current_studio_label = tk.Label(main_frame, text="Оберіть студію...",
                                       font=self.fonts.get('ui', ("Verdana", 10)),
                                       bg=self.colors.get('original_bg', 'white'),
                                       fg='grey')
        self.current_studio_label.pack(pady=(0, 15))

        placeholder_text = tk.Label(main_frame, text="(Тут буде список/деталі студій)",
                                   font=self.fonts.get('ui', ("Verdana", 10)),
                                   bg=self.colors.get('original_bg', 'white'),
                                   fg='grey')
        placeholder_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
    def _load_initial_data(self):
        print("StudioTab: Loading initial data (e.g., all studios list)...")
        pass

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