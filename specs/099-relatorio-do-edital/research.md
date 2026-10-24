# Research: Relatório do Edital

Decisões técnicas do plano, cada uma com a razão e a alternativa descartada. As medições são do estudo
de 24/10/2026 ([rodada 2](../../doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/rodada-2.md)),
sobre o cenário coerente do Edital 61/2026.

## R-001 — A derivação mora em `interface/`, ao lado da Visão Geral e da Supervisão

- **Decision**: `interface/relatorio_do_edital.py` (derivação), `interface/relatorio_pdf.py`
  (composição do documento) e `interface/relatorio.py` (views).
- **Rationale**: o relatório reaproveita `visao_geral.vagas_do_conteudo`, `contagens_por_edital` e
  `supervisao.serie_do_edital`, que moram em `interface/`. Nenhum app de domínio importa de `interface`
  hoje (a única exceção é o assistente do portal), e pôr a derivação em `processos/application`
  inverteria essa direção. `visao_geral.py` e `supervisao.py` são o precedente exato: derivações de
  leitura, sem estado, consumidas por uma tela.
- **Alternatives considered**: `processos/application/relatorio_do_edital.py`, como o estudo propunha —
  descartado pela inversão; mover `vagas_do_conteudo` e `serie_do_edital` para camadas de domínio
  primeiro — refatoração sem valor para esta feature.

## R-002 — A leitura vê um instante só: `REPEATABLE READ` no bloco de fora

- **Decision**: a leitura do relatório roda num `transaction.atomic()` cujo primeiro comando é
  `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ`, quando o bloco é o mais externo e o banco é
  PostgreSQL. Dentro de um bloco já aberto (os testes de `TestCase`), o comando não é emitido.
- **Rationale**: no `READ COMMITTED` padrão, cada consulta vê o que estava confirmado quando ela
  começou; um desfecho gravado entre a contagem das convocações e a das vagas produziria um relatório
  que nunca existiu (FR-2519). No `REPEATABLE READ`, todas as consultas da transação veem o instante da
  primeira. O projeto não usa `ATOMIC_REQUESTS`, e por isso a view abre a transação de fora.
- **Alternatives considered**: `SERIALIZABLE` — mais do que a leitura precisa, e com mais falhas de
  serialização; materializar o relatório numa tabela — estado novo, recusado pela `022` e pelo D-005.
- **Prova**: o teste lê o SQL emitido, como `test_convergencia.py` prova o `FOR UPDATE` da interposição.

## R-003 — A emissão é serializada por Edital, e o número sai da trilha

- **Decision**: na mesma transação da leitura, a emissão trava o Edital (`select_for_update`), conta os
  eventos `EMITIR_RELATORIO` daquele Edital, compõe o documento com o número seguinte e grava o evento
  com o resumo dos bytes. Uma falha de serialização do `REPEATABLE READ` responde "tente de novo".
- **Rationale**: duas emissões simultâneas não podem ter o mesmo número (FR-2517). Travar o Edital é o
  idioma do projeto (`_lock_edital` da finalização), e o tempo de composição é de décimos de segundo.
- **Alternatives considered**: `pg_advisory_xact_lock` — existe no projeto, mas para despacho de
  aviso; a trava de linha do agregado é o idioma dos atos sobre o Edital. Número por sequência — tabela
  nova.

## R-004 — O documento é escrito pelo escritor do Edital, com marcadores e links

- **Decision**: a composição usa `Composicao(metrica=METRICA_DO_EDITAL)` e `_arquivo_do_edital` com uma
  `Navegacao` de marcadores para as seções. Os endereços `https://…` escritos no texto viram links.
- **Rationale**: `render_documento` não faz anotação de link, e o escritor do Edital faz — e embute a
  fonte, de modo que o texto institucional sai com acentos e sem "?" (`estrito`). A saída é
  determinística (sem data de criação nem `/ID`), o que dá a FR-2520 de graça.
- **Alternatives considered**: acrescentar links a `render_documento` — o comprovante promete ao
  candidato o SHA-256 de um escritor que não pode mudar um byte (FR-1383 da `069`).

## R-005 — Os endereços públicos vêm da requisição

- **Decision**: a view monta os endereços com `request.build_absolute_uri(reverse(...))` — página da
  seleção (`portal:selecao`) e de cada resultado vigente (`portal:resultado`) — e os passa à derivação,
  que não conhece a requisição.
- **Rationale**: é o que os avisos aos candidatos já fazem (`interface/avisos.py`). O host é o que a
  instituição publica, por `ALLOWED_HOSTS` e pelo proxy.

## R-006 — Pendências: as leituras das telas donas, e nenhuma regra nova

- **Decision**: marco sem resultado definitivo, por `vigente_do_marco` e pelos atos de ordenação
  vigentes; recurso e providência pendentes, por `recursos_pendentes_do_marco` e
  `providencias_pendentes_do_marco`; apuração desatualizada, pelo `estado` de `recortes_do_marco`;
  convocação sem desfecho, com prazo em curso ou encerrado, pelo `vencimento` da raiz vigente comparado
  ao instante de referência.
- **Rationale**: cada pendência é a mesma pergunta que uma tela já faz; o relatório só as reúne.

## R-007 — Etapas e recursos por Perfil, em consultas agregadas

- **Decision**: uma consulta agrupa `ResultadoEtapa.vigentes` por Perfil, Etapa, consequência e origem;
  outra agrupa os recursos por Perfil e situação. As Etapas de cada Perfil são as dos marcos dele, mais
  a governada.
- **Rationale**: `panorama_da_etapa` conta como participante da Etapa inscrição de Perfil cujo marco
  não a tem (estudo, rodada 2, §A.2); `recursos_do_edital` traz nome e protocolo. O relatório precisa
  de contagens por Perfil e sem dado pessoal.

## R-008 — Registros posteriores ao desfecho, pela trilha dos agregados do Edital

- **Decision**: os identificadores do Edital, das Retificações, recursos, convocações, desfechos,
  apurações, publicações de resultado, atos de ordenação e cortes do Edital; os registros de auditoria
  desses agregados com instante posterior ao do ato de desfecho, agrupados por operação, com rótulo
  simples por operação conhecida e "outros registros" para o resto.
- **Rationale**: `trilha_do_edital` não reúne resultado, recurso, ordenação nem corte, e pagina por
  cursor. Ampliá-la é escopo de outra tela.

## R-009 — Privacidade pelo desenho, com limiar de cinco

- **Decision**: fatos não públicos só por Perfil; em Perfil com menos de cinco inscrições enviadas, a
  derivação devolve ausência com motivo de privacidade no lugar dos números não públicos (D-006).
- **Rationale**: a regra fica num lugar só, na derivação; a página e o PDF não decidem o que mostrar.

## R-010 — Rótulos: importados, com a exceção do aceite

- **Decision**: os desfechos vêm de `portal/situacao.py` (`DESFECHOS`), com `ACEITE` trocado por
  "Convocação aceita"; as decisões de recurso, de `recursos/application/selectors.py` (`ESPECIES`).
- **Rationale**: FR-2545; o aceite muda porque "vaga aceita" é lido como vaga preenchida (ajuste C).

## R-011 — A fixture é o cenário coerente do estudo

- **Decision**: `tests/fixtures/relatorio.py` reproduz o roteiro `cenario_coerente.py` como função
  parametrizada — escala, final sem pendência, cancelamento, inscrições abertas —, pelos commands da
  aplicação e com o relógio na data de cada ato.
- **Rationale**: é o cenário que a aprovação do usuário leu; os números esperados dos testes são os da
  maquete v2.

## R-012 — Desempenho: forma constante, provada por contagem de consultas

- **Decision**: o teste de orçamento compara o número de consultas entre escala 1 e escala 10.
- **Rationale**: medido no estudo, 145 consultas nas duas escalas. Teste de tempo absoluto oscila sob
  carga (memória do projeto, e a nota da `098` sobre o runner), e não entra.
