# Juliana Pereira | Delta Sollutions - 2026
import threading
import tkinter as tk
from tkinter import ttk

from domain.models import Recipe, Step
from infrastructure import serial_port
from infrastructure.serial_port import conectar
from services.barcode_service import BarcodeService
from services.execute_service import desligar_placa, executar
from services.log_service import salvar_log
from services.rastreio_service import carregar_config_rastreio, pasta_logs_efetiva
from services.recipe_service import carregar_passos
from ui.Avisos.confirmacao_popup import perguntar as perguntar_popup
from ui.Avisos.mensagem import mostrar as mostrar_mensagem
from ui.Theme import theme as t
from ui.barra_menu import criar_menu_principal
from ui.branding import (
    GEOMETRIA_PADRAO,
    aplicar_icone,
    centralizar_na_tela,
    configurar_app_id,
)


class JanelaPrincipal(tk.Tk):
    """Janela principal 

    Layout (de cima para baixo):
        1. Menu
        2. Linha de estado  — conexão, porta, baud e receita ativa
        3. Tabela           — colunas TESTE | RANGE | VALOR | STATUS
        4. Botão            — Iniciar teste
        5. Log serial       — TX/RX dos comandos
    """

    # Colunas da tabela na ordem em que aparecem
    COLUNAS = ("TESTE", "RANGE", "VALOR", "STATUS")

    def __init__(self, aplicacao):
        super().__init__()
        self.aplicacao = aplicacao

        configurar_app_id()
        self.title("FCTDelta v1.0.0")
        self.geometry(GEOMETRIA_PADRAO)
        self.minsize(640, 400)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self._conectado = False
        self._bolinha_ligada = True
        self._blink_after_id = None
        self._receita_ativa: Recipe | None = None
        self._indice_passo = 0
        self._serial_atual: str = ""
        self._ids_linhas_tabela: list[str] = []
        self._labels_status: list[tk.Label] = []

        self._montar_interface()
        serial_port._on_log = self._exibir_log
        centralizar_na_tela(self)

    # ── Montagem ──────────────────────────────────────────────────────────────

    def _montar_interface(self):
        criar_menu_principal(self, self.aplicacao)

        # Painel raiz: row 0 = estado, row 1 = tabela (cresce), row 2 = botão
        painel = tk.Frame(self, bg=t.COR_BRANCO)
        painel.pack(fill="both", expand=True, padx=16, pady=8)
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(1, weight=1)

        self._montar_linha_estado(painel)
        self._montar_tabela(painel)
        self._montar_botao_iniciar(painel)
        self._montar_log_serial(painel)

    # ── 1. Linha de estado ────────────────────────────────────────────────────

    def _montar_linha_estado(self, painel):
        linha = tk.Frame(painel, bg=t.COR_BRANCO)
        linha.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._canvas_bolinha = tk.Canvas(
            linha, width=14, height=14, bg=t.COR_BRANCO,
            highlightthickness=0, bd=0,
        )
        self._canvas_bolinha.pack(side="left", padx=(0, 6))
        self._bolinha_id = self._canvas_bolinha.create_oval(
            2, 2, 12, 12, fill=t.COR_VERMELHO, outline="",
        )

        self._label_status = tk.Label(
            linha, text="Desconectado", font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_VERMELHO,
        )
        self._label_status.pack(side="left")

        self._label_info = tk.Label(
            linha, text="   ·   —   ·   — baud   ·   —",
            font=t.FONTE_NORMAL, bg=t.COR_BRANCO, fg=t.COR_PRIMARIA,
        )
        self._label_info.pack(side="left")

        self._iniciar_piscar()

    def _cor_bolinha(self) -> str:
        return t.COR_VERDE if self._conectado else t.COR_VERMELHO

    def _cor_bolinha_apagada(self) -> str:
        return t.COR_VERDE_CLARO if self._conectado else t.COR_VERMELHO_CLARO

    def _iniciar_piscar(self) -> None:
        self._piscar_bolinha()

    def _piscar_bolinha(self) -> None:
        if not self.winfo_exists():
            return
        self._bolinha_ligada = not self._bolinha_ligada
        cor = self._cor_bolinha() if self._bolinha_ligada else self._cor_bolinha_apagada()
        self._canvas_bolinha.itemconfig(self._bolinha_id, fill=cor)
        self._blink_after_id = self.after(700, self._piscar_bolinha)

    def _definir_status(self, conectado: bool, porta: str, baud: int, receita: str) -> None:
        self._conectado = conectado
        texto = "Conectado" if conectado else "Desconectado"
        cor = t.COR_VERDE if conectado else t.COR_VERMELHO
        self._label_status.config(text=texto, fg=cor)
        self._label_info.config(
            text=f"   ·   {porta}   ·   {baud} baud   ·   {receita}"
        )
        self._bolinha_ligada = True
        self._canvas_bolinha.itemconfig(self._bolinha_id, fill=cor)

    def _range_coluna(self, passo: Step) -> str:
        if passo.type == "Pop-up":
            return "Pop-up"
        return passo.expectedValue

    def aplicar_configuracao(self, porta: str, baud: int, receita: str) -> None:
        threading.Thread(
            target=self._aplicar_configuracao_bg,
            args=(porta, baud, receita),
            daemon=True,
        ).start()

    def _aplicar_configuracao_bg(self, porta: str, baud: int, receita: str) -> None:
        conectado = conectar(porta, baud)
        passos = carregar_passos(receita)
        receita_obj = Recipe(title=receita, steps=passos) if passos is not None else None
        self.after(
            0,
            lambda: self._finalizar_configuracao(
                conectado, porta, baud, receita, receita_obj,
            ),
        )

    def _finalizar_configuracao(
        self,
        conectado: bool,
        porta: str,
        baud: int,
        receita: str,
        receita_obj: Recipe | None,
    ) -> None:
        self._definir_status(conectado, porta, baud, receita)
        if receita_obj is None:
            self._receita_ativa = None
            return
        self._receita_ativa = receita_obj
        testes = [
            {
                "nome": passo.name,
                "range": self._range_coluna(passo),
            }
            for passo in receita_obj.steps
        ]
        self.carregar_testes(testes)

    # ── 2. Tabela ─────────────────────────────────────────────────────────────

    _SCROLL_W = 14
    _SCROLL_THUMB_MIN = 36
    _COR_THUMB = "#b0b8c4"
    _COR_THUMB_HOVER = "#7a8799"
    _COR_TRILHA = "#e8ebef"
    _COR_THUMB_INATIVO = "#c8ced6"
    _COR_BORDA = "#eef1f5"
    _COR_SELECAO = "#f0f2f5"

    def _montar_tabela(self, painel):
        frame = tk.Frame(painel, bg=t.COR_BRANCO)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._estilizar_treeview()

        self.tabela = ttk.Treeview(
            frame,
            columns=self.COLUNAS,
            show="headings",
            selectmode="browse",
        )

        larguras = {"TESTE": 240, "RANGE": 160, "VALOR": 160, "STATUS": 140}
        for col in self.COLUNAS:
            ancora = "w" if col == "TESTE" else "center"
            self.tabela.heading(col, text=col, anchor=ancora)
            self.tabela.column(col, anchor=ancora, stretch=True, minwidth=60,
                               width=larguras[col])

        self._sv = tk.Canvas(
            frame, width=self._SCROLL_W,
            bg=self._COR_TRILHA, highlightthickness=0, bd=0,
        )
        self._sv_first = 0.0
        self._sv_last = 1.0
        self._sv_drag_y = None
        self._sv_drag_first = 0.0
        self._sv_hover = False

        self.tabela.configure(yscrollcommand=self._sv_on_move)
        self.tabela.bind("<MouseWheel>", self._on_mousewheel)
        self.tabela.bind("<Configure>", lambda _e: self.after_idle(self._posicionar_labels_status))
        self.tabela.bind("<<TreeviewSelect>>", lambda _e: self._posicionar_labels_status())

        self._sv.bind("<ButtonPress-1>", self._sv_click)
        self._sv.bind("<B1-Motion>", self._sv_drag)
        self._sv.bind("<ButtonRelease-1>", self._sv_release)
        self._sv.bind("<Enter>", lambda e: self._sv_set_hover(True))
        self._sv.bind("<Leave>", lambda e: self._sv_set_hover(False))
        self._sv.bind("<Configure>", lambda e: self._sv_redraw())

        self.tabela.grid(row=0, column=0, sticky="nsew")
        self._sv.grid(row=0, column=1, sticky="ns", padx=(4, 0))
        self.after_idle(self._sv_redraw)

    def _criar_label_status(self) -> tk.Label:
        return tk.Label(
            self.tabela,
            text="—",
            font=t.FONTE_NORMAL,
            fg=t.COR_PRIMARIA,
            bg=t.COR_BRANCO,
            anchor="center",
        )

    def _aplicar_estilo_status(self, indice: int, status: str) -> None:
        if indice >= len(self._labels_status):
            return
        label = self._labels_status[indice]
        label.config(text=status)
        if status == t.STATUS_PASS:
            label.config(fg=t.COR_VERDE, font=t.FONTE_STATUS)
        elif status == t.STATUS_FAIL:
            label.config(fg=t.COR_VERMELHO, font=t.FONTE_STATUS)
        else:
            label.config(fg=t.COR_PRIMARIA, font=t.FONTE_NORMAL)

    def _posicionar_labels_status(self) -> None:
        selecionados = set(self.tabela.selection())
        for indice, item in enumerate(self._ids_linhas_tabela):
            if indice >= len(self._labels_status):
                break
            label = self._labels_status[indice]
            bbox = self.tabela.bbox(item, column="STATUS")
            if not bbox:
                label.place_forget()
                continue
            x, y, largura, altura = bbox
            fundo = self._COR_SELECAO if item in selecionados else t.COR_BRANCO
            label.config(bg=fundo)
            label.place(in_=self.tabela, x=x, y=y, width=largura, height=altura)

    def _estilizar_treeview(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure("Treeview",
            background=t.COR_BRANCO,
            foreground=t.COR_PRIMARIA,
            fieldbackground=t.COR_BRANCO,
            rowheight=34,
            font=t.FONTE_NORMAL,
            borderwidth=1,
            relief="flat",
            bordercolor=self._COR_BORDA,
            lightcolor=self._COR_BORDA,
            darkcolor=self._COR_BORDA,
            focuscolor=self._COR_SELECAO,
            selectbackground=self._COR_SELECAO,
            selectforeground=t.COR_PRIMARIA,
        )

        estilo.configure("Treeview.Heading",
            background=t.COR_AZUL_MARINHO,
            foreground=t.COR_BRANCO,
            font=t.FONTE_BOLD,
            relief="flat",
            borderwidth=0,
            padding=(8, 8),
            bordercolor=t.COR_AZUL_MARINHO,
            lightcolor=t.COR_AZUL_MARINHO,
            darkcolor=t.COR_AZUL_MARINHO,
        )

        estilo.map("Treeview.Heading",
            background=[
                ("active", t.COR_AZUL_MARINHO),
                ("!active", t.COR_AZUL_MARINHO),
            ],
            foreground=[
                ("active", t.COR_BRANCO),
                ("!active", t.COR_BRANCO),
            ],
            relief=[("active", "flat"), ("!active", "flat")],
            bordercolor=[
                ("active", t.COR_AZUL_MARINHO),
                ("!active", t.COR_AZUL_MARINHO),
            ],
            lightcolor=[
                ("active", t.COR_AZUL_MARINHO),
                ("!active", t.COR_AZUL_MARINHO),
            ],
            darkcolor=[
                ("active", t.COR_AZUL_MARINHO),
                ("!active", t.COR_AZUL_MARINHO),
            ],
        )

        estilo.map("Treeview",
            background=[("selected", self._COR_SELECAO)],
            foreground=[("selected", t.COR_PRIMARIA)],
            fieldbackground=[("selected", self._COR_SELECAO)],
            bordercolor=[("selected", self._COR_SELECAO)],
            lightcolor=[("selected", self._COR_SELECAO)],
            darkcolor=[("selected", self._COR_SELECAO)],
            relief=[("selected", "flat")],
        )

        estilo.layout("Treeview", [
            ("Treeview.field", {"sticky": "nswe", "border": "1", "children": [
                ("Treeview.padding", {"sticky": "nswe", "children": [
                    ("Treeview.treearea", {"sticky": "nswe"}),
                ]}),
            ]}),
        ])
        estilo.layout("Treeview.Heading", [
            ("Treeheading.cell", {"sticky": "nswe"}),
            ("Treeheading.padding", {"sticky": "nswe", "children": [
                ("Treeheading.image", {"side": "right", "sticky": ""}),
                ("Treeheading.text", {"sticky": "we"}),
            ]}),
        ])

    def carregar_testes(self, testes: list[dict]) -> None:
        """Preenche a tabela com uma lista de testes.

        Cada teste é um dict com as chaves 'nome' e 'range'.
        VALOR e STATUS começam vazios, prontos para receber dados do teste.
        """
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        for label in self._labels_status:
            label.destroy()
        self._labels_status.clear()

        self._ids_linhas_tabela = []
        for teste in testes:
            item_id = self.tabela.insert("", "end", values=(
                teste.get("nome", "—"),
                teste.get("range", "—"),
                "—",
                "—",
            ))
            self._ids_linhas_tabela.append(item_id)
            self._labels_status.append(self._criar_label_status())
        self.after_idle(self._posicionar_labels_status)

    # ── Scrollbar customizada ─────────────────────────────────────────────────

    def _sv_on_move(self, first: str, last: str) -> None:
        self._sv_first = float(first)
        self._sv_last = float(last)
        self._sv_redraw()
        self.after_idle(self._posicionar_labels_status)

    def _sv_redraw(self) -> None:
        c = self._sv
        c.delete("all")
        h = c.winfo_height()
        if h < 4:
            return

        margem = 3
        x1, y1 = 2, margem
        x2, y2 = self._SCROLL_W - 2, h - margem

        self._sv_draw_pill(c, x1, y1, x2, y2, self._COR_TRILHA)

        if (self._sv_last - self._sv_first) >= 1.0:
            self._sv_draw_pill(c, x1, y1, x2, y2, self._COR_THUMB_INATIVO)
            return

        thumb_top = max(y1, int(h * self._sv_first) + margem)
        thumb_bot = min(y2, int(h * self._sv_last) - margem)
        thumb_bot = max(thumb_bot, thumb_top + self._SCROLL_THUMB_MIN)
        cor = self._COR_THUMB_HOVER if self._sv_hover else self._COR_THUMB
        self._sv_draw_pill(c, x1, thumb_top, x2, thumb_bot, cor)

    def _sv_draw_pill(self, canvas, x1, y1, x2, y2, color):
        r = (x2 - x1) // 2
        if (y2 - y1) <= 2 * r:
            canvas.create_oval(x1, y1, x2, y1 + 2 * r, fill=color, outline="")
            return
        canvas.create_oval(x1, y1, x2, y1 + 2 * r, fill=color, outline="")
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline="")
        canvas.create_oval(x1, y2 - 2 * r, x2, y2, fill=color, outline="")

    def _sv_set_hover(self, state: bool) -> None:
        self._sv_hover = state
        self._sv_redraw()

    def _sv_thumb_bounds(self):
        h = self._sv.winfo_height()
        top = max(0, int(h * self._sv_first)) + 3
        bot = min(h, max(int(h * self._sv_last), int(h * self._sv_first) + self._SCROLL_THUMB_MIN)) - 3
        return top, bot

    def _sv_click(self, event) -> None:
        top, bot = self._sv_thumb_bounds()
        if top <= event.y <= bot:
            self._sv_drag_y = event.y
            self._sv_drag_first = self._sv_first
        elif event.y < top:
            self.tabela.yview_scroll(-1, "pages")
        else:
            self.tabela.yview_scroll(1, "pages")

    def _sv_drag(self, event) -> None:
        if self._sv_drag_y is None:
            return
        h = self._sv.winfo_height()
        if h == 0:
            return
        delta = (event.y - self._sv_drag_y) / h
        span = self._sv_last - self._sv_first
        new_first = max(0.0, min(1.0 - span, self._sv_drag_first + delta))
        self.tabela.yview_moveto(new_first)

    def _sv_release(self, _event) -> None:
        self._sv_drag_y = None

    def _on_mousewheel(self, event) -> None:
        self.tabela.yview_scroll(-1 * (event.delta // 120), "units")

    # ── 3. Botão Iniciar teste ────────────────────────────────────────────────

    def _montar_botao_iniciar(self, painel):
        self.botao_iniciar = tk.Button(
            painel,
            text="Ler Barcode",
            font=t.FONTE_BOLD,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=16,
            pady=20,
        )
        self.botao_iniciar.configure(command=self._iniciar_teste)
        self.botao_iniciar.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _montar_log_serial(self, painel):
        linha = tk.Frame(painel, bg=t.COR_BRANCO)
        linha.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        self._var_enviado = tk.StringVar(value="")
        self._var_recebido = tk.StringVar(value="")

        tk.Label(
            linha, text="enviado:", font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_PRIMARIA,
        ).pack(side="left")
        tk.Label(
            linha, textvariable=self._var_enviado, font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO,
        ).pack(side="left", padx=(4, 16))

        tk.Label(
            linha, text="recebido:", font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_PRIMARIA,
        ).pack(side="left")
        tk.Label(
            linha, textvariable=self._var_recebido, font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO,
        ).pack(side="left", padx=(4, 0))

        self._label_alerta = tk.Label(
            linha, text="", font=t.FONTE_BOLD,
            bg=t.COR_BRANCO, fg=t.COR_VERMELHO,
        )
        self._label_alerta.pack(side="right")

    def _exibir_log(self, enviado: str, recebido: str, alerta: str = "") -> None:
        if not self.winfo_exists():
            return
        self.after(0, lambda: self._atualizar_log(enviado, recebido, alerta))

    def _atualizar_log(self, enviado: str, recebido: str, alerta: str = "") -> None:
        if enviado:
            atual = self._var_enviado.get()
            self._var_enviado.set(f"{atual}, {enviado}" if atual else enviado)
        if recebido:
            atual = self._var_recebido.get()
            self._var_recebido.set(f"{atual}, {recebido}" if atual else recebido)
        if alerta:
            self._label_alerta.config(text=alerta)

    def _atualizar_linha_teste(self, indice: int, valor: str, status: str) -> None:
        if indice >= len(self._ids_linhas_tabela):
            return
        item = self._ids_linhas_tabela[indice]
        valores = list(self.tabela.item(item, "values"))
        valores[t.COL_IDX_VALOR] = valor
        valores[t.COL_IDX_STATUS] = status
        self.tabela.item(item, values=valores)
        self._aplicar_estilo_status(indice, status)
        self.after_idle(self._posicionar_labels_status)

    def _status_linha(self, indice: int) -> str:
        if indice >= len(self._ids_linhas_tabela):
            return ""
        valores = self.tabela.item(self._ids_linhas_tabela[indice], "values")
        return valores[t.COL_IDX_STATUS]

    def _tem_falha_na_tabela(self) -> bool:
        return any(
            self._status_linha(i) == t.STATUS_FAIL
            for i in range(len(self._ids_linhas_tabela))
        )

    def _tem_falha_apos_barcode(self) -> bool:
        return any(
            self._status_linha(i) == t.STATUS_FAIL
            for i in range(1, len(self._ids_linhas_tabela))
        )

    def _barcode_aprovado(self) -> bool:
        return self._status_linha(0) == t.STATUS_PASS

    def _reiniciar_resultados_tabela(self) -> None:
        for indice, item in enumerate(self._ids_linhas_tabela):
            valores = list(self.tabela.item(item, "values"))
            valores[t.COL_IDX_VALOR] = "—"
            valores[t.COL_IDX_STATUS] = "—"
            self.tabela.item(item, values=valores)
            self._aplicar_estilo_status(indice, "—")
        self.after_idle(self._posicionar_labels_status)

    def _iniciar_teste(self) -> None:
        if not self._receita_ativa or not self._receita_ativa.steps:
            mostrar_mensagem(
                self, "Teste", "Nenhuma receita ativa para executar.", tipo="aviso",
            )
            return

        self._parar_aguardar_bimanual()
        self._indice_passo = 0
        self._serial_atual = ""
        self._var_enviado.set("")
        self._var_recebido.set("")
        self._label_alerta.config(text="")
        self._reiniciar_resultados_tabela()
        self._executar_barcode()

    def _executar_barcode(self) -> None:
        if not self._receita_ativa or not self._receita_ativa.steps:
            return
        self.aplicacao.abrir_barcode(on_ler=self._ao_ler_barcode)

    def _coletar_resultados(self) -> list[dict]:
        resultados = []
        for item in self._ids_linhas_tabela:
            v = self.tabela.item(item, "values")
            resultados.append({
                "nome": v[t.COL_IDX_TESTE],
                "range": v[t.COL_IDX_RANGE],
                "valor": v[t.COL_IDX_VALOR],
                "status": v[t.COL_IDX_STATUS],
            })
        return resultados

    def _salvar_log(self) -> None:
        if not self._receita_ativa:
            return
        try:
            config = carregar_config_rastreio()
            salvar_log(
                receita=self._receita_ativa.title,
                serial=self._serial_atual,
                resultados=self._coletar_resultados(),
                pasta=pasta_logs_efetiva(),
                formato_txt=config["formato_txt"],
                formato_excel=config["formato_excel"],
            )
        except Exception:
            pass

    def _executar_lote_serial(self) -> None:
        self._executar_passo()

    def _executar_passo(self) -> None:
        if not self._receita_ativa or self._indice_passo >= len(self._receita_ativa.steps):
            self._finalizar_lote()
            return

        passo = self._receita_ativa.steps[self._indice_passo]
        cmd = passo.command.strip()

        if cmd == "4":
            threading.Thread(
                target=self._passo_comando_bg,
                args=(passo,),
                daemon=True,
            ).start()
            return

        if passo.type == "Pop-up":
            self._executar_passo_popup(passo)
            return

        if passo.type == "Serial":
            threading.Thread(
                target=self._passo_comando_bg,
                args=(passo,),
                daemon=True,
            ).start()
            return

        self._indice_passo += 1
        self.after(0, self._executar_passo)

    def _executar_passo_popup(self, passo: Step) -> None:
        valor = (passo.expectedValue or "").strip()
        aprovado = perguntar_popup(self, "", valor)
        status = t.STATUS_PASS if aprovado else t.STATUS_FAIL
        self._atualizar_linha_teste(
            self._indice_passo,
            valor or ("Sim" if aprovado else "Não"),
            status,
        )
        self._indice_passo += 1
        if not aprovado:
            self._finalizar_lote()
            return
        self.after(0, self._executar_passo)

    def _passo_comando_bg(self, passo: Step) -> None:
        resultado = executar(passo)
        self.after(0, lambda: self._passo_comando_concluido(passo, resultado))

    def _passo_comando_concluido(self, passo: Step, resultado: dict) -> None:
        if passo.command.strip() == "4":
            if resultado["resultado"] != "Pass":
                self._atualizar_linha_teste(
                    self._indice_passo,
                    resultado["resposta"] or "—",
                    t.STATUS_FAIL,
                )
                self._finalizar_lote()
                return

            valor = (passo.expectedValue or "").strip()
            aprovado = perguntar_popup(self, "", valor)
            status = t.STATUS_PASS if aprovado else t.STATUS_FAIL
            self._atualizar_linha_teste(
                self._indice_passo,
                valor or ("Sim" if aprovado else "Não"),
                status,
            )
            self._indice_passo += 1
            if not aprovado:
                self._finalizar_lote()
                return
            self.after(0, self._executar_passo)
            return

        status = t.STATUS_PASS if resultado["resultado"] == "Pass" else t.STATUS_FAIL
        self._atualizar_linha_teste(
            self._indice_passo,
            resultado["resposta"] or "—",
            status,
        )
        if status == t.STATUS_FAIL:
            self._finalizar_lote()
            return
        self._indice_passo += 1
        self.after(0, self._executar_passo)

    # ── Bimanual ──────────────────────────────────────────────────────────────

    def _aguardar_bimanual(self) -> None:
        """Ativa o listener serial e aguarda o sinal 'start' do bimanual."""
        serial_port._on_entrada = self._ao_receber_entrada_serial
        self._label_alerta.config(text="Aguardando bimanual...")

    def _parar_aguardar_bimanual(self) -> None:
        serial_port._on_entrada = None

    def _ao_receber_entrada_serial(self, linha: str) -> None:
        """Chamado pelo thread de leitura serial — agenda no thread principal."""
        if linha.strip().lower() == "start":
            self.after(0, self._ao_receber_start)

    def _ao_receber_start(self) -> None:
        """Recebeu 'start' do bimanual: inicia os testes."""
        self._parar_aguardar_bimanual()
        self.botao_iniciar.config(state="disabled")
        self._atualizar_log("", "start", alerta="Iniciando testes")
        self._executar_lote_serial()

    # ── Finalização ───────────────────────────────────────────────────────────

    def _finalizar_lote(self) -> None:
        self._parar_aguardar_bimanual()
        self.botao_iniciar.config(state="normal")
        self._salvar_log()
        if self._tem_falha_apos_barcode():
            threading.Thread(target=self._desligar_placa_bg, daemon=True).start()

    def _desligar_placa_bg(self) -> None:
        desligar_placa()

    def _ao_ler_barcode(self, codigo: str) -> None:
        if not self._receita_ativa or self._indice_passo != 0:
            return
        passo = self._receita_ativa.steps[0]
        status = BarcodeService(codigo).CompararBarcode(passo.expectedValue)
        self._atualizar_linha_teste(0, codigo, status)
        if status == t.STATUS_PASS:
            self._serial_atual = codigo
            self._indice_passo = 1
            self._aguardar_bimanual()
            return
        mostrar_mensagem(
            self,
            "Código incorreto",
            f"O código lido não corresponde à receita ativa.\n\n"
            f"Código esperado: {passo.expectedValue}",
            tipo="aviso",
        )