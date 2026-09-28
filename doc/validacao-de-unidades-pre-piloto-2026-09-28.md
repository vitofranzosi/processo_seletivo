# Validação de unidades da auditoria de consolidação — antes do piloto

**28/09/2026.** Sete unidades da matriz da §3 de
[`auditoria-de-consolidacao-2026-09-26.md`](auditoria-de-consolidacao-2026-09-26.md) conferidas
contra a `main` (`d65f0136`): cinco de validação — RC-08, RC-112, RC-46, RC-63 e RC-86 — e duas de
higiene — RC-103 e RC-127. A auditoria não foi editada; o estado de cada unidade está aqui.

A regra foi a de sempre: defeito confirmado **com requisito escrito** é corrigido no mesmo PR, com
teste que falha sem a correção; defeito sem requisito, ou que pede decisão, fica registrado e não é
corrigido. Nenhuma spec nova e nenhum requisito novo.

| RC | Veredito | O que foi feito |
|---|---|---|
| RC-08 | **confirmado defeito**, contra a `FR-020` da `002` | corrigido |
| RC-112 | **confirmado defeito**, e pede decisão | registrado aqui, não corrigido |
| RC-46 | **não se reproduz** com inscrição criada pelo portal | resíduo latente registrado |
| RC-63 | **não se reproduz** — a reavaliação se cumpre pelas telas | a mensagem da recusa corrigida (`FR-111` da `018`); lacunas de orientação registradas |
| RC-86 | **medido**: linear, sem termo superlinear | registrado; otimizar é decisão |
| RC-103 | higiene | texto e teste feitos; o que muda comportamento ficou para decisão |
| RC-127 | higiene | testes e texto feitos; `D4` fica para decisão |

---

## RC-08 — restaurar o rascunho local perdia as coleções aninhadas

**Como foi reproduzido.** Pela tela, no Edital em elaboração do `seed_demo` (etapa Perfis de Vaga):
alterado o percentual de uma Modalidade e a denominação de um Perfil, recarregada a página sem
enviar, e clicado *"Restaurar o que eu havia digitado"*. Antes: 3 Modalidades no formulário. Depois:
**0**. O botão *"Acrescentar Modalidade"* da lista restaurada ficou inerte (o HTML não passou pelo
htmx), e o rascunho guardado foi regravado já sem Modalidade nenhuma — a perda deixava de ser
recuperável.

**A causa** era a descrita em 15/09 (`AX-16`): a restauração pedia o fragmento **vazio** de cada linha
ao servidor e preenchia só os campos de três segmentos (`perfil-3-code`). Os de quatro
(`modalidade-0-7-code`) — Modalidades, linhas do quadro, fatos — caíam no balaio dos campos simples e
eram procurados por um nome que a linha recriada já não tinha.

**A correção** (`interface/static/interface/rascunho.js`) guarda a lista como estava — o HTML dela e o
valor de cada campo pelo nome exato — e a restaura inteira, passando-a pelo htmx. Não há regra de
reconstrução por tipo de linha, e por isso a mesma correção cobre Perfis, Etapas, Documentos e
Cronograma. A comparação que decide se há o que oferecer continua sendo a canônica. O registro na
forma anterior, sem a cópia da lista, é descartado em vez de oferecido: restaurá-lo repetiria a
perda. O atributo `data-fragmento`, que só a restauração antiga lia, saiu dos quatro formulários.

**A prova.** Cinco testes novos em `tests/javascript/rascunho.test.js` — a Modalidade acrescentada
volta com o que foi digitado, o rádio volta na opção escolhida, a lista passa pelo htmx, o autosave
seguinte guarda a Modalidade, e o registro antigo é descartado — **falham os cinco** contra o script
da `main` e passam com a correção. E pela tela: restaurado o preenchimento, as 4 Modalidades
voltaram (inclusive a acrescentada no cliente, com código e denominação), o 25 digitado voltou,
*"Acrescentar Modalidade"* funcionou, e *"Salvar rascunho"* gravou no servidor `PPP 25.0000` e a
Modalidade restaurada; o recibo apagou a cópia local.

**Observado no percurso, fora do escopo.** Acrescentar a **primeira** Modalidade de lista reservada a
um Perfil que só tinha a ampla deixou dois campos `linha-1-0-*` no formulário (visto no pedido do
fragmento do quadro, antes de qualquer restauração). A gravação seguinte funcionou e o quadro saiu
certo, de modo que o efeito observado é nenhum; a causa não foi investigada. Fica registrado.

---

## RC-112 — a Ocorrência numa Etapa que nunca consolida trava a Etapa seguinte

**Confirmado.** Reproduzido por teste de integração contra PostgreSQL, em dois Editais de duas Etapas,
com três inscrições submetidas e a primeira Etapa de **leitura múltipla** (duas avaliações por
inscrição, sem regra de combinação):

```text
                                      participantes  eliminadas  aguardando
acervo, primeira Etapa eliminatória
  antes da Ocorrência                       3             0           0
  depois da Ocorrência de uma pessoa        0             1           2
  consolidar a primeira Etapa         recusa regra_de_combinacao_ausente
  ao fim                                    0             1           2

publicável hoje, primeira Etapa não eliminatória (a que a 046 publica com aviso)
  antes da Ocorrência                       3             0           0
  depois da Ocorrência de uma pessoa        0             1           2
  consolidar a primeira Etapa         recusa regra_de_combinacao_ausente
  ao fim                                    0             1           2
```

As duas pessoas que não faltaram ficam em *"aguardando a Etapa anterior"* para sempre: a exigência de
habilitação ligou com o primeiro Resultado (`resultados/application/prontidao.py:150-154`), e a Etapa
anterior não produz `HABILITADA` para ninguém. O segundo cenário é o que torna falsa a frase *"Nada
neste Edital depende dele"* com que a `046` publica a Etapa não exigida.

**Por que não foi corrigido.** O código segue a **letra** da Regra 2 da `D-003` da `013` — *"a partir
do primeiro Resultado da Etapa anterior, participa a inscrição que possua Resultado `HABILITADA`
nela"* —, e a Ocorrência é Resultado. O que ele contraria é o **propósito** escrito na mesma regra: o
gate existe para que *"Etapa anterior de leitura múltipla … não deixe a Etapa seguinte
permanentemente sem participantes"*. E a `046` (A-1) escolheu deixar o caso fora do gate de
publicação, como risco operacional. Corrigir é escolher entre leituras, e isso é do usuário:

1. o gate ignora Resultado por Ocorrência quando a Etapa anterior não pode consolidar — a Regra 2
   passa a ler "primeiro Resultado **de avaliação**";
2. o gate pergunta se a Etapa anterior **pode** produzir habilitação, e fica dormente se não pode;
3. a publicação passa a contar a precedência como consumidor (a `D-001` da `046`), e a Etapa
   inconsolidável que precede outra deixa de ser publicável;
4. a Ocorrência é recusada em Etapa que não consolida — o que contraria a I-1 do briefing da
   Ocorrência (`resultados/application/ocorrencia.py:14-20`).

O teste de reprodução não entrou no PR: prender o comportamento atual seria prender o defeito.

---

## RC-46 — a entrada no portal não chegava à confirmação de CPF

**Não se reproduz com inscrição criada pelo portal.** Percorrido pelas views reais do portal (cliente
HTTP, código lido da caixa de saída): entrar com o e-mail, informar nome e CPF, abrir a inscrição,
sair, entrar de novo com o mesmo e-mail.

```text
1ª entrada -> /selecoes/meus-dados
inscrição criada pelo portal; identidade existe: True
2ª entrada -> /selecoes/inscricoes/
área mostra a inscrição: True | oferece "Vincular": False | identidades: 1
```

A inscrição feita pelo portal nasce da identidade que acabou de provar o e-mail
(`inscricoes/application/rascunho.py`), e a segunda entrada cai direto nela — não há o que
reconciliar. A reconciliação por CPF propriamente dita (participação anterior sob outra identidade)
já é percorrida ponta a ponta em `tests/acceptance/portal/test_reencontrar_participacao.py`,
inclusive a retomada depois de recusar o convite.

**De onde veio o laço de 13/09.** O relatório da `019` usou inscrições do `seed_demo`, que as cria
com `identity_subject` sem identidade de candidato (`cand:sorteio-…`). Com esse dado o laço se
reproduz:

```text
1ª entrada -> /selecoes/inscricoes/  (área vazia; oferece "Vincular")
volta 1: código aceito -> /selecoes/inscricoes/ | oferece "Vincular" de novo: True
volta 2: código aceito -> /selecoes/inscricoes/ | oferece "Vincular" de novo: True
```

O convite (`associacao.credencial_com_correspondencia`) conta qualquer inscrição com aquele e-mail,
e a retomada (`associacao.correspondencia_historica`) só aceita as que têm identidade — as outras
somem em silêncio, e o convite volta.

**Resíduo latente, registrado e não corrigido.** Fora do `seed_demo`, a mesma forma de dado existe
por desenho: as inscrições dos conjuntos que a implantação da `010` não reconcilia (`FR-044`,
`FR-045`) ficam *"inalcançáveis pela área pessoal até tratamento operacional"* (`FR-047`). Para quem
provar um desses e-mails, a área oferece *"Vincular participação anterior"* e o clique não chega a
lugar nenhum. Não é beco sem saída — a pessoa continua com sessão e área (`P-009`) —, e nenhum
requisito diz o que o convite deve fazer nesse caso. Num piloto que começa sem dado da `009` o caso
não aparece. Se valer corrigir: o convite passar a exigir identidade do outro lado, como a retomada
já exige.

---

## RC-63 — a reavaliação determinada seria inexequível

**Não se reproduz.** Percorrido pelas views da gestão, cada passo com o papel de quem o pratica:

1. quem julga determina a reavaliação pela tela do recurso;
2. a organização da Etapa mostra a linha como *"reavaliação determinada por recurso, ainda não
   cumprida"*, e não como consolidada;
3. a distribuição aceita uma avaliadora **diferente** da que concluiu a original, apesar de o teto da
   Etapa estar ocupado (a vaga extra de `avaliacoes/application/distribuicao.py`);
4. ela conclui pela Mesa;
5. a consolidação — pela seleção, com a conferência de dois passos, que diz *"Habilitada em
   cumprimento de decisão"* — cria o Resultado sucessor com `resultado_anterior` e `decisao`;
6. antes do passo 5 a porta da definitiva recusa com `publication_reassessment_pending`; depois, a
   reavaliação deixa de barrar, e com o ato sucessor emitido a definitiva é publicável.

O percurso de 07/09 tentou só a **reabertura** da avaliação original, que é recusada por regra
(`FR-111`) e não é o caminho. O teste `tests/interface/test_reavaliacao_pelas_telas.py` fica no PR
com os passos 1 a 5 — era o que a auditoria apontava faltar: nenhum teste de interface percorria o
caminho.

**Corrigido: a mensagem da recusa.** A `FR-111` manda a recusa *"nomear o ato que existe"*. Com a
reavaliação determinada, a frase geral mandava ao *"julgamento de recurso"* — o ato que já tinha
acontecido e que determinou reavaliar. Foi ela que levou o percurso de 07/09 ao diagnóstico errado.
Agora, havendo reavaliação pendente para o par, a recusa diz que o recurso já foi julgado e que a
reavaliação se cumpre distribuindo a outro avaliador e consolidando
(`avaliacoes/application/avaliacao.py`). O teste
`test_a_recusa_da_reabertura_nomeia_o_caminho_da_reavaliacao` falha contra a `main` e passa com a
correção. Sem reavaliação pendente, a frase é a de antes.

**Lacunas de orientação, registradas e não corrigidas** — nenhuma trava o caminho, e nenhum requisito
as cobre pela letra:

- a tela do recurso, depois da decisão, diz *"Sucessor — Nenhum — este recurso não produziu resultado
  sucessor"* e não indica o próximo passo;
- a organização da Etapa não conta a reavaliação em nenhum dos números da faixa (*"0 prontas · 0 não
  consolidáveis · 1 já consolidada"*, de 2 participantes) nem oferece o filtro dela — o filtro existe
  (`?prontidao=reavaliacao-determinada`) e só se alcança digitando;
- depois de concluída a nova avaliação, a linha continua *"ainda não cumprida"*, fora de *"Consolidar
  as prontas"*; o único caminho é marcá-la e *"Consolidar as selecionadas"*;
- a Mesa não diz à avaliadora que aquela é uma reavaliação;
- a coluna de avaliações mostra *"2 de 1"* depois da distribuição extra;
- a tela de conclusões preservadas oferece *"Reabrir"* para a avaliação original, que é sempre
  recusada.

O manual (`doc/manual/00-arquitetura-do-manual.md`, §H.2) ganhou nota datada: a espécie saiu do
fluxo principal por esse diagnóstico, e a decisão editorial precisa ser refeita.

---

## RC-86 — custo de consulta por Edital na página do Processo

**Medido**, contra PostgreSQL, num Processo com 1, 3, 10, 12 e 20 Editais publicados, cada um com
três inscrições submetidas. Consultas por requisição:

| Editais | Processo (gestor) | Supervisão (gestor) | Processo (presidência) |
|---:|---:|---:|---:|
| **uma Etapa por Edital** | | | |
| 1 | 21 | 18 | 24 |
| 3 | 42 | 39 | 45 |
| 10 | 112 | 109 | 115 |
| 12 | 132 | 129 | 135 |
| 20 | 212 | 209 | 215 |
| **três Etapas por Edital** | | | |
| 3 | 54 | 51 | 57 |
| 10 | 166 | 163 | 169 |
| 12 | 198 | 195 | 201 |
| 20 | 326 | 323 | 329 |

**Linear, sem termo superlinear:** cada Edital acrescenta ~7 consultas fixas mais 3 por Etapa (10
com uma Etapa, 16 com três), e o incremento é o mesmo de 3 para 20 Editais. Bate com os ~17 de 20/09,
que usaram Editais de mais Etapas. Nenhum requisito limita esse custo — o da visão institucional
(`SC-209` da `040`) é de outra página —, e o guardião existente só prende a invariância quanto ao
número de **inscrições**. Processos do Cefor com dezenas de Editais ficam em centenas de consultas
por leitura; otimizar é decisão, não defeito. A medição não entrou no PR.

---

## RC-103 — higiene de documentação, teste e ferramenta

| Item | Estado na `main` | Feito aqui |
|---|---|---|
| README: `31 de 31` | atrás (o código tem 34) | frase sem número fixo, com o que denuncia a falha |
| README: tabela de incrementos até a `025` | atrás | `026` a `048`, e o rótulo da `012-013`; guardião `tests/test_readme_acompanha_o_codigo.py` |
| README: tabela de módulos com 7 de 21 apps | atrás | os 21, no mesmo guardião |
| contagens da suíte (README, `Makefile`, `AGENTS.md`) | três números diferentes | README e `Makefile` apontam para o `AGENTS.md`, fonte única |
| manual atrás do código | `H.2`, `H.6`, `H.7`, `H.8` | notas datadas, sem reescrever o documento de 08/09 |
| teste CSRF instável | `test_adicionar_credencial.py` **e** `test_entrar_sem_senha.py` | o token é retirado antes de afirmar que a tela não pede CPF |
| guarda de citações aceita o `UX-062` | aberto | definição passa a ser o negrito que abre a linha; o `UX-062` fica como reserva nomeada; teste do padrão |
| docstring do portal nega o que o módulo faz | aberto | reescrita |
| testes com data em UTC | nenhum caso vivo | nada — a guarda da classe é decisão (`doc/achado-teste-com-data-em-utc.md`) |
| `Status: Draft` das specs | 46 de 49 errados | nada — a convenção é decisão do usuário |
| suíte em SQLite | aberto | nada além das contagens — `doc/achado-suite-em-sqlite.md` deixa a correção para decisão |
| `seed_demo --numero` | aberto | nada — muda o comando, e o achado deixa a escolha ao usuário |
| derivação duplicada de `pode_retificar` | três lugares | nada — trocar muda o que Edital encerrado ou cancelado mostra |
| grade dos cartões | aberto | nada — *"não é defeito, e não vira escopo"* |

O README ainda diz que *"o estado de cada incremento está na pasta dele"*, o que é falso enquanto o
`Status` das specs estiver errado. A frase depende da mesma decisão, e ficou.

---

## RC-127 — testes e textos que ficaram atrás do código

Nenhuma linha de produção mudou nesta unidade. Cada teste reforçado foi conferido **introduzindo o
defeito que ele guarda** no código, vendo-o falhar, e desfazendo a mutação.

| Item | Estado na `main` | Feito aqui | Falha com o defeito? |
|---|---|---|---|
| `D3` — "aguardando decisão" escrita em Python e em SQL | as duas sem nada que as prenda | teste de equivalência em `test_sinais.py`: peça admitida, recém-interposta, inadmitida e julgada; a contagem da ação, a situação da peça e o denominador do `UX-064` precisam coincidir em cada passo | sim — tirar qualquer um dos dois ramos do filtro SQL |
| `D3` — o teste do contador cobria dois dos quatro ramos | aberto | `test_hardening_pos_auditoria.py` passa por "(2)", "(1)" e "(0)", na lista e no cartão | sim, as mesmas duas mutações |
| `D7` — o cronograma normal conferia identificadores aposentados | aberto | afirma que o Edital novo não produz sinal nenhum | sim — um `UX-003` "0 de 0" passaria no teste antigo |
| `D7` — a unidade da medida fora da comparação | aberto | asserção explícita da unidade ao lado de cada comparação de `UX-003`, `UX-063` e `UX-064`; `tests/interface/test_forma_do_sinal.py` renderiza `_sinal.html` | sim — trocar a unidade, ou o template deixar de imprimi-la |
| `D7` — nenhuma eliminada no teste de equivalência | aberto | dois testes em `test_progressao_com_corte.py`, com eliminada antes e com todos eliminados; a fixture compartilhada ficou como estava; a matriz da `045` aponta para eles | sim — desligar a Regra 1; o teste antigo **passava** com ela desligada |
| `D5` (`046`) — a tabela-verdade da `SC-275` copiava a regra | aberto | `exigida` sai de uma tabela escrita à mão a partir dos consumidores; o cenário de habilitação próprio passou a ser publicável; o método comum, que nunca carrega Etapa de habilitação, virou teste separado; guarda contra cenário impossível | sim — tirar qualquer consumidor de `_quem_exige_o_resultado` |
| `D8` — textos da `022` contradizendo a `045` sem marca | aberto | marcas datadas de substituição: a nota da `D-002`, a clarificação do status do Evento, os cenários 1–2 da US3 e a `SC-009` | — |
| `D8` — `status` na fixture de supervisão | aberto | parâmetros sem chamador removidos; o que o pulso usa ficou, com a docstring certa | — |
| `D4` — a `SC-273` só vale para o `UX-003` | aberto | **nada** — fechar pede filtro novo nas telas de destino ou estreitar o critério, e as duas coisas são decisão | — |

**Dois achados do caminho, registrados:**

- a `FR-746` da `046` lista a *"Etapa de habilitação do método de sorteio comum ao Edital"* como
  consumidor, mas `validate_common_draw_method` recusa Etapa de habilitação no método comum — nenhum
  Edital publicável chega a esse ramo;
- o cenário de habilitação própria da tabela-verdade antiga era ele mesmo impublicável
  (`draw_method_invalid`), e o teste não percebia.
