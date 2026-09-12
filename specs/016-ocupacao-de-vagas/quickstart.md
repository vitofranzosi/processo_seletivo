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

1. Como **elaborador**, componha um Edital com um Perfil de **40 vagas imediatas**, três
   Modalidades (`AC`, `PPI`, `PCD`) e quadro `28 / 10 / 2` na linha geral e nas duas cotas.
   *São os números do 28/2026 por polo, e a soma fecha com o total de propósito: `80` com quadro
   `55/20/4` somaria 79, que é a divergência silenciosa da `R-006` — caso legítimo de teste, e
   péssimo caminho felizardo para um guia.*
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
2. Faça a lista de `PPI` **esgotar** com saldo: a ordem de PPI tem 3 pessoas, as 3 ficam
   `HABILITADA`, e não há mais ninguém a analisar. Sobram 7 das 10 vagas reservadas.
3. Emita a apuração de `PPI` e da ampla.

**Esperado:** a quantidade **efetiva** da linha geral passa a **35** (28 + 7), enquanto a
**publicada** permanece **28** — e existe um movimento nomeado, com origem (`PPI`), destino (ampla)
e quantidade (`7`). A soma das efetivas por recorte **não muda**: `35 + 3 + 2 = 40`, como antes.

*O `3` aparece duas vezes e não é coincidência: cedido todo o saldo, a efetiva da linha que cede
passa a ser igual ao que ela ocupou. É a mesma conta vista dos dois lados, e é o que a
`FR-247` afirma.*

São exatamente os números da `SC-079`, e é deliberado: critério de sucesso e guia de validação
descrevem o mesmo cenário, para que percorrer o guia **seja** verificar o critério.

**Contraprova 1:** repita num Perfil cujo Edital **não** declara reversão. Nada reverte, e a
tela diz que aquele Edital não prevê reversão.

**Contraprova 2 — a que o 57/2026 exige:** com dois Perfis (dois cursos) no mesmo Edital, esgote um.
**Nenhuma vaga alcança o outro Perfil, por nenhum caminho da interface.** É o item 4.5 daquele
Edital, que proíbe remanejamento entre cursos.

**Contraprova 3 — a espécie importa, e a condição que as separa é a lista ter gente:** monte a
ordem de PPI com **12** pessoas, das quais 8 já estão `HABILITADA` e **4 seguem por analisar**.
Sobram 2 vagas reservadas e a lista **não** esgotou.

- sob `ON_EXHAUSTION`, **nada reverte** — ainda há quem possa ocupar;
- sob `ON_BALANCE`, reverteriam **2**.

É a `D-007` inteira em um par de execuções, e é por isso que o gatilho é declarado e não inferido:
o mesmo estado do mundo produz dois resultados legítimos, e quem decide é o Edital.

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

**Esperado:** a pessoa ocupa pela **ampla concorrência** e **não consta ocupando** na reservada,
cuja vaga segue aberta ao próximo daquela lista. Nenhuma quantidade muda de recorte: as efetivas dos
dois continuam as publicadas, e **movimento nenhum** aparece na tela ou na trilha. É o item 8.9 do
28/2026, literal.

**A troca que este cenário existe para pegar:** modelar isso como transferência da reservada para a
ampla. Num Perfil de 2 amplas e 1 reservada, a soma continua 3 e os recortes ficam 1 e 2 — onde o
Edital manda 2 e 1. Invariante de soma nenhum pega; só a asserção por recorte.

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
