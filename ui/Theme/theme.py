import sys

# Paleta: principal (#94a3b8), branco, azul marinho (destaque)
COR_PRIMARIA = "#5c6879"
COR_BRANCO = "#ffffff"
COR_AZUL_MARINHO = "#16345c"
COR_AZUL_MARINHO_HOVER = "#112d53"

COR_CINZA_CLARO = "#EEEEEE"   # Cinza claro para o cabeçalho
COR_CINZA_MEDIO = "#D3D3D3"   # Cinza médio para a scrollbar
COR_MENU_HOVER = "#f5f7fa"    # Hover suave nos itens do menu
COR_VERDE = "#16a34a"
COR_VERDE_CLARO = "#86efac"
COR_VERMELHO = "#dc2626"
COR_VERMELHO_CLARO = "#fca5a5"

_FONTE_BASE = "Segoe UI" if sys.platform == "win32" else "Helvetica"
_TAMANHO = 12
_TAMANHO_MENU = 12

FONTE_NORMAL = (_FONTE_BASE, _TAMANHO)
FONTE_BOLD = (_FONTE_BASE, _TAMANHO, "bold")
FONTE_STATUS = (_FONTE_BASE, _TAMANHO, "bold")
FONTE_MENU = (_FONTE_BASE, _TAMANHO_MENU)

TIPOS_TESTE = ["Serial", "Pop-up", "Modelo"]

COL_IDX_TESTE = 0
COL_IDX_RANGE = 1
COL_IDX_VALOR = 2
COL_IDX_STATUS = 3

COLUNAS_TABELA_PRINCIPAL = ("TESTE", "RANGE", "VALOR", "STATUS")

COL_TESTE = 0.32
COL_RANGE = 0.22
COL_VALOR = 0.22
COL_STATUS = 0.24

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
