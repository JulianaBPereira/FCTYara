import os
import sys

from ui.janela_barcode import JanelaBarcode
from ui.janela_configuracao import JanelaConfiguracao
from ui.janela_principal import JanelaPrincipal
from ui.janela_receita import JanelaReceita

class AplicacaoFTCYara:
    # Coordena as janelas independentes do FTCYara.

    def __init__(self):
        self.janela_principal: JanelaPrincipal | None = None
        self._janela_configuracao: JanelaConfiguracao | None = None
        self._janela_receita: JanelaReceita | None = None
        self._janela_barcode: JanelaBarcode | None = None

    def iniciar(self) -> None:
        self.janela_principal = JanelaPrincipal(self)
        self.janela_principal.mainloop()

    @property
    def raiz(self):
        return self.janela_principal

    def _esta_aberta(self, janela) -> bool:
        return janela is not None and janela.winfo_exists()

    def abrir_configuracao(self) -> None:
        if self._esta_aberta(self._janela_configuracao):
            self._janela_configuracao.atualizar()
            self._janela_configuracao.lift()
            self._janela_configuracao.focus_force()
            return
        self._janela_configuracao = JanelaConfiguracao(self)

    def abrir_barcode(self, on_ler=None) -> None:
        if self._esta_aberta(self._janela_barcode):
            self._janela_barcode.lift()
            self._janela_barcode.focus_force()
            self._janela_barcode.after(50, self._janela_barcode.focar_campo)
            return
        self._janela_barcode = JanelaBarcode(self, on_ler=on_ler)

    def abrir_receita(self, nome_editar=None) -> None:
        if self._esta_aberta(self._janela_receita):
            self._janela_receita.lift()
            self._janela_receita.focus_force()
            return
        self._janela_receita = JanelaReceita(self, nome_editar=nome_editar)

    def ao_fechar_configuracao(self) -> None:
        self._janela_configuracao = None

    def ao_fechar_receita(self) -> None:
        self._janela_receita = None
        if self._esta_aberta(self._janela_configuracao):
            self._janela_configuracao.atualizar()

    def ao_fechar_barcode(self) -> None:
        self._janela_barcode = None

    def _fechar_janelas_secundarias(self) -> None:
        for janela in (
            self._janela_configuracao,
            self._janela_receita,
            self._janela_barcode,
        ):
            if self._esta_aberta(janela):
                janela.destroy()
        self._janela_configuracao = None
        self._janela_receita = None
        self._janela_barcode = None

    def reiniciar(self) -> None:
        # Fecha tudo e relança o processo do zero.
        if self.janela_principal is None:
            return

        self._fechar_janelas_secundarias()
        self.janela_principal.destroy()

        # Substitui o processo atual por uma nova execução do mesmo script.
        # Nada após essa linha é executado.
        os.execv(sys.executable, [sys.executable] + sys.argv)