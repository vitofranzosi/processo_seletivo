# Parecer A-11 — encerramento seguro do Edital

*01/11/2026. Diagnóstico e proposta de regra; nada implementado. As seis decisões da §9 foram
aceitas pelo usuário no mesmo dia. Base: `main` em `f90835e6` (após o
A-10). Achado de origem: A-11 da
[auditoria de prontidão de 31/10](auditoria-prontidao-arquitetural-e-operacional-2026-10-31.md).
Anexos: [captura da tela atual](parecer-a11-encerramento-do-edital-2026-11-01/tela-encerrar-atual.jpg)
e [roteiro da reprodução](parecer-a11-encerramento-do-edital-2026-11-01/reproducao_a11.py).*

## Recomendação em uma frase

**Encerrar passa a recusar (409) quatro situações que tornam a "conclusão regular" falsa ou deixam
um ato preso — período de inscrições não terminado, janela recursal aberta, recurso ou providência
de recurso pendente e Retificação homologada —, e a tela passa a listar, como ciência, as
providências que continuam depois do encerramento — convocação sem desfecho, resultado não
publicado, Retificação em elaboração ou revisão; cancelar não ganha bloqueio nenhum, só as mesmas
advertências.** A lista da tela é a mesma que o Relatório do Edital (099) mostrará depois, e a
recusa é conferida sob a trava do **Processo**, que é onde recurso e convocação já se serializam.

---

## 1. O que acontece hoje

### 1.1 Reprodução

Banco isolado (`test_ps_a11`, PostgreSQL, conexão como a role da suíte), cenário da convocação da
`019` acrescido do que o A-11 pede. Um mesmo Edital publicado com, ao mesmo tempo:

- recurso **admitido** e sem decisão;
- convocação **comunicada** sem desfecho, prazo em curso;
- inscrição em **rascunho**;
- Retificação **homologada**;
- (o próprio cenário traz um marco sem resultado divulgado).

| Passo | Encerrar | Cancelar |
|---|---|---|
| `recursos_aguardando_decisao` | 1 | 1 |
| Pendências da 099 antes | resultado não divulgado, convocação aguardando, recurso aguardando | idem |
| Tela de confirmação (GET) | 200, **nenhuma pendência**, botão "Confirmar" oferecido | idem |
| O ato | **aceito** | **aceito** |
| Julgar o recurso (indeferido) depois | **aceito** | **aceito** |
| Registrar aceite da convocação depois | **aceito** | **aceito** |
| Publicar a Retificação homologada depois | recusado 409, "Edital em estado final" (A-09) | idem |
| Retificação ficou | **HOMOLOGADA, para sempre** | idem |
| Rascunho ficou | RASCUNHO, não enviável | idem |
| Pendências da 099 depois | resultado não divulgado; espécie *acompanhamento* | nenhuma; espécie *interrupção* |

Pela aplicação (demonstração, `gustavo.gestor`, Edital 51/2026 com convocação aguardando resposta
e resultado definitivo não publicado), a tela é a da captura anexa: três consequências fixas,
motivo, "Confirmar: Encerrar". Nada sobre o que está em curso. E o **detalhe do Edital não mostra
ao gestor quantos recursos aguardam** — a ação "Recursos aguardando decisão (n)" só aparece para
quem tem `recurso:julgar` —, de modo que quem encerra não tem onde ver o número.

### 1.2 O que cada ato lê depois do encerramento

Só dois caminhos leem o estado do **Edital**: o recebimento de inscrição
(`inscricoes/domain/periodo.py:86`, `ESTADOS_QUE_RECEBEM = {"PUBLICADO"}`) e os atos da
Retificação (`publicacoes/application/retificacoes.py:85`, A-09). O resto lê só o **Processo**
— e o Processo continua `ATIVO` enquanto houver Edital fora de estado final — ou não lê nada.

| Ato | Guarda | Encerrado | Cancelado |
|---|---|---|---|
| Abrir, gravar, anexar, enviar inscrição | Edital (`rascunho.py:181`, `:445`) | bloqueado | bloqueado |
| Interpor recurso | só a janela (`interpor.py:229`) | **aceito** dentro da janela | aceito |
| Admitir, julgar, instruir recurso | nenhuma (`porta.py:16` só tranca) | aceito | aceito |
| Avaliar na Mesa (`gravar`, `concluir`) | nenhuma | aceito | aceito |
| Consolidar, ocorrência, reabrir avaliação | Processo | aceito | aceito |
| Emitir ordem, corte, apuração, acréscimo de vagas | Processo | aceito | aceito |
| Publicar resultado | **nenhuma**, nem a do Processo (`divulgacao/application/publicar.py:113`) | aceito | aceito |
| Convocar, comunicar, desfecho, atestar | Processo (`comando_de_comissao`) | aceito | aceito |
| Sorteio | Processo | aceito | aceito |
| Confirmar aviso; `despachar_avisos` | Processo; o despacho, nenhuma | aceito | aceito |
| Requerimento de matrícula; exportação | nenhuma | aceito | aceito |
| Retificação: criar, editar, submeter, homologar, devolver, **cancelar**, publicar | Edital (A-09) | **bloqueado** | **bloqueado** |
| Reaproveitar como origem | `ORIGENS_ELEGIVEIS` | aceito | excluído |

Duas consequências que o A-11 não nomeava:

1. **A Retificação em curso fica sem saída.** Cancelar Retificação só parte de `EM_ELABORACAO`
   (`retificacoes.py:519`); de revisão ou homologada, é preciso devolver antes. Depois do
   encerramento, *todos* esses atos são recusados. A Retificação fica em `EM_ELABORACAO`,
   `EM_REVISAO` ou `HOMOLOGADA` indefinidamente, e a seção "Retificações em curso" da `103` continua
   anunciando um "próximo responsável" que nada pode fazer.
2. **Encerrar o Processo depois fecha o que encerrar o Edital deixou aberto, mas só em parte.**
   Com o Processo encerrado, `comando_de_comissao` recusa convocação, desfecho e apuração; julgar
   recurso, publicar resultado e o requerimento de matrícula continuam aceitos. A convocação
   aguardando resposta num Edital encerrado vira, no encerramento do Processo, desfecho que não se
   registra mais. (Registro, fora do escopo — ver §5, C-7.)

### 1.3 O que já existe a favor

- A tela de confirmação já tem o mecanismo: `praticar_ato` monta `pendencias` com `severidade`
  `erro`/`aviso`; `erro` vira `recusa_certa` e esconde o botão
  (`interface/views.py:4143-4160`, `confirmar.html`). Hoje só `submeter` e `publicar` o alimentam.
- A 099 já calcula, por tipo, as pendências de um Edital (`relatorio_do_edital.fatos_do_edital`,
  FR-2524): resultado não divulgado, definitivo não publicado, recurso aguardando, reavaliação e
  providência pendentes, apuração desatualizada, convocação aguardando e convocação vencida.
- `acoes.recursos_aguardando_decisao` conta numa consulta os que aguardam admissibilidade **ou**
  julgamento.
- O encerramento do Processo já é o precedente de recusa por pendência
  (`ensure_processo_can_be_closed`, `editais_pendentes`, 409, com a lista no texto).

---

## 2. Encerramento e cancelamento não são o mesmo ato

| | Encerramento | Cancelamento |
|---|---|---|
| Sentido (FR-006) | "conclusão regular **após o término das etapas**" | "interrupção administrativa anterior à conclusão regular" |
| Pendência significa | a conclusão afirmada ainda não aconteceu | o que a interrupção atinge |
| Quem precisa ser protegido | a verdade do ato e o direito de quem recorreu | a capacidade de interromper já (ordem judicial, vício insanável) |
| Recomendação | recusar o que torna o ato falso ou deixa ato preso; advertir o resto | **nunca recusar por pendência**; advertir o que será atingido |

Bloquear o cancelamento por pendência inverteria o ato: o cancelamento existe justamente para quando
o fluxo regular não pode terminar. O que ele pede é que quem cancela saiba o que deixa para trás.

---

## 3. Matriz de decisão

**B** = bloqueio (409 no domínio, botão escondido na tela). **A** = advertência (lista de ciência,
não impede). **P** = permissão sem menção.

| # | Pendência | Estado que a caracteriza | Regra existente | Se encerrar sem resolver | Depois do encerramento | Encerrar | Cancelar | Por quê | Forma mínima de resolver | O que a tela diz |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Período de inscrições aberto ou por abrir** | `periodo_de_inscricoes(vigente).aberto` ou `FUTURO` | FR-006; 047 `D-003` trata "encerrado antes do fim do período" só como exibição | recebimento para na hora; rascunhos morrem; o cronograma publicado é desmentido sem ato que o altere | nada se recebe | **B** | A | encerrar antes do término não é conclusão regular; o caminho regular é Retificar o prazo, e o excepcional é cancelar | aguardar o término; ou Retificar o período; ou Cancelar | "O período de inscrições vai até DD/MM às HH:MM. Encerrar antes disso não é conclusão regular: altere o período por Retificação ou cancele o Edital." |
| 2 | **Janela recursal aberta** | algum ato publicado com janela de `recursos/domain/janela.py` em curso | 018; 047 `D-005` (prazo público = o da interposição) | o prazo publicado continua correndo e a interposição continua aceita (§1.2) — o Edital "concluído" recebe recurso | interpor aceito até o fim da janela | **B** | A | o direito de recorrer foi publicado; concluir antes do fim do prazo é afirmar que ninguém mais recorrerá | aguardar o fim da janela | "O prazo de recurso contra «marco» vai até DD/MM." |
| 3 | **Recurso aguardando admissibilidade ou julgamento** | `_aguardando_decisao()` (`acoes.py:428`) | 018; 099 FR-2524; Supervisão: o recurso "continua podendo ser decidido" (045, R-7) | decisão pode mudar resultado de Edital dito concluído | admitir e julgar aceitos | **B** | A | dever de decidir da Administração; o resultado ainda não é definitivo | julgar (ou não admitir) cada peça | "N recursos aguardam decisão — [Ir aos recursos]" |
| 4 | **Reavaliação ou providência pendente de recurso** | `recursos.reavaliacoes_pendentes_do_marco`, `providencias_pendentes_do_marco` | 018 (publicabilidade), 099 FR-2524 | decisão de recurso sem efeito executado | atos aceitos | **B** | A | é a execução de uma decisão já tomada | concluir a reavaliação / a providência | "Reavaliação determinada em recurso ainda não concluída em «marco» — [Conduzir o marco]" |
| 5 | **Retificação homologada** | `Retificacao.status == HOMOLOGADA` | 001 FR-006; A-09; 103 Edge Cases | ato aprovado fica preso para sempre, sem publicar nem devolver | nenhum ato | **B** | A | mudança normativa aprovada e não publicada contradiz "conclusão regular"; e não pode haver objeto sem transição possível | publicar; ou devolver e cancelar | "A Retificação nº N foi homologada e não publicada. Publique-a ou devolva-a antes de encerrar — [Abrir a Retificação]" |
| 6 | Retificação em elaboração ou em revisão | `EM_ELABORACAO`, `EM_REVISAO` | 103 Edge Cases | fica parada para sempre; nada normativo muda | nenhum ato | A | A | é trabalho interno não aprovado — o equivalente institucional do rascunho; obrigar a cancelar antes seria ritual | cancelar (em elaboração) ou devolver e cancelar (em revisão), se quiser | "A Retificação nº N, em elaboração, deixará de poder prosseguir." |
| 7 | Convocação comunicada sem desfecho, prazo em curso | `CONVOCACAO_AGUARDANDO` (099) | 019; **099 cena 1 de US2 e D-007 assumem este estado como normal** | nenhuma, enquanto o Processo estiver ativo | desfecho aceito | **A** | A | o prazo é do candidato; esperar por ele adiaria o encerramento sem ganho, e o registro continua possível | registrar o desfecho quando vier | "1 convocação aguarda resposta até DD/MM. O desfecho continua podendo ser registrado depois." |
| 8 | Convocação com prazo vencido sem registro | `CONVOCACAO_VENCIDA` (099) | 019 (`registrar_nao_atendimento_dos_vencidos`) | vaga pode não ser reocupada | registro aceito | A | A | é registro de fato já ocorrido | registrar o não atendimento | "1 convocação venceu sem registro — [Ir à convocação]" |
| 9 | Resultado não divulgado / definitivo não publicado | `RESULTADO_NAO_DIVULGADO`, `DEFINITIVO_NAO_PUBLICADO` (099) | 099 FR-2524 | relatório fica "de acompanhamento" | publicar aceito | A | P | há marcos declarados que legitimamente não se cumprem (cadastro de reserva, marco intermediário); bloquear geraria falso impedimento | publicar o resultado | "Resultado definitivo de «marco» não publicado." |
| 10 | Apuração desatualizada | `APURACAO_DESATUALIZADA` (099) | 016 | números de ocupação defasados | reapurar aceito | A | P | consequência de atos posteriores; não é obrigação perante terceiros | reapurar | "A apuração de «Perfil» está desatualizada." |
| 11 | Rascunho com o período **encerrado** | `Inscricao.RASCUNHO` | 009 | nenhuma: já não podia ser enviado | idem | **P** | P | abandono do candidato, não obrigação da Administração | — | nada |
| 12 | Aviso na fila de despacho | aviso confirmado não despachado | 066 | sai no próximo minuto | despacho aceito | P | P | já é ato praticado | — | nada |
| 13 | Requerimento de matrícula em curso | `requerimentos` | 029/031; 099 FR-2525 ("o GPS não acompanha a matrícula") | nenhuma | aceito | P | P | fora do que o GPS acompanha | — | nada (a 099 já diz o limite) |

**Regras que exigem decisão institucional, e que não estão tomadas aqui:** as linhas 2 e 3 (se o
recurso pendente e a janela aberta impedem — recomendo que sim), a linha 1 (se encerrar antes do fim
do período é admitido em algum caso), a linha 9 (se o definitivo não publicado deve impedir), e,
no cancelamento, **o que acontece com os recursos pendentes e com os convocados** — se continuam a
ser decididos e registrados, ou se o cancelamento os prejudica. Esta última é jurídica (motivação
do ato, eventual direito adquirido do convocado), e o sistema hoje deixa tudo operável, que é a
posição mais conservadora enquanto ela não vem.

---

## 4. A Retificação homologada e o A-09

O A-09 está certo e não deve ser reaberto: Edital em estado final não ganha versão normativa. O
defeito que sobra não é a recusa da publicação, é **o estado em que a Retificação fica**: ninguém
pode publicá-la, devolvê-la ou cancelá-la, e a interface a lista para sempre "em curso".

Três saídas foram consideradas:

| Saída | Avaliação |
|---|---|
| **Impedir o encerramento enquanto houver Retificação homologada** | **Recomendada.** Mudança aprovada e não publicada é decisão normativa pendente; "conclusão regular" com ela não é verdadeira. Custo: publicar, ou devolver (homologador) e cancelar (gestor) — dois atos já existentes. |
| Encerrar cancelaria a Retificação automaticamente | Recusada: `finalizacao.py` registra o princípio "nenhum ato propaga desfecho automaticamente"; e um ato homologado seria desfeito sem motivo próprio. |
| Permitir cancelar a Retificação depois do encerramento | Recusada aqui: reabre o A-09 por uma porta lateral, e o usuário vetou. Fica como alternativa se a decisão sobre a linha 5 for "advertir". |

Para **em elaboração e em revisão**, advertir basta: nada aprovado se perde. A interface, porém,
deve deixar de anunciar "próximo responsável" para Retificação de Edital em estado final e dizer
"não pode mais prosseguir: o Edital foi encerrado" — mudança de leitura da seção da `103`, sem ato
novo. No **cancelamento** do Edital a Retificação homologada é advertência, não bloqueio: quem
interrompe não deve precisar de dois atos prévios, e a mesma frase de leitura resolve a exibição.

---

## 5. Contradições entre spec, domínio e interface

| # | Onde | Contradição |
|---|---|---|
| C-1 | `interface/atos.py:128` × FR-006 × domínio | A tela afirma "registrando a conclusão regular de suas etapas"; o domínio não confere etapa nenhuma. A frase promete o que o ato não garante — e a 099 (D-002) já decidiu que "encerramento não diz concluído". |
| C-2 | `atos.py:129` × A-09 | "Nenhuma Retificação poderá ser publicada depois disso" é verdade, mas cala que a Retificação **em curso** fica presa e que nem cancelá-la será possível. |
| C-3 | 099 (US2 cena 1, D-007, SC-935) × A-11 | A 099 tem como cenário normal "Edital encerrado com convocação no prazo de resposta" e registrou a conferência de pendência como decisão do usuário (D-007). A recomendação mantém esse cenário válido (convocação é advertência), e por isso não quebra a 099. |
| C-4 | 047 `D-003` e testes `test_desfecho_publico.py:214,225` | A 047 dá exibição a "encerrado com período em curso / por abrir". Com o bloqueio da linha 1, esse estado só nasce por cancelamento ou por dado anterior à regra; a regra de exibição continua necessária, mas os dois testes precisam chegar ao estado por outro caminho. |
| C-5 | 047, `test_prazo_recursal_publico.py:166` | "Edital encerrado com prazo [recursal] em curso" é caso-limite testado. Com o bloqueio da linha 2 ele deixa de ser alcançável por encerramento. |
| C-6 | 103 Edge Cases × A-09 | "A seção continua listando" com "próximo responsável" — mas ninguém pode agir. |
| C-7 | 001 FR-035 × domínio | "Encerramento e cancelamento DEVEM impedir novas transições incompatíveis" — quais são as incompatíveis nunca foi enumerado. Hoje: inscrição e Retificação. Encerrar o Processo acrescenta convocação e apuração, mas não julgamento, resultado nem matrícula (§1.2). Fora do A-11; merece registro próprio. |
| C-8 | Detalhe do Edital × quem encerra | O gestor (que detém `edital:encerrar`) não vê a contagem de recursos aguardando, porque a ação depende de `recurso:julgar`. A confirmação de encerramento precisa mostrar o número a quem encerra, sem dado pessoal. |
| C-9 | A-11 (texto da auditoria) × domínio | O achado fala em recurso "admitido"; a pendência real inclui o que **aguarda admissibilidade** (`_aguardando_decisao`, 099 FR-2524). |

---

## 6. Proposta visual

A mesma tela, o mesmo template, com o mecanismo `pendencias` que `submeter` e `publicar` já usam.
Nenhuma tela nova, nenhum painel.

```
Encerrar
Edital 51/2026 — seleção concluída

┌─ Antes de encerrar, resolva 2 pendências ─────────────────────── (erro) ─┐
│ • 1 recurso aguarda decisão.                     Ir aos recursos →       │
│ • A Retificação nº 3 foi homologada e não        Abrir a Retificação →   │
│   publicada. Publique-a ou devolva-a.                                    │
└──────────────────────────────────────────────────────────────────────────┘

┌─ Continuam depois do encerramento ─────────────────────────── (aviso) ───┐
│ • 1 convocação aguarda resposta até 30/10. O desfecho continua podendo   │
│   ser registrado.                                                        │
│ • Resultado definitivo de «Classificação final» não publicado.           │
└──────────────────────────────────────────────────────────────────────────┘

Este ato não pode ser desfeito
• O Edital passa a Encerrado e deixa de receber inscrição e Retificação.
• O que está acima como "continua" segue possível, e aparece no Relatório do Edital.
• Publicações, documentos e histórico permanecem disponíveis na consulta pública.

Motivo do encerramento *  [                                   ]
[Cancelar e voltar]                      ← sem "Confirmar" enquanto houver pendência
```

Sem pendência nem advertência, a primeira caixa vira uma linha só: **"Nenhuma pendência registrada
no GPS impede o encerramento."** — a mesma ressalva da 099 (FR-2525): o GPS não afirma o que não
acompanha. No cancelamento, só a caixa de aviso aparece, com o título "Serão atingidos pelo
cancelamento".

Regras da apresentação:

- **Contagens, nunca nomes.** A tela é do gestor, e recurso e convocação são fato não público
  (099, D-006). Os links levam às telas donas, onde a permissão de cada uma decide.
- **Cada item diz a ação que o resolve**, e só oferece o link a quem a tela de destino aceita —
  a regra da `104` ("oferecer o que se vai recusar é pior do que não oferecer"). Para quem não
  alcança, o texto diz a quem pedir ("peça a quem julga recursos").
- **A lista de aviso é a da 099.** O que a confirmação adverte é exatamente o que o relatório dirá
  depois como "providências" — uma regra, duas leituras.
- O texto da consequência deixa de afirmar "conclusão regular de suas etapas" (C-1).

---

## 7. Concorrência e integridade

**A janela.** Entre o GET da confirmação e o POST, outra pessoa pode admitir um recurso, homologar
uma Retificação ou abrir uma janela recursal (publicando um resultado). Dentro do POST, entre ler as
pendências e gravar `ENCERRADO`, o mesmo.

**O que as travas existentes já dão.** Os escritores relevantes se serializam em duas linhas:

| Escritor | Linha travada |
|---|---|
| interpor, admitir, julgar recurso | `ProcessoSeletivo` FOR UPDATE (`interpor.py:282`, `porta.py:16`) |
| convocar, comunicar, desfecho; apuração, corte, ordem | `ProcessoSeletivo` FOR UPDATE (`comando_de_comissao`) |
| publicar resultado (abre janela recursal) | `ProcessoSeletivo` FOR UPDATE (`publicar.py:113`) |
| atos da Retificação | `Retificacao` + `Edital` + `Processo` FOR UPDATE, sem `OF` (A-09) |
| enviar inscrição | `Edital` FOR SHARE |
| encerrar/cancelar Edital | **só** `Edital` FOR UPDATE (`finalizacao.py:_lock_edital`) |

**O mínimo.** Em `_finalize_edital`, travar o **Processo** antes do Edital — `select_for_update`
na linha do Processo, na mesma ordem que `close_process` já usa (Processo, depois Editais) — e
conferir os bloqueios **depois** das duas travas, dentro da mesma transação. Com isso:

- recurso, convocação e publicação de resultado esperam o encerramento ou são esperados por ele;
- a Retificação já se serializa pela linha do Edital (e agora também pela do Processo);
- o recebimento de inscrição já espera pelo `FOR SHARE` no Edital.

Nenhuma trava nova em tabela nova, nenhum nível de isolamento diferente. As advertências **não**
precisam dessa garantia — não impedem nada —, e a tela as recalcula se o POST for recusado. Não
recomendo "assinatura" das advertências vistas no GET: custo de estado no formulário para proteger
algo que não bloqueia.

**Risco a conferir na implementação:** os atos da Retificação trancam Retificação, Edital e Processo
num único `FOR UPDATE`; o encerramento passaria a trancar Processo e depois Edital. Os dois testes de
concorrência do A-09 (`test_encerramento_primeiro_a_publicacao_espera_e_recusa`,
`test_publicacao_primeiro_o_encerramento_espera_e_conclui`) são exatamente o caso, e devem continuar
verdes; um teste de concorrência novo com recurso admitido em paralelo prova o resto.

---

## 8. Alterações mínimas que a spec pediria

**Domínio e aplicação**

1. `processos/domain/finalizacao.py`: `ensure_edital_can_be_closed(edital, impeditivas=())` recusa
   com `DomainError("pendencias_impeditivas", <texto com a lista>, 409)` — a forma de
   `ensure_processo_can_be_closed`. `ensure_edital_can_be_cancelled` não muda.
2. Uma função de aplicação, `pendencias_do_encerramento(edital, agora)` (em `processos/application/`),
   que devolve tipos e contagens das linhas 1–5 da matriz, reaproveitando: `periodo_de_inscricoes`,
   a janela de `recursos/domain/janela.py`, `_aguardando_decisao` (movido de `interface/acoes.py`
   para `recursos/application/selectors.py`, e `acoes` passa a importá-lo), as duas funções de
   pendência de recurso da 099 e um filtro de `Retificacao` homologada.
3. `processos/application/finalizacao.py`: `_finalize_edital` trava o Processo antes do Edital; o
   `check` do encerramento recebe as impeditivas calculadas sob as travas.

**Interface**

4. `praticar_ato`: para `encerrar` e `cancelar`, montar `pendencias` — as impeditivas (só no
   encerrar) como `erro`, e as advertências a partir de `fatos_do_edital` mais as Retificações em
   elaboração/revisão — com texto e link de resolução. O resto do template já sabe exibi-las e
   esconder o botão.
5. `atos.py`: corrigir as consequências de `encerrar` (C-1, C-2).
6. Seção "Retificações em curso" (`103`): para Edital em estado final, "não pode mais prosseguir" no
   lugar do próximo responsável.

**Testes**

7. Novos: cada bloqueio da matriz recusado por command (409, código, sem mudança de estado) e pela
   tela (sem "Confirmar"); cada advertência exibida sem impedir; o cancelamento aceito com todas as
   pendências; concorrência — recurso admitido em paralelo com o encerramento; a recusa cabendo nos
   privilégios de produção (`como_producao`).
8. A ajustar (chegam ao estado final por um caminho que passará a ser recusado):
   `tests/integration/portal/test_desfecho_publico.py` (encerrado com período em curso / por abrir),
   `tests/portal/test_prazo_recursal_publico.py:166` (encerrado com prazo recursal em curso),
   `tests/integration/agenda/test_fonte.py:162`, e conferir `tests/fixtures/relatorio.py` (o final
   `pendente` encerra com convocação no prazo — continua válido como advertência — e com os
   recursos já julgados). Os demais arquivos que encerram Edital usam, em geral, o Edital recém
   publicado; os que tiverem período em curso precisarão de datas passadas ou de cancelar.
9. `tests/acceptance/test_us7_finalizacao.py`: cenários de aceitação da spec nova.

Estimativa: uma spec curta, um incremento, sem migration.

---

## 9. Decisões

**Decididas pelo usuário em 01/11/2026: as seis recomendações abaixo foram aceitas como estão**
(*"Aceito as seis"*). São a base da spec curta do A-11.


1. **Recurso aguardando decisão, e reavaliação/providência de recurso pendente, impedem encerrar?**
   Recomendo **sim** (linhas 3 e 4).
2. **Janela recursal aberta impede encerrar?** Recomendo **sim** (linha 2). Consequência: o
   caso-limite da 047 "encerrado com prazo recursal em curso" deixa de nascer por encerramento.
3. **Período de inscrições aberto ou por abrir impede encerrar?** Recomendo **sim** (linha 1): o
   caminho é Retificar o período ou cancelar.
4. **Retificação homologada impede encerrar, e só adverte no cancelamento?** Recomendo **sim** para
   os dois (linha 5 e §4). Em elaboração e em revisão, só advertência.
5. **Convocação sem desfecho e resultado definitivo não publicado só advertem?** Recomendo **sim**
   (linhas 7–9), em coerência com a 099 (D-007, US2 cena 1).
6. **No cancelamento, o que acontece com recurso pendente e com convocado sem desfecho?** É decisão
   institucional/jurídica. Até ela vir, recomendo manter o comportamento atual (tudo continua
   operável) e só advertir.

Fora do A-11, para registro e não para esta spec: a incoerência de C-7 (o que o encerramento do
**Processo** impede: convocação sim, julgamento e publicação de resultado não) e o fato de
`publicar_resultado` não conferir nem o estado do Processo.
