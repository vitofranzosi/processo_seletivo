# Verificação: Jornada operacional da Retificação

Medido em 30/10/2026, na branch `claude/silly-cerf-78b884`, sobre a `main` em `0061f28e`.

## Suíte completa (SC-977)

`cd backend && make lint check test-pg`, com `TEST_DB_ENGINE=postgresql`, `DB_USER=$USER`,
`POSTGRES_USER=$USER`, `DB_NAME=ret103_cerf`, o grupo `assistente` instalado e 4 workers
(`--dist worksteal`), sobre o commit `e8da7fc5`:

| Passo | Resultado |
|---|---|
| `ruff check .` | All checks passed |
| `ruff format --check .` | 1643 files already formatted |
| `manage.py check` | no issues |
| `makemigrations --check --dry-run` | sem mudança (o aviso sobre o banco `ret103_cerf` inexistente é do `DB_NAME` de teste; contra `ps_demo_103`: "No changes detected") |
| `pytest` | **13483 passed, 12 skipped**, 0 falhas, 563s |

Os 12 pulados são os 12 deliberados que o `CLAUDE.md` descreve com o grupo `assistente` instalado.
A medição anterior do `CLAUDE.md` (21/10, `e869d7a2`) dava 12775 e 12; a diferença em passados é a
das features `098` a `102` e desta, e o número de pulados não mudou.

Depois do commit medido entrou só `tests/interface/test_jornada_da_retificacao_convergencia.py`
(dois casos, da convergência), conferido no recorte abaixo.

## Recortes

| Recorte | Resultado |
|---|---|
| `-k "retific or Retific or edital or publica"` (Edital, Retificação e publicação), 4 workers | **3456 passed**, 155s |
| `tests/interface/test_auditoria_passagem_da_retificacao.py` | 19 passed, **nenhum `xfail`** (antes: 15 passed, 4 xfailed) |
| `tests/interface/test_jornada_da_retificacao.py` | 25 passed |
| `tests/interface/test_jornada_da_retificacao_convergencia.py` | 2 passed |
| `tests/unit/interface/test_atos_da_retificacao.py` | 22 passed |
| `tests/unit/publicacoes/test_fusao_da_edicao.py` | 12 passed |
| guardiões (citações, portas, vocabulário, acessibilidade, estáticos, folha, CSP) | 1676 passed, 10 skipped |

## Os quatro `xfail` da auditoria (SC-972)

As marcas foram retiradas sem mudar nenhuma asserção dos quatro casos:
`test_quem_homologa_encontra_a_retificacao_em_revisao_sem_conhecer_a_url`,
`test_quem_publica_encontra_a_retificacao_homologada_sem_conhecer_a_url`,
`test_quem_elabora_reencontra_o_proprio_rascunho` e
`test_o_detalhe_nao_oferece_publicar_a_quem_a_segregacao_impede`.

Dois casos do mesmo arquivo descreviam o **defeito** na forma positiva, e foram reescritos na forma
corrigida, com a razão na docstring de cada um:

- `test_hoje_nenhuma_tela_alcancavel_cita_a_retificacao_pendente` virou
  `test_a_lista_e_o_edital_citam_a_retificacao_pendente`;
- `test_um_segundo_rascunho_nasce_sem_aviso_do_primeiro` virou
  `test_quem_vai_compor_outro_rascunho_ve_o_primeiro_e_pode_continuar`. Ele continua afirmando que
  a segunda Retificação é criada (sem unicidade, D-005).

## No navegador (FR-2708)

Servidor `retificacao-103` (porta 8103), banco `ps_demo_103` com `seed_demo`, uma Retificação em
elaboração no Edital 26/2026 criada pelo mesmo POST da tela:

- a Lista mostra "Retificação em elaboração · Submeter para revisão" na linha do Edital 26/2026, como
  link para o detalhe;
- o detalhe da Retificação mostra a trilha, a situação, "O próximo ato é seu", "Editar a
  Retificação", "Submeter para revisão" e "Quem atuou";
- a edição abre com o valor do rascunho no campo ("Vitória — campus Jucutuquara"), a justificativa
  preenchida e a revisão 1 no campo oculto, sem erro no console (a CSP não recusou nada);
- o detalhe do Edital mostra "Retificações em curso" separada de "Documentos publicados", onde está
  a Retificação já publicada pelo `seed_demo`;
- a 375 px, a Lista, o detalhe do Edital, o detalhe da Retificação, a edição e a confirmação de
  submeter têm `scrollWidth` igual a `clientWidth` (375): nenhuma rola para o lado.

Os links e botões novos são `<a>` e `<button>` nativos, alcançáveis por Tab; o ato desabilitado é
um `<span aria-disabled>` com o motivo associado por `aria-describedby`, o mesmo desenho do Edital.

## O que não foi verificado

- **SC-978**: a jornada com três pessoas reais.
- A corrida verdadeira de duas edições é exercitada por um segundo fio com outra conexão no meio da
  gravação (`test_f_a_corrida…`), e não por carga.
- O leitor de tela não foi usado; a associação do motivo é conferida no HTML.
