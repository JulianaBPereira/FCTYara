import json
import sys
from pathlib import Path

from services.logs_path_service import pasta_logs_padrao

_DEFAULTS = {
    "pasta": "",
    "formato_txt": True,
    "formato_excel": False,
}


def _arquivo_config() -> Path:
    if sys.platform == "win32":
        return Path.home() / "Desktop" / "FCTDelta" / "rastreio.json"
    return Path("/var/app-data/FCTDelta/rastreio.json")


def salvar_config_rastreio(pasta: str, formato_txt: bool, formato_excel: bool) -> None:
    arquivo = _arquivo_config()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(
            {"pasta": pasta, "formato_txt": formato_txt, "formato_excel": formato_excel},
            f,
            indent=4,
        )


def carregar_config_rastreio() -> dict:
    arquivo = _arquivo_config()
    if not arquivo.exists():
        return dict(_DEFAULTS)
    try:
        with open(arquivo, encoding="utf-8") as f:
            data = json.load(f)
        return {
            "pasta": data.get("pasta", _DEFAULTS["pasta"]),
            "formato_txt": bool(data.get("formato_txt", _DEFAULTS["formato_txt"])),
            "formato_excel": bool(data.get("formato_excel", _DEFAULTS["formato_excel"])),
        }
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def pasta_logs_efetiva() -> Path:
    """Retorna a pasta configurada, ou a padrão se não estiver configurada."""
    config = carregar_config_rastreio()
    pasta_str = config.get("pasta", "").strip()
    return Path(pasta_str) if pasta_str else pasta_logs_padrao()
