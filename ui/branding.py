"""Ícone da janela na barra de tarefas e na barra de título."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

_PASTA_IMAGENS = Path(__file__).resolve().parent / "Images"
LOGO_ICO = _PASTA_IMAGENS / "Logo.ico"
LOGO_PNG = _PASTA_IMAGENS / "Logo.png"


def aplicar_icone(janela: tk.Misc) -> None:
    """Define o ícone na barra de tarefas e na barra de título da janela."""
    if LOGO_ICO.is_file():
        try:
            janela.iconbitmap(str(LOGO_ICO))
            return
        except tk.TclError:
            pass
    if LOGO_PNG.is_file():
        foto = tk.PhotoImage(file=str(LOGO_PNG))
        janela.iconphoto(True, foto)
        janela._icone_janela = foto  # noqa: SLF001 — manter referência viva


LARGURA_PADRAO = 1024
ALTURA_PADRAO = 600
GEOMETRIA_PADRAO = f"{LARGURA_PADRAO}x{ALTURA_PADRAO}"


def _posicao_centralizada(
    janela: tk.Misc,
    ref_x: int,
    ref_y: int,
    ref_largura: int,
    ref_altura: int,
) -> tuple[int, int]:
    janela.update_idletasks()
    # No Linux/X11, janelas retiradas (withdraw) retornam 1x1 antes de serem
    # mapeadas na tela. winfo_reqwidth/height reflete o tamanho real calculado
    # pelo gerenciador de layout, independente de a janela estar visível.
    w = janela.winfo_width()
    h = janela.winfo_height()
    if w <= 1:
        w = janela.winfo_reqwidth()
    if h <= 1:
        h = janela.winfo_reqheight()
    px = ref_x + (ref_largura - w) // 2
    py = ref_y + (ref_altura - h) // 2
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    px = max(0, min(px, largura_tela - w))
    py = max(0, min(py, altura_tela - h))
    return px, py


def centralizar_na_tela(janela: tk.Misc) -> None:
    """Centraliza a janela no monitor, sem sair da área visível."""
    px, py = _posicao_centralizada(
        janela,
        0,
        0,
        janela.winfo_screenwidth(),
        janela.winfo_screenheight(),
    )
    janela.geometry(f"+{px}+{py}")


def centralizar_janela(
    janela: tk.Misc,
    referencia: tk.Misc,
    *,
    largura: int | None = None,
    altura: int | None = None,
) -> None:
    """Centraliza em relação à janela de referência, sem sair da área visível."""
    if largura is not None and altura is not None:
        janela.geometry(f"{largura}x{altura}")
    referencia.update_idletasks()
    px, py = _posicao_centralizada(
        janela,
        referencia.winfo_rootx(),
        referencia.winfo_rooty(),
        referencia.winfo_width(),
        referencia.winfo_height(),
    )
    janela.geometry(f"+{px}+{py}")


def centralizar_dialogo(
    dialogo: tk.Misc,
    parent: tk.Misc,
    *,
    largura: int | None = None,
    altura: int | None = None,
) -> None:
    """Centraliza aviso ou diálogo sobre a janela principal da aplicação."""
    centralizar_janela(
        dialogo,
        parent.winfo_toplevel(),
        largura=largura,
        altura=altura,
    )


def configurar_app_id() -> None:
    """Agrupa janelas do app na barra de tarefas do Windows (ícone correto)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FCTDelta.ELUX")
    except (AttributeError, OSError):
        pass
