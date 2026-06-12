# Juliana Pereira | Delta Sollutions - 2026
import os
import sys
from pathlib import Path

from ui.janela_configuracao import JanelaConfiguracao
from ui.janela_principal import JanelaPrincipal
from ui.janela_receita import JanelaReceita

class AplicacaoFCTDelta:
    # Coordena as janelas independentes do FCTDelta.

    def __init__(self):
        self.janela_principal: JanelaPrincipal | None = None
        self._janela_configuracao: JanelaConfiguracao | None = None
        self._janela_receita: JanelaReceita | None = None

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

    def abrir_receita(self, nome_editar=None) -> None:
        if self._esta_aberta(self._janela_receita):
            self._janela_receita.lift()
            self._janela_receita.focus_force()
            self._janela_receita.after(50, self._janela_receita.focar_entrada_inicial)
            return
        self._janela_receita = JanelaReceita(self, nome_editar=nome_editar)

    def _focar_barcode_principal(self) -> None:
        if self._esta_aberta(self.janela_principal):
            self.janela_principal.lift()
            self.janela_principal.after(50, self.janela_principal._focar_campo_barcode)

    def ao_fechar_configuracao(self) -> None:
        self._janela_configuracao = None
        if self._esta_aberta(self._janela_receita):
            self._janela_receita.lift()
            self._janela_receita.focus_force()
            self._janela_receita.after(50, self._janela_receita.focar_entrada_inicial)
        else:
            self._focar_barcode_principal()

    def ao_fechar_receita(self) -> None:
        self._janela_receita = None
        if self._esta_aberta(self._janela_configuracao):
            self._janela_configuracao.atualizar()
        else:
            self._focar_barcode_principal()

    def reiniciar(self) -> None:
        if self.janela_principal is None:
            return

        pasta_projeto = Path(__file__).resolve().parent
        script = pasta_projeto / "main.py"
        os.chdir(pasta_projeto)
        os.execv(sys.executable, [sys.executable, str(script)])