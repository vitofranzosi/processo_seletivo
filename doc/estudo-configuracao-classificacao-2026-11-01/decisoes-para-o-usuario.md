# Decisões que este estudo não toma

Cada item abaixo muda o que o GPS grava, publica ou exige — ou muda o que uma regra existente
significa para quem opera. Por isso é do usuário (governança), e não da implementação. O estudo só
expõe as opções e o custo de cada uma. A recomendação do estudo vem marcada, sem valor de decisão.

## D-1 · A marca classificatória: declarada, proposta ou deduzida?

**O que é hoje.** `EtapaAvaliacao.classificatory` é marcado à mão na tela de Etapas. Efeitos no
sistema:

- autoriza a Etapa a entrar num marco ([validation.py:794](../../backend/processo_seletivo/editais/domain/validation.py), `milestone_stage_not_classificatory`);
- filtra a lista de Etapas e de alvos de desempate ([views.py:3142](../../backend/processo_seletivo/interface/views.py));
- sai no documento como "caráter classificatório" (`pdf.py`, `CARATER_DA_ETAPA`);
- é retificável (`mutabilidade.py`).

A consequência local da Etapa não depende dela ([regra.py](../../backend/processo_seletivo/resultados/domain/regra.py)
diz isso por escrito). O efeito prático é tornar possível um estado inválido (marco que usa Etapa
não marcada) e esconder Etapas da lista do marco. No diário (A7), escondeu a documental de quem
procurava "exigir" essa etapa.

| Opção | O que muda | Custo e risco |
|---|---|---|
| (a) Manter manual | Nada no domínio. A interface mostra os usos ao lado da caixa e, ao desmarcar, lista as ordens afetadas com "restaurar" ou "retirar desta ordem" (protótipo, modo "manual, como hoje") | Continua havendo um campo cujo único efeito é poder ficar incoerente com os usos |
| (b) Propor ao usar | Usar a Etapa numa ordem marca a caixa, com aviso. Desmarcar com usos pede escolher entre os dois caminhos de (a) | Pouca mudança. O campo continua sendo declaração do operador, só que coerente por construção |
| (c) Deduzir dos usos | Ao gravar, `classificatory` = "alguma ordem ou critério de desempate usa a Etapa". A tela mostra o valor deduzido e o porquê (protótipo, modo padrão) | Muda o significado de um campo publicado. Precisa decidir se existe Etapa "classificatória" que nenhuma ordem usa, e o que fazer com o acervo que tiver esse caso |

**Recomendação do estudo:** (b) agora, e (c) só se o acervo mostrar que (b) nunca diverge.

## D-2 · Peso: onde se edita?

O peso pertence à Etapa e vale em todos os marcos que a usam (`combinacao.py`). Hoje ele se edita
em Etapas, e a Classificação só avisa quando falta. O protótipo deixa editar nos dois lugares,
mostrando "o mesmo em todos os usos" e a lista desses usos. A dúvida a decidir é se a edição a
partir do marco deve pedir confirmação quando há outros usos, ou se basta mostrar o alcance.

## D-3 · A ordem dos marcos na interface e na Revisão

Hoje a ordem é alfabética pelo código ([forms.py:1009](../../backend/processo_seletivo/interface/forms.py))
e a Revisão numera "1º marco" nessa ordem ([revisao.py:693](../../backend/processo_seletivo/interface/revisao.py)).
A proposta é ordenar pela posição na jornada, como `jornada.py` já faz. Não muda dado algum. A
dúvida é se o "1º/2º/3º marco" da Revisão pode deixar de existir, ou se alguém depende dele.

## D-4 · Combinação: uma pergunta ou duas

São 4 combinações de "operação" e "normalização" para 2 comportamentos (`combinacao.py`,
`divide_pela_soma_dos_pesos`). A proposta é a interface fazer uma pergunta só ("divide pela soma
dos pesos?") e gravar `MEDIA_PONDERADA`/`NENHUMA` ou `SOMA_PONDERADA`/`NENHUMA`. O acervo
continua lido como foi gravado. A decisão é se a tela pode deixar de oferecer
`SOMA_PONDERADA`+`PELA_SOMA_DOS_PESOS` em configuração nova.

## D-5 · "Maior idade" como opção de desempate

A proposta é oferecer "mais velho primeiro" e "mais novo primeiro", que gravam
`MENOR_VALOR_DE_FATO`/`MAIOR_VALOR_DE_FATO` sobre um fato do tipo data. Quando o Perfil ainda
não tem esse fato, a própria escolha o declara. Isso faz a inscrição pedir a data de nascimento
sem o operador passar pela tela de Perfis. A decisão é se esse efeito colateral é aceitável com
um aviso, ou se a declaração do fato tem de ser um gesto explícito.

## D-6 · Leituras da estrutura: quais mostrar

O protótipo mostra, como **leitura** e não como erro:

- Perfil sem ordem final;
- corte que "pula" uma Etapa;
- Etapa eliminatória depois da ordem final.

São deduções da estrutura, não regras do GPS, e podem ser exatamente o que o edital quer. O
exame de aptidão depois da classificação é um caso legítimo. A decisão é se elas aparecem, onde
e com que força, e se alguma vira impedimento (o estudo recomenda que nenhuma vire).

## D-7 · Etapas que não valem para todos os Perfis

No protótipo, TEC-LAB herda a documental, a didática e o exame de aptidão, porque as Etapas são
do Edital. A leitura acusa que a ordem final dele fecha antes dessas Etapas. Isso é limite do
modelo, e o redesenho não resolve. Fica registrado para decidir se vira estudo próprio.

## Achados que não pedem decisão de governança

Pedem correção, e cabem numa spec curta própria:

- **A2** — a recomposição do cartão apaga o que foi digitado durante a ida e volta (`_marco.html`).
- **A3** — a mensagem "marco FINAL" não nomeia o Perfil nem leva ao campo.
- **A9** — o caso fictício da prévia mostra notas acima da máxima declarada (a conferir).
- **A11** — o desempate pela nota de uma Etapa que a ordem não usa fica sem valor para todos;
  confirmar com um teste e, se for o caso, recusar na validação ou incluir a nota no universo.
- **A10** — a frase dos suplentes num corte intermediário (`pdf.py:1963`) é questão de norma, e é
  a única deste grupo que precisa de decisão.
