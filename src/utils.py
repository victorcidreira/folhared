import os

def criar_diretorio(diretorio):
    """Cria um diretório se ele não existir."""
    try:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
    except Exception as e:
        print(f"Erro ao criar o diretório: {e}")