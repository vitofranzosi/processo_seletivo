# Rastreabilidade — 024 Descoberta e Transparência no Portal Público

Cada identificador definido em [spec.md](spec.md), com onde ele foi implementado e onde é
verificado. O teste `tests/test_citacoes_de_requisito.py` cobra esta matriz inteira e **não** aceita
intervalo cobrindo sufixo de letra — `FR-131a`, `FR-140a` e `FR-146a` aparecem citados um a um.

Caminhos relativos a `backend/`.

## Requisitos funcionais

### Cronograma público

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-125** | `processo_seletivo/portal/leitura.py` (`cronograma`), `portal/views.py` (`selecao`), `templates/portal/selecao.html` | `tests/integration/portal/test_cronograma_publico.py` |
| **FR-126** | `portal/leitura.py` (`cronograma`), `templates/portal/_cronograma.html` | `tests/integration/portal/test_cronograma_publico.py` |
| **FR-127** | `portal/leitura.py` (`cronograma`), `templates/portal/_cronograma.html` | `tests/integration/portal/test_cronograma_publico.py` |
| **FR-128** | `templates/portal/selecao.html` (a seção inteira sob condição) | `tests/integration/portal/test_cronograma_publico.py` |

### Histórico normativo

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-129** | `publicacoes/application/selectors.py` (`atos_publicados`), `portal/leitura.py` | `tests/integration/portal/test_historico_publico.py` |
| **FR-130** | `publicacoes/domain/alteracoes.py`, `templates/portal/_documentos_do_edital.html` | `tests/unit/publicacoes/test_alteracoes_legiveis.py`, `tests/integration/portal/test_historico_publico.py` |
| **FR-131** | `portal/views.py` (a página lê a versão vigente) | `tests/integration/portal/test_historico_publico.py` |
| **FR-131a** | `templates/portal/selecao.html` (aviso sob `houve_retificacao`) | `tests/integration/portal/test_historico_publico.py` |
| **FR-132** | `templates/portal/_documentos_do_edital.html` | `tests/integration/portal/test_historico_publico.py` |
| **FR-133** | `templates/portal/selecao.html` (seção sob `houve_retificacao`) | `tests/integration/portal/test_historico_publico.py` |

### A vaga

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-134** | `portal/views.py` (`_perfil`), `templates/portal/selecao.html` | `tests/integration/portal/test_detalhe_selecao.py` |
| **FR-135** | `portal/views.py` (`_perfil`), `templates/portal/selecao.html` | `tests/integration/portal/test_detalhe_selecao.py` |
| **FR-136** | `portal/views.py` (`_oferta`), `templates/portal/selecao.html` | `tests/integration/portal/test_detalhe_selecao.py` |
| **FR-137** | `templates/portal/selecao.html` | `tests/integration/portal/test_detalhe_selecao.py` |

### Descoberta na vitrine

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-138** | `portal/leitura.py` (`filtrar`, `_texto_do_cartao`), `shared/texto.py` | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-139** | `portal/leitura.py` (`filtrar`), `templates/portal/_consulta.html` | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-140** | `portal/leitura.py` (`filtrar`, ordem `recentes`), `portal/views.py` (`_selecao_da_vitrine`) | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-140a** | `portal/views.py` (`vitrine`), `portal/leitura.py` (`consulta_da_vitrine`) | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-141** | `portal/views.py` (`total_encontrado`), `templates/portal/vitrine.html`, `_consulta.html` | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-142** | `templates/portal/vitrine.html` (estado vazio) | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-143** | `portal/leitura.py` (`consulta_da_vitrine`, `querystring`) | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-144** | `portal/leitura.py` (`caminho_de_volta`), `templates/portal/_cartao_da_selecao.html`, `selecao.html` | `tests/integration/portal/test_detalhe_selecao.py`, `test_consulta_da_vitrine.py` |

### Situação na vitrine

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-145** | `portal/leitura.py` (`SITUACAO_DO_CARTAO`), `templates/portal/_cartao_da_selecao.html` | `tests/integration/portal/test_vitrine.py` |
| **FR-146** | `portal/leitura.py` (`agrupar_por_situacao`), `templates/portal/vitrine.html` | `tests/integration/portal/test_vitrine.py` |
| **FR-146a** | `portal/views.py` (`grupos` vazio com consulta ativa), `templates/portal/vitrine.html` | `tests/integration/portal/test_consulta_da_vitrine.py` |
| **FR-147** | `templates/portal/_periodo.html` (já existente), `portal/views.py` (`dias_restantes`) | `tests/integration/portal/test_vitrine.py` |
| **FR-148** | `templates/portal/_cartao_da_selecao.html` | `tests/integration/portal/test_vitrine.py` |
| **FR-149** | `portal/leitura.py` (`SITUACAO_DO_CARTAO`, `GRUPOS`), `_periodo.html` | `tests/integration/portal/test_vitrine.py` |

### Alcance

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-150** | as duas views, sem decorador de privacidade sobre o caminho anônimo | `tests/integration/portal/test_cronograma_publico.py`, `test_leitura_sem_escrita.py` |
| **FR-151** | ausência de escrita nas duas views — nada a implementar, tudo a impedir | `tests/integration/portal/test_leitura_sem_escrita.py` |
| **FR-152** | `publicacoes/application/selectors.py` (`selecoes_publicas`, já existente) | `tests/integration/portal/test_vitrine.py` |

## Requisitos de apresentação

| Requisito | Implementação | Verificação |
|---|---|---|
| **UX-016** | `templates/portal/_cartao_da_selecao.html`, `templates/portal/base.html` (`.marca-situacao`) | `tests/integration/portal/test_vitrine.py`, verificação visual do [quickstart](quickstart.md) |
| **UX-017** | `templates/portal/_consulta.html` (`<form method="get">`, sem script) | `tests/interface/test_acessibilidade_do_portal.py` |
| **UX-018** | `templates/portal/base.html` (a folha do portal é escrita para 375 px) | `tests/interface/test_acessibilidade_do_portal.py` (largura fixa), verificação visual |
| **UX-019** | `templates/portal/_cronograma.html` (`aria-current`, "Acontecendo agora"), `base.html` (`.marca-situacao`, `.operacao`) | `tests/interface/test_acessibilidade_do_portal.py` |

## Critérios de sucesso

| Critério | Onde se verifica |
|---|---|
| **SC-040** | `tests/integration/portal/test_cronograma_publico.py`; Roteiro 1 do [quickstart](quickstart.md) |
| **SC-041** | `tests/integration/portal/test_detalhe_selecao.py` (presença e ausência); Roteiro 3 |
| **SC-042** | `tests/integration/portal/test_historico_publico.py`; Roteiro 2 |
| **SC-043** | `tests/integration/portal/test_consulta_da_vitrine.py`; Roteiro 4 |
| **SC-044** | `tests/integration/portal/test_leitura_sem_escrita.py`, `test_cronograma_publico.py`; percurso anônimo inteiro |
| **SC-045** | `tests/integration/portal/test_consulta_da_vitrine.py` (mesma lista noutra sessão) |
| **SC-046** | `tests/integration/portal/test_detalhe_selecao.py` (oferta como leitura principal); Roteiro 3 |
| **SC-047** | `tests/integration/portal/test_leitura_sem_escrita.py` (nenhuma escrita, nenhuma auditoria) |

## Decisões

As nove decisões da §3 da spec não têm linha própria porque não são requisitos: elas explicam
**por que** os requisitos acima têm a forma que têm. Onde uma decisão governa um trecho de código,
ela é citada no comentário daquele trecho — `D-001` em `test_leitura_sem_escrita.py`, `D-002` em
`consulta_da_vitrine`, `D-005` em `publicacoes/domain/alteracoes.py`, `D-007` em `_oferta`,
`D-009` nas três seções que somem quando não há o que dizer.
