# E2E reais — PS-RET-002

## Ambiente e proteção

Chrome 155.0.8059.80 headless real, automatizado via Chrome DevTools Protocol com Node 24.13.1.
Playwright não foi instalado. Páginas reais, preenchimento de inputs, cliques, confirmações,
troca de identidade e recarregamento. Não se usou Django Test Client para estas comprovações.

Servidor exclusivo `http://127.0.0.1:8018`, container `ps-ret-002-app`, Django 5.2.17/Python 3.13.16,
settings de desenvolvimento; fonte do backend e specs montadas somente para leitura. Banco novo
`auditoria_ret_002` no PostgreSQL 18.6, host `ps-ret-002-db`, porta 5432, rede exclusiva `ps-ret-002`.
Conexão de runtime `auditoria_002_runtime`; preparação por roles próprias de administração/migration.

Antes da primeira escrita: instância nova, volume novo, identidade/versão conferidas e **zero
tabelas públicas**. O banco não tem porta publicada no host. `isolamento.txt` registra containers
e montagens. Preparação em três passos com **41 de 41** tabelas protegidas. Suítes usaram databases
próprios no mesmo cluster isolado. Nenhum banco real recebeu escrita.

As evidências não incluem headers de autenticação, cookies ou CSRF. `rede-sanitizada.json` e
`rede-continuacao-sanitizada.json` contêm método, URL, corpo do formulário sem CSRF, status e
redirecionamentos. `E2E-06-resposta.json` conserva somente status e presença de mensagem.

## Matriz dos seis cenários

| ID | Perfil / ações reais | Esperado e observado | Persistência / evidência | Resultado |
|---|---|---|---|---|
| E2E-01 | Elaborador cria; Homologador fundamenta; Publicador seleciona autoridade e confirma | Término 12/11/2026 22:37 e sorteio programado 14/11 14:23 publicados imediatamente; portal mostra novas datas | `E2E-01-resultado.png`, `E2E-01-portal.png`, `E2E-01-api.json`; PUBLICADA e versão SQL | APROVADO |
| E2E-02 | Após E2E-05, mesmos três papéis criam e publicam imediata sobre o mesmo Edital | Base do formulário é a vigente, não a futura. Portal passa a término 11/11 21:17 e sorteio 13/11 15:29 | `E2E-02-base.json`, `E2E-02-resultado.png`, `E2E-02-portal.png`; ato futuro e duas consolidações da fronteira preservados | APROVADO |
| E2E-03 | Elaborador tenta intervalo invertido; depois prepara candidata válida. Ato concorrente válido move só o início por HTTP real; Publicador tenta publicar candidata no Chrome | Formulário invertido é recusado antes de criar. Na combinação concorrente, publicação retorna 422, explica o Evento e preserva versão anterior válida | `falha-e2e.png` documenta a recusa precoce, não defeito residual; `E2E-03-resultado.png`, `E2E-03-portal.png`, rede de continuação, SQL com HOMOLOGADA e sem publicação | APROVADO |
| E2E-04 | Elaborador cria e conserva rascunho | Portal e API não mudam | `E2E-04-rascunho.png`, `E2E-04-portal.png`, SQL EM_ELABORACAO | APROVADO |
| E2E-05 | Três papéis publicam com vigência 30/10/2026 12:00 -03:00 | PUBLICADA, mas portal de 28/10 mantém cronograma anterior | `E2E-05-resultado.png`, `E2E-05-portal.png`, fronteira SQL 30/10 15:00 UTC | APROVADO |
| E2E-06 | Elaborador abre URL de publicação e envia POST direto com sessão e CSRF válido | Falta de permissão explicada; 403 no backend; nenhum efeito no conteúdo publicado | `E2E-06-sem-permissao.png`, `E2E-06-resposta.json`, rede sanitizada e SQL | APROVADO |

Identificadores completos, campos preenchidos, bases e respostas públicas anteriores/posteriores:
`resultados-e2e.json`. Screenshots e textos de cada etapa incluem comparativo, rascunho, revisão,
homologação, resultado e portal.

## Detalhe do E2E-03

A primeira execução do roteiro supunha que seria possível criar um rascunho invertido para tentar
publicá-lo depois. A validação compartilhada já impediu a criação, com mensagem explícita e sem
UUID; o roteiro parou nessa expectativa de teste, conservada em `falha-e2e.*`. Os três cenários já
aprovados foram preservados e o roteiro continuou sem repetir suas publicações.

Para provar especificamente a guarda de publicação sem contornar validações: a candidata válida
declara fim em 06/11 12:00 contra o início original de 27/10. Um ato concorrente válido declara
início em 06/11 23:00, mantendo fim original em 07/11. Submissão, homologação e publicação desse
concorrente são HTTP reais da API. A candidata foi então publicada pelos controles reais do Chrome;
consolidar ambos inverteria o intervalo. Resultado 422, HOMOLOGADA, publication_id nulo e versão
pública exatamente igual àquela consultada imediatamente antes da tentativa. Não houve SQL de
escrita nem manipulação de estado, horário ou permissões.

## Dados e integridade

- Quatro Processos/Editais sintéticos preparados por operações existentes; uma autoridade sintética
  válida cadastrada pelo serviço de domínio. `preparar.py` / `preparacao-http.json`.
- Todas as transições das Retificações ocorreram pela interface ou HTTP real; SQL somente leitura
  para conferi-las. `conferir.py` / `postgresql.json` incluem consultas e resultados.
- Estado final: 6 Retificações, 10 Alterações Normativas, 8 Publicações, 9 Versões Consolidadas,
  49 eventos de auditoria, incluindo preparação e teste posterior de edição pela API.
- `autorizacao-http.json`: 15 verificações adicionais, incluindo todas as operações negativas,
  edição autorizada/obsoleta e consulta anônima. A edição pela API é teste, não funcionalidade Web.
- `integridade-verificada.json`: 28 verificações aprovadas, incluindo originais comparados aos hashes
  da preparação, hashes canônicos, duas consolidações futuras preservadas, privilégio append-only,
  ausência de publicação parcial e método/ocorrência da semente não alterados.

Instantes: 12/11 22:37 -03:00 = 13/11 01:37 UTC; 14/11 14:23 -03:00 = 14/11 17:23 UTC.
`USE_TZ=True`, `TIME_ZONE=America/Sao_Paulo`. A data do evento SORTEIO do cronograma foi alterada;
a ocorrência do método que fornece a semente permaneceu intacta.

Não se aguardou 30/10 nem se alterou relógio ou banco para simular tempo. A manutenção da versão
atual, a materialização da fronteira futura e sua composição foram verificadas diretamente.

## Scripts e logs

`e2e.mjs` usa Chrome; `conferir.py` usa HTTP real e SQL de leitura; `analisar_evidencias.py`
confronta os artefatos; `conferir_baseline.py` verifica modelos originais de HEAD. `servidor.log`
registra respostas reais. Logs intermediários de testes não são confundidos com aprovação final.

`ps-ret-002-suite` foi criado para a rechecagem com todo o repositório montado somente para leitura,
permitindo ler fixtures de `doc/`, README e documentação. `PYTHONPYCACHEPREFIX` separado impede ler
bytecode Windows no runner Linux. `baseline_pytest.py` carrega cópias de HEAD dos dois módulos
alterados exclusivamente no processo comparativo. Não restaura nem troca arquivos do workspace.

Os containers/banco da auditoria são preservados sem exclusão de dados e encerrados ao término.
Os scripts são específicos deste ambiente sintético; não executar contra ambiente real.

`sanitizacao-logs.json` registra a ocultação de valores de Bearer sintéticos que o pytest havia
incluído nos tracebacks. Headers e cookies do Chrome nunca foram gravados nos logs sanitizados.
