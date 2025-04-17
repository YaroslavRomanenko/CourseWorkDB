import tkinter as tk
from tkinter import ttk, messagebox
from window_utils import center_window
import os

SCRIPT_DIR = os.path.dirname(__file__)
IMAGE_FOLDER = os.path.join(SCRIPT_DIR, 'resources', 'games_icons')

DEFAULT_IMAGE_EXT = '.png'
IMAGE_NOT_FOUND_PLACEHOLDER = None

class StoreWindow(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._image_references = {}
        
        # Window Settings #
        self.width = 700
        self.height = 450
        center_window(self, self.width, self.height)
        self.title("Universal Games")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.ui_font = ("Verdana", 10)
        self.title_font = ("Verdana", 14, "bold")
        title_label = tk.Label(self, text="Список Ігор", font=self.title_font)
        
        tree_frame = ttk.Frame(self)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('id', 'title', 'genre', 'price')
        
        self.game_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        
        # Headings #
        self.game_tree.heading('id', text='ID')
        self.game_tree.heading('title', text='Назва')
        self.game_tree.heading('genre', text='Жанр')
        self.game_tree.heading('price', text='Ціна')
        
        # Columns #
        self.game_tree.column('id', width=50, anchor='center', stretch=tk.NO)
        self.game_tree.column('title', width=250, anchor='w')
        self.game_tree.column('genre', width=150, anchor='w')
        self.game_tree.column('price', width=80, anchor='e')
        
        # Scrollbar #
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.game_tree.yview)
        self.game_tree.configure(yscrollcommand=scrollbar.set)
        
        refresh_button = ttk.Button(self, text="Оновити список", command=self.load_games)
        
        # Grids #
        title_label.grid(row=0, column=0, pady=10)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.game_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        refresh_button.grid(row=2, column=0, pady=10)
        
        self.load_games()
        
    def _get_image(self, image_id):
        """Load photo images, cashes it, handles errors"""
        if not image_id:
            return None
        
        image_key = str(image_id)
        
        if image_key in self._image_references:
            return self._image_references[image_key]
        
        image_filename = f"{image_key}{DEFAULT_IMAGE_EXT}"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)
        
        try:
            if os.path.exists(image_path):
                img = tk.PhotoImage(file=image_path)
                self._image_references[image_key] = img
                return img
            else:
                print(f"Warning: Image file not found: {image_path}")
                
                if IMAGE_NOT_FOUND_PLACEHOLDER and 'placeholder' not in self._image_references:
                    try:
                        placeholder_img = tk.PhotoImage(file=IMAGE_NOT_FOUND_PLACEHOLDER)
                        self._image_references['placeholder'] = placeholder_img
                        return placeholder_img
                    except Exception as e_placeholder:
                        print(f"Error loading placeholder image '{IMAGE_NOT_FOUND_PLACEHOLDER}': {e_placeholder}")
                        return None
                    
        except tk.TclError as e:
            print(f"Error loading image '{image_path}': {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during loading image '{image_path}': {e}")
            return None
        
        
    def load_games(self):
        """Gets games from DB and populates the Treeview"""
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
            
        games_data = self.db_manager.fetch_all_games()
        
        if games_data:
            for game in games_data:
                try:
                    game_id, title, genre, price, image_id = game
                    formatted_price = f"{price:.2f}"
                    
                    tk_image = self._get_image(image_id)
                    values_to_insert = (game_id, title, genre, formatted_price)
                    self.game_tree.insert('', tk.END, values=values_to_insert, image=tk_image)
                    
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Warning: Skipping game data with unexpected format or type: {game} - Error: {e}")
                except Exception as e:
                    print(f"Error processing or inserting game data {game}: {e}")
                    
        else:
            if games_data is not None:
                print("No games found in the database.")
                
    def on_close(self):
        """Close the window"""
        print("Closing Store Window...")
        self.destroy()
        