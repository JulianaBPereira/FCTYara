# Juliana Pereira | Delta Sollutions - 2026

# Essa classe é responsável por comparar o código de barras lido com um valor esperado, 
# retornando "PASS" se os códigos coincidirem e "FAIL" caso contrário. 
# O método CompararBarcode é simples e direto, realizando a comparação de forma 
# eficiente.

class BarcodeService:
    def __init__(self, code: str):
        self.code = code.strip()

    def CompararBarcode(self, expectedValue: str | list[str]) -> str:
        if isinstance(expectedValue, list):
            validos = {c.strip() for c in expectedValue if c.strip()}
        else:
            validos = {expectedValue.strip()} if expectedValue.strip() else set()
        if self.code in validos:
            return "PASS"
        return "FAIL"