# Índice de evidências — PS-RET-E2E-001

Data de execução: 28/10/2026, aproximadamente 09:38–10:21, America/Sao_Paulo. Os arquivos registram seus horários reais. Todos os dados e identidades são sintéticos.

## Leitura recomendada

1. [RELATORIO-FINAL.md](RELATORIO-FINAL.md): conclusão A–M, ambiente, diagnóstico e limites.
2. [MATRIZ-TESTES.md](MATRIZ-TESTES.md): procedimento, esperado, observado e situação de cada grupo.
3. [INCONSISTENCIAS.md](INCONSISTENCIAS.md): achados e reprodução.

## Navegador real

- `00-lista.png` / `.txt`: lista dos quatro Processos ativos sintéticos.
- `01-formulario.png` / `.txt`: formulário inicial de retificação.
- `c1-*`: cenário imediato, da conferência ao portal público. `c1-portal.png` mostra encerramento 12/11 às 22h37, sorteio em 14/11 e os dois documentos.
- `c2-*`: cenário futuro publicado, vigência 30/10 às 12h00 e portal ainda com as datas anteriores.
- `c3-*`: cenário de vigência vencida, publicação recusada explicitamente.
- `c4-*`: criação, submissão e devolução para elaboração.
- `base-futura-*`: formulário sobre versão futura, comparativo e recusa efetiva de publicação imediata.
- `pendencias-ausentes.png` / `.txt`: retorno ao edital sem link da retificação homologada pendente.
- `erro-inexistente.png` / `.txt`: recurso inexistente com sessão autenticada.
- `erro-sem-permissao.png` / `.txt`: confirmação direta sem permissão; `erro-sem-permissao-post.json`: POST com sessão e CSRF válido, HTTP 403.
- `rede-executar.json` e `rede-base.json`: eventos CDP de requisição/resposta, incluindo corpos dos formulários, navegações, códigos e redirecionamentos. POSTs que respondem 302 estão em `requestWillBeSent.params.redirectResponse`, não somente em `responseReceived`.
- `rede-inspect.json`: exploração inicial do formulário.
- `campos-0.json` a `campos-3.json`: nomes, rótulos e valores dos campos temporais reais.
- `resultados-navegador.json`: associação dos quatro UUIDs de edital/retificação e valores preenchidos.

`falha-navegador.png`/`.txt`, se presentes, registram uma tentativa inicial do script que procurava o código do Processo como texto clicável. A aplicação usa o título como link. O seletor foi corrigido somente no script de auditoria e o percurso completo foi repetido; isso não é falha do produto.

## HTTP e banco

- `preparacao-http.json`: requisições de preparação de cenários pelas APIs reais. O primeiro cenário foi retomado após uma tentativa de ativação redundante: publicar o edital já havia ativado o Processo. O script foi ajustado, sem modificar estado diretamente nem contornar validação.
- `cenarios.json`: quatro editais e a autoridade habilitada.
- `c1-api.json`, `c2-api.json`, `c3-api.json`: versão pública obtida depois da criação e depois da tentativa de publicação.
- `integracao-http.json`: autorização, concorrência, edição, segregação, replay, atos públicos e respostas/hash de PDFs.
- `integracao-complementar.json`: falta de efeito, cronograma invertido, portal e recurso público inexistente.
- `postgresql.json`: primeira extração por SQL real de leitura, com as consultas e colunas.
- `postgresql-final.json`: extração final após base futura e cronograma invertido. Não confundir com o momento da primeira captura válida do portal.
- `verificacoes.json`: comparação dos conteúdos API, preservação dos originais entre extrações, ausência de duplicação, privilégios e consulta do portal sem Cookie/Authorization. O item `base-futura-comprovada` confirma o fato adverso; `passed:true` significa que a comprovação encontrou a base futura, não aprovação do produto nesse caso.
- `anonimo-c1.html` a `anonimo-c4.html`: respostas do portal sem sessão administrativa, capturadas ao final. `anonimo-c1.html` já contém o efeito do teste adverso de cronograma invertido; `c1-portal.png` registra o cenário válido anterior.
- `servidor.log`: status HTTP e mensagens do runserver exclusivo.

No log de integração, `inexistente` com HTTP 200 representa redirecionamento anônimo para login; não foi usado como prova de acesso ao objeto inexistente. O recurso foi verificado separadamente com sessão e na API pública.

## Testes existentes

- `pytest.log`: rodada selecionada, 85 passed / 1 failed, cuja falha foi ausência de arquivo das specs no container de auditoria.
- `pytest-contrato-reexecucao.log`: caso de contrato repetido após cópia das specs, 1 passed.

Não houve execução da suíte completa nem instalação de dependências. Fonte montada somente para leitura. O pytest rodou com `-p no:cacheprovider`; Python com `PYTHONDONTWRITEBYTECODE=1` no container.

## Scripts exclusivos da auditoria

- `preparar.py`: unidade/autoridade por operações existentes e quatro editais por HTTP real.
- `navegador.mjs`: CDP do Chrome real, formulários, cliques, navegação, capturas e rede.
- `verificar.py`: integração HTTP e consultas SQL de leitura.
- `complementar.py`: casos adversos e extração final; reutiliza definições do script anterior sem repetir suas mutações.
- `analisar.py`: confronta os artefatos já gravados e consulta portal anônimo.

Não executar novamente esses scripts indiscriminadamente: eles praticam atos normativos sintéticos e alguns cenários terminam em estados finais. Para repetir do início, usar outro ambiente descartável e identificadores próprios.

## Isolamento e preservação

Cluster novo, rede exclusiva e volume PostgreSQL novo; zero tabelas públicas antes da preparação. Runtime separado da role migration e do superusuário de preparação. Nenhuma migração, comando ou teste foi apontado aos bancos preexistentes. A suíte teve database próprio dentro do cluster descartável.

Os containers da auditoria e o Chrome exclusivo foram encerrados ao final sem apagar o banco. Às 10:21, `git diff --exit-code` terminou com sucesso; `git status --short` continha somente `?? docs/auditorias/` (novos artefatos autorizados) e `?? docs/sorteio/` (preexistente). O diretório `chrome-profile/` contém somente o perfil temporário sintético do navegador usado nesta execução; não é um perfil pessoal. O código versionado e `docs/sorteio/` permanecem intactos.
