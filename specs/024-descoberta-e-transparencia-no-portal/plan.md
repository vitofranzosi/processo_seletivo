# Implementation Plan: Descoberta e Transparência no Portal Público

**Branch**: `claude/spec-selecoes-ifrn-ifes-0a59c7` | **Date**: 2026-09-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/024-descoberta-e-transparencia-no-portal/spec.md`

---

## Summary

Duas telas públicas do portal do candidato passam a mostrar o que o ato publicado já diz — o
cronograma, os campos da vaga que descrevem o trabalho, e o histórico de Retificações — e a vitrine
ganha busca, filtros, ordenação e situação explícita.

**A abordagem técnica cabe numa frase: nada de novo é gravado, e quase nada de novo é calculado.**
Das seis capacidades que a feature entrega, três são renderização de dado já publicado, uma reusa
uma função que já existe noutra tela, uma reusa um padrão de formulário que já existe na gestão, e
só uma é código genuinamente novo — o tradutor que diz, em linguagem do domínio, o que uma
Retificação alterou.

Isso decide a forma do plano: **sem migration, sem modelo, sem contrato de API novo**. O trabalho é
de leitura, tradução e apresentação.

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2 (views e templates do portal); nenhuma dependência nova

**Storage**: PostgreSQL — **somente leitura**. Nenhuma migration, nenhuma tabela, nenhuma coluna

**Testing**: pytest + pytest-django; integração em `tests/integration/portal/`, acessibilidade em
`tests/interface/test_acessibilidade_do_portal.py`

**Target Platform**: servidor web; o portal é escrito para o celular primeiro (375 px) e alarga
depois

**Project Type**: monólito Django, canal público server-side, sem SPA e sem build de front

**Performance Goals**: a vitrine responde de imediato num navegador comum, sem consulta nova ao
banco: busca, filtro e ordenação operam sobre o conjunto que a página já carrega (`D-003`). A página
da seleção acrescenta **uma** consulta — os atos publicados daquele Edital

**Constraints**: sem JavaScript obrigatório (`UX-017`); sem identificação em nenhuma tela
(`FR-150`); sem escrita de espécie alguma, inclusive trilha e contador (`FR-151`, `SC-047`)

**Scale/Scope**: dezenas de seleções publicadas simultâneas; duas telas; um punhado de atos
publicados por Edital

**Nenhum NEEDS CLARIFICATION.** As onze questões técnicas estão resolvidas em
[research.md](research.md).

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | O tradutor da `T-002` existe **por causa** deste princípio: `target_path` é vocabulário do sistema, e a página passa a dizer Perfil, Evento, Anexo, Etapa. Nenhum termo novo é inventado | ✅ |
| **II — Integridade normativa e imutabilidade** | A feature **só lê**. O conteúdo exibido é sempre o consolidado vigente; cada ato publicado permanece alcançável pelo documento dele; publicar e entrar em vigor continuam instantes distintos. O texto do PDF publicado **não** é tocado (`T-010`) | ✅ |
| **III — Segurança e proteção de dados** | Nenhum dado pessoal é lido ou exibido — as duas telas são anônimas por natureza. A `D-008` recusa explicitamente instrumentação de comportamento, que seria o único jeito de esta feature tocar em LGPD. O saneamento da consulta (`T-007`) fecha a superfície de redirecionamento | ✅ |
| **IV — Regras explícitas** | Nenhuma regra de domínio nova. A classificação do período continua sendo a função pura que já existe, e a feature não a duplica | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md) e camada de teste na `T-008`. A simplicidade é o eixo: a `D-003` recusa construir índice para um catálogo que cabe numa tela, e nomeia o sinal que mudaria isso | ✅ |
| **VI — Completude de jornada** | É o princípio que **motiva** a feature: o cronograma publicado é capacidade que o domínio sustenta e que nenhuma interface pública alcança — pela definição do princípio, não está entregue. O cenário demonstrável é o percurso anônimo do quickstart, pelo canal do próprio ator | ✅ |

### Invariantes do domínio tocados

| Invariante | Efeito |
|---|---|
| "Cada Edital DEVE ter Cronograma próprio… Alterações após Publicação DEVEM ocorrer por Retificação" | a feature torna as duas coisas visíveis; não altera nenhuma |
| "O PDF DEVE derivar dos dados estruturados e corresponder à versão homologada" | intocado — `T-010` isola a mudança de redação no portal |
| "Registros normativos NÃO DEVEM ser fisicamente excluídos" | nada é excluído; a feature é leitura |
| "APIs DEVEM ter contratos explícitos" | nenhuma API é alterada; o contrato desta feature é de rota HTML, em [contracts/portal-publico.md](contracts/portal-publico.md) |

**Sem violações. A tabela de Complexity Tracking fica vazia, e é a conclusão certa:** uma feature
que não persiste nada e não introduz dependência não tem complexidade a justificar.

---

## Project Structure

### Documentation (this feature)

```text
specs/024-descoberta-e-transparencia-no-portal/
├── plan.md              # este arquivo
├── spec.md              # a especificação
├── research.md          # T-001 a T-011, todas resolvidas
├── data-model.md        # modelos de leitura; nenhuma persistência
├── quickstart.md        # validação de ponta a ponta, sem sessão
├── contracts/
│   └── portal-publico.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── portal/
│   ├── views.py                     # vitrine ganha consulta; seleção ganha cronograma, atos e vaga completa
│   ├── leitura.py                   # NOVO — o cronograma que sai de views.py (T-003) e o saneamento da consulta
│   └── templates/portal/
│       ├── vitrine.html             # busca, filtros, contagem, quatro grupos
│       ├── _cartao_da_selecao.html   # situação explícita, comparabilidade (UX-016)
│       ├── _consulta.html           # NOVO — o formulário de busca e filtros
│       ├── selecao.html             # cronograma, histórico, campos da vaga
│       ├── _cronograma.html         # NOVO — a lista de Eventos, compartilhada com acompanhamento
│       ├── _historico.html          # NOVO — os atos publicados
│       └── acompanhamento.html      # passa a incluir o parcial de cronograma
├── publicacoes/
│   ├── application/selectors.py     # NOVO selector: atos publicados de um Edital (T-001)
│   └── domain/alteracoes.py         # NOVO — target_path → linguagem do domínio (T-002)
├── shared/
│   └── texto.py                     # NOVO — dobra de acento e caixa (T-005)
└── comissoes/application/selectors.py  # passa a delegar a dobra a shared (T-005)

backend/tests/
├── integration/portal/
│   ├── test_vitrine.py              # ampliado: consulta, grupos, contagem
│   ├── test_detalhe_selecao.py      # ampliado: cronograma, campos da vaga, reserva
│   └── test_historico_publico.py    # NOVO — os atos, com a fixture `retify`
├── unit/
│   ├── test_alteracoes_legiveis.py  # NOVO — o tradutor, coleção por coleção
│   └── test_dobra_de_texto.py       # NOVO
└── interface/test_acessibilidade_do_portal.py  # ampliado
```

**Structure Decision**: o monólito Django existente, sem projeto novo e sem camada nova. Três
arquivos de produção nascem, e nascem pelo mesmo motivo: uma função que passa a servir duas telas
(`T-003`), uma tradução que é regra de domínio e não de tela (`T-002`), e uma dobra de texto que já
existia duas vezes com finalidades diferentes e não pode virar três (`T-005`).

O `sorteios/domain/normalizacao.py` **não é tocado**: a normalização de lá é regra auditável do
sorteio, com prova pública dependendo dela.

---

## Ordem de execução

A da §8 da spec, e cada etapa é demonstrável sozinha:

| # | Entrega | Depende de | Novo código |
|---|---|---|---|
| 1 | Cronograma público (`US1`) | `T-003` | mover, não escrever |
| 2 | Campos da vaga e cadastro reserva (`US3`) | — | renderização direta |
| 3 | Histórico normativo (`US2`) | `T-001`, `T-002` | o único trecho substancialmente novo |
| 4 | Quatro situações na vitrine (`US5`) | `T-009` | agrupamento |
| 5 | Busca, filtros, ordenação e volta (`US4`) | `T-004`, `T-005`, `T-007` | formulário e saneamento |

A 3 é a que concentra o risco, e a 1 é a que entrega mais valor por menos código. Começar pela 1
também põe o parcial de cronograma em uso pelas duas telas cedo, o que é a prova de que a `T-003`
está certa.

**Duas armadilhas na etapa 1**, ambas levantadas na `T-003` e fáceis de atropelar:

1. O parcial compartilhado renderiza **só a lista**. O caso vazio fica com cada chamador: a área do
   candidato mantém a frase que já tem, a página pública omite a seção (`FR-128`).
2. `tests/integration/portal/test_acompanhamento.py` afirma sobre a substring
   `class="marco em_curso"`. A extração precisa preservar a marcação **exatamente** — quebrar ali é
   quebrar um teste que nada tem a ver com esta feature.

---

## Complexity Tracking

> Preenchido apenas quando o Constitution Check tem violação a justificar.

**Vazio.** Nenhuma violação: a feature não persiste, não introduz dependência, não cria serviço e
não altera contrato existente.
