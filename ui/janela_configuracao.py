import tkinter as tk

from ui.branding import GEOMETRIA_PADRAO, aplicar_icone, centralizar_janela
from ui.Theme import theme as t
from ui.AbasConfiguracao.aba_geral import AbaGeral
from ui.AbasConfiguracao.aba_rastreio import AbaRastreio
from ui.AbasConfiguracao.navegacao_abas import NavegacaoAbas


class JanelaConfiguracao(tk.Toplevel):
    # Janela de configuração: abas Geral e Rastreio.

    def __init__(self, aplicacao):
        super().__init__(aplicacao.raiz)
        self.aplicacao = aplicacao
        self.aba_geral: AbaGeral | None = None

        self.title("Configuração")
        self.geometry(GEOMETRIA_PADRAO)
        self.resizable(True, True)
        self.minsize(640, 400)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self._navegacao: NavegacaoAbas | None = None
        self._rodape: tk.Frame | None = None
        self._montar_interface()
        centralizar_janela(self, aplicacao.raiz)
        self.protocol("WM_DELETE_WINDOW", self._fechar)

    def _montar_interface(self):
        p = tk.Frame(self, bg=t.COR_BRANCO)
        p.pack(fill="both", expand=True, padx=20, pady=16)

        self._rodape = tk.Frame(p, bg=t.COR_BRANCO)
        self._rodape.pack(side="bottom", fill="x", pady=(12, 0))
        self._montar_rodape_geral()

        self._navegacao = NavegacaoAbas(p, on_trocar=self._ao_trocar_aba)

        self._navegacao.adicionar_aba(
            "Geral",
            lambda parent: self._montar_aba_geral(parent),
        )
        self._navegacao.adicionar_aba(
            "Rastreio",
            lambda parent: AbaRastreio(self, parent, ao_fechar_janela=self._fechar),
        )

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
            if not self._rodape.winfo_ismapped():
                self._rodape.pack(side="bottom", fill="x", pady=(12, 0))
        else:
            self._rodape.pack_forget()

    def atualizar(self) -> None:
        if self.aba_geral:
            self.aba_geral.atualizar()

    def _salvar_geral(self):
        if self.aba_geral:
            self.aba_geral.salvar()

    def _fechar(self):
        if self.aba_geral:
            self.aba_geral.limpar_combos()
        self.aplicacao.ao_fechar_configuracao()
        self.destroy()
