import tkinter as tk
from tkinter import messagebox, ttk
from .ui_utils import center_window
from .ui_utils import setup_text_widget_editing

class RegistrationWindow(tk.Tk):
    def __init__(self, db_manager, open_login_func):
        super().__init__()
        self.db_manager = db_manager
        self.open_login_func = open_login_func

        self.width = 476
        self.height = 306
        center_window(self, self.width, self.height)
        self.resizable(False, False)
        self.title("Registration")
        
        self.ui_font = ("Verdana", 10)
        # Labels #
        self.registration_title_label = tk.Label(self, font=("Verdana", 12), text="Реєстрація")
        self.login_label = tk.Label(self, font=self.ui_font, text="Логін:")
        self.email_label = tk.Label(self, font=self.ui_font, text="Електронна пошта:")
        self.password_label = tk.Label(self, font=self.ui_font, text="Пароль:")
        self.password_repeat_label = tk.Label(self, font=self.ui_font, text="Підтвердити Пароль:")
        
        # Entries #
        self.entry_width = 30
        
        self.login_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font)
        setup_text_widget_editing(self.login_entry)
        
        self.email_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font)
        setup_text_widget_editing(self.email_entry)
        
        self.password_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font, show="*")
        setup_text_widget_editing(self.password_entry)
        
        self.password_repeat_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font, show="*")
        setup_text_widget_editing(self.password_repeat_entry)
        
        # Buttons #
        self.buttons_width = 12
        
        self.login_button = tk.Button(self, width=self.buttons_width, height=1, font=self.ui_font, text="Назад до Входу", command=self.go_to_login)
        self.registration_button = tk.Button(self, width=self.buttons_width, height=1, font=self.ui_font, text="Зареєструватись", command=self.submit_registration)
        
        # Location of Widgets #
        self.registration_title_label.grid(row=0, column=0, columnspan=2, sticky="n", padx=5, pady=10)
        self.login_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.email_label.grid(row=2, column=0, sticky="w", padx=5, pady=10)
        self.password_label.grid(row=3, column=0, sticky="w", padx=5, pady=10)
        self.password_repeat_label.grid(row=4, column=0, sticky="w", padx=5, pady=10)
        
        self.login_entry.grid(row=1, column=1, sticky="w", padx=5, pady=10)
        self.email_entry.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        self.password_entry.grid(row=3, column=1, sticky="w", padx=5, pady=10)
        self.password_repeat_entry.grid(row=4, column=1, sticky="w", padx=5, pady=10)
        
        self.login_button.grid(row=5, column=0, sticky="e", padx=5, pady=20)
        self.registration_button.grid(row=5, column=1, sticky="e", padx=5, pady=20)
        
        self.login_entry.bind("<Return>", lambda event: self.email_entry.focus_set())
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.password_repeat_entry.focus_set())
        self.password_repeat_entry.bind("<Return>", lambda event: self.submit_registration())
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def submit_registration(self):
        messagebox_title = "Реєстрація"
        
        username = self.login_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        password_repeat = self.password_repeat_entry.get()
        
        #--- Data Correctness Check ---#
        if not all([username, email, password, password_repeat]): 
            messagebox.showwarning(messagebox_title, "Заповніть усі поля", parent=self)
            return
        if "@" not in email or "." not in email:
            messagebox.showwarning(messagebox_title, "Введіть дійсну адресу електронної пошти", parent=self)
            return
        if len(password) < 8:
            messagebox.showwarning(messagebox_title, "Пароль має бути більше, або дорівнювати 8 символам", parent=self)
            return
        if password != password_repeat:
            messagebox.showerror(messagebox_title, "Паролі не співпадають", parent=self)
            self.password_entry.delete(0, tk.END)
            self.password_repeat_entry.delete(0, tk.END)
            self.password_entry.focus_get()
            return
        
        #--- Registration ---#
        if self.db_manager.register_user(username, email, password):
            messagebox.showinfo(messagebox_title, "Реєстрація успішна!", parent=self)
            self.go_to_login()
        else:
            pass
        
    def go_to_login(self):
        """Destroy self and call the function to open login window"""
        self.destroy()
        self.open_login_func()
            
    def on_close(self):
        """Close the window"""
        print("Closing Registration Window...")
        self.destroy()
        