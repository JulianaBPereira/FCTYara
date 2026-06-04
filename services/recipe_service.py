from dataclasses import asdict
from pathlib import Path
import json

from domain.models import Recipe, Step

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

            pasta = Path.home() / "Desktop" / "Recipes"
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

    def carregar_receitas(self):
        pasta = Path.home() / "Desktop" / "Recipes"
        if not pasta.exists():
            return []
        receitas = []
        for arquivo in pasta.glob("*.json"):
            with open(arquivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                passos = [Step(**step) for step in data.get("steps", [])]
                receita = Recipe(title=data.get("title", ""), steps=passos)
                receitas.append(receita)
        return receitas

