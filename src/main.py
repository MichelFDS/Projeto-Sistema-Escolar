from src.database import inicializar_banco
from src.gui import SistemaGUI
from src.theme import apply_theme
import customtkinter as ctk
import sys
import os

def main():
    # Esconde completamente o console
    if sys.platform.startswith('win'):
        import ctypes
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            ctypes.windll.kernel32.FreeConsole()
        except:
            pass
    
    # Aplica tema global
    theme = apply_theme()
    
    # Inicializa banco e GUI
    conn = inicializar_banco()
    root = ctk.CTk()
    app = SistemaGUI(root, conn, theme)

if __name__ == '__main__':
    main()