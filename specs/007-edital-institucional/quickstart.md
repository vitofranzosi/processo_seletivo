# Fase 1 — Como demonstrar e validar

**Feature**: 007 — Edital Institucional | **Data**: 2026-08-30

A condição de merge de cada entrega é a **demonstração no navegador**, não a contagem de testes
(princípio VI da Constituição). Este guia diz como preparar o ambiente, o que rodar e o que se deve
ver.

---

## Pré-requisitos

PostgreSQL local precisa de `LC_ALL` definido, e a role padrão da máquina não existe no cluster —
sobrescreva `DB_USER`. Ambos são particularidades conhecidas deste ambiente, não da feature.

**`TEST_DB_ENGINE=postgresql` é obrigatório e é o que se esquece.** `config/settings/test.py` só
olha essa variável; sem ela a suíte usa sqlite em memória **sem avisar** e pula 43 testes de
integridade — triggers de imutabilidade, privilégios, locks e validação de migrations. Nos dois
casos a suíte fica verde, então o sinal é a contagem de skips: **894 passed, 1 skipped** com
PostgreSQL, contra 851 passed e 44 skipped sem ele.

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" uv run pytest -q
```

A interface exige o seletor de identidade ligado; sem a variável, `/gestao/` devolve 503:

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DB_USER="$(whoami)" uv run python manage.py runserver 8007
```

---

## Validação por entrega

### Entrega 1 — O documento se lê como um Edital (FR-002, FR-003)

**Preparar**: um Edital publicado com Cronograma, ao menos uma Etapa com peso `2` e nota mínima
`60`, e uma modalidade com percentual `20`. A seed de demonstração já produz esse conjunto.

**Ver**: abrir o documento pelo detalhe do Edital publicado.

| Deve aparecer | Não pode aparecer |
|---|---|
| `20%` | `20.0000%` |
| `peso 2` | `peso 2.0000` |
| `nota mínima 60` | `nota mínima 60.0000` |
| datas dos Eventos | `Situação: PLANEJADO` |

**Verificar também**: um percentual `12,5` sai como `12,5%` e não como `12.5%`.

**Suíte**: `tests/unit/publicacoes/test_humano.py` (novo) e a fixture de bytes regenerada.

---

### Entrega 2 — A forma canônica v3 (FR-004, FR-007, FR-012, FR-014, FR-017)

**Preparar**: o banco é **recriado do zero**, não migrado. Editais publicados na versão 2 não
sobrevivem a esta entrega, por decisão declarada — e `migrate` sozinho os deixaria lá, irretificáveis
e ocupando a demonstração. `seed_demo` também não é idempotente contra dados existentes.

```bash
dropdb --if-exists processo_seletivo_007 && createdb processo_seletivo_007
```

```bash
cd backend && DB_NAME=processo_seletivo_007 DB_USER="$(whoami)" uv run python manage.py migrate
```

```bash
cd backend && DB_NAME=processo_seletivo_007 DB_USER="$(whoami)" uv run python manage.py seed_demo
```

```bash
cd backend && uv run python scripts/gerar_fixture_documento.py
```

**Ver, no assistente**: a etapa `Conteúdo` mostra **dez** seções, com Apresentação em primeiro,
Requisitos Gerais antes de Da Inscrição, e Critérios de Classificação depois de Etapas de Avaliação.
Editar o texto de uma das três novas e visualizar o Edital: a alteração aparece na posição declarada.

**Ver, na etapa Perfis**: três campos novos — atribuições, carga horária e remuneração. Preencher
atribuições com **dois parágrafos**, salvar, ir ao Cronograma, salvar, voltar aos Perfis: os três
continuam lá, com os dois parágrafos.

**Ver, no documento publicado**: os três campos impressos junto dos demais dados do Perfil, com os
parágrafos preservados; e a seção de integridade dizendo `Edital 12/2027` e
`Processo Seletivo <código> — <título>`, com o SHA-256 presente e **nenhum UUID**.

**Verificar a irretificabilidade declarada**: uma Publicação da versão 2, se ainda existir, é
recusada na consolidação por versão divergente. É o comportamento esperado, não um defeito.

**Verificar a proteção da identidade** (FR-004, SC-002b): tentar uma Retificação que enderece
`/processoTitle`, `/processoCode`, `/editalId`, `/processoId` ou `/schemaVersion`. Todas recusadas.
Endereçar `/title` ou `/description` continua funcionando — são retificáveis por desenho.

**Verificar que `number` não virou inteiro**: um Edital `"02"/2027` mantém `"02"` no snapshot, com o
zero à esquerda. `Edital.number` é `CharField`, e a forma canônica o preserva.

**Suíte**: `tests/contract/test_forma_publicada.py` — forma v3 completa, incluindo a regra de
ausência `""` dos três campos e o tipo string de `number`;
`tests/unit/publicacoes/test_identidade_imutavel.py` (novo) para a recusa dos cinco campos;
`tests/migrations/` para a `0005`.

---

### Entrega 3 — O fluxo administrativo sem becos (FR-021 a FR-027)

Quatro verificações, todas na interface.

1. **A recusa aponta o campo certo.** Com um Edital `21/2027` já existente no escopo, criar um
   Processo novo cujo primeiro Edital repita `21/2027`. A mensagem deve falar do **número/ano do
   Edital**, não da identificação institucional do Processo.
2. **O próximo passo é oferecido.** Criado o Processo, a tela seguinte destaca `Elaborar o Edital
   <n>/<ano>` como ação primária; o impedimento de cancelar deixa de ocupar o destaque.
3. **Nada é oferecido e negado no mesmo cartão.** Num Edital publicado, o cartão "O que fazer agora"
   nunca lista uma ação **e** a frase de ausência. Num Edital recém-criado sem dados, `Submeter`
   aparece **desabilitado com o motivo ao lado** — não escondido, não oferecido.
4. **Retificar respeita a permissão.** Entrar como quem homologa e publica, sem
   `retificacao:elaborar`: o detalhe do Edital publicado não oferece `Retificar`. Alcançando
   `/gestao/editais/<id>/retificar` por URL, a tela abre **em leitura** — sem campos de edição, sem
   botão de envio.

**Suíte**: `tests/interface/test_acoes.py` (novo), cobrindo as cinco situações de
`ACOES_POR_SITUACAO` × papéis; `tests/unit/processos/` para o erro separado.

---

### Entrega 4 — Passagem de bastão (FR-028 a FR-031)

**Ver**: submeter um Edital como quem elabora. A confirmação e o detalhe devem dizer a situação e
qual **papel** age a seguir. Homologar como segunda pessoa e reler: o próximo ato é publicar.

**O caso que realmente testa a regra** (cenário 3 da `US5`): um ator que **elaborou e homologou o
mesmo Edital** e que também tem a permissão de publicar. A tela deve dizer que falta publicar e que o
ato exige outra pessoa autorizada — **sem apontá-lo**. Derivar só de `ACOES_POR_SITUACAO` diria "é
você"; a indicação precisa consultar também a segregação de funções, que é o que a publicação
aplicará. Verificar em seguida o contraste: com o Edital homologado por outra pessoa, a mesma tela
aponta quem publica.

**Verificar a ausência**: não existe fila, caixa de entrada, aviso, e-mail nem designação a pessoa.
Nenhum campo novo é persistido.

**Suíte**: `tests/interface/test_bastao.py` (novo).

---

### Entrega 5 — Os atritos de operação (FR-032 a FR-043)

Percurso único pelo assistente inteiro, observando:

| Onde | O que verificar |
|---|---|
| Todo formulário | Campo obrigatório marcado na etiqueta e exposto a tecnologia assistiva |
| Envio recusado | Resumo no topo com âncora **e** marca junto do campo |
| Criar Processo | `Ano` com a mesma altura, fonte e borda dos vizinhos; `Número` respeitando a largura declarada |
| Cronograma e Etapas | `↑` desabilitado na primeira linha, `↓` na última; cada linha diz "Evento 2 de 3" |
| Etapas | A opção de Evento mostra a data herdada |
| Etapas | Eliminatória e Classificatória agrupadas sob legenda "Caráter" |
| Perfis | Remover linha preenchida pede confirmação; linha vazia não pede |
| Publicar | Autoridade escolhida em lista; **nenhum UUID digitado** |
| Assistente | Edital novo: `Conteúdo` aparece como "pronta para revisar", não "concluída". Depois de salvar a etapa, passa a "concluída" |
| Depois de submeter | A faixa diz `Submissão para revisão`, não `submeter` |
| Auditoria | Quatro gravações em etapas diferentes aparecem nomeando a área alterada |

**Acessibilidade (SC-009b)**: percorrer o assistente **só pelo teclado**, com leitor de tela,
alcançando obrigatoriedade, motivo de ato desabilitado, resumo de erros e confirmação de remoção —
sem depender de cor para distinguir estado de etapa.

---

## Demonstração de ponta a ponta (SC-010)

O cenário emblemático da `006` permanece o da `007`, com **dois atores**, porque a publicação recusa
quem elaborou, homologou e publicou sozinho:

> Painel → Novo Processo → **Elaborar (ação primária)** → Identificação → Perfis (**com atribuições,
> carga horária e remuneração**) → Cronograma → Etapas → Modalidades → Conteúdo (**dez seções**) →
> Revisão → Prévia → Submissão → **passagem de bastão** → Homologação → Publicação (**autoridade
> escolhida em lista**) → documento publicado **que se lê como Edital**.

Tudo pela interface administrativa: sem manipulação de banco, sem chamada manual de API, sem shell.

---

## Antes de abrir o PR

```bash
cd backend && uv run ruff check .
```

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" uv run pytest -q
```

**Só `ruff check`, sem `ruff format`.** A CI roda exatamente `uv run ruff check .`
(`.github/workflows/backend.yml:40`), e o repositório **não** adota o formatador: 29 arquivos
pré-existentes seriam reformatados por ele, `pdf.py` e `test_fluxo.py` inclusive. Rodar
`ruff format` aqui produziria um diff enorme e alheio à feature.

E a pergunta que fecha cada entrega: **isto aumentou a fidelidade do Edital real ou a fluidez da
jornada de autoria?** Se um item da implementação não responde a nenhuma das duas, ele não pertence
a esta feature — registra-se e não se corrige aqui (P-001).
