import tkinter as tk
from tkinter import messagebox, ttk
from window_utils import center_window

class LoginWindow(tk.Tk):
    def __init__(self, db_manager, open_register_func, open_store_func):
        super().__init__()
        self.db_manager = db_manager
        self.open_registr_func = open_register_func
        self.open_store_func = open_store_func
        
        # Window settings #
        self.width = 449;
        self.height = 238;
        center_window(self, self.width, self.height)
        self.resizable(False, False)
        self.title("Login")
        
        self.ui_font = ("Verdana", 10)
        
        # Labels #
        self.login_title_label = tk.Label(self, font=("Verdana", 12), text="Вхід")
        self.login_label = tk.Label(self, font=self.ui_font, text="Логін:")
        self.password_label = tk.Label(self, font=self.ui_font, text="Пароль:")

        # Entries #
        self.entry_width = 30
        
        self.login_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font)
        self.password_entry = tk.Entry(self, width=self.entry_width, font=self.ui_font, show="*")

        # Buttons #
        self.buttons_width = 12
        
        self.login_button = tk.Button(self, width=self.buttons_width, height=1, font=self.ui_font, text="Увійти", command=self.submit_login)
        self.registration_button = tk.Button(self, width=self.buttons_width, height=1, font=self.ui_font, text="Зареєструватись", command=self.go_to_register)
        
        # grid #
        self.login_title_label.grid(row=0, column=0, columnspan=2, sticky="n", padx=5, pady=10)
        self.login_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.password_label.grid(row=2, column=0, sticky="w", padx=5, pady=10)
        
        self.login_entry.grid(row=1, column=1, sticky="w", padx=5, pady=10)
        self.password_entry.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        
        self.login_button.grid(row=3, column=0, sticky="e", padx=10, pady=40)
        self.registration_button.grid(row=3, column=1, sticky="e", padx=10, pady=40)

        self.login_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.submit_login())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def submit_login(self):
        """Check the fields to log in"""
        username = self.login_entry.get()
        password = self.password_entry.get()

        if not username or not password:
             messagebox.showwarning("Вхід", "Ви не ввели логін та пароль!", parent=self)
             return

        user_id = self.db_manager.validate_user(username, password)

        if user_id is not None:
            messagebox.showinfo("Вхід", "Вхід успішний!", parent=self)
            self.destroy()
            self.open_store_func(user_id) 
        else:
            messagebox.showerror("Вхід", "Неправильний логін або пароль", parent=self)
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
            
    def go_to_register(self):
        """Destroy self and call the function to open the registration window"""
        self.destroy()
        self.open_registr_func()
        
    def on_close(self):
        """Close the window"""
        print("Closing Login Window...")
        self.destroy()