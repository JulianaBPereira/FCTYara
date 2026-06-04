import tkinter as tk

from ui.branding import aplicar_icone, centralizar_janela
from ui.Theme import theme as t

_PLACEHOLDER = "Scannei a peça"
_COR_PLACEHOLDER = "#94a3b8"


class JanelaBarcode(tk.Toplevel):
    """Janela compacta para leitura de código de barras."""

    def __init__(self, aplicacao, *, on_ler=None):
        super().__init__(aplicacao.raiz)
        self.aplicacao = aplicacao
        self._on_ler = on_ler
        self._placeholder_ativo = True

        self.title("Leitura de código")
        self.geometry("420x96")
        self.resizable(False, False)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self._montar_interface()
        centralizar_janela(self, aplicacao.raiz)
        self.protocol("WM_DELETE_WINDOW", self._fechar)

        self.after(50, self.focar_campo)

    def focar_campo(self) -> None:
        self._campo.focus_set()
        self._ao_focar()

    def _montar_interface(self):
        painel = tk.Frame(self, bg=t.COR_BRANCO)
        painel.pack(fill="both", expand=True, padx=20, pady=16)
        painel.grid_columnconfigure(0, weight=1)

        borda = tk.Frame(
            painel,
            bg=t.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=t.COR_PRIMARIA,
        )
        borda.grid(row=0, column=0, sticky="ew")

        self._campo = tk.Entry(
            borda,
            font=t.FONTE_NORMAL,
            relief="flat",
            bd=0,
            bg=t.COR_BRANCO,
            fg=_COR_PLACEHOLDER,
            insertbackground=t.COR_AZUL_MARINHO,
        )
        self._campo.pack(fill="x", padx=10, pady=8)
        self._campo.insert(0, _PLACEHOLDER)

        self._campo.bind("<FocusIn>", self._ao_focar)
        self._campo.bind("<FocusOut>", self._ao_desfocar)
        self._campo.bind("<Return>", self._ao_confirmar)

    def _ao_focar(self, _event=None) -> None:
        if self._placeholder_ativo:
            self._campo.delete(0, "end")
            self._campo.configure(fg=t.COR_AZUL_MARINHO)
            self._placeholder_ativo = False

    def _ao_desfocar(self, _event=None) -> None:
        if not self._campo.get().strip():
            self._mostrar_placeholder()

    def _mostrar_placeholder(self) -> None:
        self._campo.delete(0, "end")
        self._campo.insert(0, _PLACEHOLDER)
        self._campo.configure(fg=_COR_PLACEHOLDER)
        self._placeholder_ativo = True

    def valor(self) -> str:
        texto = self._campo.get().strip()
        if self._placeholder_ativo or texto == _PLACEHOLDER:
            return ""
        return texto

    def _ao_confirmar(self, _event=None) -> None:
        codigo = self.valor()
        if not codigo:
            return "break"
        on_ler = self._on_ler
        self._fechar()
        if on_ler:
            on_ler(codigo)
        return "break"

    def _fechar(self):
        self.aplicacao.ao_fechar_barcode()
        self.destroy()
