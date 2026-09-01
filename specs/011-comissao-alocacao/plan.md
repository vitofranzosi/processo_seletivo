# Implementation Plan: Gestão da Comissão e Alocação por Etapa

**Branch**: `011-comissao-alocacao` | **Date**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-comissao-alocacao/spec.md`

## Summary

Dar ao sistema a resposta para "quem trabalha neste Processo e em qual Etapa?", e parar ali. O
gestor constitui a comissão do Processo, designa presidente, aloca membros às Etapas dos Editais
publicados e enxerga a distribuição por Edital; o membro entra e vê apenas as Etapas em que tem
atribuição; quem não foi alocado recebe a mesma resposta que receberia se a Etapa não existisse.

O trabalho tem duas naturezas, e a segunda é a que dá valor à primeira:

1. **Duas entidades operacionais** — `MembroComissao` e `AlocacaoEtapa`, num app novo, sem tocar
   nada de normativo.
2. **Uma camada de autorização contextual** — a função que responde "esta pessoa pode acessar esta
   Etapa?" olhando o objeto, e não o papel. É o produto real da feature, e é o que a 012 herda como
   contrato.

**A descoberta que mais determina o desenho**: a Etapa publicada e a linha de elaboração podem não
coincidir. `EtapaAvaliacao` é lida uma única vez fora da elaboração, para montar o snapshot; depois
disso o conteúdo evolui por Retificação, que não escreve de volta nas tabelas de `editais` e sabe
acrescentar item a coleção com chave. Existe, portanto, Etapa real no Edital vigente sem linha
alguma para uma chave estrangeira apontar (D-002). A alocação designa a Etapa pela identidade que o
conteúdo publicado carrega, como `Inscricao.profile_id` já faz desde a 009.

**A que mais economiza**: quase toda garantia que esta feature precisa já existe.
`effective_version` devolve a Versão Consolidada vigente e vira o resolvedor único de Etapas
(D-012); `reserve()` cobre o reenvio de formulário; `command_context()` abre a transação;
`record_event` grava a trilha com dois parâmetros opcionais a mais e nenhuma coluna nova (D-014); e
`require_permission` continua respondendo pela capacidade sistêmica, com a base contextual ao lado,
numa função só (D-011).

**A que mais encurta a feature**: não há canal novo. A 009 precisou de um app de canal porque tinha
um ator de fora; aqui os dois atores são institucionais, autenticados pelo mesmo mecanismo, na mesma
base visual. Tudo o que se vê nasce em `interface`.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** Nenhuma superfície de
API: a feature inteira é servida pelo canal HTML institucional, com os fragmentos htmx já
embarcados.

**Storage**: PostgreSQL. Uma migration nova, em `comissoes`, com dois modelos e quatro constraints.
**Nenhuma migration altera `editais`, `publicacoes` ou `auditoria`** — a única mudança fora do app
novo é a assinatura de `record_event`, que não toca esquema.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration` e
`authorization` já declarados. As constraints parciais desta feature só são exercidas com
`TEST_DB_ENGINE=postgresql`; sem isso a suíte cai para SQLite e a unicidade de vínculo ativo passa
sem ser testada.

**Target Platform**: servidor Linux; navegador do servidor institucional, incluindo celular — a
organização por Etapa precisa caber em 375 px sem tabela horizontal (`FR-081`).

**Project Type**: aplicação web renderizada no servidor, com fragmentos htmx. Um canal só, o
`interface`.

**Performance Goals**: nada de vazão. O alvo é de percurso: o gestor precisa ver, numa visão só,
quais Etapas têm e quais não têm equipe (`SC-UX-001`), e o membro precisa chegar às próprias Etapas
sem passar por tela administrativa (`SC-UX-003`).

**Constraints**: nenhuma operação da feature altera revisão, snapshot, hash ou documento publicado;
a autorização é sempre verificada no servidor e sempre sobre o objeto pedido; alocação só existe
para Etapa de Edital publicado; e nenhuma tela desta feature mostra dado de candidato.

**Scale/Scope**: dezenas de membros por Processo e poucas Etapas por Edital — a escala é de ata, não
de tráfego. Dois modelos novos, um app novo, quatro rotas novas, uma permissão nova, três entregas
navegáveis.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; identificador público não autoriza; invariantes em constraint | `Comissão` e `Presidente da Comissão` já são termos da Constituição e nascem com esse nome. As quatro unicidades vão para o banco como constraint parcial (D-013). Identificador não autoriza: o guard verifica o vínculo, e a URL de uma atribuição não carrega pessoa (D-015). A integridade referencial da Etapa é preservada no comando, pela mesma razão e com o mesmo precedente da `Inscricao` (D-002). **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | A fonte das Etapas é a Versão Consolidada vigente, por um resolvedor único (D-012). Nada da 011 entra no conteúdo publicado, na consolidação ou no hash; nenhuma migration toca `editais` ou `publicacoes` (`FR-083`, `SC-018`). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | Autorização por objeto, verificada no servidor, com 404 uniforme para tudo que o ator não alcança (D-017). Menor privilégio: participar não é administrar, e alocação numa Etapa não alcança outra. Dado pessoal é mínimo por construção — a feature guarda um identificador institucional e um rótulo opcional, e nenhum dado de candidato. As cinco operações vão para a trilha existente (D-014). **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Toda regra vive no comando; a tela não decide nada. Não há máquina de estados porque não há ciclo de vida: há presença, e ela é booleana com histórico (D-013) — a Constituição pede estados para workflow, e inventar um aqui seria o oposto do que ela quer. Concorrência tratada onde ela existe de fato: constraint parcial para duplicidade, `select_for_update` para o invariante de presidência, `reserve()` para reenvio (D-016). **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | Cada FR tem cenário previsto em [quickstart.md](./quickstart.md), e os quatro grupos de teste são os que a feature exige: autorização, integração, aceitação e regressão de Retificação. Nenhum mecanismo genérico de permissões: uma função de duas linhas responde pela autorização contextual, e é a mais simples que preserva os requisitos. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | As três entregas terminam em comportamento navegável no `interface`, que é o canal dos dois atores. A entrega 1 é a jornada inteira no caminho feliz, e a negação faz parte dela: sem o 404 demonstrado, a feature não entregou o que promete. **Passa** |

Uma exceção vai para `Complexity Tracking`: o app novo.

**Reavaliação após a Fase 1**: o desenho não introduziu violação nova e fechou dois pontos que o
gate inicial deixava em aberto. O princípio I ganhou o que faltava — as quatro unicidades são
`UniqueConstraint` parcial, e a coerência `etapa → edital → processo` é verificada no comando porque
o banco não pode expressá-la sem a chave estrangeira que D-002 proíbe; a alternativa foi registrada
em vez de silenciada. O princípio IV ficou explícito no único invariante multi-linha da feature, que
é a presidência, e no bloqueio que o protege. A exceção de complexidade permanece uma só. Nenhuma
dependência nova, nenhum modelo além dos dois, nenhuma coluna nova em tabela existente.

## Project Structure

### Documentation (this feature)

```text
specs/011-comissao-alocacao/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — a reconciliação (D-001 a D-009) e as decisões de implementação (D-010 a D-017)
├── data-model.md        # Fase 1 — entidades, invariantes e o resolvedor de Etapas
├── quickstart.md        # Fase 1 — como demonstrar cada entrega
├── contracts/
│   └── comissao.md      # Fase 1 — as superfícies HTML e o contrato de autorização
├── checklist-ux.md      # Da fase de especificação — critérios transversais herdados
└── tasks.md             # Fase 2 — criado pelo $speckit-tasks, não por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── comissoes/                    # NOVO — o domínio da organização do trabalho
│   ├── models.py                 # MembroComissao, AlocacaoEtapa
│   ├── domain/
│   │   ├── autorizacao.py        # pode_gerir_comissao() e pode_atuar_na_etapa() — as duas perguntas
│   │   ├── etapas.py             # etapas_vigentes(): o resolvedor único, sobre effective_version
│   │   └── funcoes.py            # PRESIDENTE e MEMBRO, e o invariante de presidência
│   ├── application/
│   │   ├── comissao.py           # adicionar, alterar função, remover membro
│   │   ├── alocacao.py           # alocar, remover alocação
│   │   └── selectors.py          # a visão administrativa e Minhas Etapas, com as órfãs derivadas
│   └── migrations/               # uma migration
├── auditoria/
│   └── application.py            # + new_state e new_revision opcionais (D-014); nenhuma migration
├── interface/
│   ├── identidade.py             # + "comissao:gerir" no papel gestor
│   ├── views.py                  # + comissao, alocacoes, minhas_etapas, atribuicao
│   ├── forms.py                  # + membro e alocação
│   ├── urls.py                   # + quatro rotas (D-015)
│   └── templates/interface/
│       ├── comissao.html
│       ├── alocacoes.html
│       ├── minhas_etapas.html
│       ├── atribuicao.html
│       └── _membro.html          # fragmento htmx da linha de membro
└── processos/                    # inalterado

backend/tests/
├── unit/comissoes/               # o resolvedor, o invariante de presidência, a derivação de órfã
├── integration/comissoes/        # os comandos, com constraint e concorrência
├── authorization/                # o guard: outro Processo, outra Etapa, outro escopo, sem vínculo
├── interface/                    # as quatro telas
└── acceptance/                   # o percurso da seção 49, com dois atores
```

**Structure Decision**: um app novo, `comissoes`, pela mesma linha que já separa `inscricoes` de
`editais` — domínio próprio, persistência própria, comandos próprios. As telas ficam em `interface`
porque o canal é o institucional, que já existe: ao contrário da 009, esta feature não traz ator
novo nem base visual nova. `auditoria` recebe a única mudança fora do app novo, e ela é de
assinatura, não de esquema.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples rejeitada porque |
|---|---|---|
| App novo (`comissoes`) | A comissão é autorização operacional sobre Processo e Etapa, com ciclo próprio e nenhuma relação com o ciclo normativo | Pôr os modelos em `processos` faria o agregado normativo carregar `related_name` de autorização e entregaria essa confusão à 012, que acrescenta `Avaliacao` sobre a mesma base (D-010) |

## Restrições técnicas desta feature

1. **A alocação nunca referencia `EtapaAvaliacao`.** Nem por chave estrangeira, nem por consulta:
   `edital.etapas.all()` responde pela coleção de elaboração e diverge do conteúdo vigente depois de
   uma Retificação. Toda leitura de Etapa passa por `etapas_vigentes()` (D-012).
2. **Nenhuma escrita fora de `comissoes`.** Nenhuma migration em `editais`, `publicacoes` ou
   `auditoria`; nenhum comando desta feature grava em tabela que não seja sua.
3. **A presidência não vira papel.** `comissao:presidir` existe como rótulo de trilha e não pode
   aparecer em `PAPEIS` (D-011, D-014).
4. **A autorização é uma função só, chamada por todos.** Duplicar a regra na view e no comando é
   como ela passa a divergir; a view chama a mesma função do domínio, para decidir o que desenhar.
5. **Alocação exige Edital publicado e comissão com presidente.** As duas recusas são do comando, e
   a tela as antecipa em vez de deixar o usuário descobrir no envio.
6. **Nenhuma tela desta feature mostra dado de candidato**, e nenhuma consulta desta feature toca
   `inscricoes`.
