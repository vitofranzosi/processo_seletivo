# Implementation Plan: O Cronograma — visibilidade no PDF, ordenação e prévia

**Spec**: [spec.md](spec.md) · **Pesquisa e decisões**: [research.md](research.md) ·
**Tarefas**: [tasks.md](tasks.md)

## Summary

Três incrementos, na ordem em que dependem um do outro:

1. **A — visibilidade.** Uma coluna `shown_in_pdf` no `EventoCronograma` (migration `editais/0026`,
   padrão verdadeiro), a chave `shownInPdf` no conteúdo publicado (degrau 20), o olho no cartão sobre
   um campo oculto, e uma função só na composição do PDF que diz quais Eventos saem e com que número.
2. **B — ordenação.** Um botão e uma função de cliente que move os cartões; a renumeração é a que
   `ordenacao.js` já faz.
3. **C — prévia.** Uma tabela compacta acima dos cartões, desenhada no cliente a partir do formulário.

B e C não tocam servidor além do template e da folha; A é o único com migration e degrau. Cada
incremento é um PR que passa a suíte sozinho, nesta ordem.

## Technical Context

- **Linguagem**: Python 3 / Django; JavaScript sem build, em arquivo estático (CSP `script-src 'self'`).
- **Banco**: PostgreSQL; `editais_eventocronograma` não é append-only (rascunho apagado e recriado).
- **Testes**: pytest contra PostgreSQL (`make test-pg`); `node --test` com o DOM de
  `tests/javascript/dom.js`; Playwright no grupo `navegador`.
- **Restrições**: CSP sem `unsafe-inline` (estilo em folha, script em arquivo); classe citada no
  template exige regra na folha; tudo em português; comentário diz por quê.
- **Escala**: um Cronograma tem de 3 a ~15 Eventos na amostra; nenhuma questão de desempenho.

## Constitution Check

- **Publicação é ato imutável** — nenhum documento publicado muda (FR-5114); o efeito sobre ato
  publicado só pela Retificação (FR-5113). ✅
- **Nada é excluído** — a migration acrescenta coluna com padrão; nenhum dado normativo apagado. ✅
- **Uma fonte por fato (Princípio II)** — a visibilidade mora no Evento; a numeração impressa é
  derivada (D-003), não guardada; a ordem continua o `order`. ✅
- **Negar por padrão** — nenhuma permissão nova; a etapa continua com a autorização de hoje. ✅
- **Rastreabilidade** — FR/SC/UX com linha na matriz, inclusive os casos-limite. ✅

## O desenho

### Incremento A — visibilidade no PDF

**1. O dado.**

- `editais/models/cronograma.py` — `shown_in_pdf = models.BooleanField(default=True)`, com o
  comentário da D-001 (por que no Evento, por que positivo, por que não estado).
- `editais/migrations/0026_visibilidade_do_evento_no_pdf.py` — `AddField` com `default=True`. O
  PostgreSQL grava o padrão sem reescrever linha; nenhum gatilho dispara.
- `editais/application/draft.py` — no `bulk_create`, `shown_in_pdf=event.get("shownInPdf", True)`.
- `editais/api/serializers.py` — `shownInPdf = serializers.BooleanField(required=False,
  default=True)`, com o comentário da omissão (FR-5104).

**2. A travessia da tela** — os quatro caminhos do risco 1 da pesquisa.

- `interface/forms.py` — `ler_eventos` lê `evento-N-shownInPdf` (`"false"` é oculto; qualquer outro
  valor, inclusive ausente, é exibido); `eventos_do_edital` e `eventos_persistidos` levam
  `shownInPdf`. **Não** entra em `PRESERVADO_DA_ETAPA` (D-007).
- `interface/templates/interface/_evento.html` — o campo oculto; a marca "Oculto do PDF" na legenda
  (`<span class="marca-pdf" data-marca-pdf hidden>` quando exibido); a classe `oculto-do-pdf` no
  `fieldset` quando oculto.
- `interface/templates/interface/_acoes_da_linha.html` — recebe `com_visibilidade_no_pdf` (só o
  cartão do Evento o passa) e desenha, antes das setas, o botão de alternância com `hidden`, que o
  script revela. O glifo vem de `_olho.html` (SVG, olho aberto e fechado, só um visível por CSS),
  pelo motivo da `_lixeira.html`: um traçado num lugar só.
- `interface/static/interface/cronograma.js` — **arquivo novo, da etapa**, que os três incrementos
  fazem crescer. No A: revela os botões; no clique, alterna `value`, `aria-pressed`, `title`, a classe
  do `fieldset` e a marca, e despacha `change` no campo oculto (`bubbles: true`).
- `interface/static/interface/telas/compor-cronograma.css` — o cartão atenuado, a marca, o glifo.
  **Nenhuma classe de estado se chama `oculto`**: na gestão, `.oculto` é o texto só para leitor de
  tela (`_evento.html` o usa nas ajudas dos campos), e um selo `.oculto` some da tela. E regra com
  `display` sobre elemento que o script esconde por `hidden` precisa de `[hidden]` mais forte —
  a maquete caiu nas duas.

**3. O conteúdo publicado.**

- `shared/canonical.py` — `SCHEMA_VERSION = 20`, com o parágrafo do degrau 20 no molde do 11.
- `publicacoes/domain/elevacao.py` — `DEGRAUS_DE_EVENTO = {11: {"location": ""}, 20: {"shownInPdf":
  True}}`.
- `publicacoes/application/publish_edital.py` — `"shownInPdf": event.shown_in_pdf`.
- `editais/domain/validation.py` — `Campo("shownInPdf", bool)` em `EVENTO_PUBLICADO`.
- `editais/domain/mutabilidade.py` — `("schedule", "shownInPdf"): retificavel()` (P-1, decidida).
- `duvidas/domain/cobertura.py` — `VERSAO_DO_ESQUEMA = 20` e
  `"/schedule/*/shownInPdf": excluido("visibilidade no PDF (144): o assistente responde por todos os
  Eventos, e não pela forma do documento")` (FR-5112).
- `specs/001-processo-seletivo-editais/contracts/openapi.yaml` e
  `specs/026-contrato-de-mutabilidade-normativa/matriz.md` — uma linha cada, como no degrau 19.
- `tests/fixtures/snapshot.py` — a chave no Evento da fixture.

**4. O PDF** — D-002 e D-003.

```python
# publicacoes/infrastructure/pdf.py
def eventos_no_documento(snapshot):
    """Os Eventos que a tabela do Cronograma imprime, com o número que terão nela (144, D-002).

    Só a tabela e a presença da seção leem daqui. A Etapa e o período citam o Evento pelo vínculo,
    e continuam dizendo as datas do oculto: ocultar não é desativar.
    """
    eventos = [evento for evento in snapshot.get("schedule") or [] if isinstance(evento, dict)]
    exibidos = [evento for evento in eventos if evento.get("shownInPdf") is not False]
    if len(exibidos) == len(eventos):
        # Sem oculto, o número é o de sempre — inclusive o `0` e as lacunas que a API admite. O
        # documento de antes desta feature sai igual, byte a byte (D-003, SC-1580).
        return [(evento.get("order", ""), evento) for evento in exibidos]
    return list(enumerate(exibidos, 1))


def numero_no_documento(snapshot, evento):
    """O número com que o Evento sai na tabela, ou `None` se ele não sai (FR-5107)."""
    return next(
        (numero for numero, item in eventos_no_documento(snapshot) if item.get("id") == evento.get("id")),
        None,
    )
```

- `is not False`, e não `.get(..., True)`: o conteúdo de versão anterior que chega sem elevar — a
  prévia, os consolidados — é lido como exibido sem depender de quem o elevou.
- `_cronograma` — itera `eventos_no_documento`; "Nº" é o número devolvido — o `order` sem oculto, a
  posição com algum; `algum_local` sobre os
  exibidos; sem exibidos, retorna.
- `_materializaveis` — para a fonte `schedule`, a pergunta é `eventos_no_documento(snapshot)`;
  para as demais, a de hoje. `tabelas_do_documento` passa a acertar sem mudança, porque conta o que
  `_materializaveis` devolve.
- `apresentacao._principal_presente` — a mesma troca, pela mesma função (é o segundo caminho que a
  pesquisa achou).
- `frase_do_periodo_de_inscricoes(evento, numero)` — recebe o número impresso, ou `None`; sem
  número, sai sem a remissão. Os dois chamadores (o resumo não a usa; `apresentacao._periodo` sim)
  passam `numero_no_documento(snapshot, evento)`.

**5. Revisão, Retificação e reaproveitamento.**

- `interface/revisao.py` — `_evento` acrescenta "Não sai no PDF" quando `shownInPdf is False`; o
  bloco do Cronograma ganha a frase da seção não impressa; `"shownInPdf"` em `_LIDOS_POR_COLECAO`.
- `interface/retificacao.py` — `("shownInPdf", "Sai no PDF", BOOLEANO)` em `CAMPOS_EVENTO`; o
  Evento acrescentado nasce com `"shownInPdf": True` (`:2046`). `publicacoes/domain/alteracoes.py` —
  o rótulo "Sai no PDF". `test_campos_vem_do_contrato` passa a 86.
- `editais/domain/reaproveitamento.py` — nada muda: `{**evento}` já leva a chave. O teste prova.

### Incremento B — ordenação

- `compor_cronograma.html` — na linha `.contadores`, o botão `Ordenar por data de início ↑`
  (`data-ordenar-por-inicio`, `hidden`, só quando `editavel`) e um `<p class="oculto"
  role="status" data-anuncio-da-ordem>`.
- `cronograma.js` — a função pura e a montagem:

```javascript
/* A sequência crescente por início, estável, com os sem início ao fim (144, D-005). Pura: recebe
   [{chave, inicio}] e devolve as chaves na ordem nova — é ela que o teste exercita. */
function ordemPorInicio(itens) {
  return itens
    .map(function (item, posicao) { return { item: item, posicao: posicao }; })
    .sort(function (a, b) {
      var x = a.item.inicio, y = b.item.inicio;
      if (!x !== !y) return x ? -1 : 1;          // sem início vai ao fim
      if (x !== y) return x < y ? -1 : 1;        // AAAA-MM-DDTHH:MM compara como texto
      return a.posicao - b.posicao;              // empate: a ordem de antes
    })
    .map(function (par) { return par.item.chave; });
}
```

  No clique, lê os cartões, calcula a ordem, reanexa com `appendChild` na nova sequência (o
  `MutationObserver` de `ordenacao.js` renumera), conta quantos mudaram de posição e escreve o
  anúncio. O foco fica no botão. O botão se desabilita com menos de dois cartões (recalculado na
  mutação da lista).
- `interface/static/interface/assistente.js` — **D-010**: `reposicionarFoco` passa a receber o lote
  inteiro de registros e calcula o conjunto dos nós removidos nele; o nó acrescentado que também está
  entre os removidos foi **movido**, e não recebe foco. É o script comum de todas as listas do
  assistente: a mudança vale também para as setas de Perfis e Etapas, e só no sentido de não roubar
  o foco de quem moveu.

```javascript
new MutationObserver(function (registros) {
  atualizar();
  // Mover é sair e entrar na mesma entrega: não é linha nova, e o foco fica onde quem moveu o pôs.
  var sairam = new Set();
  registros.forEach(function (registro) {
    [].forEach.call(registro.removedNodes, function (no) { sairam.add(no); });
  });
  registros.forEach(function (registro) { reposicionarFoco(registro, sairam); });
}).observe(lista, { childList: true });
```

### Incremento C — prévia

- `compor_cronograma.html` — antes de `#eventos`, `<section class="previa-do-cronograma"
  aria-labelledby="previa-titulo" hidden data-previa-do-cronograma>` com `<h3>`, o cabeçalho de
  contagem e uma `<table>` com `<thead>` (Evento · Início · Término · PDF — o quê antes do quando, a
  ordem do cartão) e `<tbody>` vazio.
- `cronograma.js` — `resumo(linhas)` (pura: contagens e frases) e `desenhar()`; escuta `input` e
  `change` no formulário, a mutação da lista, e é chamada depois da alternância e da ordenação.
  Formata a data `AAAA-MM-DDTHH:MM` em `dd/mm/aaaa hh:mm` sem `Date`, para não depender do fuso do
  navegador. Monta as linhas com `textContent`, nunca `innerHTML`.
- `compor-cronograma.css` — a tabela compacta e o empilhamento a 375 px (`@media`, sem `}}` na mesma
  linha — o guardião de estáticos lê a folha como texto).

### Testes e verificação

| Camada | Arquivo | O que prova |
|---|---|---|
| Migration | `tests/migrations/test_migrations.py` | contagem `editais: 26`; Evento existente fica exibido (SC-1580) |
| Contrato | `tests/contract/test_elevacao_degrau_20.py` (novo) | ausência vira `true`; idempotência; v19 → v20 |
| Domínio do PDF | `tests/unit/publicacoes/test_cronograma_no_documento.py` (novo) | `eventos_no_documento`; numeração sem oculto (com `order` `0` e com lacunas) e com oculto; período com e sem remissão; todos ocultos nas duas apresentações; `tabelas_do_documento`; `numeracao` (SC-1581, SC-1587) |
| Tela | `tests/interface/test_cronograma_visibilidade.py` (novo) | gravar, recarregar, gravar outra etapa, recusa, fragmento novo, lista de Eventos da etapa Etapas, vencidos, somente leitura (SC-1582, SC-1584, SC-1589) |
| PDF real | `tests/interface/test_cronograma_no_pdf.py` (novo) | `texto_de_pdf_bytes`, **nas duas apresentações**: um oculto (descrição ausente da tabela, numeração 1..k, data da Etapa presente); todos ocultos (sem título da seção, sem "Datas: no Cronograma", "Tabela N" e números das seções seguintes coerentes com o que saiu); a remissão do período, exibido e oculto; `order` `0` e com lacunas iguais ao de antes (SC-1580, SC-1588) |
| Integração | `tests/integration/editais/test_reaproveitamento.py` | preserva; origem v19 chega exibida (SC-1586) |
| Retificação | `tests/interface/test_campos_vem_do_contrato.py` e um caso em `tests/integration/publicacoes/` | 86 retificáveis; retificar a visibilidade muda o consolidado (FR-5113) |
| Canais | um caso por canal em `tests/interface/test_cronograma_visibilidade.py` | os seis continuam com o oculto: página pública da seleção, assistente, Agenda, Kit de Divulgação, relatório do Edital e leitura pela API (FR-5112) |
| Foco | `tests/navegador/test_jornada_do_cronograma.py` | depois de ordenar e de cada seta, lido após o observador, o foco é o botão; acrescentar continua focando o primeiro campo da linha nova (FR-5125, FR-5127) |
| Cliente | `tests/javascript/cronograma.test.js` (novo) | alternância e `change`; `ordemPorInicio` (empate, vazio, já ordenado); prévia nos seis gestos; estados vazio e todos ocultos (SC-1583, SC-1585) |
| Navegador | `tests/navegador/test_jornada_do_cronograma.py` (novo) | a jornada inteira, a 1440 e 375 px, sem violação de CSP, com todos os scripts da etapa carregados juntos (SC-1590) |

O roteiro manual e a captura estão em [quickstart.md](quickstart.md).

## Project Structure

```text
backend/processo_seletivo/
├── editais/models/cronograma.py                       # A
├── editais/migrations/0026_visibilidade_do_evento_no_pdf.py   # A, novo
├── editais/application/draft.py                       # A
├── editais/api/serializers.py                         # A
├── editais/domain/{validation,mutabilidade}.py        # A
├── shared/canonical.py                                # A
├── publicacoes/domain/{elevacao,alteracoes}.py        # A
├── publicacoes/application/publish_edital.py          # A
├── publicacoes/infrastructure/{pdf,apresentacao}.py   # A
├── duvidas/domain/cobertura.py                        # A
├── interface/{forms,revisao,retificacao}.py           # A
├── interface/static/interface/assistente.js           # B — mover não é acrescentar (D-010)
├── interface/templates/interface/
│   ├── compor_cronograma.html                         # A (script), B, C
│   ├── _evento.html                                   # A
│   ├── _acoes_da_linha.html                           # A
│   └── _olho.html                                     # A, novo
└── interface/static/interface/
    ├── cronograma.js                                  # A, B, C — novo
    └── telas/compor-cronograma.css                    # A, B, C
```

## Complexity Tracking

Nenhuma violação. O degrau de elevação não é complexidade acrescentada: é o caminho que todo campo
novo do conteúdo publicado percorre desde a `006`, e o molde (o degrau 11, do local do Evento) é
exatamente este.
