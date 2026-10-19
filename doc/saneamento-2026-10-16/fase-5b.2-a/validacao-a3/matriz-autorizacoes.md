# Matriz de autorizações — A.3

Data: 19/10/2026. Fonte de autorização: somente a solicitação humana desta rodada.
Nomes PERMITIDAS/ESCOPOS no código descrevem capacidades preparadas; não são concessões humanas.

| Operação | Situação |
|---|---|
| Inspeção estática de arquivos | Autorizada |
| Revisão documental | Autorizada |
| Preparação de comandos | Autorizada |
| Consulta à engine Docker | Aguarda autorização específica |
| Inicialização de Docker | Bloqueada |
| Criação de recursos | Bloqueada |
| Criação de bancos e papéis | Bloqueada |
| Execução de migrations | Bloqueada |
| Carga de dados | Bloqueada |
| Inicialização da aplicação web | Bloqueada |
| Descarte de recursos | Bloqueada |
| Commit, push e merge | Bloqueados |

Também não executados/autorizados: Compose, pull/build, bootstrap/start PostgreSQL, demonstrações,
consultas SQL, envio de e-mails, rebase/checkout, parada de serviços ou nova consulta aos registries.
Testes anteriores foram analisados estaticamente; nenhum runner de teste foi invocado nesta rodada.

## Limites dos arquivos

A A.3 só cria seis documentos em `validacao-a3/`. Não modifica fontes, configurações operacionais,
políticas anteriores, manifestos, digests, hashes históricos, specs ou Constituição. Não cria
`autorizacao.json`, `homologacao.env` ou `docker-cliente/config.json`. Exemplos documentais e
fragmentos JSON não são arquivos de configuração ativos nem aprovação.

## Concessão futura proposta, sem efeito atual

A aprovação futura deve nomear somente `inspecionar`, revisão A.2 do operador preservado,
manifesto/hashes, endpoint local, cliente vazio aprovado, responsável, janela e destino de evidências.
Deve autorizar explicitamente a preparação dos dois arquivos de controle se ainda inexistentes.
Nenhuma senha de banco, configuração de desenvolvimento ou autenticação de registry é necessária.

A consulta não concederá nenhuma outra ação. Se retornar falha, interromper e registrar; não iniciar
Docker, selecionar outro endpoint, elevar privilégios, repetir automaticamente ou corrigir infraestrutura.
Autorizar a consulta não equivale a aprovar a engine para provisionamento. Aprovar este relatório
documental tampouco equivale a autorizar a consulta.
