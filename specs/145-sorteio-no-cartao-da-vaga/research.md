# Research: O sorteio de cada vaga no cartão dela (145)

## 1. O que existe

- A página é `portal/templates/portal/selecao.html`, servida por `portal.views` com o contexto de
  `sorteios_do_edital` (`sorteios/application/selectors.py`): duas consultas, uma entrada por
  relação vigente, com os nomes de vaga, marco e lista lidos do conteúdo vigente.
- Cada relação tem endereço próprio, `portal:relacao-de-habilitados`, por identidade. Não existe
  consulta consolidada por vaga.
- A chave da relação é vaga × marco × lista. A lista nula é a ampla concorrência: é o que
  `portal/leitura.py` afirma ao ordenar resultados e o que a página da relação escreve no subtítulo.
- O cabeçalho da página já tem "O que esta seleção oferece", com âncora para cada vaga.
- A relação só congela depois das inscrições: quando o sorteio existe, o cartão já não tem o botão
  de inscrever.

## 2. As alternativas, medidas

Protótipos gerados do modelo real da página, com a folha real, sobre um Edital fabricado: quatro
vagas de nome longo, duas por sorteio com três listas, uma com dois marcos, uma por análise de
títulos. Alturas em pontos de CSS.

| | Atual | A | B | C | C refinada |
|---|---|---|---|---|---|
| Página, 1280 | 5.041 | 5.041 | 2.161 | 2.277 | 2.174 |
| Página, 375 | 6.184 | 6.576 | 4.174 | 4.423 | 3.967 |
| Título da vaga → acesso, 1280 | 1.506 | 219 | 322 | 298 | 291 |
| Título da vaga → acesso, 375 | 2.801 | 344 | 639 | 567 | 508 |
| Bloco do Edital | 4.235 | 4.235 | — | 538 | 258 / 232 |
| Cartão de três listas, 375 | 436 | 540 | 881 | 809 | 595 |
| Acessos a relações | 9 | 18 | 9 | 9 | 9 |

A — links no cartão e lateral intacta. B — tudo no cartão, sem bloco do Edital. C — cartão mais
resumo. As medidas da página variam alguns pontos entre rodadas, porque a segunda acrescentou ao
cenário o resumo da oferta no cabeçalho; as relativas não mudam.

## 3. Decisões

## D-001 — O que é da vaga vai para o cartão; o bloco "Sorteio público" fica com o Edital

A alternativa A resolve a descoberta e dobra os acessos, mantendo os 4.235 px. B perde o lugar que
diz a garantia e o andamento geral. C mantém os dois com um bloco de 258 px. Escolha do usuário,
sobre as medidas acima.

## D-002 — Duas ou mais listas abrem sob um controle; uma só é direta

Com as três listas abertas o cartão ia de 436 para 809 px a 375, e a comparação entre vagas se
perdia. Uma linha por lista, com o nome como acesso, baixava para 716; sob o controle, 595. O estado
e a existência das listas ficam sempre visíveis — é o rótulo do controle que diz "3 listas" —, e o
desenho é o do "documentos" logo acima no mesmo cartão. Recolher sempre, inclusive com uma lista,
esconderia um acesso atrás de um toque sem poupar altura.

## D-003 — O bloco do Edital não lista vagas

A primeira versão de C listava cada vaga com o andamento dela: trocava a repetição por lista pela
repetição por vaga, e o cabeçalho já tem a lista de vagas com âncora. O bloco diz a contagem e a
garantia; o andamento de cada vaga está no cartão.

## D-004 — A lista nula é a ampla concorrência

Conferido no domínio antes de virar rótulo: `portal/leitura.py` ordena os resultados com "o recorte
sem lista **é** a ampla concorrência — o mesmo do sorteio", e `relacao_de_habilitados.html` escreve
"Ampla concorrência" quando a relação não tem lista. O cartão usa o mesmo nome.

## D-005 — O agrupamento é leitura do portal, em memória

`sorteios_por_vaga` mora em `portal/leitura.py`, ao lado de `resultados_por_perfil`, que faz o mesmo
com os resultados. Recebe o que `sorteios_do_edital` já leu; o seletor do sorteio não muda.

## D-006 — Revê-se a apresentação da 021 e a grade da 055, e não os requisitos delas

A `021` escreveu no modelo "ao lado do Cronograma, e não no corpo", com um bloco por lista. A `055`
fixou a área do sorteio na grade só quando ele existe. Os requisitos — a relação alcançável antes
do sorteio, a verificação pública, a área que não se reserva vazia — continuam atendidos e
testados. O que esta feature substitui é a decisão de apresentação: o que é por vaga sai da lateral,
e a ordem em tela estreita passa a ser sorteio, vagas, cronograma, documentos.

## D-007 — A área do cartão é da classificação, e não do sorteio

As classes são `classificacao-da-vaga` e `marco-da-classificacao`. Hoje só o sorteio tem o que dizer
antes do resultado; um método que venha a ter entra na mesma área, sem segunda lateral. Nada é
construído para ele agora.

## D-008 — A relação sem cartão fica no bloco do Edital

Uma Retificação pode retirar do conteúdo vigente a vaga de uma relação já publicada. Sem cartão que
a receba, ela sumiria da página; o ato continua publicado, e a página continua apontando para ele.

## 4. O que esta sessão não fez

- Teste com candidatos: as medidas são de distância e altura, não de compreensão.
- Candidato identificado com inscrição enviada, e inscrições abertas com relação já congelada, não
  foram exercitados no protótipo.
