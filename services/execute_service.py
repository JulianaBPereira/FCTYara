from domain.models import Step
from infrastructure import serial_port
from infrastructure.serial_port import enviar_comando,_conexao, _TIMEOUT_RESPOSTA


def executar(step: Step) -> dict:
    cmd = step.command.strip()

    if not cmd:
        return {"nome": step.name, "resposta": "Comando não definido", "resultado": "Fail"}

    if cmd == "1":
        esperado = "1"
    elif cmd == "2":
        esperado = "2"
    elif cmd == "3":
        esperado = "3"
    elif cmd == "4":
        return {"nome": step.name, "resposta": "", "resultado": "Pass"}
    else:
        return {"nome": step.name, "resposta": "Erro: comando desconhecido", "resultado": "Fail"}

    resposta = enviar_comando(cmd).split("\n")[0].strip().strip("\r").split(";")[0].strip()

    if resposta == esperado:
        return {"nome": step.name, "resposta": resposta, "resultado": "Pass"}
    else:
        return {"nome": step.name, "resposta": resposta or "0", "resultado": "Fail"}

def desligar_placa() -> None:
    if not _conexao or not _conexao.is_open:
        return
    try:
        _conexao.reset_input_buffer()
        _conexao.write(b"2\n")
        _conexao.flush()
        _conexao.timeout = 2
        _conexao.readline()  # consome a resposta
        _conexao.timeout = _TIMEOUT_RESPOSTA
    except Exception:
        pass
