# Implementation Plan: Corte e Progressão entre Etapas

**Branch**: `claude/spec-014-corte-progressao-b8aa7a` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/014-corte-e-progressao-entre-etapas/spec.md`

---

## Summary

O marco classificatório passa a declarar **como aquele Edital corta** — o alvo, o excedente de
suplentes e o desfecho do empate na última posição —, e a ordem vigente passa a ser transformada num
**ato de corte** imutável que diz quem progride para a Etapa seguinte. A Etapa seguinte deixa de
receber todos os habilitados e passa a receber a faixa.

**A abordagem técnica cabe em duas frases.** A regra é mais um objeto do marco, e o marco já tem
dois: `appealWindow` e `drawMethod` percorreram exatamente este caminho — campo `JSONField`, degrau
de schema, catálogo de Retificação, documento. O ato é mais um append-only ao lado do
`AtoDeOrdenacao`, com a mesma forma de sucessão, o mesmo `comando_de_comissao` e a mesma trilha.

Isso decide o formato do plano: **duas entidades, duas migrations, um degrau de schema (12 → 13),
nenhum app, camada ou serviço novo e nenhuma permissão nova.** Módulos novos existem — `faixa.py`,
`corte.py` e `emissao_do_corte.py` —, e eles moram nos pacotes que já existem, na camada que já
existe. O risco não está na engenharia — está em três lugares
nomeados na §*Ordem de execução*: o ciclo de importação que a prontidão quase cria, a diferença entre
**sucessão** e **continuação**, e o orçamento de consulta das listagens da `011`, da `012` e da `015`,
que é verificado por teste e não pode ser corroído.

**A revisão cruzada de 11/09 mudou quatro coisas deste plano, e nenhuma delas era cosmética.** A
faixa da primeira emissão passou a ser `alvo + excedente` e a continuação passou a ser declarada
(`R-016`); a Etapa governada passou a ser declarada, e nunca inferida (`R-006`); a sucessão passou a
ser de **geração**, e não de faixa (`R-010`); e o corte obsoleto passou a **bloquear trabalho novo**
na Etapa governada (`R-017`). A `R-009` fechou, junto, o que a publicação exige quando o alvo é
derivado e o quadro é parcial.

As três primeiras eram incompatibilidades de domínio que teriam chegado ao código: a primeira
emissão do 77 progredia setenta pessoas e deixava a `US4` sem função; a Etapa governada saía de um
campo que o marco de sorteio preenche só para publicar; e uma geração com continuação não podia ser
sucedida sem deixar metade dela governando a Etapa.

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. **Nenhuma dependência nova**

**Storage**: PostgreSQL 16. **Duas** migrations — `editais/migrations/0017_regra_de_corte.py`, que
acrescenta um `JSONField` ao marco, e `classificacao/migrations/0006_corte.py`, que cria duas tabelas
append-only com as travas de privilégio e de trigger que a `015` já estabeleceu para o ato. Nenhuma
altera valor publicado, nenhuma remove nada

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). Unidade em
`tests/unit/classificacao/` e `tests/unit/editais/`; contrato em `tests/contract/`, com
`test_elevacao_degrau_13.py` na convenção estrita de nome; integração em
`tests/integration/classificacao/`; interface em `tests/interface/`; aceitação em
`tests/acceptance/`

**Target Platform**: servidor web; interface administrativa server-side com htmx, sem SPA e sem build
de front

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: o maior caso do alvo é 1.000 participantes por recorte, e o teto de abertura
da tela é 3 segundos (`SC-067`). A condição do corte entra como **um** `Exists` correlacionado dentro
de consultas que já aconteciam, e o conjunto dos cortes vigentes é resolvido uma vez por listagem
(`SC-068`)

**Constraints**: nenhum corte emitido em silêncio ao abrir tela (`FR-190`); nenhum Resultado de Etapa
gravado, alterado ou apagado (`FR-212`); nenhuma afirmação de vaga ocupada, preenchida ou de déficit
(`FR-207`, `SC-066`); conteúdo publicado antes do degrau lido com `cutRule: null`, nunca com regra
inventada (`FR-186`); Edital sem regra com comportamento idêntico ao de hoje (`FR-214`, `SC-069`)

**Scale/Scope**: duas entidades novas, um campo novo; ~24 arquivos de produção tocados; seis entregas
demonstráveis

**Nenhum NEEDS CLARIFICATION.** As quinze questões técnicas estão resolvidas em
[research.md](research.md). Os nomes que a spec delegou ao plano ficam fixados na `R-001`, e o degrau
na `R-004`.

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | *Corte*, *faixa*, *alvo*, *excedente* e *progrediu* são as palavras dos próprios Editais, citadas na §1.1 da spec. `cutRule` é irmão de `appealWindow` no mesmo objeto. A `FR-207` proíbe, e o teste verifica, o vocabulário que **não** é desta feature — vaga ocupada, vaga preenchida, déficit —, que é como a fronteira com a `016` deixa de ser promessa | ✅ |
| **II — Integridade normativa e imutabilidade** | A regra é conteúdo publicado com fonte única; o ato é append-only por `save()`, por privilégio ausente e por trigger. Nada publicado é reescrito: o degrau 13 converte **para leitura**, e a `FR-217` proíbe obsolescência alterar o vigente. O corte congela a versão que o governou, e é lido com os nomes dela | ✅ |
| **III — Segurança e proteção de dados** | Nenhuma permissão nova: `classificacao:emitir`, que já existe (`R-015`). A `FR-221` separa ler de emitir e fecha o IDOR pelo escopo do ator. Nenhum dado pessoal novo — o item do corte guarda identidade de inscrição, posição e causa, que a ordem já guarda | ✅ |
| **IV — Regras explícitas e consistência** | Toda regra vive no domínio: o alvo, o empate e os limites da continuação são recusas de `DomainError`, não validação de formulário. As três recusas de publicação são achados classificados pela operação de publicar, que é o mecanismo que o princípio exige. A concorrência da `FR-201` é resolvida por constraint, e não por trava de aplicação | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md). A simplicidade é o eixo: **zero app novo, zero camada nova, zero permissão nova** — a `R-008` encontrou que o empate que atravessa o corte já é legível na ordem emitida, e a `R-011` que as quatro causas de obsolescência saem de comparações que a tela do marco já faz | ✅ |
| **VI — Completude de jornada** | É o princípio que **motiva** a feature: quatro Editais reais param na ordem, e a decisão que define quem continua no certame vive hoje em planilha. O cenário demonstrável é o percurso do [quickstart.md](quickstart.md), pela interface administrativa, sem shell e sem banco | ✅ |

### Invariantes do domínio tocados

| Invariante da Constituição | Efeito |
|---|---|
| "Perfis PODEM possuir Etapas distintas. Cada Etapa PODE definir ordem, peso… caráter eliminatório ou classificatório" | a feature **não** toca em nada disso. O corte não é caráter de Etapa: ele não elimina, e a `FR-212` o proíbe de gravar Resultado |
| "Registros normativos, publicados, históricos ou auditáveis NÃO DEVEM ser fisicamente excluídos" | `FR-223`. Nem corte, nem item, nem regra publicada |
| "O estado normativo vigente em qualquer instante relevante DEVE ser reproduzível" | `FR-193` e `FR-199`: o universo declarado reproduz a faixa, e a `R-009` acrescenta a identidade da linha do quadro justamente para que a reprodução não dependa do quadro de hoje |
| "Mudanças persistentes DEVEM usar migrations versionadas" | duas, aditivas |
| "APIs DEVEM ter contratos explícitos" | `openapi.yaml` nos dois lugares e [contracts/corte.md](contracts/corte.md) |
| "Entidades DEVEM possuir identificadores estáveis; identificadores públicos NÃO DEVEM conferir autorização" | UUID preservado, e `FR-221` diz a segunda metade em requisito |

**Sem violações. A tabela de Complexity Tracking fica vazia.**

---

## Project Structure

### Documentation (this feature)

```text
specs/014-corte-e-progressao-entre-etapas/
├── plan.md              # este arquivo
├── spec.md              # a especificação
├── research.md          # R-001 a R-015, todas resolvidas
├── data-model.md        # as duas entidades, o campo, o degrau, os invariantes
├── quickstart.md        # os seis percursos, contra o servidor real
├── contracts/
│   └── corte.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/perfis.py                         # MarcoClassificatorio.regra_de_corte (JSONField)
│   ├── migrations/0017_regra_de_corte.py        # NOVO — o campo, com default {}
│   ├── domain/perfis.py                         # validação do cutRule (FR-179..FR-181)
│   ├── domain/validation.py                     # sete achados impeditivos (R-014)
│   ├── api/serializers.py                       # cutRule em MarcoSerializer
│   └── application/draft.py                     # persistência do cutRule no rascunho
├── classificacao/
│   ├── models.py                                # NOVOS Corte e ItemDoCorte, append-only
│   ├── migrations/0006_corte.py                 # NOVO — duas tabelas, constraints parciais, trigger
│   ├── domain/faixa.py                          # NOVO — alvo apurado, fronteira, empate que atravessa
│   ├── application/corte.py                     # NOVO — calcular_corte
│   ├── application/emissao_do_corte.py          # NOVO — emitir_corte e continuar_corte
│   └── application/selectors.py                 # estado do corte junto do estado do marco (R-011)
├── resultados/
│   └── application/prontidao.py                 # a condição do corte nas TRÊS portas (R-007)
├── publicacoes/
│   ├── application/publish_edital.py            # cutRule no dicionário do marco
│   └── domain/elevacao.py                       # DEGRAUS_DE_MARCO[13] = {"cutRule": None}
├── divulgacao/
│   └── domain/publicabilidade.py                # corte obsoleto impede publicar resultado (FR-219)
├── interface/
│   ├── forms.py                                 # a regra na seção do marco: ler, persistir, reexibir
│   ├── views.py                                 # as quatro rotas do corte (R-012)
│   ├── urls.py                                  # idem
│   ├── retificacao.py                           # cutRule no catálogo do marco
│   └── templates/interface/
│       ├── _marco.html                          # a regra dentro da seção do marco
│       ├── corte.html                           # NOVO — a tela do corte
│       └── _linha_do_corte.html                 # NOVO — a linha, reusada como fragmento
└── shared/canonical.py                          # SCHEMA_VERSION 12 → 13, com o degrau narrado

specs/001-processo-seletivo-editais/contracts/openapi.yaml   # MarcoInput e MarcoPublicado

backend/tests/
├── contract/
│   ├── test_elevacao_degrau_13.py               # NOVO — convenção estrita de nome
│   ├── test_forma_publicada.py                  # ampliado
│   └── test_documento_publicado.py              # fixture de bytes regenerada de propósito
├── unit/classificacao/
│   ├── test_faixa.py                            # NOVO — alvo, fronteira, empate que atravessa
│   └── test_corte_append_only.py                # NOVO — save, delete, privilégio, trigger
├── unit/editais/test_regra_de_corte.py          # NOVO — as três recusas de publicação
├── integration/classificacao/
│   ├── test_emissao_do_corte.py                 # NOVO — universo, sucessão, corrida, marco sem Etapa seguinte
│   ├── test_faixa_seguinte.py                   # NOVO — continuação não é sucessão; as duas vigentes
│   ├── test_reproducao_do_corte.py              # NOVO — o universo declarado reproduz a faixa
│   └── test_corte_obsoleto.py                   # NOVO — as quatro causas
├── integration/resultados/
│   └── test_progressao_com_corte.py             # NOVO — as três portas, e a não regressão
├── test_vocabulario_do_corte.py                 # NOVO — a fronteira com a 016, varrida na fonte
├── interface/test_corte.py                      # NOVO — a tela, as recusas, a confirmação
└── acceptance/test_us3_corte.py                 # NOVO — o ciclo do 14/2026 e o do 77/2026
```

**Structure Decision**: o monólito Django existente, sem projeto novo, sem camada nova e **sem app
novo**. Os três módulos que nascem — `domain/faixa.py`, `application/corte.py` e
`application/emissao_do_corte.py` — moram em `classificacao`, ao lado dos que já estão lá. A regra mora em `editais`, junto dos outros dois objetos do marco; o ato mora em
`classificacao`, ao lado do `AtoDeOrdenacao` que ele cita em toda leitura. A `R-005` mostra por que
app próprio não resolveria nada e custaria uma fronteira.

`sorteios/` **não é tocado**. O corte lê o ato de ordenação, e o ato constituído por sorteio já é um
ato como qualquer outro — a `021` cuidou disso.

---

## Ordem de execução

1. **A regra publicada.** Campo no marco, validação, degrau 13, emissão no snapshot, catálogo de
   Retificação, documento, contrato, seção na tela do marco. Sem ela nada mais é legítimo, e ela é a
   única parte que mexe em conteúdo publicado.
2. **O cálculo.** `domain/faixa.py` e `application/corte.py`: apurar alvo, formar faixa, detectar o
   empate que atravessa. Puro, sem gravar, testável sem banco de norma.
3. **A emissão.** `Corte` e `ItemDoCorte`, migration, `emitir_corte`, autorização, idempotência,
   auditoria, e as constraints que resolvem a corrida.
4. **O efeito na progressão.** As três portas da prontidão, o estado *fora do corte*, e os testes de
   orçamento de consulta que provam que nada foi corroído.
5. **A obsolescência e o reingresso.** As quatro causas no `estado_do_marco`, e o impedimento de
   publicar resultado sobre corte obsoleto.
6. **A faixa seguinte.** `continuar_corte`, com motivo, limite e recusa sobre ordem sucedida.

Os passos 1 a 4 entregam o 14/2026 até a entrevista. O passo 6 fecha o ciclo do 77, do 57 e do 28
antes de a `016` existir.

### As três armadilhas que matam em silêncio

**O ciclo de importação.** `classificacao/application/calculo.py:14` já importa
`resultados/application/prontidao.py`. A prontidão pode importar `classificacao.models`, e **nunca**
`classificacao.application.*` — o primeiro import desses fecha o ciclo, e o erro aparece na primeira
importação de qualquer um dos dois, num arquivo sorteado, longe da causa. Vira comentário no código,
não só linha de plano. Onde o import de topo não couber, o recurso é o import dentro da função, que
`avaliacoes/application/distribuicao.py:209` já usa por essa mesma razão.

**Sucessão contra continuação.** São dois campos, duas constraints e dois significados. Sucessão
substitui e deixa **um** vigente; continuação acrescenta e deixa **dois**. Escrever uma no lugar da
outra produz um sistema que parece funcionar: a faixa seguinte some da tela, ou a anterior deixa de
valer — e nos dois casos alguém deixa de participar de uma Etapa em que deveria estar. A `FR-202` diz
a frase, e o teste de integração tem de exercitar a coexistência.

**O orçamento de consulta.** A `011`, a `012` e a `015` escreveram testes que contam consultas
justamente para que uma feature seguinte não os corroesse. A condição do corte entra como junção
dentro da consulta que já ia acontecer, e os cortes vigentes são resolvidos uma vez por listagem,
junto do `_anteriores_e_gate` — que já lê o conteúdo publicado uma vez. Materializar ids e passá-los
em `__in` custaria duas leituras de população por listagem, e é o erro que a própria prontidão já
documenta ter recusado.

### As travessias que a seção do marco obriga

A `025` pagou seis defeitos para descobrir que uma seção nova no cartão do Perfil tem quatro
travessias, e todas elas valem aqui: a regra tem de aparecer no Perfil **recém-acrescentado** antes
de qualquer gravação; o fragmento htmx tem de trazer o invólucro junto; a recusa tem de ancorar no
controle certo, com o `id` na profundidade certa; e a reexibição não pode sobrescrever o valor bom
pelo da tentativa recusada. O teste de round-trip do rascunho é o que cobra as quatro.

---

## O que este plano deliberadamente não faz

- **Não apura vaga, déficit nem ocupação.** É a `016`, e a `FR-207` com a `SC-066` transformam a
  fronteira em teste.
- **Não convoca e não comunica.** É a `019`.
- **Não toca no cálculo da ordem.** `desempate.py`, `combinacao.py` e `universo.py` não são
  modificados; o corte lê `PosicaoNaOrdem` como ela foi emitida.
- **Não abre a aplicabilidade da Etapa por modalidade.** A metade dessa lacuna que dependia de ordem
  passa a ser servível pelo corte; a outra metade continua onde está.
- **Não publica o corte como resultado** e não o expõe ao candidato. A divulgação é da `017`; o que
  entra aqui é o impedimento de publicar sobre corte obsoleto.
- **Não cria segunda instância de nada**, não cria permissão e não cria app.

---

## Complexity Tracking

*Sem violações constitucionais a justificar.*
