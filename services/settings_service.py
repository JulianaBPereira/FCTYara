from dataclasses import asdict
from pathlib import Path
import json
import sys

from domain.models import Settings


def _pasta_configuracao() -> Path:
    if sys.platform == "win32":
        return Path.home() / "Desktop" / "FCTYara"
    return Path("/var/app-data/FCTYara")

# Essa função serve para salvar as escolhas do setup pelo usuario, 
# salvar a porta COM escolhida, o baud rate e a receita 
# possui 3 validações que obriga o usuario a nao deixar nenhum comboBox vazio
# cria um arquivo chamado settings.json e salvar em uma pasta especifica criada automaticamente

class SettingsService:
    def __init__(self, channelAPort: str, channelABaud: int, channelARecipe: str):
        self.channelAPort = channelAPort
        self.channelABaud = channelABaud
        self.channelARecipe = channelARecipe

    def salvar_configuracao(self):
        try:
            if not self.channelAPort:
                return "A Porta COM é obrigatória."

            if not self.channelABaud:
                return "O Baud Rate é obrigatório."

            if not self.channelARecipe:
                return "A Receita é obrigatória."

            pasta = _pasta_configuracao()
            pasta.mkdir(parents=True, exist_ok=True)

            arquivo = pasta / "settings.json"

            settings = Settings(
                channelAPort=self.channelAPort,
                channelABaud=self.channelABaud,
                channelARecipe=self.channelARecipe,
            )

            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(asdict(settings), f, indent=4, ensure_ascii=False)

            print("Configuração salva com sucesso!")

        except Exception as e:
            return f"Erro ao salvar a configuração: {e}"


def carregar_configuracao() -> Settings | None:
    arquivo = _pasta_configuracao() / "settings.json"

    if not arquivo.exists():
        return None
    
    with open(arquivo, encoding="utf-8") as f:
        data = json.load(f)

    baud = data.get("channelABaud")
    
    return Settings(
        channelAPort=data.get("channelAPort") or "",
        channelABaud=int(baud) if baud is not None else 0,
        channelARecipe=data.get("channelARecipe") or "",
    )

# Raspberry: se /var/app-data não existir ou faltar permissão, criar uma vez com:
# sudo mkdir -p /var/app-data/FCTYara
# sudo chown -R delta:delta /var/app-data
# chmod -R 750 /var/app-data
# Windows (teste): salva em Desktop/FCTYara/settings.json

