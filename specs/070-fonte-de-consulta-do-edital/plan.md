# Implementation Plan: A fonte de consulta do Edital vigente (Fase A do assistente de dúvidas)

**Branch**: `claude/audit-edital-assistant-a8f915` (pasta `070-fonte-de-consulta-do-edital`) |
**Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/070-fonte-de-consulta-do-edital/spec.md`

## Summary

Um pacote novo, `duvidas` (`R-001`), responde a doze perguntas sugeridas sobre um Edital publicado.
Cada resposta:

- sai de uma única versão consolidada, a vigente no instante consultado (`R-003`);
- distingue texto do Edital, dado e explicação;
- liga cada texto e cada dado ao documento do ato publicado que o fixou (`R-004`), e nunca ao
  documento que a página pública chama de "Edital completo" — o
  [achado](../../doc/achado-documento-ligado-nao-contem-a-versao-vigente.md), reproduzido em 12/10.

**O domínio é puro.** Recebe o conteúdo e devolve a resposta. A aplicação lê do banco a versão, as
versões futuras, a proveniência, as publicações e o desfecho, em no máximo oito consultas
(`R-019`).

**A tela é interna**, na gestão, no alcance da página do Edital (`R-018`). Ela mostra:

- as respostas;
- os pontos para revisão antes da abertura pública: canais divergentes, cláusula de exclusividade,
  anexo citado inexistente, Retificação futura e documento de origem incompleto.

**Nenhuma tabela, nenhuma migration, nenhuma dependência, nenhuma chamada a modelo ou a serviço
externo, nenhuma rota pública.** A explicação é escrita pelo próprio pacote, e um guardião proíbe
importar o compositor do documento (`R-009`). Um guardião de cobertura prende cada campo do conteúdo
publicado a uma pergunta, ou a uma exclusão com motivo (`R-015`).

A função de consulta não depende de requisição. É a porta pela qual a Fase B poderá isolar a
inferência (`R-017`).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2, templates renderizados no servidor e CSS à mão na
folha da gestão.

**Primary Dependencies**: nenhuma nova. Reaproveita:

| Função | Para quê |
|---|---|
| `publicacoes.application.selectors.effective_version` | a versão no instante |
| `publicacoes.domain.changes.resolve_path` | o valor num caminho |
| `editais.domain.documentos.aplicabilidade` | os documentos aplicáveis |
| `inscricoes.domain.periodo.periodo_de_inscricoes` | o período de inscrições |
| `editais.domain.fase_do_evento.fase_publica_do_evento` | a fase de cada Evento |
| `processos.application.selectors.desfechos` e `obter_edital` | o desfecho e o alcance |
| `publicacoes.infrastructure.humano` | a formatação de datas e decimais |
| `shared.texto.dobrar` | a comparação de termos sem acento |

**Storage**: PostgreSQL, **só leitura**. Nenhuma tabela ou coluna nova ([data-model.md](data-model.md)).

**Testing**: pytest.

- **Unitários, sem banco**, sobre o corpus copiado (`R-016`). Cobrem:
  - os `CA-*` de conteúdo;
  - o tipo por pergunta;
  - o canal e a exclusividade;
  - os anexos;
  - o literal;
  - a cobertura;
  - o guardião de importação.
- **Integração contra PostgreSQL**, pelo fluxo real, perto de dez casos transacionais. Cobrem:
  - versão no instante e fronteira;
  - mudança de versão;
  - Retificação não publicada;
  - origem e os dois cenários do achado;
  - documento de origem incompleto;
  - desfecho no instante;
  - orçamento de consultas;
  - fronteira de leitura: nenhuma tabela de candidato ou de rascunho.
- **Interface:** alcance e `404`, a entrada só com publicação, rótulos das naturezas, `aria-live`,
  375 px.

**Target Platform**: o mesmo Ubuntu com nginx, gunicorn e PostgreSQL. Nada novo na implantação.

**Project Type**: monólito web Django; uma tela de gestão.

**Performance Goals**: resposta em até 2 s no p95 para o 92/2026 (`SC-537`), medida e registrada na
verificação; até oito consultas por resposta, constantes (`R-019`).

**Constraints**:

- Zero chamadas externas (`FR-1447`).
- Zero escrita (`FR-1449`).
- Nenhum byte de PDF ou anexo lido do banco (`R-019`).
- Nenhuma importação do compositor (`R-009`).
- 375 px sem rolagem horizontal.

**Scale/Scope**:

- O pacote `duvidas`: domínio com seis a oito módulos, uma função de aplicação.
- Uma view, um template e um link na página do Edital.
- Uma linha no inventário da `033` e uma entrada em `MODULOS_DE_VIEW`.
- Os fixtures do corpus.
- Perto de 60 casos unitários e 10 de integração.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o respeita | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Assistente de dúvidas" sempre qualificado, porque "assistente" já é o de composição (`R-002`). O pacote não se chama `consulta`, que já é a consulta pública (`R-001`). Natureza, tipo e origem com nomes próprios | ✓ |
| II. Fonte única, imutabilidade, temporalidade | A única fonte é a versão consolidada publicada, determinada pelo instante (`R-003`). Nada é gravado: nenhuma segunda fonte editorial (`D-006`). Retificação futura dita, nunca aplicada antes. Texto literal idêntico ao publicado (`R-010`). O documento citado é o do ato que fixou o valor (`R-004`) | ✓ |
| III. Negar por padrão, escopo, LGPD | Alcance de `obter_edital`, por escopo institucional; fora dele, `404` inventariado (`R-018`). Nenhum dado pessoal lido nem recebido; a fronteira de leitura é testada (data-model §1). Sem capacidade nova, por decisão registrada (`D-010`): a tela só lê conteúdo já público, não grava nem pratica ato, e tem o alcance da página do Edital | ✓, com a decisão expressa |
| IV. Regras explícitas, derivação explícita | O que o sistema deriva — tipo, situação, origem, pontos para revisão — aparece rotulado como derivado, com a fonte (`FR-1432` a `FR-1437`). A explicação se declara do sistema. Nenhum ato irreversível; nenhum lote | ✓ |
| V. Simplicidade e rastreabilidade | Nenhuma dependência, tabela, fila, cache, índice ou vetor. Domínio puro e testável sem banco. Rastreabilidade por caminho da `004` em cada cartão. Guardiões de cobertura e de importação | ✓ |
| VI. Jornada demonstrável | O setor de seleção confere as respostas na gestão, pelo próprio canal, sem banco nem shell (`SC-538`; [quickstart.md](quickstart.md) B). Isso desbloqueia a Fase B, como a spec declara | ✓ |

**Re-check depois do desenho:** ✓.

- O data-model não acrescenta tabela.
- Os contratos não expõem nada fora da versão consultada, salvo o canal institucional e o desfecho.
- O desenho não introduz dependência nem processo novo.
- A única escrita em artefato de outra spec é a linha do inventário da `033`. É a prática de toda
  feature que cria porta, e não altera decisão da `033`.

## Project Structure

### Documentation (this feature)

```text
specs/070-fonte-de-consulta-do-edital/
├── spec.md
├── plan.md                # este arquivo
├── research.md            # R-001 a R-020
├── data-model.md          # o que é lido; as estruturas em memória
├── quickstart.md          # roteiro de validação (automático e pelo ator)
├── contracts/
│   ├── resposta.md        # catálogo, fontes, tipos, avisos, explicação, forma serializada
│   └── tela.md            # rota, parâmetros, negativas, ordem, vocabulário, acessibilidade
├── checklists/
│   └── requirements.md
└── tasks.md               # /speckit-tasks — ainda não
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── duvidas/                                  # novo (R-001), sem models.py
│   ├── apps.py
│   ├── domain/
│   │   ├── catalogo.py                       # P-01 a P-12, oferta, parâmetros, pertinência (D-007)
│   │   ├── estruturas.py                     # dataclasses do data-model §2
│   │   ├── leitura.py                        # conteúdo → referências TEXTO/DADO por caminho (R-010)
│   │   ├── respostas.py                      # uma função por pergunta; tipo (R-013)
│   │   ├── explicacao.py                     # textos deste pacote (R-009)
│   │   ├── canal.py                          # termos, contatos, exclusividade (R-011)
│   │   ├── anexos.py                         # vínculo e citação (R-012)
│   │   ├── origem.py                         # proveniência por ancestral e ordem (R-004)
│   │   ├── revisao.py                        # pontos para revisão (R-005)
│   │   └── cobertura.py                      # a tabela COBERTURA (R-015)
│   └── application/
│       └── consultar.py                      # consultar(...) e pontos_para_revisao(...) (R-017)
├── interface/
│   ├── duvidas.py                            # a view (contrato tela.md)
│   ├── urls.py                               # a rota
│   └── templates/interface/
│       ├── duvidas.html                      # nova
│       ├── detalhe.html                      # o link de entrada
│       └── base.html                         # regras das classes novas
backend/config/settings/base.py               # "processo_seletivo.duvidas" em INSTALLED_APPS
backend/tests/
├── fixtures/corpus_070/                      # cópia do corpus + LEIA-ME com origem e SHA-256 (R-016)
├── fixtures/corpus.py                        # publicar_do_corpus(nome, deslocamento)
├── unit/duvidas/                             # catálogo, respostas, canal, anexos, literal, cobertura, importação
├── integration/duvidas/                      # versão, fronteira, origem, achado, desfecho, orçamento, fronteira de leitura
├── interface/test_duvidas.py                 # tela, alcance, entrada, rótulos, acessibilidade
└── test_gramatica_das_portas.py              # MODULOS_DE_VIEW + interface/duvidas.py
specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # uma linha, "acrescentada pela 070"
```

**Structure Decision**: o monólito existente. O pacote novo segue o desenho em camadas dos
vizinhos (`avisos`, `divulgacao`): `domain` puro, `application` com as leituras, e `interface` para
a tela. Sem `models.py`, porque nada é gravado.

## Decisões arquiteturais para a revisão

As de maior consequência, com o argumento completo em [research.md](research.md):

1. **`R-004`, a origem por ancestral e pela ordem dos atos.** É a peça que torna o link de
   conferência correto sem corrigir o achado. A regra óbvia, o caminho mais longo, daria a origem
   errada quando um Perfil é substituído inteiro depois de outra Retificação mudar um campo dele.
2. **`R-009`, a explicação própria e o guardião de importação.** Fecha a porta pela qual as frases
   do compositor — que mudam com o código e com a `069` — entrariam como se fossem do Edital.
3. **`R-013`, o tipo por tabela de decisão.** "Depende da leitura" é a resposta honesta sempre que o
   assunto está em texto. "Fontes divergentes" fica restrito ao que o sistema compara.
4. **`R-015`, cobertura presa à versão do esquema.** Uma feature futura que acrescente campo ao
   conteúdo publicado não passa sem dizer se o assistente o mostra.
5. **`R-016`, o corpus em duas camadas.** O domínio roda sobre o conteúdo publicado de verdade, e a
   integração pelo fluxo real com datas deslocadas. O ensaio do `replace_draft` com o conteúdo é a
   primeira tarefa, e há plano B.
6. **`R-017`, a função sem requisição.** Prepara a Fase B sem antecipar nenhuma peça dela.

## Riscos remanescentes

| Risco | Onde aparece | Mitigação no plano | Resíduo |
|---|---|---|---|
| O conteúdo publicado não passa inteiro pelo `replace_draft` | testes de integração | ensaio na primeira tarefa; plano B do `R-016` | Editais mínimos por caso, em vez do corpus inteiro no banco |
| Termo de dúvida ou de exclusividade fora da lista | canal | listas fechadas, conferidas no corpus; o erro aparece na validação interna | **Editais reais** podem usar outra redação: revisar as listas no piloto |
| `ProvenienciaConteudo` não é append-only | origem | a Fase A só lê | achado à parte, sem escopo atribuído |
| Explicação e `069` com redações diferentes para a mesma regra | linguagem | só valores dos cartões; revisão de vocabulário quando a `069` for mergeada | registrado na spec (*Compatibilidade com a 069*) |
| A `069` e a `070` disputam guardiões globais (faixa de FR, contagem de templates) | integração | faixa com folga de nove números; a `070` não toca o compositor | medir de novo na hora do merge, na ordem em que entrarem |
| O tipo `DETALHE_EM_ANEXO` não é produzido pelo catálogo da Fase A | consistência spec × contrato | registrado em [resposta.md](contracts/resposta.md) §2; o anexo sai como aviso | o `/speckit-analyze` deve vê-lo como intencional |
| A suíte cresce | CI | o grosso é unitário e sem banco; cerca de dez transacionais | alguns segundos a mais por caso transacional |

## Complexity Tracking

Nenhuma violação a justificar. O único acréscimo estrutural é um pacote novo sem tabela, que segue o
desenho dos vizinhos.
