import tkinter as tk

from ui.branding import aplicar_icone
from ui.Theme import theme as t
from ui.AbasConfiguracao.aba_geral import AbaGeral
from ui.AbasConfiguracao.aba_rastreio import AbaRastreio
from ui.AbasConfiguracao.estilo_notebook import PainelAbasConfig


class JanelaConfiguracao(tk.Toplevel):
    # Janela de configuração: abas Geral e Rastreio log.

    def __init__(self, aplicacao):
        super().__init__(aplicacao.raiz)
        self.aplicacao = aplicacao
        self.aba_geral: AbaGeral | None = None

        self.title("Configuração")
        self.geometry("720x480")
        self.resizable(True, True)
        self.minsize(680, 440)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self._painel_abas: PainelAbasConfig | None = None
        self._rodape: tk.Frame | None = None
        self._montar_interface()
        self._centralizar(aplicacao.raiz)
        self.protocol("WM_DELETE_WINDOW", self._fechar)

    def _montar_interface(self):
        p = tk.Frame(self, bg=t.COR_BRANCO)
        p.pack(fill="both", expand=True, padx=20, pady=16)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        self._painel_abas = PainelAbasConfig(p, on_trocar=self._ao_trocar_aba)
        self._painel_abas.widget.grid(row=0, column=0, sticky="nsew")

        frame_geral = self._painel_abas.adicionar_aba("Geral", self._montar_aba_geral)
        self._painel_abas.adicionar_aba("Rastreio log", lambda parent: AbaRastreio(self, parent))

        frame_geral.grid_columnconfigure(0, weight=1)
        frame_geral.grid_rowconfigure(0, weight=1)

        self._rodape = tk.Frame(p, bg=t.COR_BRANCO)
        self._rodape.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self._montar_rodape_geral()
        self._ao_trocar_aba(0)

    def _montar_aba_geral(self, parent: tk.Frame) -> None:
        self.aba_geral = AbaGeral(
            self,
            self.aplicacao,
            parent,
            ao_fechar_janela=self._fechar,
        )

    def _montar_rodape_geral(self):
        acoes = tk.Frame(self._rodape, bg=t.COR_BRANCO)
        acoes.pack(side="right", padx=12)

        tk.Button(
            acoes,
            text="Cancelar",
            font=t.FONTE_NORMAL,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=14,
            pady=6,
            command=self._fechar,
        ).pack(side="left")

        tk.Button(
            acoes,
            text="Salvar",
            font=t.FONTE_NORMAL,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=14,
            pady=6,
            command=self._salvar_geral,
        ).pack(side="left", padx=(12, 0))

    def _ao_trocar_aba(self, indice: int) -> None:
        if indice == 0:
            self._rodape.grid()
        else:
            self._rodape.grid_remove()

    def atualizar(self) -> None:
        if self.aba_geral:
            self.aba_geral.atualizar_receitas()

    def _salvar_geral(self):
        if self.aba_geral:
            self.aba_geral.salvar()

    def _centralizar(self, ref):
        self.update_idletasks()
        px = ref.winfo_x() + ref.winfo_width() // 2 - self.winfo_width() // 2
        py = ref.winfo_y() + ref.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{px}+{py}")

    def _fechar(self):
        if self.aba_geral:
            self.aba_geral.limpar_combos()
        self.aplicacao.ao_fechar_configuracao()
        self.destroy()
