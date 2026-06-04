from dataclasses import asdict
from pathlib import Path
import json
import sys

from domain.models import Recipe, Step


def _pasta_receitas() -> Path:
    return Path.home() / "Desktop" / "Recipes"

# A função salvar_receita conta com uma validação inicial de cadastro, que confere se titulo
# e passos estão preenchidos, e se o titulo é único.
# a partir da linha 24, verifica se existe pasta e se não, cria.
# por fim, salva o arquivo em formato json.

class ReceitaService:
    def __init__(self, title: str, steps: list[Step], titulo_original: str | None = None):
        self.title = title
        self.steps = steps
        self.titulo_original = titulo_original

    def salvar_receita(self):
        try:
            titulo = self.title.strip()
            if not titulo:
                return "Título da receita é obrigatório."
            if not self.steps:
                return "Pelo menos um passo é obrigatório."

            pasta = _pasta_receitas()
            pasta.mkdir(parents=True, exist_ok=True)

            arquivo = pasta / f"{titulo}.json"
            if arquivo.exists():
                original = (self.titulo_original or "").strip()
                if titulo != original:
                    return "Título da receita deve ser único."

            recipe = Recipe(
                title=titulo,
                steps=self.steps
            )

            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(
                    asdict(recipe), # O asdict é uma função que transforma um objeto dataclss em um dicionário.
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            original = (self.titulo_original or "").strip()
            if original and original != titulo:
                arquivo_antigo = pasta / f"{original}.json"
                if arquivo_antigo.exists():
                    arquivo_antigo.unlink()

            print("Arquivo JSON salvo com sucesso!")

        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")

    def carregar_receitas(self) -> list[Recipe]:
        pasta = _pasta_receitas()
        if not pasta.exists():
            return []

        receitas: list[Recipe] = []
        for arquivo in sorted(pasta.glob("*.json")):
            receita = _ler_arquivo_receita(arquivo)
            if receita is not None:
                receitas.append(receita)
        return receitas


def _ler_arquivo_receita(arquivo: Path) -> Recipe | None:
    try:
        with open(arquivo, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(
            f"[FCTYara] Receita ignorada (JSON inválido): {arquivo.name} — {e}",
            file=sys.stderr,
        )
        return None
    except OSError as e:
        print(
            f"[FCTYara] Receita ignorada (erro ao ler): {arquivo.name} — {e}",
            file=sys.stderr,
        )
        return None

    if not isinstance(data, dict):
        print(
            f"[FCTYara] Receita ignorada (formato inválido): {arquivo.name}",
            file=sys.stderr,
        )
        return None

    titulo = str(data.get("title") or arquivo.stem).strip()
    passos_brutos = data.get("steps", [])
    if not isinstance(passos_brutos, list):
        passos_brutos = []

    passos: list[Step] = []
    for i, item in enumerate(passos_brutos):
        if not isinstance(item, dict):
            continue
        try:
            passos.append(Step(**item))
        except TypeError as e:
            print(
                f"[FCTYara] Passo {i + 1} ignorado em {arquivo.name}: {e}",
                file=sys.stderr,
            )

    return Recipe(title=titulo, steps=passos)

