# Research: O caminho do candidato até a convocação e o Requerimento de Matrícula

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-10-06

As decisões desta feature nascem em `D-001`. Decisão de outra feature é citada pela feature e pelo
número dela, por extenso.

---

## O que foi conferido antes de decidir

| Pergunta | Onde se respondeu | Resposta |
|---|---|---|
| Algum template do portal leva à convocação? | `grep -rn "portal:convocacao" backend/processo_seletivo/portal/templates` | Nenhum. A rota só aparece em `tests/interface/test_portal_convocacao.py`. |
| Para onde aponta a mensagem? | `interface/views.py`, quatro chamadas a `convocar_e_comunicar` e aos gestos da `050` | `reverse("portal:inscricoes")`, um endereço só para o lote inteiro. |
| Onde o Requerimento tem entrada? | `portal/templates/portal/_cartao_do_requerimento.html` | Só em "Sua inscrição", e só no momento *na inscrição*. |
| O que a `029` prende sobre custo? | `tests/integration/requerimentos/test_orcamento_de_consulta.py` | **Zero** consultas às tabelas do requerimento na lista e no acompanhamento; a docstring do segundo diz que *"o caminho para o requerimento é o cartão da inscrição e a tela da convocação"* — e a tela da convocação não tem caminho nenhum. |
| Qual regra de vigência a tela da convocação usa? | `portal/views.py::convocacao` | A vigente mais recente: `sucessoras__isnull=True`, ordenada por `-criado_em`. |
| Qual regra o requerimento usa? | `convocacao/application/selectors.py::chamada_em_aberto` | A vigente **sem desfecho**, qualquer que seja a ordem. |
| A varredura de vocabulário da `019` acha template novo sozinha? | `tests/test_vocabulario_da_convocacao.py`, `DA_019` | Não: a lista é literal. |
| Há cenário de teste com convocação real **e** momento *na convocação*? | `tests/interface/test_portal_sucessao.py` | Sim — `montar_cenario_da_convocacao(..., publicar=...)` com `declarar("AT_CALL")`. O cenário padrão da `019` não declara o requerimento. |

---

## D-001 — Uma regra de vigência só, num seletor da `019`

**Decisão.** `convocacao/application/selectors.py` ganha `vigentes_por_inscricao(inscricao_ids)`:
devolve, para cada inscrição pedida, a convocação vigente mais recente — a mesma regra da tela da
convocação —, com desfechos e comunicações já carregados, em número fixo de consultas. A view
`portal:convocacao` passa a usá-lo; a lista e o acompanhamento também.

**Por quê.** A `FR-1100` exige a mesma convocação nos três lugares. Três consultas escritas à mão
divergiriam na primeira mudança — e a `019` já pagou uma vez a confusão entre *vigente* e *em
aberto* (`convocar.py::_em_aberto_da_pessoa`).

**Alternativas.** `chamada_em_aberto` em cada tela: descartada, porque some com a convocação
concluída, e a `FR-1091` e a `FR-1093` exigem mostrá-la. Repetir a consulta da view na lista:
descartada pela razão acima.

**O que não muda.** `chamada_em_aberto` continua sendo o que o requerimento consulta. As duas
perguntas são diferentes — *qual convocação mostrar* e *a chamada está em aberto* — e a `FR-1099`
proíbe que a tela responda a segunda por conta própria.

## D-002 — A lista lê convocações por conjunto, e não lê o requerimento

**Decisão.** A lista pede as convocações das inscrições **enviadas** da identidade numa leitura por
conjunto; sem inscrição enviada, não pergunta nada. Nenhuma tabela do requerimento é lida.

**Por quê.** A `FR-1092` e o zero da `029` (`T063`). Uma consulta por item é invisível com três
inscrições e fatal com trezentas — é o defeito que `tests/performance/test_area_do_candidato.py`
existe para pegar. E a `029` decidiu que o estado do requerimento não aparece em listagem: *"se lê
na tela dele"*.

**Alternativa.** Pôr "Preencher Requerimento de Matrícula" direto na lista: descartada. Custaria a
leitura do requerimento por item e desfaria a decisão da `029`. O chamado fica a um clique, na
convocação (`SC-425`: dois cliques).

## D-003 — "Ver convocação" é a ação principal; "Acompanhar" vira secundária

**Decisão.** Com convocação aberta, a ação principal do item é "Ver convocação". "Acompanhar"
continua no item como link simples.

**Por quê.** A lista tem **uma** ação principal por item (`SC-UX-005`, comentário de
`_item_da_lista`), e com convocação aberta a coisa urgente é o prazo. Tirar "Acompanhar" do item
faria a pessoa convocada perder o caminho para o resultado e para o recurso.

## D-004 — Convocação concluída na lista é nota, e não ação

**Decisão.** Com desfecho registrado, o item ganha uma linha de texto discreto — *"Convocação:
<espécie do desfecho>"* — e a ação principal continua "Acompanhar". Decidido no `/speckit-clarify`
de 06/10.

**Por quê.** Quem volta meses depois vê o estado sem abrir nada, e a leitura já está paga pela
`D-002`. Ação não há: a convocação concluída não pede nada da pessoa, e a tela continua a um clique
pelo acompanhamento.

## D-005 — O acompanhamento só fala de convocação quando há convocação da pessoa

**Decisão.** A seção "Convocação" aparece quando a inscrição tem convocação vigente — aberta ou
concluída. Sem ela, nada.

**Por quê.** A frase da tela da convocação para quem não foi chamado — *"quem está na lista pode ser
chamado quando uma vaga vagar"* — é dita a quem navegou até lá. No acompanhamento ela seria dita a
**toda** inscrição do recorte, inclusive a eliminada, que não está em lista nenhuma: é afirmação que
a tela não pode sustentar. E é o mesmo critério do bloco de resultado: a ausência se diz em ausência
de dado (`FR-056` da `017`).

**Alternativa.** Repetir no acompanhamento as duas ausências da `FR-294`: descartada pela razão
acima, e porque custaria uma consulta a mais em todo acompanhamento.

## D-006 — O requerimento só é lido onde a convocação existe

**Decisão.** O acompanhamento consulta a política do requerimento **somente** quando há convocação
vigente da inscrição. A tela da convocação a consulta sempre que há convocação.

**Por quê.** Preserva o zero da `029` para o acompanhamento de quem não foi convocado — o caso do
teste `test_o_acompanhamento_nao_toca_a_feature`, que continua verde sem ser reescrito. Quem foi
convocado paga a leitura, e é justamente quem precisa dela.

**Custo esperado.** `apurar` lê o requerimento vigente (1 consulta) e, no momento *na convocação* ou
com requerimento enviado, a chamada em aberto (3). É constante: não depende de quantas inscrições,
convocações ou desfechos existem.

## D-007 — O chamado ao requerimento é um parcial, e traduz o estado de leitura da `029`

**Decisão.** Um parcial `_chamado_do_requerimento.html`, incluído na tela da convocação e na seção do
acompanhamento:

| Estado de leitura (`FR-405` da `029`) | O que aparece |
|---|---|
| disponível | **Preencher Requerimento de Matrícula** (ação principal) |
| em preenchimento | **Preencher Requerimento de Matrícula** (ação principal) |
| enviado | *Conferir o Requerimento de Matrícula enviado* (link) |
| ainda indisponível | nada |
| não aplicável | nada |

**Por quê.** O texto da ação é o que o usuário pediu, igual nos dois estados abertos — a tela do
requerimento já diz se há rascunho. *Conferir* leva à mesma tela, que oferece *conferir e atualizar*
quando a `FR-410` da `029` se cumpre. E o que não leva a nada não aparece: um botão que só recusa é
pior que nenhum (`FR-013` da `018`).

## D-008 — Só a tela da convocação registra leitura

**Decisão.** A lista e o acompanhamento não gravam nada na trilha. Decidido no `/speckit-clarify` de
06/10.

**Por quê.** A trilha responde *"a pessoa abriu a convocação?"*, e a resposta continua tendo um
sentido só. Gravar a cada visita ao acompanhamento faria uma linha append-only por recarga de página,
e mudaria o que a `FR-288b` da `019` significa sem que ela fosse revista.

## D-009 — A mensagem não muda

**Decisão.** Endereço e texto continuam os mesmos: *"Minhas inscrições"*, que passa a mostrar a
convocação. Decidido no `/speckit-clarify` de 06/10.

**Por quê.** O endereço é montado na gestão (fora de escopo) e os gestos em lote da `050` mandam um
endereço só para o lote inteiro. A lista é o destino que serve aos dois — e, com a `D-003`, a
convocação fica a um clique dele.

## D-010 — As ações do cartão ficam acima do título esticado

**Decisão.** Em "Minhas inscrições", o título do cartão estica a área de clique sobre o cartão
inteiro (`.selecao a.titulo::after`, posicionado). As ações do item recebem posição e camada próprias
para ficarem acima dele.

**Por quê.** Elemento posicionado pinta acima do que não é, e nenhuma regra da folha posiciona
`.principal` dentro do cartão. A hipótese é que hoje o clique do mouse em "Acompanhar" caia no
título e leve a "Sua inscrição". **Medir antes de corrigir**: `document.elementFromPoint` no centro
de "Acompanhar", no seed, antes e depois. Confirmada ou não, "Ver convocação" precisa estar acima do
título — sem isso, a `FR-1090` não se cumpre com o mouse.

## D-011 — Os templates novos entram na varredura da `019`

**Decisão.** Os dois parciais novos entram em `DA_019` de `tests/test_vocabulario_da_convocacao.py`.

**Por quê.** A lista é literal, e template novo escapa dela em silêncio. São justamente as frases
novas que a `UX-147` manda conferir.

## D-012 — A `050` disse que o portal não muda

**Registro.** A `050` (spec, *"O portal do candidato não muda"*) falava do conteúdo da convocação, e
ele continua igual. Esta feature muda a **navegação** do portal; o texto da `050` não é reescrito,
porque spec mergeada é registro do que se decidiu naquele dia.
