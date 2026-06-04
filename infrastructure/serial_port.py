import time
import serial
import serial.tools.list_ports

_conexao: serial.Serial | None = None


def listar_portas():
    portas = serial.tools.list_ports.comports()
    return [porta.device for porta in portas]


def conectar(porta: str, baud: int) -> bool:
    global _conexao
    fechar()
    try:
        _conexao = serial.Serial(porta, baud, timeout=1)
        time.sleep(7)
        _conexao.reset_input_buffer()
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


def enviar_sem_resposta(comando: str) -> bool:
    conexao = obter_conexao()

    if conexao is None or not conexao.is_open:
        return False

    try:
        conexao.reset_input_buffer()
        conexao.write(f"{comando}\n".encode())
        return True
    except Exception:
        return False


def enviar_comando(comando: str) -> str:
    conexao = obter_conexao()

    if conexao is None or not conexao.is_open:
        return "ERRO: porta serial não conectada"

    try:
        conexao.reset_input_buffer()
        conexao.write(f"{comando}\n".encode())

        while conexao.in_waiting == 0:
            time.sleep(0.05)

        time.sleep(0.1)  # aguarda a linha completa chegar
        resposta = conexao.readline().decode(errors="replace").strip()

        return resposta

    except Exception as ex:
        return f"ERRO: {ex}"