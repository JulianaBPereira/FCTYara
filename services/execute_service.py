from domain.models import Step
from infrastructure.serial_port import enviar_comando, obter_conexao


# Essa função pega a porta COM, enviar os comandos 
# e percorre as condições ate achar o teste certo e 
# enviar o comando para o arduino.

def executar(step: Step) -> dict:
    if obter_conexao() is None:
        return {"nome": step.name, "resposta": "ERRO: porta serial não conectada", "aprovado": False}

    nome = step.name.upper().strip() # Normaliza o nome do passo para comparação (tudo maiúsculo e sem espaços extras)

    if nome == "LIGAR PLACA":
        resposta = enviar_comando("1")

    elif nome == "DESLIGAR PLACA":
        resposta = enviar_comando("2")
        
    elif nome == "COMUNICAÇÃO":
        resposta = enviar_comando("3")
    else:
        return {"nome": step.name, "resposta": "Teste não cadastrado", "aprovado": False}

    if resposta == "1":
        aprovado = True
    else:
        aprovado = False

    return {"nome": step.name, "resposta": resposta, "aprovado": aprovado}
