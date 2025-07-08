import os
import sys

# Adiciona o diretório 'src' ao sys.path para que os módulos dentro dele possam ser importados
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from app import run_app

def main():
    try:
        run_app()
    except Exception as e:
        print(f"Ocorreu um erro ao executar o aplicativo: {e}")

if __name__ == "__main__":
    main()