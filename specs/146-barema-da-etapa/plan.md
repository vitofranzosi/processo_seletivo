# Implementation Plan: O barema da Etapa

**Spec**: [spec.md](spec.md) · **Pesquisa e decisões**: [research.md](research.md) ·
**Modelo**: [data-model.md](data-model.md) · **Tarefas**: [tasks.md](tasks.md)

## Summary

Três incrementos, cada um um PR que passa a suíte sozinho:

1. **A — configurar, publicar, imprimir.** Tabela `CriterioAvaliacao` filha da Etapa
   (`editais/0027`), lista `criteria` no conteúdo canônico (degrau 21), seção Barema no cartão da
   Etapa com prévia, tabela no PDF, contrato de mutabilidade e Retificação.
2. **B — pontuar e mostrar.** Função `avaliacoes/domain/barema.py`; coluna `criterios` em `Avaliacao`
   e `ConclusaoAvaliacao` (`avaliacoes/0005`, com o gatilho recriado); a ficha na Mesa; o barema em
   `CAMPOS_COMPARADOS`; o detalhamento no portal.
3. **C — corrigir por recurso.** Coluna `criterios` em `DecisaoRecurso` (`recursos/0003`); a ficha na
   tela de julgamento; o detalhamento do Resultado de recurso no portal.

**O que não se toca:** `resultados/application/consolidacao.py`, `prontidao.py`, `classificacao/`,
`divulgacao/`, `convocacao/`, `formalizacao/`, permissões, `DocumentoExigido`, `DocumentoSubmetido`.
Se uma tarefa precisar mexer num desses, ela está fora do desenho e volta para revisão.

## Technical Context

- **Linguagem**: Python 3 / Django; JavaScript sem build, em arquivo estático.
- **Banco**: PostgreSQL; `avaliacoes_avaliacao` tem gatilho de imutabilidade na concluída;
  `avaliacoes_conclusaoavaliacao` e `recursos_decisaorecurso` são append-only (gatilho e privilégio).
  Acrescentar coluna com default não reescreve linha nem dispara gatilho.
- **Testes**: `make test-pg`; `node --test` para o total ao vivo; Playwright (`navegador`) para a
  jornada de ponta a ponta.
- **Restrições**: CSP sem `unsafe-inline`; classe citada exige regra na folha; prefixo de campo
  `criterio-etapa-<i>-<n>-…` (o `_indices` de `forms.py` casa `etapa-*-id` e criaria índice espúrio);
  `replace_draft` apaga e recria — campo que não viaje no payload volta vazio.
- **Escala**: até ~10 critérios por Etapa; centenas de inscrições. Nada de desempenho.

## Constitution Check

- **Linguagem Ubíqua (I)** — "Critério de Avaliação" é termo da Constituição e vira a entidade;
  "barema" é o nome do conjunto na tela, como os Editais dizem. Distinto de Critério de Desempate. ✅
- **Fonte única (II)** — os critérios moram na Etapa; o total continua em `pontuacao` e é derivado
  das parcelas por uma função só (D-005); a máxima da Etapa é conferida contra a soma (D-003). ✅
- **Reprodutibilidade histórica** — detalhamento gravado com a versão na Conclusão preservada;
  parcelas gravadas, e não recalculadas na leitura. ✅
- **Publicação imutável** — critérios mudam só por Retificação; conteúdo antigo elevado com lista
  vazia. ✅
- **Nada é excluído** — migrations só acrescentam. ✅
- **Negar por padrão** — nenhuma permissão nova; autorização da Mesa e do julgamento intocadas. ✅
- **Explícito antes do irreversível (IV)** — a máxima derivada e as parcelas limitadas aparecem antes
  de gravar e de concluir. ✅
- **Simplicidade (V)** — sem estrutura para regra que nenhum Edital escreve (P-1, P-5, P-6). ✅

## O desenho

### Incremento A

**Dado e conteúdo.**

- `editais/models/etapas.py` — `CriterioAvaliacao` (ver data-model), com o comentário da D-001.
- `editais/migrations/0027_criterios_de_avaliacao.py`.
- `editais/domain/etapas.py::validate_stages` — FR-5201, FR-5203 (soma), FR-5204 (decisória),
  FR-5205 (documento do Edital, da inscrição e sem restrição de Perfil, modalidade ou condição; recebe
  os documentos do payload e decide pela mesma leitura de aplicabilidade de
  `editais/domain/documentos.py`). A mesma conferência entra na validação de publicação, que é onde se
  pega a restrição acrescentada ao documento depois do vínculo (D-010).
- `editais/application/draft.py::replace_draft` — criar critérios depois do `bulk_create` das Etapas,
  no molde dos critérios de desempate do marco; `_reject_identifiers_of_other_editais` cobre os ids.
- `editais/api/serializers.py` — `CriterionSerializer` aninhado em `StageSerializer.criteria`,
  `required=False, default=list`.
- `shared/canonical.py` — `SCHEMA_VERSION = 21` e o parágrafo do degrau.
- `publicacoes/application/publish_edital.py::_stages` — `criteria` com `_decimal_canonico`.
- `publicacoes/domain/elevacao.py` — `DEGRAUS[21] = {"criteria": []}` e `diz_o_mesmo_que_a_ausencia`.
- `editais/domain/validation.py` — `criteria` em `ETAPA_PUBLICADA`, com `CRITERIO_PUBLICADO`.
- `editais/domain/mutabilidade.py` — `("stages/criteria", campo)` para cada campo; `id` estrutural.
- `publicacoes/domain/colecoes.py` — `"/stages/*/criteria"` em `COLECOES_COM_CHAVE` e
  `FORMA_DA_COLECAO`; `publicacoes/domain/alteracoes.py` — nome do elemento e rótulos.
- `duvidas/domain/cobertura.py` — `VERSAO_DO_ESQUEMA = 21` e a classificação dos caminhos novos.
- `editais/domain/reaproveitamento.py` — ids novos e remapeamento de `documento` (FR-5212).

**Tela de elaboração.**

- `interface/templates/interface/_etapa.html` — seção Barema (UX-420) com linhas por
  `interface/_criterio_de_avaliacao.html`; oculta quando a forma é decisória.
- `interface/views.py` — `fragmento_criterio_de_avaliacao`, no molde de `fragmento_criterio`; rota em
  `interface/urls.py`.
- `interface/forms.py` — `ler_etapas` lê `criterio-etapa-<i>-<n>-*` (molde `_marcos`);
  `etapas_do_edital` e `etapas_persistidas` levam `criteria` (senão gravar outro passo apaga);
  `interface/aplicacao.py` idem.
- `interface/static/interface/barema.js` — prévia e soma ao vivo; acrescentar, remover e mover pelo
  `ordenacao.js` existente; reagir à troca de forma.
- `interface/static/interface/grupos/` (ou `telas/compor-etapas.css`) — regras das classes novas.
- `interface/revisao.py` — `criteria` em `_LIDOS_POR_COLECAO["stages"]` e o bloco na conferência.
- `interface/retificacao.py` — `CAMPOS_CRITERIO_DE_AVALIACAO`, no molde de `CAMPOS_CRITERIO`.

**PDF.**

- `publicacoes/infrastructure/pdf.py` — `_tabela_do_barema(etapa)` chamada por `_etapas` e pela
  redação em prosa (`frase_da_etapa` mais a tabela logo depois); `apresentacao.py::_parte` idem.
  Etapa sem critérios: nada é chamado, e o texto extraído não muda.

### Incremento B

- `avaliacoes/domain/barema.py` — `calcular(criterios_publicados, detalhamento, *, exigir)`:
  normaliza cada linha (quantidade inteira 0–9999 xor pontos `decimal(7,4)` ≤ máxima), recusa
  critério desconhecido ou repetido, aplica `min`, soma com `Decimal`, devolve `(linhas, total)`;
  `exigir=True` recusa pendentes nomeando-os. A justificativa é texto livre e nunca obrigatória
  (D-008). Recusas por `DomainError` com `campo` apontando a linha.
  `barema_da_versao(versao, etapa_id)` devolve os critérios publicados naquela versão — a leitura única
  de toda tela que mostra detalhamento de ato (D-011). `reconciliar(detalhamento, criterios_vigentes)`
  mantém os ids que continuam, descarta os removidos e deixa pendentes os novos (FR-5222).
- `avaliacoes/models.py` — `criterios` em `Avaliacao` e `ConclusaoAvaliacao`.
- `avaliacoes/migrations/0005_detalhamento_por_criterio.py` — `AddField` duplo e recriação da função
  do gatilho com a coluna nova (data-model).
- `avaliacoes/application/avaliacao.py` — `gravar` e `concluir` recebem `criterios`; com barema,
  recusam `pontuacao` vinda do cliente e gravam o total calculado; sem barema, recusam `criterios` não
  vazio. `concluir` copia para a `ConclusaoAvaliacao`. `reabrir` não toca o detalhamento (ele já está
  na linha); quem o reconcilia com o barema vigente é a leitura do rascunho, na Mesa.
- `avaliacoes/application/mesa.py::inscricao_para_avaliar` — rascunho: o barema da versão vigente e o
  detalhamento reconciliado; concluída: o barema de `avaliacao.versao`. Cada critério com o documento
  ligado já resolvido para o item da lista de documentos.
- `interface/forms.py::ler_avaliacao` — lê `criterio-<id>-quantidade|pontos|justificativa`.
- `interface/templates/interface/mesa_inscricao.html` — com barema, `_ficha_do_barema.html` no lugar
  do campo; concluída, a leitura da ficha. `interface/static/interface/mesa_barema.js` — total ao vivo
  (só exibição; o servidor recalcula).
- `interface/templates/interface/conclusoes.html` — o detalhamento de cada conclusão preservada.
- `resultados/domain/compatibilidade.py` — "barema" em `CAMPOS_COMPARADOS`, lendo o conjunto de
  critérios por `id`, cada um com nome, descrição, máxima, pontos por unidade, unidade e documento —
  tudo menos a ordem (D-006).
- `resultados/application/selectors.py::resultados_visiveis` — anexar o detalhamento lido da
  `avaliacao` do Resultado (ou da `decisao`, no C), com o barema de `resultado.versao` (D-011).
  `portal/templates/portal/acompanhamento.html` — a tabela (UX-423).
- `recursos/application/julgar.py` — a recusa temporária de FR-5232: correção fixada contra Resultado
  de Etapa com barema responde 409 `correcao_fixada_sem_barema`, apontando a reavaliação determinada
  (D-009). Uma constante e um teste; o C as remove.
- `portal/templates/portal/_documentos.html` — "Comprova: …" (FR-5224), lido do barema publicado.

### Incremento C

- `recursos/models.py` + `recursos/migrations/0003_detalhamento_da_correcao.py` — `criterios` em
  `DecisaoRecurso`.
- `recursos/domain/consequencia.py::derivar` — com barema, recebe o detalhamento e chama
  `barema.calcular(exigir=True)` contra o barema de `decisao.versao`; o total entra no caminho de hoje
  (`validar`, `_recusar_se_piora`). Remove a recusa de FR-5232.
- Tela de julgamento (template do julgamento em `interface/`) — mostrar o detalhamento do Resultado
  atacado e, na correção fixada, a mesma ficha (`_ficha_do_barema.html`) pré-preenchida.
- Portal — FR-5228: detalhamento da decisão, critérios alterados marcados.

## Guardiões que vão reprovar, e devem

Do levantamento ([research.md](research.md) §2): `migrations/test_migrations.py` (`editais: 27`),
`unit/duvidas/test_cobertura.py` (versão e caminhos), `contract/test_mutabilidade.py` (natureza de
cada par; "doze coleções" vira treze; `conteudo_maximo` com critérios),
`contract/test_retificacoes_api.py`, `interface/test_campos_vem_do_contrato.py`,
`unit/interface/test_revisao.py`, `unit/publicacoes/test_colecoes.py`. Cada um é atualizado na tarefa
que o quebra, com a razão no comentário. E o degrau novo pede `contract/test_elevacao_degrau_21.py`.

## Riscos

1. **O gatilho da concluída.** Esquecer a coluna na função deixa o detalhamento mutável na reabertura
   (T017 e SC-1630 o prendem).
2. **A travessia do `replace_draft`.** Gravar o passo Perfis ou Inscrição sem levar `criteria` apaga o
   barema — o mesmo defeito que a `144` evitou para o Evento (T009 o prende).
3. **A varredura de vocabulário** tem lista literal de telas; a ficha da Mesa e a seção Barema entram
   nela, com "critério" e "barema" no vocabulário da composição.
4. **O PDF mudar para Edital sem barema.** O texto extraído antes e depois é comparado (SC-1624).
5. **Contagem de tabelas append-only** não deve mudar (53); se mudar, o desenho saiu da D-004.
6. **B em produção sem C.** A recusa de FR-5232 é a rede; a regra é implantar B e C juntos (D-009).
7. **Ler o detalhamento pela versão vigente.** Toda tela de ato lê por `barema_da_versao`; SC-1633 o
   prende com uma Retificação que renomeia critério.

## Verificação

`cd backend && make lint check test-pg` em cada incremento; `make test-navegador` para a jornada da
US2; o quickstart percorrido à mão no 14/2026.
