# Decisão — contrato de mutabilidade normativa

Tomada na revisão da [auditoria exploratória de UX de 13/09/2026](auditoria-exploratoria-ux-2026-09-13.md),
a partir do anexo 16 daquele relatório. Registro, não escopo: nenhuma feature em curso muda por
causa deste documento.

## O que o anexo mostrou

Medindo o conteúdo canônico vigente dos quatro Editais publicados do ambiente de auditoria contra
o que `interface.retificacao.campos_editaveis()` alcança:

| | 26/2026 | 01/2026 | 51/2026 | 90/2026 |
|---|---:|---:|---:|---:|
| Campos publicados | 98 | 96 | 87 | 81 |
| Retificável pela tela | 38 | 42 | 38 | 34 |
| **Normativo, sem decisão nenhuma** | **23** | **14** | **13** | **13** |

A cobertura bruta — 38 de 98 — **não** é o achado, e lê-la como "56% da Retificação está faltando"
seria errado: o denominador inclui identidade, derivados e ausências deliberadas e documentadas. O
achado é a última linha. Existem campos de norma publicada sobre os quais **ninguém decidiu nada**.

E alguns decidem quem participa ou o resultado calculado: os requisitos de participação, a espécie
do cadastro reserva, o prazo recursal, o arredondamento, a combinação e a normalização das
pontuações, as Etapas que entram na ordem, o critério de desempate, o local da prova e o método do
sorteio inteiro.

## A decisão

**Nenhum campo normativo entra no conteúdo publicado sem uma decisão explícita sobre sua
retificabilidade.** Isto é invariante de arquitetura, e não escopo de uma feature.

A decisão assume uma de quatro naturezas:

| Natureza | Significado |
|---|---|
| **Retificável** | pode ser corrigido administrativamente depois da publicação, e a interface oferece o caminho |
| **Não retificável** | mudá-lo exige outro mecanismo, e a razão é **normativa**, escrita, não técnica |
| **Derivado** | não se retifica diretamente; muda como consequência de outro campo |
| **Identidade / estrutural** | não pertence ao objeto de Retificação |

Os nomes são do contrato conceitual; o código pode grafá-los como preferir.

### Por que "não retificável" precisa de razão normativa

As exclusões que hoje existem são justificadas por um argumento técnico: *"retificá-las por caixa de
texto publicaria regra que o cálculo não interpreta"*. Esse argumento **já caiu**. `cutRule/tieOutcome`
e `callForm` entraram depois como `REFERENCIA`, *"porque são dois valores fechados, e a referência os
oferece conferindo a escolha contra a lista"*. `operation`, `normalization`, `rounding/mode`,
`appealWindow/unit`, `whenMissing` e `reserveType` são exatamente da mesma natureza.

O obstáculo desapareceu e a exclusão sobreviveu a ele — que é o padrão de falha que este contrato
existe para impedir.

### Por que o momento é o desenho da publicação

O próprio código registra a lição, a propósito de `callForm`:

> *"Declarado aqui **antes da primeira emissão**, pela lição que a `025` registrou como a que não
> teria conserto: endereço de Retificação não se conserta depois, porque publicação é ato imutável.
> O primeiro Edital publicado com a forma declarada nasceria irretificável nela."*

Decidir retificabilidade depois da publicação é tarde por construção. Por isso a decisão pertence
ao desenho de cada campo novo, e não a uma feature de correção posterior.

## O guardião

Hoje existe um teste que protege uma lista: `tests/contract/test_retificacoes_api.py:101` compara
`CAMPOS_ETAPA` com os campos normativos da Etapa. O contrato pede a generalização disso — um teste
que compare **a forma publicada com a forma classificada** e falhe quando nascer um campo sem
decisão.

Sem ele, o contrato é prosa. Com ele, a regressão estrutural fica impossível: um campo novo em
`publish_edital.py` quebra a suíte até alguém dizer qual das quatro naturezas ele tem.

**Feito, em 13/09/2026** (spec `026`), e **emendado em 14/09**. O contrato vive em
`backend/processo_seletivo/editais/domain/mutabilidade.py` e classifica **123 campos** — 72
retificáveis, 23 não retificáveis com razão normativa escrita, 24 de identidade ou estrutura e 4
derivados. O guardião é `backend/tests/contract/test_mutabilidade.py`: ele percorre o conteúdo
canônico de um Edital publicado de verdade, sem lista nomeada de coleções, e falha por omissão nos
dois sentidos — nomeando o campo, a coleção e o caminho.

Duas coisas a feature encontrou e que esta decisão não previa:

- **`location` não estava declarado em lugar nenhum.** O `publish_edital` o emitia desde a `021`, e
  nem o `openapi.yaml` nem `validation.py` o conferiam. Nenhum teste acusava, porque a conferência
  da forma publicada olha coleções e não campos.
- **A janela recursal e o método do sorteio não eram conferidos na publicação.** As regras existiam
  e alcançavam só a elaboração do Perfil: uma Retificação podia publicar prazo de zero dias, ou
  método declarado pela metade, sem recusa alguma.

**O quarto canário foi trocado.** Esta decisão elegia a regra classificatória — `rounding` e
`operation` — e tratava o método do sorteio como quinto candidato. A spec `026` inverteu os dois, e
a D-010 registra por quê. O custo foi pago: `rounding/scale`, `rounding/mode`, `operation` e
`normalization` são todos retificáveis pela tela.

**E a matriz errou cinco linhas, que a revisão do PR #114 restaurou.** Ela foi montada cruzando o
que o sistema **emite** com o que a tela **oferece**, e não com o que ele já **decide** sobre
retificabilidade — `operation`, `normalization`, `maxInscricoesPorCandidato` e
`isRegistrationPeriod` tinham decisão anterior escrita e testada em sentido contrário, e o método do
sorteio **pode** nascer por Retificação, porque é assim que o acervo anterior ao degrau 10 o
declara. A contradição só ficou visível quando o contrato passou a governar também a API.

## Os quatro canários

A spec que fechar este contrato deve ser conduzida por quatro correções de naturezas diferentes,
para que o desenho não se especialize num caso:

1. **Corrigir o local de uma prova** — `/schedule/…/location`. A `021`, cenário de aceitação 3, diz
   *"uma Retificação altera o local de um evento"*; a tela não tem o campo. Contradição objetiva,
   sem necessidade de interpretação.
2. **Corrigir um requisito de participação** — `/profiles/…/requirements/[]`. Coleção de texto que
   decide quem pode concorrer.
3. **Corrigir o prazo recursal** — `…/appealWindow/{admits, durationDays, unit}`. Objeto composto,
   com um valor de lista fechada, que governa um direito com prazo.
4. **Corrigir a regra classificatória** — `…/rounding/{mode, scale}` e `…/operation`. Valores
   fechados que mudam a pontuação combinada e, portanto, a posição.

O método do sorteio é o quinto candidato natural, e o mais desconfortável: a própria tela do sorteio
manda o operador retificá-lo, e a Retificação não oferece um único dos seus dez campos.

## Onde isto entra na ordem

O contrato **precede** a spec estrutural de vagas. Não a implementação da completude — o contrato.
A spec de vagas vai introduzir ou reorganizar conteúdo publicado, e precisa saber responder, no
desenho, "este elemento pode ser corrigido depois? em que condições?". Sem isso ela produz outro
`callForm`.

A implementação campo a campo pode vir depois, incrementalmente, por natureza.

## O que esta decisão não é

Não é "fazer todos os campos aparecerem na tela". Algumas ausências devem continuar ausências —
desde que sejam deliberadas, justificadas por norma e protegidas por teste. O nome
"completude da Retificação" induzia o erro oposto, e por isso foi abandonado.
