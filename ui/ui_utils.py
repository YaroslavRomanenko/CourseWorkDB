import tkinter as tk
from tkinter import scrolledtext

def center_window(window, width, height):
    try:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception as e:
        print(f"Помилка центрування вікна: {e}")
        window.geometry(f"{width}x{height}")
        
def setup_text_widget_editing(widget):

    def select_all(event):
        if isinstance(widget, tk.Entry):
            widget.select_range(0, 'end')
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            widget.tag_add('sel', '1.0', 'end')
            widget.mark_set('insert', '1.0')
            widget.see('insert')
        return "break"

    widget.bind("<Control-a>", select_all)
    widget.bind("<Control-A>", select_all)

    context_menu = tk.Menu(widget, tearoff=0)

    def _do_cut(w):
        try: w.event_generate("<<Cut>>")
        except tk.TclError: pass
    def _do_copy(w):
        try: w.event_generate("<<Copy>>")
        except tk.TclError: pass
    def _do_paste(w):
        try: w.event_generate("<<Paste>>")
        except tk.TclError: pass
    def _do_select_all(w):
        select_all(tk.Event())

    context_menu.add_command(label="Cut", command=lambda w=widget: _do_cut(w))
    context_menu.add_command(label="Copy", command=lambda w=widget: _do_copy(w))
    context_menu.add_command(label="Paste", command=lambda w=widget: _do_paste(w))
    context_menu.add_separator()
    context_menu.add_command(label="Select All", command=lambda w=widget: _do_select_all(w))

    def show_menu(event):
        w = event.widget

        can_cut_copy = False
        try:
            if isinstance(w, tk.Entry):
                can_cut_copy = bool(w.selection_present())
            elif isinstance(w, (tk.Text, scrolledtext.ScrolledText)):
                 sel = w.tag_ranges('sel')
                 can_cut_copy = bool(sel)
        except tk.TclError:
            pass

        can_paste = False
        try:
            can_paste = bool(w.clipboard_get())
        except tk.TclError:
            pass

        context_menu.entryconfig("Cut", state=tk.NORMAL if can_cut_copy else tk.DISABLED)
        context_menu.entryconfig("Copy", state=tk.NORMAL if can_cut_copy else tk.DISABLED)
        context_menu.entryconfig("Paste", state=tk.NORMAL if can_paste else tk.DISABLED)
        context_menu.entryconfig("Select All", state=tk.NORMAL)

        context_menu.tk_popup(event.x_root, event.y_root)

    widget.bind("<Button-3>", show_menu)
    widget.bind("<Button-2>", show_menu)

    def _clear_selection_on_focus_out(event):
        if isinstance(event.widget, tk.Entry):
            event.widget.selection_clear()
        elif isinstance(event.widget, (tk.Text, scrolledtext.ScrolledText)):
            if event.widget.tag_ranges('sel'):
                event.widget.tag_remove('sel', '1.0', 'end')

    widget.bind("<FocusOut>", _clear_selection_on_focus_out)
