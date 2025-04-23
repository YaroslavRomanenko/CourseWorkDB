import tkinter as tk

from tkinter import messagebox
from database_manager import DatabaseManager
from ui_login import LoginWindow
from ui_registration import RegistrationWindow
from ui_store import StoreWindow

db_manager = DatabaseManager('config.json')

def start_login_window():
    """Creates and runs the login window"""
    print("Opening Login Window...")
    login_app = LoginWindow(db_manager, start_registration_window, start_store_window)
    login_app.mainloop()
    print("Login Window mainloop finished")
    
def start_registration_window():
    """Creates and runs the registration window"""
    print("Opening Registration Window...")
    register_app = RegistrationWindow(db_manager, start_login_window)
    register_app.mainloop()
    print("Registration Window mainloop finished")
    
def start_store_window(user_id):
    """Creates and runs the store window"""
    print(f"Opening Store Window for user_id: {user_id}...")
    store_app = StoreWindow(db_manager, user_id) 
    store_app.mainloop()
    print("Store Window mainloop finished")
    
    
if __name__ == '__main__':
    print("Application Starting...")
    start_login_window()
    print("Application Closing Down...")
    db_manager.close_connection()