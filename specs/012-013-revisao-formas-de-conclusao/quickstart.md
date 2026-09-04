# Quickstart: a Etapa decisória, de ponta a ponta

**Revisão**: `012-013-revisao-formas-de-conclusao` | **Data**: 2026-09-03

O que esta revisão entrega, demonstrado pelo canal de cada ator. O critério é o Princípio VI:
capacidade que o domínio sustenta e nenhuma interface alcança não está entregue.

## Pré-requisitos

```bash
cd backend && make dev
```

A suíte inteira exige PostgreSQL local — as garantias de banco desta revisão são todas
`postgresql_only`, e sob SQLite elas passam sem exercitar nada:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_NAME=test_revisao_012_013 uv run pytest
```

---

## Jornada 1 — Publicar uma Etapa decisória

**Ator**: quem elabora o Edital.

1. Na composição de Etapas, escolher **Análise documental** e marcar a forma **Decisória**.
2. Os campos de nota mínima e pontuação máxima saem do formulário; entram os dois rótulos, com
   "Deferido" e "Indeferido" pré-preenchidos e editáveis.
3. Publicar.

**Esperado**: o snapshot traz `"forma": "DECISORIA"` com os dois rótulos; `schemaVersion` é `6`; o
PDF mostra `Resultado: Deferido / Indeferido` e **não** mostra linha de nota.

**Negativa que faz parte da entrega**: publicar decisória sem rótulo é recusado, com a frase
apontando o campo. Publicar decisória com pontuação máxima é recusado pela mesma via.

## Jornada 2 — Avaliar sem nota

**Ator**: avaliador com atribuição na Etapa.

1. Abrir a Mesa e abrir a inscrição.
2. O instrumento é o par **Deferido / Indeferido**. Não existe campo de nota na tela.
3. Marcar **Indeferido**, salvar como rascunho, escrever o parecer, concluir.

**Esperado**: a avaliação conclui sem pontuação; a conclusão preservada guarda a forma, o sentido, o
parecer, a versão e o instante.

**Negativas**: concluir "Indeferido" sem parecer é recusado. Enviar `pontuacao` para uma Etapa
decisória é recusado pelo domínio no canal HTTP real — não escondido pela tela.

## Jornada 3 — Oficializar o resultado da Etapa decisória

**Ator**: presidência.

1. Abrir a prontidão da Etapa. As inscrições com avaliação concluída aparecem prontas.
2. Consolidar em lote.

**Esperado**: cada Resultado nasce `ELIMINADA` para indeferido e `HABILITADA` para deferido, com o
motivo citando o rótulo publicado — "análise documental: Indeferido", nunca `DESFAVORAVEL`.

**Progressão**: a inscrição indeferida some de todas as Etapas seguintes, pela mesma regra que já
valia para a eliminação por nota.

## Jornada 4 — A recusa que é o coração da decisão de 03/09

1. Publicar uma Etapa **decisória e não eliminatória**.
2. Avaliar e concluir normalmente.
3. Abrir a prontidão.

**Esperado**: a Etapa **não** é consolidável, e a prontidão diz por quê — o Edital não publicou o
efeito da decisão desfavorável. Nenhum Resultado é criado, e o sistema não escolhe um efeito.

O simétrico, que passa a funcionar: Etapa decisória **eliminatória e sem nota mínima** consolida
normalmente. É a configuração real dos Editais 35 e 57, e recusá-la seria procurar um número que a
norma nunca teve.

## Jornada 5 — O Edital antigo continua vivo

1. Tomar um Edital publicado na versão canônica 5.
2. Abrir uma Retificação sobre ele e consolidá-la.

**Esperado**: a Retificação funciona; a Versão Consolidada nasce na versão 6 com
`"forma": "PONTUADA"` escrita pela elevação; a **Publicação original não é tocada** e continua byte
a byte o que foi publicado; a elevação não aparece como ato normativo de ninguém.

**E a leitura direta**: consultar o snapshot v5 sem retificar continua servindo o conteúdo literal,
sem forma, e quem o consome o lê como pontuado.

## Jornada 6 — Retificar a forma

1. Sobre um Edital com Etapa pontuada e avaliações já concluídas, retificar a Etapa para decisória.

**Esperado**: a Retificação é possível e exige os rótulos. As conclusões antigas **continuam
íntegras e interpretáveis** sob a forma que as governou. A 013 recusa fundamentar Resultado nelas,
por norma divergente — a consequência fica retida, o registro não.

---

## O que não é demonstrável por jornada

As garantias de banco, que são o que sustenta as jornadas acima e precisam de teste próprio:

| garantia | como se prova |
|---|---|
| conclusão decisória com pontuação é impossível | `INSERT` cru recusado pela constraint |
| conclusão pontuada com sentido é impossível | `INSERT` cru recusado pela constraint |
| Resultado que não bate com a fonte é impossível | `INSERT` cru recusado pela trigger |
| conclusão histórica continua completa | toda linha existente com `forma = PONTUADA` |
| sentido inventado é impossível | `INSERT` cru com valor fora do par recusado pela constraint |
| o salto de versão funciona **com dados** | `MigrationExecutor` a partir do estado anterior, com avaliações, conclusões e Resultados históricos: os três backfills e as três triggers no lugar |
| a reversão é recusada depois da primeira conclusão decisória | `migrate` para trás com dado decisório, e a recusa nomeia o ato administrativo que precisa vir antes |
| nada da forma pontuada mudou | **por identidade de teste**: todo teste que existia continua existindo e passando, e as asserções alteradas são enumeradas uma a uma em [`traceability.md`](./traceability.md) §1 |

As duas linhas do salto e da reversão são as que a suíte comum **não** alcança: ela roda sobre banco
já migrado, e por isso demonstra que o esquema novo funciona, não que a migração até ele funciona.
Para chegar até elas, `tests/migrations/test_migrations.py` passou a admitir `avaliacoes` e
`resultados` no seu `APPS`, que era restrito a quatro.

E "nada da forma pontuada mudou" **não** significa "nenhuma asserção mudou": o incremento sobe a
versão canônica, e todo teste que fixa o literal dela tem de mudar. Exigir o contrário seria cobrar
o que a própria revisão torna falso (012, FR-124; 013, FR-050).
