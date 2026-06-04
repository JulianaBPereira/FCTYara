import time  
import serial 
import serial.tools.list_ports 

# Variável global que guarda a conexão serial ativa (ou None se não conectado)
_conexao: serial.Serial | None = None


def listar_portas():
    portas = serial.tools.list_ports.comports()
    
    # Retorna apenas o nome da porta (ex: COM3, /dev/ttyUSB0)
    return [porta.device for porta in portas]


def conectar(porta: str, baud: int) -> bool:
    global _conexao  # Permite modificar a variável global
    
    fechar()  # Fecha qualquer conexão anterior antes de abrir uma nova

    # Cria conexão serial com porta e baud rate informados
    # Aguarda o Arduino/Raspberry reiniciar após conexão serial
    # Limpa qualquer lixo no buffer de entrada
    # Retorna True se a conexão estiver aberta
    try:
        _conexao = serial.Serial(porta, baud, timeout=1)
        
        time.sleep(5)
        _conexao.reset_input_buffer()

        return _conexao.is_open

    except serial.SerialException:
        # Caso falhe ao abrir a porta, limpa conexão
        _conexao = None
        return False


def fechar() -> None:
    global _conexao  # Acessa variável global

    # Se existe conexão e ela está aberta, fecha a porta serial
    if _conexao and _conexao.is_open:
        _conexao.close()

    # Remove referência da conexão
    _conexao = None


def obter_conexao() -> serial.Serial | None:
    # Retorna a conexão atual (ou None se não houver conexão ativa)
    return _conexao


def enviar_sem_resposta(comando: str) -> bool:
    # Obtém conexão ativa
    conexao = obter_conexao()

    # Se não existir conexão válida, retorna erro
    if conexao is None or not conexao.is_open:
        return False

    try:
        # Limpa buffer antes de enviar comando
        conexao.reset_input_buffer()

        # Envia comando para serial (com \n no final)
        conexao.write(f"{comando}\n".encode())

        # Retorna sucesso
        return True

    except Exception:
        # Se qualquer erro acontecer, retorna False
        return False


def enviar_comando(comando: str) -> str:
    # Obtém conexão serial atual
    conexao = obter_conexao()

    # Se não estiver conectado, retorna erro
    if conexao is None or not conexao.is_open:
        return "ERRO: porta serial não conectada"

    try:
        # Limpa buffer antes de enviar novo comando
        conexao.reset_input_buffer()

        # Envia comando para o dispositivo
        conexao.write(f"{comando}\n".encode())

        # Espera até chegar algum dado no buffer
        while conexao.in_waiting == 0:
            time.sleep(0.05)

        # Pequena espera para garantir que a mensagem chegou completa
        time.sleep(0.1)

        # Lê a linha recebida do dispositivo
        resposta = conexao.readline().decode(errors="replace").strip()

        # Retorna a resposta recebida
        return resposta

    except Exception as ex:
        # Retorna erro caso algo falhe
        return f"ERRO: {ex}"