# Implementation Plan: Inscrição Simples e Documentos do Candidato

**Branch**: `009-inscricao-simples-documentos` | **Date**: 2026-08-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-inscricao-simples-documentos/spec.md`

## Summary

Abrir o sistema para um ator que ele nunca teve — a pessoa de fora — e fechar o ciclo do lado de
dentro: o Edital passa a declarar quando as inscrições abrem e o que o candidato precisa apresentar;
o candidato encontra a vaga, identifica-se, preenche o mínimo, envia PDFs e recebe protocolo; a
equipe abre cada documento sob o requisito que ele atende.

O trabalho tem três naturezas, e a divisão governa o encadeamento:

1. **Extensão normativa** — o contrato operacional de inscrição entra no domínio, no conteúdo
   publicado e no documento. É a única parte que incrementa a versão canônica, e ela incrementa
   **uma vez só** (entrega 2).
2. **Canal novo** — um segundo canal HTML, público, com identidade própria e nenhuma capacidade de
   gestão. Não é uma tela nova do `interface`; é o outro lado do produto (entregas 1, 3, 4 e 5).
3. **Capacidade nova de infraestrutura** — armazenamento privado de arquivo, que o projeto não tem.
   Nasce dentro da entrega que a consome (entrega 4), não antes.

**A descoberta que mais economiza**: quase tudo o que a jornada do candidato precisa de garantia já
existe e serve sem alteração. A idempotência de comando é indexada por `(escopo, ator, operação,
chave)` e aceita qualquer ator; a auditoria grava estado e revisão do agregado, e é por isso que
`FR-033` pede os dois na Inscrição; o padrão de imutabilidade por `save()` que recusa atualização
está em cinco modelos; a guarda `_exigir` de produção já recusa subir com o seletor de identidade
ligado. Nenhum desses mecanismos precisa mudar para servir a quem não é da instituição.

**A descoberta que mais determina o desenho**: a designação do período de inscrições cabe **dentro
do Evento**, como marca, e não como entidade, chave nova na raiz ou taxonomia de tipos. Isso torna o
incremento canônico pequeno — um campo booleano no Evento publicado e uma coleção nova na raiz — e
faz o apontamento já nascer endereçável pela Retificação, sem tocar a gramática (D-001, D-002).

**A segunda que mais economiza**: o catálogo de seções já tem `inscricao`, e a enunciação dos
documentos exigidos entra como seção **gerada** ao lado dela, pelo mesmo mecanismo que já compõe
Perfis, Etapas e Cronograma a partir de uma coleção do snapshot (D-003). Nenhuma linguagem
documental nova.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** O progresso de envio
usa o htmx já embarcado (`interface/static/interface/htmx.min.js`); a verificação de PDF é a
assinatura dos primeiros bytes, e `FR-045` proíbe biblioteca de inspeção de tipo.

**Storage**: PostgreSQL para os registros; **sistema de arquivos privado** para os documentos do
candidato, por armazenamento configurado na aplicação, fora da árvore estática e não servido pelo
servidor web (D-006). Migrations novas: uma em `editais` (marca do Evento e Documento Exigido) e uma
em `inscricoes` (Inscrição e Documento Submetido).

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. A suíte roda contra PostgreSQL apenas com
`TEST_DB_ENGINE=postgresql`; sem isso cai para SQLite em memória e as constraints parciais desta
feature não são exercidas.

**Target Platform**: servidor Linux; navegador do candidato incluindo **celular** — `FR-079` fixa
375 px sem rolagem horizontal, e é a primeira vez que o produto assume esse alvo.

**Project Type**: aplicação web renderizada no servidor, com fragmentos htmx. Dois canais HTML:
`interface` (institucional, existente) e `portal` (público, novo).

**Performance Goals**: nada de vazão. O alvo é de percurso: `SC-UX-001` fixa duas telas, dois envios
e três acionamentos até o protocolo, e `FR-048` exige progresso visível durante o envio.

**Constraints**: a forma canônica só muda na entrega 2 e uma vez; o candidato nunca recebe permissão
institucional; nenhuma resposta com dado pessoal é armazenável pelo navegador; nenhum arquivo é
alcançável por conhecer o endereço.

**Scale/Scope**: centenas a poucos milhares de inscrições por seleção, com até 10 MB por documento.
Três modelos novos — `DocumentoExigido` em `editais`, `Inscricao` e `DocumentoSubmetido` em
`inscricoes` —, dois apps novos, uma coleção nova no conteúdo publicado, uma seção nova no catálogo,
seis entregas navegáveis.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos, identificadores estáveis, invariantes em constraint | `Documento Exigido`, `Inscrição`, `Candidato` e `Documento Submetido` já são termos da Constituição e nascem com esse nome. Unicidade de inscrição, de documento por requisito e de protocolo vão para o banco (D-014). Identificador público não autoriza: a titularidade é verificada (D-009). **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | `FR-011` faz o candidato consumir a versão consolidada vigente, nunca o rascunho; `FR-058` grava a versão aceita e `FR-059a` a reconhecida. O incremento canônico é único e declarado, com a consequência assumida na precondição 1 da spec. **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | O candidato é ator sem permissão nenhuma: todo comando institucional o recusa por construção. Titularidade é eixo próprio e testado em `tests/authorization`. Coleta mínima (`FR-036`), CPF fora de endereço e mascarado, `no-store` em toda resposta com dado pessoal, retenção como gate declarado. Auditoria dos três atos do candidato, sem CPF completo. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Toda revalidação do envio é de servidor (`FR-060`); dois estados e nada mais; `compare_and_swap` e `reserve()` já existentes cobrem perda de atualização e duplo envio. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | Cada FR tem cenário e teste previstos; a forma publicada nova é transcrita do contrato e conferida por teste, como as demais. Nenhum motor genérico: quatro combinações de aplicabilidade, sem expressão. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | As seis entregas terminam em comportamento navegável, e o ator de cada uma tem o canal correspondente: o público no `portal`, o institucional no `interface`. **Passa** |

Duas exceções vão para `Complexity Tracking`: dois apps novos e uma capacidade de infraestrutura
que o projeto não possuía.

**Reavaliação após a Fase 1**: o desenho não introduziu violação nova e fechou dois pontos que a
Constituição cobrava e o gate inicial ainda deixava em aberto. O princípio I ganhou o que faltava —
as quatro unicidades da feature são `UniqueConstraint`, e a designação do período é constraint
parcial em vez de conferência em código (D-001, `data-model.md` §8). O princípio IV ficou explícito
nas duas conferências novas de publicação, que recusam o estado que só uma Retificação alcança. As
três exceções de complexidade permanecem as mesmas, com as alternativas rejeitadas registradas em
`research.md`. Nenhuma dependência nova, nenhuma entidade além das duas, nenhum mecanismo genérico.

## Project Structure

### Documentation (this feature)

```text
specs/009-inscricao-simples-documentos/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — as decisões
├── data-model.md        # Fase 1 — entidades, invariantes e forma publicada
├── quickstart.md        # Fase 1 — como demonstrar cada entrega
├── contracts/
│   └── inscricao.md     # Fase 1 — forma publicada nova e superfícies HTML
├── checklists/
│   └── requirements.md  # Da fase de especificação
└── tasks.md             # Fase 2 — criado pelo $speckit-tasks, não por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/
│   │   ├── cronograma.py        # + marca do período de inscrições no Evento
│   │   └── documentos.py        # NOVO — DocumentoExigido do Edital
│   ├── domain/
│   │   ├── secoes.py            # + seção gerada "documentos-exigidos"
│   │   ├── documentos.py        # NOVO — validação da forma e da aplicabilidade
│   │   └── validation.py        # + forma publicada e coerência da marca única
│   ├── application/draft.py     # + a coleção nova no rascunho
│   └── migrations/              # + uma migration
├── publicacoes/
│   ├── application/publish_edital.py   # + as duas mudanças no snapshot; SCHEMA_VERSION 4
│   ├── domain/colecoes.py             # + /documentRequirements como coleção com chave
│   └── infrastructure/pdf.py          # + composição da seção gerada (conflita com a 008)
├── inscricoes/                  # NOVO — o domínio da jornada
│   ├── models.py                # Inscricao, DocumentoSubmetido
│   ├── domain/
│   │   ├── aplicabilidade.py    # quais requisitos valem para (Perfil, modalidade)
│   │   ├── arquivos.py          # aceitação de PDF, limite, nome físico, resumo
│   │   ├── protocolo.py         # geração e alfabeto
│   │   └── titularidade.py      # quem pode ver o quê
│   ├── application/
│   │   ├── rascunho.py          # abrir, gravar campos, anexar e substituir arquivo
│   │   └── submissao.py         # revalidação integral, protocolo, auditoria
│   ├── storage.py               # armazenamento privado configurado
│   └── migrations/
├── portal/                      # NOVO — o canal público e do candidato
│   ├── identidade.py            # eixo próprio, sessão própria, provedor de demonstração
│   ├── views.py                 # vitrine, vaga, inscrição, revisão, comprovante
│   ├── arquivos.py              # entrega mediada do documento ao titular
│   ├── urls.py
│   ├── templates/portal/        # base própria, responsiva
│   └── static/portal/           # progresso de envio
├── interface/
│   ├── views.py                 # + etapa "Inscrição" do assistente; + Inscrições do Edital
│   ├── forms.py                 # + leitura da etapa
│   └── templates/interface/     # + as duas telas administrativas
└── shared/templates/            # NOVO — parcial de tokens visuais, incluída pelas duas bases

backend/tests/
├── unit/{editais,inscricoes}/   # aplicabilidade, aceitação de arquivo, protocolo
├── integration/{editais,inscricoes,portal}/
├── authorization/               # titularidade e ausência de permissão institucional
├── contract/                    # forma publicada nova, transcrita do contrato
└── acceptance/                  # o percurso do SC-017, com dois atores
```

**Structure Decision**: dois apps novos, pela mesma linha que já separa `interface` de
`publicacoes`: `inscricoes` guarda domínio e persistência da jornada; `portal` é o canal do ator
externo, espelhando o papel que `interface` cumpre para o ator institucional. As telas
administrativas da US6 ficam em `interface`, onde o Edital já é administrado.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples rejeitada porque |
|---|---|---|
| Dois apps novos (`inscricoes`, `portal`) | A jornada tem domínio próprio, e o canal do candidato tem autenticação, sessão, base visual e alvo de dispositivo distintos do administrativo | Pôr as telas do candidato em `interface` faria o canal herdar o processador de contexto institucional, o cabeçalho de gestão e a mesma chave de sessão — o que `FR-021` proíbe. Um app único misturaria domínio e canal, que o projeto separa desde a `002` |
| Armazenamento de arquivo, capacidade que o projeto não tem | `FR-051` a `FR-053` exigem arquivo privado, mediado e verificável, e não há nada equivalente no repositório | Reusar a coluna binária de `DocumentoPublicado` foi considerado e rejeitado em D-006: lá é um documento imutável por publicação; aqui são dezenas de megabytes por candidato, substituíveis durante o rascunho |
| Seção nova no catálogo | `FR-010` exige o documento enunciando os documentos exigidos, derivados dos dados | Compor dentro da seção textual `inscricao` faria uma seção ser textual e gerada ao mesmo tempo, quebrando a invariante do catálogo — "cada tipo usa um, e nunca os dois" |

## Restrições técnicas desta feature

1. **A entrega 2 parte da 008 integrada.** As duas escrevem em
   `publicacoes/infrastructure/pdf.py`; a 008 não toca a camada canônica, então não há disputa de
   versão — há disputa de arquivo. Começar a entrega 2 antes do merge significa compor o documento
   duas vezes.
2. **Um incremento, uma entrega.** A marca do Evento, a coleção nova e a seção nova viajam juntas na
   entrega 2. Nenhuma outra entrega altera `SCHEMA_VERSION`, o snapshot, o hash ou a gramática de
   endereçamento.
3. **O candidato nunca vira ator institucional.** O `Actor` derivado da identidade externa existe
   apenas para atravessar idempotência e auditoria, sempre com conjunto de permissões vazio. Se
   qualquer comando administrativo passar a aceitá-lo, a regra foi violada.
4. **A fonte do que se pede é o conteúdo publicado.** Nenhuma view do `portal` consulta
   `PerfilVaga`, `ModalidadeConcorrencia` ou `DocumentoExigido` da elaboração.
5. **Nenhuma dependência nova**, nem de Python nem de frontend.
