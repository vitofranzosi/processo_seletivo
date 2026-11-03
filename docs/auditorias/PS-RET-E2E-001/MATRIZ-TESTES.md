# Matriz de execução — PS-RET-E2E-001

28/10/2026. Situações por grupo: 8 APROVADOS, 3 REPROVADOS, 0 BLOQUEADOS, 0 NÃO EXECUTADOS. Reprovação considera o requisito completo do grupo, mesmo quando seus demais subcasos passam. HTTP/SQL não são classificados como navegador.

| ID / objetivo | Pré-condições | Procedimento executado | Esperado | Observado / situação | Evidência | Diagnóstico |
|---|---|---|---|---|---|---|
| E2E-01 Criar | Edital sintético publicado; Elaborador | Chrome: lista → Processo → Edital → Retificar; alterar término e sorteio; justificar; comparar; criar | Duas alterações, UUID, EM_ELABORACAO, público intacto | **APROVADO**; comparativo com duas alterações; redirecionamento ao novo UUID; conteúdo público anterior | c1-comparativo.png, c1-elaboracao.png, c1-api.json before, rede-executar.json | Criar não publica |
| E2E-02 Submeter | EM_ELABORACAO; Elaborador | Chrome: Submeter para revisão; confirmar; reabrir | EM_REVISAO; autoria/tempo/auditoria | **APROVADO**; POST 302, destino 200, revisão visível e trilha SQL | c1-revisao.png, rede-executar.json, postgresql.json auditoria | Transição persistida |
| E2E-03 Homologar | EM_REVISAO; Homologador | Chrome: trocar identidade; abrir UUID; homologar com fundamento; reabrir | HOMOLOGADA e fundamento/autoria persistidos | **APROVADO**; POST 302, estado e auditoria coerentes | c1-homologada.png, postgresql.json | Publicação ainda necessária |
| E2E-04 Publicar | HOMOLOGADA; Publicador; autoridade vigente | Chrome: escolher autoridade e confirmar; API: repetir ato com mesma chave | PUBLICADA, publicação/versão/auditoria, sem duplicação | **APROVADO**; 302 Web; publicação SQL; replay HTTP 201 mesmo UUID; nova chave 409 | c1-confirmacao.png, c1-resultado.png, integracao-http.json, postgresql.json | Publicação válida materializa |
| E2E-05 Público | Publicação imediata | Chrome portal; GET API; GET PDFs; GET sem sessão | Novas datas, documentos e histórico | **APROVADO**; portal/API concordam; PDFs 200; consulta sem Authorization/Cookie 200 | c1-portal.png, c1-api.json, integracao-http.json, verificacoes.json | Original histórico preservado |
| E2E-06 Vigência | Editais independentes; retificação futura publicada no cenário B | Chrome: imediata, futura, vencida; depois criar/aprovar/publicar outra imediata no edital futuro | Imediata aplica; futura espera; vencida recusa; nova base compatível com vigência escolhida | **REPROVADO** em D: formulário usa base futura; publicação imediata falha 409. A/B/C passaram | c2-resultado.png, c2-portal.png, c3-resultado.png, base-futura.json, base-futura-resultado.png | RET-001 |
| E2E-07 Permissões | Estados adequados e atores sintéticos | HTTP real: permissões, escopo, segregação, autoridade, replay; Chrome URL restrita e POST com CSRF | Recusas no backend e ausência de duplicação | **APROVADO**; 403/404/409/422 e replay 201 conforme caso | integracao-http.json, erro-sem-permissao.png, erro-sem-permissao-post.json, rede-base.json | Autorização validada além de botões |
| E2E-08 Devolver/editar | Retificação EM_REVISAO | Chrome: devolver, procurar edição e retorno pelo edital; HTTP PUT com revisão atual/antiga | Recuperar pendência e corrigir; concorrência recusada | **REPROVADO** na jornada Web: faltam navegação e edição. API 200 e obsoleta 412 | c4-devolvida.png, pendencias-ausentes.png, integracao-http.json | RET-003/004; backend de edição funciona |
| E2E-09 Datas/fuso | Período e sorteio distintos | Chrome altera simultaneamente; comparar corpo POST, comparativo, SQL, API e portal | Mesmos instantes em local/UTC; ocorrência da semente preservada | **APROVADO**; 22:37 -03 = 01:37 UTC dia seguinte; 14:23 -03 =17:23 UTC; sem alteração da ocorrência 5900 | rede-executar.json, verificacoes.json, c1-api.json, postgresql.json, c1-portal.png | Sem defeito de fuso observado |
| E2E-10 Integridade | Atos executados pela aplicação | Consultas SQL reais; confrontar original, versões, responsáveis e repetição | Persistência integral, original preservado, sem duplicação | **APROVADO**; autores/fundamento/trilha/versão registrados; hashes originais iguais nas extrações | postgresql.json, postgresql-final.json, verificacoes.json | SQL usado somente para leitura dos atos |
| E2E-11 Erros | Atores/estados variados | Chrome: vigência, base, permissão e inexistente; HTTP: autoridade, revisão, ausência de efeito, duplicidade e cronograma invertido | Erros claros e publicação inconsistente bloqueada | **REPROVADO**: cronograma invertido publicou 201; demais recusas exercitadas responderam coerentemente | c3-resultado.png, base-futura-resultado.png, erro-inexistente.png, integracao-http.json, integracao-complementar.json, postgresql-final.json | RET-002; sem supressão geral de erros observada |

## Subcasos HTTP

`integracao-http.json`: 28 registros, incluindo PDFs e consultas públicas. O GET anônimo à URL administrativa inexistente seguiu login; não é considerado prova de 404. `integracao-complementar.json`: 10 registros. Seus dois `passed:false` pertencem ao mesmo cenário exploratório de cronograma invertido: criação 201 e publicação 201, diante da expectativa inicial 422; criar rascunho não é, isoladamente, a falha normativa.

HTTP negativos comprovados: publicar como Elaborador 403; homologar como Publicador 403; editar como Homologador 403; atuar fora de escopo 404; publicar sem homologação 409; mesma pessoa nos três atos 403; autoridade inexistente 422; autoridade omitida 422; revisão obsoleta 412; sem alteração efetiva 422; nova publicação de estado final 409. Replay com a mesma chave retorna 201 e o mesmo ato.

## Suíte existente

Com `TEST_DB_ENGINE=postgresql`, role superusuária apenas para o runner e `DB_NAME=auditoria_suite_retificacoes`, foram executados:

- tests/interface/test_retificar.py
- tests/interface/test_devolucao_da_retificacao.py
- tests/interface/test_cancelamento_da_retificacao.py
- tests/authorization/test_retificacoes.py
- tests/contract/test_retificacoes_api.py
- tests/integration/publicacoes/test_retificacoes.py

`pytest.log`: 85 passed, 1 failed em 48,56s; única falha = arquivo de contrato não montado no container. `pytest-contrato-reexecucao.log`: 1 passed em 0,36s depois de disponibilizar as specs. Total distinto: 86 aprovados. São testes automatizados de integração/contrato/interface Django, não E2E de navegador.
