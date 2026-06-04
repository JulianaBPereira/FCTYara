from domain.models import Step
from infrastructure.serial_port import enviar_comando, obter_conexao


# Essa função pega a porta COM, enviar os comandos 
# e percorre as condições ate achar o teste certo e 
# enviar o comando para o arduino.

def executar(step: Step) -> dict:
    if obter_conexao() is None:
        return {"nome": step.name, "resposta": "ERRO: porta serial não conectada", "aprovado": False}

    nome = step.name.upper().strip() #

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

    print(f"Recebido: {repr(resposta)}")

    valor = resposta.split(";")[0] if resposta else ""

    if resposta.strip() == "1;X" or resposta.strip() == "2;X" or resposta.strip() == "3;X":
        aprovado = True
    else:
        aprovado = False

    return {
        "nome": step.name,
        "resposta": valor,
        "aprovado": aprovado
    }

    
