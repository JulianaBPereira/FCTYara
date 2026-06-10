# Juliana Pereira | Delta Sollutions - 2026
import time
import tkinter as tk

from ui.Theme import theme as t

COR_BORDA = "#eef1f5"
PAD_ITEM_X = 22
PAD_ITEM_Y = 14
LARGURA_MIN = 280
INTERVALO_TOQUE = 0.28
GRACA_APOS_ABRIR = 0.45

_menu_aberto = None
_barra_menu = None
_ultimo_toque = 0.0
_ultimo_clique_item = 0.0


def fechar_menu():
    global _menu_aberto
    if _menu_aberto is None:
        return
    _menu_aberto.fechar()
    _menu_aberto = None


def _widget_na_barra(widget) -> bool:
    if _barra_menu is None or widget is None:
        return False
    atual = widget
    while atual is not None:
        if atual == _barra_menu:
            return True
        atual = getattr(atual, "master", None)
    return False


class Submenu:
    def __init__(self, janela, itens):
        self.janela = janela
        self.itens = itens
        self.popup = None
        self._bind_fora = None
        self._aberto_em = 0.0

    def aberto(self):
        if self.popup is None:
            return False
        try:
            return self.popup.winfo_viewable()
        except tk.TclError:
            return False

    def fechar(self):
        if self._bind_fora:
            try:
                self.janela.unbind("<ButtonRelease-1>", self._bind_fora)
            except tk.TclError:
                pass
            self._bind_fora = None
        if self.popup:
            try:
                self.popup.destroy()
            except tk.TclError:
                pass
            self.popup = None

    def abrir(self, x, y):
        self.fechar()

        popup = tk.Toplevel(self.janela)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.configure(bg=COR_BORDA)

        borda = tk.Frame(popup, bg=COR_BORDA, padx=1, pady=1)
        borda.pack(fill="both", expand=True)

        lista = tk.Frame(borda, bg=t.COR_BRANCO)
        lista.pack(fill="both", expand=True)

        for item in self.itens:
            if item is None:
                tk.Frame(lista, bg=COR_BORDA, height=1).pack(fill="x", padx=10, pady=6)
            else:
                self._montar_item(lista, item)

        popup.update_idletasks()
        largura = max(LARGURA_MIN, lista.winfo_reqwidth() + 4)
        altura = lista.winfo_reqheight() + 4
        popup.geometry(f"{largura}x{altura}+{x}+{y}")
        popup.deiconify()
        popup.attributes("-topmost", True)
        self.popup = popup
        self._aberto_em = time.monotonic()

        self.janela.after(350, self._ouvir_clique_fora)

    @staticmethod
    def _clique_dentro_popup(popup, widget) -> bool:
        atual = widget
        while atual is not None:
            if atual == popup:
                return True
            atual = getattr(atual, "master", None)
        return False

    def _ouvir_clique_fora(self):
        def fora(event):
            if _menu_aberto is not self or self.popup is None:
                return
            if time.monotonic() - self._aberto_em < GRACA_APOS_ABRIR:
                return
            if self._clique_dentro_popup(self.popup, event.widget):
                return
            if _widget_na_barra(event.widget):
                return
            fechar_menu()

        self._bind_fora = self.janela.bind("<ButtonRelease-1>", fora, add="+")

    def _montar_item(self, lista, item):
        comando = item.get("command")
        atalho = item.get("accelerator", "")

        linha = tk.Frame(lista, bg=t.COR_BRANCO, cursor="hand2")
        linha.pack(fill="x")

        tk.Label(
            linha,
            text=item["label"],
            font=t.FONTE_MENU_ITEM,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            anchor="w",
            padx=PAD_ITEM_X,
            pady=PAD_ITEM_Y,
        ).pack(side="left", fill="x", expand=True)

        if atalho:
            tk.Label(
                linha,
                text=atalho,
                font=t.FONTE_MENU_ATALHO,
                bg=t.COR_BRANCO,
                fg=t.COR_PRIMARIA,
                padx=16,
                pady=PAD_ITEM_Y,
            ).pack(side="right")

        def clicar(_event=None):
            global _ultimo_clique_item

            if comando is None:
                return

            agora = time.monotonic()
            if agora - _ultimo_clique_item < INTERVALO_TOQUE:
                return
            _ultimo_clique_item = agora

            cmd = comando
            fechar_menu()
            cmd()

        def hover(entra):
            cor = t.COR_MENU_HOVER if entra else t.COR_BRANCO
            linha.configure(bg=cor)
            for filho in linha.winfo_children():
                filho.configure(bg=cor)

        for widget in (linha, *linha.winfo_children()):
            widget.bind("<Button-1>", clicar)
            widget.bind("<ButtonRelease-1>", clicar)
            widget.bind("<Enter>", lambda _: hover(True))
            widget.bind("<Leave>", lambda _: hover(False))


def _ao_clicar_rotulo(menu, rotulo):
    global _menu_aberto, _ultimo_toque

    agora = time.monotonic()
    if agora - _ultimo_toque < INTERVALO_TOQUE:
        return "break"
    _ultimo_toque = agora

    if _menu_aberto is menu and menu.aberto():
        fechar_menu()
    else:
        fechar_menu()
        menu.abrir(
            rotulo.winfo_rootx(),
            rotulo.winfo_rooty() + rotulo.winfo_height(),
        )
        _menu_aberto = menu

    return "break"


def _montar_rotulo(barra, texto, menu):
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

    # Só ButtonRelease-1: no touch, pressionar + soltar abriam e fechavam o submenu.
    rotulo.bind("<ButtonRelease-1>", lambda e: _ao_clicar_rotulo(menu, rotulo))
    rotulo.bind("<Enter>", lambda _: rotulo.config(bg=t.COR_CINZA_CLARO))
    rotulo.bind("<Leave>", lambda _: rotulo.config(bg=t.COR_BRANCO))


def criar_menu_principal(janela, aplicacao):
    global _barra_menu

    barra = tk.Frame(janela, bg=t.COR_BRANCO, highlightthickness=0)
    _barra_menu = barra
    barra.pack(fill="x", side="top")

    tk.Frame(janela, bg=COR_BORDA, height=1).pack(fill="x", side="top")

    definicao = [
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

    for titulo, itens in definicao:
        _montar_rotulo(barra, titulo, Submenu(janela, itens))

    for tecla, acao in {
        "<Control-Shift-R>": aplicacao.reiniciar,
        "<Control-r>": aplicacao.abrir_receita,
        "<Control-g>": aplicacao.abrir_configuracao,
    }.items():
        janela.bind(tecla, lambda _, cmd=acao: (fechar_menu(), cmd()))

    return barra
