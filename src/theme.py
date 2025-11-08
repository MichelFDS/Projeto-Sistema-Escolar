"""
Sistema de temas e estilo visual para a aplicação.
Uso: from src.theme import apply_theme, ThemeColors, ThemeFonts
"""
import customtkinter as ctk
from dataclasses import dataclass

@dataclass
class ThemeColors:
    # Cores principais
    PRIMARY = "#2B6BE6"  # Azul forte para menu e botões principais
    SECONDARY = "#4285F4"  # Azul mais claro para botões secundários
    SUCCESS = "#32CD32"  # Verde para confirmações
    WARNING = "#FFB74D"  # Laranja para avisos
    DANGER = "#FF4B4B"  # Vermelho para erros/exclusão
    
    # Backgrounds
    BG = "#FFFFFF"  # Branco para área principal
    BG_SECONDARY = "#F5F5F5"  # Cinza muito claro para cards
    MENU_BG = PRIMARY  # Menu lateral usa cor primária
    
    # Texto
    TEXT = "#333333"  # Texto principal (quase preto)
    TEXT_SECONDARY = "#666666"  # Texto secundário (cinza)
    TEXT_LIGHT = "#FFFFFF"  # Texto sobre fundos escuros
    
    # Estados
    HOVER = "#2258C7"  # Hover do menu (azul mais escuro)
    BUTTON_HOVER = "#2B6BE6"  # Hover dos botões (azul mais escuro)

@dataclass
class ThemeFonts:
    TITLE = ("Segoe UI", 24, "bold")
    SUBTITLE = ("Segoe UI", 18, "bold")
    MENU = ("Segoe UI", 14)
    BUTTON = ("Segoe UI", 12)
    TEXT = ("Segoe UI", 12)
    SMALL = ("Segoe UI", 10)

def configure_button_style():
    """Configura estilo padrão dos botões CTk."""
    style = {
        "corner_radius": 10,
        "border_width": 0,
        "fg_color": ThemeColors.SECONDARY,
        "hover_color": ThemeColors.BUTTON_HOVER,
        "text_color": ThemeColors.TEXT_LIGHT,
        "font": ThemeFonts.BUTTON
    }
    return style

def configure_entry_style():
    """Configura estilo padrão dos campos de entrada CTk."""
    style = {
        "corner_radius": 8,
        "border_width": 1,
        "fg_color": ThemeColors.BG,
        "border_color": ThemeColors.PRIMARY,
        "text_color": ThemeColors.TEXT,
        "placeholder_text_color": ThemeColors.TEXT_SECONDARY,
        "font": ThemeFonts.TEXT
    }
    return style

def configure_frame_style(is_card=False):
    """Configura estilo padrão dos frames CTk."""
    style = {
        "corner_radius": 12 if is_card else 0,
        "fg_color": ThemeColors.BG_SECONDARY if is_card else ThemeColors.BG,
        "border_width": 0
    }
    return style

class StyledButton(ctk.CTkButton):
    """Botão pre-estilizado seguindo o tema."""
    def __init__(self, *args, **kwargs):
        style = configure_button_style()
        # Permite override de qualquer propriedade do estilo
        style.update(kwargs)
        super().__init__(*args, **style)

class StyledEntry(ctk.CTkEntry):
    """Campo de entrada pre-estilizado seguindo o tema."""
    def __init__(self, *args, **kwargs):
        style = configure_entry_style()
        style.update(kwargs)
        super().__init__(*args, **style)

class CardFrame(ctk.CTkFrame):
    """Frame estilizado como card com sombra e cantos arredondados."""
    def __init__(self, *args, **kwargs):
        style = configure_frame_style(is_card=True)
        style.update(kwargs)
        super().__init__(*args, **style)

def apply_theme():
    """Aplica o tema global na aplicação."""
    # Configura tema global do CTk
    ctk.set_appearance_mode("light")  # Usa modo claro para combinar com as cores
    ctk.set_default_color_theme("blue")
    
    return {
        "colors": ThemeColors,
        "fonts": ThemeFonts,
        "button": configure_button_style(),
        "entry": configure_entry_style(),
        "frame": configure_frame_style
    }