from src.database import inicializar_banco
from src.gui import SistemaGUI
from src.theme import apply_theme
import customtkinter as ctk
import sys
import os

if __name__ == '__main__':
    # Aplica tema global
    theme = apply_theme()
    
    # Inicializa banco e GUI
    conn = inicializar_banco()
    root = ctk.CTk()
    app = SistemaGUI(root, conn, theme)