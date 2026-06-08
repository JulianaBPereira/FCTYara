# Juliana Pereira | Delta Sollutions - 2026

from dataclasses import dataclass, field
from typing import List
   
    # passo
@dataclass
class Step:
    name: str
    type: str
    command: str = ""
    expectedValue: str = ""

    # receita
@dataclass
class Recipe:
    title: str
    steps: List[Step] = field(default_factory=list)

    # configuração do setup
@dataclass
class Settings:
    channelAPort: str
    channelABaud: int
    channelARecipe: str
