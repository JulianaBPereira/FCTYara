import sys
from pathlib import Path

_NOME_PASTA = "FCTYaraLogs"


def pasta_logs_padrao() -> Path:
    # Desktop.FCTYaraLogs - Windows (usuário atual) ou Raspberry (delta).
    
    if sys.platform == "win32":
        return Path.home() / "Desktop" / _NOME_PASTA
    return Path("/home/delta/Desktop") / _NOME_PASTA


def sugestoes_pasta_logs() -> list[str]:
    padrao = pasta_logs_padrao()
    sugestoes = [str(padrao)]

    desktop = padrao.parent
    if desktop.is_dir():
        for item in sorted(desktop.iterdir()):
            if item.is_dir() and item.name.lower().startswith("fct"):
                caminho = str(item)
                if caminho not in sugestoes:
                    sugestoes.append(caminho)

    return sugestoes
