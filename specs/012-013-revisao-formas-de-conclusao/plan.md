# Implementation Plan: revisão de compatibilidade 012–013

**Branch**: `012-013-revisao-formas-de-conclusao` | **Date**: 2026-09-03 | **Escopo**: [spec.md](./spec.md)

**Input**: a D-008 de [`specs/012`](../012-mesa-de-avaliacao/spec.md) e a D-008 de
[`specs/013`](../013-consolidacao-resultado-etapa/spec.md), emendadas em 03/09/2026.

## Summary

Avaliar deixa de significar pontuar. A Etapa publica qual das duas formas de conclusão exige —
`PONTUADA` ou `DECISORIA` —, e as duas atravessam o sistema da Mesa ao Resultado oficial sem que
nenhuma escala numérica seja inventada onde o Edital não publicou nenhuma.

**Não é feature nova, e não é revisão de uma feature só.** É mudança de requisito sobre duas features
já entregues, e o par tem de mudar junto: emendar apenas a 012 produziria um sistema em que o
avaliador conclui "indeferido" e a Etapa nunca produz resultado — uma fronteira quebrada no meio do
fluxo, criada justamente pela rodada que existe para eliminar lacunas contra Editais reais.

O trabalho tem quatro naturezas, e elas não têm o mesmo tamanho:

1. **Um segundo incremento canônico** — a Etapa publicada passa a declarar a forma e, na forma
   decisória, os dois rótulos. Sobe `SCHEMA_VERSION` de 5 para 6 e alcança contrato, validação,
   elaboração, snapshot, elevação, conflito, Retificação e documento. É a parte cara, e o mapa dela
   é conhecido: são os mesmos catorze pontos que `maximumScore` toca hoje.
2. **Uma constraint que passa a alternar, em três tabelas** — `Avaliacao`, `ConclusaoAvaliacao` e
   `ResultadoEtapa`. O invariante forte não é relaxado; muda o que ele afirma.
3. **Dois instrumentos onde havia um** — na Mesa, e no documento publicado.
4. **Duas regras da 013 que deixam de ser incondicionais** — a consequência, que passa a ser lida da
   forma, e o impedimento por regra insuficiente, que ganha o caso simétrico.

**A descoberta que mais determina o desenho** é a que motivou a revisão do handoff: a 013 já estava
implementada quando a decisão de domínio foi tomada, e pressupõe pontuação no domínio, na coluna
não-nulável e na trigger. O briefing que planejava só a 012 foi escrito numa branch que não continha
`specs/013` nem o app `resultados` (`git ls-tree bc90820`), e o merge dos dois PRs ficou a cinco
minutos de distância. Sem esse achado, a rodada teria entregue a fronteira quebrada.

**A que mais economiza**: quase nada aqui é mecanismo novo. A elevação de esquema, o par
`PROTEGER`/`DESPROTEGER` das tabelas append-only, a conferência de coerência do Resultado com a
fonte, o impedimento de Etapa por regra insuficiente e o vocabulário publicado como dado
(`ModalidadeConcorrencia`) já existem, foram escritos por decisão explícita, e são todos reusados. O
que a revisão faz é ensinar a cada um deles uma segunda forma.

**A que mais encurta**: `resultados/domain/progressao.py` não muda uma linha. Ele consome
`HABILITADA` e `ELIMINADA`, nunca pontuação — o que confirma que generalizar a 013 é estreito, e não
o começo de um motor genérico de avaliação.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova. Nenhuma rota nova,
nenhum caminho alterado, nenhuma permissão nova, nenhum ato administrativo novo.**

**Storage**: PostgreSQL. **Três migrations**, em `editais`, `avaliacoes` e `resultados`. Em `editais`,
`forma` nasce com `default="PONTUADA"` e o próprio `AddField` alcança as Etapas já em elaboração — sem
isso, todo Edital em rascunho ficaria impublicável. Nas outras duas, **três backfills explícitos** —
`Avaliacao` concluída, `ConclusaoAvaliacao` e `ResultadoEtapa`, todos para `PONTUADA`;
rascunho de Avaliação permanece sem forma, porque ela é lida no ato de concluir. Duas das tabelas são
append-only protegidas por trigger, e por isso derrubam e recriam a trigger dentro da própria
transação para o backfill (TR-004a, TR-005, TR-006). **Nenhuma migration em `publicacoes`**: a
elevação de versão canônica é função pura sobre conteúdo lido, e não escreve linha nenhuma — a 012 já
provou isso e a prova não é refeita.

**Testing**: pytest com pytest-django. Toda garantia de banco desta revisão é `postgresql_only` — as
triggers não existem em SQLite, e sob ela os testes passariam sem exercitar nada. Quatro exigências
específicas: os `INSERT` crus das constraints e da trigger; a leitura de um snapshot v5 depois do
salto para 6; **o salto de versão exercido com dados**, por `MigrationExecutor`, que exige incluir
`avaliacoes` e `resultados` no `APPS` de `tests/migrations/test_migrations.py`, hoje restrito a
quatro apps (TR-014); e a suíte existente passando **por identidade de teste** — todo teste que
existia continua existindo e passando, com as asserções alteradas enumeradas uma a uma —, que é a
demonstração de FR-124 e FR-050. "Sem alteração de asserção" seria impossível: o incremento sobe a
versão canônica, e todo teste que fixa o literal dela tem de mudar.

O contrato tem suíte própria: `tests/contract/test_forma_publicada.py` confere o `openapi.yaml`
contra o domínio campo a campo, e três dos seus testes ficam vermelhos no instante em que
`ETAPA_PUBLICADA` ganha campo sem a alteração correspondente no contrato (TR-013).

**Target Platform**: servidor Linux; navegador institucional, incluindo celular. O par de rótulos
precisa caber em 375 px sem virar tabela horizontal.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: nenhuma mudança de custo. A forma é lida do conteúdo da versão que a transação
já lê uma vez (FR-096); nenhuma consulta nova entra em listagem, e nenhuma verificação passa a ser
por linha.

**Constraints**: a Publicação original permanece byte a byte o que foi publicado. Nenhuma conclusão
histórica perde validade. Nenhum comportamento da forma pontuada muda.

**Scale/Scope**: três migrations, dois enums, cinco campos publicados novos contando os dois
atrasados na Retificação, três constraints reescritas, uma trigger reescrita, duas funções puras de
domínio estendidas.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta revisão responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; invariantes em constraint | O campo chama-se `sentido`, e **não** `decisão` nem `tipo_resultado`: `Resultado` é a entidade da 013, e o Princípio I não admite o termo significando duas coisas. `Forma` e `Sentido` são do domínio; o vocabulário do Edital vive em `rotuloFavoravel`/`rotuloDesfavoravel`, como `ModalidadeConcorrencia` já faz. Os invariantes continuam no banco, e o que muda é o que eles afirmam — a constraint alterna, não é relaxada. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | A forma é a **única** cópia nova na Avaliação, e ela existe porque uma `CheckConstraint` não referencia outra tabela — onde a cópia não compra invariante, FR-072 segue proibindo. A conclusão histórica continua interpretável sob a forma que a governou, pelo mesmo padrão de FR-071. A elevação não escreve em `Publicacao` nem em `VersaoConsolidada` e não alcança a leitura pública, senão a tela mostraria uma coisa e o `content_hash` provaria outra. **Passa** |
| III — Segurança, dados pessoais e auditoria | Menor privilégio; auditoria de ato sensível | Nenhuma permissão nova e nenhuma superfície nova. A trilha passa a deixar o **sentido** de fora pelo mesmo motivo que já deixava parecer e pontuação: é conteúdo do juízo, e não registro de que houve juízo (012, FR-054). Sem isso, a trilha da forma decisória passaria a guardar o deferimento. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; transação; concorrência | A forma é lida na transação que conclui, do conteúdo da versão já lida uma vez, e é essa que fica gravada (FR-088, FR-096). Retificação que muda a forma no intervalo é recusada pela mesma via de FR-073. A escolha do instrumento na tela é apresentação; a recusa do campo da outra forma é do domínio. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Testado no nível certo; solução mais simples | A alternativa "deferido = 1, indeferido = 0" era mais simples de escrever e inventaria uma grandeza que o Edital não publicou. A escolhida é a mais simples **que não inventa norma**. Nenhuma abstração especulativa: a terceira forma plausível (conceito ordinal) é nomeada e deliberadamente não construída. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | O [quickstart.md](./quickstart.md) percorre as seis jornadas, incluindo as negativas: publicar decisória sem rótulo, concluir desfavorável sem parecer, enviar pontuação para Etapa decisória, e a Etapa que não é consolidável. A recusa faz parte da entrega. Os **dois controles novos** — o formulário que alterna por forma e o par de opções da Mesa — entram sob a exigência de interface da Constituição, com tarefa própria em US1 e US3: rótulo associado, operação por teclado, foco visível e recusa anunciada. A 012 tratou acessibilidade como fatia (S6), e esta revisão não a herda por omissão. **Passa** |

**A Restrição de Domínio que precisou ser lida com atenção.** A Constituição diz que *"cada Etapa
PODE definir ordem, peso, notas mínima e máxima, caráter eliminatório ou classificatório, banca,
critérios, pontuação e acumulação"*. É `PODE`, e não `DEVE` — a aplicabilidade condicional das notas
por forma é compatível com o texto, e é o `PODE` que a torna compatível. A restrição vizinha, a de
que regra sujeita a legislação não seja hard-coded, é o argumento **a favor** dos rótulos publicados:
um enum com quatro pares cresceria a cada Edital novo.

**Reavaliação após a Fase 1.** Nenhum gate mudou de veredito. Um ponto ganhou precisão em TR-006 e
merece registro porque a primeira leitura o teria errado: comparar `fonte.pontuacao IS DISTINCT FROM
NEW.pontuacao` numa conclusão decisória compara `NULL` com `NULL`, que `IS DISTINCT FROM` resolve
como iguais — a trigger passaria a aprovar qualquer coisa na forma decisória, silenciosamente. Por
isso a conferência ganha `forma` e `sentido` e compara os três incondicionalmente, em vez de alternar.

Nenhuma dependência nova. Nenhuma exceção de complexidade nova.

## Project Structure

### Documentation (this revision)

```text
specs/012-013-revisao-formas-de-conclusao/
├── spec.md          # escopo e ponteiros — não cria requisito
├── plan.md          # este arquivo
├── research.md      # TR-001 a TR-014
├── data-model.md    # só o delta
├── contracts/
│   └── forma-da-conclusao.md
├── quickstart.md    # seis jornadas, com as negativas
└── tasks.md         # $speckit-tasks — 71 tarefas em dez fases
```

Os artefatos de `specs/012-mesa-de-avaliacao/` e `specs/013-consolidacao-resultado-etapa/`
descrevem a construção original e **não são sobrescritos**. As duas `spec.md` foram emendadas em
03/09/2026; os `plan.md`, `research.md` e `tasks.md` de cada uma continuam sendo o registro da
entrega que aconteceu.

### Source Code (repository root)

```text
specs/001-processo-seletivo-editais/contracts/
└── openapi.yaml                           EtapaPublicada e EtapaInput: os três campos, na versão 6

backend/tests/
└── migrations/test_migrations.py          APPS e TRIGGERS ganham avaliacoes e resultados; o salto
                                           com dados históricos vira teste

backend/processo_seletivo/
├── shared/canonical.py                    SCHEMA_VERSION 5 → 6, com a história do incremento
├── editais/
│   ├── domain/validation.py               ETAPA_PUBLICADA + a coerência entre campos por forma
│   ├── domain/etapas.py                   a leitura da Etapa na elaboração
│   ├── api/serializers.py                 os três campos no contrato
│   ├── application/draft.py               rascunho → linha de elaboração
│   └── models/etapas.py                   forma, rotulo_favoravel, rotulo_desfavoravel  [migration]
├── publicacoes/
│   ├── domain/elevacao.py                 o degrau 5 → 6 e a equivalência de grafias
│   ├── domain/conflicts.py                acompanha a equivalência
│   ├── application/publish_edital.py      transcrição para o snapshot
│   └── infrastructure/pdf.py              os pares da Etapa, por forma
├── avaliacoes/
│   ├── models.py                          forma + sentido; duas constraints que alternam  [migration]
│   ├── domain/formas.py                   **módulo novo** — os enums Forma e Sentido
│   ├── domain/previsao.py                 a leitura da ausência, num lugar só
│   └── domain/pontuacao.py                a recusa por forma; parecer no desfavorável
├── resultados/
│   ├── models.py                          forma + sentido; trigger nova  [migration]
│   ├── domain/regra.py                    consequência lida; os dois impedimentos simétricos
│   ├── domain/compatibilidade.py          forma entra na comparação; rótulos não
│   └── application/consolidacao.py        copia a conclusão conforme a forma
└── interface/
    ├── forms.py                           elaboração: os três campos
    ├── retificacao.py                     CAMPOS_ETAPA completa
    ├── revisao.py                         o resumo da Etapa, por forma
    └── templates/interface/_etapa.html    o formulário condicional
```

**Structure Decision**: nada de app novo, e **um** módulo novo. Cada mudança cai no arquivo que já é
dono daquela responsabilidade, e a lista acima é exatamente o conjunto de pontos que `maximumScore`
toca hoje, mais os três de domínio da conclusão — e mais o `openapi.yaml`, que é fonte única da forma
publicada e não documentação de acompanhamento.

O módulo novo é `avaliacoes/domain/formas.py`, e o lugar dele decorre da direção de dependência que
já existe: `resultados` importa de `avaliacoes` — `compatibilidade.py` importa `previsao.py` hoje —, e
o contrário nunca acontece. Os dois enums descrevem **a conclusão**, que é conceito da 012, e por isso
nascem lá e são importados pela 013. Colocá-los em `shared/` os afastaria do conceito que nomeiam;
duplicá-los nos dois apps criaria a divergência que um enum existe para impedir.

`editais` os alcança por **um** caminho e não por dois, e a distinção importa: o **modelo** de
elaboração importa `Forma` para as suas `choices`, porque a alternativa seria uma terceira cópia dos
dois literais; o **validador** do conteúdo publicado mantém a tupla literal, porque ali o que se
confere é a string que chegou no snapshot, e não o domínio da conclusão.

## Fases de implementação sugeridas

| Fase | Entrega observável | Por que nesta ordem |
|---|---|---|
| **F1** | A Etapa publica a forma: `openapi.yaml`, validação, elaboração, snapshot, `SCHEMA_VERSION` 6 | Sem norma publicada, tudo que vier depois aplicaria regra que ninguém publicou (P-007). O contrato entra **nesta** fase, e não ao final: três testes de `test_forma_publicada.py` ficam vermelhos sem ele |
| **F2** | Elevação 5 → 6 e Retificação: `CAMPOS_ETAPA` completa, equivalência de grafias, conflito | É a precondição que a D-002 mandou confrontar **antes** de qualquer migration de conteúdo |
| **F3** | A conclusão por forma: `Avaliacao` e `ConclusaoAvaliacao`, constraints que alternam, backfill | O invariante desce ao banco antes de qualquer tela poder gravar nele |
| **F4** | A Mesa com dois instrumentos, e as recusas no canal HTTP real | A capacidade só existe quando é alcançável pelo ator (Princípio VI) |
| **F5** | O documento materializado, e o resumo da Retificação | Senão a fonte estruturada e o PDF divergem |
| **F6** | `ResultadoEtapa` por forma, trigger nova, consequência e os dois impedimentos | Fecha a fronteira: a decisão vira consequência oficial |
| **F7** | A bateria: garantias de banco, o salto de versão com dados, não regressão, e as seis jornadas | A demonstração, e não a intenção. O upgrade exercido é o que prova os três backfills e a recriação das triggers — a suíte comum roda sobre banco já migrado e não os alcança |

**A primeira vertical significativa** é F1 → F3 → F4: publicar uma Etapa decisória, avaliar sem nota
e concluir. F6 é o que a torna útil; sem ela o sistema aceita o indeferimento e não produz efeito, e
é exatamente esse estado intermediário que **não pode ser entregue** — ele pode existir dentro da
branch, nunca em `main`.

## Complexity Tracking

> Nenhuma violação de gate a justificar. A tabela registra as duas escolhas que **parecem**
> exceção e não são.

| Aparente violação | Por que não é | Alternativa recusada |
|---|---|---|
| A Avaliação copia a forma da Etapa, e FR-072 proíbe cópia | A proibição vale onde a cópia não compra invariante. Uma `CheckConstraint` do PostgreSQL não referencia outra tabela: sem a forma na linha, a regra que define "concluída" sairia do banco e voltaria para a aplicação | Validar a completude na aplicação, contra a Etapa vigente — devolve à camada de que a 012 desconfiou ao escrever a constraint |
| Dois incrementos canônicos na mesma feature, quando D-001 fixou "um, e só um" | D-001 continua verdadeira sobre o primeiro incremento e vira decisão histórica. O segundo nasce de mudança de requisito posterior, e não de omissão do primeiro | Reescrever a história como se os cinco campos tivessem nascido juntos — exigiria mentir em `elevacao.py`, que documenta o 4 → 5 como fato consumado |

## Restrições técnicas desta revisão

- **Nenhuma linha de `Publicacao` ou `VersaoConsolidada` é escrita.** A elevação é leitura.
- **`SCHEMA_VERSION` sobe junto da migration de `editais`**, nunca antes: entre o salto da constante
  e a chegada do campo, toda Retificação em curso compararia contra uma versão que o conteúdo
  elaborado ainda não sabe escrever.
- **Nenhum default de esquema para `forma`.** Um `DEFAULT 'PONTUADA'` economizaria o backfill e
  deixaria uma afirmação permanente de que conclusão sem forma é pontuada — verdadeira sobre o
  passado, falsa sobre o futuro.
- **Nenhum default institucional de rótulo.** Prefill editável na tela de elaboração é conveniência;
  o domínio aplicar rótulo que o Edital não publicou é P-007 violado.
- **A leitura da ausência vive num lugar só**, e vale tanto no consumo quanto na elevação. Escrever a
  mesma interpretação em dois lugares independentes é como ela passa a divergir.
- **Nenhuma inferência de consequência.** Etapa decisória e não eliminatória é recusada pelo
  mecanismo que a 013 já usa no caso simétrico — não resolvida por convenção.
- **Quando houver conflito entre generalizar um motor de formas de conclusão e implementar as duas
  que os Editais reais exercitam, prefira as duas.** A terceira forma tem lugar de extensão nomeado
  e nenhuma regra que a consuma.
