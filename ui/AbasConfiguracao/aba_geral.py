import tkinter as tk
from enum import Enum
from tkinter import ttk

from infrastructure.serial_port import listar_portas
from services.recipe_service import ReceitaService
from services.settings_service import SettingsService, carregar_configuracao
from ui.Avisos.mensagem import mostrar as mostrar_mensagem
from ui.Theme import theme as t


class Baud(Enum):
    B115200 = 115200
    B9600 = 9600
    B19200 = 19200
    B38400 = 38400
    B57600 = 57600
    B230400 = 230400
    B460800 = 460800
    B921600 = 921600

    def __str__(self) -> str:
        return str(self.value)


_FONTE_COMBO = (t.FONTE_NORMAL[0], 14)
_MAX_ITENS_VISIVEIS = 5


class AbaGeral:
    def __init__(self, janela, aplicacao, parent: tk.Frame, *, ao_fechar_janela):
        self.janela = janela
        self.aplicacao = aplicacao
        self._ao_fechar_janela = ao_fechar_janela
        self._estilo_combobox()
        self._montar(parent)

    def _estilo_combobox(self):
        self.janela.option_add("*TCombobox*Listbox.font", _FONTE_COMBO)

        estilo = ttk.Style(self.janela)
        estilo.configure(
            "Config.TCombobox",
            font=_FONTE_COMBO,
            padding=(8, 6),
            fieldbackground=t.COR_BRANCO,
            background=t.COR_BRANCO,
            foreground=t.COR_AZUL_MARINHO,
            arrowcolor=t.COR_AZUL_MARINHO,
            borderwidth=1,
            relief="solid",
            arrowsize=16,
        )
        estilo.map(
            "Config.TCombobox",
            fieldbackground=[("readonly", t.COR_BRANCO)],
            selectbackground=[("readonly", t.COR_BRANCO)],
            selectforeground=[("readonly", t.COR_AZUL_MARINHO)],
            bordercolor=[("readonly", t.COR_BRANCO)],
        )

    def _montar(self, parent: tk.Frame):
        self._painel_aba = parent
        form = tk.Frame(parent, bg=t.COR_BRANCO)
        form.pack(fill="x", padx=40, pady=16)

        settings = carregar_configuracao()
        porta_salva = settings.channelAPort if settings else ""
        baud_salvo = settings.channelABaud if settings else ""
        receita_salva = settings.channelARecipe if settings else ""

        self._portas(form, porta_salva)
        self._baud(form, baud_salvo)
        self._receitas(form, receita_salva)

    def _rolagem_combo(self, combo):
        def ajustar():
            if not combo.winfo_exists():
                return
            try:
                popdown = combo.tk.call("ttk::combobox::PopdownWindow", combo)
            except tk.TclError:
                return
            if not popdown:
                return

            caminho = str(popdown)
            if not caminho.startswith("."):
                caminho = f"{combo._w}.{caminho}"
            listbox = f"{caminho}.f.l"
            if not combo.tk.call("winfo", "exists", listbox):
                return

            itens = combo.cget("values")
            if isinstance(itens, str):
                itens = combo.tk.splitlist(itens)
            total = len(itens)
            visiveis = min(_MAX_ITENS_VISIVEIS, max(total, 1))
            try:
                combo.tk.call(
                    listbox,
                    "configure",
                    "-height",
                    visiveis,
                    "-font",
                    _FONTE_COMBO,
                )
            except tk.TclError:
                pass

        def ao_abrir():
            if combo.winfo_exists():
                combo.after_idle(ajustar)

        combo.configure(postcommand=ao_abrir)

    def _combo_campo(self, parent, rotulo, valores, valor_atual, *, margem_superior=0):
        tk.Label(
            parent,
            text=rotulo,
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        ).pack(anchor="w", pady=(margem_superior, 6))

        combo = ttk.Combobox(
            parent,
            state="readonly",
            values=valores,
            style="Config.TCombobox",
        )
        combo.pack(fill="x", pady=(0, 20))

        texto = str(valor_atual) if valor_atual else ""
        if texto in valores:
            combo.set(texto)
        elif valores:
            combo.set(valores[0])

        self._rolagem_combo(combo)
        return combo

    def _portas(self, parent, valor_atual: str = ""):
        portas = listar_portas()
        if valor_atual and valor_atual not in portas:
            portas = [valor_atual, *portas]
        self.combo_porta = self._combo_campo(
            parent, "Porta COM", portas, valor_atual,
        )

    def _baud(self, parent, valor_atual: int | str = ""):
        valores = [str(b) for b in Baud]
        self.combo_baud = self._combo_campo(
            parent, "Baud rate", valores, valor_atual,
        )

    def _receitas(self, parent, valor_atual: str = ""):
        receitas = ReceitaService("", []).carregar_receitas()
        nomes = [receita.title for receita in receitas]
        self.combo_receita = self._combo_campo(
            parent,
            "Receitas",
            nomes,
            valor_atual,
            margem_superior=8,
        )

    def atualizar(self) -> None:
        settings = carregar_configuracao()
        porta_salva = settings.channelAPort if settings else ""
        baud_salvo = settings.channelABaud if settings else ""
        receita_salva = settings.channelARecipe if settings else ""

        portas = listar_portas()
        if porta_salva and porta_salva not in portas:
            portas = [porta_salva, *portas]
        self.combo_porta.configure(values=portas)
        if porta_salva in portas:
            self.combo_porta.set(porta_salva)
        elif portas:
            self.combo_porta.set(portas[0])

        if baud_salvo:
            self.combo_baud.set(str(baud_salvo))

        self.atualizar_receitas()
        if receita_salva:
            nomes = self.combo_receita.cget("values")
            if isinstance(nomes, str):
                nomes = self.janela.tk.splitlist(nomes)
            if receita_salva in nomes:
                self.combo_receita.set(receita_salva)

    def atualizar_receitas(self) -> None:
        receitas = ReceitaService("", []).carregar_receitas()
        nomes = [receita.title for receita in receitas]
        atual = self.combo_receita.get()
        self.combo_receita.configure(values=nomes)
        if atual in nomes:
            self.combo_receita.set(atual)
        elif nomes:
            self.combo_receita.set(nomes[0])
        else:
            self.combo_receita.set("")

    def limpar_combos(self):
        for combo in (self.combo_porta, self.combo_baud, self.combo_receita):
            try:
                if combo.winfo_exists():
                    combo.configure(postcommand="")
            except tk.TclError:
                pass

    def salvar(self):
        baud = int(self.combo_baud.get())
        erro = SettingsService(
            self.combo_porta.get(),
            baud,
            self.combo_receita.get(),
        ).salvar_configuracao()
        if erro:
            mostrar_mensagem(self._painel_aba, "", erro, tipo="aviso")
            return
        self.aplicacao.janela_principal.aplicar_configuracao(
            self.combo_porta.get(),
            baud,
            self.combo_receita.get(),
        )
        mostrar_mensagem(self._painel_aba, "", "Salvo com sucesso.")
        self._ao_fechar_janela()
