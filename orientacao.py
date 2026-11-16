# Arquivo: orientacao.py
# Aqui fica a classe Orientacao, que representa UMA linha do arquivo CSV da base.
# Ela guarda os dados de uma orientação e sabe mostrar esses dados na tela.


class Orientacao:
    # O __init__ é chamado quando criamos um objeto novo: Orientacao(...)
    # Cada "self.algo" é um atributo, ou seja, uma informação guardada no objeto
    def __init__(self, codigo, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = codigo                      # número único da orientação
        self.categoria = categoria            # ex.: Saúde, Benefícios...
        self.titulo = titulo                  # nome curto da orientação
        self.palavras_chave = palavras_chave  # lista de palavras usadas na busca
        self.resposta = resposta              # texto simples explicando o que fazer
        self.documentos = documentos          # lista de documentos necessários
        self.onde = onde                      # lista de lugares onde ir
        self.fonte = fonte                    # site oficial da informação
        self.verificado_em = verificado_em    # data em que a equipe conferiu

    # Mostra a orientação completa na tela (fonte, data e aviso sempre aparecem)
    def exibir(self):
        print("\n>> " + self.titulo + "  [" + self.categoria + "]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print("  - " + documento)
        print("Onde: " + " ou ".join(self.onde))
        print("Fonte: " + self.fonte + " (verificado em " + self.verificado_em + ")")
        print("Aviso: este assistente NÃO é um canal oficial.")

    # Devolve uma linha curta para listas e menus. Ex.: "Cartão SUS [Saúde]"
    def resumo(self):
        return self.titulo + " [" + self.categoria + "]"
