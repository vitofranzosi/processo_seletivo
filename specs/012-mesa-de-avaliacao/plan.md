# Implementation Plan: Mesa de Avaliação

**Branch**: `012-mesa-de-avaliacao` | **Date**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-mesa-de-avaliacao/spec.md`

## Summary

A 011 respondeu quem pode atuar em cada Etapa e parou ali. A 012 responde quais inscrições cabem a
cada uma dessas pessoas, e deixa que elas façam o trabalho dentro do sistema: a presidência
distribui em lote entre quem está alocado, o avaliador abre a Mesa, abre a inscrição sob a
atribuição que o autoriza, registra pontuação e parecer e conclui. Resultado continua sendo da 013.

O trabalho tem três naturezas, e elas não têm o mesmo tamanho:

1. **Um incremento normativo, uma vez** — a Etapa publicada passa a declarar quantas avaliações
   cada inscrição recebe e qual a pontuação máxima. É a única coisa desta feature que toca conteúdo
   publicado, e alcança modelo, serializer, rascunho, validação, snapshot, documento e o contrato da
   001 (T-014).
2. **Três entidades operacionais** — `Atribuicao`, `Avaliacao` e `Impedimento`, num app novo, mais
   uma linha append-only por conclusão.
3. **Uma composição de autorização** — a pergunta da 011 mais a pergunta da 012, nesta ordem, em
   toda rota. Não é código novo: é `pode_atuar_na_etapa` e `etapas_autorizadas` sendo compostos com
   uma consulta a mais.

**A descoberta que mais determina o desenho** é a que a spec mandou confrontar. Elevar conteúdo da
versão canônica anterior é possível, e é possível **porque este incremento é aditivo e a spec já
declara o que a ausência significa** — coisa que não era verdade dos incrementos de 007 e 009, que
acrescentavam coleções inteiras.

Mas elevar só a base **não** resolve, e essa é a correção que a revisão do plano trouxe. A
consolidação não parte da última versão: parte do conteúdo original e **reaplica todos os atos
publicados**, que carregam o valor literal gravado quando foram elaborados. Um ato v4 que
acrescentou uma Etapa reintroduziria essa Etapa fora de forma, e a publicação inteira falharia na
materialização — nada inválido fica gravado, porque a transação reverte, mas um ato legítimo e já
homologado se torna impublicável. A elevação precisa, portanto, alcançar também o `newValue` de
cada ato, e ser **path-aware**: um `REPLACE` de nota mínima carrega um decimal, não uma Etapa. Como
a função é idempotente, ela é aplicada incondicionalmente e dispensa etiquetar cada ato com a versão
em que nasceu (T-001).

E o que o autor vê tem de ser o que o servidor confere: o editor passa a compor sobre a projeção
elevada, senão `expectedPreviousHash` falaria de uma Etapa e a conferência de outra (T-015).

Nada disso escreve, e nada disso alcança a leitura pública: o Edital publicado antes do incremento
continua retificável, e a Publicação original continua sendo byte a byte o que foi publicado.

**A que mais economiza**: quase nada desta feature é mecanismo novo. A entrega de arquivo com
conferência de integridade antes do primeiro byte já existe na 009; o invólucro de comando com
bloqueio, reautorização e idempotência já existe na 011; `AtoAdministrativo` já é o ato com motivo
obrigatório, e `RegistroAuditoria` já é a trilha. A 012 reutiliza os quatro e não escreve nenhum.

**A que mais encurta**: a página que a Mesa ocupa já foi construída. A 011 deixou nela o aviso de
que a avaliação viria quando a Etapa fosse habilitada, e recusou-se a desenhar UI falsa
antecipando esta feature. A 012 substitui o aviso pela lista.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** Nenhuma superfície de
API nova: a feature inteira é servida pelo canal HTML institucional, com os fragmentos htmx já
embarcados.

**Storage**: PostgreSQL. Uma migration no app novo `avaliacoes` — quatro modelos, duas unicidades
parciais, um índice único parcial e os checks de completude de estado. Uma migration em `editais`,
com dois campos na Etapa de elaboração. **Nenhuma migration em `publicacoes` ou `auditoria`**: a
elevação de versão canônica é função pura sobre conteúdo lido, e não escrita em linha gravada.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration` e
`authorization` já declarados. Três exigências específicas desta feature: o índice único parcial de
FR-074 só é exercido com `TEST_DB_ENGINE=postgresql`; o teste de contrato `test_forma_publicada.py`
falha se a transcrição divergir do `openapi.yaml`; e a equivalência entre `pode_atuar_na_etapa` e
`etapas_autorizadas` precisa de teste próprio, como a 011 já tem.

**Target Platform**: servidor Linux; navegador institucional, incluindo celular — a Mesa e a
distribuição precisam caber em 375 px sem tabela horizontal.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: a Mesa com 500 atribuições responde com três consultas — autorização em lote,
página e contagens. Nenhuma listagem verifica autorização por linha; nenhuma tela exige uma
submissão por atribuição.

**Constraints**: mil inscrições com dupla avaliação são duas mil atribuições. Retirar uma pessoa de
uma Etapa custa **uma** escrita — a alocação —, e zero escritas em Atribuição.

**Scale/Scope**: um Edital com mil inscritos, quarenta avaliadores, quatro Etapas. Quatro modelos
novos, dois campos normativos novos, cinco telas servidas por dez rotas.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; identificador público não autoriza; invariantes em constraint | A colisão foi encontrada e resolvida antes de virar código: `Atribuição` passa a ser a entidade avaliador→inscrição, e o identificador que a 011 usava para outra coisa é renomeado, sem mudar caminho de URL (T-012). `Avaliacao` é o ato, `EtapaAvaliacao` continua sendo a fase. As unicidades vão para o banco: parcial sobre a Atribuição ativa, `OneToOne` na Avaliação e índice único parcial para a conclusão única (T-007). Identificador não autoriza: trocar o UUID da inscrição na URL não alcança inscrição não atribuída. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | A Avaliação aponta para a `VersaoConsolidada` sob a qual foi concluída e **não copia** limite nenhum, que é o que mantém a versão como fonte única (FR-071, FR-072). A elevação de esquema não escreve em `Publicacao` nem em `VersaoConsolidada`, ambas append-only e protegidas por trigger; a Publicação original permanece o que foi publicado (T-001). A conclusão lê a versão dentro da transação que grava, de modo que a regra validada é a regra registrada (FR-096). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | Esta é a primeira feature em que membro de comissão lê dado pessoal de candidato em volume, e a autorização é composta: alocação **e** atribuição, no servidor, em toda rota, com 404 uniforme. Menor privilégio literal: a permissão da consulta administrativa da 009 alcança o Edital inteiro e por isso **não** é reutilizada (T-006). Cada abertura de documento é registrada; a trilha não guarda parecer nem pontuação. Resposta com dado pessoal é não armazenável pelo navegador. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | A Avaliação tem ciclo de vida real e por isso tem estados explícitos — `RASCUNHO` e `CONCLUIDA`, com transição de reabertura que só parte de `CONCLUIDA`. Os quatro riscos que a Constituição nomeia estão mapeados a mecanismo existente na tabela de T-010, e a seção 18 da spec diz o resultado observável de cada um. Nenhuma regra vive na tela. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | O [quickstart.md](./quickstart.md) demonstra **37 dos 99 requisitos** — os observáveis pelo canal do ator, que é o que o princípio VI exige dele. Os outros 62 são invariantes de banco, de comando e de não-regressão, e a cobertura deles é responsabilidade de `tasks.md`, com a rastreabilidade fechada em `traceability.md` ao final da implementação, como a 011 fez. Afirmar aqui que "cada FR tem cenário no quickstart" seria falso, e foi o que a primeira redação deste gate afirmou. Nada de motor genérico de avaliação: quatro modelos, nenhuma abstração especulativa. **Passa, com a cobertura declarada e não presumida** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | A vertical inteira é navegável no `interface`: presidente distribui, avaliador abre a Mesa, abre a inscrição, registra e conclui, e quem não recebeu aquela inscrição recebe 404. A negação faz parte da entrega, não é nota de rodapé. **Passa** |

Duas exceções vão para `Complexity Tracking`: o app novo e a tripla copiada na Avaliação.

**Reavaliação após a Fase 1, e o que a revisão do plano corrigiu.** A primeira passagem deste gate
aprovou dois princípios sobre premissa errada, e o registro fica porque o erro é instrutivo:

- **II** — dava-se por resolvido com a elevação do conteúdo-base. A consolidação reaplica todos os
  atos publicados, e um ato v4 que acrescentou Etapa reintroduziria conteúdo fora de forma,
  tornando impublicável um ato legítimo. A elevação passa a alcançar o `newValue` de cada ato,
  path-aware, restrita ao fluxo de Retificação para não romper o `content_hash` da leitura pública,
  e estendida à projeção que o autor compõe (T-015). Oito cenários viram teste obrigatório.
  **Agora passa.**
- **I** — a garantia de FR-074 estava ancorada em `membro_id`, que é vínculo e não pessoa: remover
  e readicionar alguém liberaria uma segunda conclusão sobre a mesma inscrição. O índice passa a
  usar a identidade institucional estável, e o Impedimento, pela mesma razão, acompanha a pessoa
  (FR-099). **Agora passa.**

Além disso, o vocabulário de elegibilidade foi fechado na spec — "invalidar" estava significando
duas coisas —, e o contrato passou a declarar `idempotency_key` em todo comando que reutiliza
`comando_de_comissao`, e não só no lote.

Nenhuma dependência nova. As duas exceções de complexidade permanecem duas.

## Project Structure

### Documentation (this feature)

```text
specs/012-mesa-de-avaliacao/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — as decisões técnicas (T-001 a T-014)
├── data-model.md        # Fase 1 — entidades, invariantes, estados e o incremento normativo
├── quickstart.md        # Fase 1 — como demonstrar cada entrega
├── contracts/
│   └── mesa.md          # Fase 1 — superfícies HTML, autorização composta e a forma publicada nova
└── tasks.md             # Fase 2 — criado pelo $speckit-tasks, não por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── avaliacoes/                   # NOVO — o domínio da execução do trabalho
│   ├── models.py                 # Atribuicao, Avaliacao, ConclusaoAvaliacao, Impedimento
│   ├── domain/
│   │   ├── autorizacao.py        # pode_avaliar_inscricao(): a composição, sobre o guard da 011
│   │   ├── pontuacao.py          # validação contra a versão: máxima, forma decimal, não-negativa
│   │   └── previsao.py           # avaliacoes_previstas() e pontuacao_maxima() — a leitura da ausência (T-002)
│   ├── application/
│   │   ├── distribuicao.py       # o lote, sobre comando_de_comissao da 011
│   │   ├── avaliacao.py          # gravar, concluir, reabrir
│   │   ├── impedimento.py        # registrar, e a inativação no mesmo ato
│   │   └── selectors.py          # a Mesa, a organização do trabalho e as invalidadas
│   └── migrations/               # uma migration
├── editais/
│   ├── models/etapas.py          # + evaluations_per_registration, maximum_score
│   ├── api/serializers.py        # + os dois campos
│   ├── application/draft.py      # + os dois campos no rascunho
│   ├── domain/validation.py      # + ETAPA_PUBLICADA na versão canônica 5
│   └── migrations/               # uma migration
├── publicacoes/
│   ├── application/publish_edital.py   # + os dois campos em _stages()
│   ├── application/retificacoes.py     # base, conteúdo em vigor e cada newValue passam por elevar
│   ├── domain/elevacao.py              # NOVO — elevar() e elevar_alteracoes(), as puras de T-001
│   └── infrastructure/pdf.py           # + as duas linhas na Etapa do documento
├── shared/canonical.py           # SCHEMA_VERSION 4 -> 5, com o comentário do incremento
├── interface/
│   ├── views.py                  # + distribuicao, mesa, inscricao_da_mesa, documento_da_mesa, impedimentos
│   ├── forms.py                  # + lote, avaliação, impedimento, reabertura
│   ├── retificacao.py            # campos_editaveis e diferencas recebem a projeção (T-015)
│   ├── urls.py                   # + dez rotas; atribuicao -> minha_etapa (T-012)
│   └── templates/interface/
│       ├── distribuicao.html
│       ├── mesa.html
│       ├── mesa_inscricao.html
│       ├── impedimentos.html
│       └── minha_etapa.html      # renomeado; o aviso da 011 dá lugar à Mesa
└── comissoes/                    # INALTERADO — nem guard, nem modelo, nem comando

specs/001-processo-seletivo-editais/contracts/openapi.yaml
    # EtapaPublicada e EtapaInput ganham os dois campos (T-014)

backend/tests/
├── unit/avaliacoes/              # a leitura da ausência, a validação da pontuação, a elevação
├── integration/avaliacoes/       # os comandos, com constraint, concorrência e idempotência
├── integration/publicacoes/      # histórico misto v4/v5: os quatro cenários de T-001
├── authorization/                # alocado sem atribuição, atribuição de outro, alocação removida
├── contract/                     # a forma publicada nova, contra o openapi.yaml
├── interface/                    # as cinco telas
└── acceptance/                   # a vertical inteira, com dois atores
```

**Structure Decision**: app novo `avaliacoes`, pela mesma linha que separou `comissoes` de
`processos` na 011 — domínio próprio, persistência própria, comandos próprios. As telas ficam em
`interface`, porque os dois atores desta feature são institucionais e já têm canal. O incremento
normativo é a única coisa que mora fora do app novo, e mora exatamente onde conteúdo normativo
sempre morou.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples rejeitada porque |
|---|---|---|
| App novo (`avaliacoes`) | A execução do trabalho tem persistência, comandos e ciclo próprios, e nenhuma relação com o ciclo normativo do Edital | Pôr os modelos em `comissoes` misturaria organizar o trabalho com executá-lo — as duas coisas que a 011 e a 012 existem para manter separadas — e faria a 013 herdar a confusão |
| Tripla `(identity_subject, etapa, inscrição)` copiada na Avaliação | FR-074 exige garantia de banco para "no máximo uma conclusão por pessoa, inscrição e Etapa", e a condição atravessa uma junção que índice não atravessa | Verificar só no comando deixaria a invariante que protege a 013 de contar duas vezes dependendo de todo caminho futuro lembrar de conferir. Copiar `membro_id` em vez da identidade estável seria pior que não copiar: a garantia cairia justamente no caso de remover e readicionar. A divergência que costuma condenar denormalização é impossível aqui — os três valores são escritos uma vez, na criação, e nunca atualizados |

## Restrições técnicas desta feature

1. **A elevação nunca escreve, e vale dentro do fluxo de Retificação — só ali.** Na elaboração, na
   composição e na consolidação, todo conteúdo lido da persistência passa por `elevar()` e todo
   conjunto de alterações — do banco ou da requisição — passa por `elevar_alteracoes()`, antes de
   qualquer uso. **Fora desse fluxo nada é elevado**: consulta pública, comprovante e documento de
   Publicação já existente servem o conteúdo literal, que é o que o `content_hash` cobre (T-002).
   Listar "três pontos", como a primeira redação fez, deixava descoberto o caso sem precondição —
   `ADD` não tem hash a conferir, e uma Retificação v4 em voo montaria `Publicacao` carimbada v5 com
   Etapa em forma v4 (T-001). Nenhuma linha de `VersaoConsolidada`, `Publicacao` ou
   `AlteracaoNormativa` é atualizada. Os oito cenários de T-001 são teste obrigatório.
1a. **O autor compõe sobre a projeção elevada**, e é dela que sai `expectedPreviousHash`. O editor
   deixa de montar formulário e diff sobre `base.content` cru; autor e servidor passam a conferir o
   mesmo objeto (T-015). Projetar não é persistir nem publicar.
2. **A ausência tem um leitor só.** Nenhum consumidor testa presença de chave por conta própria:
   `avaliacoes_previstas()` e `pontuacao_maxima()` são o lugar onde FR-009 e FR-066 vivem.
3. **A revogação é computada.** Nenhum ato da 011 — alocar, desalocar, remover membro — pode
   disparar escrita em Atribuição. Se aparecer uma, o desenho de D-004 foi abandonado (FR-069).
4. **Nenhuma listagem chama `pode_atuar_na_etapa`.** Listagem usa `etapas_autorizadas`; o guard
   individual serve rota individual. Um teste exige que as duas nunca divirjam.
5. **A permissão da 009 não é reutilizada.** Nada em `avaliacoes` chama `inscricao:consultar`, e
   nada em `inscricoes/application/consulta.py` muda.
6. **Os quatro atos da presidência passam por `comando_de_comissao`** — distribuir, **remover
   Atribuição**, impedir e reabrir. Bloqueio do Processo, reavaliação da autorização depois do
   bloqueio, recusa de Processo final e reserva de idempotência depois de autorizar — herdados
   inteiros, com as razões que a 011 documentou. `idempotency_key` é obrigatória nos quatro
   (FR-084, FR-086).
7. **A conclusão lê a versão dentro da transação que grava**, e a versão validada é a versão
   gravada. Duas leituras seriam uma Avaliação que afirma obedecer a regra contra a qual nunca foi
   verificada.
8. **Inativar Atribuição sob Avaliação concluída não é caminho comum.** O comando de redistribuição
   recusa; só impedimento e anulação declarada alcançam, e os dois gravam `AtoAdministrativo` com
   motivo (FR-092). O efeito sobre a Avaliação é o par de FR-075: **preservada e tornada
   inelegível**. Em código, nome de campo e mensagem de tela vale o termo preciso — `elegivel`,
   "inelegível" —, e nunca um nome que sugira que o registro foi alterado.
8a. **A identidade estável é a âncora do que é fato sobre a pessoa** — conclusão única (FR-074) e
   impedimento (FR-099). O vínculo de comissão é a âncora do que é trabalho distribuído — a
   Atribuição (D-004). Confundir os dois eixos reabre o contorno de remover-e-readicionar.
9. **Nenhuma tela da 012 mostra média, quórum, divergência, situação ou resultado**, e nenhuma
   consulta desta feature agrega avaliações de avaliadores diferentes.
