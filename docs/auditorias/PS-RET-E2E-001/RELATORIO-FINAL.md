# PS-RET-E2E-001 — Relatório final

Data: 28/10/2026, America/Sao_Paulo. Nenhuma correção implementada.

## A — Identificação e baseline

- Repositório: `D:\projetos\cefor\processo_seletivo`; backend: `backend/`.
- Branch: `002-inserir-documentacao-sistema`.
- HEAD: `42871b4243cdb5f00b0a560d6323281df8590087`.
- Estado inicial: somente `?? docs/sorteio/`; preservado. Os arquivos desta auditoria são novos.
- Instruções: `AGENTS.md` e Constituição `.specify/memory/constitution.md`.
- Host: Windows, PowerShell, Python local 3.13.15, Node 24.13.1, cliente psql 17.7.
- Execução Django: container exclusivo `ps-ret-e2e-001-app`, Python 3.13.16, Django 5.2.17, pytest 8.4.2.
- Navegador: Chrome 155.0.8059.80 headless real, automatizado por Chrome DevTools Protocol via WebSocket do Node. Playwright não instalado no container; nenhuma dependência instalada.
- Servidor auditado: `http://127.0.0.1:8017`; container trabalha com fonte do backend montada somente para leitura.
- Banco: PostgreSQL 18.6, `ps-ret-e2e-001-db:5432`, database `auditoria_retificacoes`; rede Docker exclusiva `ps-ret-e2e-001`.
- Container PostgreSQL: `0f41ca18ac5392de4ee9b768ba4a0332ff6fe1a9a80ddfd68415b3cb2b5c6561`. Novo volume anônimo `bbd3c31a0d9da1c48a24e679e0b349a7fe95acc7faeaa1f801deeb28512d8c77`; nenhum volume anterior reutilizado.
- Antes de migrations/escritas: consulta confirmou database/usuário/versão e **zero tabelas públicas**. Instância criada nesta execução com imagem já disponível, sem dados reais e sem porta PostgreSQL publicada no host.
- Preparação: provisionamento → migrations pela role migration → provisionamento; proteção confirmada em **41 de 41** tabelas. Servidor usa `auditoria_runtime`, sem UPDATE/DELETE nas tabelas append-only.
- Suite existente: banco próprio `test_auditoria_suite_retificacoes` no mesmo cluster descartável, separado dos cenários do navegador.
- A aplicação já existente na porta 8000 e os bancos/containers preexistentes não receberam escritas da auditoria.

## B — Resumo executivo

**CONCLUÍDA no ambiente sintético, com reprovações funcionais.** Nos 11 grupos solicitados: **8 APROVADOS, 3 REPROVADOS, 0 BLOQUEADOS e 0 NÃO EXECUTADOS**. Os grupos combinam navegador real, integração HTTP e SQL, identificados na matriz; não representam 11 testes exclusivamente de navegador.

O fluxo principal foi executado no Chrome: criar, submeter, homologar e publicar. A publicação imediata alterou corretamente as datas no portal e na API. Não foi encontrado defeito de persistência/materialização nesse cenário válido.

Foram confirmados quatro achados: base futura inadequada para publicação imediata; publicação de cronograma invertido; ausência de navegação para pendências; ausência de edição Web de rascunho devolvido.

Suíte existente selecionada: **86 casos distintos aprovados**. A primeira rodada teve 85 aprovações e uma falha por falta de `/app/specs/.../openapi.yaml` no container da auditoria. Após copiar as specs para o container descartável, somente esse teste foi repetido e passou. Não se apresenta isso como execução da suíte completa.

## C — Reprodução do problema original

**Reproduzido o sintoma em cenários controlados, sem atribuir uma causa ao edital real não fornecido.**

1. Após criar o rascunho, as novas datas ficam registradas na retificação e o público continua vendo as antigas. Isso é comportamento esperado: ainda não existe publicação.
2. Após publicação com vigência em **30/10/2026 12:00 -03:00**, o estado é PUBLICADA, mas o portal de 28/10 ainda mostra as datas antigas. Também esperado.
3. Uma segunda retificação imediata sobre esse edital futuro é criada e homologada, mas não publica: o formulário escolhe a base futura e a publicação acusa conflito com o conteúdo vigente. **Defeito funcional reproduzido, com erro explícito.**
4. No cenário imediato válido, as datas novas aparecem após a publicação. Não se reproduziu um salvamento/publicação válida silenciosamente perdido.

O diagnóstico operacional mais direto é distinguir salvar rascunho, aprovar, publicar e alcançar a vigência. Para identificar qual desses casos ocorreu com o usuário original ainda são necessários o UUID/estado da retificação e o ambiente correspondente; nenhum edital real foi consultado ou alterado.

## D — Fluxo de retificação

Operação real observada:

1. Entrar como Elaborador pelo seletor de demonstração, com identidade sintética.
2. `Processos Seletivos` → Processo sintético → Edital publicado → `Retificar`.
3. Alterar `Término` do evento Inscrições e `Início` do evento Sorteio programado sintético; preencher `Justificativa`.
4. `Ver o que vai mudar` → conferir duas alterações → `Criar Retificação`.
5. Guardar `/gestao/retificacoes/{R}/`: falta listagem de pendências para reencontrá-la.
6. `O que fazer agora` → `Submeter para revisão` → `Confirmar: Submeter para revisão`.
7. Homologador abre o mesmo endereço → `Homologar` → `Fundamento da homologação` → `Confirmar: Homologar`.
8. Publicador abre o mesmo endereço → `Publicar Retificação` → escolhe Autoridade Signatária → `Confirmar: Publicar Retificação`.
9. Conferir estado PUBLICADA, publicação e vigência; depois consultar `/selecoes/{E}/` e `/api/v1/public/editais/{E}/versao-vigente`.

Estados comprovados pelo conjunto de tela, requisições, SQL e trilha: EM_ELABORACAO → EM_REVISAO → HOMOLOGADA → PUBLICADA. Devolução: EM_REVISAO → EM_ELABORACAO, seguida de edição pela API. Os POSTs Web bem-sucedidos responderam 302; o destino respondeu 200. Publicação com vigência vencida: 422. Publicação sobre base futura incompatível: 409.

Views: `retificar`, `retificacao_detalhe`, `praticar_ato_retificacao`, em `backend/processo_seletivo/interface/views.py:4176`, `:4402`, `:4673`. Templates: `retificar.html`, `retificacao_detalhe.html`, `retificacao_confirmar.html`. Rotas em `interface/urls.py:122` e `:169`.

## E — Perfis e permissões

O seletor da aplicação concede papéis às identidades da sessão; não foram criadas contas institucionais reais nem alteradas permissões preexistentes. Nos testes HTTP negativos foi usado o adaptador Bearer de desenvolvimento da própria aplicação.

| Cenário executado | Resposta | Resultado |
|---|---:|---|
| Elaborador publica sem permissão | 403 | Bloqueado no backend; também POST Web com sessão Elaborador retornou 403 |
| Publicador homologa sem permissão | 403 | Bloqueado |
| Homologador edita rascunho | 403 | Bloqueado |
| Ator de outra unidade submete a retificação | 404 | Escopo protegido |
| Publicador publica antes da homologação | 409 | Estado protegido |
| Mesmo subject submete, homologa e publica | 403 | `segregation_of_duties` |
| Autoridade inexistente em retificação homologada sem vigência vencida | 422 | `autoridade_indisponivel` |
| Autoridade omitida na API | 422 | Payload recusado |
| Repetição da mesma publicação e chave | 201/201, mesmo UUID | Sem segundo ato |
| Nova tentativa de publicar estado PUBLICADA com chave nova | 409 | Sem segundo ato |

Permissões positivas: Elaborador = `retificacao:elaborar` e `retificacao:submeter`; Homologador = `retificacao:homologar`; Publicador = `retificacao:publicar`. Todos os atos positivos foram no escopo `cefor`.

A segregação exige impedir a concentração de três atos no mesmo subject; não obriga três pessoas distintas. A identidade de preparação usada nessa regra é a de submissão (`prepared_by`). Autoridade Signatária é registro institucional selecionado e não substitui a permissão do operador.

## F — Datas, horários e vigência

`USE_TZ=True`; `TIME_ZONE=America/Sao_Paulo`.

| Informação | Formulário/requisição local | Alteração persistida e versão consolidada UTC | Apresentação pública |
|---|---|---|---|
| Encerramento novo | `2026-11-12T22:37` | `2026-11-13T01:37:00+00:00` | `12/11/2026 às 22h37` |
| Sorteio programado novo | `2026-11-14T14:23` | `2026-11-14T17:23:00+00:00` | `14/11/2026` no cronograma; a tela pública resume este evento por data |
| Vigência futura | `2026-10-30T12:00` | `2026-10-30T15:00:00+00:00` | `Passa a vigorar em 30/10/2026 12:00` |

Não houve desvio de fuso no cenário executado. O recebimento pelo backend é comprovado pela resposta/comparativo e pelos valores persistidos; não foi adicionada instrumentação ao servidor.

O método do marco manteve ocorrência `5900` e `occurrenceAt=2020-01-01T20:00:00-03:00` (normalizado em UTC no conteúdo). Essa ocorrência da fonte é distinta do evento SORTEIO do cronograma; não foi alterada pelo teste de remarcação.

Vigência imediata passou; futura publicou preservando a versão atual; vencida foi recusada; base futura foi reprovada com impacto real. Não se avançou relógio nem alterou SQL para simular passagem do tempo.

## G — PostgreSQL

`postgresql.json` contém SQL de leitura e seus resultados após os primeiros cenários: 4 retificações, 8 alterações normativas, 7 publicações, 7 versões consolidadas e 46 eventos de auditoria. O caso devolvido foi editado e publicado pela API depois da captura da devolução.

`postgresql-final.json` contém o estado após os testes adicionais: 6 retificações, 10 alterações, 8 publicações, 8 versões e 53 eventos de auditoria. Os dois casos adicionais são a base futura bloqueada (HOMOLOGADA, sem publicação) e o cronograma invertido publicado.

As consultas registram autores, horários, justificativas, fundamento de homologação, revisões, base, publicação e vigência. A conferência dos registros de publicação original entre as duas extrações preservou todos os campos consultados e os hashes. Os documentos publicados responderam 200 com bytes PDF e hashes registrados em `integracao-http.json`.

A repetição idempotente devolveu exatamente o mesmo UUID de publicação, sem duplicar publicação/versão/ato. A role runtime não tem UPDATE/DELETE em Publicacao, VersaoConsolidada e RegistroAuditoria; a segunda passada de provisionamento confirmou o conjunto completo de 41 tabelas.

## H — Interface Web

Os botões existem e funcionaram nas etapas adequadas. Os comparativos exibiram as duas alterações e as telas apresentaram erros de vigência e base incompatível. A URL de publicação aberta por Elaborador explica a falta de permissão e não oferece confirmação; POST direto com CSRF válido foi recusado com 403.

Confirmadas lacunas de navegação e edição: ao voltar ao edital não há link para retificações não publicadas; após devolver não existe opção Editar. A API `PUT /api/v1/admin/retificacoes/{R}/rascunho` editou com If-Match válido (200) e recusou revisão antiga (412).

## I — Portal público

O portal real mostrou as novas datas no cenário imediato, o alerta de retificação e os documentos anteriores preservados. O nome da seção pública é **Edital e documentos**; **Documentos publicados** é a seção da gestão. PDFs da publicação original e da retificação foram acessados por HTTP real.

Foram repetidas consultas sem Authorization e sem Cookie, todas com 200. A API vigente e o portal concordaram: data nova no cenário imediato; data anterior no futuro; data anterior quando a publicação foi recusada. O documento original permanece histórico e não deve ser usado para decidir se a versão vigente foi atualizada.

## J — Inconsistências

Detalhes, reprodução e referências em [INCONSISTENCIAS.md](INCONSISTENCIAS.md):

| ID | Gravidade | Achado |
|---|---|---|
| RET-001 | ALTA | Base futura torna inviável a nova publicação imediata pela jornada Web testada |
| RET-002 | ALTA | Término anterior ao início foi publicado e materializado; divergência com FR-017 da 001 |
| RET-003 | MÉDIA | Retificações pendentes não são alcançáveis pela navegação do edital |
| RET-004 | ALTA | Retificação devolvida não pode ser corrigida pela interface Web, embora a API permita |

Nenhum achado foi corrigido. O calendário invertido não explica, por si, o relato de datas novas ausentes; é outro defeito exposto pela auditoria autorizada.

## K — Limitações

- Nenhum UUID ou ambiente do caso real foi fornecido; não se identifica qual causa ocorreu naquela sessão.
- Os cenários usam seletor de identidade e Bearer de desenvolvimento, não autenticação de produção.
- O instante futuro de 30/10 não foi aguardado. Foram comprovadas publicação futura, materialização da fronteira e manutenção da versão atual; não se afirma observação de virada futura em tempo real.
- Alguns cenários negativos são integração HTTP, não navegação por cliques. Não são apresentados como E2E de navegador.
- O GET anônimo chamado `inexistente` em `integracao-http.json` seguiu o redirecionamento para login e devolveu 200; **esse registro não comprova 404 do recurso**. A verificação autenticada no Chrome e a API pública inexistente retornaram 404.
- O primeiro teste de autoridade inválida no caso vencido encontrou primeiro `invalid_effective_at`; a autoridade foi depois testada separadamente no caso homologado sem esse impedimento.
- O rascunho de cronograma invertido foi admitido com 201; a reprovação de integridade se fundamenta na publicação 201 e materialização, não somente na admissão de rascunho.
- Não foram feitas indisponibilização de serviços, testes de carga nem execução da suíte inteira.
- Os dados sintéticos e containers são preservados, parados ao final para não manter serviços de auditoria ativos.

## L — Recomendações

1. Reconciliar a validação de cronograma da publicação de retificações com FR-017 e os artefatos posteriores; impedir publicação de intervalos impossíveis conforme decisão normativa vigente.
2. Fazer a composição explicitar a base temporal e permitir retificação imediata quando há atos futuros, preservando a validação das fronteiras futuras.
3. Disponibilizar edição de rascunho/devolvida no canal Web com controle de revisão e autorização existentes.
4. Listar as retificações de todos os estados no edital, com próxima etapa, responsável e vigência.
5. Incorporar regressões dos casos RET-001 e RET-002 e um teste de navegador da jornada com troca de atores e retorno pelo menu.

## M — Próxima etapa

Propor incremento de especificação para base temporal, edição e navegação; registrar a divergência de cronograma para decisão de governança. Depois de autorizada a implementação, usar os cenários e evidências desta auditoria como critérios de aceitação. Nenhuma implementação corretiva foi iniciada.

**Resposta operacional:** Publicador abre o detalhe da retificação HOMOLOGADA, clica Publicar Retificação, escolhe a Autoridade Signatária e confirma. Salvar um rascunho não altera o edital público; publicação com vigência futura também não muda o conteúdo atual antes do prazo. Os testes válidos confirmaram essa distinção e a atualização correta após publicação imediata.
