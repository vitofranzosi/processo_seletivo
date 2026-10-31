# Verificação: Trilha da unidade

Sobre a `main` em `ca1e53ed`, na branch `claude/108-trilha-da-unidade`, em 30/10/2026.

## Executado nesta sessão

### Lint e checagens

`make lint check` — `ruff check` e `ruff format --check` verdes; `manage.py check` e
`makemigrations --check --dry-run` sem migration pendente. **Nenhuma migration nova.**

### Suíte contra PostgreSQL

`make test-pg` com `DB_NAME=ps_108_trilha` (exclusivo desta worktree), 4 workers, `worksteal`, com os
grupos `assistente` e `navegador` instalados.

**13862 passando e 12 pulados, em 569s** (`make lint check test-pg`, 9min31s no total). Os doze
pulados são os doze deliberados que o `CLAUDE.md` descreve com o grupo `assistente` instalado; a
`108` não acrescenta pulado nenhum.

A primeira rodada (634s) teve **uma falha, que era desta branch**:
`tests/test_readme_acompanha_o_codigo.py::test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos`
— a pasta `specs/108-trilha-da-unidade` não estava na tabela de incrementos do README. Corrigida
com a linha da 108, e a suíte inteira foi rodada de novo: é dessa segunda rodada o número acima. O
teste de tempo da ocupação, que oscila com 4 workers, passou nas duas.

### Os casos novos

- `tests/interface/test_trilha_da_unidade.py` — 25 casos: leitura dos cinco assuntos a partir dos
  próprios comandos (cadastrar e encerrar autoridade, sincronizar unidades, criar, editar e inativar
  modelo, confirmar e interromper aviso), exclusão do piloto, estado vazio, paginação e empate,
  custo constante, recusa por papel (os sete sem `auditoria:consultar`), escopo institucional,
  vazamento entre unidades e de escopo vazio, cursor adulterado, filtro e os dois guardiões de
  rótulo.
- `tests/seguranca/test_trilha_da_unidade_acessos.py` — 4 casos no modo institucional, com o provedor
  simulado da `106`: concessão e revogação com os nomes, concessão institucional do Administrador de
  acessos (a do `cefor` aparece, a do campus A não), suspensão e entrada fora, filtro de acessos, e o
  administrador institucional sem unidade recusado.

### Guardiões de lista literal crescidos

- `tests/test_gramatica_das_portas.py`, `MODULOS_DE_VIEW`: o módulo novo. Não há 404 novo, e o
  inventário de negativas da `033` não muda.
- `tests/interface/test_folha_estatica.py`, `QUEM_CARREGA`: a folha `telas/trilha-da-unidade.css`.
- `tests/interface/test_shell_da_gestao.py`, o teste do ícone: passa a identificar Gestor **e**
  Auditor. Sem isso ele deixaria de olhar o ícone do item novo, que o Gestor não alcança. A
  expectativa do teste — todo item com o seu ícone — não mudou.

### Demonstração pelo navegador

O roteiro A do [quickstart](quickstart.md) foi executado num banco próprio (`ps_108_demo`:
`migrate`, `sincronizar_unidades`, `seed_demo`), com o seletor ligado na porta 8108:

- como `gustavo.gestor` (Gestor), a barra não ofereceu "Trilha da unidade"; cadastrei "Maria Teste",
  encerrei a vigência dela e inativei o modelo "Publicação retificadora";
- como `demo.auditor` (Auditor), a barra ofereceu o item, inclusive recolhida (o ícone novo); a
  página mostrou a inativação ("Ativo → Inativo"), o encerramento ("Fim da vigência — → 29/11/2026"),
  os cadastros por `gustavo.gestor` e `gabriel.gestor`, os três modelos iniciais e o registro do
  Cefor **por Implantação**; o filtro "Autoridades" deixou só os quatro atos de autoridade;
- como `ana.elaboradora` (Elaboradora), `/gestao/trilha-da-unidade` respondeu "Você não tem
  permissão para isto … depende da permissão de consultar a trilha de auditoria da unidade";
- o console do navegador ficou sem erro nenhum (nenhuma violação de CSP).

SC-1025: a pergunta da J-8 se respondeu em duas telas a partir da barra.

### Revisão de código (31/10/2026)

Seis achados, todos corrigidos:

- **Cursor bem formado por fora e inválido por dentro dava 500.** `decode_cursor` só conferia o
  base64 e o separador; uma data ou um `event_id` inválidos chegavam ao filtro e saíam como
  `ValidationError` do Django. Agora as duas metades se conferem no `decode_cursor`, e a recusa é a
  de cursor, 400 — o que vale também para a API de consulta, que usa a mesma função.
  `test_o_cursor_adulterado_e_recusado` passou a cobrir os três formatos.
- **A barra oferecia a trilha no escopo institucional**, onde a página recusa. O predicado da barra
  confere agora o escopo, como a view, e o caso do escopo institucional confere a barra também.
- O catálogo de papéis se montava a cada linha de vínculo; agora uma vez por página.
- O caso de `TS` chamado "auditor institucional" usava o Administrador institucional, que não tem a
  permissão: renomeado, com a docstring dizendo de onde vem a recusa.
- `tasks.md` citava a folha, o arquivo dos casos de acesso e o predicado da barra com nomes errados.
- Esta seção dizia que a CI não tinha sido conferida.

Depois das correções, `make lint check test-pg` com o mesmo `DB_NAME`: **13863 passando, 12
pulados e 1 falha, em 1040s**. A falha é a do teste de tempo da ocupação
(`test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`), que o `CLAUDE.md` descreve como
oscilante sob carga; a 108 não toca a ocupação, e o teste passou três de três isolado, em série.
A primeira tentativa dessa rodada nem chegou a rodar: o parâmetro novo do caso do cursor sorteava um
`uuid4()`, e os workers coletavam casos diferentes — o UUID agora é fixo.

## Executado pela CI

No PR #348, sobre `c4639ab9`: `test` e `compose` verdes. A revisão acima foi empurrada depois, e o
resultado da CI sobre ela está no próprio PR.

## Pendente

- **As três decisões de governança** (P1 nível institucional, P2 sessões, P3 Gestor), com a saída
  que não concede nada já implementada.
- **A demonstração manual dos acessos**: só nasce no modo institucional, que não tem provedor fora
  dos testes; está provada pelos casos de `TS`, e não pelo navegador.
- **O achado da interrupção do aviso** (`UUID(int=pk)` na trilha), registrado na spec.
- O merge, que é do usuário.
