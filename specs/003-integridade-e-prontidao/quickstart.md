# Quickstart: Integridade Normativa e Prontidão para Produção

**Feature**: `003-integridade-e-prontidao` | **Fase**: 1 | **Data**: 2026-08-29

Como verificar o que esta feature entrega. Cada seção diz o que rodar e **o que precisa acontecer**
— não "deve funcionar", mas o resultado exato.

## Suíte

```bash
cd backend && make lint check test
```

A régua desta feature exige também PostgreSQL, sem testes ignorados por falta de banco:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=postgres DB_PASSWORD=postgres uv run pytest
```

Esperado: **zero falhas, zero `ResourceWarning`**. A suíte falha em `ResourceWarning` de propósito
— conexão não fechada é vazamento silencioso.

Cobertura com branches, que SC-006 exige em pelo menos 89% nas duas execuções:

```bash
cd backend && uv run pytest --cov --cov-report=term && uv run coverage report --precision=3
```

## Provisionamento dos papéis

Esta é a verificação que mais dá errado, porque depende de ordem. Contra um banco **realmente
vazio**:

```bash
createdb processo_seletivo && cd backend
```

O provisionamento roda com um papel que possa criar papéis. Atenção: `DB_ROLE`,
`DB_MIGRATION_USER` e `DB_RUNTIME_USER` também escolhem com qual usuário o Django conecta — para
esta etapa, conecte como administrador e passe os nomes dos papéis por flag.

```bash
cd backend && DB_USER=postgres uv run python manage.py provisionar_papeis --migration-role=processo_seletivo_owner --migration-password=... --runtime-role=processo_seletivo_runtime --runtime-password=...
```

Esperado: `0 de 6 tabelas append-only` e o aviso de que a segunda passada é necessária. Falhar aqui
com `relation ... does not exist` é o defeito que esta feature corrigiu.

```bash
cd backend && DB_ROLE=migration uv run python manage.py migrate
```

Esperado: todas as migrations aplicam. Rodar **como o papel de migração** é parte da verificação:
se a propriedade das tabelas não tiver sido transferida, `ALTER TABLE` falha.

```bash
cd backend && DB_USER=postgres uv run python manage.py provisionar_papeis --migration-role=processo_seletivo_owner --migration-password=... --runtime-role=processo_seletivo_runtime --runtime-password=...
```

Esperado: `6 de 6 tabelas append-only estão sem UPDATE nem DELETE para o runtime`, sem aviso.

Conferência independente, conectando como o runtime:

```bash
psql -U processo_seletivo_runtime -d processo_seletivo -c 'UPDATE auditoria_registroauditoria SET reason = reason;'
```

Esperado: `ERROR: permission denied for table auditoria_registroauditoria`.

`--dry-run` imprime a política sem aplicá-la, com as senhas ocultas — é o que se cola numa revisão
ou anexa a um chamado:

```bash
cd backend && uv run python manage.py provisionar_papeis --dry-run
```

Esperado: `PASSWORD '********'`, nunca a senha real.

## Prontidão de produção

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.production uv run python manage.py check --deploy
```

Esperado: **zero achados** com o ambiente correto, e falha de inicialização nomeando a variável
quando faltar segredo forte, hosts explícitos, HTTPS, senha do banco ou autenticação institucional.
Tente com `API_AUTHENTICATION_CLASSES` apontando para o adaptador de desenvolvimento: precisa
recusar.

## Integridade da Retificação

O caminho manual, com o sistema no ar:

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py seed_demo
```

Depois, pela interface em `/gestao/`:

1. Abra dois Perfis com **a mesma denominação**.
2. Elabore uma Retificação que renomeie o segundo.
3. Antes de publicá-la, elabore e publique outra que **remova o primeiro Perfil**.
4. Publique a primeira.

Esperado: `409 target_identity_mismatch`, nomeando `/profiles/1`. Se publicar, o sistema alterou o
Perfil errado — que é o defeito que originou esta feature.

Repita trocando o passo 2 por um `ADD` na posição 1: mesmo resultado.

## JavaScript da interface

As regras da tela são executadas, não procuradas no fonte:

```bash
cd backend/tests && node --test "javascript/*.test.js"
```

Esperado: 19 testes passando. Sem `node` instalado, o teste equivalente em `pytest` é ignorado e a
suíte segue.

**O que estes testes não cobrem, e continua sendo verificação manual:** movimentação de foco para
o campo inválido, anúncio da mensagem pelo leitor de tela, e o balão que `reportValidity` desenha.
Para conferir, abra `/gestao/editais/<id>/compor/perfis`, escolha *Cadastro Reserva limitado*,
deixe o limite vazio e tente enviar — o navegador precisa levar o foco ao campo do limite e
anunciar "Cadastro Reserva limitado exige um limite.".

Expiração do rascunho, também manual quando se quer ver acontecendo: preencha sem enviar, adiante o
relógio do sistema em mais de 24 horas, recarregue. O rascunho não deve ser oferecido.
