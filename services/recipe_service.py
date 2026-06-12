# Juliana Pereira | Delta Sollutions - 2026

from dataclasses import asdict
from pathlib import Path
import json
import sys

from domain.models import Recipe, Step


def _pasta_receitas() -> Path:
    # Retorna o caminho padrão onde as receitas (.json) são salvas e lidas.
    return Path.home() / "Desktop" / "Recipes"


class ReceitaService:
    """Responsável por validar e salvar uma receita em disco."""

    def __init__(self, title: str, steps: list[Step], titulo_original: str | None = None):
        self.title = title
        self.steps = steps
        # Usado na edição: permite renomear a receita e apagar o .json antigo depois.
        self.titulo_original = titulo_original

    def salvar_receita(self):
        """Valida os dados, grava a receita em JSON e retorna mensagem de erro ou None."""
        try:
            titulo = self.title.strip()
            if not titulo:
                return "Título da receita é obrigatório."
            if not self.steps:
                return "Pelo menos um passo é obrigatório."

            pasta = _pasta_receitas()
            pasta.mkdir(parents=True, exist_ok=True)

            # O nome do arquivo é o título da receita (ex.: "MinhaReceita.json").
            arquivo = pasta / f"{titulo}.json"
            if arquivo.exists():
                original = (self.titulo_original or "").strip()
                # Bloqueia título duplicado, exceto quando é a mesma receita em edição.
                if titulo != original:
                    return "Título da receita deve ser único."

            recipe = Recipe(title=titulo, steps=self.steps)

            with open(arquivo, "w", encoding="utf-8") as f:
                # asdict converte o dataclass Recipe em dict para o json.dump.
                json.dump(asdict(recipe), f, indent=4, ensure_ascii=False)

            original = (self.titulo_original or "").strip()
            if original and original != titulo:
                arquivo_antigo = pasta / f"{original}.json"
                if arquivo_antigo.exists():
                    arquivo_antigo.unlink()

            print("Arquivo JSON salvo com sucesso!")

        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")


def carregar_receitas() -> list[str]:
    """Lista os títulos das receitas disponíveis.

    Usado para popular combosBox (ex.: aba de configuração).
    Lê apenas o nome do arquivo (.stem), sem abrir o JSON.
    """
    pasta = _pasta_receitas()
    if not pasta.exists():
        return []
    return sorted(arquivo.stem for arquivo in pasta.glob("*.json"))


def carregar_passos(titulo: str) -> list[Step] | None:
    # Monta o caminho completo do arquivo JSON da receita.
    # O '/' do pathlib junta pastas como os.path.join, e strip() remove espaços no título.
    arquivo = _pasta_receitas() / f"{titulo.strip()}.json"

    # Se o arquivo não existir, retorna None para o chamador saber que a receita não existe.
    if not arquivo.exists():
        return None

    # Lê o arquivo e converte o JSON em dicionário Python.
    # Captura erros de JSON inválido (JSONDecodeError) ou falha de leitura (OSError).
    try:
        data = json.loads(arquivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[FCTDelta] Erro ao ler {arquivo.name}: {e}", file=sys.stderr)
        return None

    # O JSON precisa ser um dicionário no nível raiz, senão o arquivo está no formato errado.
    if not isinstance(data, dict):
        return None

    # Busca a chave "steps". Se não existir, get() retorna [] por padrão.
    passos_brutos = data.get("steps", [])

    # "steps" precisa ser uma lista. Se for outro tipo, retorna lista vazia (arquivo existe mas sem passos).
    if not isinstance(passos_brutos, list):
        return []

    # Percorre cada item tentando criar um Step. Itens inválidos são ignorados com aviso no stderr.
    passos = []
    for i, item in enumerate(passos_brutos):
        if not isinstance(item, dict):
            continue
        try:
            raw_val = item.get("expectedValue", "")
            if isinstance(raw_val, list):
                expected_value: str | list[str] = [
                    str(c).strip() for c in raw_val if str(c).strip()
                ]
            else:
                expected_value = str(raw_val) if raw_val is not None else ""
            passos.append(Step(
                name=item.get("name", ""),
                type=item.get("type", ""),
                command=item.get("command", ""),
                expectedValue=expected_value,
            ))
        except TypeError as e:
            print(f"[FCTDelta] Passo {i + 1} ignorado em {arquivo.name}: {e}", file=sys.stderr)

    return passos