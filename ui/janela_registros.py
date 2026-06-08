# Juliana Pereira | Delta Sollutions - 2026
import calendar as cal_mod
import os
import tkinter as tk
from datetime import date
from tkinter import ttk

from services.log_service import listar_logs
from services.rastreio_service import pasta_logs_efetiva
from ui.branding import GEOMETRIA_PADRAO, aplicar_icone, centralizar_janela
from ui.Theme import theme as t

_COR_BORDA = "#eef1f5"
_COR_CABECALHO = "#64748b"
_COR_PLACEHOLDER = "#94a3b8"
_COR_BTN_SECUNDARIO = "#e2e8f0"
_COR_BTN_SECUNDARIO_TXT = "#94a3b8"
_COR_DIA_HOVER = t.COR_MENU_HOVER
_COR_DIA_SEL = t.COR_AZUL_MARINHO

_COLUNAS = ("Arquivo", "Tipo", "Resultado", "Data / hora", "Pasta")
_OPCOES_TIPO = ("Todos", "TXT", "Excel")
_OPCOES_RESULTADO = ("Todos", "PASS", "FAIL")
_MSG_VAZIO = "Nenhum registro encontrado com os filtros atuais."
_FMT_DATA = "%d/%m/%Y"
_DIAS_SEMANA = ("Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb")


class _PopupCalendario(tk.Toplevel):
    """Calendário mensal para escolha de data."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        titulo: str,
        data_ref: date | None,
        on_escolher,
    ):
        super().__init__(parent)
        self._on_escolher = on_escolher
        hoje = date.today()
        self._ano = (data_ref or hoje).year
        self._mes = (data_ref or hoje).month

        self.title(titulo)
        self.configure(bg=t.COR_BRANCO)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._montar()
        self._desenhar_mes()
        centralizar_janela(self, parent.winfo_toplevel())

    def _montar(self) -> None:
        topo = tk.Frame(self, bg=t.COR_BRANCO)
        topo.pack(fill="x", padx=12, pady=(12, 8))

        tk.Button(
            topo, text="‹", font=t.FONTE_BOLD, width=2,
            bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO,
            activebackground=_COR_DIA_HOVER, relief="flat", bd=0,
            cursor="hand2", command=self._mes_anterior,
        ).pack(side="left")

        self._lbl_mes = tk.Label(
            topo, font=t.FONTE_BOLD, bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO,
        )
        self._lbl_mes.pack(side="left", expand=True)

        tk.Button(
            topo, text="›", font=t.FONTE_BOLD, width=2,
            bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO,
            activebackground=_COR_DIA_HOVER, relief="flat", bd=0,
            cursor="hand2", command=self._mes_seguinte,
        ).pack(side="right")

        cab = tk.Frame(self, bg=t.COR_BRANCO)
        cab.pack(fill="x", padx=12)
        for dia in _DIAS_SEMANA:
            tk.Label(
                cab, text=dia, width=4, font=t.FONTE_NORMAL,
                bg=t.COR_BRANCO, fg=_COR_CABECALHO,
            ).pack(side="left")

        self._grade = tk.Frame(self, bg=t.COR_BRANCO)
        self._grade.pack(padx=12, pady=(4, 12))

        rodape = tk.Frame(self, bg=t.COR_BRANCO)
        rodape.pack(fill="x", padx=12, pady=(0, 12))

        tk.Button(
            rodape, text="Limpar", font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_PRIMARIA,
            activebackground=_COR_DIA_HOVER, relief="flat", bd=0,
            cursor="hand2", command=self._limpar,
        ).pack(side="left")

        tk.Button(
            rodape, text="Hoje", font=t.FONTE_NORMAL,
            bg=t.COR_AZUL_MARINHO, fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white", relief="flat", bd=0,
            padx=12, pady=4, cursor="hand2",
            command=lambda: self._escolher(date.today()),
        ).pack(side="right")

    def _nome_mes(self) -> str:
        nomes = (
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        )
        return f"{nomes[self._mes]} {self._ano}"

    def _mes_anterior(self) -> None:
        if self._mes == 1:
            self._mes, self._ano = 12, self._ano - 1
        else:
            self._mes -= 1
        self._desenhar_mes()

    def _mes_seguinte(self) -> None:
        if self._mes == 12:
            self._mes, self._ano = 1, self._ano + 1
        else:
            self._mes += 1
        self._desenhar_mes()

    def _desenhar_mes(self) -> None:
        self._lbl_mes.config(text=self._nome_mes())
        for w in self._grade.winfo_children():
            w.destroy()

        semanas = cal_mod.monthcalendar(self._ano, self._mes)
        hoje = date.today()

        for semana in semanas:
            linha = tk.Frame(self._grade, bg=t.COR_BRANCO)
            linha.pack()
            for dia in semana:
                if dia == 0:
                    tk.Label(
                        linha, text="", width=4, bg=t.COR_BRANCO,
                    ).pack(side="left", padx=1, pady=1)
                    continue

                d = date(self._ano, self._mes, dia)
                eh_hoje = d == hoje
                tk.Button(
                    linha,
                    text=str(dia),
                    width=3,
                    font=t.FONTE_BOLD if eh_hoje else t.FONTE_NORMAL,
                    bg=_COR_DIA_SEL if eh_hoje else t.COR_BRANCO,
                    fg="white" if eh_hoje else t.COR_AZUL_MARINHO,
                    activebackground=t.COR_AZUL_MARINHO_HOVER,
                    activeforeground="white",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda dd=d: self._escolher(dd),
                ).pack(side="left", padx=1, pady=1)

    def _escolher(self, escolhida: date) -> None:
        self._on_escolher(escolhida)
        self.destroy()

    def _limpar(self) -> None:
        self._on_escolher(None)
        self.destroy()


class _ComboFiltro:
    def __init__(self, parent: tk.Widget, valores: tuple[str, ...]):
        self.frame = tk.Frame(parent, bg=t.COR_BRANCO)
        self.combo = ttk.Combobox(
            self.frame,
            state="readonly",
            values=valores,
            style="Registros.TCombobox",
        )
        self.combo.set(valores[0])
        self.combo.pack(fill="x", padx=(0, 4), pady=4)


class _SeletorData:
    def __init__(self, parent: tk.Widget, *, rotulo_popup: str, placeholder: str):
        self._placeholder = placeholder
        self._rotulo_popup = rotulo_popup
        self._data: date | None = None

        self.frame = tk.Frame(parent, bg=t.COR_BRANCO)
        linha = tk.Frame(self.frame, bg=t.COR_BRANCO)
        linha.pack(fill="x", padx=(0, 4), pady=4)

        self.entry = tk.Entry(
            linha,
            font=t.FONTE_NORMAL,
            relief="flat",
            bd=0,
            bg=t.COR_BRANCO,
            fg=_COR_PLACEHOLDER,
            insertbackground=t.COR_AZUL_MARINHO,
            state="readonly",
            readonlybackground=t.COR_BRANCO,
            cursor="hand2",
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self._mostrar_placeholder()

        self.btn_cal = tk.Button(
            linha,
            text="\U0001f4c5",
            font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO,
            fg=_COR_PLACEHOLDER,
            activebackground=_COR_DIA_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._abrir_calendario,
        )
        self.btn_cal.pack(side="right", padx=(4, 0))

        self.entry.bind("<Button-1>", lambda _: self._abrir_calendario())

    def _mostrar_placeholder(self) -> None:
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, self._placeholder)
        self.entry.configure(fg=_COR_PLACEHOLDER, state="readonly")

    def _mostrar_data(self, d: date) -> None:
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, d.strftime(_FMT_DATA))
        self.entry.configure(fg=t.COR_AZUL_MARINHO, state="readonly")

    def _abrir_calendario(self) -> None:
        _PopupCalendario(
            self.btn_cal,
            titulo=self._rotulo_popup,
            data_ref=self._data,
            on_escolher=self._ao_escolher,
        )

    def _ao_escolher(self, escolhida: date | None) -> None:
        self._data = escolhida
        if escolhida is None:
            self._mostrar_placeholder()
        else:
            self._mostrar_data(escolhida)

    def valor(self) -> date | None:
        return self._data


class _EntradaSerial:
    def __init__(self, parent: tk.Widget, *, placeholder: str):
        self._placeholder = placeholder
        self.frame = tk.Frame(parent, bg=t.COR_BRANCO)

        self.entry = tk.Entry(
            self.frame,
            font=t.FONTE_NORMAL,
            relief="flat",
            bd=0,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            insertbackground=t.COR_AZUL_MARINHO,
        )
        self.entry.pack(fill="x", padx=(0, 4), pady=4)

        self._mostrar_placeholder()
        self.entry.bind("<FocusIn>", self._ao_focar)
        self.entry.bind("<FocusOut>", self._ao_desfocar)

    def _mostrar_placeholder(self) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, self._placeholder)
        self.entry.configure(fg=_COR_PLACEHOLDER)

    def _ao_focar(self, _event=None) -> None:
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=t.COR_AZUL_MARINHO)

    def _ao_desfocar(self, _event=None) -> None:
        if not self.entry.get().strip():
            self._mostrar_placeholder()

    def valor(self) -> str:
        texto = self.entry.get().strip()
        if texto == self._placeholder:
            return ""
        return texto


class JanelaRegistros(tk.Toplevel):
    """Consulta de registros de teste (TXT e Excel) — somente UI."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao.raiz)
        self.aplicacao = aplicacao

        self.title("Registros")
        self.geometry(GEOMETRIA_PADRAO)
        self.resizable(True, True)
        self.minsize(640, 400)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self._label_status: tk.Label | None = None
        self._btn_abrir: tk.Button | None = None

        self._montar_interface()
        centralizar_janela(self, aplicacao.raiz)
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.after_idle(self._atualizar)

    def _montar_interface(self) -> None:
        painel = tk.Frame(self, bg=t.COR_BRANCO)
        painel.pack(fill="both", expand=True, padx=24, pady=20)
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(2, weight=1)

        tk.Label(
            painel,
            text="Registros de teste (TXT e Excel)",
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        self._montar_filtros(painel)
        self._montar_tabela(painel)
        self._montar_rodape(painel)

    def _montar_filtros(self, painel: tk.Frame) -> None:
        caixa = tk.Frame(
            painel,
            bg=t.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=_COR_BORDA,
        )
        caixa.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        caixa.grid_columnconfigure(0, weight=1)
        caixa.grid_columnconfigure(1, weight=1)
        caixa.grid_columnconfigure(2, weight=1)
        caixa.grid_columnconfigure(3, weight=1)

        conteudo = tk.Frame(caixa, bg=t.COR_BRANCO)
        conteudo.pack(fill="x", padx=16, pady=14)
        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_columnconfigure(1, weight=1)
        conteudo.grid_columnconfigure(2, weight=1)
        conteudo.grid_columnconfigure(3, weight=1)

        self._estilizar_combos()

        self._combo_tipo = _ComboFiltro(conteudo, _OPCOES_TIPO)
        self._combo_tipo.frame.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._combo_resultado = _ComboFiltro(conteudo, _OPCOES_RESULTADO)
        self._combo_resultado.frame.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self._data_inicial = _SeletorData(
            conteudo,
            rotulo_popup="Data inicial",
            placeholder="Data inicial",
        )
        self._data_inicial.frame.grid(row=0, column=2, sticky="ew", padx=(0, 12))

        self._data_final = _SeletorData(
            conteudo,
            rotulo_popup="Data final",
            placeholder="Data final",
        )
        self._data_final.frame.grid(row=0, column=3, sticky="ew")

        linha2 = tk.Frame(conteudo, bg=t.COR_BRANCO)
        linha2.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        linha2.grid_columnconfigure(0, weight=1)

        self._campo_serial = _EntradaSerial(
            linha2,
            placeholder="Serial (parte do nome)",
        )
        self._campo_serial.frame.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        acoes = tk.Frame(linha2, bg=t.COR_BRANCO)
        acoes.grid(row=0, column=1, sticky="e")

        tk.Button(
            acoes,
            text="Atualizar",
            font=t.FONTE_NORMAL,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=18,
            pady=8,
            command=self._atualizar,
        ).pack(side="left", padx=(0, 8))

        self._btn_abrir = tk.Button(
            acoes,
            text="Abrir",
            font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO,
            fg=_COR_BTN_SECUNDARIO_TXT,
            activebackground=t.COR_BRANCO,
            activeforeground=_COR_BTN_SECUNDARIO_TXT,
            disabledforeground=_COR_BTN_SECUNDARIO_TXT,
            highlightbackground=_COR_BTN_SECUNDARIO,
            highlightcolor=_COR_BTN_SECUNDARIO,
            relief="solid",
            bd=1,
            padx=18,
            pady=7,
            state="disabled",
            cursor="arrow",
        )
        self._btn_abrir.pack(side="left")

    def _estilizar_combos(self) -> None:
        self.option_add("*TCombobox*Listbox.font", t.FONTE_NORMAL)
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(
            "Registros.TCombobox",
            font=t.FONTE_NORMAL,
            padding=(4, 6),
            fieldbackground=t.COR_BRANCO,
            background=t.COR_BRANCO,
            foreground=t.COR_AZUL_MARINHO,
            arrowcolor=t.COR_PRIMARIA,
            borderwidth=0,
            relief="flat",
        )
        estilo.map(
            "Registros.TCombobox",
            fieldbackground=[("readonly", t.COR_BRANCO)],
            selectbackground=[("readonly", t.COR_BRANCO)],
            selectforeground=[("readonly", t.COR_AZUL_MARINHO)],
        )

    def _montar_tabela(self, painel: tk.Frame) -> None:
        frame = tk.Frame(painel, bg=t.COR_BRANCO)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._estilizar_tabela()

        self._tabela = ttk.Treeview(
            frame,
            columns=_COLUNAS,
            show="headings",
            selectmode="browse",
            style="Registros.Treeview",
        )

        larguras = {
            "Arquivo": 200,
            "Tipo": 80,
            "Resultado": 100,
            "Data / hora": 160,
            "Pasta": 280,
        }
        for col in _COLUNAS:
            ancora = "w" if col in ("Arquivo", "Pasta") else "center"
            self._tabela.heading(col, text=col, anchor=ancora)
            self._tabela.column(
                col,
                anchor=ancora,
                stretch=True,
                minwidth=60,
                width=larguras.get(col, 100),
            )

        self._tabela.grid(row=0, column=0, sticky="nsew")
        self._tabela.bind("<<TreeviewSelect>>", self._ao_selecionar_linha)

    def _estilizar_tabela(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(
            "Registros.Treeview",
            background=t.COR_BRANCO,
            foreground=t.COR_PRIMARIA,
            fieldbackground=t.COR_BRANCO,
            rowheight=32,
            font=t.FONTE_NORMAL,
            borderwidth=0,
            relief="flat",
        )
        estilo.configure(
            "Registros.Treeview.Heading",
            background=t.COR_BRANCO,
            foreground=_COR_CABECALHO,
            font=t.FONTE_BOLD,
            relief="flat",
            borderwidth=0,
            padding=(8, 10),
        )
        estilo.map(
            "Registros.Treeview",
            background=[("selected", t.COR_MENU_HOVER)],
            foreground=[("selected", t.COR_AZUL_MARINHO)],
        )
        estilo.map(
            "Registros.Treeview.Heading",
            background=[
                ("active", t.COR_BRANCO),
                ("!active", t.COR_BRANCO),
            ],
            foreground=[
                ("active", _COR_CABECALHO),
                ("!active", _COR_CABECALHO),
            ],
        )

    def _montar_rodape(self, painel: tk.Frame) -> None:
        self._label_status = tk.Label(
            painel,
            text=_MSG_VAZIO,
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            anchor="w",
        )
        self._label_status.grid(row=3, column=0, sticky="w", pady=(10, 0))

    def _atualizar(self) -> None:
        for item in self._tabela.get_children():
            self._tabela.delete(item)
        if self._btn_abrir:
            self._btn_abrir.configure(state="disabled", cursor="arrow")
        if self._label_status:
            self._label_status.config(text=_MSG_VAZIO)

        filtro_tipo = self._combo_tipo.combo.get()
        filtro_resultado = self._combo_resultado.combo.get()
        data_ini = self._data_inicial.valor()
        data_fim = self._data_final.valor()
        filtro_serial = self._campo_serial.valor().strip().lower()

        registros = listar_logs(pasta_logs_efetiva())

        total = 0
        for reg in registros:
            tipo = reg["tipo"]
            resultado = reg["resultado"].upper() if reg["resultado"] else "—"
            data_hora = reg["data_hora"]

            if filtro_tipo != "Todos" and tipo != filtro_tipo:
                continue
            if filtro_resultado != "Todos" and resultado != filtro_resultado:
                continue
            if filtro_serial and filtro_serial not in reg["arquivo"].lower():
                continue
            if data_ini or data_fim:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(data_hora, "%d/%m/%Y %H:%M:%S").date()
                    if data_ini and dt < data_ini:
                        continue
                    if data_fim and dt > data_fim:
                        continue
                except ValueError:
                    pass

            self._tabela.insert(
                "",
                "end",
                iid=str(reg["caminho"]),
                values=(reg["arquivo"], tipo, resultado, data_hora, reg["pasta"]),
            )
            total += 1

        if self._label_status:
            if total == 0:
                self._label_status.config(text=_MSG_VAZIO)
            else:
                self._label_status.config(text=f"{total} registro(s) encontrado(s).")

    def _ao_selecionar_linha(self, _event=None) -> None:
        if not self._btn_abrir:
            return
        selecionado = self._tabela.selection()
        if selecionado:
            self._btn_abrir.configure(
                state="normal",
                cursor="hand2",
                fg=t.COR_AZUL_MARINHO,
                activeforeground=t.COR_AZUL_MARINHO,
                command=self._abrir_selecionado,
            )
        else:
            self._btn_abrir.configure(
                state="disabled",
                cursor="arrow",
                fg=_COR_BTN_SECUNDARIO_TXT,
                activeforeground=_COR_BTN_SECUNDARIO_TXT,
            )

    def _abrir_selecionado(self) -> None:
        selecionado = self._tabela.selection()
        if not selecionado:
            return
        caminho = selecionado[0]
        try:
            os.startfile(caminho)
        except Exception:
            pass

    def _fechar(self) -> None:
        self.aplicacao.ao_fechar_registros()
        self.destroy()
