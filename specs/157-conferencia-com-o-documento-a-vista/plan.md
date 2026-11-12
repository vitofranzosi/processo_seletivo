# Implementation Plan: Conferência com o documento à vista

**Branch**: `claude/157-implementacao` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: `specs/157-conferencia-com-o-documento-a-vista/spec.md`, mergeada pelo PR #481. Plano sobre
a `main` em `7441e5c0`, depois do #482, do #483 e do #484.

**Decisões**: todas do usuário — as quatro questões da spec (D-002, D-005 a D-008) e, para este plano,
a de 11/11/2026 sobre a FR-6544: *"defina abertura como acesso ao arquivo vigente, sem afirmar
comprovação de exibição ou leitura"* (R-001). Nenhuma se reabre. Os `R-` de
[research.md](research.md) dizem onde e como cada requisito se cumpre.

## Summary

Uma tela muda de forma e uma regra muda de lugar no tempo; nenhum estado novo.

1. **A conferência com o arquivo ao lado.** A página *Documentos da convocação* ganha o painel do
   visualizador da Mesa, agora um script só para as duas telas (`visualizador.js`): em tela larga, o
   arquivo ao lado do formulário, com a pessoa, o documento e a versão na barra; abaixo dela, o
   arquivo abre fora da página, e a volta relê a marca, restaura o formulário e oferece o retorno. O
   registro da conferência passa a ser por htmx, sem recarga, com o cartão, a situação e a
   confirmação trocados no lugar; sem script, tudo como hoje.
2. **A abertura é o acesso ao arquivo vigente** (R-001). A rota do arquivo da convocação grava a
   consulta ao fim da entrega, e não antes dela: pedido interrompido não é abertura. A rota passa a se
   deixar emoldurar pela própria origem, e a recusa da entrega, pedida pelo painel, sai legível
   dentro dele (R-002).
3. **O pedido de aviso de uma pessoa** (D-008). O comando do aviso de pendência da `134` aceita o
   recorte de uma convocação, com as mesmas regras; a confirmação o oferece quando a conferência da
   pessoa termina com pendência. A situação do aviso passa a três grupos (R-009).
4. **A Mesa** (D-007): a recusa legível no painel, a alternativa sem prévia, *"Baixar"* na barra e a
   volta com o formulário preservado. Sem exigência de abertura, e com o registro de hoje.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2 (monólito); JavaScript sem build, em arquivo estático
**Primary Dependencies**: as de hoje — htmx 2.0.4, já servido pela gestão; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**, nenhum modelo, nenhuma tabela append-only nova (58
continuam 58)
**Testing**: pytest contra PostgreSQL (`make test-pg`); cliente de teste do Django nas rotas e nos
fragmentos; `node --test` (`tests/javascript/visualizador.test.js`) sobre o shim de DOM; verificação
no navegador do painel (quickstart)
**Target Platform**: a gestão (`/gestao/`), sob a CSP da `091` — script e estilo só de arquivo; moldura
só da própria origem
**Project Type**: aplicação web, servidor renderizando HTML
**Performance Goals**: nenhuma consulta por item na página dos documentos; os guardiões de
`tests/performance/` não mudam de número (R-014)
**Constraints**: FR-3609 da `115` (sem lote); FR-3611 da `115` e FR-4460 da `131` lidas pelo comando,
não pela tela; FR-4604 da `134` (registrar pendência não grava aviso); nada na Mesa exige abertura
**Scale/Scope**: duas telas da gestão, uma rota de arquivo revista, três rotas novas (cartão do item,
lista da Mesa, pedido de aviso), um comando com um parâmetro a mais; ~12 arquivos de produto, ~10 de
teste

## Constitution Check

*GATE: antes da Fase 0 e de novo depois do desenho.*

- **II. Integridade normativa e imutabilidade**: nada publicado muda. A trilha ganha o mesmo evento,
  em outro instante (R-001), e o gesto do aviso individual grava o mesmo `Aviso` da `134` (R-008).
  Nenhum `UPDATE` em dado gravado; nenhuma migration.
- **III. Negar por padrão**: as rotas novas usam as portas de hoje — `_convocacao_para_conferir`, a
  porta da Mesa pela Atribuição, `pode_conferir_documentos` no aviso. O emolduramento é só da própria
  origem (R-002). O `?painel=1` não muda autorização: só a forma da recusa da entrega.
- **IV. Regras explícitas**: o "conforme" continua decidido pelo comando, que lê a trilha (FR-3611 da
  `115`); a tela só informa. O pedido individual usa a mesma seleção do lote (R-008): uma regra só.
- **I. Linguagem ubíqua**: *"aberto por você"* diz acesso; nenhum texto diz *viu* ou *leu*
  (FR-6549). As frases do aviso, da `066` (R-009).
- **V. Rastreabilidade e simplicidade**: um visualizador para as duas telas (D-001); cada FR, SC e
  caso-limite ganha linha em `rastreabilidade.md`. Os achados são citados como *"achado NN do
  estudo"*.
- **VI. Completude de jornada**: o quickstart refaz o passo C2 do estudo, em tela larga e a 390 px,
  com prévia e sem ela, e a Mesa.
- **Acessibilidade e teclado** (§ das interfaces): foco, região viva, recusa com foco, sem prender o
  foco (R-012).

Sem violação. Pós-desenho: igual — o desenho acrescentou rotas de leitura e um parâmetro de recorte,
nenhum estado nem permissão.

## O desenho

### 1. A entrega do arquivo — `interface/views.py`, `documento_da_convocacao` (R-001, R-002)

- `@xframe_options_sameorigin`.
- A resposta passa a `StreamingHttpResponse` sobre `_entregar_e_registrar(...)`, um gerador que lê a
  cópia verificada em blocos e grava `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` depois do último. Cabeçalhos
  de hoje. O helper fica em `portal/arquivos.py`, ao lado de `entregar`, como
  `entregar_e_registrar_ao_fim(fonte, *, anexo, verificado, ao_fim)`.
- Com `?painel=1`, a recusa por integridade e por arquivo indisponível, depois de gravar o evento de
  hoje, responde `interface/_recusa_no_painel.html`, status 409, emoldurável.

### 2. A Mesa — `documento_da_mesa`, `inscricao_da_mesa`, `mesa_inscricao.html` (D-007)

- `documento_da_mesa`: o `?painel=1` da R-002; a gravação continua antes da entrega (FR-6548), com o
  comentário dizendo por quê.
- Rota nova `mesa-documentos` (GET): a lista de documentos, parcial `interface/_documentos_da_mesa.html`,
  extraído do template.
- O template passa aos atributos `data-` do visualizador; *"Baixar"* na barra.

### 3. A página dos documentos — `convocacao_documentos.html` e o parcial do item

- O `<article>` vai para `interface/_documento_da_convocacao.html`, com `id` pelo `id` do item.
- O contêiner `data-visualizador` com o painel antes da lista; a barra com a identificação (UX-640).
- O link *"Abrir"* com `data-abrir-documento`, `data-documento`, `data-versao`, `data-tamanho` e o
  tamanho à vista (UX-641). O *"Baixar"* fica.
- O formulário com `hx-post`, `hx-target="closest article"`, `hx-swap="outerHTML"`, e uma mensagem
  por formulário (`#mensagem-<item>`) para a recusa sem identidade e a falha de rede.
- A ajuda recolhida: o arquivo que não abre (UX-645) e o significado da marca (UX-652).
- A região de confirmação `#confirmacao-da-conferencia` (`role="status"`), vazia ao carregar.
- `htmx.min.js` e `visualizador.js` carregados com `defer`.

### 4. Os fragmentos — `interface/views.py`

- `cartao_do_documento_da_convocacao` (GET, R-005).
- `conferir_documento_view`, ramo `HX-Request` (R-006): cartão, situação, pessoas do recorte e
  confirmação; `HX-Refresh` na recusa sem cartão; `HX-Retarget` sem identidade.
- `_confirmacao_da_conferencia(...)` (R-007): o que foi registrado, o próximo documento ou a próxima
  pessoa, e — sem documento a conferir e com pendência — a oferta do pedido de aviso (R-008).
- `pedir_aviso_de_pendencia_view` (POST, R-008).
- O contexto do cartão sai para `_contexto_do_cartao(...)`, usado pela página e pelos fragmentos.

### 5. O aviso — `avisos/application/pendencias.py` e `conducao_da_convocacao.py` (R-008, R-009)

- `selecionar(..., convocacao_id=None)`; `avisar_pendencias(..., convocacao_id=None)`;
  `proximo_dia_do_pedido(agora)`; o motivo da recusa individual.
- `frase_do_aviso` em três grupos.

### 6. O script e as folhas — `visualizador.js`, `visualizador.css` (R-003, R-004, R-010 a R-013)

- `mesa.js` vira `visualizador.js`: abrir no painel (tela larga), alternativa (`pdfViewerEnabled`),
  carregamento, recusa lida da moldura, releitura do cartão, volta de fora da página (marca,
  restauração, retorno, foco), região viva, mensagem de falha de rede do htmx.
- `gestao/telas.css` perde as regras do painel da Mesa; `grupos/visualizador.css` as recebe, com as
  da conferência.

### 7. Os testes

- **Rota do arquivo** (`tests/interface/test_conferencia_com_o_documento_a_vista.py`, novo): o
  registro só depois de consumida a resposta; o pedido interrompido (gerador fechado antes do fim)
  sem registro; `X-Frame-Options: SAMEORIGIN`; `?painel=1` com integridade e indisponível — o parcial
  409 emoldurável, o evento de hoje, nenhuma consulta; sem `?painel=1`, a página de hoje.
- **Fragmentos**: o cartão relido; o registro com `HX-Request` — aceito, recusado sem abertura (com
  o preenchimento), versão superada (sem o resultado), desfecho no meio (`HX-Refresh`), sem
  identidade (`HX-Retarget`); a confirmação com o próximo documento, a próxima pessoa e o fim do
  recorte; o duplo envio. Igualdade, em texto, entre o fragmento e a página recarregada (SC-2146).
- **Aviso individual** (`tests/integration/avisos/test_aviso_de_uma_pessoa.py`, novo): o mesmo aviso
  e o mesmo texto que o lote gravaria para a pessoa; o limite comum aos dois gestos; as exclusões com o
  motivo; a data no *"já avisada hoje"*; nada agendado; a trilha com o recorte de uma pessoa;
  registrar pendência não grava aviso.
- **Mesa** (`tests/interface/test_mesa_visualizador.py`, novo): a recusa no painel; a lista relida;
  avaliar sem abrir continua aceito.
- **JavaScript** (`tests/javascript/visualizador.test.js`, de `mesa.test.js`): painel em tela larga,
  nada abaixo dela, a alternativa com `pdfViewerEnabled` falso, a recusa lida da moldura, a volta com
  e sem recarga, a restauração sem envio, o foco.
- **Os de hoje que mudam**: os três de `tests/interface/` que afirmam a consulta depois do GET passam
  a consumir a resposta; os que prendem as frases do aviso (`143`, `134`) passam às da FR-6543.
- **Matriz**: `rastreabilidade.md`, todo FR e SC.

## Onde os arquivos se cruzam com as specs em paralelo

Ver [research.md, R-015](research.md). Em resumo: a `154` (implementação em sessão própria) mexe
em `ROTULO_DO_ITEM`, no passo `REENVIADO`, na contagem do resumo e na exclusão `COMPLEMENTADA`, todas
regiões vizinhas das desta; a `152` mexe nas views de convocar, corte e desfecho. Antes da validação
final, a `main` entra nesta branch e os conflitos se resolvem preservando os requisitos de cada uma.

## Project Structure

### Documentation (this feature)

```text
specs/157-conferencia-com-o-documento-a-vista/
├── spec.md               # PR #481
├── checklists/requirements.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-015
├── data-model.md         # nenhuma entidade nova; o evento e o gesto
├── contracts/telas.md    # rotas, fragmentos e textos
├── quickstart.md         # testes e percurso no navegador
├── tasks.md              # /speckit-tasks
└── rastreabilidade.md    # na implementação
```

### Source Code

```text
backend/processo_seletivo/
├── portal/arquivos.py                                   # entregar_e_registrar_ao_fim
├── avisos/application/pendencias.py                     # convocacao_id; proximo_dia_do_pedido
├── interface/
│   ├── views.py                                         # entrega, fragmentos, pedido de aviso, Mesa
│   ├── urls.py                                          # cartão, lista da Mesa, pedido de aviso
│   ├── conducao_da_convocacao.py                        # frase_do_aviso em três grupos
│   ├── static/interface/visualizador.js                 # novo (de mesa.js)
│   ├── static/interface/grupos/visualizador.css         # novo (de gestao/telas.css)
│   ├── static/interface/telas/convocacao-documentos.css # as classes novas
│   ├── static/interface/gestao/telas.css                # sem as regras do painel
│   └── templates/interface/
│       ├── convocacao_documentos.html
│       ├── _documento_da_convocacao.html                # novo (o cartão)
│       ├── _confirmacao_da_conferencia.html             # novo
│       ├── _recusa_no_painel.html                       # novo
│       ├── mesa_inscricao.html
│       └── _documentos_da_mesa.html                     # novo
backend/tests/
├── interface/test_conferencia_com_o_documento_a_vista.py  # novo
├── interface/test_mesa_visualizador.py                    # novo
├── integration/avisos/test_aviso_de_uma_pessoa.py         # novo
├── javascript/visualizador.test.js                        # de mesa.test.js
└── (os da seção 7, alterados)
```

**Structure Decision**: o monólito de sempre; nenhum app novo. O helper de entrega fica com o de
hoje, em `portal/arquivos.py`, que as duas áreas já usam.

## Complexity Tracking

Sem violação da Constituição a justificar.
