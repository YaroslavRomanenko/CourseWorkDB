import tkinter as tk
from tkinter import ttk
from ..utils import setup_text_widget_editing 

def create_search_bar(parent_frame, load_list_command, original_bg="white", custom_button_style="TButton"):
    search_bar_frame = ttk.Frame(parent_frame, style='TFrame')
    search_bar_frame.grid_columnconfigure(1, weight=1)

    search_label = ttk.Label(search_bar_frame, text="Пошук:", background=original_bg)
    search_label.pack(side=tk.LEFT, padx=(0,5))

    search_entry = ttk.Entry(search_bar_frame, width=30)
    setup_text_widget_editing(search_entry)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    search_entry.bind("<Return>", lambda e, cmd=load_list_command: cmd())

    search_button = ttk.Button(search_bar_frame, text="Знайти", command=load_list_command, style=custom_button_style)
    search_button.pack(side=tk.LEFT, padx=(5,0))
    
    return search_entry, search_button, search_bar_frame


def setup_treeview_with_scrollbar(parent_frame, columns_config, on_select_callback, on_double_click_callback=None):
    tree_frame = ttk.Frame(parent_frame, style='TFrame')

    column_ids = [cfg[0] for cfg in columns_config]
    tree = ttk.Treeview(tree_frame, columns=column_ids, show='headings', selectmode='browse')

    for col_id, head_text, width, stretch, anchor, sort_cmd in columns_config:
        heading_options = {'text': head_text}
        if sort_cmd:
            heading_options['command'] = sort_cmd
        tree.heading(col_id, **heading_options)
        tree.column(col_id, width=width, stretch=stretch, anchor=anchor)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(side='left', fill='both', expand=True)

    if on_select_callback:
        tree.bind('<<TreeviewSelect>>', on_select_callback)
    if on_double_click_callback:
        tree.bind("<Double-1>", on_double_click_callback)
        
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=5)
    return tree


def update_treeview_sort_indicators(treeview_widget, clicked_col_id, current_sort_db_key, is_asc):
    for c_id in treeview_widget['columns']:
        current_text = treeview_widget.heading(c_id, 'text')
        treeview_widget.heading(c_id, text=current_text.replace('▲', '').replace('▼', '').strip())

    if clicked_col_id in treeview_widget['columns']:
        arrow = ' ▲' if is_asc else ' ▼'
        current_heading_text = treeview_widget.heading(clicked_col_id, 'text')
        treeview_widget.heading(clicked_col_id, text=current_heading_text + arrow)