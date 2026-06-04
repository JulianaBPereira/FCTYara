import tkinter as tk
from collections.abc import Callable

from ui.Theme import theme as t


class NavegacaoAbas:
    """Troca de abas só por rótulos clicáveis, sem borda de notebook."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trocar: Callable[[int], None] | None = None,
    ):
        self._on_trocar = on_trocar
        self._indice = 0
        self._rotulos: list[tk.Label] = []
        self._frames: list[tk.Frame] = []
        self._hover_indice: int | None = None

        self.widget = tk.Frame(parent, bg=t.COR_BRANCO)
        self.widget.pack(fill="both", expand=True)

        self._barra = tk.Frame(self.widget, bg=t.COR_BRANCO)
        self._barra.pack(fill="x", pady=(0, 8))

        self._area = tk.Frame(self.widget, bg=t.COR_BRANCO)
        self._area.pack(fill="both", expand=True)

    def adicionar_aba(self, titulo: str, montar: Callable[[tk.Frame], None]) -> tk.Frame:
        indice = len(self._rotulos)

        rotulo = tk.Label(
            self._barra,
            text=titulo,
            font=t.FONTE_MENU,
            bg=t.COR_BRANCO,
            fg=t.COR_PRIMARIA,
            padx=14,
            pady=8,
            cursor="hand2",
        )
        rotulo.pack(side="left")
        rotulo.bind("<Button-1>", lambda _, i=indice: self.selecionar(i))
        rotulo.bind("<Enter>", lambda _, i=indice: self._entrar(i))
        rotulo.bind("<Leave>", lambda _, i=indice: self._sair(i))
        self._rotulos.append(rotulo)

        frame = tk.Frame(self._area, bg=t.COR_BRANCO)
        frame.pack(fill="both", expand=True)
        montar(frame)
        self._frames.append(frame)

        if indice != 0:
            frame.pack_forget()

        if indice == 0:
            self._atualizar_rotulos()

        return frame

    def selecionar(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._frames):
            return
        if indice == self._indice:
            return

        self._frames[self._indice].pack_forget()
        self._indice = indice
        self._frames[self._indice].pack(fill="both", expand=True)
        self._atualizar_rotulos()

        if self._on_trocar:
            self._on_trocar(self._indice)

    @property
    def indice_atual(self) -> int:
        return self._indice

    def _entrar(self, indice: int) -> None:
        self._hover_indice = indice
        self._rotulos[indice].config(bg=t.COR_CINZA_CLARO)

    def _sair(self, indice: int) -> None:
        self._hover_indice = None
        self._atualizar_rotulos()

    def _atualizar_rotulos(self) -> None:
        for i, rotulo in enumerate(self._rotulos):
            if self._hover_indice == i:
                rotulo.config(
                    bg=t.COR_CINZA_CLARO,
                    fg=t.COR_AZUL_MARINHO if i == self._indice else t.COR_PRIMARIA,
                )
            elif i == self._indice:
                rotulo.config(bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO)
            else:
                rotulo.config(bg=t.COR_BRANCO, fg=t.COR_PRIMARIA)
