# Auditoria — a passagem da Retificação entre pessoas, e a recusa do sorteio

**Pedido**: reunião de validação de 29/10/2026. **Código auditado**: `main` em `0ff70f07`,
reconferido em 30/10 sobre `0061f28e`, depois dos merges do #335, do #336 (Agenda dos Editais) e do
#337 (spec 102). Os números de linha citados são os de `0061f28e`. O commit que roda no servidor não
foi conferido.

> **Registro, e não escopo.** Nada aqui foi corrigido. O comportamento do sistema não mudou: o único
> arquivo novo além deste é um teste de reprodução. Decidir o que corrigir, e quando, é do usuário.

## 1. Diagnóstico executivo

**A falha de continuidade está confirmada, e a causa é uma só: nenhuma tela lista Retificação que
ainda não foi publicada.** O único link para o detalhe de uma Retificação sai do cartão "Documentos
publicados" do Edital, e só existe depois da Publicação. Em elaboração, em revisão ou homologada,
a Retificação não aparece na Lista, na Agenda, no Processo, no Edital nem na tela de Retificar.
Isso vale até para quem a criou: saindo da tela, nem ela a reencontra. A Agenda, que entrou em 30/10,
não muda o quadro: ela só anuncia a Retificação **já publicada** com vigência futura.

**O servidor está certo.** A URL copiada funcionou porque o segundo usuário **tinha** a permissão:
o detalhe é aberto a qualquer ator do mesmo escopo, e os botões são calculados a partir da permissão
e da situação. Não há desvio de autorização. Quem não tem a permissão é recusado com 403, mesmo
mandando a requisição direto. Quem é de outra unidade recebe 404. O ato fora da situação recebe 409.
A segregação é verificada no servidor.

A reunião viu uma porta sem corredor, e não uma porta destrancada.

**O sorteio recusou pelo motivo certo.** O "00:00" não é conversão acidental. A Caixa publica a
extração só com a data, e o sistema a toma de propósito como o início do dia, porque é o único
instante que a fonte comprova. Com o congelamento no mesmo dia, a precedência não se prova. As duas
lacunas em volta dessa recusa foram corrigidas pelo #335 e pelo #337, mergeados em 30/10
(seção 6).

## 2. O fluxo real

Estados (`publicacoes/models_retificacao.py:37`): `EM_ELABORACAO → EM_REVISAO → HOMOLOGADA →
PUBLICADA`, mais `CANCELADA`. As transições estão em `TRANSITIONS`
(`publicacoes/application/retificacoes.py:477`), e a publicação tem comando próprio
(`publish_retification`, `:875`).

**Papéis** (`interface/identidade.py:25`). Cada papel é um conjunto fixo de permissões. Não existe
"papel ativo": a sessão recebe a **união** das permissões dos papéis escolhidos, e é recalculada a
cada requisição a partir da sessão. Nada fica em cache entre uma troca de sessão e outra.

| Operação | Permissão (papel) | Estado exigido | Restrição de identidade | Endpoint (gestão · API) | Acesso pela UI |
|---|---|---|---|---|---|
| Criar | `retificacao:elaborar` (Elaborador) | Edital `PUBLICADO` | nenhuma | `POST /gestao/editais/{id}/retificar` · `POST /api/v1/admin/editais/{id}/retificacoes` | "Retificar" no Edital e na Lista, só para quem elabora |
| Editar rascunho | `retificacao:elaborar` | `EM_ELABORACAO` | nenhuma: qualquer elaborador do escopo | **só API**: `PUT /api/v1/admin/retificacoes/{id}/rascunho` | **nenhum** (AUD-RET-04) |
| Submeter | `retificacao:submeter` (Elaborador) | `EM_ELABORACAO` | nenhuma; grava `prepared_by` = quem submete | `/gestao/retificacoes/{id}/atos/submeter` · `…/submissoes` | botão no detalhe, que só se alcança logo após criar |
| Homologar | `retificacao:homologar` (Homologador) | `EM_REVISAO` | nenhuma: quem submeteu pode homologar | `…/atos/homologar` · `…/homologacoes` | botão no detalhe, **que ninguém alcança** (AUD-RET-01) |
| Devolver | `retificacao:homologar` | `EM_REVISAO` ou `HOMOLOGADA` | nenhuma | `…/atos/devolver` · `…/devolucoes` | idem |
| Publicar | `retificacao:publicar` (Publicador) | `HOMOLOGADA` | recusa se `prepared_by == homologated_by == ator` | `…/atos/publicar` · `…/publicacoes` | idem |
| Cancelar | `retificacao:cancelar` (Gestor) | `EM_ELABORACAO` | nenhuma | `…/atos/cancelar` · `…/cancelamentos` | idem |
| Ler o detalhe | **qualquer ator autenticado do escopo** | qualquer | escopo da unidade (404 fora dele) | `GET /gestao/retificacoes/{id}/` · **não há GET na API** | só a publicada, por "Documentos publicados" |

**Onde a regra está escrita.** A segregação é a `FR-021` da `001`: *"uma única pessoa NÃO PODE
concluir sozinha as três etapas"*. Ela foi escrita para o Edital, e a Retificação a copia na
mesma forma (`retificacoes.py:892`). A matriz de permissões por papel é código
(`identidade.py`), com docstrings. Nenhuma spec diz **como** quem homologa ou publica chega à
Retificação. A "passagem de bastão" da `007` (`acoes.py:362`, `PROXIMO_RESPONSAVEL`) foi
especificada e implementada **só para o Edital**.

## 3. Achados

### AUD-RET-01 — Retificação não publicada é inalcançável pela navegação · **Alta**

- **Esperado**: quem tem o próximo ato encontra a Retificação a partir das telas que já usa.
- **Observado**: nenhuma página alcançável a partir das seções da barra (Lista, Minhas Etapas,
  Agenda), em dois cliques, cita o identificador ou o endereço de uma Retificação pendente.
- **Evidência**:
  - `interface/views.py:3731` (`_documentos_publicados`) monta a lista a partir das
    **Publicações**, e `detalhe.html:143` só liga à Retificação que tem uma;
  - `views.py:3758` (`detalhe`) não passa Retificação nenhuma ao template;
  - `interface/agenda.py:701` (`retificacoes_a_vigorar`) lê `VersaoConsolidada` de vigência
    futura, que só existe depois da Publicação, e não liga ao detalhe;
  - `acoes.py:101-105` oferece só "Retificar", e só a quem elabora;
  - `acoes.py:362`: `PROXIMO_RESPONSAVEL` não tem entrada para Edital `PUBLICADO`, de modo que o
    cartão "próximo passo" se cala justamente enquanto há Retificação em curso;
  - a API não tem nenhum `GET` de Retificação (`publicacoes/api/urls.py`).
- **Reprodução**: `test_quem_homologa_encontra_a_retificacao_em_revisao_sem_conhecer_a_url` e os
  dois irmãos `xfail`; `test_hoje_nenhuma_tela_alcancavel_cita_a_retificacao_pendente`, na forma
  positiva.
- **Causa-raiz** (confirmada): a listagem nunca existiu. Não é filtro errado. Das três relações
  que a reunião suspeitou confundidas (*criadas por mim*, *que posso consultar*, *que dependem de
  mim*), **nenhuma** tem consulta na interface. A prova é que nem quem criou reencontra o próprio
  rascunho.
- **Impacto operacional**: o fluxo só anda por URL copiada fora do sistema. Quem elabora tende a
  compor uma segunda Retificação sem saber da primeira
  (`test_um_segundo_rascunho_nasce_sem_aviso_do_primeiro`).
- **Impacto de segurança**: nenhum. A URL copiada não concede nada que o papel já não concedesse.
- **Recomendação**: ver o plano mínimo (seção 5).

### AUD-RET-02 — Nenhuma passagem de bastão na Retificação · **Média**

- **Esperado**: o mesmo que o Edital faz. A confirmação diz *"o Edital fica aguardando quem
  homologa"* (`confirmar.html:58`), e o detalhe diz quem age a seguir.
- **Observado**: `retificacao_confirmar.html` e `retificacao_detalhe.html` não dizem a quem o ato
  entrega. Depois de submeter, só aparece "Ato registrado."
- **Causa**: `ENTREGA_DO_ATO` e `proximo_passo` (`acoes.py`) só leem o Edital.
- **Recomendação**: estender a mesma derivação de leitura à Retificação, sem fila nem atribuição a
  pessoa. A `007` já decidiu que a passagem é informação, e não motor.

### AUD-RET-03 — O detalhe oferece "Publicar" a quem a segregação vai recusar · **Baixa**

- **Esperado**: a tela antecipa a recusa, como faz no Edital (`acoes._motivo_previsivel`,
  `proximo_passo` com `segregacao`, `homologar_fecharia_a_publicacao` em `selectors.py:278`).
- **Observado**: `atos_retificacao.disponiveis` (`:117`) e `impedimento` (`:140`) consultam só a
  permissão e a situação. Quem elaborou e homologou vê "Publicar Retificação", preenche a
  confirmação e recebe 403.
- **Segurança**: nenhuma. O servidor recusa
  (`test_uma_pessoa_sozinha_nao_publica_o_que_elaborou_e_homologou`).
- **Reprodução**: `test_o_detalhe_nao_oferece_publicar_a_quem_a_segregacao_impede` (`xfail`).
- **Recomendação**: passar a mesma condição para `impedimento` e `disponiveis`, com o motivo
  visível.

### AUD-RET-04 — A tela não edita o rascunho existente · **Média**

- **Observado**: `edit_retification` só é chamado pela API (`publicacoes/api/views.py:182`). A tela
  de Retificar sempre **cria**. Depois de uma devolução, a consequência anunciada (*"pode ser editada
  novamente"*, `atos_retificacao.py:95`) só se cumpre pela API. Pela interface, a pessoa compõe outra
  Retificação, e a devolvida fica em elaboração para sempre, até alguém do Gestor cancelá-la.
- **Lacuna de teste**: `test_devolvida_a_retificacao_volta_a_aceitar_edicao` confere só que a tela
  de Retificar abre (200). Ela abre para compor uma **nova**.
- **Recomendação**: depende de decisão. A tela pode reabrir a devolvida, ou o fluxo pode assumir
  "devolver = recompor" e dizer isso no texto. Não foi verificado aqui.

### AUD-RET-05 — A segregação lê quem submeteu, e não quem compôs · **depende da regra**

- **Observado**: a recusa compara `prepared_by`, gravado na **submissão** (`retificacoes.py:522`).
  `created_by`, quem compôs as alterações, não entra na conta, e a edição pela API não grava autor.
  Quem acumula os três papéis compõe, pede a outra pessoa só o clique em "Submeter", homologa e
  publica sem recusa (`test_caracterizacao_quem_so_compos_conclui_se_outra_pessoa_submeter`).
- **O Edital tem a mesma forma** (`publish_edital.py:705`, `RevisaoEdital.prepared_by`), de modo
  que não é divergência entre os dois fluxos. É uma leitura da `FR-021`.
- **Pergunta para a governança**: na `FR-021`, "elaborou" quer dizer "submeteu" ou "compôs"? Se
  for "compôs", o caso caracterizado passa a ser recusado nos dois fluxos.

### Verificados sem defeito

| Hipótese da reunião | Resultado | Evidência |
|---|---|---|
| Consulta só do que eu criei | não existe consulta nenhuma (AUD-RET-01) | — |
| Filtro por status errado | não se aplica | — |
| Escopo errado por unidade | correto: 404 no detalhe e no envio | `test_outra_unidade_nao_ve_nem_pratica` |
| Papel ativo mal escolhido | não há papel ativo: as permissões dos papéis da sessão se somam | `identidade.py:161` |
| Permissão desatualizada após trocar de sessão | não: o ator é lido da sessão a cada requisição | idem |
| Botão e servidor divergem | concordam em 5 de 5 combinações de papel e situação (salvo AUD-RET-03) | `test_o_detalhe_oferece_exatamente_o_que_o_servidor_aceita` |
| Requisição direta sem permissão | 403 | idem |
| Ato fora da situação | 409 | `test_ato_em_situacao_incompativel_e_recusado_pelo_servidor` |
| Duas sessões no mesmo ato | uma passa, a outra recebe 409, e a trilha registra um só HOMOLOGAR. `select_for_update` (`retificacoes.py:67`) e a revisão por CAS seguram a corrida verdadeira | `test_a_segunda_homologacao_e_recusada_e_nao_duplica` |
| Trilha de auditoria | ator, permissão, operação, estado anterior e posterior, revisão e instante | `test_a_trilha_registra_ator_operacao_e_os_dois_estados` |

**Sobre a trilha.** Ela grava a **permissão** exercida, e não o papel. Como uma sessão pode
acumular papéis e o papel não é persistido, não se reconstrói "com qual papel" alguém agiu. Não é
defeito hoje, porque cada permissão de Retificação pertence a um papel só. Fica registrado para
quando o diretório institucional entrar.

## 4. Evidências automatizadas

Arquivo novo: `backend/tests/interface/test_auditoria_passagem_da_retificacao.py`. Usa só dados
sintéticos, um banco de teste próprio e três sessões `Client` independentes. A navegação parte de
**cada seção da barra**, lida de `navegacao.SECOES`, e segue, em até dois cliques, os links do
Processo e do Edital em causa. Uma seção nova entra na varredura sem ninguém precisar lembrar dela;
foi assim que a Agenda entrou na rodada de 30/10.

Contra PostgreSQL (`TEST_DB_ENGINE=postgresql`, `DB_NAME=audit_ret_60a8`, 4 workers):
**15 passed, 4 xfailed**, tanto em 29/10 sobre `0ff70f07` quanto em 30/10 sobre `0061f28e`. Com
`--runxfail`, os quatro `xfail` falham exatamente na asserção do achado: lista de páginas vazia ou
botão presente. Nenhum falha por erro de preparação.

Os `xfail` são `strict`. Quando a correção chegar, eles passam, o pytest reprova, e quem corrigiu
retira a marca.

**Lacunas.** A suíte completa não foi rodada; o arquivo é aditivo e não altera fixture comum. A
corrida simultânea verdadeira, com duas transações em paralelo, não foi exercitada; o teste é
sequencial, e a garantia vem do `select_for_update`. Nada foi conferido no ambiente do servidor.

## 5. Plano mínimo de correção (AUD-RET-01)

**Uma seção no detalhe do Edital: "Retificações em curso".** Ela lista as Retificações não finais
do Edital, com a situação e o link para o detalhe, a todo ator do escopo. O detalhe da Retificação
já é aberto a esse mesmo público, de modo que a lista não amplia acesso nenhum.

Quem tem o próximo ato, calculado por `atos_retificacao.disponiveis`, vê o rótulo do ato ao lado
("Homologar", "Publicar Retificação"). É a mesma derivação que o detalhe já usa, e por isso a lista
e o botão não divergem.

O custo é uma consulta por Edital no detalhe, e nenhuma na Lista. Não toca autorização, modelo nem
migration.

**Segundo passo, opcional.** Uma marca na linha do Edital, na Lista ("1 Retificação aguardando
você"), resolve a descoberta a partir da tela inicial. Custa uma consulta agregada por página, e
pede decisão de produto sobre o lugar.

Fora do mínimo: fila pessoal, notificação, atribuição a pessoa. A `007` (P-004) já recusou
transformar a passagem de bastão em motor.

## 6. Diagnóstico independente do sorteio

**Classificação: nem dado cadastrado errado, nem persistência inadequada, nem defeito da
validação.** A recusa de 29/10 estava certa. Havia uma **ambiguidade de negócio** que o Edital
deixou passar e um **defeito de apresentação** na mensagem. Os dois foram corrigidos em 30/10.

- **Persistência**: `OcorrenciaDaFonte.ocorrida_nao_antes_de` é `DateTimeField` com fuso, separado
  de `observada_em`, que é a consulta (`sorteios/models.py:167`).
- **Origem do 00:00**: a Caixa publica `dataApuracao` como data, sem horário.
  `loteria_federal.py:106` (`_nao_antes_de`) a converte **de propósito** em início do dia no fuso
  institucional (`:130`). É o limite inferior que a fonte comprova. A versão anterior carimbava
  20:00, e isso foi retirado por ser invenção.
- **Instante exigido pela regra**: a ocorrência tem de ser **posterior** ao congelamento da relação
  (`sorteio.py:229`). O horário declarado no Edital (`occurrenceAt`, 20h05) é norma, e não prova:
  ele só separa "ainda não publicou" de "não publicará".
- **Neste caso a ordem temporal não é demonstrável** com o que a fonte fornece. A relação foi
  congelada às 11:20 de 28/10, horário de Brasília, e a fonte só diz "28/10". A extração real às
  20h05 é posterior, mas nenhum dado do sistema o comprova.
- **A comparação da reunião misturava fusos.** "00:00" é o que a tela mostra, no horário de
  Brasília; "14:20" vem da mensagem, em UTC. No mesmo fuso, os pares são 00:00 × 11:20 e
  03:00 × 14:20. A conclusão é a mesma nos dois.

**O que mudou em 30/10.** As duas lacunas de
`doc/achado-sorteio-com-extracao-no-dia-do-congelamento.md` estão resolvidas na `main`:

1. **A mensagem em UTC** (#335). A recusa formata os instantes com `timezone.localtime`
   (`sorteio.py:260`), e a 102 a reescreveu para dizer o que aconteceu e a saída em dois atos:
   retificar a extração, depois suceder a relação (`_recusa_por_precedencia`, `:244`).
2. **O Edital que nasce sem condição de sortear** (#337, spec 102). Com fonte que publica só a data,
   a publicação **recusa** a extração que não cai em dia posterior ao fim das inscrições
   (`editais/domain/validation.py:2366`, `EXTRACAO_INVIAVEL`). A Retificação só **adverte**
   (`:2371`). A tela do sorteio avisa, antes de congelar, quando congelar agora torna o sorteio
   inviável (`sorteios/application/previa.py:63`).

A suíte também passou a ter como reproduzir o caso: `FonteDeTesteSoData`
(`loteria_federal.py:168`) devolve o início do dia, como a Caixa.

**Não conferido aqui.** Não reexecutei a suíte da 102, nem verifiquei se o Edital 72/2026 já
publicado é alcançado pela regra nova. Ela confere a publicação e a Retificação, e não um Edital
publicado antes dela. Para ele continua valendo a saída que a recusa agora descreve.

## 7. O que autorizar, e o que depende de regra

**Recomendo autorizar** (não mudam regra de negócio):

- AUD-RET-01, pelo plano mínimo da seção 5;
- AUD-RET-02, a passagem de bastão da Retificação, na forma da `007`;
- AUD-RET-03, prever a recusa por segregação no detalhe e na confirmação.

**Dependem de esclarecimento**:

- **AUD-RET-05**: o "elaborou" da `FR-021` é quem submete ou quem compõe? Vale para o Edital e para
  a Retificação.
- **AUD-RET-04**: a devolvida se reabre na tela, ou devolver significa recompor?
- **Segundo passo da seção 5**: marca na Lista, sim ou não, e onde.

**Já resolvido na `main`**: as duas lacunas do sorteio, pelo #335 e pelo #337.
