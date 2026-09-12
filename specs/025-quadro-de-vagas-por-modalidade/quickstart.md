# Quickstart — 025 · Quadro de Vagas por Modalidade

Como provar que a feature funciona, de ponta a ponta, **pelo canal do ator** — que é o que o
Princípio VI da Constituição exige e o que o gate da §9 da spec percorre.

Este arquivo é guia de validação. Ele não traz implementação: modelo e contratos estão em
[data-model.md](data-model.md) e [contracts/quadro-de-vagas.md](contracts/quadro-de-vagas.md).

---

## Antes de começar

### O banco desta worktree é próprio

Suítes paralelas disputam `test_processo_seletivo` e se derrubam. Esta feature usa banco próprio:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_025 DB_USER=$USER make preparar
```

`preparar` são **três** passos nesta ordem — provisionar, migrar, provisionar de novo. A segunda
passada é a que concede privilégio sobre as tabelas que as migrations acabaram de criar; se ela
disser `0 de N protegidas`, ela não rodou.

No macOS com PostgreSQL do Homebrew, `LC_ALL` não é opcional: `createdb` e `pg_ctl` falham sem ele.

### Antes de investigar qualquer erro estranho

```bash
cd backend && DB_NAME=ps_demo_025 DB_USER=$USER uv run python manage.py migrate --check
```

Migration desaplicada contamina a sessão inteira, e o sintoma é `relation ... does not exist` num
arquivo sorteado, longe da causa.

### O servidor

Acrescente uma entrada ao `.claude/launch.json` — **acrescente**, sem reescrever o arquivo, que é
versionado e tem as entradas de outras sessões:

```json
{
  "name": "quadro-025",
  "runtimeExecutable": "sh",
  "runtimeArgs": ["-c", "cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_demo_025 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8025"],
  "port": 8025,
  "url": "http://localhost:8025"
}
```

Três coisas que já custaram sessões:

- **`INTERFACE_SELETOR_IDENTIDADE=true` não é opcional**: sem ela `/gestao/` devolve 503.
- **`localhost`, e não `127.0.0.1`**: o padrão de `ALLOWED_HOSTS` só tem o primeiro, e o segundo
  devolve `DisallowedHost`.
- **O servidor serve o código da worktree.** "Não vejo a mudança" costuma ser a porta errada.

### O elenco

```bash
cd backend && DB_NAME=ps_demo_025 DB_USER=$USER uv run python manage.py seed_demo
```

`seed_demo` **não** produz o certame que este percurso pede — o elenco dele colide com o que
precisamos. Monte o Edital de teste à mão, pela interface, como abaixo.

---

## O Edital do percurso

O `57/2026`, reduzido ao que a feature precisa provar. Dois Perfis, para que a `FR-158` tenha o que
recusar:

| Perfil | Modalidades | Vagas imediatas |
|---|---|---|
| `P1` — Técnico em Informática | `PCD`, `PPI` | **80** |
| `P2` — Técnico em Edificações | `PPI` | **40** |

Quadro a declarar em `P1`: linha geral **56**, `PCD` **4**, `PPI` **20**. Fecha em 80.

---

## Percurso 1 — Declarar (`US1`, `SC-048`)

Como **elaborador**, em `/gestao/editais/<id>/compor/perfis/`.

1. No cartão de `P1`, a seção **Quadro de vagas** já traz três linhas oferecidas: a geral e uma por
   Modalidade. Só há campo de quantidade — nenhum rótulo, código ou denominação a redigitar.
2. Digite `56`, `4`, `20`. Salve o rascunho.
3. Recarregue. As três quantidades voltam.

**Prova**: quatro números digitados, três linhas gravadas, cada uma com identidade própria
(`FR-153`, `UX-021`).

### As recusas, na mesma tela

| Faça | Espere |
|---|---|
| declarar uma **segunda** linha geral em `P1` | recusa: a ampla concorrência tem uma linha só (`FR-154`) |
| apontar, numa linha de `P1`, a Modalidade `PPI` **de `P2`** | *"…não pertence ao Perfil declarado"* (`FR-158`) |
| trocar `20` por `19` e **submeter** | recusa dizendo **soma 79, declarado 80, diferença 1** (`FR-161`, `UX-023`) |
| deixar a quantidade da `PCD` **em branco** | grava sem aquela linha; a ausência **não** vira zero (`FR-159`, `D-006`) |
| digitar `-1` ou `2,5` | recusa (`FR-156`) |

### A que tem de ser aceita

Submeta `P2` **sem quadro nenhum**. Passa. O quadro é opcional (`FR-160`, `SC-050`).

---

## Percurso 2 — Publicar (`US2`, `SC-051`, `SC-053`)

Como **homologador** e depois como **publicador** — atores distintos, que a segregação de funções
exige.

1. Homologue e publique.
2. Abra o documento publicado. A seção do Perfil `P1` traz o quadro, com **"Ampla concorrência" em
   primeiro lugar** e as reservadas na ordem declarada (`FR-169`).
3. Abra o Perfil `P2`, que não declarou quadro: **a seção não existe** — sem título, sem linha, sem
   frase de ausência (`FR-169`).
4. Leia o conteúdo publicado. `vacancyTable` está lá, com `modalityId: null` na linha geral
   (`FR-164`).

**O quadro que percentual nenhum gera.** Declare, num Perfil de teste, `Q 1` e `PCD 1`. Publique.
Leia de volta: sai exatamente como entrou (`SC-051`).

### O acervo anterior (`SC-050`)

Abra um Edital publicado **antes** desta feature — o `seed_demo` os produz.

- Ele continua legível.
- `vacancyTable` é `[]`.
- **Nenhuma tela afirma que ele tem zero vagas.** Confira a vitrine pública, a página da seleção e o
  documento.

### O resumo canônico (`FR-168`)

Publique o mesmo conteúdo duas vezes e compare os dois resumos. Iguais.

---

## Percurso 3 — Retificar (`US3`, `SC-049`)

Como **elaborador de Retificação**, sobre o Edital publicado.

1. Retifique **a linha da `PPI`**, de `20` para `18`, pela identidade dela.
2. **No mesmo ato**, retifique o total de vagas imediatas de `P1`, de `80` para `78`.
3. Publique a Retificação.
4. Confira: a linha geral continua `56`, a `PCD` continua `4`, e a versão anterior do quadro
   permanece legível sob a norma que a governou (`FR-170`, `FR-173`).

**Nenhuma quantidade foi recalculada.** O total virou `78` porque **quem retifica o declarou**, e não
porque o sistema o somou (`FR-162`, `D-007`).

### E a recusa que prova isso

Tente retificar **só** a linha da `PPI`, de `20` para `18`, deixando o total em `80`. **Recusada**:
soma `78`, declarado `80`, diferença `2` (`FR-161`, `UX-023`). É o mesmo formato de recusa da
`D-008` — dois movimentos que são um ato só.

### A recusa que a `D-008` exige

| Faça | Espere |
|---|---|
| Retificação que remove **só** a Modalidade `PPI` | **recusada**, dizendo qual linha a impede (`FR-172`) |
| Retificação que remove a Modalidade `PPI` **e** a linha, no mesmo ato | aceita — são dois movimentos declarados (`D-008`) |
| endereçar `/profiles/id=…/vacancyTable/0` | `422 positional_addressing_refused` (`FR-170`) |

### Acrescentar

Retifique acrescentando uma linha nova. Ela nasce com identidade própria, e é alcançável na
Retificação seguinte (`FR-171`).

---

## Percurso 4 — O Edital grande (`US4`, `SC-052`)

O `28/2026`: **7 polos**, cada um com as mesmas 3 Modalidades.

Componha os sete Perfis e declare os sete quadros **numa sessão**. Conte os campos digitados.

**Alvo: no máximo 28.** São 7 × (1 geral + 3 reservadas), e nada além — nenhum rótulo, nenhum código,
nenhuma denominação (`SC-052`, `UX-021`).

---

## Verificação automatizada

```bash
cd backend && make lint check test-pg
```

`test-pg`, e **não** `test`: sem `TEST_DB_ENGINE=postgresql` **e** `DB_USER`, a suíte cai para SQLite,
21 casos falham e 182 são pulados — e nada avisa. Com banco próprio nesta worktree:

```bash
cd backend && DB_NAME=ps_demo_025 make lint check test-pg
```

`lint` são **dois** passos — `ruff check` **e** `ruff format --check`. Rodar só o primeiro declara
verde local e quebra no CI.

**O teste de citações lê `specs/`.** Escreveu spec, plano ou pesquisa? Rode a suíte antes de
empurrar — `tests/test_citacoes_de_requisito.py` falha se alguma citação `FR-`, `SC-`, `UX-` ou `D-`
apontar para identificador que nenhuma spec define.

---

## Registro do percurso

O E2E deste projeto é percurso exploratório conduzido contra o servidor real, com relatório
versionado. O desta feature vai para `doc/e2e/025-quadro-de-vagas/relatorio.md`, com capturas em
`screenshots/`.

Cada achado recebe identificador `E2E25-NNN`, e ele é **citado na docstring do teste que o fecha** —
é o que `tests/interface/test_round_trip_do_rascunho.py:1` faz com o `E2E17-001`. Esses
identificadores não casam com a varredura de citações, e podem ser usados livremente.

**Achado encontrado aqui vira registro, não escopo.** A governança é do usuário.
