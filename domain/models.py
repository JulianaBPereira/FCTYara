from dataclasses import dataclass, field
from typing import List
   
    # receita
@dataclass
class Step:
    name: str
    type: str
    command: str = ""
    expectedValue: str = ""

@dataclass
class Recipe:
    title: str
    steps: List[Step] = field(default_factory=list)

    # teste
@dataclass
class Test:
    name: str
    type: str
    expectedValue: str 
   
   # resultado do teste
@dataclass
class ResultTest:
    value: str
    status: str  # "PASS" | "FAIL" 

    # salvar resultado do teste
@dataclass
class SaveTest:
    title: str
    name: str
    type: str
    expectedValue: str
    data: int

    # configuração do setup
@dataclass
class Settings:
    channelAPort: str
    channelABaud: int
    channelARecipe: str

    # Barcode
@dataclass
class Barcode:
    code: str