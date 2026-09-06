# Contrato — os canais públicos

A página do resultado, o documento e o que a Área do Candidato passa a mostrar.

## 1. Rotas

| Rota | Método | View | Autenticação |
|---|---|---|---|
| `resultados/<publicacao_id>/` | GET | `portal.views.resultado` | nenhuma |
| `resultados/<publicacao_id>/documento.pdf` | GET | `portal.views.resultado_em_pdf` | nenhuma |

Não colidem com `path("<uuid:edital_id>/", …)`, que fecha `portal/urls.py`: `resultados` não casa
com `uuid`. O `.pdf` no fim segue o precedente do comprovante — é o que uma pessoa reconhece como
arquivo para guardar.

**O endereço é estável e histórico** (FR-047, FR-048): uma publicação sucedida continua respondendo
no mesmo lugar, dizendo que foi sucedida.

## 2. A página

Lê a publicação e desserializa `conteudo_publico` (T-013). Nenhuma consulta alcança `Inscricao`,
`PosicaoNaOrdem`, `VersaoConsolidada` ou `SituacaoDivulgada` — a fronteira é a ausência da consulta,
e não um filtro na serialização.

O número de consultas é constante: a publicação, e a cadeia para saber se ela ainda é a vigente. O
**custo** não é constante — desserializar, montar o HTML e transmiti-lo crescem com o número de
posições, como em qualquer lista. O que o teste de desempenho afirma é derivada zero em
**consultas** entre 10 e 1.000 posições, e é isso que ele mede.

Responde, em texto e sem código interno (FR-049):

- **que resultado é** — o `natureza_rotulo` do cabeçalho, como afirmação: "Resultado preliminar";
- **de qual Edital** — com o caminho para a página pública dele;
- **quando foi publicado** — instante, e a autoridade que assinou;
- **se é a vigente** — e, quando não é, o aviso de sucessão com o caminho para a vigente (FR-044);
- **onde a pessoa está** — a lista, com posições compartilhadas ditas como tais.

**Acessibilidade e responsividade**: a situação vigente/sucedida não depende de cor (FR-052); a
lista tem estrutura semântica (FR-054); a 375 px não há rolagem horizontal da página (FR-051) — para
listas longas, a apresentação empilha em vez de rolar a tabela inteira.

**Não há botão de recurso** (FR-055). Havendo prazo recursal declarado na versão que o ato cita, a
informação normativa pode ser exibida como texto — sem mecanismo transacional.

## 3. A descobribilidade

`portal/views.selecao` — a página pública do Edital — passa a listar as publicações **vigentes** dos
marcos daquele Edital, com natureza e instante. É a página que alguém já abre para conhecer a
seleção, e é onde procura o resultado (FR-050, SC-018).

## 4. O documento

`HttpResponse(bytes, content_type=…)` com `ETag` igual ao `documento_hash`, no molde de
`PublishedDocumentView` (`publicacoes/api/views.py:120-133`). Entrega os bytes gravados; não
recompõe nada (FR-062).

Imprime, além da lista: Processo e Edital, marco, natureza, ato de origem e seu instante, data e
hora da publicação, autoridade signatária, e o resumo criptográfico do conteúdo (FR-063). Os rótulos
são os mesmos da página, porque vêm dos mesmos bytes (FR-064).

## 5. A Área do Candidato

`portal/views.acompanhamento` ganha uma chave de contexto, e **`_fatos_da_participacao` não muda** —
ele descreve fatos da própria inscrição, e a publicação é ato de terceiro (FR-060 é acréscimo, não
reescrita).

O seletor busca `SituacaoDivulgada` pela Inscrição — índice próprio — e fica com a linha cuja
publicação é a vigente. Não havendo linha, a chave é `None` e **nada** aparece: a I-004 dita em
ausência de dado, e não em `if` de template (FR-056).

Havendo:

| `situacao` | O que aparece |
|---|---|
| `CLASSIFICADA` | Natureza, posição, pontuação e o caminho para o resultado completo |
| `SEM_POSICAO` | Natureza, a situação e o motivo — sem posição, e sem aparecer na lista pública |

O caminho leva sempre à publicação **vigente** (FR-061). O resumo não é outra fonte de verdade
(FR-058): ele é a projeção individual congelada na **mesma transação**, a partir do **mesmo ato
imutável** que produziu a lista pública, e aponta para a publicação que a originou. O que a FR-058
proíbe é uma fonte viva — que mudasse com o ato enquanto a publicação permanece histórica —, e esta
é congelada como a outra (T-010).
