# Juliana Pereira | Delta Sollutions - 2026

import tkinter as tk

from ui.branding import aplicar_icone, centralizar_dialogo
from ui.Theme import theme as t

MENSAGEM_PADRAO_POPUP = (
    "Verifique se a versão no display é a mesma ativa no teste."
)


def perguntar(
    parent,
    titulo: str,
    valor_display: str = "",
    *,
    instrucao: str = MENSAGEM_PADRAO_POPUP,
) -> bool:
    """Diálogo modal Sim/Não. Retorna True se o operador confirmou (Sim)."""
    numeracao = (valor_display or "").strip()

    dlg = tk.Toplevel(parent)
    dlg.withdraw()
    aplicar_icone(dlg)
    dlg.configure(bg=t.COR_PRIMARIA)
    dlg.resizable(False, False)
    _LARGURA = 420
    _ALTURA = 220
    dlg.minsize(_LARGURA, _ALTURA)
    dlg.maxsize(_LARGURA, _ALTURA)
    # overrideredirect e transient definidos antes da centralização para que o
    # cálculo de posição já reflita a janela sem barra de título no Linux/X11.
    dlg.overrideredirect(True)
    dlg.transient(parent.winfo_toplevel())

    moldura = tk.Frame(dlg, bg=t.COR_PRIMARIA, padx=1, pady=1)
    moldura.pack(fill="both", expand=True)

    conteudo = tk.Frame(moldura, bg=t.COR_BRANCO, padx=24, pady=16)
    conteudo.pack(fill="both", expand=True)

    fonte_instrucao = (t.FONTE_NORMAL[0], 13)
    fonte_numeracao = (t.FONTE_BOLD[0], 32, "bold")
    fonte_btn = (t.FONTE_NORMAL[0], 16)
    fonte_titulo = (t.FONTE_BOLD[0], 15, "bold")

    if titulo:
        tk.Label(
            conteudo,
            text=titulo,
            font=fonte_titulo,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            justify="center",
        ).pack(pady=(0, 4))

    tk.Label(
        conteudo,
        text=instrucao,
        font=fonte_instrucao,
        bg=t.COR_BRANCO,
        fg=t.COR_AZUL_MARINHO,
        wraplength=360,
        justify="center",
    ).pack(pady=(0, 6))

    if numeracao:
        tk.Label(
            conteudo,
            text=numeracao,
            font=fonte_numeracao,
            bg=t.COR_BRANCO,
            fg=t.COR_AZUL_MARINHO,
            justify="center",
        ).pack(pady=(0, 10))

    resultado = {"confirmado": False}

    def fechar(confirmado: bool) -> None:
        resultado["confirmado"] = confirmado
        dlg.grab_release()
        dlg.destroy()

    botoes = tk.Frame(conteudo, bg=t.COR_BRANCO)
    botoes.pack()

    estilo_btn = dict(
        font=fonte_btn,
        relief="flat",
        cursor="hand2",
        bd=0,
        padx=22,
        pady=8,
    )

    tk.Button(
        botoes,
        text="Sim",
        bg=t.COR_AZUL_MARINHO,
        fg="white",
        activebackground=t.COR_AZUL_MARINHO_HOVER,
        activeforeground="white",
        command=lambda: fechar(True),
        **estilo_btn,
    ).pack(side="left", padx=(0, 12))

    tk.Button(
        botoes,
        text="Não",
        bg=t.COR_PRIMARIA,
        fg="white",
        activebackground="#4a5568",
        activeforeground="white",
        command=lambda: fechar(False),
        **estilo_btn,
    ).pack(side="left")

    dlg.protocol("WM_DELETE_WINDOW", lambda: fechar(False))

    centralizar_dialogo(dlg, parent, largura=_LARGURA, altura=_ALTURA)

    dlg.deiconify()
    dlg.lift(parent)
    # No Linux/X11, deiconify() é assíncrono: o servidor X ainda não mapeou a
    # janela quando grab_set() é chamado na linha seguinte. wait_visibility()
    # aguarda o VisibilityNotify do X11 antes de ativar o grab, evitando que o
    # input fique capturado por uma janela invisível (freeze).
    try:
        dlg.wait_visibility()
    except tk.TclError:
        pass
    dlg.grab_set()
    dlg.focus_force()
    parent.wait_window(dlg)
    return resultado["confirmado"]
