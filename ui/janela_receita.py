# Juliana Pereira | Delta Sollutions - 2026
import tkinter as tk
from tkinter import ttk

from domain.models import Step
from services.recipe_service import ReceitaService
from ui.branding import GEOMETRIA_PADRAO, aplicar_icone, centralizar_janela
from ui.Theme import theme as t
from ui.Avisos.mensagem import mostrar as mostrar_mensagem


class JanelaReceita(tk.Toplevel):
    """Janela para criar receitas de teste."""

    def __init__(self, aplicacao, nome_editar=None):
        super().__init__(aplicacao.raiz)
        self.aplicacao = aplicacao
        self.nome_editar = nome_editar
        self.linhas = []
        self.linha_selecionada = None
        self._entrada_ativa: tk.Entry | None = None

        self.title("Criar Receita")
        self.geometry(GEOMETRIA_PADRAO)
        self.resizable(True, True)
        self.minsize(800, 400)
        self.configure(bg=t.COR_BRANCO)
        aplicar_icone(self)

        self.transient(aplicacao.raiz)
        self._montar_interface()
        centralizar_janela(self, aplicacao.raiz)
        self.protocol("WM_DELETE_WINDOW", self._fechar_janela)

        if nome_editar:
            self.campo_titulo.insert(0, nome_editar)
            self.campo_titulo.select_range(0, "end")

        self.after(100, self.focar_entrada_inicial)

    # ── Montagem ──────────────────────────────────────────────────────────────

    def _montar_interface(self):
        # Rodapé fixo (Salvar / Cancelar) fora do scroll para sempre ficar visível
        rodape = tk.Frame(self, bg=t.COR_BRANCO)
        rodape.pack(fill="x", side="bottom", padx=20, pady=(8, 12))
        self.btn_cancelar(rodape)
        self.btn_salvar(rodape)

        tk.Frame(self, bg="#eef1f5", height=1).pack(fill="x", side="bottom")

        # Canvas principal com scroll vertical — contém TODO o restante
        outer = tk.Frame(self, bg=t.COR_BRANCO)
        outer.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(outer, orient="vertical")
        sb.pack(side="right", fill="y")

        self._canvas_principal = tk.Canvas(
            outer,
            bg=t.COR_BRANCO,
            highlightthickness=0,
            yscrollcommand=sb.set,
        )
        self._canvas_principal.pack(side="left", fill="both", expand=True)
        sb.configure(command=self._canvas_principal.yview)

        p = tk.Frame(self._canvas_principal, bg=t.COR_BRANCO)
        self._id_janela_canvas = self._canvas_principal.create_window(
            (0, 0), window=p, anchor="nw"
        )

        # Espaçador fixo no fim do conteúdo — garante scroll mesmo com poucos itens
        # (equivale à altura aproximada do teclado virtual no Raspberry Pi)
        self._espacador_teclado = tk.Frame(p, bg=t.COR_BRANCO, height=300)
        self._espacador_teclado.pack(fill="x", side="bottom")

        p.bind(
            "<Configure>",
            lambda e: self._canvas_principal.configure(
                scrollregion=self._canvas_principal.bbox("all")
            ),
        )
        self._canvas_principal.bind(
            "<Configure>",
            lambda e: self._canvas_principal.itemconfig(
                self._id_janela_canvas, width=e.width
            ),
        )

        # Scroll com roda do mouse
        self._canvas_principal.bind("<MouseWheel>", self._ao_rolar_mouse)
        self._canvas_principal.bind("<Button-4>", self._ao_rolar_mouse)
        self._canvas_principal.bind("<Button-5>", self._ao_rolar_mouse)

        self._painel = p
        self._registrar_captura_teclado(self, p, self._canvas_principal)

        # Conteúdo interno
        p.configure(padx=20, pady=16)
        self.nome_receita(p)

        barra = tk.Frame(p, bg=t.COR_BRANCO)
        barra.pack(fill="x", pady=(0, 6))
        self.btn_adicionar(barra)
        self.btn_remover(barra)

        self.tabela_testes(p)

    def _ao_rolar_mouse(self, event):
        if event.num == 4:
            self._canvas_principal.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas_principal.yview_scroll(1, "units")
        else:
            self._canvas_principal.yview_scroll(int(-event.delta / 120), "units")

    # ── Widgets ───────────────────────────────────────────────────────────────

    def nome_receita(self, parent):
        tk.Label(
            parent,
            text="Título da receita",
            font=t.FONTE_BOLD,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
        ).pack(anchor="w", pady=(0, 4))

        borda = tk.Frame(
            parent,
            bg=t.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=t.COR_PRIMARIA,
        )
        borda.pack(fill="x", pady=(0, 8))

        self.campo_titulo = tk.Entry(
            borda,
            font=t.FONTE_NORMAL,
            relief="flat",
            bd=0,
            highlightthickness=0,
            exportselection=False,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            insertbackground=t.COR_AZUL_MARINHO,
        )
        self.campo_titulo.pack(fill="x", padx=10, pady=8)
        self._registrar_captura_teclado(borda)
        self._habilitar_toque_entrada(self.campo_titulo, borda)

    def focar_entrada_inicial(self) -> None:
        self.lift()
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self._focar_entrada(self.campo_titulo)

    def _focar_entrada(self, entry: tk.Entry) -> None:
        self._entrada_ativa = entry
        entry.focus_set()
        try:
            entry.icursor(tk.END)
        except tk.TclError:
            pass

    def _rolar_para_entry(self, entry: tk.Entry) -> None:
        """Rola o canvas para que o campo fique visível acima do teclado virtual."""
        self.update_idletasks()
        try:
            # Posição Y do widget em relação ao frame interno (_painel)
            y_abs = entry.winfo_rooty()
            y_painel = self._painel.winfo_rooty()
            y_relativo = y_abs - y_painel

            altura_canvas = self._canvas_principal.winfo_height()
            altura_conteudo = self._painel.winfo_reqheight()

            if altura_conteudo <= altura_canvas:
                return

            # Deixa o campo com uma margem de 80px do topo
            alvo = max(0, y_relativo - 80)
            fracao = alvo / altura_conteudo
            self._canvas_principal.yview_moveto(fracao)
        except tk.TclError:
            pass

    def _habilitar_toque_entrada(self, entry: tk.Entry, *containers: tk.Widget) -> None:
        def focar(_event=None):
            def _fazer():
                self._focar_entrada(entry)
                self._rolar_para_entry(entry)
            entry.after(80, _fazer)

        entry.bind(
            "<FocusIn>",
            lambda _e, campo=entry: setattr(self, "_entrada_ativa", campo),
            add="+",
        )
        for widget in (entry, *containers):
            widget.bind("<ButtonRelease-1>", focar, add="+")

    def _encaminhar_tecla(self, event: tk.Event):
        """No Raspberry o teclado virtual às vezes envia teclas para a janela, não para o Entry."""
        entry = self._entrada_ativa
        if entry is None or not entry.winfo_exists():
            return
        if str(entry.cget("state")) == "disabled":
            return
        if event.widget is entry:
            return

        keysym = event.keysym
        if keysym == "BackSpace":
            try:
                pos = entry.index(tk.INSERT)
                if pos > 0:
                    entry.delete(pos - 1)
            except tk.TclError:
                pass
            return "break"
        if keysym == "Delete":
            try:
                pos = entry.index(tk.INSERT)
                if pos < len(entry.get()):
                    entry.delete(pos)
            except tk.TclError:
                pass
            return "break"

        if event.char and event.char.isprintable():
            entry.insert(tk.INSERT, event.char)
            return "break"

    def btn_adicionar(self, parent):
        tk.Button(
            parent, text="+ Adicionar linha",
            font=t.FONTE_BOLD,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0, padx=14,
            pady=6,
            command=self._adicionar_linha,
        ).pack(side="left", padx=(0, 8))

    def btn_remover(self, parent):
        tk.Button(
            parent,
            text="− Remover linha",
            font=t.FONTE_BOLD,
            bg=t.COR_AZUL_MARINHO,
            fg="white",
            activebackground=t.COR_AZUL_MARINHO_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=14,
            pady=6,
            command=self._remover_linha_selecionada,
        ).pack(side="left")

    def btn_salvar(self, parent):
        tk.Button(
            parent,
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
            command=self._salvar_receita,
        ).pack(side="right")

    def btn_cancelar(self, parent):
        tk.Button(
            parent,
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
            command=self._fechar_janela,
        ).pack(side="right", padx=(6, 0))

    def tabela_testes(self, parent):
        container = tk.Frame(parent, bg=t.COR_BRANCO)
        container.pack(fill="both", expand=True, pady=(0, 8))

        # Cabeçalho
        cab = tk.Frame(container, bg=t.COR_BRANCO)
        cab.pack(fill="x")
        for texto in ("NOME DO TESTE", "TIPO", "COMANDO", "VALOR ESPERADO"):
            tk.Label(
                cab,
                text=texto,
                font=t.FONTE_BOLD,
                bg=t.COR_BRANCO,
                fg=t.COR_PRIMARIA,
            ).pack(side="left", expand=True, padx=4, pady=8)

        tk.Frame(container, bg=t.COR_PRIMARIA, height=1).pack(fill="x", pady=(0, 8))

        # Linhas diretamente no frame (sem Canvas interno — o scroll principal cobre tudo)
        self.container_linhas = tk.Frame(container, bg=t.COR_BRANCO)
        self.container_linhas.pack(fill="both", expand=True)

        self._registrar_captura_teclado(self.container_linhas)

    def _registrar_captura_teclado(self, *widgets: tk.Widget) -> None:
        for widget in widgets:
            widget.bind("<KeyPress>", self._encaminhar_tecla, add="+")

    def combo_box(self, parent, valor="", on_focus=None, linha_ref=None):
        estilo = ttk.Style()
        estilo.configure("Flat.TCombobox",
            fieldbackground=t.COR_BRANCO,
            background=t.COR_BRANCO,
            foreground=t.COR_AZUL_MARINHO,
            arrowcolor=t.COR_AZUL_MARINHO,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padding=0,
        )
        estilo.map("Flat.TCombobox",
            fieldbackground=[("readonly", t.COR_BRANCO)],
            selectbackground=[("readonly", t.COR_BRANCO)],
            selectforeground=[("readonly", t.COR_AZUL_MARINHO)],
            bordercolor=[("readonly", t.COR_BRANCO)],
        )
        estilo.layout("Flat.TCombobox", [
            ("Combobox.field", {"sticky": "nswe", "children": [
                ("Combobox.downarrow", {"side": "right", "sticky": "ns"}),
                ("Combobox.padding", {"sticky": "nswe", "children": [
                    ("Combobox.textarea", {"sticky": "nswe"})
                ]}),
            ]}),
        ])

        frame = tk.Frame(parent, bg=t.COR_BRANCO)
        cb = ttk.Combobox(frame, values=t.TIPOS_TESTE, state="readonly",
                          justify="center", style="Flat.TCombobox", width=12,
                          font=t.FONTE_NORMAL)
        cb.set(valor)
        # Itens da lista suspensa grandes para fácil toque no Raspberry Pi
        cb.option_add("*TCombobox*Listbox.font", (t.FONTE_NORMAL[0], 20))
        cb.option_add("*TCombobox*Listbox.selectBackground", t.COR_AZUL_MARINHO)
        cb.option_add("*TCombobox*Listbox.selectForeground", t.COR_BRANCO)
        cb.pack(anchor="center", ipady=8)
        cb.bind("<FocusIn>", lambda e: (on_focus and on_focus(), linha_ref and linha_ref.configure(bg=t.COR_AZUL_MARINHO)))
        cb.bind("<FocusOut>", lambda e: linha_ref and linha_ref.configure(bg=t.COR_CINZA_CLARO))
        return frame, cb

    def _campo_texto(self, parent, valor="", on_focus=None, linha_ref=None):
        frame = tk.Frame(parent, bg=t.COR_BRANCO)
        entry = tk.Entry(
            frame, font=t.FONTE_NORMAL, relief="flat", bd=0,
            highlightthickness=0,
            exportselection=False,
            bg=t.COR_BRANCO, fg=t.COR_AZUL_MARINHO, insertbackground=t.COR_AZUL_MARINHO,
            justify="center",
        )
        entry.pack(fill="x", ipady=8)
        if valor:
            entry.insert(0, valor)
        entry.bind("<FocusIn>", lambda e: (on_focus and on_focus(), linha_ref and linha_ref.configure(bg=t.COR_AZUL_MARINHO)))
        entry.bind("<FocusOut>", lambda e: linha_ref and linha_ref.configure(bg=t.COR_CINZA_CLARO))
        self._habilitar_toque_entrada(entry, frame)
        return frame, entry

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _atualizar_campo_comando(self, combo_tipo, entry_comando):
        if combo_tipo.get().strip() in ("Serial", "Pop-up"):
            entry_comando.config(state="normal")
            return
        entry_comando.config(state="normal")
        entry_comando.delete(0, "end")
        entry_comando.config(state="disabled")

    def _adicionar_linha(
        self,
        nome="Passo",
        tipo="Serial",
        comando_val="",
        ValorEsperado_val="",
    ):
        dados = {}

        linha_frame = tk.Frame(self.container_linhas, bg=t.COR_BRANCO)
        linha_frame.pack(fill="x", pady=(0, 4))

        conteudo = tk.Frame(linha_frame, bg=t.COR_BRANCO)
        conteudo.pack(fill="x")

        selecionar = lambda: self._selecionar_linha(dados)

        linha_ativa = tk.Frame(linha_frame, bg=t.COR_CINZA_CLARO, height=1)
        linha_ativa.pack(fill="x", pady=(4, 0))

        frame_nome, entry_nome = self._campo_texto(
            conteudo, nome, on_focus=selecionar, linha_ref=linha_ativa,
        )
        frame_nome.pack(side="left", expand=True, fill="x", padx=4)

        frame_tipo, combo_tipo = self.combo_box(
            conteudo, tipo, on_focus=selecionar, linha_ref=linha_ativa,
        )
        frame_tipo.pack(side="left", expand=True, fill="x", padx=4)

        frame_comando, entry_comando = self._campo_texto(
            conteudo, comando_val, on_focus=selecionar, linha_ref=linha_ativa,
        )
        frame_comando.pack(side="left", expand=True, fill="x", padx=4)

        frame_valor, entry_valor = self._campo_texto(
            conteudo, ValorEsperado_val, on_focus=selecionar, linha_ref=linha_ativa,
        )
        frame_valor.pack(side="left", expand=True, fill="x", padx=4)

        combo_tipo.bind(
            "<<ComboboxSelected>>",
            lambda e: self._atualizar_campo_comando(combo_tipo, entry_comando),
        )
        self._atualizar_campo_comando(combo_tipo, entry_comando)

        dados.update({
            "frame": linha_frame,
            "entry_nome": entry_nome,
            "combo_tipo": combo_tipo,
            "entry_comando": entry_comando,
            "entry_valor": entry_valor,
        })
        self.linhas.append(dados)

        # Atualiza o scroll do canvas principal
        self._painel.update_idletasks()
        self._canvas_principal.configure(
            scrollregion=self._canvas_principal.bbox("all")
        )

    def _selecionar_linha(self, dados):
        self.linha_selecionada = dados

    def _remover_linha_selecionada(self):
        if self.linha_selecionada is None:
            return
        self.linha_selecionada["frame"].destroy()
        self.linhas.remove(self.linha_selecionada)
        self.linha_selecionada = None
        self._canvas_principal.configure(
            scrollregion=self._canvas_principal.bbox("all")
        )

    def _fechar_janela(self):
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.aplicacao.ao_fechar_receita()
        self.destroy()

    def _limpar_formulario(self):
        """Limpa título e passos para cadastrar outra receita na mesma janela."""
        self.nome_editar = None
        self.campo_titulo.delete(0, "end")
        for linha in self.linhas:
            linha["frame"].destroy()
        self.linhas.clear()
        self.linha_selecionada = None
        self._canvas_principal.configure(
            scrollregion=self._canvas_principal.bbox("all")
        )
        self._focar_entrada(self.campo_titulo)

    def _coletar_passos(self) -> list[Step]:
        passos = []
        for linha in self.linhas:
            nome = linha["entry_nome"].get().strip()
            tipo = linha["combo_tipo"].get().strip()
            comando = (
                linha["entry_comando"].get().strip()
                if tipo in ("Serial", "Pop-up")
                else ""
            )
            valor = linha["entry_valor"].get().strip()
            if not nome and not tipo and not comando and not valor:
                continue
            passos.append(
                Step(name=nome, type=tipo, command=comando, expectedValue=valor)
            )
        return passos

    def _validar_passos(self, passos: list[Step]) -> str | None:
        for passo in passos:
            cmd = passo.command.strip()
            if passo.type == "Serial":
                if not cmd:
                    return f'Comando obrigatório no passo "{passo.name}".'
                if cmd not in ("1", "2", "3"):
                    return f'Comando inválido no passo "{passo.name}": use 1, 2 ou 3.'
            elif passo.type == "Pop-up" and cmd and cmd != "4":
                return f'Comando inválido no passo "{passo.name}": use 4 para acionar o display.'
        return None

    def _salvar_receita(self):
        """Chamado pelo btn_Salvar: lê a tela e delega ao ReceitaService."""
        titulo = self.campo_titulo.get()
        passos = self._coletar_passos()
        erro = self._validar_passos(passos)
        if erro:
            mostrar_mensagem(self, "Receita", erro, tipo="aviso")
            return
        erro = ReceitaService(titulo, passos, titulo_original=self.nome_editar).salvar_receita()
        if erro:
            mostrar_mensagem(self, "Receita", erro, tipo="aviso")
            return
        mostrar_mensagem(self, "", "Salvo com sucesso.")
        self._limpar_formulario()
