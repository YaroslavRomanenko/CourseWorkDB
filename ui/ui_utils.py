import tkinter as tk
import screeninfo
import pyautogui

from tkinter import ttk, scrolledtext

def center_window(self, width, height):
        try:
            monitors = screeninfo.get_monitors()
            primary_monitor = next((m for m in monitors if m.is_primary), None)

            if primary_monitor:
                pm_width, pm_height = primary_monitor.width, primary_monitor.height
                pm_x, pm_y = primary_monitor.x, primary_monitor.y
                x = pm_x + (pm_width - width) // 2
                y = pm_y + (pm_height - height) // 2
                x, y = max(pm_x, x), max(pm_y, y)
                self.geometry(f"{width}x{height}+{x}+{y}")
            else:
                print("Warning: Primary monitor not found, using pyautogui")
                screen_width, screen_height = pyautogui.size()
                x = (screen_width - width) // 2
                y = (screen_height - height) // 2
                self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        except Exception as e:
            print(f"Error centering window: {e}. Using basic Tkinter placement")
            self.eval('tk::PlaceWindow . center')
        
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
    
def create_scrollable_list(parent, item_creation_func, item_data_list,
                             bg_color="white", placeholder_text="Список порожній.",
                             placeholder_font=("Verdana", 10), placeholder_fg="grey",
                             item_pack_config=None):
    if item_pack_config is None:
        item_pack_config = {'fill': tk.X, 'pady': 2, 'padx': 2}

    for widget in parent.winfo_children():
        widget.destroy()

    canvas_scrollbar_frame = tk.Frame(parent, bg=bg_color)
    canvas_scrollbar_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_scrollbar_frame, borderwidth=0, background=bg_color, highlightthickness=0)
    scrollbar = ttk.Scrollbar(canvas_scrollbar_frame, orient="vertical", command=canvas.yview)
    inner_frame = tk.Frame(canvas, background=bg_color)

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_inner_frame_configure(event=None):
         if canvas.winfo_exists(): 
            canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_inner_canvas_configure(event):
         if canvas.winfo_exists():
            canvas_width = event.width
            canvas.itemconfig(canvas_frame_id, width=canvas_width)
            canvas.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_inner_mousewheel(event):
        if not canvas.winfo_exists(): return
        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        else:
            try: delta = -1 if event.delta > 0 else 1
            except AttributeError: return
        canvas.yview_scroll(delta, "units")
        return "break"

    inner_frame.bind("<Configure>", _on_inner_frame_configure)
    canvas.bind('<Configure>', _on_inner_canvas_configure)

    for widget in [canvas, inner_frame]:
        widget.bind("<MouseWheel>", _on_inner_mousewheel)
        widget.bind("<Button-4>", _on_inner_mousewheel)
        widget.bind("<Button-5>", _on_inner_mousewheel)

    list_widgets = []
    if not item_data_list:
        placeholder_label = tk.Label(inner_frame, text=placeholder_text,
                                     font=placeholder_font, fg=placeholder_fg, bg=bg_color)
        placeholder_label.pack(pady=20)
        placeholder_label.bind("<MouseWheel>", _on_inner_mousewheel)
        placeholder_label.bind("<Button-4>", _on_inner_mousewheel)
        placeholder_label.bind("<Button-5>", _on_inner_mousewheel)
    else:
        for item_data in item_data_list:
            item_widget = item_creation_func(inner_frame, item_data)
            if item_widget:
                item_widget.pack(**item_pack_config)
                list_widgets.append(item_widget)
                item_widget.bind("<MouseWheel>", _on_inner_mousewheel)
                item_widget.bind("<Button-4>", _on_inner_mousewheel)
                item_widget.bind("<Button-5>", _on_inner_mousewheel)
                for child in item_widget.winfo_children():
                    if isinstance(child, tk.Frame):
                         for grandchild in child.winfo_children():
                              grandchild.bind("<MouseWheel>", _on_inner_mousewheel)
                              grandchild.bind("<Button-4>", _on_inner_mousewheel)
                              grandchild.bind("<Button-5>", _on_inner_mousewheel)
                    else:
                        child.bind("<MouseWheel>", _on_inner_mousewheel)
                        child.bind("<Button-4>", _on_inner_mousewheel)
                        child.bind("<Button-5>", _on_inner_mousewheel)


    inner_frame.update_idletasks()
    if canvas.winfo_exists():
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0)

    return canvas, inner_frame, list_widgets