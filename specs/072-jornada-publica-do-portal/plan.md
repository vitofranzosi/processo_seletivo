# Implementation Plan: A jornada pública do portal

**Branch**: `claude/072-jornada-publica` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: a spec da 072, com as decisões Q1 a Q9 e a clarificação de 12/10 sobre o resumo de prazos.

## Summary

Mudança de **apresentação e de leitura**, sem domínio novo: a vitrine passa a titular o cartão pelo
Edital, dizer a oferta por Perfil e o lugar, recolher filtros no celular e resumir resultados e
prazos de recurso; a página da seleção ganha o resumo da oferta com atalho para as vagas e o anúncio
do Requerimento; as telas de acesso passam a nomear a vaga do destino, e a volta à vaga explica a
confirmação que continua sendo exigida. O resumo de resultados reaproveita a leitura e a regra de
prazo que a página da seleção já usa, feitas para vários Editais de uma vez (research, T-001).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2 (templates do portal, CSS inline em `portal/base.html`)

**Primary Dependencies**: nenhuma nova

**Storage**: PostgreSQL — nenhuma migration, nenhuma tabela, nenhum campo

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg` com `DB_NAME` exclusivo)

**Target Platform**: o portal público, servido pelo mesmo monólito

**Project Type**: aplicação web (monólito Django, páginas renderizadas no servidor)

**Performance Goals**: vitrine sem consulta por cartão; hoje 2 consultas, previstas até 6, constantes
no número de cartões (T-001). Página da seleção: as mesmas 8–10 de hoje — a mensagem de volta vem da
sessão, que já é carregada, e nenhuma consulta nova é esperada. Telas de acesso: + 1 leitura da
versão vigente, só quando há destino de vaga (T-004).

**Constraints**: sem script para a consulta funcionar; sem rolagem lateral de 320 a 1.440 px; resposta
equivalente no acesso; nenhum GET abre inscrição; nenhum dado de navegação registrado.

**Scale/Scope**: dezenas de seleções simultâneas (premissa da `024`); 8 templates do portal, a folha
(`base.html`), 2 módulos Python e 1 selector alterados; 1 script estático novo, de poucas linhas.

## Constitution Check

| Princípio | Como a 072 o atende | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Vaga" mantida (Q6), com denominação e quantidade separadas; nenhum termo novo de domínio | ✅ |
| II. Integridade normativa | Tudo lido da versão vigente; o momento do Requerimento vem do conteúdo publicado; nenhum dado publicado é alterado | ✅ |
| III. Segurança e LGPD | Nenhum dado novo coletado nem registrado (FR-1637); destino continua validado como hoje; equivalência de acesso preservada (FR-1620); resposta privada quando a página mostra o e-mail (T-003); finalidade de nome e CPF dita na coleta (FR-1627, a validar) | ✅, com a validação de texto pendente |
| IV. Regras no backend | Abrir rascunho continua sendo POST verificado no servidor; o script novo só abre um `<details>` | ✅ |
| V. Simplicidade e rastreabilidade | Reuso das leituras existentes (T-001, T-005); nenhuma dependência, cache ou persistência; matriz de rastreabilidade na fase de tarefas | ✅ |
| VI. Completude de jornada | Cenários demonstráveis para visitante novo (identidade nova pelos formulários), recorrente e participante; quickstart | ✅ |
| Fluxo | Spec → clarificação → **este plano, para aprovação** → tarefas → análise → implementação → convergência | aguardando aprovação |

Nenhuma violação a justificar; a seção *Complexity Tracking* fica vazia.

## Project Structure

### Documentation (this feature)

```text
specs/072-jornada-publica-do-portal/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # T-001 a T-009 e a linha de base de consultas
├── data-model.md        # só estruturas de leitura e uma chave de sessão
├── contracts/telas-publicas.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md             # fase seguinte
```

### Source Code — arquivos afetados

| Arquivo | Mudança | Requisitos |
|---|---|---|
| `backend/processo_seletivo/divulgacao/application/selectors.py` | `historico_publico_dos_editais(editais)`; a função de um Edital passa a delegar | FR-1635 |
| `backend/processo_seletivo/portal/leitura.py` | extraído de `views.selecao`: resultados vigentes com `recurso_ate`; novos: resumo do acompanhamento (D-004), `quantidade_da_oferta`, lista com teto e busca primeiro, lugares, busca alcançando lugares, `open` dos filtros | FR-1600, FR-1601, FR-1607 a FR-1610, FR-1629 a FR-1636 |
| `backend/processo_seletivo/portal/views.py` | `vitrine` e `_selecao_da_vitrine`: leitura em lote, sigla da unidade, oferta, lugares, resumo, contagem de abertas; `selecao`: chama a função extraída, resumo da oferta, Requerimento, volta condicional, mensagem de volta e resposta privada; `_vaga_do_destino`; `acesso`, `acesso_codigo`, `acesso_reconciliar`, `meus_dados`, `_entrar`: contexto e chave de volta | FR-1604 a FR-1606, FR-1611, FR-1612, FR-1615 a FR-1627 |
| `backend/processo_seletivo/portal/templates/portal/vitrine.html` | título, contagem de abertas, subtítulo, estado vazio | FR-1611 a FR-1613 |
| `.../portal/_consulta.html` | busca e botão fora; `<details class="mais-filtros">` com os quatro controles; `<script>` síncrono | FR-1600 a FR-1603 |
| `.../portal/_cartao_da_selecao.html` | nova ordem: título do Edital, oferta, lugares, período, acompanhamento, convite, dados de apoio | FR-1604 a FR-1609, FR-1614, FR-1629 a FR-1634 |
| `.../portal/selecao.html` | volta condicional, resumo da oferta, frase do Requerimento, mensagem de volta no Perfil | FR-1615 a FR-1618, FR-1622, FR-1626 |
| `.../portal/acesso_email.html`, `acesso_codigo.html`, `acesso_reconciliar.html`, `meus_dados.html` | contexto da vaga; título do acesso; ajuda de spam; finalidade | FR-1619, FR-1621, FR-1627 |
| `.../portal/base.html` | regras: `.mais-filtros`, oferta e lugares do cartão, acompanhamento, dados de apoio, resumo da oferta, `.perfil:target`, mensagem de volta | FR-1614, FR-1617, FR-1639 |
| `backend/processo_seletivo/portal/static/portal/consulta.js` | **novo**, ~10 linhas: abre o grupo em tela larga e acompanha a mudança de largura | FR-1602 |

### Testes

| Arquivo | O que prova |
|---|---|
| `tests/portal/test_resumo_do_acompanhamento.py` (**novo**, sem banco) | D-004: 1 vigente; vários com prazos iguais, parciais, diferentes, encerrados; natureza mista; vazio |
| `tests/portal/test_acompanhamento_na_vitrine.py` (**novo**, com banco) | cartão × página no mesmo instante; sucedida fora; encerrado some; sem resultado nada; **orçamento: 1 e 3 Editais com resultado, mesmo número de consultas** — reaproveita `montar` e `consultas` de `test_prazo_recursal_publico.py` |
| `tests/integration/portal/test_vitrine.py`, `test_consulta_da_vitrine.py` | título e aba, contagem de abertas, título do cartão, oferta por Perfil e teto, lugares, número não repetido, sigla, `open` dos filtros, busca por lugar com o casado primeiro, estado vazio |
| `tests/integration/portal/test_detalhe_selecao.py` | volta condicional, resumo da oferta com âncoras, Requerimento presente/ausente/na convocação, POST preservado |
| `tests/acceptance/portal/test_jornada_publica.py` (**novo**) | SC-603: identidade **nova** pelos formulários até o rascunho; recorrente; com sessão; mensagem uma vez; nenhum rascunho antes da confirmação; destino colado por terceiro |
| `tests/integration/portal/test_contexto_do_acesso.py` (**novo**) | contexto com destino de vaga; nada com destino inválido, externo ou de outro Edital; corpo idêntico exista ou não identidade (FR-1620); resposta privada com mensagem |
| `tests/interface/test_acessibilidade_do_portal.py` | consulta sem `hx-`/`onclick`, rótulos ligados, `summary` presente; mensagem com `role="status"` |
| `tests/portal/test_vocabulario_das_telas_publicas.py` (**novo**) | T-008: `PROIBIDAS` sobre o texto visível das telas alteradas |
| ajustes de texto | `test_detalhe_selecao.py` ("Voltar aos resultados"), `test_atos_que_respondem.py` ("Seus dados foram guardados"), `test_entrar_sem_senha.py` e `test_mudanca_de_credencial.py` ("Sem senha") — cada um conferido contra a decisão que o originou |

**Structure Decision**: o monólito existente; nenhum módulo novo além do script estático.

## Riscos concretos

| Risco | Tratamento |
|---|---|
| A extração do cálculo de prazo mudar a página da seleção | A página passa a chamar a função extraída; os testes da 047 e da 062 (`test_prazo_recursal_publico.py`, `test_resultados_por_perfil.py`, `test_historico_publico.py`) continuam verdes sem alteração |
| N+1 na vitrine | Leitura em lote (T-001) e teste de orçamento com 1 e 4 Editais |
| Cache compartilhado guardar a página com o e-mail | Resposta privada sempre que a mensagem de volta é renderizada (T-003), com teste |
| O contexto do acesso revelar existência de identidade | Derivado só do destino (T-004); teste compara o corpo com e sem identidade |
| Desktop sem script ver os filtros recolhidos | Degradação aceita e registrada (T-002): funcional, com o `summary` à vista |
| Testes de varredura do repositório (classe sem regra, `}}` em CSS, vocabulário na prosa da folha) | Cada classe nova com regra em `base.html`; CSS em linhas separadas; comentários sem o vocabulário proibido |
| Busca que casa com Perfil fora do teto | Os que casam vêm primeiro (FR-1610) |
| Seed sem cenário de vários resultados | Os casos de 3 e 5 vigentes são montados nos testes, não no seed |

## Como cada jornada será verificada

Detalhado no [quickstart](quickstart.md). Em resumo: **encontrar** pelo script de medição da auditoria
nas telas do SC-600 e por integração; **começar** por um teste de aceitação com identidade nova
atravessando os formulários, e no navegador com o CPF digitado por uma pessoa; **preparar** por
integração e no Edital 01/2026 do seed; **acompanhar** por testes de cenário (1, 3 e 5 vigentes) e no
Edital 51/2026; **sem script** em `iframe` sem permissão de script; **larguras** pelo mesmo script.
Verificação canônica: `make lint check test-pg` com `DB_NAME` exclusivo, `migrate --check` antes.

## Necessidade de ampliar escopo

**Nenhuma.** Dois ajustes na spec, ambos dentro do escopo aprovado e já registrados nela:

- FR-1610: com busca ativa, o que casa com o termo vem primeiro, para o teto de três não esconder o
  motivo do resultado;
- a exclusão do cartão compacto de encerradas, por contrariar a UX-016 da `024`.

E um achado lateral registrado (research): a vitrine não tinha teste de orçamento de consultas — a 072
acrescenta um porque passa a ler resultados.

## Complexity Tracking

Vazio — nenhuma violação da Constituição.
