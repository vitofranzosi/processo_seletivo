# Research — 086

*Decisões técnicas do plano, de 18/10/2026. Numeradas `R-`, porque `D-001` a `D-005` são da spec.*

## R-001 — A trilha das telas de um Edital, medida antes

Lida nos templates e conferida nas capturas de `depois-da-086/antes/`, sobre `cf6d7372`:

| Tela | Trilha no conteúdo, antes | Leva ao Processo? |
|---|---|---|
| Avisos aos candidatos | Processos Seletivos › Edital › **Avisos aos candidatos** | não |
| Histórico do aviso | Processos Seletivos › Edital › Avisos aos candidatos › **Aviso de DD/MM/AAAA** | não |
| Interrupção | Processos Seletivos › Edital › Aviso de DD/MM/AAAA › **Interromper** | não — e salta os Avisos aos candidatos |
| Prévia | Processos Seletivos › Edital › Avisos aos candidatos *ou* Convocação › **Avisar candidatos** | não |

**Decisão**: o bloco `caminho_do_contexto`, com o parcial do produto e os níveis do detalhe do
Edital (`FR-1767` da `078`) — Processos Seletivos, o código do Processo, o Edital — seguidos dos que
cada tela já tinha, e os Avisos aos candidatos na interrupção. Os rótulos da página atual não mudam.
As quatro views já entregam `processo` e `edital`: nenhuma consulta a mais.

**Alternativa descartada**: repetir exatamente os níveis de antes, como a `079` fez nas suas
(`FR-1781` da `079`). Levaria ao cabeçalho a falta do Processo e, na interrupção, a dos Avisos aos
candidatos.

## R-002 — A prévia diz a porta

A prévia é um template só para três views: o aviso de resultado (`voltar` = os Avisos aos
candidatos), o da chamada (`voltar` = a Convocação do marco, com o recorte de lista) e o reenvio
(`voltar` = o aviso anterior). O template de antes decidia o rótulo só pela origem do universo:
*Convocação* se `CHAMADA`, *Avisos aos candidatos* nos demais — e o link era sempre `voltar`. No
reenvio de um aviso de resultado, *Avisos aos candidatos* levava ao aviso anterior; no reenvio de um
aviso de chamada, *Convocação* levava ao aviso anterior.

**Decisão** (D-001 da spec): o reenvio vem primeiro, e se reconhece por `anterior`, que só a view do
reenvio entrega; ele tem os dois níveis — os Avisos aos candidatos, pela rota, e o aviso anterior,
por `voltar`. Depois a chamada, e por fim o resultado. Em toda variante o último link é `voltar`, que
é também o destino de "Cancelar": a trilha e o botão dizem o mesmo lugar.

**Alternativa descartada**: deixar o nível acima ser sempre "a tela de onde se veio" com um rótulo
genérico ("Voltar"). Trilha nomeia lugares; "voltar" é ação, e já existe como "Cancelar".

## R-003 — Os modelos começam na seção

A barra da `076` declara *Modelos de aviso* como seção do grupo Unidade, e a seção atual sai do
endereço (`/gestao/modelos-de-aviso…`). O cabeçalho da `076` já dizia *GPS › Modelos de aviso*; a
trilha do conteúdo dizia *Processos Seletivos › Modelos de aviso*.

**Decisão** (D-002 da spec): na lista, a seção como página atual, sem link, como a lista de Processos e
Minhas Etapas (`FR-1746` da `077`); na edição, a seção como link e o nome do modelo, ou *Novo modelo*.
A view de modelos não entrega `processo`, e não precisa.

## R-004 — O estado vazio

Os três "não há nada" usavam `.nenhuma` — letra pequena e esmaecida, a classe das pendências de uma
linha ("nada novo a avisar", na mesma lista). As telas que a `078` à `080` tocaram usam `.vazio`, a
caixa tracejada, com regra na folha comum desde antes da `076`.

**Decisão**: `<p class="vazio">`, sem `role="status"` — a frase não é resposta a um envio, é o estado
da página ao abrir, como nas Conclusões preservadas da `080`. "nada novo a avisar", dentro da linha
de um marco, continua sem classe: é parte de uma linha, e não o estado da região.

**Medido**: no banco do inventário, os Avisos aos candidatos do 51/2026 têm resultado publicado e
aviso confirmado, e a unidade tem modelos — nenhum dos três estados vazios aparece nas capturas. Eles
são provados por teste e vistos no navegador num Edital sem resultado (o 76/2027, em elaboração).

## R-005 — O rodapé do formulário e a faixa de ações

Na edição de um modelo e na conferência da interrupção, o botão e o link de voltar eram filhos
diretos do `form`, logo depois do último campo. As conferências da `079` e da `080` usam `p.salvar` —
a linha com borda em cima, que separa o ato dos campos —, e a lista de Processos põe a sua única ação
em `p.acoes-do-painel` (`FR-1741` da `077`).

**Decisão**: `p.salvar` nos dois formulários, com os mesmos botões, desenhos e ordem — inclusive
"Cancelar" e "Voltar sem interromper" como `botao secundario`, que é o que eram; a conferência da
inclusão na comissão usa `acao` para o seu "Cancelar e voltar", e trocar o desenho de um botão não é
o que este incremento pede. `p.acoes-do-painel` para "Novo modelo". Nas duas classes já existe regra
na folha comum; nada se acrescenta a ela.

**Alternativa descartada**: `p.botoes-do-aviso`, a linha de botões da folha própria dos avisos. Ela não
tem a borda que separa o ato, e a interrupção não carrega a folha dos avisos.

## R-006 — Testes que mudam

Nenhum teste existente mudou. `tests/interface/test_avisos.py` prende textos e destinos, e não a
trilha; `test_shell_da_gestao.py` prende a seção que sai do endereço, que não muda; os guardiões da
`077` à `080` que dizem "as demais telas ficam com o cabeçalho da `076`" são provados na Auditoria do
Edital, que esta feature não toca. A `FR-1803` da `080` é anotada como emendada.

Os testes novos, em `tests/interface/test_telas_dos_avisos.py`, provam a trilha nas três variantes
da prévia — a da chamada com a fixture `chamada_publicada` da `066`. O módulo de onde ela vem é
transacional, mas a fixture não precisa disso: aqui ela roda dentro da transação que se desfaz, e o
arquivo não tem caso transacional nenhum (code review de 18/10).

## Achados (registrados, não corrigidos)

- **A prévia do resultado aberta pelas publicações do marco** volta, por "Cancelar" e pela trilha, aos
  Avisos aos candidatos, e não à tela de onde a pessoa veio. É o `voltar` que a view entrega desde a
  `066`; dizer a outra porta pediria à view saber por onde se chegou.
- **A prévia da chamada continua fora do inventário visual**: ela pede uma comunicação por publicação
  que o seed não emite (como em 16/10). É provada pelos testes.
- **Os estados vazios não aparecem no inventário** (R-004): o banco tem aviso, resultado e modelos.
  Uma variante "sem nada" pediria um Edital ou uma unidade a mais no seed.

### Achados do code review de 18/10 (registrados, não corrigidos)

- **`.salvar` não quebra a linha.** A regra comum é `display:flex` sem `flex-wrap`; a 375 px, na
  conferência da interrupção, os dois botões encolhem lado a lado e cada rótulo vai a duas linhas
  (+46 px no inventário). Nada estoura. Corrigir é mudar a folha comum, que serve dezenas de telas —
  inclusive as conferências da `079` e da `080` —, e pede o inventário inteiro refeito: fica para quem
  decidir mexer na regra geral.
- **"Aviso de DD/MM/AAAA" sem a hora.** Dois avisos do mesmo dia — o pai e o filho de um reenvio —
  têm na trilha o mesmo rótulo e destinos diferentes; só o `h1`, com a hora, os distingue. O rótulo é
  o que a tela já usava, e a `FR-1941` o fixa: acrescentar a hora é mudar o requisito, e fica com o
  produto.
- **Os níveis até o Edital estão copiados em quatro templates.** Extraí-los num parcial seria o
  movimento natural, mas a decisão 003 da `081` escolheu manter a abertura escrita em cada tela, com
  um guardião, em vez de extrair; esta feature segue a decisão, e não a reabre.
