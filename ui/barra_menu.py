import tkinter as tk

from ui.Theme import theme as t


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
            menu.add_command(**item)
    return menu


def _abrir_popup(menu, rotulo):
    menu.post(rotulo.winfo_rootx(), rotulo.winfo_rooty() + rotulo.winfo_height())


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

    rotulo.bind("<Button-1>", lambda _: _abrir_popup(menu, rotulo))
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
