# Arquivo: base_conhecimento.py
# Aqui ficam a função normalizar() e a classe BaseConhecimento.
# A BaseConhecimento lê o CSV, guarda todas as orientações e faz a busca com pontuação.

from orientacao import Orientacao

# Dicionário que troca letras com acento por letras sem acento
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Quantidade de campos que cada linha do CSV precisa ter
TOTAL_CAMPOS = 9


# Deixa o texto em minúsculas, sem acento e sem pontuação.
# O espaço no começo e no fim ajuda a achar palavras inteiras (ex.: " sus ")
def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    # caminho = onde está o CSV | orientacoes = lista de objetos Orientacao (composição)
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    # Lê o arquivo CSV e transforma cada linha em um dicionário e depois em um objeto
    # Devolve True se carregou alguma orientação e False se deu problema
    def carregar(self):
        self.orientacoes = []
        linhas_invalidas = 0

        # Se o arquivo não existir, o programa avisa e continua rodando
        try:
            arquivo = open(self.caminho, "r", encoding="utf-8-sig")
        except OSError:
            print("Aviso: não consegui abrir a base de conhecimento em '" + self.caminho + "'.")
            return False

        primeira_linha = True
        for linha in arquivo:
            # A primeira linha é o cabeçalho, então pulamos
            if primeira_linha:
                primeira_linha = False
                continue
            linha = linha.strip()
            if linha == "":
                continue

            campos = linha.split(";")
            # Linha com quantidade errada de campos é ignorada
            if len(campos) != TOTAL_CAMPOS:
                linhas_invalidas += 1
                continue

            # Primeiro guardamos os dados em um dicionário
            try:
                registro = {
                    "id": int(campos[0]),
                    "categoria": campos[1].strip(),
                    "titulo": campos[2].strip(),
                    "palavras_chave": self.separar_itens(campos[3]),
                    "resposta": campos[4].strip(),
                    "documentos": self.separar_itens(campos[5]),
                    "onde": self.separar_itens(campos[6]),
                    "fonte": campos[7].strip(),
                    "verificado_em": campos[8].strip(),
                }
            except ValueError:
                # Acontece quando o id não é um número
                linhas_invalidas += 1
                continue

            # Depois criamos o objeto Orientacao com os dados do dicionário
            orientacao = Orientacao(registro["id"], registro["categoria"],
                                    registro["titulo"], registro["palavras_chave"],
                                    registro["resposta"], registro["documentos"],
                                    registro["onde"], registro["fonte"],
                                    registro["verificado_em"])
            self.orientacoes.append(orientacao)
        arquivo.close()

        if linhas_invalidas > 0:
            print("Aviso: " + str(linhas_invalidas) + " linha(s) da base foram ignoradas por formato inválido.")
        if len(self.orientacoes) == 0:
            print("Aviso: a base de conhecimento está vazia.")
            return False

        print("Base carregada: " + str(len(self.orientacoes)) + " orientações em "
              + str(len(self.categorias())) + " categorias.")
        return True

    # Separa campos com vários itens (ex.: "RG|CPF") e devolve uma lista limpa
    def separar_itens(self, texto):
        itens = []
        for parte in texto.split("|"):
            parte = parte.strip()
            if parte != "":
                itens.append(parte)
        return itens

    # Devolve a lista de categorias sem repetir nenhuma
    def categorias(self):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    # Devolve só as orientações de uma categoria
    def por_categoria(self, categoria):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria == categoria:
                lista.append(orientacao)
        return lista

    # Calcula quantos pontos uma orientação ganha para uma pergunta
    # Regra 1: cada palavra-chave que aparece na pergunta vale +3
    # Regra 2: cada palavra da pergunta (4+ letras) que aparece no título vale +1
    def pontuar(self, pergunta, orientacao):
        pontos = 0
        texto = normalizar(pergunta)

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in texto:
                pontos = pontos + 3

        titulo = normalizar(orientacao.titulo)
        palavras_vistas = []
        for palavra in texto.split():
            # Cada palavra só conta uma vez, mesmo se repetida na pergunta
            if palavra in palavras_vistas:
                continue
            palavras_vistas.append(palavra)
            if len(palavra) >= 4 and (" " + palavra + " ") in titulo:
                pontos = pontos + 1
        return pontos

    # Compara a pergunta com todas as orientações
    # Devolve uma lista de tuplas (pontos, orientacao) da maior para a menor pontuação
    # Só entram na lista as orientações com 3 pontos ou mais
    def buscar(self, pergunta):
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos >= 3:
                resultados.append((pontos, orientacao))

        # Ordenação simples (bubble sort): troca vizinhos até ficar do maior para o menor
        total = len(resultados)
        for i in range(total):
            for j in range(0, total - i - 1):
                if resultados[j][0] < resultados[j + 1][0]:
                    resultados[j], resultados[j + 1] = resultados[j + 1], resultados[j]
        return resultados
