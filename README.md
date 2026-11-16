# Citizen Assist AI — Assistente Digital de Orientação ao Cidadão

**Global Solution GS2026.2 — Pensamento Computacional e Automação com Python (FIAP)**

## 1. Integrantes

| Nome | RM |
|------|----|
| Conrado Gracie | 569157 |
| Renato Sandreschi | 569156 |

## 2. Público e problema escolhidos

- **Público:** pessoas idosas e seus familiares.
- **Problema:** a informação sobre Cartão SUS, aposentadoria, transporte gratuito ou golpes existe, mas está espalhada, em linguagem técnica e misturada com páginas falsas. O Citizen Assist AI responde em linguagem simples, **sempre mostrando a fonte oficial, a data de verificação e o aviso de que não é um canal oficial**, e **sem coletar dados pessoais**.

## 3. ODS relacionados

- **ODS 3** – Saúde e Bem-Estar (Cartão SUS, vacinas, remédios, SAMU).
- **ODS 10** – Redução das Desigualdades (acesso a benefícios e gratuidades).
- **ODS 16** – Paz, Justiça e Instituições Eficazes (informação confiável, denúncia e proteção contra golpes).

## 4. Como executar

Requisitos: Python 3.8 ou superior. Nenhuma biblioteca externa (usa apenas `time` e `datetime`).

```
cd citizen-assist-ai
python main.py
```

> Execute **dentro da pasta do projeto**, pois os caminhos (`Datasets/...`) são relativos.

## 5. Como usar (passo a passo)

Ao abrir, o menu aparece:

| Opção | O que faz |
|-------|-----------|
| 1 | **Fazer uma pergunta** em texto livre (ex.: *Como faço o cartão do SUS?*). Digite `0` para voltar. |
| 2 | **Navegar por categorias**: escolha uma categoria e depois uma orientação. `0` volta em todas as telas. |
| 3 | **Ver indicadores** (percentuais, tempo médio, dúvidas sem solução). |
| 4 | **Exportar** os atendimentos para `Datasets/atendimentos.csv`. |
| 0 | **Sair**: pede uma nota de facilidade de 1 a 5, exporta o CSV e mostra os indicadores. |

Depois de cada resposta o assistente pergunta *"Essa orientação respondeu sua dúvida? (s/n)"*. Se a resposta for **n**, ele oferece as alternativas ou você pode reescrever a pergunta.

**Entradas inválidas** (letras, número fora da faixa, vazio, s/n inválido) apenas geram um aviso e a pergunta é repetida; o programa nunca fecha por erro.
**Dados pessoais:** pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.

## 6. Estrutura do projeto

```
citizen-assist-ai/
├── README.md              (este relatório)
├── main.py                (ponto de partida do programa)
├── orientacao.py          (classe Orientacao)
├── base_conhecimento.py   (função normalizar + classe BaseConhecimento)
├── assistente.py          (classe Assistente)
└── Datasets/
    ├── base_conhecimento.csv   (14 orientações, 5 categorias)
    ├── historico.csv           (um registro por atendimento, gravado na hora)
    ├── atendimentos.csv        (exportação dos atendimentos)
    └── notas.csv               (notas de facilidade dadas ao sair)
```

## 7. Como o código funciona

### Visão geral (composição)

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

O `Assistente` **tem uma** `BaseConhecimento`, que **tem uma lista** de objetos `Orientacao`. Isso se chama **composição**.

### `main.py`
Cria a base, chama `carregar()`, cria o assistente e chama `menu()`. Se a pessoa apertar Ctrl+C, o programa se despede sem erro.

### `orientacao.py` — classe `Orientacao` (um registro do CSV)

| Item | Função |
|------|--------|
| `__init__` | Guarda os 9 atributos: id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em. |
| `exibir()` | Mostra título, resposta, documentos, onde ir, fonte, data de verificação e o aviso. |
| `resumo()` | Devolve uma linha curta ("Título [Categoria]") para listas. |

### `base_conhecimento.py`

| Item | Função |
|------|--------|
| `normalizar(texto)` | Deixa o texto em minúsculas, sem acentos e sem pontuação. |
| `carregar()` | Lê o CSV com `open()`, `for` e `split(";")`. Cada linha vira um **dicionário** e depois um objeto `Orientacao`. Arquivo ausente ou linha com formato errado gera aviso, nunca erro. |
| `separar_itens()` | Separa campos com vários itens usando `split("\|")`. |
| `categorias()` | Lista as categorias sem repetir. |
| `por_categoria()` | Devolve as orientações de uma categoria. |
| `pontuar()` | Calcula os pontos de uma orientação para uma pergunta. |
| `buscar()` | Pontua todas e devolve **lista de tuplas** `(pontos, orientacao)` da maior para a menor (ordenação *bubble sort*). |

### `assistente.py` — classe `Assistente`

| Método | Função |
|--------|--------|
| `menu()` | Menu principal. |
| `perguntar()` / `atendimento_pergunta()` | Faz atendimentos por texto livre; conta tentativas e mede o tempo com `time.time()`. |
| `perguntar_se_ajudou()` | Pergunta s/n e oferece alternativas se não ajudou. |
| `navegar()` / `navegar_orientacoes()` | Navegação por categorias, com "0 para voltar". |
| `registrar()` | Guarda o atendimento na lista `historico` e no `historico.csv`. |
| `indicadores()` | Calcula e mostra os indicadores. |
| `exportar_csv()` | Escreve `atendimentos.csv` com `open()` e `write()`. |
| `ler_numero()`, `ler_sim_nao()` | Leem a entrada e repetem até ser válida (`try/except`). |
| `tem_dado_pessoal()` | Detecta 8+ dígitos ou `@`. |
| `encerrar()` | Pede a nota (1 a 5), exporta e mostra os indicadores. |

Funções soltas em `assistente.py`: `garantir_arquivo()` (cria o arquivo com cabeçalho se não existir), `gravar_linha()` e `registro_para_linha()`.

## 8. Regra de pontuação

| Regra | Resultado |
|-------|-----------|
| Palavra-chave da orientação que aparece na pergunta | +3 pontos |
| Palavra da pergunta (4+ letras) que aparece no título | +1 ponto (cada palavra conta uma vez) |
| Melhor orientação com 6 pontos ou mais | Confiança **ALTA** |
| Melhor orientação com 3 a 5 pontos | Confiança **MÉDIA** |
| Nenhuma orientação com 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

**Exemplo:** *"Como faço o cartão do SUS?"* → `cartao` (+3), `sus` (+3), e "cartao" no título (+1) = **7 pontos, ALTA**.
O assistente mostra a melhor orientação e até **2 alternativas**. Os pesos e limites são os do enunciado, sem alterações.

## 9. Base de conhecimento (CSV)

Cabeçalho: `id;categoria;titulo;palavras_chave;resposta;documentos;onde;fonte;verificado_em`

- Campos separados por `;`. Itens múltiplos separados por `|`. **Nunca use `;` dentro do texto.**
- **Como adicionar uma palavra-chave:** abra `Datasets/base_conhecimento.csv`, vá até a linha da orientação e acrescente `|palavra` no quarto campo. Salve e rode o programa novamente.
- Para criar uma nova orientação, copie uma linha, mude o `id` e preencha os 9 campos (fonte oficial e data de verificação são obrigatórias).

## 10. Histórico e indicadores

Cada atendimento é gravado em `Datasets/historico.csv` com: `data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo_segundos`.
Ao abrir o programa, o histórico anterior é lido, então os indicadores somam todos os testes.

| Indicador | Como é calculado |
|-----------|------------------|
| Resposta encontrada (%) | atendimentos em que achou orientação ÷ total |
| Taxa de acerto (%) | atendimentos em que a pessoa respondeu **s** ÷ total |
| Tempo médio para encontrar | média do tempo dos atendimentos em que achou |
| Tentativas por atendimento | média de perguntas digitadas por atendimento |
| Facilidade de uso | média das notas (1 a 5) dadas ao sair |
| Dúvidas sem solução | perguntas de atendimentos em que a pessoa respondeu **n** |

## 11. Integrações com outras disciplinas

Nenhuma. O projeto usa somente a busca por pontuação exigida.

## 12. Fontes consultadas

Os sites oficiais usados na base (campo `fonte` do CSV):

- https://www.gov.br/saude
- https://meu.inss.gov.br
- https://www.gov.br/inss
- https://www.gov.br/mds
- https://www.gov.br/mdh
- https://www.gov.br/antt
- https://www.gov.br/receitafederal
- https://www.gov.br
- https://www.consumidor.gov.br

Data de verificação registrada na base: **2026-11-13**.

## 13. Teste com usuários

> Preencher após testar com **3 ou mais pessoas de fora da equipe (10 atendimentos ou mais)**. Não registrar nomes nem dados pessoais.

| Indicador | Resultado |
|-----------|-----------|
| Pessoas testadas | 3 |
| Total de atendimentos | 11 |
| Resposta encontrada (%) | 100 |
| Taxa de acerto (%) | 90.9 |
| Tempo médio para encontrar | 59.3s |
| Tentativas por atendimento | 1.6 |
| Facilidade de uso (1 a 5) | 4.2 |

- **Melhoria feita a partir do teste:** Documentos: CNH 

## 14. Limitações

- A busca compara palavras exatas: erros de digitação e plurais não listados nas palavras-chave não são entendidos.
- A base tem 14 orientações e as regras (idade, renda, prazos) podem mudar; o aviso e a data de verificação mostram isso ao usuário.
- Algumas regras variam por cidade (ex.: cartão de gratuidade no ônibus), então a resposta orienta, mas não substitui o atendimento oficial.
- Os caminhos dos arquivos são relativos: o programa deve ser executado dentro da pasta do projeto.
- O assistente **não é canal oficial**.
