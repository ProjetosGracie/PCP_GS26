# Arquivo: main.py
# É o arquivo que você executa: python main.py
# Ele cria a base de conhecimento, cria o assistente e inicia o menu.

from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main():
    # Cria a base apontando para o CSV e carrega as orientações
    base = BaseConhecimento("Datasets/base_conhecimento.csv")
    base.carregar()

    # Cria o assistente, que usa a base (composição)
    assistente = Assistente("Citizen Assist AI", base)

    # Se a pessoa apertar Ctrl+C, o programa se despede sem mostrar erro feio
    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        print("\nAtendimento encerrado. Até logo!")
        assistente.exportar_csv()


# Só roda o main() quando este arquivo é executado diretamente
if __name__ == "__main__":
    main()
