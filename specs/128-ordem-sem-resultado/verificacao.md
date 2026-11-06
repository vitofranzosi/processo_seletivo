# Verificação: A ordem por pontuação sem nenhum resultado é recusada (128)

Feita em 06/11/2026, na branch `claude/128-ordem-sem-resultado-9720fd`, sobre a da `126`
(`claude/126-orientacao-p0-307906`, PR #414, aberto e `MERGEABLE` no início e antes do push).

## A análise cruzada (spec × plano × tarefas)

`/speckit-analyze` antes de implementar. Todos os requisitos e critérios cobertos por tarefa, por
intervalo ou por citação direta, exceto a **FR-4219** (acervo e "sem migration"), que nenhuma tarefa
citava: entrou em T006 (o ato do acervo continua vigente) e em T016 (`makemigrations --check`).
Nenhum conflito com a Constituição; nenhuma ambiguidade aberta. A spec revê a FR-4039 da `126` no caso
de nenhum resultado, pela decisão do usuário, e o diz em *Compatibilidade*.

## Suíte

`make lint check test-pg` com `DB_NAME=ps_128`, 4 workers.

| Rodada | Resultado |
|---|---|
| 1ª, com a recusa ligada e antes dos ajustes | **16916 passando, 12 pulados, 2 falhas, 3 erros** (1408s; o fim esperou o `DROP DATABASE` por outra suíte no cluster) |
| 2ª, depois dos ajustes abaixo | **16922 passando, 12 pulados, sem falha** (1416s); `make lint check` verde, `makemigrations --check`: *No changes detected* |
| depois da revisão (título com ato vigente, recorte reservado, ordem do `avaliar` em `test_resultado_da_etapa`) | os arquivos tocados e os guardiões de acessibilidade, CSP, estáticos e vocabulário: **57 + 1972 passando**, 10 pulados (os do vocabulário); lint verde |

As cinco da primeira rodada foram todas previstas pelo plano (R-5): quatro emitiam ordem sem nenhum
Resultado por conveniência, e a quinta era a linha do README que faltava
(`test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos`).

Os 12 pulados são os mesmos da linha de base com os grupos `assistente` e `navegador` instalados: 10
pares do vocabulário, a recusa por vendor e o E2E da Caixa.

## Os testes e fixtures ajustados (FR-4220)

| Teste | Por que emitia sem resultado | O ajuste | O que continua provado |
|---|---|---|---|
| `tests/performance/test_corte.py` (fixture `edital_com_corte`; os dois casos, erro na preparação) | mil inscrições criadas em lote, nenhuma avaliada; a ordem só existia para haver o que cortar | uma Ocorrência na primeira inscrição, pelo comando (`registrar_ocorrencia`) | a mesma população — mil considerados, sem posição (um, eliminado) —, e as mesmas medidas: consultas que não crescem e o teto da tela |
| `tests/performance/test_resultado_da_etapa.py::test_o_custo_e_constante_entre_um_e_dois_marcos` (fixture `com_dois_marcos`) | o marco intermediário enumera a primeira Etapa, que ninguém avaliava; o ato existia só para haver dois marcos publicados | as mesmas duas inscrições são avaliadas também na primeira Etapa (aprovadas, de modo que continuam na segunda), **depois** de emitido e publicado o ato final, para que ele saia como no cenário de um marco só | dois marcos publicados, cada um com o seu ato; a contagem de consultas compara os mesmos dois cenários |
| `tests/integration/classificacao/test_citacao_de_decisao.py::test_citacao_para_ato_de_outro_marco_e_recusada` | o "outro marco" enumera a segunda Etapa, e o cenário só avalia a primeira | a inscrição habilitada na primeira Etapa é avaliada na segunda antes de emitir | a trigger recusa a citação de uma decisão a um ato de outro marco — o ato agora tem Resultado, e o vínculo que se testa é o mesmo |
| `tests/fixtures/corte.py::montar_cenario_do_corte` | — | aceita `pontuacoes=()` sem distribuir nem consolidar: é o cenário do Edital 91 | nenhum chamador existente passava `()` |
| `tests/fixtures/divulgacao.py::pontuar` | — | a distribuição, a conclusão e a consolidação saíram para `avaliar`, que serve também a inscrições existentes; as chaves de idempotência são as mesmas | todos os chamadores de `pontuar` passam na 2ª rodada |

Nenhum teste foi relaxado nem marcado: o comando recusa, e a fixture passou a dar o Resultado que o
cenário pressupunha.

## A coerência com a `126` e a `127` (FR-4217, FR-4218, SC-1306)

- **A `126`**: `conferencia_da_ordem.resumo` passou a ler `nenhuma_com_resultado`, que é a regra do
  comando; o critério é o mesmo que ela usava (a chave da Etapa em `pontuacoes`). A confirmação não abre
  mais no caso recusado (`te::test_a_confirmacao_nao_abre`); no parcial, abre e diz o que dizia
  (`te::test_a_ordem_parcial_continua_com_formulario_e_confirmacao`). `test_orientacao_p0.py` e
  `test_conferencia_da_ordem.py` passaram sem mudança.
- **A `127`** (PRs #415, #416, #417) não está na `main` nem nesta base. Pela leitura de
  `interface/andamento.py::situacao_da_ordem` na branch dela: a ordem é *Depois* enquanto alguma Etapa
  que a ordem lê (enumerada ou de desempate) não está *feita* no Perfil, e só é *Pendente* quando todas
  estão feitas — todo participante do Perfil consolidado, ou ninguém participando. Feitas as
  enumeradas, ou todo inscrito do recorte tem Resultado, ou o universo é vazio; nos dois casos esta
  regra aceita. Logo a `127` nunca diz *Pendente* para o que a `128` recusa. O inverso não vale, e não
  precisa: a `127` diz *Depois* também para a ordem parcial, que esta regra aceita. **Quando a `127`
  for mergeada, falta o teste de coerência**, que fica registrado como pendência (T015).

## A captura antes e depois (SC-1302, UX-261)

Cenário montado pelos helpers dos testes (`montar_cenario_do_corte(pontuacoes=())` mais onze
inscrições: doze, como o Edital 91), num banco de teste descartável, com o `live_server` e o Playwright,
entrando como gestor pelo seletor de identidade. "Antes" rodou numa worktree descartável no commit da
`126` (`262cf30f`), com a mesma fixture.

| Arquivo | O que mostra |
|---|---|
| `capturas/ordem-sem-resultado-antes.jpg` | a tela oferece "Emitir ordem"; o aviso do topo diz "é aqui que ele se emite" |
| `capturas/confirmacao-sem-resultado-antes.jpg` | a confirmação da `126`: "Nenhuma inscrição deste recorte tem resultado…", com "Emitir a ordem" |
| `capturas/ordem-sem-resultado-depois.jpg` | no lugar do formulário, "A ordem ainda não pode ser emitida", a frase e "Distribuir Prova didática"; o aviso do topo sem "é aqui que ele se emite" |

Nenhuma violação de CSP no console nas duas rodadas.

**Achado da captura**, corrigido aqui: o aviso do topo da tela ("Ainda não existe ato emitido para
este recorte, e é aqui que ele se emite") contradizia o bloco novo. No caso recusado ele perde a
segunda oração; o teste da tela o prende.

## Revisão independente

Um subagente que não escreveu o código leu `git diff 262cf30f` contra a spec, somente leitura.

**Conferiu e achou correto**: a posição da recusa em `emitir_ordem` (depois da repetição e da recusa do
sorteio, sobre o cálculo que se grava, antes do vigente, da assinatura e do motivo); que a recusa não
grava nada e não prende a chave de idempotência; que "chave da Etapa em `pontuacoes`" equivale a
"Resultado vigente de Etapa enumerada" (o superado não entra, a porta e a Ocorrência entram, o
desempate não enumerado não conta, o recorte é aplicado); que as quatro leituras usam a mesma função;
a tela (sem formulário nem sucessão, sem pedido a quem não gere, o link com a mesma base que a
distribuição exige, a frase sem duplicação, sem estilo nem script em linha); a refatoração de `pontuar`
sem mudança de comportamento; e que o `seed_demo` consolida antes de emitir.

| # | Achado | Severidade | Desfecho |
|---|---|---|---|
| 1 | Uma Ocorrência na Etapa anterior acorda o portão da progressão antes de alguém ser habilitado; o universo fica vazio e a ordem sai como "ninguém concorreu" | média | **registrado como decisão do usuário** (*P-1* na spec): segue a letra da opção b e não é criado por esta spec |
| 2 | Recorte reservado sem ordem própria e sem resultado: o aviso "emitir a ordem deste recorte é ato novo" vem antes do bloco | baixa | mantido: o aviso diz o que é a ordem do recorte, e não a oferece; o bloco logo abaixo diz que ainda não se emite |
| 3 | Com ordem do acervo, o título "A ordem ainda não pode ser emitida" fica abaixo de "Ato vigente emitido em…" | baixa | **corrigido**: "A ordem vigente ainda não pode ser sucedida"; teste |
| 4 | Faltavam testes de integração do recorte reservado, da porta consolidada e do Resultado superado; e esta verificação | baixa | **recorte reservado: teste novo**. A porta e o superado ficam provados pela regra (unitários) e pela leitura de `calcular_ordem`, que lê `ResultadoEtapa.vigentes`; montar uma Etapa decisória e um recurso deferido só para isso não acrescentaria garantia ao critério, que é o mesmo |
| 5 | Em `com_dois_marcos`, avaliar a primeira Etapa antes do ato final muda mais de uma variável | baixa | **corrigido**: a avaliação vem depois do ato final |
| 6 | O ramo "nenhuma com resultado" da confirmação da `126` não é mais alcançável; no marco só de portas, os sem Resultado ficam com posição e agora contam como "nenhuma" | baixa | mantido: o ramo é defensivo, e diz a verdade se for alcançado; no marco só de portas, a contagem nova é a da regra decidida (nenhum Resultado em nenhuma Etapa enumerada) |

## Pendências

- **A decisão P-1** (o universo esvaziado pelo portão da progressão), com o usuário.

- O teste de coerência com a `127`, quando ela estiver na `main` (T015).
- Trocar *Falta* por *Depois* na célula da ordem da condução continua P3 (fora desta spec): a célula leva
  à tela, que agora explica.
