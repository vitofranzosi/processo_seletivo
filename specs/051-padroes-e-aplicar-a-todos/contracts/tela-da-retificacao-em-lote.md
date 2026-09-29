# Contrato — o gesto na tela de Retificação (P2)

A tela é a de sempre (`/gestao/editais/<edital>/retificar`), e o formulário é o mesmo: os campos do
conteúdo vigente, os acréscimos e a justificativa. O gesto acrescenta botões nos cartões e um bloco na
conferência. Nenhum caminho normativo chega ao HTML (FR-019 da `002`): a origem viaja pela referência
do cartão (`g14`), que só significa alguma coisa contra a versão base que atravessa o formulário.

## Os botões (UX-110)

Com dois ou mais Perfis no conteúdo vigente, cada cartão de origem oferece o gesto das suas unidades.
O alcance é dito uma vez, no rótulo do grupo — *"Aplicar aos demais Perfis (6):"* —, e cada botão
mostra a unidade (*"Janela recursal"*); o nome acessível do botão diz as duas — *"Aplicar a janela
recursal aos demais Perfis (6)"* —, e contém o texto visível (WCAG 2.5.3). O cartão tem a âncora
`cartao-<g>`, que o bloco do gesto na conferência alcança por *"Ir ao cartão de origem"*.

| Cartão | `aplicar` | Unidade |
|---|---|---|
| Marco | `janela:<g>` | a janela recursal |
| Marco | `corte:<g>` | a regra de corte |
| Marco | `criterios:<g>` | os critérios de desempate |
| Marco | `campos_do_marco:<g>` | forma da ordem, Etapas, combinação, normalização e arredondamento |
| Perfil | `callForm:<g>` | a forma de convocação |
| Perfil | `vacancyReversion:<g>` | a reversão de vaga reservada |
| Modalidade | `modalidade:<g>` | a Modalidade, pelo código |

## Declarar o gesto

Envio do formulário inteiro com `aplicar=<unidade>:<g>`. **Resposta**: 200, a tela com o digitado
reexibido e a conferência no alto, que traz:

- a tabela de sempre, com as Alterações **digitadas**;
- um bloco por gesto declarado, intitulado com o verbo do botão (*"Aplicar a janela recursal do
  Perfil POLO01 aos demais Perfis"*), com a frase do alcance (*"6 mudam, 1 fica fora do alcance"*,
  UX-113) e, só quando há caixa, *"Desmarque o Perfil que diverge de propósito"*; uma linha por
  Perfil destino na ordem dos Perfis (UX-111) — código, denominação, efeito numa palavra e, na
  coluna do que muda, o *antes → depois* de cada campo com os rótulos da tela ou o motivo de quem
  fica fora, com os dois valores e a razão do contrato —; a linha sem mudança atenuada e a fora do
  alcance com fundo; a caixa `gesto_destino:<gesto>=<perfil>` marcada por padrão em *nasce* e
  *substitui*; e o botão `desfazer_gesto=<gesto>`;
- acima da tabela do digitado, quantas Alterações vêm do digitado e quantas dos gestos; sem
  Alteração nenhuma, o título não mostra contagem e diz *"Nenhuma Alteração a criar ainda."*;
- as consequências do ato (FR-941): as ordens que ficam obsoletas, os recortes que nascem sem ordem e
  os marcos com resultado divulgado cuja janela muda;
- o botão *Criar Retificação*, com o número de Alterações do ato — e só quando há Alteração a criar.

O formulário envia para o endereço da tela **sem âncora** (`action` explícito): depois de um
*"Ir para"* ou de um *"Ir ao cartão de origem"*, a tela que volta abre no alto, na conferência.

O gesto viaja em `gesto=<unidade>:<g>` (um por gesto, na ordem em que foram declarados),
`gesto_mostrado:<gesto>=1` e `gesto_impressao:<gesto>`. Declarar de novo o mesmo gesto não o
duplica. **Nada é gravado.**

Origem que não declara a unidade → 200, a tela com a recusa *"… não declara …: não há o que
aplicar"*, e o gesto não é declarado (R-013).

## Conferir de novo

*Ver o que vai mudar* recalcula todos os gestos declarados sobre o que está digitado agora, lendo as
caixas de quem já foi mostrado, e devolve a conferência com a impressão de agora.

## Confirmar

*Criar Retificação* (`confirmar=1`), com a justificativa:

- Impressão de cada gesto igual à recalculada → cria **uma** Retificação com as Alterações digitadas
  e as dos destinos marcados que não estão fora do alcance, registra cada gesto na trilha na mesma
  transação, e redireciona para a Retificação.
- Impressão diferente → 200, a conferência de agora, com *"O que estava na tela mudou depois da
  conferência. Confira de novo antes de criar a Retificação."*; nada criado.
- Gesto sem nenhum destino marcado → 200, com *"Nenhum Perfil marcado em …: marque um Perfil ou
  desfaça o gesto."*; nada criado.
- Recusa do ato (as guardas da `048`, o `RC-130`, a validação da publicação) → 200, como hoje.

## Permissão

A de sempre, `retificacao:elaborar`. Sem ela, a tela é de leitura e não oferece o gesto.
