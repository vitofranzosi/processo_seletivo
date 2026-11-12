# Verificação: cenários de treinamento e homologação

**Spec**: [spec.md](spec.md) · 08/11/2026, worktree `gps-training-staging-scenarios-bc947c`,
sobre a `main` em `86cd0ee0`.

## Testes da feature

`tests/unit/treinamento/` e `tests/integration/treinamento/`, contra PostgreSQL: **63 casos**,
depois da revisão de código.

| O que se prova | Onde | Requisitos |
|---|---|---|
| As três barreiras, para os quatro comandos, sem gravar nada | `test_ambiente.py` | FR-4601, FR-4602, FR-4604, FR-4605 |
| Pré-visualização com destino e plano; sorteio recusado sem a fonte | `test_ambiente.py` | FR-4604, FR-4643 |
| Sem autoridade vigente, recusa sem criar; nunca usada, só com `--autoridade` | `test_ambiente.py`, `test_carga_e_restauracao.py` | FR-4615, FR-4616 |
| Carga sobre o banco do `seed_demo` sem alterar **nenhuma** linha, em **todas** as tabelas | `test_carga_e_restauracao.py` | SC-1451, FR-4611 |
| A segunda carga não grava nenhuma linha | idem | SC-1452, FR-4611 |
| Sorteio feito **pela tela** no C07; o C04 continua intacto; a carga não desfaz o exercício | idem | SC-1453, FR-4617 |
| Restaurar sem `--confirmar` (ou com outro código) não muda nada; com ele, só mudam o Processo, o Edital e o manifesto da rodada anterior; a rodada nova sorteia de novo | idem | SC-1454, FR-4620 a FR-4626 |
| Falha no meio de um cenário não deixa rastro e não impede os outros | idem | FR-4612 |
| Processo com código reservado e sem manifesto: relatado, intocado, restauração recusada | idem | FR-4614 |
| Propriedade que não se comprova bloqueia a restauração | idem | FR-4613, FR-4622 |
| Os quinze juntos, cada um no seu Processo | idem | FR-4650, FR-4651 |
| A próxima ação de cada um dos quinze, executada pelo ator da ficha; e recusada a quem a ficha não nomeia | `test_proxima_acao.py` | SC-1455, FR-4655, FR-4642 |
| CPF válido iniciado por 000, nomes e e-mails fictícios, PDF válido e marcado, atores sem permissão além do papel | `tests/unit/treinamento/` | FR-4630 a FR-4633, FR-4642 |
| A chave nasce desligada e produção recusa subir com ela | `tests/test_configuracao_producao.py` | FR-4601 |

O C04 confere a ordem emitida: os candidatos 01 e 02, empatados no total, saem em 1º e 2º pelo
desempate da prova; 03 e 04 dividem o 3º lugar; 08, eliminado na prova, fica fora da ordem.

## Achados da própria verificação

1. **A carga congelava uma autoridade da unidade.** O instantâneo linha a linha acusou a autoridade
   da suíte alterada: a primeira publicação com uma autoridade grava `usada_em`, e a partir dali o
   cadastro dela é imutável. Corrigido pela FR-4616.
2. **Os atores do gerador tomavam as sugestões da página de acesso.** Visto no navegador:
   "Elaborador como treino.elaboracao". `treino.` passou a ser sujeito fora da equipe, como `cand:`.
3. **Conforme exige abertura registrada pela tela** — o C12 deixou de nascer com item conforme
   (D-007).
4. **O mesmo arquivo reenviado não conta como entrega nova** — o roteiro de correção do C11 usa
   um arquivo diferente.

## Achados da revisão de código (09/11)

Dez, todos corrigidos, cada um com o seu caso na suíte:

1. **Os identificadores não levavam a unidade.** Perfis, Etapas, pessoas e concurso são globais
   no banco, e o `--unidade` de uma segunda unidade falhava em todos os cenários. A unidade entrou
   na derivação (FR-4630, FR-4643); o caso carrega o C04 e o C07 no Cefor e numa segunda unidade.
2. **Os Editais a cancelar eram lidos fora da transação.** Um Edital criado depois da
   pré-visualização fazia o cancelamento do Processo recusar a restauração inteira. Agora são
   relidos sob trava, e o plano vencido por outra restauração é recusado sem mudar nada (FR-4624).
3. **O CPF usava a rodada módulo 10**, e a rodada 11 repetia os da 1 (FR-4631).
4. **A procura de vestígios ia só até a R99.**
5. **Defeito do gerador saía como recusa do domínio**, sem pilha: agora é `ERRO` (FR-4612).
6. **O ano do Edital era o do UTC**, e a noite de 31/12 datava o Edital do ano seguinte.
7. A pré-visualização calculava o retrato de cada cenário pronto só para dizer `MANTER`.
8. O plano da restauração era calculado duas vezes, pelo comando e pelo serviço.
9. Uma montagem incompleta era construída só para obter o código, o número e o ator.
10. Duas citações de requisito estavam trocadas (listagem → FR-4654, retrato → FR-4617).

## No navegador

Banco `ps_demo_134`, com o `seed_demo` no papel de dados preexistentes, e os quinze cenários
carregados pelo comando (entrada `cenarios-134` do `.claude/launch.json`):

- a carga dos quinze levou **8 segundos**; a segunda carga, `MANTER` em todos;
- a página de acesso lista `treino.presidencia` e `treino.avaliacao1` em **Comissões**, com os
  Processos de cada uma;
- o Edital `SIM04/2026` mostra uma só providência: **SUA — Emitir a ordem**;
- o Edital `SIM07/2026` mostra **SUA — Observar a extração**; na tela do sorteio, a fonte é a
  **Fonte de demonstração** e o concurso da rodada diz "cenário de treinamento, sem valor legal";
  **Observar a ocorrência** e **Realizar o sorteio** funcionaram, e a tela passou a mostrar
  "Sorteio realizado … por treino.presidencia" com semente e manifesto;
- a verificação acusou o C07 como `EXERCITADO` (ato de ordenação, 10 posições, sorteio) e o C04
  como `INTACTO`; a restauração criou `SIM-TREINAMENTO-007-R2`, e a rodada 1 foi para
  **Cancelados**;
- os documentos do convocado 02 do C11 mostram o diploma **Pendente** e a residência **A
  apresentar**; o PDF fictício é servido íntegro, com a marca de treinamento.

- depois das correções, a página de acesso voltou a sugerir a equipe ("Elaborador como
  ana.elaboradora"), e o Edital de sorteio restaurado (`SIM07R3`) deixou de declarar as duas Etapas
  do molde que nenhum ato usa. Continua a providência de distribuir a "Análise de títulos", que é a
  Etapa enumerada pelo marco de sorteio do molde do `seed_demo`; o sorteio não depende dela, e o
  guia a anota como observação para o exercício.

## Suíte completa

`make test-pg` com `DB_NAME=ps_treino_wt`, 4 workers, antes das três correções finais:
**17 417 passando, 20 pulados, 1 falha, em 758 s**. A falha é
`tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`,
o teste de tempo que o `AGENTS.md` registra como oscilante sob carga — a suíte rodou ao lado do
servidor de demonstração e da carga dos cenários. Isolado, passou três vezes em três; esta feature
não toca a ocupação.

Depois das correções finais (sugestões da página de acesso, travessão do PDF, Etapas do Edital de
sorteio): `ruff check`, `ruff format --check`, `manage.py check` e `makemigrations --check` limpos,
e os 108 casos afetados — a feature, a entrada da gestão, o `seed_demo`, as citações, o README e a
configuração de produção — passando.

Depois da revisão de código de 09/11, a suíte completa (`make test-pg`, 4 workers): **17 427
passando, 20 pulados, sem falha, em 1389 s**.

## Sorteio com cota (09/11)

Pedido do setor depois da carga na homologação (FR-4656, D-008). No banco `ps_demo_134`, o C06 e o
C07 restaurados com o catálogo novo:

- o C06 oferece **Publicar e congelar a relação** nas duas listas — "Todos os inscritos" e
  "Pessoas pretas, pardas e indígenas (PPP)";
- o C07 nasce com as duas relações congeladas, 10 e 3 participantes, os três cotistas com número
  próprio em cada uma;
- **Observar a ocorrência** uma vez, e **Realizar o sorteio** nas duas listas, pela tela: a mesma
  semente, manifestos diferentes, cada um com o seu "Verificar no canal público".

Os casos do C06 e do C07 em `test_proxima_acao.py` e o sorteio pela tela de
`test_carga_e_restauracao.py` passaram a exigir as duas relações e os dois sorteios.

Suíte completa (`make check test-pg`, 4 workers): **17 474 passando, 20 pulados, sem falha, em
774 s**.

## Provisionamento da formalização (12/11)

Revisão da FR-4615 por decisão do usuário (FR-6720 a FR-6729). No banco novo `ps_treino_nav`
(`make preparar`, uma autoridade cadastrada pelo comando do Gestor, nenhum outro dado), a carga do
C16 e do C17 com `--autoridade`:

- a pré-visualização disse `pessoa treino.formalizacao: criar; papel Formalização em cefor:
  conceder` nos dois, e a carga criou os dois em 1 pessoa e 1 vínculo;
- **entrar como o setor:** página de acesso → *Opções avançadas de demonstração* → *Nome na
  auditoria* `treino.formalizacao`, *Formalização* marcada. A lista do setor trouxe **só o
  `SIM16/2026`**, com *Todos os Perfis*; o `SIM17` não aparece, porque nele a pessoa não está
  designada;
- **exportar:** *Verificar e exportar todos os aptos (3)* → *Pacote completo: 3 de 3 pessoas
  incluídas · 3 documentos · 2 KB* → *Baixar pacote*: 200, e uma exportação registrada por
  `treino.formalizacao`;
- **o Centro como Gestor**, fase Conclusão: no `SIM16`, *Feito · Quem recebe: 1 pessoa designada* e
  *Feito · Pessoas disponibilizadas: 3 de 3*, e nenhuma ocorrência de "ninguém designado" — o N-03
  da reavaliação sumiu; no `SIM17`, *Em aberto · Quem recebe: ninguém designado (quem administra os
  acessos da unidade)* e a providência *designar quem recebe os documentos*, sem o "antes, é preciso
  conceder o papel" da FR-6113 da `153`, porque a pessoa já está habilitada.

O exercício de **designar** não foi feito pela tela: o seletor não oferece o Administrador de
acessos (ver *Limitações* na spec). A suíte o faz pelo comando, com `treino.acessos`, e confere que a
presidência é recusada.

`tests/integration/treinamento/test_formalizacao_nos_cenarios.py`: a exportação pela tela e o
Centro no C16 (SC-2210), a lista do setor e o Centro no C17 (SC-2211), as contagens de pessoa e
vínculo na carga, na segunda carga e na restauração (SC-2212), a pessoa inativa que não é reativada,
e a restauração do C16 que revoga a designação anterior (FR-6726).

Suíte completa (`make lint check test-pg`, 4 workers, sem o grupo `navegador`): **19 031
passando, 23 pulados, sem falha, em 908 s**.

**Depois da revisão do #500** (achados 1, 3 a 7; o 2 espera a revisão da `117`): a restauração
revoga as designações de todos os Editais do Processo, também do encerrado e em qualquer cenário,
e a pré-visualização as conta; a pessoa suspensa com vínculo é recusada com `pessoa_indisponivel`;
a pré-visualização do C16 e do C17 juntos diz que o C17 recebe a pessoa e o papel do cenário
anterior. Num segundo banco novo (`ps_treino_nav2`), o mesmo percurso no navegador deu o mesmo
resultado. Suíte completa: **19 033 passando, 23 pulados, sem falha, em 1396 s** (com outras
suítes no mesmo cluster).

**Depois do merge da revisão da `117` (12/11):** no banco novo `ps_treino_nav3`, com o C17, a
presidência (`treino.presidencia`, pelo grupo Comissões) chega pelo Centro a *Designar quem recebe
os documentos*, e a lista oferece **só** *Formalização Treinamento*. Ao designar, a tela recusa:
*"Esta pessoa não está disponível para receber acesso: está suspensa ou desativada, ou o
identificador não é de pessoa institucional."* — a tela resolve a pessoa por
`pessoa_institucional`, que exige o prefixo `pessoa-`. O comando aceita a designação (a suíte o
prova); a tela, não. Conflito registrado nas limitações da spec, à espera de decisão.
Suíte completa depois do merge da main (`make lint check test-pg`, 4 workers): **19 109 passando,
23 pulados, sem falha, em 582 s**.

**Observação, sem mudança:** o *O que fazer agora* do `SIM16` também mostra a classificação da lista
PPP, em que ninguém concorreu, e o resultado definitivo à espera do prazo recursal. É o estado da
cadeia de notas que o C10 a C12 já percorrem, e não é da formalização.

## Pendente

- **SC-1456 (humana):** uma pessoa da comissão percorrer um cenário só com o guia.
- **A carga na homologação compartilhada** é do administrador, depois do backup e do ensaio do
  [manual](../../doc/cenarios-de-treinamento/manual-de-operacao.md). Nada foi carregado lá.
- **O exercício de designar pela demonstração** (C17) depende da revisão da `117` que dá a designação
  à presidência, em curso em 12/11; até lá, é de quem tem o Administrador de acessos pela entrada
  institucional.
