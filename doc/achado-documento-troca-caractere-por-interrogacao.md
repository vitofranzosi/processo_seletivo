# Achado — o documento oficial trocava caractere por `?` em silêncio

Encontrado em 08/10/2026 na auditoria das atribuições do Edital 90/2026 (Tutor TADS), onde foi o
ACH-01 — rótulo daquela auditoria, sem relação com o ACH-01 da
[reauditoria de UX de 16/09](auditoria-exploratoria-ux-2026-09-16.md). Reproduzido com o
renderizador real.

> **Situação: resolvido em 08/10/2026 por correção pontual**, escolhida pelo responsável pelo
> produto em vez de spec própria. A lista do que se normaliza e o ponto de recusa foram decididos
> antes da implementação, e estão em *A decisão*, abaixo. Continuam abertos os pontos de *O que
> fica de fora*.

## O que se observou

`_texto_pdf`, em `publicacoes/infrastructure/pdf.py`, codificava todo texto com
`encode("cp1252", "replace")`. As fontes do documento são a Helvetica base-14 em `WinAnsiEncoding`,
e o repertório delas é o do cp1252: cobre o português inteiro, e não cobre o que o Word cola junto
com ele. Todo caractere fora do repertório virava `?` **sem aviso**, no documento que é o ato
oficial do piloto.

As atribuições do Edital 90/2026 foram coladas do Word com `●` (U+25CF) e um espaço de largura zero
(U+200B) antes de cada item. A prévia saiu com `?` no lugar de cada marcador.

| Caractere | Antes | Origem típica |
|---|---|---|
| `●` U+25CF, U+F0B7, `▪` U+25AA | `?` | marcadores do Word |
| U+200B, U+FEFF | `?` | espaço de largura zero, BOM |
| `≥ ≤ ≠`, `→`, `✓` | `?` | texto técnico |
| `ç` decomposto (`c` + U+0327) | `c?` | texto colado do macOS |
| U+00AD, hífen condicional | `-` visível no meio da palavra | Word |
| `•` U+2022, `·`, `–` | certo | — |

O hífen condicional está **dentro** do cp1252, e por isso nunca virou `?`. Mas o WinAnsi o desenha
como hífen visível, que é o mesmo defeito por outro caminho.

## Por que nenhum guardião viu

Nenhuma validação de publicação olhava o repertório do texto. E nenhum teste usava caractere fora
do cp1252: todos os extratores de texto da suíte decodificam cp1252, e `?` decodifica sem erro.

O defeito contraria a Constituição, Princípio II: *"Divergência entre a configuração homologada e o
documento DEVE impedir a publicação"*, e o PDF *"DEVE corresponder exatamente à versão homologada"*.

## A decisão (responsável pelo produto, 08/10/2026)

1. **Normalizar apenas o que é conhecido e seguro**, preservando o significado:

   | O quê | Vira |
   |---|---|
   | composição NFC — a mesma que `shared/canonical.py` já aplica antes do resumo | a forma composta |
   | marcadores cheios: U+25CF `●`, U+F0B7 e U+F0A7 (área privada do Word), U+25AA `▪`, U+25A0 `■`, U+2023 `‣`, U+2043 `⁃`, U+2219 `∙` | `•` |
   | invisíveis: U+200B, U+200C, U+200D, U+2060, U+FEFF, U+00AD | removidos |
   | espaços tipográficos: U+2000–U+200A, U+202F, U+205F, U+3000 | espaço |
   | U+2010, U+2011, U+2212 | `-` |
   | U+2028, U+2029 | quebra de linha |

   **O marcador vazado `◦` (U+25E6) ficou de fora por decisão explícita**: trocá-lo por `•` apagaria
   a diferença de nível entre uma lista e a lista dentro dela. A composição NFC entrou depois da
   proposta inicial, quando se viu que texto colado do macOS seria recusado inteiro por causa dos
   acentos decompostos; para o resumo do conteúdo, as duas grafias já eram o mesmo conteúdo.

2. **O que sobra é impeditivo**, na publicação e na Retificação. A mensagem diz o campo, o Perfil
   ou a seção, e o caractere com o código: *"Nas atribuições do Perfil «Tutor TADS», há «≥»
   (U+2265) — caractere que o documento oficial não imprime. Reescreva o trecho sem ele."*

3. **A prévia também informa.** O caractere sai como `[U+2265]` no PDF, e não como `?`, e a tela da
   prévia lista as pendências deste tipo acima do documento, com o caminho até a etapa.

4. **Só os campos impressos são conferidos.** A descrição da Modalidade, por exemplo, só aparece na
   web, que é UTF-8.

5. Sem mudança no modelo de domínio. Independente da `064`, que compara o texto registrado e não o
   impresso justamente para não depender desta correção.

## O que foi feito

- `publicacoes/domain/grafia.py` — a lista fechada, num módulo de domínio que o renderizador e o
  validador importam. Uma tabela só, porque duas divergiriam, e a primeira divergência seria um `?`
  que a validação deixou passar.
- `pdf.py` — normaliza o snapshot **antes** de compor, para que o separador de linha separe
  parágrafo e o invisível não ocupe largura, e também em `largura` e em `_texto_pdf`, para os
  outros documentos. O Edital compõe em modo **estrito**: se um caractere sem grafia chegar ao
  papel, a publicação falha com `CaractereSemGrafia` em vez de imprimir `?`. É a segunda camada,
  porque a validação recusa antes.
- `validation.py` — `caractere_sem_grafia`, impeditivo nos dois atos, sobre os textos que o
  documento imprime.
- `interface/views.py` e `previa.html` — o destino da pendência, inclusive o método de sorteio
  comum, que caía como "não corrigível" (o `common_draw_method_invalid`, que tem o mesmo caminho,
  passou a ir à Classificação junto), e a lista na prévia.
- Testes: `tests/unit/publicacoes/test_grafia.py` (a lista), `test_pdf_grafia.py` (o documento),
  `tests/unit/editais/test_caractere_sem_grafia.py` (a regra) e
  `tests/interface/test_caractere_sem_grafia.py` (a prévia, a Revisão e a submissão recusada).

**O guarda de cobertura.** `test_todo_texto_impresso_passa_pela_validacao` injeta `≥` em cada um
dos textos de um snapshot máximo, um por vez. Onde o documento publicado recusa o caractere, a
validação tem de tê-lo recusado antes. A lista de campos da regra não é confiada à memória: tirar as
atribuições dela reprova o teste. Foi ele que achou o número do Edital e o código do marco, que a
primeira lista não tinha.

A fixture byte a byte do documento publicado não mudou: nenhum texto dela tem caractere afetado.

## O que fica de fora

- **Comprovante de inscrição e documentos da divulgação continuam com o `?`.** Eles usam o mesmo
  `render_documento`, e a normalização vale para eles; mas o texto ali é nome de candidato, que
  nenhuma validação de publicação alcança. Um nome com letra fora do cp1252 sai com `?`. Pede
  decisão própria: recusar no cadastro, transliterar ou embutir fonte com repertório maior.
- **O número do Edital e o título do Processo não se corrigem pelo assistente.** A regra os recusa,
  e a pendência sai como "não corrigível aqui", o que é verdade: o número se digita na criação, e
  nenhuma etapa o edita. Um Edital criado com `≥` no número não publica, nem se corrige. É
  improvável; fica registrado.
- **Edital publicado antes desta correção** com `?` no papel continua como está: documento
  publicado não se regenera. Uma Retificação dele passa a exigir que o texto de origem seja corrigido
  junto, porque a Retificação recompõe o documento inteiro.
- **A quebra rígida de texto colado** (ACH-02 da mesma auditoria): a dica do campo de atribuições
  diz que "uma linha em branco separa parágrafos", e `_paragrafos` separa a qualquer quebra. É
  registro separado.
