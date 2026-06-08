import threading
import queue
import serial
import serial.tools.list_ports

_TIMEOUT_RESPOSTA = 5

_conexao: serial.Serial | None = None
_fila: queue.Queue = queue.Queue()
_lendo = False
_on_log = None


def log(enviado: str = "", recebido: str = "", alerta: str = "") -> None:
    if _on_log:
        _on_log(enviado, recebido, alerta)


def _loop_leitura() -> None:
    while _lendo and _conexao and _conexao.is_open:
        try:
            linha = _conexao.readline().decode(errors="replace").strip()
            if linha and linha != "0":
                _fila.put(linha)
        except Exception:
            break


def listar_portas() -> list[str]:
    return [p.device for p in serial.tools.list_ports.comports()]


def conectar(porta: str, baud: int) -> bool:
    global _conexao, _lendo

    fechar()

    try:
        _conexao = serial.Serial(porta, baud, timeout=1)

        _lendo = True
        threading.Thread(target=_loop_leitura, daemon=True).start()
        return True

    except serial.SerialException:
        _conexao = None
        return False


def fechar() -> None:
    global _conexao, _lendo

    _lendo = False
    if _conexao and _conexao.is_open:
        _conexao.close()
    _conexao = None


def enviar_comando(comando: str) -> str:
    if not _conexao or not _conexao.is_open:
        return "ERRO: porta serial não conectada"

    try:
        with _fila.mutex:
            _fila.queue.clear()

        _conexao.write(f"{comando}\n".encode())
        _conexao.flush()

        return _fila.get(timeout=_TIMEOUT_RESPOSTA)

    except queue.Empty:
        return "ERRO: Sem resposta"
    except Exception as ex:
        return f"ERRO: {ex}"