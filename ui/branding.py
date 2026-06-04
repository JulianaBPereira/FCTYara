"""Ícone da janela na barra de tarefas e na barra de título."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

_PASTA_IMAGENS = Path(__file__).resolve().parent / "Images"
LOGO_ICO = _PASTA_IMAGENS / "ELUX-LOGO.ico"
LOGO_PNG = _PASTA_IMAGENS / "ELUX-LOGO.png"


def aplicar_icone(janela: tk.Misc) -> None:
    """Define o ícone na barra de tarefas e na barra de título da janela."""
    if not LOGO_ICO.is_file():
        return
    try:
        janela.iconbitmap(str(LOGO_ICO))
    except tk.TclError:
        if LOGO_PNG.is_file():
            foto = tk.PhotoImage(file=str(LOGO_PNG))
            janela.iconphoto(True, foto)
            janela._icone_janela = foto  # noqa: SLF001 — manter referência viva


def configurar_app_id() -> None:
    """Agrupa janelas do app na barra de tarefas do Windows (ícone correto)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FTCYara.ELUX")
    except (AttributeError, OSError):
        pass
