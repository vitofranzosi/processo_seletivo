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

## Entrega 2 — O candidato informa os fatos, e eles congelam na submissão

1. No mesmo Edital, declarar dois fatos — data de nascimento e meses de experiência — e publicar o
   teto de uma inscrição por candidato.
2. Como candidato, abrir a inscrição, preencher os dois e submeter.
3. Alterar o perfil depois da submissão.
4. Tentar submeter uma segunda inscrição, em outro Perfil do mesmo Edital.

**Prova:** os dois campos aparecem com o tipo declarado; depois da submissão os valores estão
congelados sob a versão que então vigorava; alterar o perfil muda **zero** valores congelados; e a
segunda submissão é recusada pelo teto, com o motivo, sem afetar a primeira.

**A conferir explicitamente:** num Edital que não declara fato nenhum, a inscrição não ganha campo
nenhum. E um rascunho aberto antes de uma Retificação que acrescenta fato só submete depois de
reconhecer a versão nova — é o caminho que a 009 já usa, e não um segundo.

**O que esta entrega não oferece, e é deliberado:** não há como o candidato **corrigir** o que
informou depois de submeter. Congelar é o ponto de D-2, a 009 não tem retificação de inscrição, e
esta feature não a cria.

## Entrega 3 — A ordem é calculada, e nada é gravado

1. Consolidar Resultados numa Etapa enumerada pelo marco, pela 013.
2. Abrir a tela do marco.

**Prova:** a ordem aparece com posição, pontuação combinada e modalidade declarada; os eliminados na
Etapa aparecem sem posição, com consequência e motivo; a soma das duas partes é o universo. Nenhum
ato foi criado, nenhum evento de emissão foi gravado.

**A conferir explicitamente:** um grupo empatado até o fim compartilha posição, é identificado como
grupo, e o próximo participante recebe a posição seguinte pulando as consumidas — `1, 1, 3`.

**As duas medições de desempenho vivem aqui:** a contagem de consultas não muda entre um marco
pequeno e um de 1.000 participantes, e o percurso de 1.000 participantes fica dentro do teto de tempo
medido de ponta a ponta.

## Entrega 4 — A ordem vira ato, e o ato não muda mais

1. Emitir, informando a chave de idempotência do render.
2. Repetir o mesmo POST com a mesma chave.
3. Tentar alterar o ato por fora — ORM e SQL cru.

**Prova:** o primeiro POST cria o ato com autor, instante e a versão normativa; o segundo devolve o
mesmo desfecho sem emitir de novo; as duas tentativas de alteração são recusadas, a segunda pela
trigger, que é a que vale por fora do ORM. **Nada no ato é alterável, nem para sucedê-lo:** a
sucessão grava linha nova, e o vigente é o ato que ninguém sucedeu.

**Concorrência:** duas emissões simultâneas no mesmo marco produzem exatamente um ato vigente, e a
segunda recebe 409 — não uma sucessão.

## Entrega 5 — A obsolescência aparece, por dois caminhos

1. Consolidar um Resultado tardio no universo do marco e reabrir a tela.
2. Retificar a ordem dos critérios de desempate e reabrir a tela.

**Prova:** nos dois casos o vigente aparece como obsoleto, com a divergência posição a posição — e no
segundo **sem que nenhum Resultado tenha mudado**, que é o caminho que a revisão do prompt cobrou.
Um Resultado novo em outro Perfil não marca nada.

3. Retificar o Edital removendo a Etapa enumerada pelo marco **sem** ajustar o marco.

**Prova:** a publicação é **recusada**, com o motivo. Este é o ponto em que o critério pendurado é
impedido — ele não é estado que a tela precise tratar depois.

4. Retificar o Edital removendo o **marco** inteiro, e reabrir a tela do ato já emitido.

**Prova:** o ato aparece **obsoleto e não recomputável** — não há regra vigente com que comparar —,
íntegro e consultável, e a comparação não aparece vazia sem explicação. E a prova que fecha o par: o
ato continua **reproduzível** pela sua proveniência e pela versão histórica que o governou. Não
recomputável não é irreproduzível.

## Entrega 6 — A proveniência basta, e a sucessão exige confirmação

1. Abrir o ato e conferir a proveniência inteira.
2. Emitir o sucessor a partir de um recálculo confirmado.

**Prova:** a consulta mostra quais Resultados entraram, sob qual versão, e qual critério separou cada
par de vizinhas com quais valores. Depois da sucessão há exatamente um vigente, e o anterior continua
consultável com o motivo. Uma sucessão tentada a partir de leitura anterior ao vigente é recusada.

## O percurso completo, para o Princípio VI

Declarar o marco e os fatos → publicar → o candidato se inscreve e os fatos congelam → consolidar
Resultados → abrir a tela → conferir → emitir → consultar a proveniência → ver a obsolescência →
emitir o sucessor. Tudo pela interface administrativa, sem
banco, sem shell e sem chamada manual.

## Cobertura declarada, e não presumida

| Prova | Onde vive |
|---|---|
| combinação, desempate, valor ausente, numeração do empate | `tests/unit/classificacao/` |
| fato congelado na submissão, teto por candidato, Edital sem fato | `tests/integration/inscricoes/` |
| forma do snapshot com a coleção nova; elevação 6→7 | `tests/unit/editais/`, `tests/integration/publicacoes/` |
| coleção aninhada declarada e endereçável | `tests/integration/publicacoes/test_enderecamento.py` |
| imutabilidade e coerência por trigger, com SQL cru | `tests/integration/classificacao/` |
| um vigente por marco sob concorrência | `tests/integration/classificacao/` |
| 404 uniforme; consultar é de dois, emitir é de um | `tests/authorization/` |
| custo em consultas não cresce com a população | `tests/performance/` |
| percurso de 1.000 participantes dentro do teto de tempo | `tests/performance/`, no molde de `test_public_queries.py:145-169` |
| o percurso inteiro | `tests/acceptance/test_ordenacao.py` |

**O que este quickstart não prova, e por quê:** o Edital 57/2026 não percorre este roteiro. Ele
seleciona por sorteio, e não existe Resultado de sorteio para ordenar enquanto o mecanismo não
existir na 013 — está na §5 da spec, e é dependência, não escolha.
