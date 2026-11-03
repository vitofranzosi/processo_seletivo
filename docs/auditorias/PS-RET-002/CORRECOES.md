# Correções — PS-RET-002

Escopo: somente RET-001 e RET-002. Sem migration, alteração de contrato de payload, permissões,
edição Web, navegação nova ou escrita sobre dados reais.

## 1. Base futura

**Causa-raiz:** `interface/views.py`, `_versao_vigente`, selecionava maior `valid_from` sem limitar
ao instante atual. O GET de composição mostrava futuro como vigente; publicar imediatamente
conferia contra o conteúdo atual e recusava a precondição divergente.

**Regra:** FR-2609 e FR-2610 da nova spec 101; temporalidade cumulativa já definida na 001.
`publicacoes/domain/consolidation.py` aplica atos por `(effectiveAt, publicationOrder)`. O futuro
não é cancelado ou reescrito pela publicação de outro ato imediato.

**Alteração:** filtro `valid_from__lte=timezone.now()` na seleção da base. Mantida a ordenação por
vigência/materialização, o retorno vazio para Edital sem versão e a base explícita que atravessa
conferência/POST. Não se recalcula silenciosamente o alvo de um formulário já aberto.

**Efeito observado:** Chrome publicou uma Retificação imediata com novas datas mesmo após um ato
futuro publicado. O portal passou às novas datas atuais; os dois registros de consolidação da
fronteira futura permanecem e correspondem ao conteúdo do ato futuro imutável. Há novas versões
append-only, não atualização de publicações anteriores.

**Riscos controlados:** bases que envelhecem continuam sujeitas às precondições existentes; conflitos
estruturais continuam 409. Intervalo inválido numa fronteira futura agora retorna 422 e desfaz
todas as escritas do ato tentado. Nenhuma política nova de precedência foi criada.

**Testes:** `test_base_temporal_da_retificacao.py`; teste existente
`test_publication_that_would_break_a_later_effective_act_is_rejected`; testes existentes de revisão
obsoleta, precondição e replay; E2E-01, E2E-02, E2E-04 e E2E-05.

## 2. Intervalo invertido

**Causa-raiz:** a conferência central verificava forma/formato e outras regras de cronograma, mas
não comparava `endAt` com `startAt`. O comentário anterior dizia que a coerência não tinha decisão
normativa, em conflito com FR-017 da 001. PS-RET-002 autorizou expressamente a garantia.

**Regra:** FR-2611 e FR-2612 da 101. Término não pode ser anterior ao início; igualdade é permitida;
Evento sem término continua permitido quando sua forma admite isso. Comparação de instantes com
offset, não de textos ou dias isolados.

**Alteração:** `_intervalos_dos_eventos` em `editais/domain/validation.py`, chamado por
`validate_for_publication`; achado `BLOCKING_ERROR`, código `schedule_end_before_start`, mensagem
em português e caminho do campo `endAt`. Usados os parsers e identificadores de Evento existentes.
Textos inválidos continuam sendo diagnosticados pela conferência de forma, sem erro de comparação
entre datetime ingênuo e consciente.

**Alcance:** a validação já é compartilhada pela criação/edição de Retificação, publicação original
e conferência de cada consolidação afetada. Assim, um formulário invertido é recusado antes de
criar o rascunho; a barreira na publicação continua necessária para combinação de atos concorrentes.

**Atomicidade observada:** dois atos individualmente válidos foram preparados. Um moveu o início
das inscrições para 06/11 23:00, mantendo término em 07/11. O outro pretendia término em 06/11
12:00, válido contra a base original. Após publicar o primeiro, a publicação do segundo pelo Chrome
retornou 422 com o Evento e o erro. Estado permaneceu HOMOLOGADA, publication_id nulo, sem novo
evento de sucesso PUBLICAR e sem troca da versão vigente. Nenhum estado foi forçado por SQL.

**Testes:** 36 combinações de unidade (dois atos × três tipos × seis pares de datas); cinco testes
de integração para recusa precoce, múltiplos Eventos, concorrência, fronteira futura e igualdade;
E2E-03 e E2E-06. Não se introduziu obrigação de duração positiva.

## Integridade e segurança

Os serviços de autorização, escopo, segregação, idempotência, controle de revisão e registro de
autoria não foram alterados. As validações executam dentro da transação existente. Recusas não
criam evento de publicação bem-sucedida; seguem o mecanismo existente de registro de rejeição.

`integridade-verificada.json`: 28 verificações aprovadas, incluindo hashes dos atos, originais
comparados às respostas da preparação, base futura, registros append-only, ausência de ato parcial
e preservação da ocorrência usada como semente. `autorizacao-http.json`: 15 verificações HTTP reais.

## Limitações externas ao escopo

Lint geral e `makemigrations --check --dry-run` identificaram problemas preexistentes em três
modelos não alterados. `baseline-checks.json` comprova igualdade desses arquivos com HEAD e
reproduz os problemas de lint/formatação sobre o conteúdo original. As migrations sugeridas
referem-se às mesmas classes fora do escopo. Não foram criadas migrations para esse desvio.
