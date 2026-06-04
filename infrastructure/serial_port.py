import serial
import serial.tools.list_ports

_conexao: serial.Serial | None = None

# Essa função lista as portas seriais disponíveis no sistema, usando a biblioteca pyserial.
# Fechar conexão serial, caso exista, para evitar conflitos ao tentar conectar a uma nova porta.
# A função obter_conexao retorna a conexão serial atual, ou None se não houver conexão ativa.


def listar_portas():
    # o comports é uma função que detecta automaticamente as portas seriais disponíveis no sistema.
    # Para cada porta na lista de portas, pega o atributo device que é referente ao nome da porta
    portas = serial.tools.list_ports.comports()
    return [porta.device for porta in portas]


def conectar(porta: str, baud: int) -> bool:
    global _conexao
    fechar()
    try:
        _conexao = serial.Serial(porta, baud, timeout=1)
        return _conexao.is_open
    except serial.SerialException:
        _conexao = None
        return False


def fechar() -> None:
    global _conexao
    if _conexao and _conexao.is_open:
        _conexao.close()
    _conexao = None


def obter_conexao() -> serial.Serial | None:
    return _conexao


def enviar_comando(comando: str) -> str:
    conexao = obter_conexao()
    if conexao is None or not conexao.is_open:
        return "ERRO: porta serial não conectada"
    
    try:
        conexao.reset_input_buffer()
        conexao.write(f"{comando}\n".encode())
        resposta = conexao.readline().decode(errors="replace").strip()
        return resposta
    except serial.SerialTimeoutException:
        return "TIMEOUT"
    except Exception as ex:
        return f"ERRO: {ex}"
