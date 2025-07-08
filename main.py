from app import run_app

def main():
    try:
        run_app()
    except Exception as e:
        print(f"Ocorreu um erro ao executar o aplicativo: {e}")

if __name__ == "__main__":
    main()