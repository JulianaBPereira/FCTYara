from domain.models import Step
from infrastructure.serial_port import enviar_comando, enviar_sem_resposta, obter_conexao


def disparar_display() -> bool:
    """Envia comando 4; o hardware não retorna resposta — o operador confirma na UI."""
    if obter_conexao() is None:
        return False
    ok = enviar_sem_resposta("4")
    if ok:
        print("Enviado: 4")
    return ok


def executar(step: Step) -> dict:
    if obter_conexao() is None:
        return {"nome": step.name, "resposta": "ERRO: porta serial não conectada", "aprovado": False}

    nome = step.name.upper().strip()

    if nome == "LIGAR PLACA":
        resposta = enviar_comando("1")
        print(f"Enviado: 1")

    elif nome == "DESLIGAR PLACA":
        resposta = enviar_comando("2")
        print(f"Enviado: 2")

    elif nome == "COMUNICAÇÃO":
        resposta = enviar_comando("3")
        print(f"Enviado: 3")

    else:
        return {"nome": step.name, "resposta": "Teste não cadastrado", "aprovado": False}

    # pega só a primeira linha limpa
    primeira_linha = resposta.split("\n")[0].strip().strip("\r")
    print(f"Recebido: {repr(primeira_linha)}")

    if not primeira_linha or primeira_linha == "0":
        return {"nome": step.name, "resposta": "0", "aprovado": False}

    valor = primeira_linha.split(";")[0]

    aprovado = primeira_linha in ("1;X", "2;X", "3;X", "4;X")

    return {
        "nome": step.name,
        "resposta": valor,
        "aprovado": aprovado
    }