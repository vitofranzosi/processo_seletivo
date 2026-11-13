# Research: O limite do cadastro de reserva lido do corte

**Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Date**: 2026-11-13

As decisões técnicas do plano. As de produto são as `D-001` a `D-007` da spec; aqui elas não se
repetem. Cada item diz o que foi escolhido, por quê, e o que foi descartado.

---

## T-001 — A derivação mora num módulo puro de `editais/domain`

**Decisão.** Um módulo novo, `editais/domain/cadastro_de_reserva.py`, sem banco e sem ORM, recebe o
Perfil do conteúdo (publicado ou do rascunho) e devolve um valor imutável, `Cadastro`:

| Campo | O que é |
|---|---|
| `especie` | `NONE`, `LIMITED` ou `UNLIMITED`, como declarada |
| `legado` | o Perfil publicou número digitado (T-002) |
| `publicado` | esse número, ou `None` |
| `por_lista` | tupla de `(lista_id, nome, codigo, numero)`, na ordem do quadro; vazia sem corte |
| `alcance_cresce` | o marco que convoca admite continuação |
| `admite_empate` | o desfecho do empate do marco que convoca é `ADMITS_SURPLUS` |
| `com_modalidade` | o quadro tem linha de Modalidade |

E três leituras sobre ele: `numero_unico` (o número, quando é o mesmo em todas as listas),
`descricao_curta` (o texto das telas de gestão) e `incoerencias(ato)` (os achados da T-004).

**Por quê.** A FR-6930 pede uma regra só, lida por oito lugares em quatro apps (`publicacoes`,
`portal`, `interface`, `duvidas`) e por `ocupacao`/`convocacao` na nota do legado. `editais/domain`
é o único lugar que todos já importam. A direção `editais → classificacao.domain` já existe
(`validation.py` importa `classificacao.domain.combinacao`, e `faixa.py` registra isso), e o módulo
precisa de duas peças de lá: `faixa.normalizar` e `marco_intermediario.marco_que_le`.

**Descartado.** Pôr a conta em `classificacao/domain/faixa.py`, ao lado do alcance: o portal e as
dúvidas passariam a importar a classificação para uma frase de oferta. E calcular em cada lugar,
como hoje se lê o campo: é a terceira fonte que a FR-6930 proíbe.

## T-002 — O legado é um fato do conteúdo, e não uma data

**Decisão.** `legado` é verdadeiro quando o Perfil tem `reserveType == "LIMITED"` e `reserveLimit`
inteiro no conteúdo lido. Nesse caso, `publicado` é o número, e todas as telas o mostram (FR-6944);
`por_lista` continua calculado, porque a nota da ocupação (FR-6947) diz o alcance do corte.

**Por quê.** A spec decide que "antes desta feature" é um fato do Perfil publicado (Assumptions).
Depois desta feature, nenhum caminho grava número (T-003), de modo que o número presente **é** a
marca do legado. Uma data de corte erraria nos Editais retificados depois, que continuam legados
(FR-6948).

**Consequência que precisa de cuidado.** A Revisão de um rascunho antigo, que ainda guarda o número,
o veria como legado. Por isso o conteúdo composto do rascunho deixa de levar o número (T-003), e a
advertência da FR-6940 lê as linhas do rascunho, e não o conteúdo.

## T-003 — Nenhum caminho grava número; o rascunho antigo o perde na composição

**Decisão.**
- `editais/domain/perfis.py` (`validate_profile`): `LIMITED` com `reserveLimit` não nulo passa a ser
  recusado, com a frase da FR-6931 e `campo="reserveLimit"`. `NONE` e `UNLIMITED` continuam
  recusando número, como hoje.
- `interface/forms.py` deixa de ler o campo; o template `_perfil.html` deixa de desenhá-lo.
- `editais/domain/duplicacao.py` (`043`) e `editais/domain/reaproveitamento.py` (A-10) zeram
  `reserveLimit` ao copiar um Perfil, para que duplicar ou reaproveitar um Perfil legado não seja
  recusado pela regra nova.
- `interface/retificacao.py`: `NOVO_PERFIL` perde o campo. O Perfil acrescentado por Retificação nasce
  com `reserveType: "NONE"`, e o número que ele aceitava era incoerência antiga.
- `publicacoes/application/publish_edital.py` (`edital_snapshot`): para `LIMITED`, `reserveLimit` sai
  sempre `None`, mesmo que a linha do rascunho guarde número. É o que impede publicar o número
  digitado (FR-6940) e o que faz a Revisão não tratar o rascunho como legado (T-002).

**Por quê.** A FR-6931 diz "por qualquer caminho": a tela, a API, o assistente de elaboração e as
cópias. A coluna `PerfilVaga.reserve_limit` **fica**: rascunhos antigos a usam, e nada se exclui.

**Descartado.** Ignorar o número enviado em silêncio: a FR-6931 pede que a resposta diga de onde o
número vem. E uma migration que zerasse a coluna nos rascunhos: perderia o número que a FR-6940
mostra.

## T-004 — A coerência é achado de `validate_for_publication`, recortada pelo ato

**Decisão.** Cinco achados `BLOCKING_ERROR` novos em `editais/domain/validation.py`, produzidos por
`Cadastro.incoerencias(ato)`:

| Código | Requisito | Ato | Perfis alcançados |
|---|---|---|---|
| `reserve_limited_with_continuation` | FR-6933 | publicação e Retificação | `LIMITED` não legado |
| `reserve_unlimited_without_continuation` | FR-6934 | publicação | `UNLIMITED` com corte no marco que convoca |
| `reserve_limited_without_cut` | FR-6935 | publicação | `LIMITED` não legado |
| `reserve_limited_to_nobody` | FR-6936, FR-6951 | publicação e Retificação | `LIMITED` não legado |
| `reserve_limited_divergent_milestones` | FR-6939 | publicação e Retificação | `LIMITED` não legado |

**Por quê o recorte.** A espécie, a continuação e a Etapa governada não se retificam
(`mutabilidade.py`); o alvo e o excedente se retificam, e por isso o zero e a divergência valem também
na Retificação, como pede a FR-6951. *Revisto no code review de 13/11*: o corte inteiro **nasce** por
Retificação (`PODE_PASSAR_A_EXISTIR`), e um marco que convoca pode passar a cortar com continuação —
por isso o limitado com continuação também se confere na Retificação. O ilimitado sem continuação e o
limitado sem corte continuam só na publicação. É o recorte que a `027` registrou ao lado de `ATO_DE_PUBLICACAO`: uma exigência impeditiva
sem ele bloquearia toda Retificação do acervo. Para o `UNLIMITED` não há marca de legado (T-002), e
por isso a FR-6934 só vale na publicação, o que já satisfaz a FR-6948.

**A frase.** Cada achado nomeia o Perfil e o marco, diz o que está incoerente e o que mudar (FR-6937),
no vocabulário do documento (UX-726). O texto está em [contracts/telas.md](contracts/telas.md).

**Descartado.** Recusar na gravação do rascunho: o corte é declarado em outra etapa, e quem elabora
escolhe a espécie antes de ter o marco. A Revisão é onde as duas metades se encontram.

## T-005 — O marco que convoca é o não intermediário com corte

**Decisão.** São os marcos do Perfil para os quais `marco_que_le` devolve `None`, e que têm
`cutRule`. Sem nenhum, `por_lista` fica vazio (FR-6935 para o limitado). Com mais de um, cada um dá a
sua tupla; se divergirem em alguma lista, o achado da FR-6939. `alcance_cresce` e `admite_empate`
valem se **algum** deles admitir — é o lado que não afirma um teto que não existe.

**Por quê.** É a definição da FR-4531 da `133`, e a mesma que a ocupação e a convocação usam para
recusar o marco intermediário. Um marco que convoca e governa uma Etapa que nenhum outro marco lê —
o do `seed_demo` — continua sendo o que convoca, como a `133` decidiu.

## T-006 — A conta é por linha do quadro

**Decisão.** As listas são as linhas de `vacancyTable`. Perfil sem quadro (legado anterior à `025`)
tem uma lista só, a geral, com as vagas de `immediateVacancies`. Para cada lista:

- alvo do quadro: número = excedente;
- alvo fixo: número = alvo + excedente − vagas da linha.

O nome é o da Modalidade da linha, ou "Ampla concorrência" na linha geral, pela mesma regra de
`nome_da_lista_da_convocacao` do portal; o código é o da Modalidade, para a célula estreita do
documento.

**Por quê.** O alvo fixo vale em cada recorte (a FR-4553 da `133`), e o do quadro é a linha. É a mesma
conta que `_alcance_da_faixa` (FR-2474 da `097`) faz para o Perfil só de reserva, generalizada para
vagas maiores que zero; aquela função passa a ler a T-001, para que a advertência da `097` e o número
do cadastro não divirjam.

## T-007 — O documento muda em quatro funções de `pdf.py`, e `apresentacao.py` as segue

**Decisão.**
- `frase_do_cadastro(perfil)` e `_reserva(perfil)` leem `Cadastro`. As formas estão em
  [contracts/documento.md](contracts/documento.md).
- `frases_do_corte(marco, etapas, *, sem_cadastro, com_reservadas, cadastro=None)`: quem chama passa o
  `Cadastro` do Perfil **quando o marco é o que convoca**. Com ele e 0 vaga imediata, a frase de abertura
  vira a do cadastro (FR-6943). `sem_cadastro` deixa de ser do Edital e passa a ser do Perfil, e a frase
  dos suplentes muda conforme o Perfil tenha cadastro ou não (FR-6942).
- Os três chamadores — `pdf.py`, `apresentacao.py` e `interface/revisao.py` — passam o `Cadastro`.

**Por quê.** A unidade do corte é indivisível (o K1 a K10 da `069`): as frases que mudam são dela, e a
consolidação por Perfil da `068` continua comparando a unidade inteira. Perfis que antes se agrupavam e
agora diferem só no cadastro passam a sair separados, e isso é correção, e não regressão.

**O Perfil legado compõe a unidade de antes** (FR-6944). Os cenários da auditoria são o caso que
motivou a feature, publicados antes dela: "limitado em 15" com alvo 10, excedente 5 e continuação. A
abertura nova diria que o cadastro é dos primeiros que a faixa alcança e, na mesma unidade, que outros
podem ser chamados; recomposto, o Perfil legado diz o que dizia, e os PDFs gravados da auditoria
continuam idênticos byte a byte.

**A redação 1.** `_reserva` com `REDACAO_1` imprime "limitado em N" no documento antigo; com a T-002, o
legado continua igual (FR-6944), e o não legado imprime o número derivado na mesma forma.

## T-008 — As telas leem `Cadastro`, e o texto curto mora no domínio

**Decisão.**
- Portal: `views._oferta` e `situacao.frase_da_reserva` recebem `Cadastro`.
- Gestão: `revisao.py` (a linha "Cadastro Reserva"), `relatorio_do_edital._reserva` e
  `visao_geral.Reserva.do_perfil` usam `Cadastro.descricao_curta()`. A tabela da etapa (o resumo do
  cartão em `perfis.js`, da `052`) lê o `data-resumo` da opção "limitado", que o servidor passa a
  escrever com `Cadastro.resumo_limitado()` — `limitado` sem corte, `limitado: até 3` com ele (T-011).
- Assistente: `duvidas/domain/respostas.py` passa a dizer o número de `Cadastro`. No legado, cita
  `/profiles/…/reserveLimit`, como hoje; no derivado, cita o `cutRule` do marco que convoca, com o
  rótulo "Cadastro de reserva (pelo corte)", e `cobertura.py` ganha o caminho.

**Por quê.** As frases do portal são para o candidato, e as da gestão são curtas e iguais entre si;
deixar `descricao_curta` no domínio é o que garante que Revisão, relatório e visão institucional digam
o mesmo (SC-2298), sem cada uma formatar à sua maneira.

## T-009 — A nota do legado entra nas duas telas da condução, por um seletor só

**Decisão.** `ocupacao/application/selectors.py` ganha `nota_do_cadastro_legado(conteudo, perfil_id)`,
que devolve a frase da FR-6947 ou `None`. A tela da ocupação e a da convocação a desenham como
**nota** (UX-727), com a classe que as notas da ocupação já usam. A convocação a lê pela seta
`convocacao → ocupacao`, que é a que existe.

**Por quê.** A frase depende só do conteúdo vigente e do `Cadastro`; duas telas, uma regra.

## T-010 — A Retificação: o campo só no legado, e o antes e o depois derivados

**Decisão.**
- `CAMPOS_PERFIL` continua com `reserveLimit`, mas a tela só o desenha no Perfil legado (FR-6948,
  FR-6950).
- Na conferência da Retificação, quando a alteração toca `cutRule/targetCount` ou
  `cutRule/surplusCount` do marco que convoca de um Perfil `LIMITED` não legado, a lista de antes e
  depois ganha uma linha derivada "Cadastro de reserva", com `descricao_curta` dos dois conteúdos.
- `publicacoes/domain/alteracoes.py` não muda: o "O que mudou" público diz o campo, sem valor, e o
  campo é o do corte.

**Por quê.** A tela de homologação é a que mostra valores (o docstring de `alteracoes.py` registra
isso); acrescentar valor derivado na lista pública seria mudar a regra dela.

## T-011 — A Etapa Perfis: frase de origem e o número quando já há corte

**Decisão.** O campo do número sai de `_perfil.html`. No lugar, um único elemento de ajuda na opção
"Cadastro reserva limitado" (UX-725) diz que o número vem do corte do marco que convoca; quando o
Perfil do rascunho já tem esse corte, a linha diz o número, ou a lista curta por Modalidade. `perfis.js`
(o resumo do cartão, a tabela da etapa) deixa de ler o campo e usa só o `data-resumo` da opção
marcada, que o servidor escreve com o número derivado do corte salvo (T-008): a tabela lê a mesma
regra, como pede a FR-6930. Enquanto o corte não é salvo, o resumo é o do último salvo — o número
depende de outra etapa. `validacao.js` deixa de exigir o número.

**Por quê.** A ordem das etapas põe Perfis antes da Classificação, e quem elabora pode escolher a
espécie antes do marco; a Revisão é quem fecha (T-004).

## T-012 — O `seed_demo` e as fixtures

**Decisão.**
- `seed_demo`, Perfil `DOC-INFO`: sai `reserveLimit: 6`. O corte dele (alvo fixo de 2 e excedente
  de 1, sem continuação, aplicados em cada lista; a ampla e a PPP têm 1 vaga cada) dá **2 em cada
  lista**, e o documento passa a dizer "até 2 (dois) classificados em cada lista de concorrência".
- `seed_demo`, Perfil `TEC-LAB` (ilimitado, 0 vaga): a continuação do marco passa a `ALLOWED`. Sem
  isso, a FR-6934 recusa a demonstração. A advertência da `097` deixa de dizer o alcance nesse Perfil,
  porque a faixa cresce (o comportamento da `_alcance_da_faixa`).
- As fixtures com `LIMITED` e número que **publicam** passam a não ter número; as que representam
  conteúdo **já publicado** (o corpus da `070`, `snapshot_publicado.json`) ficam como estão: são
  legado, e é o caso que a FR-6944 prende.

**Por quê.** A regra impeditiva nova alcança toda fixture que publica Perfil incoerente. É o risco que
a memória do projeto registra como "regra impeditiva quebra a suíte em bloco": a causa costuma ser uma
só, nas fixtures.

## T-013 — O que não muda

- A faixa, a continuação sem teto (a FR-204 da `014`), a apuração, a convocação e o acréscimo da `097`.
- `PerfilVaga`: nenhuma tabela, nenhuma coluna. *Revisto na implementação*: uma migration, a
  `editais/0028`, afrouxa a constraint que exigia número em todo limitado (ver `data-model.md`).
- A advertência `reserve_only_convocation_external` da `097`: continua, e o alcance dela passa a sair da
  T-006.
- A Visão do Sistema (`docs/visao-sistema/`): é atualizada no merge, como as anteriores.
