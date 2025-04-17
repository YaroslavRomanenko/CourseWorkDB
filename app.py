import sys
import tkinter as tk
from tkinter import messagebox

from database_manager import DatabaseManager
from ui_login import LoginWindow
from ui_games import GameListWindow

class App:
    def __init__(self):
        print("Initializing Database Manager...")
        self.db_manager = DatabaseManager()
        
        if not self.db_manager.get_connection():
            print("Failed to establish initial database connection. Exiting.")
            try:
                root_temp = tk.Tk()
                root_temp.withdraw()
                
                messagebox.showerror("Помилка Бази Даних", "Не вдалося встановити початкове з'єднання з базою даних")
                root_temp.destroy()
        
            except tk.TclError:
                pass
            
            sys.exit(1)
        
        self.root = tk.Tk()
        self.root.title("Менеджер Ігор")
        # self.root.geometry("400x300") 
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.current_user = None
        self.show_login_window()

    def show_login_window(self):
        print("Showing login window...")
        try:
            self.root.update()
            self.root.update_idletasks()
            
            print("App: Root window updated")
        
        except tk.TclError as e:
            print(f"App: Error updating root window")
        
        LoginWindow(self.root, self) 

    def show_game_list_window(self):
        print("Showing game list window...")
        GameListWindow(self.root, self)

    def attempt_login(self, username, password):
        print(f"App validating login for: {username}")
        is_valid = self.db_manager.validate_user(username, password)
        
        if is_valid:
            messagebox.showinfo("Успіх", "Вхід виконано успішно!")
            self.current_user = username
            self.show_game_list_window()
            return True
        else:
            messagebox.showerror("Помилка входу", "Неправильне ім'я користувача або пароль.")
            return False
            
    def cancel_login(self):
        print("Login was cancelled. Exiting application.")
        self.quit_app()

    def get_game_data(self):
        print("App fetching game data...")
        return self.db_manager.fetch_all_games()

    def run(self):
        print("Starting Tkinter main loop...")
        self.root.mainloop()
        print("Tkinter main loop finished.")

    def quit_app(self):
        print("Closing application...")
        if self.db_manager:
            self.db_manager.close_connection()
        if self.root and self.root.winfo_exists:
            try:
                self.root.destroy()
            except tk.TclError:
                print("Error destroying root window")
                
            self.root = None
        print("Application finished.")
        
        sys.exit(0)