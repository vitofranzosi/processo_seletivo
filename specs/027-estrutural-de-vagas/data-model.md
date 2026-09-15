# Modelo — 027 · Estrutural de vagas

Fase 1. **Nenhuma entidade nasce, nenhuma muda de forma.** Este documento existe para dizer o que
muda no *significado* do que já existe, e onde cada regra passa a morar.

---

## 1 · O que não muda

| Entidade | Situação |
|---|---|
| `PerfilVaga.immediate_vacancies` | continua declarado por quem compõe, continua sendo o total, continua sem ser calculado a partir de coisa alguma (`FR-320`) |
| `LinhaDoQuadroDeVagas` | mesma tabela, mesmas colunas, mesmas duas constraints parciais. A linha geral continua sendo a de `modalidade` nulanula. **Linha** é o que o quadro escreve; **lista** é a Modalidade sobre a qual ele escreve (`FR-317`) |
| `ModalidadeConcorrencia` | inalterada |
| `PerfilVaga.modalidade_ampla_concorrencia` | inalterado, e passa a ter uma segunda consequência: é ele que decide o que é lista reservada |
| Conteúdo publicado (`vacancyTable`, `generalCompetitionModalityId`) | mesma forma, mesmo degrau. **Sem migration e sem conversão** |

---

## 2 · O conceito que esta feature acrescenta: lista reservada

Não é campo nem tabela — é uma leitura, e vive numa função.

```
listas_reservadas(perfil) = { Modalidades declaradas } − { a declarada como ampla concorrência }
```

Três consequências, e as três são requisito:

1. **Se o conjunto é vazio**, o Perfil tem exatamente uma lista de concorrência, e a linha geral é a
   projeção do total (`FR-318`).
2. **Se não é vazio**, o quadro reparte, e a repartição é declarada (`FR-321`).
3. **A completude do quadro passa a descontar a ampla declarada** — é o que faz a conferência de
   igualdade da `025` finalmente rodar no formato comum ([research.md](research.md), `T-002`).

**O que a função não faz:** casar denominação. Um Perfil que declare uma Modalidade chamada "Ampla
concorrência" e não a aponte tem, para o sistema, duas listas reservadas — e é sobre isso que a
`FR-325` adverte.

---

## 3 · A derivação, como regra

Função pura sobre a carga do Perfil, aplicada antes de persistir:

```
para cada Perfil da carga:
    se listas_reservadas(perfil) == ∅:
        garantir exatamente uma linha geral, com quantidade = immediateVacancies
        preservando o `id` que chegou, ou criando um se não houver
```

| Propriedade | Por quê |
|---|---|
| **Idempotente** | gravar duas vezes a mesma carga produz o mesmo conteúdo, e o mesmo resumo canônico |
| **Preserva identidade** | é por ela que a Retificação alcança a linha depois de publicada (`T-001`) |
| **Reafirma a quantidade** | é o que faz a `FR-322` valer quando a última lista reservada é removida |
| **Não toca no total** | `FR-320`. A projeção tem uma direção só |
| **Aplicada no command, e não na tela** | é o que faz a regra valer para a API (`FR-316`) |

**Onde ela não roda:** sobre conteúdo publicado. A Retificação não passa por aqui, e é por isso que o
acervo fica como está (`FR-330`, `FR-333`).

---

## 4 · Os achados que a validação passa a produzir

| Código | Severidade | Quando | Requisito |
|---|---|---|---|
| `vacancy_general_row_missing` | **impeditivo, no ato de publicação** | Perfil sem linha geral | `FR-323` |
| `vacancy_reserved_list_without_row` | advertência | lista reservada sem linha, uma por lista, dita em números | `FR-324` |
| `general_competition_modality_undeclared` | advertência | Perfil declara Modalidade e não declara qual é a da ampla | `FR-325` |
| `vacancy_table_absent_in_archive` | **advertência, e só no ato de Retificação** | Perfil publicado que declara vaga imediata e não publica quadro nenhum | `FR-332`, `FR-335` |

Os três seguem a forma que `validation.py` já usa: código, mensagem em português com os números
dentro, e caminho que `interface/views._destino` traduz para a etapa que resolve.

**A severidade do primeiro depende do ato conferido**, e é a armadilha nomeada em `T-003`: no ato de
Retificação ele não é produzido, porque o acervo inteiro o dispararia e nenhuma Retificação passaria.

**E o quarto é o espelho dele**, acrescentado na execução: a mesma ausência que é impedimento ao
publicar Edital novo é, no acervo, a condição normal — e ali ela vira o aviso que **nomeia o ato**.
Os dois nunca coexistem, porque cada um só existe no ato em que o outro se cala.

---

## 5 · O sinal do acervo

Sexta espécie do catálogo de `interface/supervisao.py`, na forma que as cinco já têm:

| Campo | Conteúdo |
|---|---|
| `especie` | a espécie nova, na ordem do catálogo |
| `edital` | o Edital publicado |
| `alvo` | o Perfil |
| `mensagem` | o que ele publica, o que a apuração alcança, e o ato que declara |
| `medida` | recortes sem quantidade **sobre** recortes publicados |
| `destino` | a Retificação daquele Edital, quando o ator a alcança |

**A detecção lê o conteúdo vigente que a supervisão já carregou por Edital** — nenhuma consulta nova.
Um Perfil entra quando publica vagas imediatas e não publica a linha correspondente.

---

## 6 · Transições

| De | Para | O que acontece |
|---|---|---|
| Perfil sem lista reservada | com a primeira lista reservada | o bloco aparece, com a linha geral no valor que já estava persistido; a repartição passa a ser declarada |
| Perfil com listas reservadas | sem nenhuma | a linha geral volta a ser reafirmada com o total na gravação, e a tela diz que voltou (`FR-322`) |
| Rascunho | publicado | a linha geral viaja no conteúdo, com identidade própria (`FR-329`) |
| Publicado sem linha | publicado com linha | só por Retificação, e só para o que vier (`FR-334`) |

A última linha é a única que atravessa a publicação, e é a única que exige ato.
