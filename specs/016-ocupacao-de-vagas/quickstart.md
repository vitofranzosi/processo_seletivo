# Quickstart — validar a Ocupação de Vagas pela interface

**Feature:** `016` · Percorre o gate da §9 da [spec](spec.md), pela interface administrativa, **sem
shell e sem manipulação de banco** — que é o que o Princípio VI exige.

---

## Pré-requisitos

**Um banco de teste próprio.** Suítes paralelas disputam `test_processo_seletivo` e se derrubam;
passe um `DB_NAME` seu.

```bash
cd backend && DB_NAME=ps_demo_016 make provisionar migrate provisionar
```

**Os três passos, nesta ordem, e a segunda passada não é redundância** — é ela que concede
privilégio sobre as tabelas que a migration acabou de criar. O comando informa `N de M`; com esta
feature o `M` é **26**. Se o primeiro número vier `0`, a segunda passada não rodou.

**O seletor de identidade, senão `/gestao/` devolve 503:**

```bash
cd backend && DB_NAME=ps_demo_016 INTERFACE_SELETOR_IDENTIDADE=true make runserver
```

Para servir esta worktree pelo painel de preview, acrescente uma entrada ao `.claude/launch.json`
— **sem reescrevê-lo**, porque o arquivo é versionado e tem entradas de outras sessões. E use
`localhost`: `127.0.0.1` devolve `DisallowedHost`, porque o padrão de `ALLOWED_HOSTS` é só
`localhost`.

**O certame precisa ser montado à mão.** O `seed_demo` não produz este — o elenco dele colide com
os candidatos, e o quadro por modalidade com polos não está lá. Monte pela tela, que é o ponto.

## Cenário 1 — Ler os quatro números (História 1, `UX-031`, `UX-032`)

1. Como **elaborador**, componha um Edital com um Perfil de **80 vagas imediatas**, três
   Modalidades (`AC`, `PPI`, `PCD`) e quadro `55 / 20 / 4` na linha geral e nas duas cotas.
2. Declare **qual Modalidade é a ampla concorrência** (`AC`) — sem isso a conferência do alvo
   derivado recusa a publicação nomeando "Ampla concorrência".
3. Publique. Emita a ordem do marco classificatório e o corte.
4. Abra a ocupação do Perfil.

**Esperado:** três linhas de recorte, cada uma com **publicadas, efetivas, ocupadas e faltando**.
Nenhuma linha mostra só um número. Sem movimento algum, publicadas e efetivas coincidem, e a tela
pode dizê-las em um número só.

**Contraprova que importa:** abra a ocupação de um Edital publicado **antes do degrau 12** (sem
quadro). A tela diz *que o Edital não publicou quadro* — e **não** mostra zero. Mostrar `0` aqui é o
defeito que a `UX-032` existe para impedir.

## Cenário 2 — Emitir a apuração e sucedê-la (`FR-262`, `D-008`)

1. Emita a apuração do recorte de `PPI`.
2. Emita de novo, **sem motivo**. → recusado, `motivo_da_sucessao_obrigatorio`.
3. Emita de novo **com** motivo. → a anterior fica **sucedida**, e continua legível.

**Esperado:** duas apurações no histórico, a segunda vigente. Nenhuma linha alterada — a primeira
guarda os números que ela apurou.

**A contraprova que prova a imutabilidade** (esta sim pelo shell, porque é sobre o banco e não sobre
a jornada): um `UPDATE` direto na apuração é recusado pelo gatilho **e** pela ausência de
privilégio. As duas camadas, e nenhuma contornável em desenvolvimento.

## Cenário 3 — Reverter cota para a ampla (História 2, `FR-245`–`FR-248`)

1. Retifique o Perfil declarando reversão com espécie **"A quantidade que ficou sem preencher"**
   (`ON_BALANCE`).
2. Faça a lista de `PPI` esgotar com saldo — conduza a Etapa governada de modo que apenas 13 dos 20
   fiquem `HABILITADA`.
3. Emita a apuração de `PPI` e da ampla.

**Esperado:** a linha geral passa a **62** (55 + 7) e existe um movimento nomeado, com origem
(`PPI`), destino (ampla) e quantidade (`7`). A soma por recorte **não muda**: 62 + 13 + 4 = 79, como
antes.

**Contraprova 1:** repita num Perfil cujo Edital **não** declara reversão. Nada reverte, e a
tela diz que aquele Edital não prevê reversão.

**Contraprova 2 — a que o 57/2026 exige:** com dois Perfis (dois cursos) no mesmo Edital, esgote um.
**Nenhuma vaga alcança o outro Perfil, por nenhum caminho da interface.** É o item 4.5 daquele
Edital, que proíbe remanejamento entre cursos.

**Contraprova 3 — a espécie importa:** declare `ON_EXHAUSTION` no mesmo cenário. Com 13 de 20
habilitados e a lista **ainda tendo gente**, nada reverte — que é a diferença entre as duas espécies
da `D-007`.

## Cenário 4 — A faixa seguinte causada por déficit (História 3, `FR-255`, `FR-256`)

1. No recorte da ampla, recuse a documentação de 3 pessoas da faixa (`ELIMINADA` na Etapa
   governada).
2. Emita a apuração. → `faltando` = 3.
3. Peça a faixa seguinte **pela ocupação**.

**Esperado:** a faixa seguinte é emitida, e o ato guarda o **déficit apurado** como causa — não
texto digitado. É o que substitui o motivo textual que a `014` hoje exige de quem emite.

**Contraprova 1:** com `faltando` = 0, pedir faixa seguinte é recusado dizendo que não há vaga a
preencher.

**Contraprova 2:** suceda a ordem do recorte e peça de novo. A apuração aparece **obsoleta**, com a
causa nomeada, e não causa faixa nenhuma.

## Cenário 5 — Quem ocupa por duas listas (História 4, `FR-252`, `FR-253`)

1. Monte alguém autodeclarado que esteja dentro do número de vagas **nas duas** listas.
2. Emita a apuração dos dois recortes.

**Esperado:** a pessoa ocupa pela **ampla concorrência**, e a vaga reservada dela fica disponível —
**para o próximo da lista reservada**, nunca para a linha geral. É o item 8.9 do 28/2026, literal.

**A troca que este cenário existe para pegar:** se a vaga liberada for para a ampla, a soma continua
certa e o recorte está errado. Nenhum invariante de soma pega isso; só a asserção de recorte.

## Cenário 6 — Auditar (História 5, `FR-259`)

Abra a auditoria do Perfil e reconstrua o número de hoje a partir do quadro publicado: quadro →
apurações → movimentos. Cada número exibido aponta o ato que o produziu e a versão do conteúdo que
ele leu.

## O que este guia deliberadamente não percorre

- **Convocar, comunicar, aceitar ou matricular.** Não existem antes da `019` (`FR-258`).
- **A cascata Grupo 1→2→3 do 14/2026.** É alvo derivado da `014` (`D-006`), e não está construída.
- **A segunda metade do item 8.8 do 28/2026** — desistência liberando vaga reservada. Desistência
  não existe como fato; ver `R-001` da [pesquisa](research.md).

## Verificação

```bash
cd backend && DB_NAME=ps_demo_016 make lint check test-pg
```

`test-pg` e **não** `test`: no modo padrão a suíte cai para SQLite, onde 31 casos falham por
garantias que aquele banco não tem — inclusive o gatilho append-only desta feature.
