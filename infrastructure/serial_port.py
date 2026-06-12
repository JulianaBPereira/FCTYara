# Juliana Pereira | Delta Sollutions - 2026

import threading
import queue
import serial
import serial.tools.list_ports

_TIMEOUT_RESPOSTA = 5

_conexao: serial.Serial | None = None
_fila: queue.Queue = queue.Queue()
_fila_log: queue.Queue[tuple[str, str, str]] = queue.Queue()
_fila_entrada: queue.Queue[str] = queue.Queue()
_lendo = False
_escutando_entrada = False


def log(enviado: str = "", recebido: str = "", alerta: str = "") -> None:
    if enviado or recebido or alerta:
        _fila_log.put((enviado, recebido, alerta))


def drenar_logs() -> list[tuple[str, str, str]]:
    itens: list[tuple[str, str, str]] = []
    try:
        while True:
            itens.append(_fila_log.get_nowait())
    except queue.Empty:
        pass
    return itens


def iniciar_escuta_entrada() -> None:
    global _escutando_entrada
    try:
        while True:
            _fila_entrada.get_nowait()
    except queue.Empty:
        pass
    _escutando_entrada = True


def parar_escuta_entrada() -> None:
    global _escutando_entrada
    _escutando_entrada = False
    try:
        while True:
            _fila_entrada.get_nowait()
    except queue.Empty:
        pass


def drenar_entrada() -> list[str]:
    if not _escutando_entrada:
        return []
    itens: list[str] = []
    try:
        while True:
            itens.append(_fila_entrada.get_nowait())
    except queue.Empty:
        pass
    return itens


def _loop_leitura() -> None:
    while _lendo and _conexao and _conexao.is_open:
        try:
            linha = _conexao.readline().decode(errors="replace").strip()
            if linha and linha != "0":
                _fila.put(linha)
                if _escutando_entrada:
                    _fila_entrada.put(linha)
        except Exception:
            if not (_conexao and _conexao.is_open):
                break
            continue


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