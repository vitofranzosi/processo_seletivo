# Diário de construção — rodada 2

Configuração de uma classificação **do zero, pela interface**, por quem conhece o edital e não o
GPS. Feito em 01/11/2026 sobre a mesma árvore da rodada 1, no banco do estudo
(`ps_ux_classificacao_20261101`, porta 8113), num Processo novo criado para isto:
`UX-DIARIO-20261101`, Edital 90/2027.

O registro passo a passo, sem edição, está em [diario-registro-bruto.txt](diario-registro-bruto.txt).

## Por que esta rodada

A rodada 1 montou o cenário complexo com um script que conferia os campos antes de salvar, e
descartou as tentativas que falharam. Ou seja, quem preencheu já sabia as respostas. O sintoma
relatado pelos operadores é de **construção**, e não se mede assim.

## O que se quis configurar

O texto que o operador tem na mão, como um edital o escreveria:

> **DOC-INFO, Professor Substituto de Informática, 2 vagas.** Prova objetiva, eliminatória e
> classificatória, 0 a 10, nota mínima 6, peso 2. Os **12 primeiros** da objetiva, e os empatados,
> passam à análise de títulos (0 a 10, classificatória, peso 1). Após os títulos, os **6
> primeiros e 2 suplentes** passam à análise documental (Deferido/Indeferido, eliminatória). A
> prova didática (0 a 10, mínimo 6, peso 3) é feita por quem for deferido. **Classificação final:
> média ponderada** de objetiva, títulos e didática. Desempate: maior nota na didática; persistindo,
> **maior idade**.
>
> **TEC-LAB, Técnico de Laboratório, 1 vaga.** Classificação pela soma ponderada de objetiva e
> títulos.

## Método e limites

- Navegador embutido do aplicativo, 1280 × 900, como `ana.elaboradora`. Criar o Processo exigiu
  `gustavo.gestor`.
- Os campos foram preenchidos pela ferramenta de formulário, não tecla a tecla. Isso deixa as
  ações mais rápidas que as de uma pessoa, e foi assim que apareceu o achado A2. Nos demais passos
  houve uma pausa de 2 segundos depois de cada ação que recompõe o cartão.
- As escolhas seguem o texto acima. Onde ele é omisso, foi registrado o palpite. Dois erros foram
  cometidos **de propósito**, porque são os que o texto induz: "maior idade" lido como "maior
  valor" da data de nascimento, e "Faixa seguinte" deixada sem resposta.
- Um único executor, que conhece o domínio pela rodada 1. **Não é teste com operadores.** O que
  se mede aqui é o que a interface diz e cala diante de cada gesto, não o tempo nem a taxa de
  erro de pessoas.

## Passo a passo

| # | Intenção (do edital) | Gesto | Resposta do GPS | Onde está a causa | Classificação |
|---|---|---|---|---|---|
| 0 | Criar o Edital | Elaboradora: Criar Processo | "A operação não é permitida." **Formulário volta vazio** | Papel (Gestor) | recusa com perda do digitado |
| 1 | Dois Perfis | Perfis: códigos, vagas | Salvo | — | ok |
| 2 | Quatro Etapas como no texto | Etapas: forma, mínima, máxima, peso, caráter | Salvo; ao escolher "decisão", **Eliminatória vem marcada** | — | ok (a 051 ajuda) |
| 3 | "12 da objetiva seguem para títulos" | Classificação → Acrescentar marco | Marco nasce chamado **"Classificação final"**, código = código do Perfil, corte "quantas vagas o quadro publicar" e destino "Não governa Etapa alguma" pré-marcados ([d01](capturas/diario/d01-marco-novo.jpg)) | — | o padrão fala da final quando o edital começa pelo corte |
| 4 | idem | Escolhe "pela pontuação", digita código, nome, marca objetiva, troca o corte | **O cartão é recomposto pelo servidor e desfaz** código, nome, etapa e alvo ([A2](#a2)) | `hx-swap="outerHTML"` com o estado do instante do pedido | entrada perdida em silêncio |
| 5 | idem | Refeito com pausas; corte fixo 12, empatados, alimenta títulos; "Faixa seguinte": **palpite** | Salvo. DOC-INFO **"sem pendência"** com um único marco intermediário ([d02](capturas/diario/d02-so-pre-sem-pendencia.jpg)) | — | aceito; nada indica que falta a final |
| 6 | "6 + 2 para documental" | 2º marco: objetiva + títulos | Surgem "Como as pontuações se combinam" **e** "Normalização" — duas perguntas para uma decisão ([A5](#a5)) | — | palpite (normalização) |
| 7 | "final exige a documental" | 3º marco: a documental **não está na lista** | Nenhuma pista de que a progressão já exclui os indeferidos | Etapas: marca classificatória; `calculo.py` (progressão) | exigência do edital sem lugar visível |
| 8 | "desempate por maior idade" | Acrescentar critério | Opções: pontuação numa Etapa / maior valor de fato / menor valor de fato. A lista do alvo só tem Etapas | Perfis (passo 2): o fato não foi declarado | ida e volta entre telas |
| 9 | idem | Perfis → Editar DOC-INFO → Acrescentar fato "Data de nascimento" → salvar → voltar → Editar → critério | Fato aparece **misturado às Etapas**; qualquer tipo aceita qualquer alvo | — | 4 navegações para uma cláusula |
| 10 | idem | **"Maior valor de fato" + Data de nascimento** (o que "maior idade" sugere) | Salvo, "sem pendência". **Favorece o mais jovem** | — | erro semântico aceito |
| 11 | Conferir | Simular classificação | A prévia mostra a jornada etapa → marco → etapa ([d03](capturas/diario/d03-previa-ja-e-trilho.jpg)). No caso "Desempate por critérios sucessivos" → Explorar: "2º · maior data de nascimento … Separou: Bruno = Carla › Alice", com Alice nascida em 1961 atrás dos nascidos em 1979 ([d04](capturas/diario/d04-idade-invertida-na-previa.jpg)) | — | o erro aparece no 3º nível, para quem inverte as datas de cabeça |
| 12 | TEC-LAB | Marco de objetiva + títulos, soma; "Faixa seguinte" em branco | Salvo, e no topo: **"IMPEDE A regra de corte do marco FINAL não declara se…"**. Há dois FINAL (um por Perfil); a frase não diz qual | campo do 2º Perfil | único ciclo salvar → erro |
| 13 | Revisar | Revisão | "Desempate, 2º: data de nascimento **mais recente**" — o erro fica legível. Marcos numerados **"1º marco = Classificação final", "3º = Seleção para títulos"** ([d05](capturas/diario/d05-revisao-traduz-e-inverte.jpg)) | — | o tradutor existe, no passo 9 |
| 14 | Mudança anterior | Etapas: "Subir" a didática para antes da documental; salvar | **Nenhum aviso** em Etapas, Classificação ou Revisão | — | mudança de sentido aceita em silêncio |

**Totais.** 9 salvamentos (Perfis 3, Etapas 2, Classificação 4) e uma única recusa depois de
salvar. Houve ainda:
- 1 entrada perdida por recomposição;
- 1 ida e volta entre telas;
- 6 palpites: faixa seguinte ×3, valor ausente ×2, normalização;
- 3 configurações aceitas em silêncio que **não dizem o que o edital diz**: idade invertida,
  reordenação e Perfil "sem pendência" só com um corte intermediário;
- 1 exigência do edital sem lugar visível (a documental na final).

## O que isto muda no diagnóstico

**O ciclo "salvar, receber erro, voltar" foi raro nesta construção: uma vez em nove
salvamentos.** O backend aceita rascunho incompleto, a apresentação condicional esconde o que não
se aplica e os padrões da 051 acertam vários casos. A rodada 1 tinha razão ao dizer que a
interface não "só valida ao salvar".

O problema que dominou foi outro, e é pior: **o GPS aceita, sem dizer nada, configurações que
contrariam o edital**, porque elas são válidas como estrutura. Idade invertida, ordem de etapas
que muda quem faz qual prova, classificação sem marco final. Nenhuma validação pode recusá-las, já
que não são inválidas. O que falta é o operador **ver o que configurou** no momento em que decide.

Os dois instrumentos que mostrariam isso **já existem no produto**, longe da decisão:

1. **O tradutor.** A Revisão escreve cada marco em português com as funções que compõem o PDF
   (`pdf.py`: `frases_da_combinacao`, `frases_do_corte`, `frases_do_desempate`…; em
   [revisao.py:505](../../backend/processo_seletivo/interface/revisao.py): *"A frase é a do
   documento"*). "Data de nascimento mais recente" denuncia o erro. Mas está no passo 9, numa lista
   de "o que será congelado", e não ao lado do critério.
2. **O trilho.** A prévia desenha a jornada na ordem do certame, etapa → marco → etapa
   ([jornada.py](../../backend/processo_seletivo/classificacao/domain/jornada.py)). A
   reordenação ficaria evidente ali. Mas ela só existe dentro do simulador, sob demanda, depois da
   configuração, e em modo leitura.

A proposta da rodada 2 deriva diretamente disso: **trazer o texto publicado e a jornada para o
lugar da decisão**, e fazer da jornada a superfície de edição.

## Achados

### A1 — A edição ordena pelo código; o certame, pela etapa

[forms.py:1009](../../backend/processo_seletivo/interface/forms.py) carrega os marcos com
`order_by("code")`. A tabela, os cartões e a Revisão
([revisao.py:693](../../backend/processo_seletivo/interface/revisao.py), `"{posicao + 1}º
marco"`) seguem essa ordem: FINAL, POS-TIT, PRE. Quem lê de cima para baixo encontra a
classificação final como "1º marco" e a seleção para títulos como "3º". É o caso mais nítido da
hipótese de que **a interface segue o modelo de dados, e o operador, o fluxo do edital**.

### A2 — A recomposição do cartão apaga o que foi digitado durante a ida e volta <a id="a2"></a>

"Como a ordem é produzida", cada caixa de Etapa e "Quantos progridem" disparam `hx-get` com
`hx-include` e `hx-swap="outerHTML"` sobre o cartão
([_marco.html](../../backend/processo_seletivo/interface/templates/interface/_marco.html), linhas
59–63 e 160–164). O cartão volta com o que foi enviado **no instante do pedido**. O que foi
digitado depois, enquanto a resposta não chegava, é substituído. Foi observado com preenchimento
automático, mais rápido que uma pessoa. A janela de perda é a latência da resposta, e numa rede
institucional ela não é desprezível. É um defeito, não questão de desenho; precisa de registro
próprio.

### A3 — A mensagem de impedimento não diz de qual Perfil é o marco

"A regra de corte do marco FINAL não declara se este Edital admite continuação…". O código do marco
só é único **dentro** do Perfil, e o próprio GPS sugere o mesmo nome ("Classificação final") para
o primeiro marco de cada Perfil. Correção imediata: nomear Perfil e marco, e levar ao campo.

### A4 — "Sem pendência" não quer dizer "expressa o edital"

Um Perfil com um único marco, que corta para títulos, fica "sem pendência". Uma ordem de etapas
que coloca a documental depois da final também. A validação faz o que deve, que é recusar o que é
inválido. Falta uma camada **descritiva**, que mostre o que foi construído; avisos novos não
resolvem isto.

Uma pista estrutural barata, assumidamente heurística: etapas que acontecem depois do último marco
do Perfil e que nenhum marco usa. No exemplo, títulos, documental e didática ficaram nessa
situação depois do passo 5.

### A5 — Duas perguntas para uma decisão: dividir ou não pela soma dos pesos <a id="a5"></a>

`combinacao.py` divide quando `operation == MEDIA_PONDERADA` **ou** `normalization ==
PELA_SOMA_DOS_PESOS`. São 4 combinações e 2 comportamentos. "Média ponderada" com "Normalização:
nenhuma" divide de qualquer jeito, o que contraria a leitura natural do segundo campo. A tela pode
fazer uma pergunta só e continuar gravando os dois campos.

### A6 — "Maior idade" não existe no vocabulário do operador

O operador precisa:
1. saber que idade vem de um fato;
2. declará-lo em outro passo;
3. voltar;
4. traduzir "maior idade" para **menor** valor da data.

A lista do alvo mistura Etapas e fatos e aceita combinações incoerentes. O texto do documento já
faz a tradução certa ("data de nascimento mais recente"). Falta oferecer "idade (mais velho
primeiro)" como opção, que grava `MENOR_VALOR_DE_FATO` sobre um fato do tipo data, e declarar o
fato ali mesmo.

### A7 — A documental "exigida na final" não tem lugar visível, mas já vale

O FINAL só considera quem participa da última etapa que enumera (`calculo.py` →
`restringir_a_participantes`). Quem foi eliminado antes, inclusive na documental, fica fora. A
porta decisória enumerada é, neste caso, redundante. Como a progressão não aparece na tela, o
operador procura a documental na lista e não a encontra: a marca classificatória a esconde.

### A8 — Reordenar etapas muda quem faz cada prova, sem aviso

Depois de subir a didática:
- o FINAL fecha antes da documental;
- o corte 6 + 2 passa a alimentar uma etapa posterior à didática;
- a didática recebe todos os que passaram pelos títulos.

Nada avisa nas Etapas, na Classificação ou na Revisão. As relações mudadas podem ser calculadas
sem dado pessoal: posição de cada marco, etapas "puladas" por um corte, eliminatórias antes e
depois da final.

### A9 — A prévia usa notas fora da escala declarada

No caso "Desempate por critérios sucessivos", a pontuação combinada é 95,00, numa configuração cuja
máxima declarada é 10 em todas as etapas. O caso é declaradamente "construído para demonstração",
mas um operador que confere números estranha. Fica para conferir se os casos ignoram a máxima de
propósito.

### A10 — Texto dos suplentes num corte intermediário (a conferir)

No corte de POS-TIT (para a documental), o documento publica "Os suplentes são chamados, na
ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados"
([pdf.py:1963](../../backend/processo_seletivo/publicacoes/infrastructure/pdf.py)). Para um corte
que não ocupa vagas, a frase parece descrever outro ato. É questão de norma, que fica para o
usuário decidir, e não se propõe aqui.

### A11 — Desempate pela nota de uma Etapa que a ordem não usa

Achado ao conferir se as linhas do protótipo representam a configuração, e não durante o
percurso. O cálculo oficial só lê os Resultados das Etapas que a ordem usa:
- [calculo.py](../../backend/processo_seletivo/classificacao/application/calculo.py) filtra
  `etapa_id__in=enumeradas`;
- [universo_classificavel.py](../../backend/processo_seletivo/classificacao/domain/universo_classificavel.py)
  monta as pontuações só desses Resultados;
- o desempate as lê dali ([desempate.py](../../backend/processo_seletivo/classificacao/domain/desempate.py)).

Um critério "maior nota em Entrevista", numa ordem que não usa a Entrevista, encontra o valor
vazio para todos. Com "fica por último", não separa ninguém; com "não se aplica", sai de todos os
grupos. O seletor oferece essa Etapa, e não foi encontrada validação que acuse o caso.

**Confirmado por teste** contra PostgreSQL:
[test_desempate_por_etapa_nao_enumerada.py](../../backend/tests/integration/classificacao/test_desempate_por_etapa_nao_enumerada.py).
O teste publica, avalia e consolida a Etapa pontuada (80, 80, 70) e a Entrevista (70 e 90 para os
dois empatados). Mesmo com os dois Resultados vigentes, a ordem oficial põe ambos em 1º, com
`empate_residual` verdadeiro, `separado_por` nulo e `pontuacoes` só da Etapa pontuada.

O teste afirma o que o edital diz e está marcado `xfail(strict=True)`, como os da auditoria da
Retificação. Quando a correção vier, ele passa a falhar e a marca sai. A correção tem dois
caminhos, e escolher entre eles é do usuário:
- ler no universo a nota da Etapa citada pelo critério;
- recusar o critério na validação.

## O que se confirma da rodada 1, e o que se corrige

- **Confirma-se** a separação entre Etapa (Edital) e marco (Perfil) como fonte de idas e vindas, e
  a semântica da marca. A rodada 2 acrescenta que ela **esconde** a documental de quem procura
  "exigir" essa etapa.
- **Corrige-se o centro do diagnóstico:** o problema dominante não é o operador "receber erros sem
  entender", e sim **não receber nada** quando a configuração diz outra coisa que o edital.
- **Muda a recomendação:** ela deixa de ser "mapa + painel de consequências". Passa a ser um
  **trilho editável**, que é a jornada que o GPS já calcula, promovida a superfície de edição, com
  **o texto do documento ao lado de cada decisão**. Os dois estão materializados em
  [prototipos/v2/](prototipos/v2/index.html).
