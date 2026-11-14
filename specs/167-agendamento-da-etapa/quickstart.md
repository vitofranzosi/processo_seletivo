# Quickstart: validar o agendamento da Etapa

Roteiro de verificação da `167`. O modelo está em [data-model.md](data-model.md); as rotas, em
[contracts/telas.md](contracts/telas.md); as frases esperadas, em
[contracts/recusas.md](contracts/recusas.md). Os caminhos de teste são os de [tasks.md](tasks.md).

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado, e um `DB_NAME` próprio da worktree (ver *As armadilhas
  caras* no `CLAUDE.md`). A suíte em SQLite não vale.
- `uv sync --extra dev` na worktree (worktree nova não tem pytest).
- O banco preparado por `make preparar`. Depois da entrega B, o provisionamento deve dizer
  **63** tabelas append-only no total — e o primeiro número não pode ser zero.
- `manage.py migrate --check` limpo antes de investigar qualquer erro estranho.

## 1. A suíte de cada entrega

Enquanto trabalha, rode só o que a entrega toca (a suíte inteira, uma de cada vez):

```bash
cd backend && DB_NAME=gps_167 make test-pg PYTEST_ADDOPTS="tests/unit/agendamento tests/integration/agendamento tests/interface/test_agenda_da_etapa_configurar.py tests/interface/test_agenda_da_etapa_montar.py"
```

```bash
cd backend && DB_NAME=gps_167 make test-pg PYTEST_ADDOPTS="tests/integration/agendamento tests/interface/test_agenda_da_etapa_conferir.py tests/portal/test_agenda_publica.py tests/integration/test_database_permissions.py tests/migrations/test_migrations.py"
```

```bash
cd backend && DB_NAME=gps_167 make test-pg PYTEST_ADDOPTS="tests/integration/agendamento/test_avisos_da_agenda.py tests/integration/agendamento/test_atos_individuais.py tests/interface/test_agenda_da_etapa_publicada.py tests/test_situacoes_de_mensagem.py"
```

## 2. Cenários de aceitação, pelo teste que os prova

| Cenário | Teste | Esperado |
|---|---|---|
| US1, a conta do teste independente | `tests/unit/agendamento/test_horarios.py` | 23/11 08–12 e 13–17, 10 + 5, uma banca: 32; com 24/11: 64; duas bancas 08–12, 20 + 10: 16 (SC-2391) |
| US1, as oito recusas | `tests/unit/agendamento/test_configuracao.py` | cada uma com a frase do contrato (SC-2391) |
| US1, configurar antes de a lista fechar | `tests/integration/agendamento/test_configuracao.py` | aceita, com a frase de lista aberta |
| US2, preencher e ajustar | `tests/unit/agendamento/test_preenchimento.py`, `tests/integration/agendamento/test_montagem.py` | 32 recebem, 11 sobram; o agendado à mão não se move; empate pelo protocolo |
| US2, concorrência | `tests/integration/agendamento/test_concorrencia_da_montagem.py` | duas transações no mesmo horário: uma ocupa, a outra recebe `horario_ocupado` (SC-2392) |
| US3, impedimentos e publicação | `tests/integration/agendamento/test_publicacao.py` | cada impedimento recusa; o completo publica; o repetido devolve o mesmo ato (SC-2393, SC-2396) |
| US3, a página pública | `tests/portal/test_agenda_publica.py` | busca por protocolo e por nome; só protocolo na Etapa por Modalidade; nenhum endereço, CPF, e-mail, telefone ou Modalidade nos bytes nem no HTML (SC-2394) |
| US3, a área do candidato | `tests/portal/test_horario_na_area_do_candidato.py` | publicado e não publicado; o botão da sala só ali |
| US4, os avisos | `tests/integration/agendamento/test_avisos_da_agenda.py` | um aviso por pessoa por ato; o despacho envia; a falha não desfaz (SC-2395) |
| US5, os atos individuais | `tests/integration/agendamento/test_atos_individuais.py` | remarcação, inclusão e cancelamento com motivo; um aviso só; o anterior no histórico |
| Append-only | `tests/integration/agendamento/test_atos_imutaveis.py` | `UPDATE` e `DELETE` recusados pelo gatilho e pelo privilégio |
| SC-2397 | `tests/interface/test_agenda_da_etapa_no_estreito.py`, varreduras de CSP e folhas | nenhum `style=`, `<style>`, `<script>` ou `on…=`; toda classe com regra na folha |

## 3. Pelo navegador (cenário A do estudo)

```bash
cd backend && make runserver
```

Com `INTERFACE_SELETOR_IDENTIDADE=true` no ambiente (sem ele, `/gestao/` dá 503) e um Edital
publicado com uma Etapa ligada a um Evento de 23 a 25/11 e 43 inscrições enviadas:

1. Na página da Etapa (Distribuição), a seção "Agenda" diz para que serve; "Configurar a agenda".
2. Remota, 10 + 5, 23/11 com 08:00–12:00 e 13:00–17:00, uma banca com endereço de sala: o simulador
   diz "Faltam 11 horários para as 43 pessoas". "Acrescentar Ter., 24/11 +32": "Cabem todas as 43".
3. Salvar; "Montar a agenda"; "Preencher automaticamente": a prévia diz 43; "Aplicar".
4. Clicar numa pessoa, escolher outro dia e horário, "Mudar de horário".
5. "Conferir e publicar": as quatro linhas de prontidão; escolher o veículo e a autoridade;
   "Publicar a agenda e avisar as pessoas".
6. `manage.py despachar_avisos` à mão (com `AVISOS_AOS_CANDIDATOS` ligada, como no `development`):
   os e-mails saem no terminal **do comando**.
7. Na página pública da seleção, "Agendas"; buscar pelo protocolo de uma pessoa.
8. "Remarcar" uma pessoa, com motivo; despachar de novo: um e-mail só, que diz que o anterior não vale.
9. Repetir em 375 px: a montagem vira coluna e a grade, lista; nenhuma rolagem horizontal; o console
   sem violação de CSP.

Para o cenário B (heteroidentificação), compor a Etapa com alcance restrito a `PPI`: a página pública
mostra só o protocolo.

## 4. Verificação final

```bash
cd backend && make lint check && DB_NAME=gps_167 make test-pg
```

`lint` são dois passos (`ruff check` e `ruff format --check`). A suíte inclui
`tests/test_citacoes_de_requisito.py` e `tests/test_readme_acompanha_o_codigo.py`.
