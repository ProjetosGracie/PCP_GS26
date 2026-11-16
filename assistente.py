# Arquivo: assistente.py
# Aqui fica a classe Assistente: ela conversa com o cidadão, guarda o histórico,
# calcula os indicadores e exporta o CSV.

import time
from datetime import datetime

# Caminhos dos arquivos de dados (todos dentro da pasta Datasets)
ARQ_HISTORICO = "Datasets/historico.csv"
ARQ_ATENDIMENTOS = "Datasets/atendimentos.csv"
ARQ_NOTAS = "Datasets/notas.csv"

# Primeira linha dos arquivos CSV
CABECALHO_HISTORICO = "data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo_segundos"
CABECALHO_NOTAS = "data;nota"


# ----- Funções auxiliares para arquivos (usadas pela classe) -----

# Garante que o arquivo existe. Se não existir, cria com o cabeçalho.
# Devolve True se o arquivo está pronto e False se não foi possível criar.
def garantir_arquivo(caminho, cabecalho):
    try:
        arquivo = open(caminho, "r", encoding="utf-8")
        arquivo.close()
        return True
    except FileNotFoundError:
        try:
            arquivo = open(caminho, "w", encoding="utf-8")
            arquivo.write(cabecalho + "\n")
            arquivo.close()
            return True
        except OSError:
            return False
    except OSError:
        return False


# Adiciona uma linha no final de um arquivo CSV (modo "a" = append)
def gravar_linha(caminho, cabecalho, linha):
    if not garantir_arquivo(caminho, cabecalho):
        print("Aviso: não consegui criar o arquivo " + caminho + ".")
        return
    try:
        arquivo = open(caminho, "a", encoding="utf-8")
        arquivo.write(linha + "\n")
        arquivo.close()
    except OSError:
        print("Aviso: não consegui gravar no arquivo " + caminho + ".")


# Transforma um registro (dicionário) em uma linha de texto separada por ;
def registro_para_linha(r):
    campos = [r["data"], r["origem"], r["pergunta"], str(r["id"]), r["encontrou"],
              r["ajudou"], str(r["tentativas"]), str(r["tempo"])]
    return ";".join(campos)


class Assistente:
    # nome = nome do assistente | base = objeto BaseConhecimento (composição)
    # historico = lista de dicionários, um por atendimento | notas = lista de notas de 1 a 5
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.notas = []
        self.carregar_historico()
        self.carregar_notas()

    # ----- Leitura de arquivos salvos em execuções anteriores -----

    # Lê o historico.csv para que os indicadores somem os testes de vários dias
    def carregar_historico(self):
        garantir_arquivo(ARQ_HISTORICO, CABECALHO_HISTORICO)
        try:
            arquivo = open(ARQ_HISTORICO, "r", encoding="utf-8-sig")
        except OSError:
            print("Aviso: não consegui ler o histórico. Vou começar do zero.")
            return
        primeira_linha = True
        for linha in arquivo:
            if primeira_linha:
                primeira_linha = False
                continue
            campos = linha.strip().split(";")
            # Linha com formato errado é ignorada
            if len(campos) != 8:
                continue
            try:
                registro = {"data": campos[0], "origem": campos[1], "pergunta": campos[2],
                            "id": int(campos[3]), "encontrou": campos[4], "ajudou": campos[5],
                            "tentativas": int(campos[6]), "tempo": float(campos[7])}
            except ValueError:
                continue
            self.historico.append(registro)
        arquivo.close()

    # Lê o notas.csv (notas de facilidade de uso dadas ao sair)
    def carregar_notas(self):
        garantir_arquivo(ARQ_NOTAS, CABECALHO_NOTAS)
        try:
            arquivo = open(ARQ_NOTAS, "r", encoding="utf-8-sig")
        except OSError:
            return
        primeira_linha = True
        for linha in arquivo:
            if primeira_linha:
                primeira_linha = False
                continue
            campos = linha.strip().split(";")
            if len(campos) != 2:
                continue
            try:
                nota = int(campos[1])
            except ValueError:
                continue
            if 1 <= nota <= 5:
                self.notas.append(nota)
        arquivo.close()

    # ----- Entradas do usuário (sempre validadas) -----

    # Pede um número inteiro entre minimo e maximo. Repete até a pessoa acertar.
    def ler_numero(self, texto, minimo, maximo):
        while True:
            resposta = input(texto).strip()
            if resposta == "":
                print("Atenção: você não digitou nada.")
                continue
            try:
                numero = int(resposta)
            except ValueError:
                print("Atenção: digite apenas números.")
                continue
            if numero < minimo or numero > maximo:
                print("Atenção: escolha um número entre " + str(minimo) + " e " + str(maximo) + ".")
                continue
            return numero

    # Pede s ou n. Devolve "s" ou "n". Repete até a resposta ser válida.
    def ler_sim_nao(self, texto):
        while True:
            resposta = input(texto).strip().lower()
            if resposta in ["s", "sim"]:
                return "s"
            if resposta in ["n", "nao", "não"]:
                return "n"
            print("Atenção: responda apenas com s (sim) ou n (não).")

    # Verifica se o texto tem dado pessoal: 8 ou mais dígitos ou o símbolo @
    def tem_dado_pessoal(self, texto):
        digitos = 0
        for letra in texto:
            if letra.isdigit():
                digitos = digitos + 1
        if digitos >= 8 or "@" in texto:
            return True
        return False

    # ----- Menu principal -----

    def menu(self):
        print("\nOlá! Eu sou o " + self.nome + ", um assistente de orientação ao cidadão.")
        print("Público: pessoas idosas e seus familiares.")
        print("Importante: nunca digite nome, CPF, telefone ou e-mail.")
        while True:
            print("\n===== " + self.nome + " =====")
            print("1 - Fazer uma pergunta")
            print("2 - Navegar por categorias")
            print("3 - Ver indicadores")
            print("4 - Exportar atendimentos para CSV")
            print("0 - Sair")
            opcao = self.ler_numero("Escolha uma opção: ", 0, 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.encerrar()
                break

    # ----- Atendimento por pergunta em texto livre -----

    # Repete atendimentos até a pessoa digitar 0 para voltar ao menu
    def perguntar(self):
        voltar = False
        while not voltar:
            voltar = self.atendimento_pergunta()

    # Faz UM atendimento completo. Devolve True se a pessoa quer voltar ao menu.
    def atendimento_pergunta(self):
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        id_orientacao = 0
        encontrou = "n"
        ajudou = "n"

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            # 0 = voltar. Se já houve tentativas, o atendimento é registrado
            if pergunta == "0":
                if tentativas > 0:
                    tempo = round(time.time() - inicio, 1)
                    self.registrar("pergunta", ultima_pergunta, id_orientacao,
                                   encontrou, ajudou, tentativas, tempo)
                return True

            # Entrada vazia nunca encerra o programa
            if pergunta == "":
                print("Atenção: você não digitou nada. Escreva sua dúvida.")
                continue

            # Dado pessoal é recusado e NÃO é registrado
            if self.tem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas = tentativas + 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)

            # Nenhuma orientação com 3 pontos: sugere outras palavras ou categorias
            if len(resultados) == 0:
                encontrou = "n"
                ajudou = "n"
                id_orientacao = 0
                self.mostrar_nao_encontrei()
                continue

            # Achou: mostra a melhor orientação e até duas alternativas
            encontrou = "s"
            pontos, melhor = resultados[0]
            print("\nConfiança da resposta: " + self.confianca(pontos) + " (" + str(pontos) + " pontos)")
            melhor.exibir()
            id_orientacao = melhor.id

            alternativas = resultados[1:3]
            if len(alternativas) > 0:
                print("\nOutras orientações parecidas:")
                for i in range(len(alternativas)):
                    pontos_alt, orientacao_alt = alternativas[i]
                    print("  " + str(i + 1) + " - " + orientacao_alt.resumo()
                          + " (" + str(pontos_alt) + " pontos)")

            ajudou, id_orientacao = self.perguntar_se_ajudou(alternativas, id_orientacao)
            if ajudou == "s":
                tempo = round(time.time() - inicio, 1)
                self.registrar("pergunta", ultima_pergunta, id_orientacao,
                               encontrou, ajudou, tentativas, tempo)
                return False

    # Pergunta se a orientação ajudou. Se não ajudou, oferece as alternativas.
    # Devolve ("s" ou "n", id da última orientação mostrada)
    def perguntar_se_ajudou(self, alternativas, id_atual):
        resposta = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
        while resposta == "n" and len(alternativas) > 0:
            escolha = self.ler_numero("Digite o número de uma alternativa (0 para reescrever a pergunta): ",
                                      0, len(alternativas))
            if escolha == 0:
                break
            orientacao = alternativas[escolha - 1][1]
            orientacao.exibir()
            id_atual = orientacao.id
            resposta = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
        return resposta, id_atual

    # Devolve o nível de confiança conforme os pontos
    def confianca(self, pontos):
        if pontos >= 6:
            return "ALTA"
        return "MÉDIA"

    # Mensagem mostrada quando nenhuma orientação foi encontrada
    def mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras (ex.: cartão SUS, aposentadoria, ônibus, golpe).")
        categorias = self.base.categorias()
        if len(categorias) > 0:
            print("Ou use a opção 2 do menu e navegue pelas categorias: " + ", ".join(categorias) + ".")

    # ----- Atendimento por navegação em categorias -----

    # Mostra as categorias numeradas. 0 volta ao menu.
    def navegar(self):
        while True:
            categorias = self.base.categorias()
            if len(categorias) == 0:
                print("\nA base de conhecimento está vazia. Não há categorias para mostrar.")
                return
            print("\n===== Categorias =====")
            for i in range(len(categorias)):
                print(str(i + 1) + " - " + categorias[i])
            print("0 - Voltar")
            escolha = self.ler_numero("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            self.navegar_orientacoes(categorias[escolha - 1])

    # Mostra as orientações de uma categoria. 0 volta às categorias.
    def navegar_orientacoes(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print("\n===== " + categoria + " =====")
            for i in range(len(orientacoes)):
                print(str(i + 1) + " - " + orientacoes[i].titulo)
            print("0 - Voltar")
            inicio = time.time()
            escolha = self.ler_numero("Escolha uma orientação: ", 0, len(orientacoes))
            if escolha == 0:
                return
            orientacao = orientacoes[escolha - 1]
            orientacao.exibir()
            ajudou = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", "Categoria: " + orientacao.titulo, orientacao.id,
                           "s", ajudou, 1, tempo)

    # ----- Histórico, indicadores e exportação -----

    # Guarda o atendimento na lista e no arquivo historico.csv
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        # O ; e a quebra de linha quebrariam o CSV, então trocamos
        pergunta = pergunta.replace(";", ",").replace("\n", " ")
        registro = {"data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "origem": origem, "pergunta": pergunta, "id": id_orientacao,
                    "encontrou": encontrou, "ajudou": ajudou,
                    "tentativas": tentativas, "tempo": tempo}
        self.historico.append(registro)
        gravar_linha(ARQ_HISTORICO, CABECALHO_HISTORICO, registro_para_linha(registro))

    # Calcula e mostra os indicadores. Também devolve os valores em um dicionário.
    def indicadores(self):
        print("\n===== Indicadores =====")
        total = len(self.historico)
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return {}

        encontrados = 0
        ajudaram = 0
        soma_tempo = 0.0
        soma_tentativas = 0
        sem_solucao = []

        for r in self.historico:
            if r["encontrou"] == "s":
                encontrados = encontrados + 1
                soma_tempo = soma_tempo + r["tempo"]
            if r["ajudou"] == "s":
                ajudaram = ajudaram + 1
            elif r["pergunta"] not in sem_solucao:
                sem_solucao.append(r["pergunta"])
            soma_tentativas = soma_tentativas + r["tentativas"]

        pct_encontrada = encontrados / total * 100
        pct_ajudou = ajudaram / total * 100
        tentativas_media = soma_tentativas / total
        if encontrados > 0:
            tempo_medio = soma_tempo / encontrados
        else:
            tempo_medio = 0.0

        print("Total de atendimentos: " + str(total))
        print("Resposta encontrada: " + str(round(pct_encontrada, 1)) + "%")
        print("Taxa de acerto (ajudou): " + str(round(pct_ajudou, 1)) + "%")
        print("Tempo médio para encontrar: " + str(round(tempo_medio, 1)) + " s")
        print("Tentativas por atendimento: " + str(round(tentativas_media, 1)))

        if len(self.notas) > 0:
            media_nota = sum(self.notas) / len(self.notas)
            print("Facilidade de uso (1 a 5): " + str(round(media_nota, 1)))
        else:
            media_nota = 0
            print("Facilidade de uso (1 a 5): ainda sem notas")

        print("Dúvidas sem solução:")
        if len(sem_solucao) == 0:
            print("  (nenhuma)")
        for duvida in sem_solucao:
            print("  - " + duvida)

        return {"total": total, "encontrada": pct_encontrada, "acerto": pct_ajudou,
                "tempo_medio": tempo_medio, "tentativas": tentativas_media,
                "facilidade": media_nota, "sem_solucao": sem_solucao}

    # Escreve todos os atendimentos em Datasets/atendimentos.csv (um por linha, separados por ;)
    def exportar_csv(self):
        try:
            arquivo = open(ARQ_ATENDIMENTOS, "w", encoding="utf-8")
            arquivo.write(CABECALHO_HISTORICO + "\n")
            for r in self.historico:
                arquivo.write(registro_para_linha(r) + "\n")
            arquivo.close()
            print("\nAtendimentos exportados para " + ARQ_ATENDIMENTOS
                  + " (" + str(len(self.historico)) + " registros).")
        except OSError:
            print("\nAviso: não consegui exportar o arquivo " + ARQ_ATENDIMENTOS + ".")

    # ----- Saída -----

    # Pede a nota de facilidade, exporta o CSV e mostra os indicadores finais
    def encerrar(self):
        print("\nAntes de sair, avalie a facilidade de uso do assistente.")
        nota = self.ler_numero("Nota de 1 (muito difícil) a 5 (muito fácil): ", 1, 5)
        self.notas.append(nota)
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gravar_linha(ARQ_NOTAS, CABECALHO_NOTAS, data + ";" + str(nota))
        self.exportar_csv()
        self.indicadores()
        print("\nObrigado por usar o " + self.nome + ". Até logo!")
