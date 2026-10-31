# Quickstart: Trilha da unidade

Dois roteiros. O primeiro é o da homologação, pelo seletor de identidade, e mostra a página com os
atos que o banco de demonstração já tem. O segundo é o dos acessos, que só nascem no modo
institucional e por isso só se mostram pelos testes, como as telas da `107`.

## Roteiro A — pelo navegador, com o seletor

Pré-requisitos (execução nativa, `backend/.env` com um `DB_NAME` próprio; no macOS com o
PostgreSQL do Homebrew, `LC_ALL` exportado):

```bash
cd backend
make preparar     # provisionar, migrar, provisionar: "46 de 46"; "Unidades: 1 criadas"; "Modelos de aviso: 3 criados"
DB_USER=$POSTGRES_USER DB_RUNTIME_USER=$POSTGRES_USER uv run python manage.py seed_demo
INTERFACE_SELETOR_IDENTIDADE=true DB_USER=$POSTGRES_USER DB_RUNTIME_USER=$POSTGRES_USER \
  uv run python manage.py runserver 8108
```

Nenhuma variável nova: a página é da gestão de sempre, e abre com o seletor como as outras.

| Passo | No navegador | O que se vê |
|---|---|---|
| 1 | `http://localhost:8108/gestao/identificar` → "Acessar ambiente de demonstração" → no cartão **Gestor** ("como gustavo.gestor"), "Acessar" | a barra **não** oferece "Trilha da unidade": o Gestor não tem `auditoria:consultar` |
| 2 | "Autoridades da unidade" → "Cadastrar autoridade": cargo "Diretora-Geral substituta", nome "Maria Teste", ato "Portaria 108/2026", início hoje → "Cadastrar autoridade" | a autoridade nova na lista |
| 3 | Abrir "Gerir Maria Teste…" → fim da vigência daqui a 30 dias → "Encerrar a vigência" | a vigência com fim |
| 4 | "Modelos de aviso" → "Inativar “Publicação retificadora”" | o modelo inativo |
| 5 | "Trocar identidade" → "Acessar ambiente de demonstração" → no cartão **Auditor** ("como demo.auditor"), "Acessar" | a barra oferece "Trilha da unidade", no grupo Unidade (recolhida, é o ícone da lista com relógio) |
| 6 | "Trilha da unidade" | do mais recente para o mais antigo: "Inativação de modelo de aviso", Publicação retificadora, "Ativo → Inativo", por gustavo.gestor; "Encerramento de autoridade", Maria Teste, com "Fim da vigência — → dd/mm/aaaa"; "Cadastro de autoridade", Maria Teste, por gustavo.gestor; os dois cadastros do `seed_demo`, por gabriel.gestor; os três modelos iniciais e o "Registro da unidade", **por Implantação** |
| 7 | Assunto → "Autoridades" → "Filtrar" | só os quatro atos de autoridade; "Limpar" volta a todos |
| 8 | Trocar a identidade para o cartão **Elaborador** e abrir `/gestao/trilha-da-unidade` à mão | a recusa explicada: falta "a permissão de consultar a trilha de auditoria da unidade" |

Responde J-8 da auditoria — "quem cadastrou e quem encerrou esta autoridade, e quando" — em duas
telas a partir da barra, sem terminal (SC-1025).

O que o roteiro **não** mostra: as concessões e revogações de acesso. Elas só nascem no modo
institucional, que não tem provedor em execução fora dos testes (a `107`, `FR-3133`). Um aviso
confirmado aparece se o banco tiver resultado publicado e alguém o avisar pela tela do marco; o
`seed_demo` não o faz.

## Roteiro B — os acessos, pelos testes

```bash
cd backend
PYTEST_ADDOPTS="tests/seguranca/test_trilha_da_unidade_acessos.py tests/interface/test_trilha_da_unidade.py" \
  make test-pg PYTEST_WORKERS=0
```

| Caso | O que prova |
|---|---|
| `test_a_concessao_e_a_revogacao_na_unidade_aparecem_com_os_nomes` | o Auditor institucional do Cefor lê a concessão e a revogação de Elaborador, com o nome de quem recebeu e de quem concedeu; a entrada dele na sessão não aparece; nenhum `pessoa-<uuid>` |
| `test_a_concessao_institucional_do_administrador_da_unidade_aparece_e_a_de_outra_nao` | a concessão do Administrador de acessos do Cefor, gravada no escopo institucional, aparece; a do campus A e a suspensão, não (`D-002`, `D-003`) |
| `test_nada_de_outra_unidade_de_escopo_vazio_ou_da_trilha_do_certame_aparece` | nenhum parâmetro faz a página ler outra unidade |
| `test_o_custo_da_pagina_nao_cresce_com_as_linhas` | uma página de poucos atos e uma de vinte, dos cinco assuntos, custam as mesmas consultas |
