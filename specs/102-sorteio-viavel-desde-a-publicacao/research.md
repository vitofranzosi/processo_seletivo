# Research: Sorteio viável desde a publicação

**Feature**: [spec.md](spec.md) | **Date**: 2026-10-29

Tudo foi lido na `main` em `0ff70f07`. Não há `NEEDS CLARIFICATION` no contexto técnico: as três
perguntas de produto foram respondidas no clarify (D-005 a D-007), e o que sobrava era saber onde
cada regra mora.

## R-001 — A granularidade fica na tabela de fontes, como propriedade do adaptador

**Decision**: cada classe de adaptador declara um atributo de classe que diz se a fonte publica só a
data. `LoteriaFederal` e a nova fonte de demonstração "só a data" o declaram verdadeiro; a
`FonteDeTeste` atual o declara falso. Uma função nova em `sorteios/infrastructure/fontes/__init__.py`,
ao lado de `fonte_declarada`, responde a pergunta pelo **nome publicado**, lendo o vocabulário
deste ambiente (`fontes_publicadas`) e importando a classe sem instanciá-la. Para nome que não está
no vocabulário, ela responde "não se sabe", e quem pergunta se cala, porque essa fonte já tem achado
próprio (FR-2655).

**Rationale**: a granularidade é verdade do adaptador. `_nao_antes_de` é o código que devolve 00h00,
e uma declaração que more longe dele diverge na primeira mudança. O teste da FR-2649 chama
`observar` de cada adaptador do vocabulário, com a rede substituída no da Caixa, e confere que o
limite devolvido é meia-noite exatamente quando a declaração diz "só a data".

**Alternatives considered**: transformar `FONTES` num dicionário de tuplas `(caminho, granularidade)`
muda o formato que `fontes_publicadas`, `forms.py` e dois testes leem, e não ganha nada. Um campo no
`drawMethod` foi recusado pela D-001: a granularidade não é conteúdo do Edital.

## R-002 — A regra é pura e mora no domínio do sorteio

**Decision**: um módulo novo, `sorteios/domain/viabilidade.py`, com duas funções puras:

- o **limite previsto**, que recebe o `occurrenceAt` publicado e se a fonte publica só a data, e
  devolve 00h00 do dia no fuso institucional, ou nada quando a fonte publica a hora ou o instante
  não se lê;
- a **inviabilidade**, que recebe o limite previsto e o instante mais cedo de congelamento e devolve
  verdadeiro quando o limite não é posterior a ele.

Quem chama resolve a granularidade (R-001) e o instante de congelamento (R-003, R-005).

**Rationale**: a FR-2650 exige uma regra só para a publicação, a tela e a recusa. Pura, ela é
testável pela matriz da SC-954 sem banco. O domínio do sorteio não importa a infraestrutura, e é por
isso que a granularidade entra como argumento. `editais/domain/perfis.py` já importa
`sorteios.domain` de forma preguiçosa (algoritmos, regras de normalização e de substituição), e a
validação segue o mesmo caminho.

**Alternatives considered**: escrever a conta dentro de `validation.py` deixaria a tela do sorteio e
a recusa com uma segunda cópia. Pôr a regra em `editais/domain` inverteria a direção: quem lê método
de sorteio é o sorteio.

## R-003 — Na publicação, o instante mais cedo é o fim do período de `periodo_de_inscricoes`

**Decision**: a validação lê o fim pelo mesmo `periodo_de_inscricoes` que o congelamento obedece
(`recusa_por_inscricoes_em_curso`). Cala quando o período não está designado, não tem término ou está
cancelado, e recua quando há mais de um Evento marcado, como `_periodo_de_inscricoes_encerrado`.

**Rationale**: o congelamento recusa enquanto `agora <= fim` (`agora > fim` é o encerramento), de
modo que qualquer instante estritamente posterior ao fim é o primeiro possível. "Limite não posterior
ao fim" é, portanto, exatamente "nenhum congelamento possível vem antes do limite". Uma leitura
própria do `endAt` divergiria da que o congelamento obedece, que é o que o Princípio II proíbe.

## R-004 — Dois códigos: impeditivo na publicação e advertência na Retificação

**Decision**: na publicação, o achado é `BLOCKING_ERROR` com código próprio. Na Retificação, é
`WARNING` com **outro** código. Os dois são produzidos pela mesma função, que recebe o ato.

**Rationale**: `advertencias_do_ato` (`publicacoes/application/retificacoes.py`) subtrai da lista da
Retificação todo código que seria impeditivo na publicação. Com um código só, a advertência da
Retificação sumiria justamente onde a FR-2656 a quer. É o mesmo desenho de `_etapa_sem_resultado`,
cuja docstring registra a armadilha.

## R-005 — "Marco já sorteado" chega à validação por argumento

**Decision**: `validate_for_publication` ganha um argumento opcional com as identidades dos marcos
cujo sorteio já foi constituído em todos os recortes, com padrão vazio. Só `retificacoes.py` o
passa, a partir de um seletor novo em `sorteios/application/selectors.py`. Esse seletor deriva os
recortes de cada marco por `recortes_do_perfil` e procura um `Sorteio` sem sucessor em cada um.

O método comum do Edital é excluído só quando **todos** os marcos que ele governa (por
`marcos.metodo_que_governa`) estão no conjunto (FR-2656).

**Rationale**: a validação é pura sobre o snapshot, e é assim que a topologia de referência já chega
a ela (`topologia`, `054`). Com o padrão vazio, o erro cai para o lado que acusa, a mesma escolha que
a docstring de `validate_for_publication` registra para o ato.

**Alternatives considered**: consultar o banco dentro da validação quebraria a pureza que os testes
unitários de `tests/unit/editais/` usam. Excluir o marco com *algum* recorte sorteado esconderia o
recorte que ainda falta sortear.

## R-006 — A tela lê a viabilidade em `recortes_do_marco`

**Decision**: `sorteios/application/previa.py::recortes_do_marco`, que já monta o método vigente, o
`ocorre_em` e a recusa de inscrições em curso, passa a devolver:

- para o marco, um diagnóstico de congelamento, que vale quando a fonte do método vigente publica só
  a data e o limite previsto não é posterior ao congelamento mais cedo possível. Esse instante é o
  mais tarde entre `at` e o fim do período de inscrições lido por `periodo_de_inscricoes` (FR-2651).
  Comparar só com `at` deixaria sem aviso o Edital com as inscrições correndo até o dia da extração,
  que é justamente o que uma Retificação de prorrogação produz;
- para cada recorte congelado, um diagnóstico da relação. Ele usa o método **da versão que a relação
  cita** (`relacao.versao.content`) e o compara com o `publicada_em` dela. Diz também se o método
  vigente difere do comprometido (resumo diferente de `relacao.metodo_hash`), que é o caso da
  FR-2661.

O template mostra os dois com as classes `aviso` e `erro` que a folha já tem.

**Rationale**: a tela hoje calcula a "ocorrência da vez" a partir do método **vigente**. Depois de
uma Retificação do método, ela ofereceria "Realizar o sorteio" com a ocorrência nova a uma relação
que exige a antiga, e o clique terminaria em `occurrence_not_declared`. O diagnóstico da relação é o
que avisa antes. Nada se calcula no navegador, e nada é gravado.

**Achado lateral, registrado e não corrigido**: o botão "Realizar o sorteio" continua sendo oferecido
nesse caso. Escondê-lo não é pedido pela spec, e a decisão é do usuário.

## R-007 — A recusa ganha a saída, e a frase antiga fica

**Decision**: a recusa `occurrence_precedes_freeze` em `sorteios/application/sorteio.py` mantém a
primeira frase exatamente como está, com a formatação em UTC que é da lacuna 2, e acrescenta duas
frases:

- a granularidade, só quando a fonte da ocorrência publica só a data;
- a saída em três passos, sempre.

**Rationale**: a FR-2668 deixa a frase existente para a correção da lacuna 2, que mexe no mesmo
ponto. Reescrevê-la aqui criaria conflito garantido com aquele PR. Os testes que casam a mensagem
(`test_constituicao.py`, `test_ocorrencia_declarada.py`, `test_listas_de_concorrencia.py`) leem o
código ou um trecho da primeira frase, e a frase continua ali.

## R-008 — A segunda fonte de demonstração

**Decision**: `FONTE_DE_DEMONSTRACAO` passa de um par a uma tupla de pares: a atual e
`("Fonte de demonstração (só a data)", "...loteria_federal.FonteDeTesteSoData")`. A classe nova herda
o material fixo da `FonteDeTeste` e devolve como limite inferior `datetime.combine(hoje, time.min)`
no fuso institucional, com a mesma forma de `_nao_antes_de`. `fontes_publicadas` acrescenta as duas
sob a mesma chave de configuração.

**Rationale**: as duas existem pela mesma razão e se ligam juntas; uma segunda chave de configuração
seria mais uma variável que produção precisa recusar. `test_fonte_fora_de_producao.py` continua
afirmando que em produção o vocabulário é `{"Loteria Federal"}`. A ocorrência é única por
`(fonte, referência)`, e como o nome da fonte é outro, as duas demonstrações nunca compartilham
linha.

**Custo medido**: a `seed_demo`, as quatro fixtures centrais e os 46 arquivos que dependem delas
declaram a fonte atual, e nenhum muda. O seletor de fonte da composição (`forms.py`) passa a oferecer
três nomes em desenvolvimento. Nenhum teste fixa a quantidade de opções desse campo
(`grep "drawMethod/source"` em `tests/`).

## R-009 — Riscos de suíte conhecidos

- **Regra impeditiva nova quebra a suíte em bloco quando uma fixture a viola.** Não é o caso aqui:
  as fixtures declaram a fonte com horário (D-006). Os casos que declaram a Loteria Federal com
  extração em 2020 são do acervo, passam pela Retificação, e lá o achado só adverte. A suíte inteira
  roda antes do PR (`make test-pg`).
- **`test_vocabulario_da_composicao.py`** tem `sorteio.html` na lista literal. Ele exige que a tela
  que usa um termo do vocabulário (recorte, geração, faixa…) o defina em texto visível. O aviso novo
  fala de "relação", "extração" e "Retificação", e não pode introduzir termo da lista sem a definição
  que a tela já dá. A suíte acusa se introduzir.
- **`test_acessibilidade`** exige regra na folha para toda classe citada. O aviso usa `aviso` e
  `erro`, que já têm.
- **A CSP recusa estilo e script embutidos.** O aviso é só texto, sem `style=` nem `onclick=`.
