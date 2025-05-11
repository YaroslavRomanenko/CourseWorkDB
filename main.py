import os

from functools import partial

from ui.login import LoginWindow
from ui.registration import RegistrationWindow
from ui.store import StoreWindow

from database_manager import DatabaseManager

try:
    MAIN_SCRIPT_PATH = os.path.abspath(__file__)
    BASE_DIR = os.path.dirname(MAIN_SCRIPT_PATH)
except NameError:
    BASE_DIR = os.getcwd()
    print(f"Warning: Could not determine script path, using CWD as BASE_DIR: {BASE_DIR}")

CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
IMAGE_FOLDER_PATH = os.path.join(RESOURCES_DIR, 'games_icons')
STUDIO_LOGO_FOLDER_PATH = os.path.join(RESOURCES_DIR, 'studios_icons')
PLACEHOLDER_IMG_NAME = 'placeholder.png'
PLACEHOLDER_IMG_PATH = os.path.join(IMAGE_FOLDER_PATH, PLACEHOLDER_IMG_NAME)

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
    
def start_store_window(user_id, is_app_admin):
    """Creates and runs the store window"""
    print(f"Opening Store Window for user_id: {user_id}, Is App Admin: {is_app_admin}...")
    store_app = StoreWindow(
        db_manager=db_manager,
        user_id=user_id,
        is_app_admin=is_app_admin,
        image_folder=IMAGE_FOLDER_PATH,
        studio_logo_folder=STUDIO_LOGO_FOLDER_PATH,
        placeholder_image_path=PLACEHOLDER_IMG_PATH,
        placeholder_image_name=PLACEHOLDER_IMG_NAME,
        open_login_func=start_login_window
    )
    
    refresh_callback = partial(store_app.refresh_user_info_display)
    store_app.after(50, refresh_callback)

    store_app.mainloop()
    print("Store Window mainloop finished")
    
    
if __name__ == '__main__':
    print("Application Starting...")
    if not os.path.exists(IMAGE_FOLDER_PATH):
        print(f"Warning: Game image folder not found: {IMAGE_FOLDER_PATH}")
    if not os.path.exists(STUDIO_LOGO_FOLDER_PATH):
        print(f"Warning: Studio logo folder not found: {STUDIO_LOGO_FOLDER_PATH}")
    if not os.path.exists(PLACEHOLDER_IMG_PATH):
        print(f"Warning: Placeholder image not found: {PLACEHOLDER_IMG_PATH}")
        
    start_login_window()
    print("Application Closing Down...")
    db_manager.close_connection()