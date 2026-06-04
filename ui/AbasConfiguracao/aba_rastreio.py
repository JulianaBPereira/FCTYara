import tkinter as tk
from tkinter import filedialog

from services.logs_path_service import pasta_logs_padrao, sugestoes_pasta_logs
from services.rastreio_service import carregar_config_rastreio, salvar_config_rastreio
from ui.Avisos.mensagem import mostrar as mostrar_mensagem
from ui.Theme import theme as t

_MAX_SUGESTOES_VISIVEIS = 6
_TECLAS_IGNORAR_FILTRO = frozenset({
    "Return", "Tab", "Escape", "Up", "Down",
    "Shift_L", "Shift_R", "Control_L", "Control_R",
})


class _EntradaAutocomplete:
    """Campo de texto livre com lista de sugestões abaixo (não é combobox)."""

    def __init__(self, parent: tk.Frame, textvariable: tk.StringVar, sugestoes: list[str]):
        self._sugestoes = list(sugestoes)

        self.entry = tk.Entry(
            parent,
            textvariable=textvariable,
            font=t.FONTE_NORMAL,
            relief="flat",
            bd=0,
            highlightthickness=0,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        )
        self.entry.pack(fill="x", padx=10, pady=8)

        self._painel = tk.Frame(parent, bg=t.COR_BRANCO)
        self._lista = tk.Listbox(
            self._painel,
            font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            selectbackground=t.COR_MENU_HOVER,
            selectforeground=t.COR_AZUL_MARINHO,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#eef1f5",
            activestyle="none",
            height=_MAX_SUGESTOES_VISIVEIS,
        )
        self._lista.pack(fill="x")

        self.entry.bind("<KeyRelease>", self._ao_digitar)
        self.entry.bind("<FocusOut>", self._ao_perder_foco)
        self.entry.bind("<Escape>", lambda _: self._esconder_lista())
        self._lista.bind("<ButtonRelease-1>", self._ao_clicar_sugestao)
        self._lista.bind("<Return>", self._ao_clicar_sugestao)

    def adicionar_sugestao(self, caminho: str) -> None:
        if caminho and caminho not in self._sugestoes:
            self._sugestoes.insert(0, caminho)

    def _filtrar(self, texto: str) -> list[str]:
        if not texto.strip():
            return self._sugestoes[:]
        chave = texto.lower()
        filtradas = [s for s in self._sugestoes if chave in s.lower()]
        filtradas.sort(key=lambda s: (not s.lower().startswith(chave), s.lower()))
        return filtradas

    def _ao_digitar(self, event):
        if event.keysym in _TECLAS_IGNORAR_FILTRO:
            if event.keysym == "Escape":
                self._esconder_lista()
            elif event.keysym == "Down" and self._painel.winfo_ismapped():
                self._lista.focus_set()
                if self._lista.size():
                    self._lista.selection_set(0)
            return

        filtradas = self._filtrar(self.entry.get())
        if not filtradas:
            self._esconder_lista()
            return

        self._lista.delete(0, "end")
        for item in filtradas[:_MAX_SUGESTOES_VISIVEIS]:
            self._lista.insert("end", item)

        if not self._painel.winfo_ismapped():
            self._painel.pack(fill="x", padx=10, pady=(0, 8))

    def _ao_clicar_sugestao(self, _event=None):
        selecao = self._lista.curselection()
        if not selecao:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, self._lista.get(selecao[0]))
        self._esconder_lista()
        self.entry.focus_set()

    def _ao_perder_foco(self, _event=None):
        self.entry.after(120, self._fechar_se_foco_saiu)

    def _fechar_se_foco_saiu(self):
        foco = self.entry.winfo_toplevel().focus_get()
        if foco not in (self.entry, self._lista):
            self._esconder_lista()

    def _esconder_lista(self):
        if self._painel.winfo_ismapped():
            self._painel.pack_forget()


class AbaRastreio:
    def __init__(self, janela, parent: tk.Frame, *, ao_fechar_janela=None):
        self.janela = janela
        self._ao_fechar_janela = ao_fechar_janela
        self._todas_sugestoes = sugestoes_pasta_logs()
        self.campo_pasta: _EntradaAutocomplete | None = None
        self.btn_procurar: tk.Button | None = None

        config = carregar_config_rastreio()
        pasta_inicial = config["pasta"] if config["pasta"] else str(pasta_logs_padrao())
        self.pasta_logs = tk.StringVar(value=pasta_inicial)
        self.var_txt = tk.BooleanVar(value=config["formato_txt"])
        self.var_excel = tk.BooleanVar(value=config["formato_excel"])

        self._montar(parent)

    def _montar(self, parent: tk.Frame):
        self._painel_aba = parent
        form = tk.Frame(parent, bg=t.COR_BRANCO)
        form.pack(fill="x", padx=40, pady=16)
        form.grid_columnconfigure(0, weight=1)

        tk.Label(
            form,
            text="Pasta dos logs (registros)",
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        linha = tk.Frame(form, bg=t.COR_BRANCO)
        linha.grid(row=1, column=0, columnspan=2, sticky="ew")
        linha.grid_columnconfigure(0, weight=1)

        borda = tk.Frame(
            linha,
            bg=t.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=t.COR_PRIMARIA,
        )
        borda.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.campo_pasta = _EntradaAutocomplete(
            borda,
            self.pasta_logs,
            self._todas_sugestoes,
        )

        self.btn_procurar = tk.Button(
            linha,
            text="Procurar…",
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
            command=self._procurar_pasta,
        )
        self.btn_procurar.grid(row=0, column=1, sticky="e")

        # ── Formato de saída ──────────────────────────────────────────────────
        tk.Label(
            form,
            text="Formato do log",
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(20, 8))

        checks = tk.Frame(form, bg=t.COR_BRANCO)
        checks.grid(row=3, column=0, columnspan=2, sticky="w")

        tk.Checkbutton(
            checks,
            text="TXT",
            variable=self.var_txt,
            font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO,
            fg=t.COR_PRIMARIA,
            activebackground=t.COR_BRANCO,
            selectcolor=t.COR_BRANCO,
            cursor="hand2",
        ).pack(side="left", padx=(0, 24))

        tk.Checkbutton(
            checks,
            text="Excel (.xlsx)",
            variable=self.var_excel,
            font=t.FONTE_NORMAL,
            bg=t.COR_BRANCO,
            fg=t.COR_PRIMARIA,
            activebackground=t.COR_BRANCO,
            selectcolor=t.COR_BRANCO,
            cursor="hand2",
        ).pack(side="left")

        # ── Botões Cancelar / Salvar ──────────────────────────────────────────
        acoes = tk.Frame(form, bg=t.COR_BRANCO)
        acoes.grid(row=4, column=0, columnspan=2, sticky="e", pady=(20, 0))

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
            command=self._cancelar,
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
            command=self._salvar,
        ).pack(side="left", padx=(12, 0))

    def _cancelar(self) -> None:
        if self._ao_fechar_janela:
            self._ao_fechar_janela()

    def _salvar(self) -> None:
        if not self.var_txt.get() and not self.var_excel.get():
            mostrar_mensagem(
                self._painel_aba,
                "",
                "Selecione ao menos um formato de log.",
                tipo="aviso",
            )
            return
        salvar_config_rastreio(
            pasta=self.pasta_logs.get().strip(),
            formato_txt=self.var_txt.get(),
            formato_excel=self.var_excel.get(),
        )
        mostrar_mensagem(self._painel_aba, "", "Configuração de rastreio salva.")

    def _procurar_pasta(self):
        inicial = self.pasta_logs.get().strip() or str(pasta_logs_padrao().parent)
        escolhida = filedialog.askdirectory(
            parent=self.janela,
            title="Selecionar pasta dos logs",
            initialdir=inicial,
        )
        if not escolhida:
            return

        self.pasta_logs.set(escolhida)
        if self.campo_pasta:
            self.campo_pasta.adicionar_sugestao(escolhida)
            self.campo_pasta._esconder_lista()
