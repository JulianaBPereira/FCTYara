import time
import tkinter as tk

from ui.Theme import theme as t

_menu_aberto: tk.Menu | None = None
_ultimo_toque_menu = 0.0
_INTERVALO_TOQUE_MENU = 0.28


def _fechar_menu() -> None:
    global _menu_aberto
    if _menu_aberto is None:
        return
    try:
        if _menu_aberto.winfo_ismapped():
            _menu_aberto.unpost()
    except tk.TclError:
        pass
    _menu_aberto = None


def _alternar_popup(menu: tk.Menu, rotulo: tk.Label) -> None:
    """Abre o submenu; toque repetido no mesmo rótulo fecha (touch)."""
    global _menu_aberto
    if _menu_aberto is menu and menu.winfo_ismapped():
        _fechar_menu()
        return
    _fechar_menu()
    menu.post(rotulo.winfo_rootx(), rotulo.winfo_rooty() + rotulo.winfo_height())
    _menu_aberto = menu


def _ao_clicar_rotulo(_event, menu: tk.Menu, rotulo: tk.Label) -> str:
    global _ultimo_toque_menu
    agora = time.monotonic()
    if agora - _ultimo_toque_menu < _INTERVALO_TOQUE_MENU:
        return "break"
    _ultimo_toque_menu = agora
    _alternar_popup(menu, rotulo)
    return "break"


def _criar_popup(janela, itens):
    """Popup de submenu (não nativo) com fonte e cores do tema."""
    menu = tk.Menu(janela, tearoff=0)
    menu.configure(
        bg=t.COR_BRANCO,
        fg=t.COR_AZUL_MARINHO,
        activebackground=t.COR_MENU_HOVER,
        activeforeground=t.COR_AZUL_MARINHO,
        relief="flat",
        borderwidth=1,
        activeborderwidth=0,
        font=t.FONTE_MENU,
    )
    for item in itens:
        if item is None:
            menu.add_separator()
        else:
            comando = item.get("command")
            if comando is not None:
                item = {
                    **item,
                    "command": lambda cmd=comando: (_fechar_menu(), cmd()),
                }
            menu.add_command(**item)
    return menu


def _criar_rotulo(barra, texto, menu):
    rotulo = tk.Label(
        barra,
        text=texto,
        font=t.FONTE_MENU,
        bg=t.COR_BRANCO,
        fg=t.COR_AZUL_MARINHO,
        padx=14,
        pady=8,
        cursor="hand2",
    )
    rotulo.pack(side="left")

    handler = lambda e, m=menu, r=rotulo: _ao_clicar_rotulo(e, m, r)
    rotulo.bind("<Button-1>", handler)
    rotulo.bind("<ButtonRelease-1>", handler)
    rotulo.bind("<Enter>", lambda _: rotulo.config(bg=t.COR_CINZA_CLARO))
    rotulo.bind("<Leave>", lambda _: rotulo.config(bg=t.COR_BRANCO))

    return rotulo


def criar_menu_principal(janela, aplicacao):
    """Barra de menu customizada: Arquivo, Receita e Configurações."""
    barra = tk.Frame(janela, bg=t.COR_BRANCO, highlightthickness=0)
    barra.pack(fill="x", side="top")

    separador = tk.Frame(janela, bg="#eef1f5", height=1)
    separador.pack(fill="x", side="top")

    menus = [
        ("Arquivo", [
            {"label": "Reiniciar", "command": aplicacao.reiniciar, "accelerator": "Ctrl+Shift+R"},
            None,
            {"label": "Sair", "command": janela.quit, "accelerator": "Alt+F4"},
        ]),
        ("Receita", [
            {"label": "Criar Receita…", "command": aplicacao.abrir_receita, "accelerator": "Ctrl+R"},
        ]),
        ("Configurações", [
            {"label": "Configurações…", "command": aplicacao.abrir_configuracao, "accelerator": "Ctrl+G"},
        ]),
    ]

    for texto, itens in menus:
        popup = _criar_popup(janela, itens)
        _criar_rotulo(barra, texto, popup)

    atalhos = {
        "<Control-Shift-R>": aplicacao.reiniciar,
        "<Control-r>": aplicacao.abrir_receita,
        "<Control-g>": aplicacao.abrir_configuracao,
    }
    for tecla, comando in atalhos.items():
        janela.bind(tecla, lambda _, cmd=comando: cmd())

    return barra
