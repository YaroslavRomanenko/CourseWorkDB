
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