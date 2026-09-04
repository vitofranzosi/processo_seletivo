# Quickstart — 015 Ordenação e Classificação

O percurso que prova a feature de ponta a ponta, pelo canal do ator (Princípio VI), e a cobertura
que ele declara.

## Pré-requisitos

```bash
cd backend
.venv/bin/python -m pytest -q
```

A suíte contra PostgreSQL local exige **as duas** variáveis, e sem a primeira ela cai para sqlite e
pula os testes de trigger e concorrência em silêncio:

```bash
TEST_DB_ENGINE=postgresql DB_USER=<usuario> DB_NAME=test_015_ordenacao .venv/bin/python -m pytest -q
```

Para a interface administrativa, o seletor de identidade precisa estar ligado — sem ele `/gestao/`
responde 503 no runserver local.

## Entrega 1 — O Edital declara o marco, e ele viaja no documento

1. Na composição do Edital, no passo do Perfil, acrescentar um marco: código, nome, as Etapas que
   entram, a operação, a normalização e o arredondamento.
2. Acrescentar dois critérios de desempate em ordem — por exemplo, maior pontuação numa Etapa
   específica e depois maior idade.
3. Submeter, homologar e publicar.

**Prova:** o marco aparece no PDF publicado, dentro da seção do Perfil; o conteúdo canônico traz
`classificationMilestones` com `schemaVersion: 7`; o hash confere.

**Recusas a exercitar:** marco que enumera Etapa não classificatória; critério apontando Etapa
inexistente; critério sem comportamento declarado para valor ausente. As três recusam a publicação
com motivo (contrato `marco.md` §4).

## Entrega 2 — A ordem é calculada, e nada é gravado

1. Consolidar Resultados numa Etapa enumerada pelo marco, pela 013.
2. Abrir a tela do marco.

**Prova:** a ordem aparece com posição, pontuação combinada e modalidade declarada; os eliminados na
Etapa aparecem sem posição, com consequência e motivo; a soma das duas partes é o universo. Nenhum
ato foi criado, nenhum evento de emissão foi gravado.

**A conferir explicitamente:** um grupo empatado até o fim compartilha posição, é identificado como
grupo, e o próximo participante recebe a posição seguinte pulando as consumidas — `1, 1, 3`.

## Entrega 3 — A ordem vira ato, e o ato não muda mais

1. Emitir, informando a chave de idempotência do render.
2. Repetir o mesmo POST com a mesma chave.
3. Tentar alterar o ato por fora — ORM e SQL cru.

**Prova:** o primeiro POST cria o ato com autor, instante e a versão normativa; o segundo devolve o
mesmo desfecho sem emitir de novo; as duas tentativas de alteração são recusadas, a segunda pela
trigger, que é a que vale por fora do ORM.

**Concorrência:** duas emissões simultâneas no mesmo marco produzem exatamente um ato vigente, e a
segunda recebe 409 — não uma sucessão.

## Entrega 4 — A obsolescência aparece, por dois caminhos

1. Consolidar um Resultado tardio no universo do marco e reabrir a tela.
2. Retificar a ordem dos critérios de desempate e reabrir a tela.

**Prova:** nos dois casos o vigente aparece como obsoleto, com a divergência posição a posição — e no
segundo **sem que nenhum Resultado tenha mudado**, que é o caminho que a revisão do prompt cobrou.
Um Resultado novo em outro Perfil não marca nada.

3. Retificar o Edital removendo a Etapa que um critério consumia.

**Prova:** o ato aparece **obsoleto e não recomputável**, íntegro e consultável, com o critério e a
Etapa ausentes nomeados. A comparação não aparece vazia sem explicação.

## Entrega 5 — A proveniência basta, e a sucessão exige confirmação

1. Abrir o ato e conferir a proveniência inteira.
2. Emitir o sucessor a partir de um recálculo confirmado.

**Prova:** a consulta mostra quais Resultados entraram, sob qual versão, e qual critério separou cada
par de vizinhas com quais valores. Depois da sucessão há exatamente um vigente, e o anterior continua
consultável com o motivo. Uma sucessão tentada a partir de leitura anterior ao vigente é recusada.

## O percurso completo, para o Princípio VI

Declarar o marco → publicar → consolidar Resultados → abrir a tela → conferir → emitir → consultar a
proveniência → ver a obsolescência → emitir o sucessor. Tudo pela interface administrativa, sem
banco, sem shell e sem chamada manual.

## Cobertura declarada, e não presumida

| Prova | Onde vive |
|---|---|
| combinação, desempate, valor ausente, numeração do empate | `tests/unit/classificacao/` |
| forma do snapshot com a coleção nova; elevação 6→7 | `tests/unit/editais/`, `tests/integration/publicacoes/` |
| coleção aninhada declarada e endereçável | `tests/integration/publicacoes/test_enderecamento.py` |
| imutabilidade e coerência por trigger, com SQL cru | `tests/integration/classificacao/` |
| um vigente por marco sob concorrência | `tests/integration/classificacao/` |
| 404 uniforme; consultar é de dois, emitir é de um | `tests/authorization/` |
| custo não cresce com a população | `tests/performance/` |
| o percurso inteiro | `tests/acceptance/test_ordenacao.py` |

**O que este quickstart não prova, e por quê:** o Edital 57/2026 não percorre este roteiro. Ele
seleciona por sorteio, e não existe Resultado de sorteio para ordenar enquanto o mecanismo não
existir na 013 — está na §5 da spec, e é dependência, não escolha.
