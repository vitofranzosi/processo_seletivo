# Rastreabilidade — `036` · Instrução do recurso

**O que este arquivo responde**: onde cada requisito foi implementado e onde ele é prendido; quais
testes mudaram e por quê; e — porque esta é a **primeira feature da série que concede acesso a dado
pessoal** — quem passou a ver o quê, por quanto tempo, e o que ficou registrado.

O "antes" contra o qual tudo aqui se compara está em
[antes-da-instrucao.md](antes-da-instrucao.md), medido antes da primeira edição.

---

## 1. Requisitos funcionais

| Requisito | Onde foi implementado | Onde é prendido |
|---|---|---|
| **FR-522** | `recursos/application/selectors.py::pareceres_do_titular` — as duas condições, e a segunda por `resultado_atacado_id__in` | `test_parecer_do_titular.py::test_o_titular_le_o_parecer_do_proprio_resultado`, `…::test_com_o_prazo_fechado_e_a_peca_dele_em_curso_o_parecer_permanece`, `…::test_peca_contra_outro_resultado_nao_reabre_este_parecer` |
| **FR-523** | `recursos/application/selectors.py::parecer_que_fundamenta` — a `ConclusaoAvaliacao` preservada, e não o campo corrente | `test_parecer_do_titular.py::test_o_parecer_lido_e_o_da_conclusao_que_fundamenta_o_resultado` |
| **FR-524** | `POR_QUE_SAIU` e `POR_QUE_NAO_APARECE`, exibidos em `portal/acompanhamento.html` | `test_parecer_do_titular.py::test_com_as_duas_condicoes_encerradas_o_parecer_sai_e_a_tela_diz_por_que` |
| **FR-525** | `NAO_HOUVE_PARECER`, no mesmo bloco do template | `test_parecer_do_titular.py::test_sem_parecer_escrito_a_tela_diz_que_nao_ha` |
| **FR-525a** | `portal/acompanhamento.html` — o parecer **depois** do motivo, em moldura própria | `test_parecer_do_titular.py::test_o_parecer_vem_ao_lado_do_motivo_e_nao_no_lugar_dele` |
| **FR-526** | a porta do portal é a titularidade, e nada nesta feature a afrouxa | `test_parecer_do_titular.py::test_outro_candidato_nao_alcanca_o_parecer_alheio` |
| **FR-527** | `recursos/models.py::AtoDeInstrucao` e `recursos/application/instruir.py::instruir` | `test_alcance_da_instrucao.py::test_a_instrucao_abre_o_alcance_com_autor_e_instante` |
| **FR-528** | o alcance é **derivado** da relação `recurso → instrucoes`; não há lista de pessoas | `test_alcance_da_instrucao.py::test_instruir_uma_peca_nao_alcanca_outra_da_mesma_etapa`, `test_instrucao_na_peca.py::test_o_mesmo_julgador_em_outro_recurso_nao_alcanca_nada` |
| **FR-529** | `Alcance.aberto` pende de `encerrado(peca)` — **decisão de mérito ou juízo negativo**; `ato_alcancado` recusa depois dos dois | `test_alcance_da_instrucao.py::test_o_alcance_fecha_com_a_decisao_e_o_registro_permanece`, `…::test_o_alcance_fecha_com_a_inadmissao`, `…::test_depois_da_inadmissao_o_documento_nao_abre` |
| **FR-530** | a autorização é `pode_gerir_comissao` — a base composta que a `033` já exigia; nenhum papel e nenhuma permissão nova em `interface/identidade.py` | `test_alcance_da_instrucao.py::test_quem_so_julga_nao_instrui_e_a_recusa_nomeia_as_duas_bases`; e os dois vizinhos intactos em `test_proveniencia_do_recurso.py` |
| **FR-531** | `AtoDeInstrucao.documento` é `FK` para o documento original; `documento_instruido` serve os bytes dele. **Instruir documento exige `inscricao:consultar`** — a autoridade não anexa o que ela própria não abre | `test_alcance_da_instrucao.py::test_o_ato_alcanca_o_documento_por_referencia_e_nao_por_copia`, `…::test_quem_nao_consulta_inscricoes_nao_instrui_documento` |
| **FR-531a** | não há campo de arquivo no ato — não há onde uma cópia caber | `test_instrucao_na_peca.py::test_instruir_nao_duplica_arquivo_no_armazenamento`, `…::test_abrir_o_documento_instruido_tambem_nao_duplica` (conferido no **armazenamento**) |
| **FR-532** | `interface/views.py::_instrucao_da_peca` e os três ramos de `interface/recurso.html` | `test_instrucao_na_peca.py` — os três casos de estado, mais os quatro de "não oferecer o que não se alcança" |
| **FR-533** | `instruir.py::instruir` audita cada linha, com `motivo_do_ato` | `test_trilha_da_instrucao.py::test_o_ato_aparece_com_autor_instante_recurso_e_o_que_foi_anexado`, `…::test_o_ato_registra_qual_base_autorizou` |
| **FR-534** | `_instrucao_da_peca` (escopo, uma vez por leitura) e `documento_instruido` (por item) | `test_trilha_da_instrucao.py::test_o_acesso_a_tela_fica_registrado_com_o_escopo`, `…::test_abrir_o_documento_instruido_fica_registrado_por_item` |
| **FR-535** | `_documentos_da_peca` confere a Inscrição, e a trigger a confere de novo | `test_alcance_da_instrucao.py::test_nao_se_instrui_documento_de_outro_candidato`, `…::test_a_trigger_recusa_o_documento_de_outro_candidato`, `test_instrucao_na_peca.py::test_nada_de_outro_candidato_atravessa_a_tela_instruida` |
| **FR-536** | as duas rotas novas passam por `_peca_para_julgar`, que filtra por escopo | `test_instrucao_na_peca.py::test_escopo_institucional_divergente_recebe_recurso_nao_encontrado`, `test_parecer_do_titular.py::test_escopo_institucional_divergente_recebe_a_resposta_uniforme` |
| **FR-537** | **nenhuma escrita em `Avaliacao` nem em `ConclusaoAvaliacao`** em todo o diff — as duas são só lidas | conferido por leitura do diff, e sustentado por `test_alcance_da_instrucao.py::test_o_alcance_fecha_com_a_decisao_e_o_registro_permanece`, que reafirma o parecer intacto depois do ciclo inteiro |

## 2. Critérios de sucesso

| Critério | Como foi verificado |
|---|---|
| **SC-182** | **percorrido pelo portal** — cenário 1 da §4: Elisa Moraes lê *"pontuação inferior à nota mínima da Etapa (4,0000 < 6,0000)"* e, ao lado, *"FUNDAMENTAÇÃO ESCRITA POR QUEM AVALIOU — Avaliação concluída."* Prendido por `test_parecer_do_titular.py` |
| **SC-183** | **percorrido pela gestão** — cenário 3 da §4: `helena.julgadora`, com o papel `julgador` e nada mais, lê o parecer atacado depois do ato, e continua lendo *"Julgar não as concede."* As capacidades antes e depois são as mesmas: `recurso:julgar` |
| **SC-184** | `test_trilha_da_instrucao.py` — os dois registros, e o caso do **zero**: sem instrução não há registro de acesso. Percorrido na trilha do Edital (cenário 5) |
| **SC-185** | `test_alcance_da_instrucao.py::test_o_alcance_fecha_com_a_decisao…` e `…::test_depois_de_decidido_o_documento_nao_abre…`; `test_instrucao_na_peca.py::test_depois_de_decidido_a_tela_diz_que_houve…` e `…::test_o_mesmo_julgador_em_outro_recurso_nao_alcanca_nada`. Percorrido no cenário 4 |
| **SC-186** | `test_parecer_do_titular.py::test_nada_de_terceiro_atravessa_a_tela_do_titular` e `test_instrucao_na_peca.py::test_nada_de_outro_candidato_atravessa_a_tela_instruida`; e o caso emendado em `test_resultado_da_etapa.py` (§3) |
| **SC-187** | **conferido lendo o diff**: `interface/identidade.py` não foi tocado — nenhum papel novo, nenhuma permissão nova. Nenhuma migration toca `avaliacoes_avaliacao`. Os dois vizinhos de `test_proveniencia_do_recurso.py` continuam idênticos |

---

## 3. Os testes alterados, caso a caso — e a recontagem

A `research.md` `R-6` previa **um**. Foram **dois**, e o segundo é o mesmo defeito de leitura que o
`R-5` havia encontrado no comentário do template — só que num teste.

| Caso | O que afirmava | O que afirma agora | Por quê |
|---|---|---|---|
| `test_proveniencia_do_recurso.py::test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta` | três asserções: o Edital alcançável, a tela de documentos fora, e *"Julgar não as concede."* | **as três, intactas**, mais quatro: a tela nomeia o que falta, diz que a prova chega por **ato**, nomeia as duas bases a quem pedir, e **não** oferece o formulário de instrução a quem não pode instruir | o previsto pelo `R-6`. O alcance **não** mudou — mudou o que a tela diz sobre a falta, que era um beco sem saída e passou a ter endereço |
| `test_resultado_da_etapa.py::test_nada_de_terceiro_atravessa` | *"a palavra `parecer` não está no corpo"* | *"o parecer **das outras pessoas** não está no corpo"*, com uma frase distintiva a procurar, **e** que a tela declara não haver parecer nesta inscrição | **não previsto.** A asserção só equivalia à regra enquanto parecer nenhum aparecia ali. O sujeito da regra sempre foi *de terceiro*, e agora ele está escrito. A asserção ficou **mais forte**: antes ela não teria detectado o vazamento de um parecer alheio cujo texto não contivesse a palavra |

**Um caso que a `T020` mandava conferir e que NÃO mudou**, e a ausência é resultado:
`test_a_tela_do_recurso_nao_faz_uma_consulta_por_ato` continua em **oito** consultas, sem uma linha
alterada. A existência de instrução entra por subconsulta `EXISTS`, que não custa leitura; as linhas
do ato só são lidas quando há ato. Para chegar lá foi preciso corrigir uma regressão que a primeira
escrita introduziu: `pode_gerir_comissao` passou a ser perguntada **duas** vezes na mesma tela — uma
pelo bloco dos caminhos, outra pelo da instrução — e o orçamento subia para nove. A base agora é
lida uma vez e entregue aos dois blocos.

**E há um orçamento novo, para a tela instruída**: `test_instrucao_na_peca.py::test_a_tela_instruida
_custa_uma_leitura_a_mais_e_ela_nao_cresce` fixa **treze**, nomeia cada uma das cinco a mais, e afere
que o número **não cresce** quando se acrescenta um terceiro ato. É essa propriedade que um registro
de acesso por item teria quebrado — e foi por ela que o acesso à tela virou **um** registro de
escopo, no padrão da `031`.

### Arquivos de teste novos

| Arquivo | O que prende |
|---|---|
| `tests/integration/recursos/test_alcance_da_instrucao.py` | o ato, o append-only nas três camadas, o alcance de **uma** peça, o fim com a decisão, e as recusas |
| `tests/portal/test_parecer_do_titular.py` | o que o titular lê, e quando — as duas condições, o recorte da segunda, as duas ausências ditas |
| `tests/interface/test_instrucao_na_peca.py` | os três estados, a referência sem cópia, o orçamento, e a contraprova do outro recurso |
| `tests/integration/recursos/test_trilha_da_instrucao.py` | os dois registros, e a contraprova de que o conteúdo não vaza |

### Fixtures ampliadas — por acréscimo, nunca por reescrita

`pontuar`, `cenario_julgavel`, `rascunho_com_marco` e `montar_marco` ganharam parâmetros opcionais
(`parecer`, `documentos`, `janela_recursal`) cujo padrão preserva o comportamento anterior. Nenhuma
asserção existente mudou por causa deles. A janela é declarada **no rascunho**, antes de publicar —
e não reescrevendo conteúdo publicado com o gatilho desligado, que é o caminho que a `018` abriu
para exercitar norma antiga e que aqui não era necessário.

---

## 4. Os cinco cenários do quickstart, percorridos

Percorridos em 19/09/2026 contra o certame de `make seed` (banco `ps_demo_036`, porta 8037), pelos
canais reais: o portal para a candidata, a gestão para a comissão e a autoridade.

| Cenário | Desfecho |
|---|---|
| **1 — o candidato lê a razão** | **percorrido.** Elisa Moraes (4,0 contra mínima 6,0) lê o motivo e, ao lado, o parecer. Contraprovas: outra candidata recebe *"Recurso não encontrado"*; Ana Silva, com resultado favorável, não vê bloco nenhum |
| **2 — o prazo fecha, e a tela diz** | **percorrido**, com `seed_demo --dias-atras 10`. Encerrado o prazo e sem peça pendente, o parecer some **e a tela diz por quê**, na letra da `FR-524`. A contraprova da segunda condição ficou de fora — §5.1 |
| **3 — quem julga, antes e depois** | **percorrido, inclusive o passo 5.** Antes: *"Nada foi instruído… Peça a alguém com a permissão de gerir a comissão ou a quem preside este Processo."* A presidência instrui. Depois: a mesma julgadora lê o parecer. **E em outro recurso da mesma Etapa não alcança nada** |
| **4 — o alcance morre com a decisão** | **percorrido.** Decidido o recurso, a tela diz *"Houve instrução neste recurso: 1 ato(s). O alcance que ela concedia terminou com a decisão, e o registro de que ela houve permanece — nada foi apagado."* O parecer sai da tela |
| **5 — a auditoria responde quem viu o quê** | **percorrido.** A trilha do Edital mostra o ato (*"Recurso REC-2026-AUA2FHAJ instruído com o parecer atacado"*, por `paulo.presidente`) e os acessos (por `helena.julgadora` e `paulo.presidente`). **Contraprova conferida na página**: o texto do parecer e a fundamentação de quem recorreu não aparecem |

**O que o cenário 3 revelou e nenhum teste teria revelado com a mesma clareza**: a presidência que
instruiu está **impedida de julgar** aquele recurso — *"Você consolidou o resultado atacado."* Se
`instruir` conferisse elegibilidade, como `admitir` e `julgar` conferem, a autoridade competente
nunca poderia instruir, e a feature seria inútil no caso normal. A decisão de **não** conferir
impedimento está escrita em `instruir.py`, e foi este percurso que a confirmou no produto.

---

## 5. O que ficou inexequível pela interface, e por quê

### 5.1 A contraprova da **segunda** condição (cenário 2, passos 4 e 5)

**O cenário 2 foi percorrido**, e o caminho não é o que o quickstart sugeria. Ele propunha
*"declarar a janela recursal do marco curta, de minutos"*, e **isso não existe no produto**:
`editais/domain/perfis.py` recusa qualquer unidade que não seja `DIAS_CORRIDOS`, e
`recursos/domain/janela.py` fecha no **último instante do dia** do vencimento — a janela mais curta
declarável só fecha no fim do dia seguinte.

O caminho que existe é `seed_demo --dias-atras N`, e ele **não afrouxa regra nenhuma**: o certame
percorre os mesmos commands, com as mesmas aferições, e só o instante em que ele ocorreu é outro.
A aplicação continua lendo o relógio real — por isso o resultado semeado aparece, no navegador, com
a janela já encerrada. É o que o próprio comando documenta, e foi assim que a `FR-524` foi vista na
tela, na letra.

**O que ficou de fora é a contraprova dos passos 4 e 5**: com o prazo fechado **e** uma peça dela
contra aquele resultado ainda em julgamento, o parecer **continua** aparecendo. Isolar isso exigiria
uma peça interposta **no passado** — e interpor agora, com o prazo vencido, é recusado pelo comando,
corretamente. O seed não interpõe recurso nenhum, e não há caminho de interface que o faça retroagir.

**O que cobre a contraprova**: `test_parecer_do_titular.py` exercita o prazo fechado avançando o
relógio **da leitura** — a publicação continua no instante em que aconteceu, e o que muda é quando
se pergunta. São três casos, e juntos eles separam as duas condições: o parecer permanece com peça
viva, sai com as duas encerradas, e **não** volta por peça contra outro resultado.

### 5.2 A instrução de **documento** (cenário 3, segunda espécie)

`seed_demo` não produz documento nenhum: o Edital semeado declara que a inscrição **não exige
documentos**, e a tela da candidata diz isso com todas as letras. Anexar um depois é impossível pelo
caminho certo — documento de inscrição enviada não é criado, e a guarda é do modelo desde a `009`.
Montar um certame com documentos exigidos **e** resultado publicado **e** prazo aberto exigiria
compor, publicar, inscrever, avaliar, consolidar, emitir e divulgar um Edital inteiro à mão.

**O que foi percorrido** é a espécie `PARECER`, que é a que fecha o `ACH-43` no seu ponto central —
quem julga decide com o texto atacado à vista. **O que cobre a outra espécie**: quatro casos em
`test_instrucao_na_peca.py`, incluindo a abertura do arquivo pelo julgador e a conferência de que
nada foi duplicado no armazenamento.

**É achado, e não escopo desta feature** — a governança do projeto é clara. O que ele diz é que o
`seed_demo` não sustenta a jornada de documento comprobatório, e isso alcança mais do que a `036`.

---

## 6. Quem passou a ver o quê, por quanto tempo, e o que ficou registrado

*Esta seção existe porque a `036` é a primeira da série que concede acesso a dado pessoal. Ela é o
que torna o acesso defensável, e é por escrito de propósito: um acesso que só o código explica é um
acesso que ninguém audita.*

### Quem passou a ver

| Quem | O que passou a ver | O que **não** passou a ver |
|---|---|---|
| **o titular da inscrição** | o **parecer da avaliação dele**, no acompanhamento, quando o resultado lhe foi desfavorável | nada de terceiro. A tela dele não ganhou nenhuma outra informação |
| **quem julga aquele recurso** | o **parecer atacado** e os **documentos citados**, depois de a autoridade praticar o ato | nada de nenhum outro recurso; nada da tela de documentos da inscrição; nada que `recurso:julgar` não alcançasse antes, fora o que o ato anexou |
| **quem preside ou audita** | **exatamente o que já alcançava.** A feature não lhes deu nada | — |

**Ninguém ganhou permissão.** `interface/identidade.py` não foi tocado: os sete papéis e as
capacidades de cada um são os mesmos de antes da feature. Quem instrui é quem já podia gerir a
comissão ou presidir o Processo; quem lê o instruído é quem já podia julgar **aquele** recurso.

### Por quanto tempo

| Acesso | Abre | Fecha |
|---|---|---|
| o parecer, para o titular | com o resultado desfavorável, enquanto o prazo recursal correr **ou** enquanto a peça dele contra aquele resultado não for decidida | quando **as duas** condições se encerram — e a tela diz por quê |
| o instruído, para quem julga | com o ato de instrução daquela peça | com a **decisão** daquela peça |

**O fechamento não depende de ninguém lembrar de fechar.** O alcance é derivado do estado do
recurso: não há linha a revogar, não há lista a podar, não há tarefa periódica. Uma permissão que se
concedesse teria de ser retirada; este alcance simplesmente deixa de existir quando a decisão nasce.

**O custo que permanece, e ele está na `D-001`**: encerradas as duas condições, o titular perde
acesso à razão da própria eliminação, e continua sendo o titular daquele dado. A `FR-524` é o que
impede o custo de virar defeito — a tela diz por quê, em vez de calar. Se a decisão for revista um
dia, é a `D-001` que muda, e esta linha junto.

### O que ficou registrado

| Registra | Não registra |
|---|---|
| que houve instrução: quem, quando, qual recurso | **o texto do parecer** |
| o que foi anexado, **por espécie** — e, no documento, qual **requisito** | **o conteúdo do documento** |
| qual **base** autorizou o ato | **o nome do arquivo**, que é do candidato |
| que alguém **exerceu** o acesso: quem, quando, e o **escopo** do que viu | **a fundamentação de quem recorreu** |

Os dois registros chegam à trilha do Edital, e não só ao banco: sem isso a `FR-533` e a `FR-534`
estariam cumpridas num lugar que nenhum ator alcança, que é o que o Princípio VI recusa.

**O acesso do titular ao próprio parecer não é registrado**, e a ausência é decisão: ele lê um dado
que é dele, no canal dele, autorizado pela titularidade que a porta já verifica. Registrar cada
abertura do acompanhamento produziria volume sem responder pergunta nenhuma que alguém faça — a
pergunta que a `FR-534` responde é *"quem, além do titular, viu isto?"*.

### A pergunta que um encarregado de dados faria, respondida

> *"Alguém que não tinha acesso ao parecer de um candidato passou a ter. Quem autorizou, quando, e
> até quando vale?"*

A trilha do Edital responde as quatro, numa tela: o ato nomeia quem autorizou e quando; o alcance é
daquele recurso e termina com a decisão dele; e os registros de acesso dizem quem de fato leu, e
quantas vezes.

---

## 6a. O que a revisão do PR encontrou, e o que cada achado custava

Três achados, **todos procedentes**. Os dois primeiros eram acesso a dado pessoal — a espécie de
defeito que esta feature existe para não ter.

### O alcance de um recurso **inadmitido** nunca fechava

`encerrado()` olhava só para `DecisaoRecurso`. Mas juízo de admissibilidade negativo é **terminal**,
e o banco o garante: a trigger `decisao_recurso_coerente` **recusa** decisão sobre recurso não
admitido. Uma peça inadmitida, portanto, nunca receberia a decisão que o alcance esperava.

**Não era uma janela larga demais: era uma janela sem fechadura.** O documento instruído continuava
abrindo, o parecer continuava na tela do titular, e novas instruções continuavam sendo aceitas —
indefinidamente. Nos dois canais, porque `pareceres_do_titular` classificava a peça inadmitida como
"pendente" pela mesma razão.

O predicado passou a reconhecer os **dois** desfechos, e a tela diz qual: *"terminou com a
decisão"* ou *"terminou com a inadmissão"*, em vez de acertar por sorte.

### Instruir documento sem poder abri-lo

A tela escondia a escolha de quem não tem `inscricao:consultar`; o **comando aceitava**. Uma
presidência com `recurso:julgar` — que tem a base composta e **não** tem a permissão de consultar
inscrições — podia forjar o `POST`, anexar o documento e depois abri-lo pela rota nova. Isto é a
`FR-105` da `018` contornada **pelo ato que existe para respeitá-la**.

**Esconder não é recusar**, e a fronteira é o comando. O parecer segue instruível por ela, porque
esse a autoridade já alcança pela porta da Etapa.

### Duas instruções sucessivas morriam em `409`

A chave de idempotência vinha da **assinatura da peça**, que cobre juízo e decisão — e instrução
nenhuma a move. Anexar o parecer e depois o documento reusava a mesma chave com conteúdo diferente:
`idempotency_conflict`. O oposto exato de *"instruir de novo acrescenta"*, e invisível na tela,
porque ela redireciona de todo jeito. A chave passou a vir do **pedido**.

**E o teste que deveria ter pego isso media o nada.** Ele postava um terceiro ato e conferia só o
orçamento de consulta; com o `409`, nada era criado e o número não se movia — corretamente. Agora
ele confere status e contagem, e há duas regressões novas pelo canal real: dois envios parciais
criam dois atos, e o mesmo envio repetido continua criando um só.

---

## 7. Verificação final

```bash
cd backend && make lint check test-pg
```

| | Antes | Depois |
|---|---|---|
| passando | 7343 | **7398** |
| pulados | 11 | **11** |
| falhando | 0 | **0** |
| tabelas append-only protegidas | 32 de 32 | **33 de 33** |

**O `+55` conferido caso a caso**, comparando a coleta desta árvore com a da `main` `2beb2d9`:

| Quantos | Onde | Por quê |
|---|---|---|
| 48 | os quatro arquivos de teste novos | a feature |
| 5 | `tests/test_sem_dado_pessoal_da_amostra.py` | ele varre **um caso por arquivo** de teste e de fixture; os quatro novos mais `tests/fixtures/instrucao.py` |
| 2 | `tests/integration/test_database_permissions.py` | dois casos parametrizados pela lista de tabelas append-only, que passou de 32 para 33 |

**Nenhum arquivo perdeu casos**, e é a outra metade da conferência: teste apagado some da contagem
sem fazer barulho, e foi assim que a `030` perdeu oito regressões com a suíte verde.

### Os dois guardiões que a migration fez falar

Os dois falharam na primeira passada completa, e **os dois estavam certos** — são exatamente a
conversa que eles existem para forçar:

- `tests/migrations/test_migrations.py::test_a_022_nao_acrescenta_migration_aos_apps_que_ela_apenas_le`
  conta as migrations por app, e `recursos` subiu de 1 para 2. A contagem foi corrigida **com a
  justificativa escrita**, no idioma que o arquivo já pratica, e os dois gatilhos novos entraram na
  lista que o teste verifica — de modo que ele passou a **conferir** que eles existem, em vez de
  ignorá-los;
- `tests/unit/test_leitura_do_documento_submetido.py::test_o_documento_submetido_nao_e_comparado_com_o_modelo`
  recusa qualquer arquivo que nomeie, ao mesmo tempo, o artefato do Anexo e o documento submetido —
  e `interface/views.py` já nomeava o primeiro. Quem o fez falhar foi uma **docstring** minha, que
  citava a classe do documento em prosa. A varredura é por texto e não distingue prosa de código, e
  **é bom que não distinga**: quem lê um arquivo que nomeia os dois não sabe, de antemão, se ele só
  fala ou se ele compara. A prosa foi reescrita; o guardião ficou como estava.

**`lint` são dois passos** — `ruff check` e `ruff format --check` —, e os dois passam.

**`make check` tem `makemigrations --check`, e aqui ele prova outra coisa.** Nas três features
anteriores ele provava *"nada mudou"*; esta **tem** migration, e o que ele prova é que a migration
escrita cobre o modelo — nem mais, nem menos.

**As promessas que se conferem lendo o diff**, e não rodando teste:

- **nenhuma capacidade nova, nenhum papel novo** (`FR-530`, `SC-187`) — `interface/identidade.py`
  não aparece no diff;
- **nenhum parecer alterado** (`FR-537`) — não há escrita em `Avaliacao` nem em
  `ConclusaoAvaliacao` em lugar nenhum do diff; as duas só são lidas;
- **nada de conteúdo publicado reescrito** — nenhuma migration toca conteúdo normativo, e a única
  tabela nova nasce vazia.
