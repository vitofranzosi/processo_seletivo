# Quickstart: validar a Interface Administrativa

Como subir a interface e verificar cada história da [spec.md](./spec.md). Escrito depois da
implementação e com cada comando executado — o que não funcionou está dito como não funcionando.

## Subir

Pré-requisitos: os mesmos da 001 — Python 3.13, `uv` e PostgreSQL. Nenhuma dependência de build
JavaScript; o HTMX é servido pelo próprio projeto.

```bash
cd backend && make install
```

Banco de demonstração, do zero:

```bash
createdb processo_seletivo_demo
```

Migrar e povoar. `DB_RUNTIME_USER` é a role que as migrations usam para conceder os privilégios de
runtime; em desenvolvimento aponte para o seu próprio usuário:

```bash
DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=processo_seletivo_demo DB_USER=$USER DB_RUNTIME_USER=$USER DB_HOST=localhost DB_PORT=5432 uv run python manage.py migrate
```

```bash
DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=processo_seletivo_demo DB_USER=$USER DB_RUNTIME_USER=$USER DB_HOST=localhost DB_PORT=5432 uv run python manage.py seed_demo
```

Servir, com o seletor de identidade ligado:

```bash
DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=processo_seletivo_demo DB_USER=$USER DB_RUNTIME_USER=$USER DB_HOST=localhost DB_PORT=5432 DJANGO_DEBUG=true DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8000
```

A interface fica em `http://127.0.0.1:8000/gestao/`.

**O seed publica seu único Edital.** Para ver o assistente de composição, que só abre em elaboração,
crie um rascunho:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/admin/processos -H 'Authorization: Bearer gestor.demo|cefor|processo:criar,edital:elaborar' -H 'Content-Type: application/json' -H 'Idempotency-Key: rascunho-para-validacao-0001' -d '{"institutionalCode":"PS-RASCUNHO-2026","title":"Processo Seletivo Simplificado 2026","firstEdital":{"number":"02","year":2026,"title":"Edital 02/2026 — Rascunho","description":"Para validar o assistente."}}'
```

## O seletor de identidade

`INTERFACE_SELETOR_IDENTIDADE` **nunca deve ser ligada em produção**. Verificado nos dois estados:

| Variável | `/gestao/identificar` | Papéis no HTML |
|---|---|---|
| ausente | 503 | nenhum |
| `true` | 200 | os cinco |

Isso não torna a interface segura. O adaptador do backend aceita
`Bearer <pessoa>|<escopo>|<permissões>`: qualquer pessoa declara qualquer identidade. **Esta feature
não é implantável em produção antes da autenticação institucional.**

## Verificar cada história

### US1 — Entrar e enxergar o próprio trabalho

Identifique-se como `ana.elaboradora` com o papel **Elaborador** e abra `/gestao/`.

- Os Processos do escopo aparecem com seus Editais e situações.
- Em "O que posso fazer", **só** ações que o papel permite. Identifique-se como **Auditor** e volte:
  nenhuma ação de ato aparece.
- Ocultar não é autorizar: abra `/gestao/editais/<id>/atos/cancelar` direto como Auditor. A tela
  explica qual permissão falta e **não** oferece "Confirmar".

### US2 — Montar um Edital sem assistência

No Edital em elaboração, "Elaborar" abre o assistente em quatro etapas.

- "Acrescentar Perfil" insere uma linha sem recarregar; o contador acompanha.
- "Salvar rascunho" preserva; "Avançar" leva à etapa seguinte.
- Cronograma: datas no horário de Brasília.
- Revisão mostra o que falta antes de submeter.

**Não verifique retomada após queda de conexão**: FR-020 não está implementado. O digitado sobrevive
a uma recusa do domínio, não a uma sessão expirada.

### US3 — Conduzir até a publicação

Com o Edital completo, "Submeter para revisão". Antes de confirmar, a tela diz o que o ato provoca.

- Como **Homologador**, homologar exige fundamento.
- Como **Publicador**, publicar exige Autoridade Signatária.
- **Segregação**: identifique-se com os três papéis, faça tudo sozinho e tente publicar. A tela
  avisa antes da tentativa e não oferece "Confirmar".

### US4 — Retificar com clareza do efeito

Em um Edital publicado, "Retificar" mostra o conteúdo vigente em campos editáveis. Altere as vagas
imediatas de um Perfil: só esse campo vira Alteração Normativa.

Retificação também percorre elaborar → submeter → homologar → publicar, e nada muda para o público
antes da publicação.

### US5 — Registrar o desfecho

Em um Processo com Edital publicado, "Cancelar Processo" mostra o impedimento — quais Editais
precisam ser encerrados antes — e não oferece "Confirmar". Encerre o Edital e volte.

### US6 — Consultar a trilha

"Ver trilha de auditoria" lista os atos do mais recente ao mais antigo, com autoria, transição e
fundamento. Sem o papel **Auditor**, a tela recusa com 403.

Nada de conteúdo normativo aparece na trilha, e nenhuma chave de idempotência: ela não é via
alternativa de leitura dos agregados.

## Verificação automatizada

```bash
cd backend && make lint
```

```bash
TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=$USER DB_RUNTIME_USER=$USER DB_HOST=localhost DB_PORT=5432 uv run pytest
```

385 testes, 113 deles em `tests/interface/`.

Só a interface:

```bash
TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=$USER DB_RUNTIME_USER=$USER DB_HOST=localhost DB_PORT=5432 uv run pytest tests/interface/
```

## Acessibilidade

O que está preso em teste — contraste, link de salto, marcação nativa — roda com a suíte. O que
exige navegador está em [accessibility.md](./accessibility.md), com o método para repetir a
verificação com axe-core e o que ela **não** cobre.

Leitor de tela com pessoa usuária real continua pendente e não é substituível por automação.

## Medir os critérios de sucesso

SC-001, SC-002 e SC-008 exigem servidores do Cefor usando a interface, com tempo e taxa de acerto
medidos. **Nunca foram medidos** — é o que esta entrega serve para permitir.

Sugestão: cada pessoa monta um Edital com dois Perfis e três Eventos a partir do assistente, sem
assistência, com o relógio correndo. SC-001 pede 15 minutos; SC-002 pede 90% concluindo na primeira
tentativa.
