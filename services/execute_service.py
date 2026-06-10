# Juliana Pereira | Delta Sollutions - 2026

from domain.models import Step
from infrastructure.serial_port import enviar_comando, log


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
        log("4", "pop-up aberto")
        return {"nome": step.name, "resposta": "", "resultado": "Pass"}
    elif cmd == "start":
        log("teste iniciado")
    else:
        return {"nome": step.name, "resposta": "Erro: comando desconhecido", "resultado": "Fail"}

    resposta_bruta = enviar_comando(cmd)
    log(cmd, resposta_bruta)
    resposta = resposta_bruta.split("\n")[0].strip().strip("\r").split(";")[0].strip()

    if resposta == esperado:
        return {"nome": step.name, "resposta": resposta, "resultado": "Pass"}
    else:
        return {"nome": step.name, "resposta": resposta or "0", "resultado": "Fail"}


def desligar_placa() -> None:
    resposta = enviar_comando("2")
    log("2", resposta, alerta="Desligando Placa")
