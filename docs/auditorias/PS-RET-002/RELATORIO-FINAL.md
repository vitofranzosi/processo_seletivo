# PS-RET-002 — Diagnóstico e correção controlada

Data: 28/10/2026. Ambiente: desenvolvimento local e cluster de testes exclusivo.

## A — Identificação e baseline

- Repositório: `D:\projetos\cefor\processo_seletivo`, backend em `backend/`.
- Branch: `002-inserir-documentacao-sistema`.
- HEAD inicial e final: `42871b4243cdb5f00b0a560d6323281df8590087`. Sem commit, push, merge ou deploy.
- Git inicial: `?? docs/auditorias/` e `?? docs/sorteio/`; ambos preservados. A auditoria histórica
  PS-RET-E2E-001 não foi editada.
- Git final: dois módulos de aplicação alterados, registro da spec 101 no README, três testes novos, pasta nova em specs/101 e
  novos artefatos PS-RET-002. Nenhum arquivo fora dessa relação foi corrigido ou descartado.
- Instruções: AGENTS.md, Constituição e quatro documentos principais PS-RET-E2E-001 consultados.
- Python 3.13.16/Django 5.2.17/pytest 8.4.2 no container; Chrome 155.0.8059.80/Node 24.13.1;
  PostgreSQL 18.6 exclusivo. Nenhuma dependência instalada globalmente ou arquivo de dependência
  modificado.
- Cluster novo: `ps-ret-002-db:5432`, database `auditoria_ret_002`, rede `ps-ret-002`, volume novo.
  Zero tabelas públicas antes das escritas; identificação em `isolamento.txt`. Suítes com nomes
  próprios (`regressao_ret_002`, `selecao_ret_002`, `suite_completa_ret_002` e seus bancos de teste).
- Aplicação E2E na porta 8018 com role `auditoria_002_runtime`; backend/specs montados somente
  para leitura. Provisionamento → migrations → provisionamento: 41/41 tabelas protegidas.

## B — Diagnóstico do caso real

**CASO_REAL_NAO_IDENTIFICADO.** Foi investigada somente por leitura a conexão do container local
existente (`db:5432`, database `processo_seletivo`, runtime `processo_seletivo_runtime`). A transação
foi explicitamente READ ONLY e desfeita. Resultado: 1 Edital, **zero Retificações e zero Alterações**.
Não havia candidato para reconstruir o incidente. Não se presumiu que o único edital fosse o caso.

Não se afirma que o incidente individual foi resolvido. O próximo passo desse diagnóstico exige
identificar URL/UUID e o ambiente correto. Detalhes em [DIAGNOSTICO-CASO-REAL.md](DIAGNOSTICO-CASO-REAL.md).

## C — Causa-raiz da versão futura

O GET de composição escolhia a maior vigência materializada, sem filtrar o instante atual. Havendo
ato futuro, oferecia esse conteúdo como base imediata. A publicação, corretamente, comparava os
valores anteriores com a versão vigente agora e recusava a operação com conflito.

## D — Correção da versão futura

`interface/views.py::_versao_vigente` agora filtra `valid_from <= timezone.now()`. Preservados base
explícita no POST, ordenação/materialização, autorização e controle de revisão. Uma publicação
concorrente não troca silenciosamente a base que a pessoa viu.

Conservada a política existente: atos aplicados por vigência e ordem de publicação; novas
consolidações append-only nas fronteiras futuras; nenhum cancelamento ou reescrita de atos.
Conflitos legítimos continuam recusados, inclusive quando uma imediata invalidaria o futuro.

Chrome comprovou o caso: ato futuro publicado para 30/10; em 28/10 a nova imediata partiu da vigente,
publicou e alterou as datas atuais. O ato futuro e as versões anteriores permanecem íntegros.

## E — Causa-raiz do cronograma

A conferência central verificava os campos/formatos e outras coerências, mas não comparava início
e término. Isso permitia publicar intervalo invertido e divergia de FR-017 da 001. O procedimento
atual autorizou expressamente essa correção, sem necessidade de decisão institucional adicional.

## F — Correção do cronograma

`editais/domain/validation.py::_intervalos_dos_eventos`, chamado na conferência central, compara
datetimes conscientes. Término anterior produz `BLOCKING_ERROR`, código
`schedule_end_before_start`, mensagem com o Evento e caminho do `endAt`. Igualdade e Evento sem
término continuam permitidos quando o modelo os admite.

O mesmo serviço já atua na criação/edição, publicação original e consolidação de Retificação.
Consequentemente, o intervalo inválido é barrado já na criação. Para comprovar a guarda na publicação,
foram usados atos individualmente válidos cuja combinação concorrente inverteria o período. A
publicação retornou 422 e desfez todas as escritas parciais. Não se usaram mocks ou SQL de escrita.

## G — Testes automatizados

- Antes da correção: 15 falhas e 24 aprovações nas regressões iniciais; ambos os defeitos reproduzidos.
- Seleção final: **128 aprovados, zero falhas e zero pulados**, em 389,31s. São os 86 testes anteriores
  e 42 casos novos. Evidência: `regressao-selecionada-final.log`.
- As novas regressões cobrem offsets/mudança de dia, três tipos de Evento, igualdade, término
  ausente, forma inválida, múltiplos Eventos, concorrência, fronteira futura, rollback e histórico.
- Os testes anteriores cobrem permissões, estados, revisão obsoleta, replay, auditoria e conflitos
  legítimos. Nenhuma regra de autorização foi relaxada.
- JavaScript no Node já instalado no host: **154 aprovados, zero falhas e zero pulados**.
  Rastreabilidade/README finais: **7 aprovados e 1 falha**, exclusivamente a omissão preexistente
  `099-link-documentacao`; as citações da nova spec passaram. Logs em `javascript-host.log` e
  `rastreabilidade-final.log`.
- Primeira execução ampla: **12.967 aprovados, 133 falhas, 14 pulados e 55 erros**, em 1.159,98s.
  Não é uma suíte verde: faltavam `/app/doc` e README/fixtures no primeiro runner; bytecode do host
  Windows também prejudicou introspecção de fonte em Linux. Duas expectativas iniciais dos novos
  testes ainda esperavam criar rascunho inválido e foram corrigidas para a recusa precoce, mantendo
  a prova independente de publicação inválida por concorrência. Esses casos passaram na seleção final.
- Repetição dos arquivos afetados, com repositório completo somente para leitura e cache Python
  separado: **617 aprovados, 7 falhas, 12 pulados, 1 erro**, em 55,02s. Rechecagem dos caminhos
  Windows restantes: **1.086 aprovados, 1 falha, 2 pulados**, em 25,28s. Contagens não são somadas,
  pois há sobreposição de cobertura.
- Falhas remanescentes: seis expectativas da navegação, um erro de fechamento de FileResponse na
  mesma suíte, catálogo incompleto do README e migrations pendentes dos modelos fora do escopo.
  Navegação/migrations foram repetidas carregando os dois módulos originais de HEAD, sem restaurar
  arquivos do workspace: **7 falhas, 39 aprovações, 1 erro**, os mesmos casos remanescentes desse
  recorte. O catálogo do HEAD já omitia `099-link-documentacao`; `baseline-readme.json` comprova.
  A nova 101 foi registrada e não é mais uma omissão criada por este incremento.
- Lint e formatação dos cinco arquivos alterados: aprovados; `git diff --check`: aprovado.
- `manage.py check` e `migrate --check`: aprovados no banco de E2E preparado.

**Ressalvas de baseline:** lint geral acusa E501 em `processos/models.py:30` e formatação em três
modelos não alterados. `makemigrations --check --dry-run` aponta constraints sem migrations em
`processos`, `editais` e `comissoes`. `baseline-checks.json` comprova os mesmos modelos idênticos
ao HEAD e reproduz o lint sobre o conteúdo original. Não foram criadas migrations nem corrigidos
esses modelos fora do escopo. Não se apresenta o check geral como verde.

## H — E2E reais

**Seis cenários aprovados em Chrome real**: imediata; imediata com futura preexistente; intervalo
inválido; rascunho sem efeito público; publicação futura; publicação sem permissão.

Criar, submeter, homologar e publicar foram realizados por formulários reais, com perfis distintos
e Autoridade Signatária válida. As respostas e o portal foram confrontados com SQL. No teste de
concorrência, o ato concorrente foi praticado por HTTP real e a candidata foi publicada pelos
controles do Chrome. Não se classifica Django Test Client como navegador.

Datas comprovadas: término 12/11/2026 22:37 -03 = 13/11 01:37 UTC; sorteio programado 14/11 14:23
-03 = 14/11 17:23 UTC. No caso com ato futuro, a imediata passou a término 11/11 21:17 e sorteio
13/11 15:29. `USE_TZ=True`, `TIME_ZONE=America/Sao_Paulo`. Ocorrência da semente preservada.

Detalhes e índices em [EVIDENCIAS-E2E.md](EVIDENCIAS-E2E.md) e `resultados-e2e.json`.

## I — Segurança e permissões

| Operação | Perfil no mapa Web | Permissão | Resultado validado |
|---|---|---|---|
| Criar | Elaborador | `retificacao:elaborar` | E2E positivo; sem permissão 403 |
| Editar rascunho pela API | Elaborador | `retificacao:elaborar` | 200; sem permissão 403; revisão antiga 412 |
| Submeter | Elaborador | `retificacao:submeter` | E2E positivo; sem permissão 403 |
| Homologar | Homologador | `retificacao:homologar` | E2E positivo; sem permissão 403 |
| Devolver | Homologador | `retificacao:homologar` | Regressões existentes aprovadas; sem permissão 403 |
| Publicar | Publicador | `retificacao:publicar` | E2E positivo; POST direto sem permissão 403 |
| Consultar trilha administrativa | Auditor | `auditoria:consultar` | HTTP 200 autorizado; outro perfil 403 |
| Consultar histórico publicado | Anônimo | Sem permissão administrativa | HTTP 200, sem sessão |

Escopo incompatível retornou 404; publicação antes de homologação 409. Segregação, validação da
autoridade e idempotência não foram modificadas. `autorizacao-http.json` contém 15 verificações;
`seguranca-adicional.json`, outras quatro, todas aprovadas. Não foram gravados tokens ou headers.

## J — Integridade de dados e auditoria

SQL final: 6 Retificações, 10 Alterações, 8 Publicações, 9 Versões Consolidadas e 49 eventos de
auditoria. Os registros incluem base, autores, horários, fundamento, vigência e publicação.

`integridade-verificada.json`: **28 verificações aprovadas**. Originais mantêm os hashes recebidos
na preparação; conteúdo canônico confere com o hash; as duas versões da fronteira futura permanecem;
runtime não tem UPDATE/DELETE nas tabelas append-only conferidas; método da semente preservado.

Tentativa inválida: HOMOLOGADA, publication_id nulo, nenhum evento PUBLICAR bem-sucedido e versão
pública igual àquela imediatamente anterior à tentativa. A auditoria segue a política existente;
não se confunde log de rejeição com publicação.

## K — Arquivos alterados

Aplicação, somente:

- `backend/processo_seletivo/interface/views.py`: filtro temporal da base.
- `backend/processo_seletivo/editais/domain/validation.py`: validação do intervalo e comentário.

Três arquivos de testes novos:

- `backend/tests/interface/test_base_temporal_da_retificacao.py`.
- `backend/tests/unit/editais/test_intervalo_do_evento.py`.
- `backend/tests/integration/publicacoes/test_intervalo_retificado.py`.

Artefatos novos: spec/plan/tasks em `specs/101-publicacao-segura-de-retificacoes/`; seis relatórios
e scripts/capturas/logs em `docs/auditorias/PS-RET-002/`. Sem alteração de modelos, migrations,
permissões, dependências, auditorias ou especificações históricas.

`README.md` recebeu somente a linha da nova spec 101 no catálogo, necessária à rastreabilidade
do incremento. A entrada ausente da 099 já era problema de HEAD e foi preservada fora do escopo.

## L — Pendências para PS-RET-003

Permanecem fora do escopo: navegação para Retificações pendentes e edição Web das devolvidas.
Detalhes em [PENDENCIAS-PS-RET-003.md](PENDENCIAS-PS-RET-003.md). A edição pela API foi apenas testada.

## M — Classificação final

**CONCLUÍDO COM RESSALVAS.** Os dois defeitos estão corrigidos, os 128 testes diretamente
relacionados passaram e os seis E2E reais comprovaram os critérios essenciais em PostgreSQL.
O incidente individual permanece **CASO_REAL_NAO_IDENTIFICADO**. A suíte geral e os checks de
baseline não estão verdes; as falhas residuais foram delimitadas e comparadas com HEAD, sem
correções fora do escopo. Não há autorização de merge ou deploy.

## N — Próxima ação recomendada

Revisar o diff dos dois módulos e as evidências; tratar separadamente os desvios de baseline antes
de integração/deploy. Identificar UUID/ambiente para fechar o incidente real. PS-RET-003 depende de
autorização posterior. Nenhum commit ou deploy foi realizado.

Fechamento em 28/10/2026 às 12:00 -03:00: Chrome exclusivo encerrado e containers
`ps-ret-002-suite`, `ps-ret-002-app` e `ps-ret-002-db` parados, preservando o banco sintético.
Containers preexistentes continuam ativos. Estado final em `git-final.txt`; nenhum descarte
de alterações preexistentes. As duas alterações de aplicação estão disponíveis no working tree.
