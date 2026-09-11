# Quickstart — 014 · Corte e Progressão entre Etapas

Como provar que a feature funciona, de ponta a ponta, **pelo canal do ator** — que é o que o
Princípio VI da Constituição exige e o que o gate da §9 da spec percorre.

Este arquivo é guia de validação. Ele não traz implementação: modelo e contratos estão em
[data-model.md](data-model.md) e [contracts/corte.md](contracts/corte.md).

---

## Antes de começar

### O banco desta worktree é próprio

Suítes paralelas disputam `test_processo_seletivo` e se derrubam. Esta feature usa banco próprio:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_014 DB_USER=$USER make preparar
```

`preparar` são **três** passos nesta ordem — provisionar, migrar, provisionar de novo. A segunda
passada é a que concede privilégio sobre as tabelas que as migrations acabaram de criar; se ela
disser `0 de N protegidas`, ela não rodou. É ela que dá ao papel de runtime o `INSERT` sem `UPDATE`
das duas tabelas novas desta feature.

No macOS com PostgreSQL do Homebrew, `LC_ALL` não é opcional: `createdb` e `pg_ctl` falham sem ele.

### Antes de investigar qualquer erro estranho

```bash
cd backend && DB_NAME=ps_demo_014 DB_USER=$USER uv run python manage.py migrate --check
```

Migration desaplicada contamina a sessão inteira, e o sintoma é `relation ... does not exist` num
arquivo sorteado, longe da causa.

### Numa worktree nova, instale o grupo dev antes da primeira suíte

```bash
cd backend && uv sync --extra dev
```

Sem isso, `make test-pg` cria o ambiente, instala só o runtime e morre com `Failed to spawn: pytest`.
Parece defeito do alvo; é ambiente vazio.

### O servidor

Acrescente uma entrada ao `.claude/launch.json` — **acrescente**, sem reescrever o arquivo, que é
versionado e tem as entradas de outras sessões:

```json
{
  "name": "corte-014",
  "runtimeExecutable": "sh",
  "runtimeArgs": ["-c", "cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_demo_014 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8014"],
  "port": 8014,
  "url": "http://localhost:8014"
}
```

Três coisas que já custaram sessões:

- **`INTERFACE_SELETOR_IDENTIDADE=true` não é opcional**: sem ela `/gestao/` devolve 503.
- **`localhost`, e não `127.0.0.1`**: o padrão de `ALLOWED_HOSTS` só tem o primeiro, e o segundo
  devolve `DisallowedHost`.
- **O servidor serve o código da worktree.** "Não vejo a mudança" costuma ser a porta errada.

E uma quarta, própria desta feature: **404 na gestão costuma ser autorização**, não rota quebrada.
Reproduza com o papel exato do ator antes de sair caçando URL.

---

## O Edital do percurso

O `14/2026`, reduzido ao que a feature precisa provar, mais um recorte do `77/2026` para a faixa
seguinte. `seed_demo` **não** produz este certame — o elenco dele colide com os candidatos que
precisamos —, então o Edital é montado à mão pela interface.

| | Perfil | Etapas | Marco | Regra de corte |
|---|---|---|---|---|
| **A** | `TFC-01` — Orientador de TFC | 1 Prova de Títulos (pontuada), 2 Entrevista | `M1` | alvo **fixo 10**, excedente **0**, empate **STRICT**, governa a **Etapa 2**, continuação **NONE** |
| **B** | `FIC-01` — vagas remanescentes | **uma só**: Análise documental | `M2`, que ordena por sorteio e **enumera essa mesma Etapa** | alvo **derivado**, excedente **30**, empate `ADMITS_SURPLUS`, governa a **Análise documental**, continuação **ALLOWED** |

No Perfil B, o quadro de vagas publica **40** vagas imediatas na linha geral — é dele que o alvo
derivado sai.

**O Perfil B tem uma Etapa só, e isso não é simplificação.** É a forma do 77/2026: não há Etapa
avaliada antes do sorteio — quem envia inscrição completa entra na relação de habilitados, sorteia-se,
e só então os documentos dos primeiros são analisados. O marco precisa enumerar ao menos uma Etapa,
porque o domínio exige, e a única que existe é justamente a que o corte governa. Inventar uma Etapa
"Sorteio" para contornar isso — como uma redação anterior deste percurso fazia — cria uma Etapa que
ninguém avalia, que nunca produz Resultado e que trava o certame.

**As duas declarações de fronteira não são detalhe de formulário.** A Etapa governada é declarada
porque num marco de sorteio a Etapa enumerada não significa nada — o domínio exige que o marco
enumere alguma, e a ordem nasce da semente. E a continuação é declarada porque o 14 e o 77 respondem
diferente: a cláusula 6.1 do 14 diz que quem não foi convocado não será classificado, e a 6.3 do 77
manda analisar o próximo *até que se preencha*.

Inscreva **14 candidatos** no Perfil A e consolide os Resultados da Etapa 1 de modo que as posições
9, 10 e 11 fiquem **empatadas e sem desempate publicado**. É esse arranjo que exercita a fronteira, e
montá-lo de outro jeito faz o Percurso 2 passar sem provar nada.

---

## Percurso 1 — Declarar a regra (`US1`, `SC-058`)

Como **elaborador**, em `/gestao/editais/<id>/compor/perfis/`.

1. No cartão do Perfil A, seção **Marcos classificatórios**, abra `M1`. Junto da janela recursal
   aparece **Regra de corte**.
2. Escolha *quantidade fixa*, digite `10`, excedente `0`, desfecho do empate **alvo estrito**, a
   **Etapa governada** (a Entrevista) e continuação **não admitida**.
3. Salve o rascunho, recarregue: os seis valores voltam.

**Prova**: a regra é conteúdo do marco, não configuração de tela (`FR-178`, `UX-024`).

### As recusas, na mesma tela

| Faça | Espere |
|---|---|
| escolher *derivado do quadro* e ainda assim digitar `10` no alvo | recusa: o alvo tem uma fonte só (`FR-179`) |
| digitar `-1` no alvo ou no excedente | recusa (`FR-179`, `FR-180`) |
| deixar o desfecho do empate **em branco** e tentar **publicar** | publicação impedida, com o marco nomeado (`FR-182`, `UX-025`) |
| não declarar a **Etapa governada** — nem uma Etapa, nem a ausência explícita — e publicar | impedida, dizendo que ela não é inferida de lugar nenhum (`FR-224`) |
| declarar Etapa governada que **não existe** na versão | impedida, nomeando o marco e a Etapa (`FR-225`) |
| no Perfil **A**, governar uma das Etapas que alimentam a própria ordem | impedida: seria laço (`FR-229`) — e no Perfil **B**, governar a Etapa que o marco enumera **publica**, porque a ordem vem do sorteio |
| não declarar se admite **continuação** e publicar | impedida, nomeando o marco (`FR-226`) |
| pôr regra *derivada* num marco de **três listas** com quadro parcial e publicar | impedida, nomeando o recorte sem linha (`FR-183`) — e linha **zerada** publica |
| declarar regra de corte em **dois** marcos que declaram governar a mesma Etapa | impedida, nomeando os dois marcos e a Etapa |

### O que tem de ser aceito

Publique o Perfil A **sem** regra de corte em nenhum marco. Passa — e a Etapa 2 recebe todos os
habilitados, exatamente como antes desta feature (`FR-214`, `SC-069`).

---

## Percurso 2 — Emitir o corte (`US2`, `SC-055`, `SC-059`)

Como **presidência**, em `/gestao/editais/<id>/marcos/<M1>/corte`.

1. A tela abre com a faixa calculada: alvo declarado `10`, alvo apurado `10`, excedente `0` — faixa
   de `10` —, quem progride, quem fica fora e a última posição alcançada. **Nada foi gravado**
   (`FR-190`).
2. Com as posições 9, 10 e 11 empatadas e o desfecho **alvo estrito**, a emissão é **recusada**, e a
   mensagem nomeia as posições empatadas (`FR-195`, `SC-059`).
3. Retifique o marco para **admite excedente** e recarregue: agora as três empatadas progridem, a
   faixa tem 11, e o ato registra **1 além do alvo** (`FR-196`, `SC-060`).
4. Emita. O corte passa a existir com autor, instante, ordem citada e versão.
5. Abra o corte emitido: os **14** participantes considerados constam — 11 que progrediram e 3 fora
   da faixa, cada um com posição e causa (`FR-194`, `SC-057`).

### As recusas da emissão

| Faça | Espere |
|---|---|
| emitir num recorte **sem ordem vigente** | recusa nomeada (`FR-197`) |
| suceder a ordem e **então** emitir | recusa: não se corta sobre ordem obsoleta (`FR-198`) |
| abrir o corte de um marco **sem regra declarada** | recusa `marco_sem_regra_de_corte`; nenhum corte existe sem regra publicada (`SC-058`) |
| emitir de novo, com geração vigente e **sem motivo** | recusa (`FR-200`) |
| emitir duas vezes em paralelo | uma geração só; a segunda volta como conflito (`FR-201`, `SC-064`) |
| alterar o corte emitido, por qualquer caminho | recusado (`SC-061`) |

---

## Percurso 3 — Conduzir a Etapa seguinte (`US3`, `SC-056`)

Como **comissão**, na Etapa 2 do Perfil A.

1. A Etapa 2 lista **11** participantes — a faixa —, e a contagem confere com o alvo apurado mais o
   excedente por empate, sem diferença de uma unidade (`SC-056`).
2. Os 3 de fora aparecem nomeados **fora do corte**, com posição e faixa não alcançada. Não somem da
   tela (`FR-210`, `UX-026`).
3. Tente distribuir um deles: recusado, e a recusa diz que está fora do corte — não que não existe.
4. Tome alguém **eliminado na Etapa 1** que apareceria dentro da faixa: continua fora. O corte soma à
   regra anterior, não a revoga (`FR-209`).
5. Crie uma Atribuição antes de emitir o corte, emita, e confirme que ela é preservada e **não**
   autoriza trabalho (`FR-211`).

**Prova do orçamento**: a listagem da Etapa 2 faz o mesmo número de consultas que fazia antes desta
feature (`SC-068`). O teste que conta consultas é quem cobra, e ele é anterior a esta feature.

---

## Percurso 4 — A faixa seguinte (`US4`, `SC-064`, `SC-065`)

Como **presidência**, no Perfil B — o recorte de sorteio, com alvo derivado.

1. Abra o corte de `M2`: alvo apurado **40**, lido da linha geral do quadro com a origem visível, e
   excedente **30** — faixa de **70** (`FR-189`, `FR-193`, `SC-071`).
2. Emita. Os **70** primeiros da ordem do sorteio progridem para a Análise documental: as 40 vagas e
   os até 30 suplentes, analisados **juntos**, que é o que a cláusula 6.10 manda com a palavra
   *imediata*.
3. Indefira seis inscrições dessa faixa.
4. **Continue**: declare `quantidade 6` e o motivo *"indeferimento de seis inscrições da 1ª faixa"*.
   A faixa seguinte começa na posição 71, e a anterior **continua vigente** — as duas na mesma
   geração (`FR-202`, `SC-064`).
5. Volte ao Perfil A e tente continuar: recusado, porque aquele Edital publicou `continuation: NONE`
   (`FR-204`, `FR-226`).

### As recusas da continuação

| Faça | Espere |
|---|---|
| continuar **sem motivo** | recusa (`FR-203`) |
| continuar onde a regra publica `continuation: NONE` | recusa dizendo que aquele Edital não a publicou (`FR-204`) |
| suceder a ordem e **então** continuar | recusa (`FR-205`) |
| esperar o sistema continuar sozinho | nada acontece, em nenhum cenário (`FR-206`, `SC-065`) |

**E a prova da fronteira**: em nenhuma tela, mensagem, ato ou documento deste percurso aparecem as
palavras *vaga ocupada*, *vaga preenchida* ou *déficit* (`FR-207`, `SC-066`).

---

## Percurso 5 — A obsolescência (`US5`, `SC-062`, `SC-063`)

1. Com o corte de `M1` emitido, **suceda a ordem**. Abra o marco: o corte aparece obsoleto, com a
   causa **ordem sucedida** — e o corte vigente continua o mesmo, byte a byte (`FR-215`, `FR-217`).
2. Retifique o `targetCount` de `M1`: a causa passa a ser **regra alterada**.
3. No Perfil B, retifique a linha do quadro de `40` para `38`: causa **quadro alterado** — que só é
   detectável porque o ato guardou o `rowId` (`R-009`).
4. Defira um recurso que devolva alguém eliminado ao universo: causa **participante reingressou**, e
   não uma divergência genérica (`FR-218`, `FR-216`).
5. Com o corte obsoleto, tente publicar resultado que dele dependa: **impedido**, com o caminho a
   seguir (`FR-219`, `SC-063`).
6. Ainda obsoleto, tente **distribuir**, concluir avaliação ou **consolidar Resultado** na Etapa
   governada: os três são recusados, dizendo
   que a faixa está para trás e que o caminho é emitir a geração sucessora. O trabalho já registrado
   continua íntegro e legível (`FR-228`, `UX-030`, `SC-073`).
7. No Perfil B, que já tem faixa inicial **e** continuação: suceda a geração com motivo. **Nenhuma**
   das duas faixas continua autorizando participante, e a Etapa governada passa a ler apenas a
   geração nova (`FR-227`, `SC-072`).

---

## Percurso 6 — Auditar (`US6`, `SC-061`, `SC-070`)

1. Abra um corte sucedido: ele continua legível, com a regra na versão que o governou.
2. Retifique o Edital renomeando a Modalidade do recorte. Reabra o corte antigo: ele é lido com os
   **nomes da versão que congelou**, e não com os de hoje.
3. Reproduza a faixa a partir do universo declarado: idêntica, com a mesma última posição alcançada
   (`FR-199`, `SC-061`).
4. Recupere a auditoria da emissão sem tocar no banco: ator, instante, recorte, ordem citada e alvo
   apurado (`FR-222`, `SC-070`).

---

## Verificação automatizada

```bash
cd backend && DB_NAME=ps_demo_014 make lint check test-pg
```

`test-pg`, e **não** `test`: sem `TEST_DB_ENGINE=postgresql` **e** `DB_USER`, a suíte cai para SQLite,
21 casos falham e 182 são pulados — e nada avisa.

`lint` são **dois** passos — `ruff check` **e** `ruff format --check`. Rodar só o primeiro declara
verde local e quebra no CI.

**O teste de citações lê `specs/`.** Escreveu spec, plano, pesquisa ou tarefa? Rode a suíte antes de
empurrar — `tests/test_citacoes_de_requisito.py` falha se alguma citação `FR-`, `SC-`, `UX-` ou `D-`
apontar para identificador que nenhuma spec define.

**A fixture de bytes do documento é regenerada de propósito** nesta feature: a regra de corte entra na
seção do marco no PDF, e `test_documento_publicado.py` compara bytes.

---

## Registro do percurso

O E2E deste projeto é percurso exploratório conduzido contra o servidor real, com relatório
versionado. O desta feature vai para `doc/e2e/014-corte-e-progressao/relatorio.md`, com capturas em
`screenshots/`.

Cada achado recebe identificador `E2E14-NNN`, e ele é **citado na docstring do teste que o fecha** —
é assim que o defeito encontrado no percurso deixa de poder voltar em silêncio.
