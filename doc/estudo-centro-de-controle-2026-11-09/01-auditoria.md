# Entrega 1 — Auditoria da experiência atual

**Base.** `main` em `0254fb91`. Os 15 cenários de treinamento (134) carregados num banco isolado
(`ps_cc_centro`). As telas foram lidas como `treino.presidencia`, `treino.gestao` (Gestor),
`treino.publicacao` (Publicador) e `treino.avaliacao1`. Todas as capturas estão em
[`capturas/`](capturas/).

**O que esta auditoria é.** Inspeção heurística mais medição automatizada por Playwright. **Não**
houve teste com operadores. O mesmo vale para os cenários: o nome de cada um não foi tomado como
prova do estado dele. O estado foi lido de `interface/andamento.do_edital`, a função que já decide
o detalhe do Edital, e conferido na tela de cada ato.

**Ponto de partida.** O estudo de 06/11 e as specs 126, 127 e 133 já resolveram boa parte do que o
pedido descreve:
- "O que fazer agora" deixou de ser igual em todo Edital publicado;
- as providências separam "sua", "de outro papel" e "em espera";
- cada lista tem uma matriz de sete situações.

O que resta não é falta de derivação. É **arquitetura da informação**: o estado existe, mas a página
não o diz em palavras, mistura operação com administração, e esconde o detalhe por lista no meio da
página. Por isso as hipóteses do pedido foram tratadas como hipóteses, uma a uma.

## Hipóteses do pedido, verificadas

| # | Hipótese | Veredito | Evidência |
|---|---|---|---|
| H1 | "Ativo"/"Publicado" não representam o andamento | **Confirmada** | Depois da publicação o cabeçalho só tem o selo "Publicado". A trilha some por decisão da 127 (D-002), e nada a substitui em palavras. Ver `atual-c06-edital.png` |
| H2 | Encerrar/Cancelar com destaque excessivo | **Confirmada**, nas duas páginas | No Edital, para o Gestor, Encerrar e Cancelar ficam **dentro** de "O que fazer agora", em vermelho, logo abaixo de "Congelar a relação" (`atual-c06-edital-gestor.png`). No Processo do C12, o único conteúdo de "O que fazer agora" é o aviso de que encerrar e cancelar estão impedidos (`atual-c12-processo.png`) |
| H3 | Detalhamento disperso | **Confirmada** | A ordem do detalhe é: O que fazer agora → Quem atuou → Retificações em curso → Documentos publicados → **Andamento** → Avisos → Validação. A matriz por lista vem recolhida, depois de duas seções de histórico |
| H4 | "ordenação · conduzir o marco · corte · ocupação · convocação" pressupõe conhecimento | **Confirmada** | Os cinco links aparecem sem explicação. Nenhuma tela define "congelar", "semente" ou "apuração"; só existe "Termos desta tela" em cinco telas de ato |
| H5 | "relação 0 de 2" não explica | **Confirmada** | A linha "relação 0 de 2 · sorteio 0 de 2 · corte 0 de 2 · apuração 0 de 2" conta atos e não distingue "falta fazer" de "ainda não dá" |
| H6 | Prazo, bloqueio, providência e advertência sem hierarquia | **Parcial** | Dentro do cartão, a 127 já separa as três (Sua, Aguarda, de outro papel). Fora dele não: a "Validação do conteúdo" pós-publicação e o aviso de conteúdo imutável competem com elas |
| H7 | Sem jornada visual | **Confirmada**, e por decisão | A 127 tirou a trilha pós-publicação (D-002) e deixou a barra de fases fora do escopo ("Fica fora"). A questão volta como decisão D-1 do README |
| H8 | Muita navegação e rolagem para reconstruir o estado | **Confirmada** | Medido: a situação operacional dita em palavras está **ausente** nos três Editais medidos, e o histórico de um ato feito só aparece abrindo um bloco recolhido ([validacao-automatizada.txt](validacao-automatizada.txt)) |

## Achados

Severidade: **Alta** quando leva a ato errado, ou a não saber o que fazer; **Média** quando custa
tempo ou induz a uma leitura errada; **Baixa** quando é ruído.

### A-01 · Alta — o estado operacional não é dito em lugar nenhum
Publicado o Edital, a página não responde "onde estamos". A resposta precisa ser montada a partir de
três peças:
- o selo "Publicado";
- a linha de contagens do Perfil, que vem recolhida;
- as providências.

No C12, a seleção está ao mesmo tempo em classificação (a lista PPP sem ordem), aguardando o prazo
de recurso, com vagas apuradas e conferindo documentos. Nenhuma frase diz isso.

- **Impacto:** quem chega ao Edital pela primeira vez não sabe em que fase ele está.
- **Oportunidade:** a derivação já tem tudo, ponto a ponto e lista a lista. Falta agrupar e dizer.

### A-02 · Alta — a página do Processo contradiz a do Edital
No C12, para a presidência, a página do Processo diz *"Nenhum ato disponível para seus papéis
nesta situação"*. O Edital do mesmo Processo tem 4 providências, e 2 delas são da presidência
(`atual-c12-processo.png` × `atual-c12-edital.png`).

- **Causa:** o cartão do Processo só conhece os atos do ciclo de vida do Processo
  (`atos_processo.disponiveis`). A agregação das providências por Edital é a "Frente B" da 129,
  ainda pendente.
- **Impacto:** quem começa pelo Processo conclui que não há o que fazer.

### A-03 · Alta — no sorteio, a tela oferece observar a extração antes do congelamento
Em `Sorteio — Sorteio público` do C06, o botão **"Observar a ocorrência 806001106 na fonte"** aparece
com as duas relações ainda não congeladas.

A derivação da 127 já diz *Depois* para a semente, com a razão "nenhuma relação deste marco está
congelada". O guia da equipe (C06) avisa: *"congele as duas antes de observar a ocorrência: uma
relação congelada depois de conhecida a semente é recusada"*.

- **O conflito:** a tela convida a um ato de um clique que inviabiliza o passo anterior. Saímos dele
  por Retificação e relação sucessora (guia da jornada do sorteio, cap. 4 e 6). A tela e a derivação
  divergem.
- **Não verificado:** o ato não foi praticado. Pode ser que observar com zero relações congeladas
  seja recusado pelo comando; a tela, de todo modo, o oferece.
- **Relação com o que já existe:** casa com o item P1 do guia da jornada do sorteio (confirmação em
  duas fases para congelar e sortear), que segue pendente.

### A-04 · Média — a providência paralela tem o mesmo peso da principal, sem dizer que é paralela
No C06, "Distribuir 10 inscrições sem avaliador suficiente — Análise de títulos" aparece com o mesmo
destaque de "Congelar a relação".

A derivação **sabe** que o sorteio não lê essa Etapa: ela é esperada, mas nada a jusante a consome
(`expectativa_das_etapas`, D-019 da 127). O próprio guia de treinamento pede ao aluno que *"anote se
a presença dela confundiu você"*.

- **Impacto:** quem conduz pode achar que precisa avaliar os títulos antes de sortear.

### A-05 · Média — atos de fim de ciclo competem com a operação diária
Como na H2: no Edital, Encerrar e Cancelar ficam no mesmo cartão que as providências. No Processo,
o impedimento de encerrar é o primeiro e único conteúdo de "O que fazer agora".

- **Impacto:** o destaque fica com o ato mais raro e mais perigoso.

### A-06 · Média — vocabulário técnico sem explicação no lugar da decisão
"Relação", "universo ainda não comprometido", "recorte", "semente", "corte", "faixa", "apuração",
"ocupação", "conduzir o marco" e "geração" aparecem sem definição.

O estudo de 06/11 recomendou definir "semente" e "relação" em "Termos desta tela", e **isso não foi
feito**. Os guias que explicam esses conceitos existem, mas são HTML soltos em `doc/`:
`gps-por-dentro`, guia da jornada do sorteio e guia dos documentos. Nenhum deles é alcançável de
dentro do produto.

### A-07 · Média — contagens que não somam
No C06, o resumo do Perfil diz *"1 providência em aberto"*, enquanto o cartão do mesmo Edital diz
*"2 providências em aberto · 2 são suas"*.

- **Causa, deliberada:** as providências das Etapas são do Edital, e por decisão do código
  (comentário em `resumo_do_perfil`) ficam no nível 1 e em "Etapas X de Y", fora da contagem do
  Perfil. O defeito não é a conta: são dois números com as mesmas palavras e escopos diferentes, sem
  que nenhum diga o seu escopo.
- **Impacto:** a pessoa desconfia de um dos dois números, e não sabe de qual.

### A-08 · Média — o texto da espera sugere um ato já praticado
No C08 e no C12, a espera diz: *"Publicar o resultado definitivo — … Aguarde o encerramento, **ou
publique como resultado preliminar**"*. O preliminar **já** foi publicado nos dois Editais: a célula
mostra a nota "resultado preliminar".

- **Causa:** é a mensagem genérica `JANELA_ABERTA` de `divulgacao/domain/publicabilidade.py`, a mesma da tela de publicação, onde a escolha entre preliminar e definitivo faz sentido. Na providência, ela é lida sem olhar o que já está publicado. A `RECURSO_PENDENTE` tem o mesmo final ("…ou publique como resultado preliminar").

### A-09 · Média — a providência de lista vazia não diz que a lista é vazia
"Emitir a ordem — PPP" aparece no C08, no C12 e no C14, Editais em que **ninguém** concorre pela
PPP. A tela do ato explica: *"a ordem vazia é um fato normativo, e emiti-la declara que ninguém
concorreu ali"*. A providência não diz nada disso.

- **No protótipo:** quando essa é a única providência da pessoa, ela vira **"Sua próxima ação"**
  (C08). É a prova de que destacar uma ação exige saber o que ela é. Ver a lacuna G-1 do mapa.

### A-10 · Média — "Próximos marcos" do Processo lê só o cronograma declarado
No C12, o Processo lista *"Aplicação da prova — 04/12/2026"* e *"Resultado final — 29/12/2026"*. Nesse
mesmo Edital a ordem já foi emitida e há convocados entregando documentos.

A causa é dupla:
- **Dado da fixture.** O gerador da 134 pratica hoje os atos que o cronograma declara para o futuro.
- **Desenho da aplicação.** O bloco não cruza o cronograma com o estado operacional: o
  `EventoCronograma.status` é declarado (inventário da supervisão, 09/09). Num certame real, um ato
  adiantado ou atrasado produz a mesma incoerência.

### A-11 · Baixa — a validação do conteúdo continua na página operacional depois da publicação
"A Etapa «Análise de títulos» não está vinculada a nenhum Evento do Cronograma" aparece em todo
cenário e não pede gesto nenhum, porque o conteúdo publicado não muda. É informação de
histórico, e ocupa o fim da página operacional.

### A-12 · Baixa — o detalhe por lista mora num `<details>` dentro da linha do Perfil
A matriz da 127 é a melhor peça de leitura da página, e precisa de um clique numa linha de texto
corrido para aparecer. Depois de aberta, rola na horizontal a 1440 px (`atual-c12-matriz-aberta.png`).

## Defeito de dado × defeito da aplicação

| Observação | Natureza | Por quê |
|---|---|---|
| C06 tem uma Etapa "Análise de títulos" num Edital de sorteio | **Fixture**, com efeito real de UX | O marco enumera a Etapa (receita da 134); a aplicação a deriva certo. O que é da aplicação é não dizer que ela é paralela (A-04) |
| Cronograma com prova em 04/12 e atos já praticados (C12) | **Fixture**, e também **aplicação** | Ver A-10 |
| "Etapa não vinculada a Evento do Cronograma" em todos os cenários | **Fixture** | As Etapas da receita não têm evento. A persistência do aviso na página operacional é A-11 |
| "Emitir a ordem — PPP" com zero inscritos na PPP | **Aplicação** | A ordem vazia é ato legítimo; o que falta é a providência dizer isso (A-09) |
| Processo "sem ato" com Edital cheio de providências | **Aplicação** | A-02 |
| "ou publique como resultado preliminar" com o preliminar publicado | **Aplicação** | A-08 |
| "Observar a ocorrência" antes do congelamento | **Aplicação** | A-03 |
| Nenhum cenário termina concluído | **Limite do catálogo da 134** | O C14 para antes da convocação. A situação 5 do pedido (seleção concluída) é fixture no protótipo, e a tela diz isso |
| Nenhum cenário tem dois Perfis, dois Editais no Processo ou vários marcos | **Limite do catálogo da 134** | A proposta trata esses casos por construção (um bloco por Perfil, um item por Edital), mas eles **não foram vistos** com dado real |

## O que a tela atual já faz bem, e o protótipo preserva
- As três famílias de providência: sua, de outro papel e em espera. "Sua" é texto e não só cor
  (127).
- A espera como **recomendação**, distinta de impedimento (133, R2).
- O link de cada providência só para quem abre a tela do ato.
- O conteúdo imutável nomeia a permissão, e não uma pessoa (037).
- O andamento não derruba a página: sem derivação, o cartão volta ao de antes (127).
