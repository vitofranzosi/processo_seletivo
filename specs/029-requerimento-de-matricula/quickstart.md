# Roteiro de validação — Requerimento de Matrícula (`029`)

**Fase 1** · 16/09/2026. Cada cenário abaixo é percorrível **pelo canal do ator**, sem shell, sem
banco e sem canal alheio — que é o que a Constituição cobra em VI.

---

## Preparar

```bash
cd backend && make DB_NAME=ps_demo_029 lint check test-pg
```

`test-pg`, e não `test`: sem o par `TEST_DB_ENGINE=postgresql` e a role certa, a suíte cai para
SQLite e o gatilho de imutabilidade desta feature **não é exercido** — ele é PostgreSQL puro.

Para percorrer a mão:

```bash
cd backend
make DB_NAME=ps_demo_029 seed
make DB_NAME=ps_demo_029 runserver
```

**Um `cd` só**: a primeira redação repetia `cd backend` na segunda linha, e a segunda tentaria entrar em `backend/backend`. Os alvos são **`seed`** e **`runserver`** — `seed-demo` e `run` não existem no `Makefile`, e a
primeira redação deste roteiro os inventou. E `DB_NAME` vai **como variável do Make**: o `include
.env` sobrepõe o prefixo de ambiente, e sem isso esta worktree semeia o banco de outra.

O seletor de identidade precisa estar ligado (`INTERFACE_SELETOR_IDENTIDADE`) e o portal em modo de
demonstração (`PORTAL_IDENTIDADE_DEMO`), ou `/gestao/` devolve 503. O código de acesso do candidato
sai **no terminal do servidor** na execução nativa, e em <http://localhost:8025> no compose.

---

## C1 — Quem elabora declara a exigência e o texto *(US3)*

1. `/gestao/` → Edital em elaboração → etapa **Inscrição**.
2. Declarar o momento e escrever o texto da declaração de veracidade.
3. Etapa **Revisão** → publicar.

**Esperado**: o conteúdo publicado traz `matriculationRequest` com `moment` e `declarationText`
([contracts](contracts/requerimento-de-matricula.md) §1.1).

**Esperado, e é o teste que importa**: apagar o texto e tentar publicar → **erro impeditivo**, com a
pendência encaminhada à etapa Inscrição (`FR-407`, `SC-136`).

**Esperado**: Edital **sem** a declaração publica normalmente, e nele o requerimento não existe em
lugar nenhum (`FR-371`, `SC-123`) — inclusive digitando a rota à mão.

---

## C2 — O candidato entrega, na inscrição, só o que falta *(US1)*

1. Portal → entrar → iniciar inscrição num Edital que declara *na inscrição*.
2. Abrir o requerimento pelo cartão.

**Esperado**: nome, CPF, e-mail, curso, modalidade e protocolo aparecem como **informação**, com o
caminho para onde se corrigem — e não como campo (`FR-378`, `FR-380`, `SC-120`).

3. Tentar submeter a inscrição sem enviar o requerimento.

**Esperado**: a tela da inscrição **já dizia** que o envio dependia dele — o aviso vem antes da
tentativa, não no clique (`UX-054`).

4. Preencher, aceitar a declaração, enviar. Reabrir.

**Esperado**: a tela mostra o que o sistema recebeu e o instante, sem campo editável (`FR-406`).

5. Tentar enviar sem aceitar a declaração.

**Esperado**: recusado, com o motivo em palavras (`SC-128`).

---

## C3 — O convocado, e o suplente pelo mesmo caminho *(US2)*

1. Edital que declara *na convocação*. Candidato inscrito, sem chamada.

**Esperado**: *"ainda indisponível"*, e a tela distingue isso de *"este certame não pede
requerimento"* (`FR-405`).

2. `/gestao/` → convocar para vaga inicial.

**Esperado**: o requerimento abre, sem intervenção manual (`SC-121`).

3. Registrar desistência de quem foi chamado; apurar; convocar o suplente.

**Esperado**: para o suplente o requerimento abre **pelo mesmo caminho** — nenhum passo
administrativo próprio, nenhuma exceção (`SC-122`).

4. Registrar um desfecho sobre a chamada de quem ainda não enviou.

**Esperado**: o rascunho **permanece**, legível e não enviável (`FR-411`, `SC-134`).

---

## C4 — Correção por convocação para regularizar *(US5)*

1. Requerimento enviado → registrar indeferimento.
2. Convocar a pessoa **para regularizar**.
3. Portal → *conferir e atualizar* → corrigir → enviar.

**Esperado**: nasce um sucessor; o anterior continua legível pelo link da `UX-059`; o vigente é o
novo (`SC-135`).

**Esperado**: sem chamada em aberto, a mesma tentativa é recusada com
`successor_not_authorized`.

---

## C5 — Endereço conhecido, CEP reconhecido, e CEP que não responde

1. Candidato com requerimento enviado em certame anterior abre um novo.

**Esperado**: endereço, filiação e documento já preenchidos. Editar e enviar; abrir o anterior e
encontrá-lo **intacto** (`SC-124`) — é a prova da `D-005`.

2. Digitar um CEP presente na base.

**Esperado**: município, UF e código IBGE chegam preenchidos, sem digitação; logradouro, número,
complemento e bairro seguem editáveis (`SC-126`, `UX-055`).

3. Digitar um CEP cujo registro esteja **incompleto** — sem bairro, ou sem código IBGE.

**Esperado**: o que veio é preenchido, o que faltou fica editável, o código IBGE permanece **não
digitável** e vazio, e o envio conclui (`FR-388`, `FR-390`).

4. Esvaziar a base de referência e repetir.

**Esperado**: a tela diz que não foi possível consultar, **sem culpar quem digitou**; todos os campos
abrem, inclusive município e UF; o envio conclui com código IBGE vazio (`SC-125`, `FR-390`).

---

## C6 — O que não se consegue fazer

| Tentativa | Esperado |
|---|---|
| Alterar requerimento enviado pela tela | recusado |
| `QuerySet.update()` sobre linha `ENVIADO` | recusado pelo **gatilho**, com a role de runtime real |
| `DELETE` sobre linha `ENVIADO` | idem (`SC-127`) |
| Abrir o requerimento de outra pessoa | indistinguível de inexistente (`SC-131`) |
| Ler o dossiê sem `inscricao:consultar` | recusado, sem revelar que o requerimento existe |
| Criar um segundo sucessor do mesmo requerimento | recusado pela restrição de banco |
| Criar dois requerimentos raiz para a mesma Inscrição | idem |

**O de gatilho não é teatro**: é a metade da `FR-396` que a guarda de aplicação não entrega, e é
exercível só contra PostgreSQL — o molde está em `tests/unit/ocupacao/test_efeito_append_only.py`,
que já faz `UPDATE` e `DELETE` com uma role de runtime real.

---

## C7 — As varreduras

```bash
cd backend && uv run pytest tests/test_vocabulario_do_requerimento.py tests/test_citacoes_de_requisito.py tests/test_sem_dado_pessoal_da_amostra.py tests/test_dado_sensivel_do_requerimento.py
```

**Esperado**: nenhuma tela desta feature diz *deferido*, *indeferido*, *homologado* ou *matrícula
efetivada* (`SC-132`, `UX-058`) — lendo o texto **sem** comentário e sem docstring, porque explicar a
proibição exige escrever a palavra proibida.

**Esperado**: nenhum artefato — spec, descoberta, **teste ou fixture** — contém dado pessoal da
amostra real (`SC-137`).

**Esperado**: nenhuma rota, recusa ou registro de auditoria desta feature carrega cor/raça,
filiação, documento, endereço ou faixa de renda (`FR-401`).

---

## C8 — A jornada inteira, de uma vez *(Princípio VI)*

Compor → publicar → inscrever → avaliar → divulgar → apurar → **convocar** → o candidato abre a Área
do Candidato, confere o que o sistema já sabe, completa o que falta, aceita e envia → quem conduz
abre o dossiê e lê o que ela declarou.

**Nenhum passo por shell, por banco ou por canal alheio ao ator daquele passo.** É o cenário que
decide se a feature está entregue.
