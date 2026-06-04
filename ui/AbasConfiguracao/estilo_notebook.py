import tkinter as tk
from collections.abc import Callable

from ui.Theme import theme as t

_COR_BORDA = "#eef1f5"


class PainelAbasConfig:
    """Abas com contorno interno e hover cinza claro (igual ao menu)."""

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

        self.widget = tk.Frame(
            parent,
            bg=t.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=_COR_BORDA,
            highlightcolor=_COR_BORDA,
        )
        self.widget.grid_columnconfigure(0, weight=1)
        self.widget.grid_rowconfigure(2, weight=1)

        self._barra = tk.Frame(self.widget, bg=t.COR_BRANCO)
        self._barra.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

        separador = tk.Frame(self.widget, bg=_COR_BORDA, height=1)
        separador.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 0))

        self._area = tk.Frame(self.widget, bg=t.COR_BRANCO)
        self._area.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 12))
        self._area.grid_columnconfigure(0, weight=1)
        self._area.grid_rowconfigure(0, weight=1)

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
        frame.grid(row=0, column=0, sticky="nsew")
        montar(frame)
        self._frames.append(frame)

        if indice == 0:
            self._atualizar_rotulos()
        else:
            frame.grid_remove()

        return frame

    def selecionar(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._frames):
            return
        if indice == self._indice:
            return

        self._frames[self._indice].grid_remove()
        self._indice = indice
        self._frames[self._indice].grid()
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


def aplicar_estilo_notebook(_janela) -> None:
    """Mantido por compatibilidade; abas usam PainelAbasConfig."""
