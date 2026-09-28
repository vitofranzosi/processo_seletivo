# Correções antes do piloto — o que ficou para decisão (28/09/2026)

A ordem era corrigir, das sete unidades abaixo, só o que um candidato ou um operador do piloto vai
encontrar como informação ou dado errado — e só onde houvesse requisito escrito para restaurar. Duas
tinham, e foram corrigidas no mesmo PR deste registro. As outras cinco **não têm requisito que o
código viole**, ou pedem uma escolha que é do usuário, e ficam aqui, sem código.

Cada unidade foi conferida na `main` de 28/09 (`d65f0136`). Nenhum PR posterior à auditoria de 26/09
tocou nelas. A auditoria não foi editada: este registro é a leitura dela no dia.

| RC | Estado na `main` | Requisito | Desfecho |
|---|---|---|---|
| RC-47 | aberto: `<h1>` e `<title>` com o título do Processo; o do Edital não aparecia na página | `009` FR-014 (o detalhe apresenta o título), lido com `001` FR-007 (o título é do Edital) | **corrigido** |
| RC-49 | aberto: a lista oferecia *Continuar inscrição*; o rascunho e a revisão não diziam que o prazo acabou | `009` FR-032 (rascunho encerrado fica só para consulta) | **corrigido** |
| RC-76 | aberto na parte não executável | nenhum | decisão de modelo — abaixo |
| RC-22 | aberto | nenhum | decisão de modelo — abaixo |
| RC-119 | aberto | nenhum; a `047` o registrou como pergunta de domínio | decisão — abaixo |
| RC-62 | aberto | nenhum | decisão curta — abaixo |
| RC-118 | aberto | o requisito escrito **permite** o comportamento de hoje | decisão — abaixo |

## RC-76 — o prazo de recurso da tela diverge do Cronograma

**Conferido.** A janela é relativa ao ato que divulgou o resultado
(`backend/processo_seletivo/recursos/domain/janela.py`), e a data que a tela diz é a que a
interposição aplica — a `047` fez a página pública do resultado e a do Edital dizerem essa data.
O Evento *"Prazo para recurso"* do Cronograma é texto livre: nada o liga ao marco que abre a janela.
As duas datas continuam podendo discordar, e a tela diz a verdadeira.

**Por que não se corrige.** Confrontar as duas exige saber qual Evento é o do recurso de qual
resultado, e o modelo não tem esse vínculo. Casar por texto do tipo do Evento foi vetado (a mesma
razão da `009`, FR-002, para o período de inscrições). Nenhuma spec pede o confronto.

**A decisão.** Designar o Evento de recurso — como `isRegistrationPeriod` designa o de inscrições —
e decidir quem prevalece quando discordarem: a publicação avisa, impede, ou a janela passa a ler o
Cronograma. É spec própria. Até lá, o operador do piloto precisa conferir à mão que o Cronograma
publicado e a janela declarada dizem a mesma coisa.

## RC-22 — o Evento só com data sai "às 00h" no documento

**Conferido.** A composição exige data **e** hora (`interface/templates/interface/_evento.html`, o
`datetime-local` com `required`), e o documento escreve o instante como o recebe
(`publicacoes/infrastructure/humano.py`, `instante`). Um Evento que o Edital real publica só com a
data é cadastrado com a hora `00:00` e sai *"às 00h"*. E a meia-noite como hora é regra deliberada
do renderizador: a docstring de `instante` registra que *"um prazo que termina à meia-noite precisa
dizer que termina à meia-noite"*.

**Por que não se corrige.** Omitir a hora zero no documento desfaria essa regra, e o sistema não
tem como distinguir meia-noite declarada de hora ausente. Falta o estado "sem hora declarada" no
modelo de instante do Evento, e nenhuma spec o define.

**A decisão.** O Evento passa a aceitar data sem hora — e então o que a régua da fase, o período de
inscrições e o documento fazem com ele —, ou a composição passa a exigir hora sempre. A auditoria
agrupa esta com o RC-23 e o RC-24 (B-16). Até lá, o operador do piloto deve declarar a hora que o
Edital real pratica, e não deixar `00:00`.

## RC-119 — o período de inscrições `CANCELADO` continua recebendo

**Conferido.** `periodo_de_inscricoes` e `recebe_inscricoes` (`inscricoes/domain/periodo.py`) leem
as datas do Evento designado e o status do Edital, e nenhuma lê o `status` do Evento. Os testes
`test_o_periodo_marcado_como_cancelado_segue_a_regua_do_periodo` e
`test_periodo_cancelado_a_gestao_le_o_cancelamento_e_o_portal_le_o_periodo` prendem o comportamento.

**Por que não se corrige.** A `045` (FR-736) fez do `CANCELADO` a única declaração do Evento, e
deixou expressamente fora o portal e o documento. A `047` registrou que decidir se o período
cancelado fecha o recebimento *"é regra de domínio da inscrição, e não projeção"*. Nenhum requisito
diz que fecha. E o caso só se produz pela API: nenhuma tela declara `CANCELADO`.

**A decisão.** Junto do RC-118: o que, além do estado do Edital e das datas do período, fecha o
recebimento. No piloto, ninguém chega a este caso sem usar a API.

## RC-62 — a Mesa aceita concluir avaliação de inscrição que já tem Resultado na Etapa

**Conferido.** `pode_avaliar_inscricao` (`avaliacoes/domain/autorizacao.py`) compõe alocação,
participação e atribuição; `participa_da_etapa` (`resultados/application/prontidao.py`) olha
Resultado eliminatório nas Etapas **anteriores** e a faixa do corte, e não Resultado na própria
Etapa. `concluir` (`avaliacoes/application/avaliacao.py`) não confere nada além disso. Nenhum
Resultado é alterado — é imutável —, e a avaliação tardia fica inelegível; o que sobra é o par
contraditório na trilha.

**Por que não se corrige.** A `012` e a `013` não escrevem a regra, e ela não pode ser um bloqueio
simples: a reavaliação determinada pela `018` é justamente avaliar quem já tem Resultado vigente na
própria Etapa. O anexo 1 da auditoria pede *"decisão curta de governança: aviso ou bloqueio com
exceção da reavaliação"*, e o manual já instrui a presidência a registrar a ocorrência antes de as
avaliações pendentes serem concluídas.

**A decisão.** Bloquear, com a exceção das reavaliações pendentes, ou só avisar na Mesa. Decidida,
a correção é pequena e cabe num PR.

## RC-118 — encerrar o Processo não exige Editais em estado final

**Conferido.** `ensure_processo_can_be_closed` (`processos/domain/finalizacao.py`) exige só o
Processo ativo; o cancelamento, ao lado, exige os Editais finais. Um Edital publicado de Processo
encerrado continua recebendo inscrição dentro do período, e
`test_processo_encerrado_com_edital_aberto_diz_o_fato_e_continua_recebendo` prende isso.

**Por que não se corrige.** O requisito escrito **autoriza** o comportamento: a `001`, FR-034, põe
a exigência dos Editais finais só no cancelamento do Processo, e a `047`, FR-762 e `D-003`, diz o
encerramento do Processo como fato e deixa o Edital seguir o próprio estado e período. A `047`
registrou a pergunta como *"decisão pendente, para outra feature"*. É o item 14 da §13 da auditoria.

**A decisão.** Exigir os Editais em estado final para encerrar o Processo, como o cancelamento já
exige, ou fazer a regra do recebimento ler o Processo. Até lá, o operador do piloto não deve
encerrar um Processo com Edital ainda recebendo inscrição: a página diz o encerramento, e o sistema
continua recebendo.
