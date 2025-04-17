import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class GameListWindow:
    def __init__(self, master, app_controller):
        self.master = master
        self.app = app_controller

        self.window = tk.Toplevel(master)
        self.window.title("Список доступних ігор")
        self.window.geometry("600x400")

        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top_frame, text="Доступні ігри:", font=("Arial", 14)).pack(side=tk.LEFT)

        refresh_button = tk.Button(top_frame, text="Оновити", command=self.load_games)
        refresh_button.pack(side=tk.RIGHT)

        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('id', 'title', 'genre', 'price')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Назва')
        self.tree.heading('genre', text='Жанр')
        self.tree.heading('price', text='Ціна ($)') 

        self.tree.column('id', width=50, anchor=tk.CENTER, stretch=tk.NO)
        self.tree.column('title', width=300)
        self.tree.column('genre', width=120)
        self.tree.column('price', width=80, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.load_games()

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_force()

    def load_games(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        games_data = self.app.get_game_data()

        if games_data is None:
            self.tree.insert('', tk.END, values=('', 'Помилка завантаження даних', '', ''))
        elif not games_data:
             self.tree.insert('', tk.END, values=('', 'Немає доступних ігор', '', ''))
        else:
            for game in games_data:
                try:
                    price_str = f"{float(game[3]):.2f}" if game[3] is not None else "N/A" 
                except (ValueError, TypeError):
                    price_str = str(game[3]) 
                
                display_values = (game[0], game[1], game[2], price_str)
                self.tree.insert('', tk.END, values=display_values)

    def _on_close(self):
        print("Game list window closed.")
        self.app.quit_app()
        
        try:
            if self.window.winfo_exists():
                self.window.destroy()
                
        except tk.TclError:
            pass