import tkinter as tk

from ui.branding import aplicar_icone
from ui.Theme import theme as t


def mostrar(parent, titulo: str, mensagem: str, tipo: str = "info") -> None:
    """Diálogo modal sem barra do sistema; a janela pai mantém decoração normal."""
    dlg = tk.Toplevel(parent)
    dlg.withdraw()
    aplicar_icone(dlg)
    dlg.configure(bg=t.COR_PRIMARIA)
    dlg.resizable(False, False)
    dlg.minsize(420, 160)

    moldura = tk.Frame(dlg, bg=t.COR_PRIMARIA, padx=1, pady=1)
    moldura.pack(fill="both", expand=True)

    conteudo = tk.Frame(moldura, bg=t.COR_BRANCO, padx=40, pady=32)
    conteudo.pack(fill="both", expand=True)

    fonte_msg = (t.FONTE_NORMAL[0], 14)
    cor_texto = t.COR_PRIMARIA if tipo == "aviso" else t.COR_AZUL_MARINHO

    tk.Label(
        conteudo,
        text=mensagem,
        font=fonte_msg,
        bg=t.COR_BRANCO,
        fg=cor_texto,
        wraplength=460,
        justify="center",
    ).pack(pady=(0, 24))

    def fechar():
        dlg.grab_release()
        dlg.destroy()

    tk.Button(
        conteudo,
        text="OK",
        font=fonte_msg,
        bg=t.COR_AZUL_MARINHO,
        fg="white",
        activebackground=t.COR_AZUL_MARINHO_HOVER,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        bd=0,
        padx=32,
        pady=10,
        command=fechar,
    ).pack()

    dlg.bind("<Return>", lambda _e: fechar())
    dlg.bind("<Escape>", lambda _e: fechar())
    dlg.protocol("WM_DELETE_WINDOW", fechar)

    dlg.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - dlg.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - dlg.winfo_height()) // 2
    dlg.geometry(f"+{x}+{y}")

    dlg.overrideredirect(True)
    dlg.deiconify()
    dlg.lift(parent)
    dlg.grab_set()
    dlg.focus_force()
    parent.wait_window(dlg)
