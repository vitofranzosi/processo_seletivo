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

**O endereço é estável e histórico** (FR-045, FR-046): uma publicação sucedida continua respondendo
no mesmo lugar, dizendo que foi sucedida.

## 2. A página

Lê **um** registro e renderiza `publico` (T-013). Nenhuma junção com `Inscricao`, `PosicaoNaOrdem`
ou `VersaoConsolidada`.

Responde, em texto e sem código interno (FR-047):

- **que resultado é** — o `natureza_rotulo` do cabeçalho, como afirmação: "Resultado preliminar";
- **de qual Edital** — com o caminho para a página pública dele;
- **quando foi publicado** — instante, e a autoridade que assinou;
- **se é a vigente** — e, quando não é, o aviso de sucessão com o caminho para a vigente (FR-042);
- **onde a pessoa está** — a lista, com posições compartilhadas ditas como tais.

**Acessibilidade e responsividade**: a situação vigente/sucedida não depende de cor (FR-050); a
lista tem estrutura semântica (FR-052); a 375 px não há rolagem horizontal da página (FR-049) — para
listas longas, a apresentação empilha em vez de rolar a tabela inteira.

**Não há botão de recurso** (FR-053). Havendo prazo recursal declarado na versão que o ato cita, a
informação normativa pode ser exibida como texto — sem mecanismo transacional.

## 3. A descobribilidade

`portal/views.selecao` — a página pública do Edital — passa a listar as publicações **vigentes** dos
marcos daquele Edital, com natureza e instante. É a página que alguém já abre para conhecer a
seleção, e é onde procura o resultado (FR-048, SC-018).

## 4. O documento

`HttpResponse(bytes, content_type=…)` com `ETag` igual ao `documento_hash`, no molde de
`PublishedDocumentView` (`publicacoes/api/views.py:120-133`). Entrega os bytes gravados; não
recompõe nada (FR-060).

Imprime, além da lista: Processo e Edital, marco, natureza, ato de origem e seu instante, data e
hora da publicação, autoridade signatária, e o resumo criptográfico do conteúdo (FR-061). Os rótulos
são os mesmos da página, porque vêm dos mesmos bytes (FR-062).

## 5. A Área do Candidato

`portal/views.acompanhamento` ganha uma chave de contexto, e **`_fatos_da_participacao` não muda** —
ele descreve fatos da própria inscrição, e a publicação é ato de terceiro (FR-058 é acréscimo, não
reescrita).

O seletor procura a publicação **vigente** cujo marco pertença ao Perfil da Inscrição e cujo
`individual` contenha a Inscrição. Não havendo, a chave é `None` e **nada** aparece — que é a I-004
dita em ausência de dado, e não em `if` de template (FR-054).

Havendo:

| Situação | O que aparece |
|---|---|
| `CLASSIFICADA` | Natureza, posição, pontuação e o caminho para o resultado completo |
| `SEM_POSICAO` | Natureza, a situação e o motivo — sem posição, e sem aparecer na lista pública |

O caminho leva sempre à publicação **vigente** (FR-059). O resumo é vista sobre os mesmos bytes que
a página pública renderiza: uma fonte, duas faces (FR-056, T-010).
