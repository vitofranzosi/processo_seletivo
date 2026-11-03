# Inconsistências — PS-RET-E2E-001

Todos os achados foram observados no ambiente sintético exclusivo. Nenhuma correção executada.

## RET-001 — ALTA — Base futura bloqueia retificação imediata

1. **Descrição:** o formulário de criação usa a consolidação com maior `valid_from`, inclusive futura, embora a publicação imediata confira precondições contra a versão vigente agora.
2. **Reprodução:** publicar retificação do AUD-2 para 30/10/2026 12:00; em 28/10 abrir Retificar novamente; alterar término de 12/11 22:37 para 13/11 22:37; deixar Vigência vazia; criar, submeter, homologar e publicar com autoridade válida.
3. **Esperado:** composição sobre uma base compatível com vigência imediata, ou escolha temporal explícita que permita completar a operação válida.
4. **Observado:** formulário parte da versão `c3986324-4cb3-4099-ab2d-5f232f30e2a3`, vigente apenas em 30/10; chega a HOMOLOGADA, mas a publicação retorna 409: “O conteúdo anterior informado não corresponde ao vigente ... Refaça a Retificação sobre a versão consolidada atual.” Abrir novamente o formulário continua escolhendo a futura.
5. **Evidências:** `base-futura.json`, `base-futura-formulario.png`, `base-futura-comparativo.png`, `base-futura-resultado.png`, `rede-base.json`, `postgresql-final.json`.
6. **Código:** `backend/processo_seletivo/interface/views.py:4145` (`_versao_vigente`, sem filtro temporal); `:4164` (GET usa essa base); `publicacoes/application/retificacoes.py:894` (confere contra `_content_in_force`); `publicacoes/application/selectors.py:28` (consulta pública filtra por instante).
7. **Causa-raiz comprovada:** composição e publicação escolhem bases temporais diferentes; o hash do valor futuro não corresponde ao valor atual.
8. **Impacto:** bloqueia a conclusão Web de uma alteração imediata válida num edital com ato futuro já publicado; o usuário pode acumular retificação aprovada sem efeito.
9. **Recomendação:** definir base e vigência de forma coerente na composição; manter conferência de todas as fronteiras futuras para evitar invalidar ato agendado.
10. **Camada:** backend de composição e interface; não requer reescrever publicações nem dados históricos. Decisão temporal deve constar da especificação.

## RET-002 — ALTA — Publicação de intervalo impossível

1. **Descrição:** retificação pode publicar um término de inscrições anterior ao início.
2. **Reprodução:** sobre o AUD-1 publicado, criar pela API uma retificação que troca somente `schedule/.../endAt` para `2020-01-01T12:00:00-03:00`, mantendo `startAt=2026-10-27T12:45:38.120272+00:00`; submeter, homologar e publicar por atores distintos com autoridade válida.
3. **Esperado:** erro impeditivo na publicação de intervalo invertido, conforme FR-017 de `specs/001-processo-seletivo-editais/spec.md:303`.
4. **Observado:** criação 201; submissão/homologação 200; publicação **201**, publicação `31b0fb9d-3018-453b-a196-46d3dfe6b2c1`, estado PUBLICADA e versão consolidada com esse intervalo. Portal anônimo continua respondendo 200 e consome o conteúdo publicado. Não houve SQL para produzir o estado.
5. **Evidências:** `integracao-complementar.json`, `postgresql-final.json`, `anonimo-c1.html`. Este cenário ocorreu depois da captura válida `c1-portal.png`; as duas evidências representam momentos diferentes, não resultados conflitantes.
6. **Código:** `backend/processo_seletivo/editais/domain/validation.py:19` registra expressamente que coerência `endAt`/`startAt` não é validada como regra normativa; `publicacoes/application/retificacoes.py:691` usa essa validação; `:810` valida antes de materializar, mas não recusa a inversão.
7. **Causa-raiz:** lacuna da regra entre campos na validação usada pela publicação. Há **conflito de artefatos**: FR-017 exige rejeitar a inversão e o comentário da implementação diz que a decisão normativa não foi tomada. A auditoria registra a divergência; não resolve governança.
8. **Impacto:** publica calendário impossível e altera o comportamento de disponibilidade de inscrições com informação inconsistente.
9. **Recomendação:** reconciliar especificação, decisões posteriores e contrato; aplicar a garantia normativa vigente na publicação e cobrir as fronteiras consolidadas com teste de regressão.
10. **Camada:** backend/validação e artefatos normativos; preservação do histórico publicado. Sem alteração de banco proposta para apagar ou corrigir o ato.

Não se classifica a criação de um rascunho inválido isoladamente como defeito: a constatação decisiva é a publicação bem-sucedida. Também não se classifica qualquer data passada como proibida: o teste demonstra especificamente término anterior ao início.

## RET-003 — MÉDIA — Pendências ausentes da navegação

1. **Descrição:** retificações ainda não publicadas têm detalhe acessível por UUID, mas não aparecem no detalhe do edital nem em lista de pendências.
2. **Reprodução:** criar/submeter uma retificação ou devolver para elaboração; sair do detalhe e retornar ao edital pelo caminho da interface; procurar a retificação pendente.
3. **Esperado:** reencontrar a pendência e acessar seus próximos atos pela navegação normal.
4. **Observado:** em AUD-2, a retificação imediata bloqueada não aparece; “Documentos publicados” lista apenas original e retificação futura já publicada. O endereço guardado continua funcionando.
5. **Evidências:** `pendencias-ausentes.png`, `pendencias-ausentes.txt`, `base-futura-url.txt`, `c4-devolvida.png`.
6. **Código:** `backend/processo_seletivo/interface/views.py:3718` percorre publicações; `:3758` entrega somente esses documentos; `interface/templates/interface/detalhe.html:132` desenha a seção; rotas de detalhe/ato existem em `interface/urls.py:169`.
7. **Causa-raiz:** consulta e apresentação restritas a atos já publicados, sem lista dos objetos Retificacao pendentes.
8. **Impacto:** dificuldade para reencontrar e encaminhar aprovação/publicação entre perfis; possível abandono do fluxo após salvar.
9. **Recomendação:** seção de retificações de todos os estados, com links e próxima etapa adequada ao ator.
10. **Camada:** interface e consulta de leitura; sem concessão de novas permissões.

## RET-004 — ALTA — Devolução sem edição Web

1. **Descrição:** retificação devolvida fica editável no domínio, mas não tem formulário de edição no navegador.
2. **Reprodução:** AUD-4: criar, submeter, entrar como Homologador, Devolver para elaboração com motivo; abrir o mesmo UUID como Elaborador e procurar Editar.
3. **Esperado:** corrigir o mesmo rascunho devolvido e reenviá-lo pelo canal Web.
4. **Observado:** detalhe não oferece edição; criar novamente pela ação Retificar cria outro objeto. A API do mesmo rascunho retorna 200 com If-Match atual e 412 com revisão antiga.
5. **Evidências:** `c4-devolvida.png`, `c4-devolvida.txt`, `integracao-http.json` (`editar-valido`, `editar-obsoleto`). Depois da prova de edição, o mesmo rascunho foi novamente submetido/homologado e publicado por HTTP para testar segregação/idempotência.
6. **Código:** `backend/processo_seletivo/interface/templates/interface/retificacao_detalhe.html:19` lista apenas atos; `interface/atos_retificacao.py:46` não contém edição; `publicacoes/api/views.py:178` implementa `EditRetificationView`; `publicacoes/application/retificacoes.py:425` aceita edição em elaboração.
7. **Causa-raiz:** edição existe no domínio/API sem correspondência Web.
8. **Impacto:** impede a recuperação normal do fluxo devolvido para quem opera exclusivamente pelo navegador.
9. **Recomendação:** formulário Web de edição em elaboração e devolução, com precondição de revisão e mesmas permissões existentes.
10. **Camada:** frontend/view Web, reutilizando domínio e API; nenhuma alteração de permissões reais necessária.

## Comportamentos esperados e hipóteses

- Rascunho salvo não altera versão pública: comprovado, esperado.
- Homologação sem publicação não altera versão pública: comprovado, esperado.
- Publicada com vigência futura mantém versão anterior até a vigência: comprovado, esperado.
- Vigência vencida bloqueia com erro claro: comprovado, esperado.
- Original/PDF histórico não é sobrescrito: esperado, não defeito.
- Falta de permissão, escopo ou autoridade bloqueia: comprovado.
- Perda silenciosa de persistência ou erro geral de fuso: não encontrados nos cenários válidos.
- Qual dessas causas explica o caso real do usuário: não determinado sem identificar o registro/ambiente real.
