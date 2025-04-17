import screeninfo
import pyautogui
import json
import os

def center_window(window, width, height):
    """Centers a window on the primary monitor"""
    try:
        monitors = screeninfo.get_monitors()
        primary_monitor = next((m for m in monitors if m.is_primary), None)
        
        if primary_monitor:
            pm_width, pm_height = primary_monitor.width, primary_monitor.height
            pm_x, pm_y = primary_monitor.x, primary_monitor.y
            x = pm_x + (pm_width - width) // 2
            y = pm_y + (pm_height - height) // 2
            x, y = max(pm_x, x), max(pm_y, y)
            
            print(f"Centering on primary: {width}x{height}+{x}+{y}")
            window.geometry(f"{width}x{height}+{x}+{y}")
        else:
            print("Warning: Primary monitor not found")
            screen_width, screen_height = pyautogui.size()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
            
    except Exception as e:
        print(f"Error centering window: {e}. Using basic Tkinter placement")