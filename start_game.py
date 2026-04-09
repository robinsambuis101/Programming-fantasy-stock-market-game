#!/usr/bin/env python3
"""
Fantasy Stock Market Game Launcher
Simple launcher to choose between GUI and Terminal versions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Stock Market Game Launcher")
        self.root.geometry("400x300")
        self.root.configure(bg='#2d2d30')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2d2d30')
        style.configure('TLabel', background='#2d2d30', foreground='#ffffff')
        style.configure('TButton', background='#0e639c', foreground='#ffffff')
        style.map('TButton', background=[('active', '#1177bb')])
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create launcher widgets"""
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ttk.Label(title_frame, text="Fantasy Stock Market Game", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        ttk.Label(title_frame, text="Choose your preferred interface:", 
                 style='Subtitle.TLabel').pack(pady=(0, 30))
        
        # Game mode buttons
        button_frame = ttk.Frame(title_frame)
        button_frame.pack(expand=True)
        
        # GUI Version
        gui_button = ttk.Button(button_frame, text="Launch GUI Version", 
                               command=self.launch_gui, width=20)
        gui_button.pack(pady=10)
        
        ttk.Label(button_frame, text="(Modern desktop interface)", 
                 style='Subtitle.TLabel').pack()
        
        # Terminal Version
        terminal_button = ttk.Button(button_frame, text="Launch Terminal Version", 
                                    command=self.launch_terminal, width=20)
        terminal_button.pack(pady=(20, 10))
        
        ttk.Label(button_frame, text="(Classic command-line interface)", 
                 style='Subtitle.TLabel').pack()
        
        # Test mode checkbox
        self.test_mode_var = tk.BooleanVar(value=False)
        test_check = ttk.Checkbutton(title_frame, text="Test Mode (No API key required)", 
                                     variable=self.test_mode_var)
        test_check.pack(pady=30)
    
    def launch_gui(self):
        """Launch GUI version"""
        try:
            if self.test_mode_var.get():
                subprocess.Popen([sys.executable, "gui_app.py", "--test"])
            else:
                subprocess.Popen([sys.executable, "gui_app.py"])
            self.root.after(1000, self.root.destroy)  # Close launcher after 1 second
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch GUI: {e}")
    
    def launch_terminal(self):
        """Launch terminal version"""
        try:
            if self.test_mode_var.get():
                subprocess.Popen([sys.executable, "main.py", "--test"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, "main.py"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.root.after(1000, self.root.destroy)  # Close launcher after 1 second
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch terminal: {e}")

def main():
    """Main launcher entry point"""
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
