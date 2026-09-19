# Phase 0 — Pesquisa e medição · 036 · Instrução do recurso

**Método**: leitura dirigida e varredura de `backend/`, em 19/09/2026, contra a `main` `dd71d46`.
Cada afirmação tem o arquivo, a função ou o teste em que foi conferida.

> **Esta feature concede acesso a dado pessoal.** É a primeira da série que o faz, e por isso o Phase
> 0 gastou o esforço em três perguntas que, se respondidas errado, sairiam caro: *o que exatamente a
> `FR-105` proíbe*, *a auditoria sabe registrar leitura*, e *quem já pode o quê*.
>
> **As três respostas encolhem ou precisam a feature. Nenhuma a aumenta.**

---

## R-1 — A `FR-105` da `018`: o que ela proíbe, e o que não proíbe

Ela tem **duas cláusulas**, e só a segunda governa esta feature:

> *"Respostas com Resultado individual, fundamentação ou decisão MUST NOT ser armazenáveis pelo
> navegador **e MUST NOT ampliar o acesso a documentos do candidato**."*

**O que ela proíbe**: que as superfícies do recurso sirvam de porta lateral para os documentos do
candidato. É isto que torna *"dar mais acesso ao papel de julgar"* uma violação — e é por isso que a
melhoria 13.2 propõe um **ato**, e não uma permissão.

**O que ela NÃO proíbe**: mostrar a alguém o que aquela pessoa já tem direito de ver. Ela fala de
**ampliar**, não de **exibir**.

### A doutrina que a acompanha, e que a feature precisa respeitar

`tests/portal/test_recurso_privacidade.py` prende as bordas com **sete casos**, e o cabeçalho do
arquivo declara a regra em três círculos:

| Quem | Lê |
|---|---|
| o titular | o próprio recurso, no portal |
| o julgador | a peça que vai julgar, na gestão |
| a auditoria | a trilha — *"que registra que houve ato, e não o conteúdo dele"* |

**O terceiro círculo é o que mais importa aqui.** O caso
`test_a_trilha_registra_o_ato_e_nao_o_conteudo` afirma que a fundamentação **não** aparece na trilha,
e explica: *"copiar a fundamentação para a trilha criaria uma segunda cópia do conteúdo sensível, num
lugar com outro regime de acesso e outro tempo de retenção."*

**Consequência para a `FR-533` e a `FR-534`**: o registro diz **que houve** e **qual o alcance** —
nunca o conteúdo do parecer.

---

## R-2 — A auditoria **já registra leitura**, e há padrão a seguir

Esta era a pergunta que podia dobrar o tamanho da feature. **A resposta é não.**

`record_event` é construído para ato que muda estado — recebe agregado, estado anterior e novo,
revisões. Mas a **`031`** o usa para registrar uma **leitura** de dado pessoal:

| | Como a `031` faz |
|---|---|
| operação | `MATRICULA_PREVER` |
| agregado | o Edital |
| revisão nova | **`None`** — nada mudou de estado |
| razão | *"prévia de exportação: {população}; {N} linha(s)"* |

**É exatamente o padrão que a `FR-534` precisa**, e ele já convive com a doutrina do `R-1`: a razão
descreve **o escopo do que foi visto**, e não o conteúdo.

**Decisão**: a `036` segue este padrão. **Alternativa descartada**: criar um registro de acesso
próprio, com outro modelo e outro regime — seria a segunda cópia com outro tempo de retenção que o
`R-1` nomeia como o erro a evitar.

---

## R-3 — O parecer **já está em memória** na tela de quem julga

`interface/views.py::_peca_para_julgar` monta a peça com
`select_related("resultado_atacado", "resultado_atacado__avaliacao", …)`.

**A avaliação que produziu o resultado atacado — e portanto o `parecer` dela — já está carregada.**
O que falta na tela de quem só julga **não é consulta: é autorização**.

E a mesma função já traz o Processo no `select_related`, com o comentário dizendo por quê: *"a tela
pergunta pela presidência dele para decidir quais caminhos oferecer."* A tela **já sabe** quem
preside.

**Consequência**: a `US2` é menor do que parece, e há um teste de orçamento de consulta —
`test_a_tela_do_recurso_nao_faz_uma_consulta_por_ato` — que a feature **não pode quebrar**. Exibir o
que já está carregado não o quebra; buscar de novo, sim.

---

## R-4 — O candidato **já lê um motivo**. O que falta é o parecer.

A tela de acompanhamento exibe, para cada Etapa, `etapa.motivo` — e o comentário do template diz o
que ele é:

> *"O motivo é escrito para ser lido — 'pontuação inferior à nota mínima da Etapa (45,0000 <
> 60,0000)' —, e é obrigatório por constraint desde a `013`. Antes desta feature ninguém o lia."*

**A pessoa não está no escuro absoluto.** Ela lê a **regra aplicada**. O que ela não lê é o
**parecer** — o que o avaliador escreveu, que é onde está *"o currículo não comprova os seis meses"*.

| | O que é | Quem escreve |
|---|---|---|
| **motivo** | a regra aplicada ao número | a máquina, a partir da norma |
| **parecer** | a razão da avaliação | a pessoa que avaliou |

**Esta distinção precisa estar na spec.** Sem ela, a primeira revisão pergunta *"mas já não há um
motivo?"* — e a resposta é sim, e ele não substitui o outro.

---

## R-5 — O template diz *"nenhum parecer"*, e a frase fala de **terceiro**

O comentário do bloco do acompanhamento declara:

> *"Nada aqui é de terceiro: nenhum nome, nenhuma nota alheia, nenhum parecer, nenhuma avaliação."*

**O sujeito da frase é *de terceiro***, e é isso que ela proíbe. O parecer **do próprio titular**
não é dado de terceiro — mas a frase, lida rápido, diz o contrário.

**Emendar esse comentário é trabalho desta feature**, e não detalhe: ele é a regra escrita no lugar
onde alguém a lê antes de mexer. A emenda precisa dizer a distinção, não apagar a proibição.

---

## R-6 — A superfície de teste que muda é **um** caso

`tests/interface/test_proveniencia_do_recurso.py` prende o alcance atual com três casos vizinhos:

| Caso | Depois da `036` |
|---|---|
| `test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta` | **muda** — passa a alcançar o que foi instruído |
| `test_quem_audita_alcanca_o_resultado_e_a_avaliacao` | permanece |
| `test_quem_consulta_inscricoes_alcanca_os_documentos` | permanece |

E `test_a_tela_do_recurso_nao_faz_uma_consulta_por_ato` **permanece, e é rede**: a `US2` acrescenta o
que exibir, e exibir o que já está carregado não custa consulta.

**Um caso muda, em um arquivo.** A `034` previu oito e entregou doze porque um código vivia num
dicionário compartilhado; aqui a varredura não encontrou compartilhamento equivalente — mas a
contagem MUST ser refeita contra a implementação, que foi como a `034` descobriu a diferença.

---

## R-7 — Quem instrui: a autoridade **já tem expressão no produto**

| Pergunta | Medido |
|---|---|
| Quem julga | `recurso:julgar`, exigido na porta da peça |
| Quem preside | `pode_gerir_comissao`, já consultado pela mesma tela |
| Como o produto expressa "gestão **ou** presidência" | `require_authorization_base`, criado pela `033`, com as bases nomeadas |

**A `FR-530` — nenhuma capacidade nova — é cumprível sem inventar nada**: a autoridade que instrui é
a mesma base composta que a `033` já sabe exigir e explicar quando falta.

---

## R-8 — O padrão de ato append-only, nomeado pelo próprio código

`ConclusaoAvaliacao` declara: *"Append-only, como `AtoAdministrativo` e `VersaoConsolidada`. Existe
porque reabrir **não pode destruir** o que foi concluído."*

É o padrão que a instrução segue, e é também a resposta ao `R-9`: quando há reabertura, o que o ato
citou continua consultável.

---

## R-9 — O Resultado aponta para **uma** avaliação

`resultados/models.py`: `avaliacao = OneToOneField(Avaliacao, …)`, com o comentário *"`OneToOne`
porque uma Avaliação fundamenta no máximo um Resultado"*.

**Confirma a `D-002`**: o parecer que responde pelo resultado é o daquela avaliação. O outro registro
de parecer, em `ConclusaoAvaliacao`, é **histórico de reaberturas** — e é a fonte quando o resultado
contestado antecede uma reabertura (`FR-523`).

---

## Resumo, e o que ele muda

| | Medição | Efeito na feature |
|---|---|---|
| R-1 | a `FR-105` proíbe **ampliar**, não **exibir**; a trilha registra ato, não conteúdo | o desenho da spec está certo |
| **R-2** | **a auditoria já registra leitura, com padrão da `031`** | **a `FR-534` deixa de ser mecanismo novo** |
| **R-3** | **o parecer já está carregado na tela de quem julga** | **a `US2` encolhe: falta autorização, não consulta** |
| **R-4** | **o candidato já lê um motivo** | **a spec precisa distinguir motivo de parecer** |
| R-5 | o comentário do template diz "nenhum parecer", falando de terceiro | emendá-lo é trabalho, e precisa dizer a distinção |
| R-6 | **um** caso de teste muda | recontar contra a implementação |
| R-7 | a base composta da `033` já expressa a autoridade | `FR-530` cumprível sem inventar |
| R-8 | há padrão append-only nomeado | a instrução o segue |
| R-9 | o Resultado aponta para uma avaliação | confirma a `D-002` |

**Nenhuma medição contradiz a spec.** Duas a encolhem, uma pede um parágrafo novo — o do `R-4` —, e
nenhuma reabre decisão tomada.
