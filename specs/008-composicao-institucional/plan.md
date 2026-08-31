# Implementation Plan: Composição Institucional do Edital

**Branch**: `008-composicao-institucional` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-composicao-institucional/spec.md`

## Summary

Evoluir o compositor do documento para que o Edital publicado tenha aparência, hierarquia e
paginação de ato administrativo — **sem tocar domínio, snapshot, hash ou migration**. A feature
inteira vive em um arquivo de produção, `publicacoes/infrastructure/pdf.py`, mais dois pontos de
chamada que passam a entregar o contexto do ato.

O trabalho se divide em três naturezas, e a divisão governa o encadeamento:

1. **Capacidade de composição** — medir texto pela largura real, desenhar fio e contorno, paginar
   por bloco. São três capacidades estreitas, cada uma nasce **dentro** da entrega que a consome, e
   nenhuma nasce sozinha (FR-002 a FR-004, princípio VI).
2. **Materialização** — cabeçalho institucional, numeração normativa, Perfil em quadro, Cronograma
   em tabela, Etapas em pares rótulo-valor, órfãos e espaçamento.
3. **Fechamento do ato** — autoridade signatária e bloco de verificação discreto.

**A descoberta que mais determina o plano**: nos dois fluxos de publicação o documento é composto
**antes** de a `Publicacao` existir — `publish_edital.py:364` e `retificacoes.py:580` chamam o
renderizador e só depois executam `Publicacao.objects.create`. Isso decide FR-034 sozinho: o
compositor não pode ler a autoridade de lugar nenhum, ela **tem** de chegar por parâmetro. As duas
chamadas já têm o dicionário `signatory` em mãos nesse ponto, então o custo é zero.

**A segunda descoberta que mais economiza**: sete requisitos da primeira redação da spec já estavam
implementados e viraram invariantes. O plano não os planeja — ele os protege por teste de regressão.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** O compositor é
artesanal e não tem biblioteca de PDF; FR-005 proíbe introduzir uma, e nada nesta feature a exige.

**Storage**: PostgreSQL. **Nenhuma migration.** Nenhum campo, nenhuma tabela, nenhum dado a
converter.

**Testing**: pytest com `tests/{unit,contract,interface,integration,acceptance}`. A fixture de bytes
de `tests/contract/` é regenerada a cada entrega que muda a composição (FR-044).

**Target Platform**: servidor Linux; documento PDF 1.4, A4, fontes base-14 Helvetica e
Helvetica-Bold com `WinAnsiEncoding`.

**Project Type**: aplicação web Django em camadas por app. Esta feature toca apenas
`publicacoes/infrastructure/` e dois arquivos de `publicacoes/application/`.

**Performance Goals**: nenhuma meta nova. A composição é síncrona no ato de publicar, sobre dezenas
de Perfis no pior caso realista; a segunda passada de paginação é linear no número de linhas.

**Constraints**: a forma canônica não muda por motivo visual (FR-001); nenhuma imagem é embutida
(FR-008); o vocabulário visual é texto, fio e contorno (FR-003); a composição continua determinística
e o corpo normativo continua função pura do snapshot (FR-034, SC-013).

**Scale/Scope**: cinco entregas; 45 requisitos; um arquivo de produção reescrito por dentro; zero
entidade; zero migration; zero endpoint novo.

## Constitution Check

*GATE: avaliado contra a Constituição 1.1.1, antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Portão | Situação |
|---|---|---|
| I — Linguagem ubíqua | Nenhum conceito é renomeado nem duplicado | `Autoridade Signatária` já é termo da Constituição e chega ao compositor com esse nome. Nenhum termo novo de domínio nasce: bloco, fio e moldura são vocabulário de composição, não de domínio, e não aparecem em API, banco nem interface. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; cadeia demonstrável | A cadeia "dados estruturados → versão homologada → PDF publicado" **fica mais forte**: o corpo normativo continua função pura do snapshot (FR-034), e o único elemento externo — a autoridade — é metadado do ato, declarado e verificável. Publicação já praticada não é rematerializada (invariante de não regressão). **Passa** |
| III — Segurança, dados pessoais e auditoria | LGPD avaliada; auditoria não regride | A feature não coleta, não persiste e não expõe dado pessoal novo. Ela **imprime** nome e cargo já registrados na Publicação — que a Constituição exige que o ato registre — e nada além: sem CPF, matrícula, contato ou imagem (FR-037). Nenhum evento de auditoria muda. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; recusa explícita | FR-035 põe a regra no compositor e a faz recusar: publicado sem autoridade não compõe. A garantia não fica com quem chama — mesmo desenho que a `007` deu ao hash da prévia. **Passa** |
| V — Qualidade e simplicidade | Solução mais simples que preserve os requisitos | Nenhum padrão novo: sem biblioteca, sem serviço, sem DTO, sem camada de abstração para documentos futuros. Três capacidades estreitas, autorizadas nominalmente e limitadas a cinco regras de quebra. **Passa, com registro** — ver *Complexity Tracking* |
| VI — Completude de jornada | Cada entrega termina em cenário demonstrável pelo canal do ator | As cinco entregas terminam num documento aberto pela interface administrativa — prévia nas entregas 1 a 4, publicação na 5 — e conferido pela rubrica de catorze itens da spec. Nenhuma entrega é preparatória. **Passa** |

**Restrições e Invariantes do Domínio.** Uma incide diretamente:

- *"O PDF DEVE derivar dos dados estruturados e conteúdo homologado e corresponder exatamente à
  versão homologada. O documento DEVE ter identificação, versão e, quando apropriado, hash
  criptográfico."* Preservada por FR-038 a FR-040: a declaração de integridade **muda de lugar e de
  peso tipográfico, não de conteúdo**. O SHA-256 completo permanece, o abreviado permanece no
  rodapé, a afirmação de derivação permanece. O que sai do corpo do ato é `Versão do schema`, que
  continua no snapshot e no mecanismo.

**Fluxo de Desenvolvimento — divergência declarada.** A spec contém âncoras técnicas que o template
desaprova, e o checklist a registra em `checklists/requirements.md` como divergência deliberada,
12/16. Este plano é onde a Constituição manda que o desenho viva, e é o que o `research.md` faz: as
seis decisões que a spec fechou como **limite** aparecem lá como **decisão**, com alternativa
recusada.

**Conclusão do portão, sem arredondar.** Os **seis princípios centrais passam**. A conformidade
constitucional desta feature **não é integral**: permanece uma divergência declarada no *Fluxo de
Desenvolvimento* — a spec conserva âncoras técnicas que o template manda deixar para o plano —,
registrada em `checklists/requirements.md` como 12/16 e aceita pela Governance na forma de
divergência documentada, como a `007` já fizera. Dizer "6/6 passa" sem esta ressalva seria
apresentar como conformidade completa aquilo que é conformidade com exceção registrada.

**Reavaliação pós-Fase 1**: sem violações novas. Uma entrada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/008-composicao-institucional/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — as dez decisões de desenho e o que foi recusado
├── data-model.md        # Fase 1 — estruturas de composição; nenhuma entidade, nenhuma migration
├── quickstart.md        # Fase 1 — como demonstrar e validar cada entrega
├── contracts/
│   └── composicao.md    # Entrada do compositor, o que a página materializa, o que não muda
├── checklists/
│   └── requirements.md  # Qualidade da spec (12/16, divergência declarada)
├── referencias/
│   └── estado-inicial-apos-007.pdf  # O documento que o sistema produz hoje — o "antes"
└── tasks.md             # Fase 2 — criado pelo $speckit-tasks, não por este comando
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   └── publicacoes/
│       ├── infrastructure/
│       │   ├── pdf.py            # A feature inteira vive aqui: métrica, primitivas,
│       │   │                     # blocos, paginação, cabeçalho, quadros, tabelas,
│       │   │                     # assinatura e bloco de verificação
│       │   └── humano.py         # Formatação humana já existente; reusada, não ampliada
│       └── application/
│           ├── publish_edital.py # Passa a entregar o contexto do ato ao compositor
│           └── retificacoes.py   # Idem, no fluxo consolidado (FR-043)
├── scripts/
│   └── gerar_fixture_documento.py # Passa a usar a autoridade fixa versionada (FR-044)
└── tests/
    ├── unit/publicacoes/test_pdf.py          # Conteúdo e estrutura do documento
    └── contract/
        ├── test_documento_publicado.py       # Bytes congelados + contrato de modo
        └── fixtures/
            ├── snapshot_publicado.json       # Existente
            ├── autoridade_publicada.json     # **Novo** — autoridade fixa da fixture
            └── documento_publicado_v1.pdf    # Regenerado a cada entrega que muda a composição
```

**Referências visuais — tarefa bloqueante da entrega 1.** O estado inicial está versionado em
`referencias/estado-inicial-apos-007.pdf`: é o documento que o sistema produz hoje, e serve de
"antes" para todas as comparações. **Falta o alvo** — ao menos um Edital oficial do Cefor. Isso é a
primeira tarefa da entrega 1 e a bloqueia: sem alvo, os itens R-01 a R-03 da rubrica não têm contra
o quê ser conferidos. Não bloqueia o `$speckit-tasks`.

**Structure Decision**: nenhuma estrutura nova. A feature é uma reescrita interna de um módulo de
infraestrutura existente, mais dois pontos de chamada e um script. O app `interface/` só é tocado se
a demonstração revelar necessidade, e hoje não revela: a prévia já chama o mesmo compositor.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples recusada porque |
|---|---|---|
| **Um algoritmo de layout estreito** dentro do compositor: métrica de largura, paginação em duas passadas, blocos aninhados em três níveis, linha de tabela fragmentável, repetição de cabeçalho e moldura por continuação (FR-002 a FR-004) | Cabeçalho centralizado, tabela com coluna alinhada, quadro delimitado e "Perfil não partido no meio" são inexprimíveis sem isso. Hoje a composição só escreve texto, mede largura contando caracteres e pagina uma lista plana de linhas | *Manter o compositor como está e aproximar com espaço em branco* produziria exatamente o defeito que a feature existe para corrigir — coluna torta e centro fora do centro. *Trocar por uma biblioteca de PDF* é vedado por FR-005 e traria dependência, superfície e perda do controle byte a byte de que a fixture contratual depende |

**Esta entrada é a única, e é a que mais merece atenção nas tarefas.** Chamá-la de "três capacidades
pequenas" subestimaria: as seis peças interagem, e a maior parte das falhas possíveis é silenciosa —
o documento sai, apenas errado. O limite que a mantém estreita é nominal e verificável: sem
hifenização, sem justificação, sem fonte nova, sem imagem, sem restrição declarativa, sem motor de
caixas, e a quebra por bloco serve **somente** às cinco regras de FR-020, FR-021, FR-022, FR-026 e
FR-030. A tabela de interações de `research.md` (D-004) enumera os seis modos de falha silenciosa, e
cada um vira teste antes de virar código.

## Restrições técnicas desta feature

*Estas restrições estavam na primeira redação da spec como FR-005 e como "Instruções para o
`/plan`". São decisões de implementação, e a Constituição manda que vivam aqui.*

**R-T1 — O mecanismo de geração do documento não é substituído.** Nenhuma dependência de
renderização é introduzida, salvo impedimento concreto e demonstrado para cumprir um requisito da
spec — caso em que o impedimento se registra em `research.md` **antes** de a substituição começar.
Trocar por uma biblioteca de PDF traria dependência, superfície e a perda do controle byte a byte de
que a evidência contratual depende.

**R-T2 — Solução específica antes de solução genérica.** Havendo uma solução simples específica para
o Edital e uma genérica para documentos futuros, usar a específica. Não construir camada de
abstração para tipo de documento que não existe, nem design system de documentos.

**R-T3 — As três capacidades de FR-002, FR-003 e FR-004 são necessárias e não devem ser evitadas.**
Tabela fingida com espaço, cabeçalho centralizado por contagem de caractere e Perfil partido no meio
são o resultado de evitá-las. O que continua proibido é generalizá-las.

**R-T4 — A autoridade entra por parâmetro, nunca pelo conteúdo publicado.** Qualquer proposta que a
acrescente ao snapshot viola P-001 e FR-034, e quebraria hash, reprodutibilidade e endereçamento de
Retificação de uma vez. Os dois chamadores já têm o dado (D-005).

**R-T5 — A numeração é atribuída depois da filtragem.** É o único defeito desta feature que não
aparece no cenário-base: só se manifesta num Edital sem Etapas de Avaliação (D-006).

**R-T6 — Três chamadores, uma composição.** Publicação, Retificação e prévia usam o mesmo
compositor. A Retificação é fácil de esquecer porque não tem tela própria de prévia.

**R-T7 — Nada aqui é migration.** Se aparecer campo persistido, tabela, migration ou permissão nova,
o requisito foi lido errado.
