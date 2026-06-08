# Juliana Pereira | Delta Sollutions - 2026

# Essa classe é responsável por comparar o código de barras lido com um valor esperado, 
# retornando "PASS" se os códigos coincidirem e "FAIL" caso contrário. 
# O método CompararBarcode é simples e direto, realizando a comparação de forma 
# eficiente.

class BarcodeService:
    def __init__(self, code: str):
        self.code = code.strip()

    def CompararBarcode(self, expectedValue: str) -> str:
        if self.code == expectedValue.strip():
            return "PASS"
        return "FAIL"