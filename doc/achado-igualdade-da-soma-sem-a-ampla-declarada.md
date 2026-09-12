# A `014` criou o campo que fecharia a `R-006`, e a igualdade da soma não o lê

**Data:** 2026-09-12
**Origem:** revisão das implementações recentes, sobre `daded41` — a `main` com a `014` integrada
(PR #105). Nenhuma linha de código foi escrita.
**Natureza:** a lacuna é a mesma que a `R-006` da `025` registrou; o que mudou é o **custo de
fechá-la**, e é só isso que este documento acrescenta.

> **Não vira escopo por estar escrito aqui.** A `R-006` nomeou duas saídas e disse que a escolha é
> do usuário; a `014` tomou a primeira **para outro fim**, e a consequência para a conferência da
> `025` não foi decidida por ninguém. Continua sendo decisão sua.

## O que a `R-006` registrou

A `FR-161` da `025` define quadro completo como *linha geral e uma linha para cada Modalidade
declarada no Perfil*, e só então confere a **igualdade** da soma contra o total. A `FR-176` proíbe
dar linha reservada à Modalidade que serve de ampla concorrência, porque a quantidade dela mora na
linha geral. No Edital do formato normal — o que declara uma Modalidade *chamada* "Ampla
concorrência" — as duas se encontram: uma Modalidade fica sem linha, o quadro nunca é completo, e a
igualdade nunca roda.

A pesquisa da `025` recusou por escrito identificar a ampla concorrência **casando o nome**, e a
recusa continua certa. Ela deixou duas saídas:

1. o Perfil declarar **explicitamente** qual Modalidade é a ampla concorrência — campo novo, degrau
   novo; ou
2. redefinir completude como *linha geral presente e no máximo uma Modalidade sem linha* — barato e
   frouxo.

## O que a `014` fez

A `014` precisou da **mesma** informação, por outro caminho: a `D-014` exige linha de quadro para
todo recorte que o marco ordena, e a implementação descobriu que exigir linha de *toda* Modalidade
tornava impublicável o Edital do formato normal. A saída adotada foi a **saída 1** — e está entregue:

| | |
|---|---|
| campo no conteúdo publicado | `generalCompetitionModalityId`, no Perfil (`FR-231`) |
| modelo | `PerfilVaga.modalidade_ampla_concorrencia` (`editais/migrations/0018_ampla_concorrencia_declarada.py`) |
| alcançável por Retificação | `interface/retificacao.py:55` |
| coerência do que aponta | `_ampla_concorrencia_declarada` (`editais/domain/validation.py:929`) |

O campo é **opcional** (`validation.py:85`, `admite_nulo=True`), e a coerência dele proíbe dar linha
à Modalidade declarada — exatamente o que a `FR-176` já dizia.

## A assimetria, medida

As duas conferências olham o mesmo Perfil e só uma lê o campo novo. Medido em `daded41`, chamando
as duas funções diretamente com um Perfil de 80 vagas que declara `AC`, `PPI` e `PCD`, quadro
`55 + 20 + 4 = 79` na linha geral e nas duas cotas:

```
                                                     conferência da soma (025)
AC declarada     · soma 79 contra 80 (conservador) -> PASSA
AC declarada     · soma 81 contra 80 (perigoso)    -> vacancy_sum_exceeds_total
AC não declarada · soma 79 contra 80               -> PASSA

                                                     alvo derivado do corte (014)
alvo derivado · AC declarada                       -> PASSA
alvo derivado · AC não declarada                   -> cut_rule_sem_linha_de_quadro
    "A regra de corte do marco M1 deriva o alvo do quadro de vagas, e não há
     linha para Ampla concorrência."
```

A causa é uma linha só. `_quadro_para_o_corte` lê `generalCompetitionModalityId`
(`validation.py:907`) e tira a Modalidade declarada da lista de recortes exigidos.
`_coerencia_do_quadro_de_vagas` **nunca** o lê: a completude dela continua sendo

```python
elif tem_linha_geral and not (set(modalidades) - com_linha) and soma != total:
```

em `validation.py:1478`, e a Modalidade declarada como ampla concorrência está em `modalidades` e
nunca em `com_linha` — porque a `014` proíbe que ela tenha linha. **Seguir a `D-014` garante que o
conjunto nunca fique vazio**, e a igualdade fica inerte no formato que a spec chama de normal.

O que continua rodando é o **limite superior** da `FR-177`, que não identifica Modalidade nenhuma:
o `PPI 200` digitado no lugar de `20` é recusado. Passa o erro conservador — o quadro que soma
menos que o total —, que é o esquecimento de cota.

## Por que o custo mudou

A `R-006` mediu a saída 1 como *"campo novo, degrau novo, e a reconciliação das duas grafias que a
§7 adiou"*. **Esse preço está pago.** O campo existe, viaja no conteúdo publicado, tem caminho de
Retificação e tem coerência verificada; e a reconciliação de grafias não foi necessária, porque a
identidade declarada substitui a heurística de nome.

E há um ponto mais estreito: quando o marco declara **alvo derivado do quadro**, a `014` já
**obriga** a declaração — sem ela a publicação é recusada nomeando "Ampla concorrência". Isto é,
existe hoje uma classe de Editais em que o campo é garantidamente presente, e em que a igualdade da
soma continua ignorando-o.

## O que continua aberto

A lacuna, na forma que a `025` descreveu: um quadro somando `79` contra `80` publica sem
advertência de divergência, no formato normal de Edital. O teste que a registra continua passando e
continua dizendo a verdade:

```
tests/interface/test_compor_quadro.py::test_a_igualdade_nao_roda_onde_uma_modalidade_fica_sem_linha
```

O docstring de `_coerencia_do_quadro_de_vagas` (`validation.py:1372`) ainda aponta para a `R-006`
como o que sobra, e a `research.md` da `025` ainda lista as duas saídas como não tomadas — o que é
verdade sobre aquela feature e deixou de ser verdade sobre o repositório.

## Os caminhos, sem escolher nenhum

1. **Ligar o campo na completude da `025`.** Excluir a Modalidade declarada do conjunto exigido, do
   mesmo modo que `_quadro_para_o_corte` já faz. Fecha a lacuna onde o Edital declara, não inventa
   nada onde ele não declara, e não toca o conteúdo publicado nem o esquema canônico. **É uma
   conferência de publicação que passa a recusar o que hoje passa** — e por isso não é mudança de
   código sem decisão: um Edital em elaboração que hoje publica passaria a ser recusado, e a
   pergunta de quem decide é se essa recusa é desejada.
2. **Exigir a declaração sempre que houver quadro**, e não só sob alvo derivado. Fecharia a lacuna
   inteira em vez de onde o Edital colabora, ao custo de tornar obrigatório um campo que nasceu
   opcional — o que alcança o acervo em elaboração e pede caminho de leitura.
3. **A saída 2 da `R-006`** — completude como *no máximo uma Modalidade sem linha*. Continua
   disponível, continua barata, e continua deixando passar o esquecimento genuíno de uma cota. Com
   o campo existindo, ela é agora a saída que **adivinha** onde há informação declarada.
4. **Deixar como está.** O limite superior da `FR-177` segue pegando a direção perigosa, e a
   advertência do percentual segue valendo linha a linha. O que passa é o quadro conservador, e
   quem confere é quem lê o documento.

Enquanto não houver decisão, o que é verdade: a igualdade da `FR-161` roda apenas em Perfil cuja
única Modalidade declarada tem linha — e o Edital do formato normal não é um deles.
